# coding=utf-8
import datetime
from django.db import models
from datetime import datetime 

from app_user.models import AppUserModel

class OnboardingModel(models.Model):
    class Meta:
        db_table = 'onboarding'

    onboarding_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(AppUserModel,on_delete=models.CASCADE,null=False)

    company = models.TextField(null=False)
    website = models.TextField(null=True)
    about_brand = models.TextField(null=False)
    remarks = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)    
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=1,unique=False)
    deleted = models.IntegerField(default=0,unique=False)


    def __str__(self):
        return f"({self.company},{self.website},{self.about_brand},{self.remarks})"
