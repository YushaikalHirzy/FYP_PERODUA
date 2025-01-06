from django.db import models

class VendorGradeData(models.Model):
    num = models.CharField(max_length=50,null=True)
    vendor = models.CharField(max_length=255, null=True)
    short_name = models.CharField(max_length=255, null=True)
    vendor_code = models.CharField(max_length=50, null=True)
    overall_2018 = models.CharField(max_length=50, null=True)
    overall_2019 = models.CharField(max_length=50, null=True)
    overall_2020 = models.CharField(max_length=50, null=True)
    overall_2021 = models.CharField(max_length=50, null=True)
    overall_2022 = models.CharField(max_length=50, null=True)

class VendorSpendData(models.Model):
    vendor = models.CharField(max_length=255, null=True)
    vendor_code = models.CharField(max_length=50, null=True)
    grand_total_2019 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    grand_total_2020 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    grand_total_2021 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    grand_total_2022 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    grand_total_2023 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    overall_5_years = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

class VendorMatrixData(models.Model): 
    vendor = models.CharField(max_length=255, null=True)
    gipv = models.TextField(null=True)
    cost_reduction_activity = models.TextField(null=True)
    ppkv = models.TextField(null=True)
    dte = models.TextField(null=True)
    beep = models.TextField(null=True)
    tmiep = models.TextField(null=True)
    trade_mission = models.TextField(null=True)
    lean_mgmt = models.TextField(null=True)
    kaizen = models.TextField(null=True)
    icc = models.TextField(null=True)
    contract_nego_skill = models.TextField(null=True)
    sspoa = models.TextField(null=True)
    espo = models.TextField(null=True)
    vip2 = models.TextField(null=True)
    ir4 = models.TextField(null=True)
    remarks = models.TextField(null=True)
    ongoing_project = models.TextField(null=True) 
    status = models.TextField(null=True)






    def __str__(self):
        return f"{self.vendor} - {self.short_name} - {self.vendor_code} - {self.overall_2018} - {self.overall_2019} - {self.overall_2020} - {self.overall_2021} - {self.overall_2022}" 