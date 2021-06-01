from django.db import models

from product.models import ProductModel

class MaterialCompositionModel(models.Model):
    class Meta:
        db_table = 'material_composition'

    materialcomposition_id = models.AutoField(primary_key=True)
    product_id = models.ForeignKey(ProductModel,on_delete=models.CASCADE,null=False)
    material_name = models.TextField()
    percentage = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)    
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=1,unique=False)
    deleted = models.IntegerField(default=0,unique=False)

    def __str__(self):
        return f"({self.product_id},{self.material_name},{self.percentage})"
