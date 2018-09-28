from django.db import models

# Create your models here.
class Company(models.Model):
    companyid = models.AutoField(primary_key = True)
    name = models.CharField(max_length = 100, blank = False, null = False)

class CompanyRole(models.Model):
    ROLES = [("Customer","Customer"),
             ("Vendor","Vendor")]
    roleid = models.AutoField(primary_key = True)
    company = models.ForeignKey(Company, on_delete = models.CASCADE, blank = False, null = False)
    role = models.CharField(max_length = 100, choices = ROLES, blank = False, null = False)

