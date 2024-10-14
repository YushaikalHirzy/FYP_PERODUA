from django.db import models

class ExcelData(models.Model):
    # Add more fields depending on your Excel structure
    num = models.CharField(max_length=50,null=True)
    vendor = models.CharField(max_length=255, null=True)
    short_name = models.CharField(max_length=255, null=True)
    vendor_code = models.CharField(max_length=50, null=True)
    overall_2018 = models.CharField(max_length=50, null=True)
    overall_2019 = models.CharField(max_length=50, null=True)
    overall_2020 = models.CharField(max_length=50, null=True)
    overall_2021 = models.CharField(max_length=50, null=True)
    overall_2022 = models.CharField(max_length=50, null=True)

    def __str__(self):
        return f"{self.vendor} - {self.short_name} - {self.vendor_code} - {self.overall_2018} - {self.overall_2019} - {self.overall_2020} - {self.overall_2021} - {self.overall_2022}" 