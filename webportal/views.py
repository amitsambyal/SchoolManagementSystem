from django.shortcuts import render
from .models import favicon,logo,CarouselItem,SchoolClass,SchoolFacility,AboutUs,CallToAction,\
      Teacher,Appointment,TeamMember,Testimonial,FooterNewsletter,FooterSocialLink

# Create your views here.

def index(request):
    carouselItem=CarouselItem.objects.all()
    schoolfacility=SchoolFacility.objects.all()
    aboutus=AboutUs.objects.all()
    calltoaction=CallToAction.objects.all()
    #favicon=favicon.objects.all()
    #logo=logo.objects.all()
    schoolclass=SchoolClass.objects.all()
    teacher=Teacher.objects.all()
    appointment=Appointment.objects.all()
    teamMember=TeamMember.objects.all()
    testimonial=Testimonial.objects.all()
    footerNewsletter=FooterNewsletter.objects.all()
    footerSocialLink=FooterSocialLink.objects.all()
   
    
    
    content={'carouselItem':carouselItem, 'schoolfacility': schoolfacility, 'aboutus':aboutus, \
             'calltoaction':calltoaction, 'favicon':favicon , 'logo':logo, 'schoolclass':schoolclass, 'teacher':teacher, \
                 'appointment':appointment,'teammember':teamMember ,'testimonial': testimonial,'footerNewsletter':FooterNewsletter, \
                     'footerSocialLink':footerSocialLink }
    return render(request,'webportal/index.html',content)

def about(request):
    return render(request,'webportal/about.html')

def contact(request):
    return render(request,'webportal/contact.html')

