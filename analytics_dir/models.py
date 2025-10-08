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

class Frequency(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class FlowType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class Variability(models.Model):
    name = models.CharField(max_length=100, unique=True)
    flow_type = models.ForeignKey(FlowType, on_delete=models.CASCADE, verbose_name="Тип потока")

    def __str__(self):
        return self.name
    
class Item(models.Model):

    name = models.CharField(max_length=100, unique=True, verbose_name="Название")
    group = models.ForeignKey(Group, on_delete=models.PROTECT, verbose_name="Группа")
    flow_type = models.ForeignKey(FlowType, on_delete=models.PROTECT, verbose_name="Тип потока")
    variability = models.ForeignKey(Variability, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Изменчивость")


    def clean(self):
        if self.variability and self.variability.flow_type != self.flow_type:
            raise ValidationError(
                {"variability": "Тип изменчивости не соответсвует выбранному типу потока"}
            )
    def __str__(self):
        return self.name
