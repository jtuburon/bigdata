from django.db import models

# Create your models here.
from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100, blank=True, default='')
    url = models.CharField(max_length=300, blank=True, default='')

    class Meta:        
        managed = False


class Teacher(models.Model):
    name = models.CharField(max_length=100, blank=True, default='')
    email = models.CharField(max_length=100, blank=True, default='')
    dependency = models.CharField(max_length=100, blank=True, default='')
    rangekind = models.CharField(max_length=100, blank=True, default='')
    extension = models.CharField(max_length=20, blank=True, default='')
    webpage = models.CharField(max_length=100, blank=True, default='')

    class Meta:        
        managed = False

class New(models.Model):
    title = models.CharField(max_length=100, blank=True, default='')
    pubdate = models.CharField(max_length=100, blank=True, default='')
    link = models.CharField(max_length=150, blank=True, default='')
    
    class Meta:        
        managed = False