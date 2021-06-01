from django.db import models

class AppUserModel(models.Model):
    class Meta:
        db_table = 'appusers'

    appusers_id = models.AutoField(primary_key=True)
    first_name = models.TextField(null=True,blank=True)
    last_name = models.TextField(null=True,blank=True)
    email = models.TextField(null=False)
    cognito_id = models.TextField()
    city = models.TextField(null=True,blank=True)
    country = models.TextField(null=True,blank=True)
    phone = models.TextField(null=True,blank=True)
    user_type = models.TextField(null=False)
    newsletter = models.BooleanField()

    created_at = models.DateTimeField(auto_now_add=True)    
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=1,unique=False)
    deleted = models.IntegerField(default=0,unique=False)

    def __str__(self):
        return f"({self.first_name},{self.last_name},{self.email},{self.cognito_id},{self.city},{self.country},{self.phone})"