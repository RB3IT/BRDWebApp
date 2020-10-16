from django.db import models


class Entity(models.Model):
    entityid = models.AutoField(primary_key = True)
    name = models.CharField(max_length = 100, blank = False, null = False)

class Company(models.Model):
    companyid = models.AutoField(primary_key = True)
    entity_id = models.ForeignKey(Entity, on_delete = "CASCADE", unique = True)

class CompanyRole(models.Model):
    ROLES = [("Customer","Customer"),
             ("Vendor","Vendor")]
    roleid = models.AutoField(primary_key = True)
    company = models.ForeignKey(Company, on_delete = models.CASCADE, blank = False, null = False)
    role = models.CharField(max_length = 100, choices = ROLES, blank = False, null = False)

class Person(models.Model):
    personid = models.AutoField(primary_key= True)
    entity = models.ForeignKey(Entity, on_delete = "CASCADE", unique = True)
    first_name = models.CharField(max_length = 100, blank = True, null = True)
    last_name = models.CharField(max_length = 100, blank = True, null = True)
    suffix = models.CharField(max_length = 5, blank = True, null = True)

    @property
    def fullname(self):
        output = ""
        for at in [self.first_name, self.last_name, self.suffix]:
            if at: output += at
        return output

class CompanyEmployee(models.Model):
    employeeid = models.AutoField(primary_key = True)
    person = models.ForeignKey(Person, on_deleted = "CASCADE")
    company = models.ForeignKey(Company, on_deleted = "CASCADE")
    role = models.CharField(max_length = 255, blank = True, null = True)

    unique_together = ["person", "company"]

