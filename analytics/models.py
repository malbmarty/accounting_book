from django.db import models

# Create your models here.
class CounterpartyOpeningBalance(models.Model):
    counterparty = models.ForeignKey("analytics_dir.Counterparty", on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ('counterparty', 'year')
