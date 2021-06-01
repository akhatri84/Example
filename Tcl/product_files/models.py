from django.db import models

from product.models import ProductModel

class ProductFilesModel(models.Model):
    class Meta:
        db_table = 'product_files'
    productfiles_id = models.AutoField(primary_key=True)
    product_id = models.ForeignKey(ProductModel,on_delete=models.CASCADE,null=False)
    file_type = models.TextField()
    file_extension = models.TextField()
    aws_file_url = models.TextField()
    file_size = models.TextField()
    productfile_name = models.TextField()
    store_file_id = models.TextField(null=True)


    created_at = models.DateTimeField(auto_now_add=True)    
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=1,unique=False)
    deleted = models.IntegerField(default=0,unique=False)


    def __str__(self):
        return f"({self.product_id},{self.file_type},{self.aws_file_url},{self.file_size})"
