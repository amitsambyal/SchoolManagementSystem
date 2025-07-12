from django.contrib import admin
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.utils import timezone
from .models import Vehicle, Route, TransportAssignment, Driver, MeterReading
from .forms import TransportAssignmentForm

class TransportAssignmentAdmin(admin.ModelAdmin):
    form = TransportAssignmentForm
    list_display = ('student', 'school_class', 'vehicle', 'route')
    list_filter = ('school_class', 'vehicle', 'route')  # Added vehicle and route filters

admin.site.register(Vehicle)
admin.site.register(Route)
admin.site.register(TransportAssignment, TransportAssignmentAdmin)

class DriverAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'contact', 'license_number')
    exclude = ('user',)  # Hide the user field in the admin form

    def save_model(self, request, obj, form, change):
        if not change:
            password = get_random_string(8)
            user = User.objects.create_user(
                username=obj.email,
                email=obj.email,
                password=password,
                first_name=obj.name
            )
            obj.user = user  # Link the user to the driver
            send_mail(
                'Your Driver Account Created',
                f'Hello {obj.name},\n\nYour driver account has been created.\nUsername: {obj.email}\nPassword: {password}\n\nPlease log in and change your password.',
                'admin@yourschool.com',
                [obj.email],
                fail_silently=False,
            )
        super().save_model(request, obj, form, change)

admin.site.register(Driver, DriverAdmin)

class MeterReadingAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'driver', 'date', 'start_meter_value', 'end_meter_value', 'distance_covered')
    list_filter = ('vehicle', 'driver', 'date')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        today = timezone.localdate()
        try:
            driver = Driver.objects.get(user=request.user)
            return qs.filter(driver=driver, date=today)
        except Driver.DoesNotExist:
            return qs

    def get_readonly_fields(self, request, obj=None):
        # If driver, restrict fields; if admin, allow all
        try:
            driver = Driver.objects.get(user=request.user)
            # Driver can only edit end_meter_value, end_time, remarks
            readonly = ['vehicle', 'driver', 'date', 'start_meter_value', 'start_time']
            if obj and obj.date != timezone.localdate():
                # Prevent editing if not today
                return [f.name for f in obj._meta.fields]
            return readonly
        except Driver.DoesNotExist:
            # Admin: only make driver field readonly if editing
            if obj:
                return ['driver']
            return []

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        try:
            driver = Driver.objects.get(user=request.user)
        except Driver.DoesNotExist:
            driver = None

        if db_field.name == "vehicle" and driver:
            kwargs["queryset"] = Vehicle.objects.filter(driver=driver)
        if db_field.name == "driver" and driver:
            kwargs["queryset"] = Driver.objects.filter(pk=driver.pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        today = timezone.localdate()
        try:
            driver = Driver.objects.get(user=request.user)
            obj.driver = driver
            obj.date = today
            # If creating a new reading, set start_meter_value from yesterday's end_meter_value
            if not change:
                from datetime import timedelta
                yesterday = today - timedelta(days=1)
                last_reading = MeterReading.objects.filter(
                    vehicle=obj.vehicle, date=yesterday
                ).order_by('-date').first()
                if last_reading and last_reading.end_meter_value is not None:
                    obj.start_meter_value = last_reading.end_meter_value
        except Driver.DoesNotExist:
            pass
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        # Only allow editing today's reading
        if obj is not None:
            today = timezone.localdate()
            return obj.date == today or request.user.is_superuser
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        # Only allow deleting today's reading
        if obj is not None:
            today = timezone.localdate()
            return obj.date == today or request.user.is_superuser
        return super().has_delete_permission(request, obj)

admin.site.register(MeterReading, MeterReadingAdmin)

