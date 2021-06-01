from django.db import models

from app_user.models import AppUserModel

class ProfilePictureModel(models.Model):
    class Meta:
        db_table = 'profile_pictures'

    profilepictures_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(AppUserModel,on_delete=models.CASCADE,null=False)
    file_type = models.TextField()
    file_extension = models.TextField()
    aws_file_url = models.TextField()
    file_size = models.TextField()
    profilepicture_name = models.TextField()
    thumb_awsurl = models.TextField()
    thumb_name = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)    
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=1,unique=False)
    deleted = models.IntegerField(default=0,unique=False)

    def __str__(self):
        return f"({self.user_id},{self.file_type},{self.aws_file_url},{self.file_size})"