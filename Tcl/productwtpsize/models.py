from django.db import models
from product.models import ProductModel
from product.models import AttributeValueModel

# Create your models here.
class ProductWtpSizeModel(models.Model):
    productwtpsize_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE)
    size_weight = models.TextField(null=True)
    attribute_value=models.ForeignKey(AttributeValueModel,on_delete=models.CASCADE,default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=1, unique=False)
    deleted = models.IntegerField(default=0, unique=False)

    class Meta:
        db_table = "product_wt_p_size"
