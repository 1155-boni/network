
from django.db import models

# Create your models here.
class Socialnetwork(models.Model):
    id = models.AutoField(primary_key=True)

    def __str__(self):
        pass
        