from django.db import models

class Vendor(models.Model):
    name = models.CharField(max_length=255, null=True)
    code = models.CharField(max_length=50, unique=False, null=True)

    def __str__(self):
        return self.name


class VendorGradeData(models.Model):
    vendor = models.OneToOneField(Vendor, on_delete=models.CASCADE, related_name='grade_data')
    short_name = models.CharField(max_length=255, null=True)


class VendorYearGrade(models.Model):
    vendor_grade = models.ForeignKey(VendorGradeData, on_delete=models.CASCADE, related_name='year_grades')
    year = models.IntegerField()
    grade = models.CharField(max_length=50, null=True)


class VendorSpendData(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='spend_data')
    overall_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    def calculate_overall_total(self):
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
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='matrix_data')
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
