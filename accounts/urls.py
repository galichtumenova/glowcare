from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('catalog/<slug:slug>/', views.category_detail, name='category_detail'),
    path('catalog/<slug:slug>/sub/<slug:sub_slug>/', views.subcategory_detail, name='subcategory_detail'),
    path('catalog/<slug:slug>/product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('tips/', views.tips, name='tips'),

    # Корзина
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),

    # Оформление заказа в Telegram
    path('checkout/', views.checkout_order, name='checkout_order'),

    # Избранное
    path('wishlist/', views.wishlist_view, name='wishlist_view'),
    path('wishlist/toggle/<int:product_id>/', views.wishlist_toggle, name='wishlist_toggle'),

    # Профиль
    path('profile/', views.profile_view, name='profile'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('chatbot/', views.chatbot_view, name='chatbot'),
]