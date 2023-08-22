from django.db import models


class WorkPlace(models.Model):
    id = models.BigIntegerField(primary_key=True, null=False)
    name = models.CharField(max_length=500, null=False)
    short_name = models.CharField(max_length=500, null=False)


class Group(models.Model):
    name = models.CharField(primary_key=True, max_length=100, null=False)
    course = models.IntegerField(null=False)
    faculty_name = models.CharField(max_length=500, null=False)
    qualification_name = models.CharField(max_length=500, null=True)


class IsuData(models.Model):
    t_user_id = models.BigIntegerField(primary_key=True, null=False)
    sub = models.TextField(null=False, unique=True)
    gender = models.CharField(max_length=100, null=False)
    name = models.CharField(max_length=500, null=False)
    isu = models.BigIntegerField(null=True)
    preferred_username = models.CharField(max_length=100, null=False)
    given_name = models.CharField(max_length=100, null=False)
    middle_name = models.CharField(max_length=100, null=True)
    family_name = models.CharField(max_length=100, null=False)
    email = models.CharField(max_length=1000, null=False)
    email_verified = models.BooleanField(null=False)
    is_student = models.BooleanField(null=False)
    is_worker = models.BooleanField(null=False)
    groups = models.ManyToManyField(Group)
    work_places = models.ManyToManyField(WorkPlace)
