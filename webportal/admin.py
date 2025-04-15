from django.contrib import admin
from django.utils.html import format_html
from .models import favicon,logo,CarouselItem,SchoolClass,SchoolFacility,AboutUs,CallToAction,Teacher,Appointment,TeamMember,Testimonial,FooterNewsletter,FooterSocialLink,Student,Attendance,Timetable,Homework

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

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'school_class', 'image_tag')
    readonly_fields = ('image_tag',)

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />'.format(obj.image.url))
        return "-"
    image_tag.short_description = 'Image'

admin.site.register(Attendance)
admin.site.register(Timetable)
admin.site.register(Homework)

  


