from unittest.util import _MAX_LENGTH
from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime    
from django.utils.timezone import now


class CustomUser(AbstractUser):
    #username = models.DateTimeField(auto_now_add=True,blank=True)
    username = models.CharField(max_length=150,unique=True,blank=True)
    userfirstname = models.CharField(max_length=50)
    userlastname = models.CharField(max_length=50)
    email = models.CharField(max_length=50,unique=True)
    password = models.CharField(max_length=50)
    is_admin = models.BooleanField(default=False)
    #leaveid = models.ForeignKey('Leave', on_delete=models.CASCADE)
    gender = models.CharField(max_length=50)
    paternity = models.IntegerField(default=0)
    maternity = models.IntegerField(default=0)
    paid = models.IntegerField(default=30)
    rtt = models.IntegerField(default=0)
    id = models.AutoField(primary_key=True)
    def __int__(self):
        return self.id
class Leave(models.Model):
    startdate= models.DateTimeField(blank=False)
    enddate = models.DateTimeField(blank=False)
    days = models.IntegerField(default=0)
    leavetype = models.CharField(max_length=100,default="")
    userid = models.IntegerField(default=0)
    status = models.CharField(max_length=100,default="")
    id = models.AutoField(primary_key=True)
    def __int__(self):
        return self.id


# when adding new field
# run python manage.py migrate --run-syncdb