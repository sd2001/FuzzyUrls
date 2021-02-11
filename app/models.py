from django.db import models

# Create your models here.
class URL(models.Model):
    link = models.CharField(max_length = 1000)
    new = models.CharField(max_length = 6)
    uid = models.CharField(max_length = 50)
