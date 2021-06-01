# coding=utf-8
from django.db import models

from app_user.models import AppUserModel

class RequestQuoteModel(models.Model):
    class Meta:
        db_table = 'request_quote'

    request_quote_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(AppUserModel,on_delete=models.CASCADE,null=False)
    quote_content =models.TextField()
    status = models.TextField(default="pending")
    
    created_at = models.DateTimeField(auto_now_add=True)    
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=1,unique=False)
    deleted = models.IntegerField(default=0,unique=False)

    def __str__(self):
        return f"({self.request_quote_id},{self.quote_content},{self.user_id})"
