from django.db import models

class VendorGradeData(models.Model):
    num = models.CharField(max_length=50, null=True)
    vendor = models.CharField(max_length=255, null=True)
    short_name = models.CharField(max_length=255, null=True)
    vendor_code = models.CharField(max_length=50, null=True)

class VendorYearGrade(models.Model):
    vendor_grade = models.ForeignKey(
        VendorGradeData, 
        on_delete=models.CASCADE, 
        related_name='year_grades'
    )
    year = models.IntegerField()
    grade = models.CharField(max_length=50, null=True)

class VendorSpendData(models.Model):
    vendor = models.CharField(max_length=255, null=True)
    vendor_code = models.CharField(max_length=50, null=True)
    overall_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    def calculate_overall_total(self):
        # Use self.details instead of self.VendorSpendDetail
        total = self.details.aggregate(
            total=models.Sum('grand_total')
        )['total'] or 0
        self.overall_total = total
        return total

class VendorSpendDetail(models.Model):
    vendor_spend_data = models.ForeignKey(VendorSpendData, on_delete=models.CASCADE, related_name='details')
    year = models.IntegerField()
    grand_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)


class VendorMatrixData(models.Model):
    vendor = models.CharField(max_length=255, null=True)
    remarks = models.TextField(null=True)
    ongoing_project = models.TextField(null=True)
    status = models.TextField(null=True)

class ProgramAttribute(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

class VendorProgramValue(models.Model):
    vendor_matrix = models.ForeignKey(VendorMatrixData, on_delete=models.CASCADE, related_name='program_values')
    program = models.ForeignKey(ProgramAttribute, on_delete=models.CASCADE)
    value = models.TextField(null=True)

    class Meta:
        unique_together = ('vendor_matrix', 'program')






    def __str__(self):
        return f"{self.vendor} - {self.short_name} - {self.vendor_code} - {self.overall_2018} - {self.overall_2019} - {self.overall_2020} - {self.overall_2021} - {self.overall_2022}" 