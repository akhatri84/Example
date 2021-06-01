from django.db import models
from product.models import ProductModel
from product.models import AttributeValueModel


# Create your models here.
class ImpactSizeModel(models.Model):
    impactsize_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE)
    attribute_value=models.ForeignKey(AttributeValueModel,on_delete=models.CASCADE,null=True)
    weight = models.TextField(null=True)
    kgco2 = models.TextField(null=True)
    liter = models.TextField(null=True)
    kmtravel = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=1, unique=False)
    deleted = models.IntegerField(default=0, unique=False)

    class Meta:
        db_table = "impact_size"
