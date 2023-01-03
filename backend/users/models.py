from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """ Кастомная модель пользователя. """
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']
    email = models.EmailField(
        max_length=254, verbose_name='Email', unique=True
    )
    username = models.CharField(max_length=150, verbose_name='Никнейм')
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    password = models.CharField(max_length=150, verbose_name='Пароль')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['id']

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    """ Модель подписок. """
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='author',
        verbose_name='Автор'
    )
    subscriber = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscriber',
        verbose_name='Подписчик'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'subscriber'],
                name='author_subscriber_unique'
            )
        ]

    def __str__(self):
        return f'{self.subscriber} подписан на {self.author}'
