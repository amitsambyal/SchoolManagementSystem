from django.shortcuts import render, get_object_or_404
from .models import favicon, logo, CarouselItem, SchoolClass, SchoolFacility, AboutUs, CallToAction, \
      Teacher, Appointment, TeamMember, Testimonial, FooterNewsletter, FooterSocialLink, SchoolClass, Syllabus
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

def syllabus_list(request, class_id):
    school_class = get_object_or_404(SchoolClass, id=class_id)
    syllabi = Syllabus.objects.filter(subject__school_class=school_class).order_by('subject__name', 'title')
    context = {
        'school_class': school_class,
        'syllabi': syllabi,
    }
    return render(request, 'webportal/syllabus_list.html', context)

def syllabus_by_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    syllabi = Syllabus.objects.filter(subject=subject).order_by('title')
    context = {
        'subject': subject,
        'syllabi': syllabi,
    }
    return render(request, 'webportal/syllabus_list.html', context)

