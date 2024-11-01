from django.db import models

# Create your models here.
class Response(models.Model):
    id = models.AutoField(primary_key=True)
    response = models.CharField(max_length=1024)

class Connection(models.Model):
    ip = models.CharField(primary_key=True, max_length=256)
    command_history = models.CharField(max_length=512)
    response_id = models.OneToOneField(Response, on_delete=models.CASCADE)