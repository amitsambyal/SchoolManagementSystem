from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import favicon, logo, CarouselItem, SchoolClass, SchoolFacility, AboutUs, CallToAction, Teacher, Appointment, TeamMember, Testimonial, FooterNewsletter, FooterSocialLink, Student, Attendance, Timetable, Homework, Subject

admin.site.site_header = "School Management System"
admin.site.site_title = "School Admin Panel"

admin.site.register(logo)

@admin.register(favicon)
class faviconAdmin(admin.ModelAdmin):
    list_display = ['favicon', 'appletouchicon']

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
    list_display = ('name', 'roll_no', 'age', 'school_class', 'image_tag')
    readonly_fields = ('image_tag',)
    list_filter = ('school_class',)
    search_fields = ('name', 'roll_no')

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />'.format(obj.image.url))
        return "-"
    image_tag.short_description = 'Image'

# Custom UserAdmin to set default password
class UserAdmin(BaseUserAdmin):
    def save_model(self, request, obj, form, change):
        if not change:  # Only set default password for new users
            obj.set_password('password')  # Set your default password here
            print(f"Setting default password for user: {obj.username}")  # Debugging statement
        super().save_model(request, obj, form, change)

admin.site.unregister(User)  # Unregister the default User admin
admin.site.register(User, UserAdmin)  # Register the custom User admin
