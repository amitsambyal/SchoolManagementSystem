from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import favicon, logo, CarouselItem, SchoolClass, SchoolFacility, AboutUs, CallToAction, \
      Teacher, Appointment, TeamMember, Testimonial, FooterNewsletter, FooterSocialLink, SchoolClass, Syllabus, Subject
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse

# Create your views here.

def index(request):
    carouselItem = CarouselItem.objects.all()
    schoolfacility = SchoolFacility.objects.all()
    aboutus = AboutUs.objects.all()
    calltoaction = CallToAction.objects.all()
    favicon1 = favicon.objects.all()
    logo1 = logo.objects.all()
    schoolclass = SchoolClass.objects.all()
    teacher = Teacher.objects.all()
    appointment = Appointment.objects.all()
    teamMember = TeamMember.objects.all()
    testimonial = Testimonial.objects.all()
    footerNewsletter = FooterNewsletter.objects.all()
    footerSocialLink = FooterSocialLink.objects.all()

    # Prepare subjects grouped by class
    subjects_by_class = {}
    for school_class in schoolclass:
        subjects_by_class[school_class.id] = school_class.subjects.all()

    # Process team members profile pictures
    for member in teamMember:
        if not member.profile_picture:
            member.profile_picture_url = None
        else:
            member.profile_picture_url = member.profile_picture.url

    content = {
        'carouselItem': carouselItem,
        'schoolfacility': schoolfacility,
        'aboutus': aboutus,
        'calltoaction': calltoaction,
        'favicon1': favicon1,
        'logo1': logo1,
        'schoolclass': schoolclass,
        'subjects_by_class': subjects_by_class,
        'teacher': teacher,
        'appointment': appointment,
        'teammember': teamMember,
        'testimonial': testimonial,
        'footerNewsletter': footerNewsletter,
        'footerSocialLink': footerSocialLink
    }
    return render(request, 'webportal/index.html', content)

def about(request):
    return render(request, 'webportal/about.html')

def contact(request):
    return render(request, 'webportal/contact.html')

def privacy_policy(request):
    return render(request, 'webportal/privacy-policy.html')

def syllabus(request):
    schoolclass = SchoolClass.objects.prefetch_related('subjects').all()
    return render(request, 'webportal/syllabus.html', {'schoolclass': schoolclass})

# Custom Login View
class CustomLoginView(LoginView):
    def form_valid(self, form):
        user = form.get_user()
        if user.check_password('defaultpassword'):
            # Log the user in
            login(self.request, user)
            # Redirect to password change page
            return redirect('password_change')  # Ensure this URL name matches your password change view
        return super().form_valid(form)

def get_subjects_by_class(request, class_id):
    school_class = get_object_or_404(SchoolClass, id=class_id)
    subjects = school_class.subjects.all()
    subject_data = [{'id': subject.id, 'name': subject.name} for subject in subjects]
    return JsonResponse({'subjects': subject_data})


