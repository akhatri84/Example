from django.db import models
 

from supplychain.models import SupplychainModel


class ProducerManufacturerModel(models.Model):
    class Meta:
        db_table = 'producer_manufacturer'

    producermanufacturer_id = models.AutoField(primary_key=True)
    supply_chain_id = models.ForeignKey(SupplychainModel,on_delete=models.CASCADE,null=False)
    producer_name = models.TextField(null=False)
    process = models.TextField(null=False)
    city = models.TextField(null=False)
    country = models.TextField(null=False)
    
    
    created_at = models.DateTimeField(auto_now_add=True)    
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=1,unique=False)
    deleted = models.IntegerField(default=0,unique=False)

    def __str__(self):
        return f"({self.producer_name},{self.process},{self.city},{self.country})"