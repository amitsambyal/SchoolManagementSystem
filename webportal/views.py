from django.shortcuts import render
from .models import favicon, logo, CarouselItem, SchoolClass, SchoolFacility, AboutUs, CallToAction, \
      Teacher, Appointment, TeamMember, Testimonial, FooterNewsletter, FooterSocialLink
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

    content = {
        'carouselItem': carouselItem,
        'schoolfacility': schoolfacility,
        'aboutus': aboutus,
        'calltoaction': calltoaction,
        'favicon1': favicon1,
        'logo1': logo1,
        'schoolclass': schoolclass,
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
