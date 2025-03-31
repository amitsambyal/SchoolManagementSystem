from django.contrib import admin
from .models import favicon,logo,CarouselItem,SchoolClass,SchoolFacility,AboutUs,CallToAction,Teacher,Appointment,TeamMember,Testimonial,FooterNewsletter,FooterSocialLink

admin.site.site_header="School Mangement System"
admin.site.site_title="School Admin Panel"
# Register your models here.

admin.site.register(logo)

@admin.register(favicon)
class faviconAdmin(admin.ModelAdmin):
    list_display=['favicon','appletouchicon']
    
admin.site.register(CarouselItem)
admin.site.register(SchoolFacility)
admin.site.register(AboutUs)
admin.site.register(CallToAction)
admin.site.register(Teacher)
admin.site.register(SchoolClass)
admin.site.register(Appointment)
admin.site.register(TeamMember)
admin.site.register(Testimonial)    
admin.site.register(FooterSocialLink)
admin.site.register(FooterNewsletter)

  


