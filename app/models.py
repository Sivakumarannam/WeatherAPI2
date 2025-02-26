from django.db import models

# Create your models here.

from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", blank=True, null=True)
    address=models.TextField(blank=True, null=True)
    profile_pic=models.ImageField(upload_to='images', blank=True, null=True)
    def __str__(self):
        return f"{self.user.username} Profile"


class WeatherData(models.Model):
    username=models.ForeignKey(User,on_delete=models.CASCADE,default=0)
    city = models.CharField(max_length=100)
    temperature = models.DecimalField(max_digits=5, decimal_places=2)
    humidity = models.DecimalField(max_digits=5, decimal_places=2)
    weather=models.CharField(max_length=10,default=0)
    speed=models.CharField(max_length=10,default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Weather in {self.city} at {self.timestamp}"


