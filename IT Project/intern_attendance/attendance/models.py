from django.db import models
from django.utils import timezone

class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Intern(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Attendance(models.Model):
    intern = models.ForeignKey('Intern', on_delete=models.CASCADE)
    time_in = models.DateTimeField(default=timezone.now)  # Time in when intern marks attendance
    time_out = models.DateTimeField(null=True, blank=True)  # Time out when intern marks attendance

    def __str__(self):
        return f"{self.intern.name} - {self.time_in} - {self.time_out}"

