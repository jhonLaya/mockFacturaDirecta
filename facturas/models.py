from django.db import models

# Create your models here.

class Clients(models.Model):
    invoice_payload = models.JSONField()