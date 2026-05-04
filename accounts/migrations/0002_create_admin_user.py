from django.db import migrations


def create_admin_user(apps, schema_editor):
    User = apps.get_model("accounts", "CustomUser")

    username = "admin"
    email = "admin@mail.com"
    password = "Admin12345"

    if not User.objects.filter(username=username).exists():
        user = User(
            username=username,
            email=email,
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )
        user.set_password(password)
        user.save()


def delete_admin_user(apps, schema_editor):
    User = apps.get_model("accounts", "CustomUser")
    User.objects.filter(username="admin").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_admin_user, delete_admin_user),
    ]