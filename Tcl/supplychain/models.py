from django.db import models

from app_user.models import AppUserModel

class SupplychainModel(models.Model):
    class Meta:
        db_table = 'supplychain'

    supplychain_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(AppUserModel,on_delete=models.CASCADE,null=False)


    #step - 1
    supply_chain_name = models.TextField(null=False)
    shipping_transportation_routes_information = models.TextField(null=False)
    gathering_data = models.TextField(null=True)
    social_impact = models.TextField(null=False)
    final_remarks = models.TextField(null=True,blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)    
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=1,unique=False)
    deleted = models.IntegerField(default=0,unique=False)



    def __str__(self):
        return f"({self.supply_chain_name},{self.shipping_transportation_routes_information},{self.gathering_data},{self.social_impact},{self.final_remarks})"