from django.db import models
from django.core.exceptions import ValidationError


def validate_product_availability(product, order):
    from .models import OrderProduct
    overlapping_orders = OrderProduct.objects.filter(
        product=product,
        order__start_date__lt=order.end_date,
        order__end_date__gt=order.start_date
    ).exclude(id=order.id)
    
    if overlapping_orders.exists():
        raise ValidationError('This product is already rented during this period.')


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField()

    def __str__(self):
        return self.name

class Order(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    total_price = models.FloatField()

    def __str__(self):
        return f"Order {self.id} from {self.start_date} to {self.end_date}"
    
class OrderProduct(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    price = models.FloatField()
    rental_duration = models.IntegerField(help_text="Duration in days")

    class Meta:
        unique_together = ('order', 'product')

    def clean(self):
        validate_product_availability(self.product, self.order)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
