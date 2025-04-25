from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django import forms
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

try:
    admin.site.unregister(Teacher)
except admin.sites.NotRegistered:
    pass

class TeacherAdminForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclude superusers from user field queryset
        self.fields['user'].queryset = User.objects.filter(is_superuser=False)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    form = TeacherAdminForm
    list_display = ('name', 'user', 'profile_picture')
    search_fields = ('name', 'user__username')

admin.site.register(SchoolClass)
admin.site.register(Appointment)
admin.site.register(TeamMember)
admin.site.register(Testimonial)
admin.site.register(FooterSocialLink)
admin.site.register(FooterNewsletter)

class StudentAdminForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'

    class Media:
        js = ('webportal/js/student_admin.js',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    form = StudentAdminForm
    list_display = ('name', 'roll_no', 'phone_no', 'age_display', 'school_class', 'image_tag')
    readonly_fields = ('image_tag',)
    list_filter = ('school_class',)
    search_fields = ('name', 'roll_no')

    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'roll_no', 'phone_no', 'date_of_birth', 'gender', 'image', 'image_tag')
        }),
        ('Contact Information', {
            'fields': ('address', 'parent_guardian_name', 'parent_guardian_contact', 'email')
        }),
        ('Academic Information', {
            'fields': ('school_class',)
        }),
    )

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
        return "-"
    image_tag.short_description = 'Image'

    def age_display(self, obj):
        return obj.age
    age_display.short_description = 'Age'

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status')
    list_filter = ('status', 'date')
    search_fields = ('student__name',)

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('school_class', 'day', 'start_time', 'end_time', 'subject')
    list_filter = ('day', 'school_class')
    search_fields = ('school_class__class_name', 'subject__name')

@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ('school_class', 'subject', 'assigned_date', 'due_date')
    list_filter = ('assigned_date', 'due_date', 'school_class')
    search_fields = ('school_class__class_name', 'subject__name')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'school_class')
    search_fields = ('name', 'school_class__class_name')

# Custom UserAdmin to set default password
class UserAdmin(BaseUserAdmin):
    def save_model(self, request, obj, form, change):
        if not change:  # Only set default password for new users
            obj.set_password('password')  # Set your default password here
            print(f"Setting default password for user: {obj.username}")  # Debugging statement
        super().save_model(request, obj, form, change)

admin.site.unregister(User)  # Unregister the default User admin
admin.site.register(User, UserAdmin)  # Register the custom User admin
