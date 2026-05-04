from django.db import migrations
from django.contrib.auth.hashers import make_password


def create_admin_user(apps, schema_editor):
    User = apps.get_model("accounts", "CustomUser")

    username = "admin"
    email = "admin@mail.com"
    password = "Admin12345"

    if not User.objects.filter(username=username).exists():
        User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )


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