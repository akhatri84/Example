# coding=utf-8
from django.db import models

from app_user.models import AppUserModel

class ApiConfigModel(models.Model):
    class Meta:
        db_table = 'api_config'

    apiconfig_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(AppUserModel,on_delete=models.CASCADE,null=False)
    api_key = models.TextField(null=False)
    secret_key = models.TextField(null=False)
    pwd = models.TextField()
    apiend_point = models.TextField()
    platform = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)    
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=1,unique=False)
    deleted = models.IntegerField(default=0,unique=False)

    def __str__(self):
        return f"({self.pwd},{self.apiend_point},{self.platform})"

