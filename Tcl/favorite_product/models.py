from django.db import models
from product.models import ProductModel
from app_user.models import AppUserModel


class FavoriteProductModel(models.Model):
    class Meta:
        db_table = 'favoriteproduct'

    favoriteproduct_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, null=False)
    user_id = models.ForeignKey(AppUserModel, on_delete=models.CASCADE,null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=1, unique=False)
    deleted = models.IntegerField(default=0, unique=False)

    def __str__(self):
        return f"({self.product_id})"
