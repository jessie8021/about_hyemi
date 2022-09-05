from django.db import models
from accounts.models import  CustomUser

class Post(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField()

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d/', blank=True)
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    author = models.ForeignKey(CustomUser, null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'posts'


    def __str__(self):
        return f'[{self.pk}]{self.title}'