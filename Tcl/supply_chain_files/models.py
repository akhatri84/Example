from django.db import models

from supplychain.models import SupplychainModel

class SupplychainFilesModel(models.Model):
    class Meta:
        db_table = 'supplychain_files'

    supplychainfiles_id = models.AutoField(primary_key=True)
    supply_chain_id = models.ForeignKey(SupplychainModel,on_delete=models.CASCADE,null=False)
    file_type = models.TextField(null=False)
    file_extension = models.TextField(null=False)
    aws_file_url = models.TextField(null=False)
    file_size = models.TextField(null=False)
    supplychain_filename = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)    
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=1,unique=False)
    deleted = models.IntegerField(default=0,unique=False)

    def __str__(self):
        return f"({self.supply_chain_id},{self.file_type},{self.aws_file_url},{self.file_size})"
