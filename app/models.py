from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class ActivityTrackModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True

class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

class Client(ActivityTrackModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    
    @property
    def id(self):
        return self.user.id
    
    @property
    def username(self):
        return self.user.username
    
    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if not self.is_active:
            Warehouse.objects.filter(client=self).update(is_active=False)
            RecordsModel.objects.filter(warehouse__client=self).update(is_active=False)
        super().save(*args, **kwargs)

class Warehouse(ActivityTrackModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='warehouses')
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.is_active:
            RecordsModel.objects.filter(warehouse=self).update(is_active=False)
        super().save(*args, **kwargs)

class RecordsModel(ActivityTrackModel):
    id_record = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="records")
    type_record = models.CharField(max_length=10, choices=[("IN", "ENTRY"), ("OUT", "EXIT")])
    quantity = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.warehouse.address} - {self.id_record}"
