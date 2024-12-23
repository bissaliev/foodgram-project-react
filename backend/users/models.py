from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Пользовательский менеджер моделей пользователей, где электронная почта
    является уникальным идентификатором для аутентификации
    вместо имен пользователей
    """

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Введите адрес электронной почты.")
        email = self.normalize_email(email)
        print(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError(
                "У суперпользователя должно быть значение is_staff=True."
            )
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                "У суперпользователя должно быть значение is_superuser=True."
            )
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Кастомная модель пользователя."""

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name", "password"]
    email = models.EmailField(
        max_length=254, verbose_name="Email", unique=True
    )
    username = models.CharField(max_length=150, verbose_name="Никнейм")
    first_name = models.CharField(max_length=150, verbose_name="Имя")
    last_name = models.CharField(max_length=150, verbose_name="Фамилия")
    password = models.CharField(max_length=150, verbose_name="Пароль")

    objects = CustomUserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["id"]

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    """Модель подписок."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscribers",
        verbose_name="Автор",
    )
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Подписчик",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["author", "subscriber"],
                name="author_subscriber_unique",
            )
        ]

    def __str__(self):
        return f"{self.subscriber} подписан на {self.author}"
