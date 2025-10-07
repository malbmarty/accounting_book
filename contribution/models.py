from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

# Create your models here.
class OperationalAccounting(models.Model):
    payment_date = models.DateField(verbose_name="Дата платежа (ОДДС)", null=True, blank=True)
    recognition_date = models.DateField(verbose_name="Дата признания (ОПУ)", null=True, blank=True)
    payer = models.ForeignKey(
        'analytics_dir.Participant', 
        on_delete=models.PROTECT, 
        verbose_name="Плательщик", 
        null=True, blank=True,
        related_name='acc_as_payer')
    recipient = models.ForeignKey(
        'analytics_dir.Participant', 
        on_delete=models.PROTECT, 
        verbose_name="Получатель",
        related_name='acc_as_recipient')
    item = models.ForeignKey('analytics_dir.Item', on_delete=models.PROTECT, verbose_name="Статья")
    payment_system = models.ForeignKey('analytics_dir.PaymentSystem', on_delete=models.PROTECT, verbose_name="Платежная система")
    project = models.ForeignKey('analytics_dir.Project', on_delete=models.PROTECT, verbose_name="Проект", null=True, blank=True,)
    payment_amount = models.DecimalField(
            decimal_places=2, 
            max_digits=20,
            null=True, 
            blank = True, 
            validators=[MinValueValidator(0.01)],
            verbose_name="Сумма оплаты") 
    counterparty = models.ForeignKey('analytics_dir.Counterparty', on_delete=models.PROTECT, verbose_name="Контрагент")
    commission_amount = models.DecimalField(
            decimal_places=2, 
            max_digits=20,
            null=True, 
            blank = True, 
            validators=[MinValueValidator(0.01)],
            verbose_name="Сумма комиссии")
    comment = models.CharField(max_length=100, null=True, blank=True, verbose_name="Комментарий")

        # Проверка выполнения бизнес-правил
    def clean(self):
        
        if self.payer == self.recipient:
            raise ValidationError({
                'recipient': 'Плательщик и получатель не могут быть одинаковыми'
                })
        
    def save(self, *args, **kwargs):
        """Переопределение save для автоматической валидации"""
        self.full_clean()
        super().save(*args, **kwargs)
    

class Planning(models.Model):
    FREQUENCY_CHOICES = [
        ('once', 'Разово'),
    ] + [(str(i), f'{i} мес.') for i in range(2, 13)]
    date = models.DateField(verbose_name="Дата ОДДС")
    project = models.ForeignKey('analytics_dir.Project', on_delete=models.PROTECT, verbose_name="Проект", null=True, blank=True)
    item = models.ForeignKey('analytics_dir.Item', on_delete=models.PROTECT, verbose_name="Статья")
    payment_amount = models.DecimalField(
            decimal_places=2, 
            max_digits=20,
            null=True, 
            blank = True, 
            validators=[MinValueValidator(0.01)],
            verbose_name="Сумма")
    frequency = models.CharField(
        max_length=5,
        choices=FREQUENCY_CHOICES,
        default='once',
        verbose_name="Частота платежа"
    )
    comment = models.CharField(max_length=100, null=True, blank=True, verbose_name="Примечание")