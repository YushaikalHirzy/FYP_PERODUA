from django.db import models

class ExcelData(models.Model):
    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10)
    address = models.CharField(max_length=255)
    # Add more fields depending on your Excel structure

    def __str__(self):
        return f"{self.name} - {self.gender} - {self.address}"