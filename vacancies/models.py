from django.contrib.auth.models import User
from django.db import models


class Skill(models.Model):
    name = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)

    # Русифицируем админку Навыки
    class Meta:
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"

    def __str__(self):
        return self.name


class Vacancy(models.Model):
    STATUS = [
        ("draft", "Черновик"),
        ("open", "Открытая"),
        ("closed", "Закрыта")
    ]
    slug = models.SlugField(max_length=50)
    text = models.CharField(max_length=2000)
    status = models.CharField(max_length=6, choices=STATUS, default="draft")
    created = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    skills = models.ManyToManyField(Skill)

    likes = models.IntegerField(default=0)

    # Русифицируем админку Вакансии
    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
    # Сортировка в алфавитном порядке
    #     ordering = ["text"]

    def __str__(self):
        return self.slug

    @property
    def username(self):
        return self.user.username if self.user else None

