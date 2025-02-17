from django.db import models

# Create your models here.
class Connection(models.Model):
    ip = models.CharField(primary_key=True, max_length=256)
    cpu = models.CharField(max_length=128)
    node_name = models.CharField(max_length=64)
    os = models.CharField(max_length=64)
    version = models.CharField(max_length=64)
    recent_status = models.CharField(max_length=16)
    
class CommandHistory(models.Model):
    id = models.AutoField(primary_key=True)
    time = models.CharField(max_length=30)
    ip = models.ForeignKey(Connection, on_delete=models.CASCADE)
    command = models.CharField(max_length=512)
    response = models.TextField()
