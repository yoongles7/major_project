from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    virtual_balance = models.DecimalField(max_digits=12, decimal_places=2, default=100000)
    created_at = models.DateTimeField(auto_now_add=True)