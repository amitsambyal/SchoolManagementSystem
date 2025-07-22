from dal_select2.views import Select2QuerySetView
from webportal.models import Student
from django.shortcuts import render
from django.http import JsonResponse,HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Vehicle, LocationUpdate

class StudentAutocomplete(Select2QuerySetView):
    def get_queryset(self):
        qs = Student.objects.all()
        school_class_id = self.forwarded.get('school_class', None)
        if school_class_id:
            qs = qs.filter(school_class_id=school_class_id)
        else:
            qs = qs.none()
        return qs
    
def track_bus(request):
    if request.method == 'POST':
        bus_number = request.POST.get('bus_number')
        try:
            vehicle = Vehicle.objects.get(number=bus_number)
            latest_update = LocationUpdate.objects.filter(vehicle=vehicle).order_by('-timestamp').first()
            context = {
                'vehicle': vehicle,
                'latest_update': latest_update,
            }
            return render(request, 'track_bus.html', context)
        except Vehicle.DoesNotExist:
            return render(request, 'track_bus.html', {'error': 'Bus not found.'})
    return render(request, 'track_bus.html')  




@csrf_exempt  # Temporary for testing, should be secured in production
def update_location_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            vehicle_number = data.get('vehicle_number')
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            
            try:
                vehicle = Vehicle.objects.get(number=vehicle_number)
                # Create location update record
                LocationUpdate.objects.create(
                    vehicle=vehicle,
                    latitude=latitude,
                    longitude=longitude
                )
                # Update vehicle's current location
                vehicle.current_latitude = latitude
                vehicle.current_longitude = longitude
                vehicle.save()
                
                return JsonResponse({'status': 'success'})
            except Vehicle.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Vehicle not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@login_required
def driver_tracking_view(request):
    # Make sure only drivers can access this
    try:
        request.user.driver  # Check if user is a driver
    except:
        return HttpResponseForbidden("Access denied")
    
    vehicles = Vehicle.objects.filter(driver=request.user.driver)
    return render(request, 'driver_tracking.html', {'vehicles': vehicles})