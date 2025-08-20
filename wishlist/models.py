# wishlist/models.py
from django.db import models
from store.models import Product, Variation
from accounts.models import Account

class Wishlist(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)  # store selected variations
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.product_name} - {self.user.email}"
