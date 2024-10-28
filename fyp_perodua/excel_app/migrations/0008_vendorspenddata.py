# Generated by Django 5.1.1 on 2024-10-21 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('excel_app', '0007_delete_vendorspenddata'),
    ]

    operations = [
        migrations.CreateModel(
            name='VendorSpendData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grand_total_2019', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('grand_total_2020', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('grand_total_2021', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('grand_total_2022', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('grand_total_2023', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('overall_5_years', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
            ],
        ),
    ]
