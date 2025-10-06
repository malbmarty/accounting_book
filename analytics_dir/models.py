from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.
class Project(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class Participant(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class PaymentSystem(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class Counterparty(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class Item(models.Model):
    # Варианты для расхода/прихода
    FLOW_TYPE_CHOICES = [
        ("income", "Приход"),
        ("expense", "Расход"),
    ]

    # Варианты для постоянных/переменных
    VARIABILITY_CHOICES = [
        ("variable", "Переменные"),
        ("fixed", "Постоянные"),
    ]

    name = models.CharField(max_length=100, unique=True, verbose_name="Название")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name="Группа")

    flow_type = models.CharField(
        max_length=10,
        choices=FLOW_TYPE_CHOICES,
        verbose_name="Приход/расход",
    )

    variability = models.CharField(
        max_length=10,
        choices=VARIABILITY_CHOICES,
        blank=True,
        null=True,
        verbose_name="Переменные/постоянные",
    )
    def clean(self):
        if self.flow_type == "income" and self.variability:
            raise ValidationError(
                {"variability": "Поле «Постоянные/переменные» можно указывать только для расходов."}
            )
    def __str__(self):
        return self.name
