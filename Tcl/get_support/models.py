from django.db import models

from app_user.models import AppUserModel

class GetSupportModel(models.Model):
    class Meta:
        db_table = "get_support"
    getsupport_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(AppUserModel,on_delete=models.CASCADE,null=False)
    support_content = models.TextField(null=False)
    status = models.TextField(default="submitted")

    created_at = models.DateTimeField(auto_now_add=True)    
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=1,unique=False)
    deleted = models.IntegerField(default=0,unique=False)

    def __str__(self):
        return f"({self.support_content})"