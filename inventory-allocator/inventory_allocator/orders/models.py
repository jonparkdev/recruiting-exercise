from django.db import models

# Create your models here.

class Warehouse(models.Model):
    name = models.CharField(primary_key=True, max_length=100)
    lat = models.DecimalField(max_digits=9, decimal_places=6, blank=False)
    lng = models.DecimalField(max_digits=9, decimal_places=6, blank=False)

    def __str__(self):
        return f'{self.name} Warehouse'


class Item(models.Model):
    name = models.CharField(primary_key=True, max_length=100)

    def __str__(self):
        return self.name


class Inventory(models.Model):
    warehouse = models.ForeignKey('Warehouse', on_delete=models.CASCADE)
    item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name='item')
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.warehouse}: {self.item}-{self.quantity}'

    class Meta:
        constraints = [models.UniqueConstraint(fields=['warehouse','item'], name='item_inventory')]
