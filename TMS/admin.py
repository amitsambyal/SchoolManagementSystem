from django.contrib import admin
from .models import Vehicle, Route, TransportAssignment
from .forms import TransportAssignmentForm

class TransportAssignmentAdmin(admin.ModelAdmin):
    form = TransportAssignmentForm
    list_display = ('student', 'school_class', 'vehicle', 'route')
    list_filter = ('school_class', 'vehicle', 'route')  # Added vehicle and route filters

admin.site.register(Vehicle)
admin.site.register(Route)
admin.site.register(TransportAssignment, TransportAssignmentAdmin)
