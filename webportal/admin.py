from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django import forms
from django.core.exceptions import PermissionDenied
from .models import favicon, logo, CarouselItem, SchoolClass, SchoolFacility, AboutUs, CallToAction, Teacher, Appointment, TeamMember, Testimonial, FooterNewsletter, FooterSocialLink, Student, Attendance, Timetable, Homework, Subject,Syllabus

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

class HomeworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'teacher', 'assigned_date', 'due_date', 'created_at', 'updated_at')
    list_filter = ('subject', 'teacher', 'assigned_date', 'due_date')
    search_fields = ('title', 'description')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(teacher=request.user.teacher_profile)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "subject" and not request.user.is_superuser:
            kwargs["queryset"] = Subject.objects.filter(expert_teachers=request.user.teacher_profile)
        if db_field.name == "teacher" and not request.user.is_superuser:
            kwargs["queryset"] = Teacher.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            # Only allow adding if the teacher is linked to the subject
            if not obj.teacher.subject_expert.filter(id=obj.subject.id).exists():
                raise PermissionDenied("You can only add homework for subjects you are an expert in.")
            obj.teacher = request.user.teacher_profile
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        # Only allow adding if the user is a teacher
        if request.user.is_superuser:
            return True
        try:
            teacher = request.user.teacher_profile
            return True
        except Teacher.DoesNotExist:
            return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        # Only allow change if the logged-in teacher is the homework teacher
        return obj.teacher == request.user.teacher_profile

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        # Only allow delete if the logged-in teacher is the homework teacher
        return obj.teacher == request.user.teacher_profile

admin.site.register(Homework, HomeworkAdmin)

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

class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'mobile')
    filter_horizontal = ('subject_expert',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:  # This is a new teacher
            obj.create_user_account()

class SyllabusAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'teacher', 'created_at', 'updated_at')
    list_filter = ('subject', 'teacher')
    search_fields = ('title', 'content')
    unique_together = {('subject', 'title')}

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(teacher=request.user.teacher_profile)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "subject" and not request.user.is_superuser:
            kwargs["queryset"] = Subject.objects.filter(expert_teachers=request.user.teacher_profile)
        if db_field.name == "teacher" and not request.user.is_superuser:
            kwargs["queryset"] = Teacher.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            # Only allow adding if the teacher is linked to the subject
            if not obj.teacher.subject_expert.filter(id=obj.subject.id).exists():
                raise PermissionDenied("You can only add syllabus for subjects you are an expert in.")
            obj.teacher = request.user.teacher_profile
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        # Only allow adding if the user is a teacher
        if request.user.is_superuser:
            return True
        try:
            teacher = request.user.teacher_profile
            return True
        except Teacher.DoesNotExist:
            return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        # Only allow change if the logged-in teacher is the syllabus teacher
        return obj.teacher == request.user.teacher_profile

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        # Only allow delete if the logged-in teacher is the syllabus teacher
        return obj.teacher == request.user.teacher_profile

admin.site.register(Syllabus, SyllabusAdmin)
admin.site.register(Teacher, TeacherAdmin)
