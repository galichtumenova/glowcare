from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.http import require_POST
from django.db.models import Q

from .forms import RegisterForm, LoginForm, ProfileUpdateForm
from .models import Category, SubCategory, Product, CartItem, WishlistItem

import json
import os
import requests

try:
    from google import genai
except ImportError:
    genai = None


def home(request):
    products = Product.objects.all()
    return render(request, 'accounts/index.html', {
        'bestsellers': products[:5],
        'sale_products': products[5:10] if products.count() > 5 else products[:5],
    })


def catalog(request):
    query = request.GET.get("q", "").strip()

    if query:
        category = Category.objects.filter(
            Q(name__icontains=query) |
            Q(slug__icontains=query)
        ).first()

        if category:
            return redirect('category_detail', slug=category.slug)

        product = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(category__slug__icontains=query)
        ).select_related('category').first()

        if product:
            return redirect(
                'product_detail',
                slug=product.category.slug,
                product_id=product.id
            )

    categories = Category.objects.prefetch_related('subcategories').all()

    return render(request, 'accounts/catalog.html', {
        'categories': categories,
        'query': query,
    })


def category_detail(request, slug):
    categories = Category.objects.all()
    category = get_object_or_404(Category, slug=slug)
    subcategories = SubCategory.objects.filter(category=category)
    products = Product.objects.filter(category=category)

    wishlist_ids = []
    cart_ids = []

    if request.user.is_authenticated:
        wishlist_ids = list(
            WishlistItem.objects.filter(user=request.user)
            .values_list('product_id', flat=True)
        )
        cart_ids = list(
            CartItem.objects.filter(user=request.user)
            .values_list('product_id', flat=True)
        )

    return render(request, 'accounts/category_detail.html', {
        'categories': categories,
        'category': category,
        'subcategories': subcategories,
        'products': products,
        'wishlist_ids': wishlist_ids,
        'cart_ids': cart_ids,
        'active_sub': None,
    })


def subcategory_detail(request, slug, sub_slug):
    categories = Category.objects.all()
    category = get_object_or_404(Category, slug=slug)
    subcategories = SubCategory.objects.filter(category=category)
    active_sub = get_object_or_404(SubCategory, category=category, slug=sub_slug)
    products = Product.objects.filter(subcategory=active_sub)

    wishlist_ids = []
    cart_ids = []

    if request.user.is_authenticated:
        wishlist_ids = list(
            WishlistItem.objects.filter(user=request.user)
            .values_list('product_id', flat=True)
        )
        cart_ids = list(
            CartItem.objects.filter(user=request.user)
            .values_list('product_id', flat=True)
        )

    return render(request, 'accounts/category_detail.html', {
        'categories': categories,
        'category': category,
        'subcategories': subcategories,
        'products': products,
        'wishlist_ids': wishlist_ids,
        'cart_ids': cart_ids,
        'active_sub': active_sub,
    })


def product_detail(request, slug, product_id):
    categories = Category.objects.all()
    category = get_object_or_404(Category, slug=slug)
    product = get_object_or_404(Product, id=product_id, category=category)

    in_wishlist = False
    in_cart = False

    if request.user.is_authenticated:
        in_wishlist = WishlistItem.objects.filter(
            user=request.user,
            product=product
        ).exists()

        in_cart = CartItem.objects.filter(
            user=request.user,
            product=product
        ).exists()

    return render(request, 'accounts/product_detail.html', {
        'categories': categories,
        'category': category,
        'product': product,
        'in_wishlist': in_wishlist,
        'in_cart': in_cart,
    })


# ===== КОРЗИНА =====

@login_required
@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        item.quantity += 1
        item.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': CartItem.objects.filter(user=request.user).count(),
            'in_cart': True
        })

    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
@require_POST
def cart_remove(request, product_id):
    CartItem.objects.filter(
        user=request.user,
        product_id=product_id
    ).delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': CartItem.objects.filter(user=request.user).count(),
            'in_cart': False
        })

    return redirect('cart_view')


@login_required
def cart_view(request):
    items = CartItem.objects.filter(user=request.user).select_related('product')
    total = sum(item.total_price() for item in items)

    return render(request, 'accounts/cart.html', {
        'items': items,
        'total': total
    })


# ===== ИЗБРАННОЕ =====

@login_required
@require_POST
def wishlist_toggle(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    item = WishlistItem.objects.filter(
        user=request.user,
        product=product
    )

    if item.exists():
        item.delete()
        in_wishlist = False
    else:
        WishlistItem.objects.create(
            user=request.user,
            product=product
        )
        in_wishlist = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'in_wishlist': in_wishlist,
            'wishlist_count': WishlistItem.objects.filter(user=request.user).count()
        })

    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def wishlist_view(request):
    items = WishlistItem.objects.filter(user=request.user).select_related('product')

    return render(request, 'accounts/wishlist.html', {
        'items': items
    })


def tips(request):
    return render(request, 'accounts/tips.html')


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {
        'form': form
    })


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profile')

        return render(request, 'accounts/login.html', {
            'form': form,
            'error': 'Неверный username или password'
        })

    return render(request, 'accounts/login.html', {
        'form': LoginForm()
    })


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user
        )

        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'accounts/profile.html', {
        'form': form
    })


def logout_view(request):
    logout(request)
    return redirect('home')


# ===== CHATBOT =====

def is_kazakh_text(text):
    text = text.lower()
    kazakh_letters = ["ә", "і", "ң", "ғ", "ү", "ұ", "қ", "ө", "һ"]
    kazakh_words = [
        "сәлем", "қалай", "қандай", "керек", "тері", "күтім",
        "құрғақ", "майлы", "сезімтал", "безеу", "күннен", "қорғаныс",
        "жуу", "крем", "сыворотка", "тазарту", "кожа", "қожам"
    ]

    return any(letter in text for letter in kazakh_letters) or any(word in text for word in kazakh_words)


def local_chatbot_response(user_message):
    msg = user_message.lower().strip()

    if is_kazakh_text(user_message):
        if "құрғақ" in msg:
            return (
                "Құрғақ теріге жұмсақ тазарту, ылғалдандыратын тонер, гиалурон қышқылы бар сыворотка "
                "және тері қорғанысын қалпына келтіретін крем керек. Таңертең SPF қолданған дұрыс."
            )

        if "майлы" in msg:
            return (
                "Майлы теріге жеңіл гель немесе флюид текстуралы күтім жақсы келеді. "
                "Теріні қатты құрғатпаңыз, себебі ол май бөлінуін күшейтуі мүмкін."
            )

        if "сезімтал" in msg:
            return (
                "Сезімтал теріге минималды күтім керек: жұмсақ тазарту, тыныштандыратын крем және SPF. "
                "Құрамында центелла, пантенол немесе керамидтер болғаны жақсы."
            )

        if "spf" in msg or "күн" in msg:
            return (
                "SPF күн сайын қажет. Ол теріні күн сәулесінен, пигментациядан және ерте қартаюдан қорғайды. "
                "Таңертең күтімнің соңғы кезеңі ретінде жағылады."
            )

        if "қандай" in msg or "тип" in msg or "кожа" in msg or "қожам" in msg:
            return (
                "Тері түрін білу үшін бетіңізді жұмсақ құралмен жуып, 1–2 сағат крем жақпай күтіңіз. "
                "Егер бет толық жылтыраса — майлы тері. Егер тартылып, құрғап тұрса — құрғақ тері. "
                "Егер тек T-аймақ майланса — аралас тері. Егер қызарып, тез тітіркенсе — сезімтал тері."
            )

        return (
            "Тері күтімінің негізгі реті: тазарту → тонер → сыворотка → крем → таңертең SPF. "
            "Егер теріңіз қатты қабынса, аллергия немесе ауыр акне болса, дерматологқа қаралған дұрыс."
        )

    if "тип кожи" in msg or "определить тип кожи" in msg:
        return (
            "Чтобы определить тип кожи, умойтесь мягким средством и подождите 1–2 часа без крема. "
            "Если кожа блестит по всему лицу — жирная. Если стянутая и шелушится — сухая. "
            "Если жирная только T-зона — комбинированная. Если часто краснеет и реагирует — чувствительная."
        )

    elif "базовый уход" in msg or "каждый день" in msg or "ежедневный уход" in msg:
        return (
            "Базовый уход состоит из 4 шагов: очищение, тонизация, увлажнение и SPF утром. "
            "Вечером используйте очищение, тонер или сыворотку и крем. Главное — не перегружать кожу."
        )

    elif "spf" in msg or "солнц" in msg or "санскрин" in msg:
        return (
            "SPF нужен каждый день, даже если пасмурно. Он защищает кожу от пигментации, фотостарения "
            "и повреждения солнцем. Утром наносите SPF последним этапом ухода."
        )

    elif "акне" in msg or "прыщ" in msg or "высыпания" in msg:
        return (
            "При акне важно мягкое очищение, лёгкий увлажняющий крем и SPF. "
            "Не пересушивайте кожу спиртовыми средствами. Лучше выбирать продукты с ниацинамидом, "
            "салициловой кислотой или центеллой, но вводить их постепенно."
        )

    elif "сухая кожа" in msg or "кожа сухая" in msg or "сухость" in msg:
        return (
            "Для сухой кожи выбирайте мягкое очищение, увлажняющий тонер, сыворотку с гиалуроновой кислотой "
            "и крем для восстановления барьера. Избегайте жёстких скрабов и горячей воды."
        )

    elif "чувствительная кожа" in msg or "кожа чувствительная" in msg or "раздражение" in msg:
        return (
            "Для чувствительной кожи лучше использовать минимум средств: мягкое очищение, успокаивающий крем и SPF. "
            "Подойдут компоненты: центелла, пантенол, керамиды. Новые активы вводите осторожно."
        )

    elif "жирная кожа" in msg or "кожа жирная" in msg or "жирный блеск" in msg:
        return (
            "Для жирной кожи подойдут лёгкие гели и флюиды, мягкое очищение и средства с ниацинамидом. "
            "Не нужно пересушивать кожу, потому что из-за этого себума может стать ещё больше."
        )

    elif "сыворотк" in msg:
        return (
            "Сыворотку выбирают по задаче кожи. Для увлажнения — гиалуроновая кислота, "
            "для сияния — ниацинамид, для постакне — витамин C или кислоты, "
            "для восстановления — пантенол и центелла."
        )

    elif "порядок" in msg or "наносить уход" in msg or "как наносить" in msg:
        return (
            "Правильный порядок ухода: очищение → тонер → сыворотка → крем → SPF утром. "
            "Вечером SPF не нужен. Наносите средства от самой лёгкой текстуры к более плотной."
        )

    elif "ретинол" in msg:
        return (
            "Ретинол помогает улучшить текстуру кожи, уменьшить постакне и признаки старения. "
            "Но его нужно вводить постепенно: 1–2 раза в неделю вечером. Утром обязательно SPF."
        )

    elif "тоник" in msg or "тонер" in msg or "тонизация" in msg:
        return (
            "Тонер помогает вернуть коже комфорт после умывания и подготовить её к сыворотке или крему. "
            "Для сухой кожи лучше увлажняющий тонер, для жирной — лёгкий балансирующий."
        )

    elif "крем" in msg:
        return (
            "Крем нужен для удержания влаги и восстановления защитного барьера кожи. "
            "Для сухой кожи выбирайте более плотный крем, для жирной — лёгкий гель-крем."
        )

    elif "очищение" in msg or "пенка" in msg or "умывание" in msg:
        return (
            "Очищение нужно утром и вечером. Выбирайте мягкое средство, которое не оставляет сильной стянутости. "
            "Если есть макияж или SPF, вечером лучше делать двухэтапное очищение."
        )

    elif "каталог" in msg or "товар" in msg or "продукт" in msg:
        return (
            "В разделе «Каталог» вы можете посмотреть товары по категориям: очищение, тонизация, сыворотки, кремы и SPF."
        )

    elif "избранное" in msg:
        return (
            "В избранное можно добавить товары, которые вам понравились. Потом их легко найти и сравнить."
        )

    elif "корзина" in msg:
        return (
            "В корзине сохраняются товары, которые вы хотите заказать. Вы можете добавить или убрать товар."
        )

    elif "регистрация" in msg:
        return (
            "Чтобы зарегистрироваться, перейдите в раздел «Регистрация» и заполните форму."
        )

    elif "вход" in msg or "логин" in msg:
        return (
            "Чтобы войти в аккаунт, перейдите в раздел «Вход» и введите username и password."
        )

    elif "привет" in msg or "здравствуйте" in msg or "сәлем" in msg:
        return (
            "Здравствуйте! Я AI-консультант GlowCare. Могу помочь с подбором ухода, SPF, акне, сухостью и типом кожи."
        )

    elif "спасибо" in msg or "рахмет" in msg:
        return (
            "Пожалуйста! Если хотите, я могу помочь подобрать базовый уход по вашему типу кожи."
        )

    return (
        "Я пока не знаю точный ответ на этот вопрос. Попробуйте спросить про тип кожи, базовый уход, SPF, акне, "
        "сухую кожу, чувствительную кожу или порядок нанесения средств."
    )


def clean_gemini_text(text):
    text = text.strip()
    text = text.replace("**", "")
    text = text.replace("*", "")
    text = text.replace("__", "")
    text = text.replace("_", "")
    text = text.replace("#", "")
    return text


def gemini_chatbot_response(user_message):
    if genai is None:
        print("GEMINI ERROR: google-genai кітапханасы орнатылмаған")
        return None

    api_key = getattr(settings, "GEMINI_API_KEY", "")

    if not api_key:
        print("GEMINI ERROR: GEMINI_API_KEY табылмады")
        return None

    try:
        client = genai.Client(api_key=api_key)

        prompt = f"""
Ты AI-консультант интернет-магазина GlowCare.

GlowCare — это сайт уходовой косметики.

Очень важное правило языка:
Если клиент пишет на казахском языке — отвечай на казахском языке.
Если клиент пишет на русском языке — отвечай на русском языке.
Если клиент пишет на английском языке — отвечай на английском языке.
Всегда отвечай на том же языке, на котором задан вопрос.

Стиль ответа:
Коротко, понятно, дружелюбно и эстетично.
Максимум 5–7 предложений.
Не используй Markdown-разметку.
Не используй символы **, *, #.
Пиши обычным текстом.

Правила безопасности:
Не ставь медицинские диагнозы.
Если вопрос про сильное акне, аллергию, ожог, боль, воспаление, лечение или лекарства — мягко посоветуй обратиться к дерматологу.

Темы:
Если вопрос про уход за кожей, SPF, очищение, тонизацию, кремы, сыворотки, сухую кожу, жирную кожу, чувствительную кожу — отвечай как консультант по уходовой косметике.
Если вопрос про каталог, корзину или избранное — объясни, как пользоваться сайтом GlowCare.
Не упоминай, что ты Gemini.
Не говори, что ты искусственный интеллект от Google.

Вопрос клиента:
{user_message}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        if response and response.text:
            return clean_gemini_text(response.text)

        return None

    except Exception as e:
        print("GEMINI ERROR:", e)
        return None


def chatbot_response(user_message):
    gemini_answer = gemini_chatbot_response(user_message)

    if gemini_answer:
        return gemini_answer

    return local_chatbot_response(user_message)


def load_chat_history():
    file_path = os.path.join(settings.BASE_DIR, 'chat_history.json')

    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    return []


def save_chat_history(history):
    file_path = os.path.join(settings.BASE_DIR, 'chat_history.json')

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=4)


def chatbot_view(request):
    bot_reply = None
    user_message = ""
    chat_history = load_chat_history()

    if request.method == "POST":

        if "clear_all" in request.POST:
            save_chat_history([])

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True
                })

            return redirect('chatbot')

        if "delete_index" in request.POST:
            try:
                idx = int(request.POST.get("delete_index"))

                if 0 <= idx < len(chat_history):
                    del chat_history[idx]
                    save_chat_history(chat_history)

            except (ValueError, TypeError):
                pass

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True
                })

            return redirect('chatbot')

        user_message = request.POST.get("message", "").strip()

        if user_message:
            bot_reply = chatbot_response(user_message)
            username = request.user.username if request.user.is_authenticated else "Guest"

            chat_history.append({
                "user": username,
                "message": user_message,
                "bot": bot_reply
            })

            save_chat_history(chat_history)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'user': username,
                    'user_message': user_message,
                    'bot_reply': bot_reply,
                    'index': len(chat_history) - 1
                })

    return render(request, 'accounts/chatbot.html', {
        'user_message': user_message,
        'bot_reply': bot_reply,
        'chat_history': load_chat_history()[-10:]
    })


# ===== ОФОРМЛЕНИЕ ЗАКАЗА В TELEGRAM =====

@login_required
@require_POST
def checkout_order(request):
    name = request.POST.get("name", "").strip()
    phone = request.POST.get("phone", "").strip()
    address = request.POST.get("address", "").strip()
    comment = request.POST.get("comment", "").strip()

    items = CartItem.objects.filter(user=request.user).select_related("product")

    if not items.exists():
        return JsonResponse({
            "success": False,
            "message": "Корзина пустая"
        })

    if not name or not phone or not address:
        return JsonResponse({
            "success": False,
            "message": "Заполните имя, телефон и адрес"
        })

    total = sum(item.total_price() for item in items)

    products_text = ""

    for item in items:
        products_text += (
            f"\n• {item.product.name}\n"
            f"  Количество: {item.quantity}\n"
            f"  Цена: {item.product.price} ₸\n"
            f"  Сумма: {item.total_price()} ₸\n"
        )

    telegram_message = f"""
🛍 Новый заказ GlowCare

👤 Клиент: {name}
📞 Телефон: {phone}
📍 Адрес: {address}

🧴 Товары:
{products_text}

💰 Итого: {total} ₸

💬 Комментарий:
{comment if comment else "Без комментария"}

👥 Аккаунт: {request.user.username}
"""

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"

    try:
        response = requests.post(url, data={
            "chat_id": settings.TELEGRAM_CHAT_ID,
            "text": telegram_message
        })

        if response.status_code == 200:
            items.delete()

            return JsonResponse({
                "success": True,
                "message": "Заказ отправлен в Telegram"
            })

        return JsonResponse({
            "success": False,
            "message": "Ошибка отправки в Telegram. Проверьте TOKEN и CHAT_ID."
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"Ошибка: {e}"
        })