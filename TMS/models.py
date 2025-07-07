from django.db import models

# Create your models here.

class Vehicle(models.Model):
    VEHICLE_TYPE_CHOICES = [
        ('bus', 'Bus'),
        ('van', 'Van'),
        ('car', 'Car'),
        ('other', 'Other'),
    ]
    number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPE_CHOICES)
    capacity = models.PositiveIntegerField()
    driver_name = models.CharField(max_length=100)
    driver_contact = models.CharField(max_length=20)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.number} ({self.get_vehicle_type_display()})"

class Route(models.Model):
    name = models.CharField(max_length=100, unique=True)
    start_point = models.CharField(max_length=100)
    end_point = models.CharField(max_length=100)
    stops = models.TextField(help_text="Comma-separated list of stops")

    def __str__(self):
        return self.name

class TransportAssignment(models.Model):
    school_class = models.ForeignKey('webportal.SchoolClass', on_delete=models.CASCADE)
    student = models.ForeignKey('webportal.Student', on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True)
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True)
    pickup_point = models.CharField(max_length=100)
    drop_point = models.CharField(max_length=100)
    assigned_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.route} - {self.vehicle}"
