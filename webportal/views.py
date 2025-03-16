from django.shortcuts import render
from .models import favicon,logo,CarouselItem,SchoolClass,SchoolFacility,AboutUs,CallToAction,Teacher,Appointment,TeamMember,Testimonial,FooterNewsletter,FooterSocialLink

# Create your views here.

def index(request):
    carouselItem=CarouselItem.objects.all()
    
    
    content={'carouselItem':carouselItem}
    return render(request,'webportal/index.html',content)

def about(request):
    return render(request,'webportal/about.html')

def contact(request):
    return render(request,'webportal/contact.html')

