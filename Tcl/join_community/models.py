from django.db import models


# Create your models here.
class JoinCommunityModel(models.Model):
    joincommunity_id = models.AutoField(primary_key=True)
    fname = models.TextField(null=True)
    lname = models.TextField(null=True)
    email = models.TextField(null=True)
    phone = models.TextField(null=True)
    company = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=1, unique=False)
    deleted = models.IntegerField(default=0, unique=False)

    class Meta:
        db_table = "join_community"
