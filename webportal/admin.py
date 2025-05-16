from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django import forms
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.contrib.admin.filters import RelatedFieldListFilter
from .models import favicon, logo, CarouselItem, SchoolClass, SchoolFacility, AboutUs, CallToAction, Teacher, Appointment, TeamMember, Testimonial, FooterNewsletter, FooterSocialLink, Student, Attendance, Timetable, Homework, Subject, Syllabus

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
    list_display = ('name', 'roll_no', 'phone_no', 'age_display', 'school_class', 'pen_number')
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
            'fields': ('school_class','pen_number')
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
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:  # This is a new student
            obj.create_user_account()

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

class CustomSubjectListFilter(RelatedFieldListFilter):
    def field_choices(self, field, request, model_admin):
        if hasattr(request.user, 'teacher_profile'):
            teacher = request.user.teacher_profile
            return [(s.pk, str(s)) for s in Subject.objects.filter(expert_teachers=teacher)]
        elif hasattr(request.user, 'student_profile'):
            student = request.user.student_profile
            return [(s.pk, str(s)) for s in Subject.objects.filter(school_class=student.school_class)]
        else:
            return super().field_choices(field, request, model_admin)

class HomeworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'teacher', 'assigned_date', 'due_date', 'created_at', 'updated_at')
    list_filter = (('subject', CustomSubjectListFilter), 'teacher', 'assigned_date', 'due_date')
    search_fields = ('title', 'description')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'teacher_profile'):
            return qs.filter(teacher=request.user.teacher_profile)
        if hasattr(request.user, 'student_profile'):
            student = request.user.student_profile
            return qs.filter(subject__school_class=student.school_class)
        return qs.none()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        from datetime import date
        # Filter subjects for teachers and students
        if db_field.name == "subject":
            if hasattr(request.user, 'teacher_profile'):
                teacher = request.user.teacher_profile
                today = date.today()
                # Exclude subjects for which homework already exists today
                used_subjects = Homework.objects.filter(
                    teacher=teacher, assigned_date=today
                ).values_list('subject_id', flat=True)
                kwargs["queryset"] = Subject.objects.filter(expert_teachers=teacher).exclude(id__in=used_subjects)
            elif hasattr(request.user, 'student_profile'):
                student = request.user.student_profile
                kwargs["queryset"] = Subject.objects.filter(school_class=student.school_class)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        from datetime import date
        if not request.user.is_superuser and hasattr(request.user, 'teacher_profile'):
            obj.teacher = request.user.teacher_profile
            # Enforce only one homework per subject per day
            if not change:
                exists = Homework.objects.filter(
                    teacher=obj.teacher,
                    subject=obj.subject,
                    assigned_date=obj.assigned_date
                ).exists()
                if exists:
                    raise PermissionDenied("You have already added homework for this subject today.")
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'teacher_profile'):
            from datetime import date
            teacher = request.user.teacher_profile
            today = date.today()
            # Only allow add if there is at least one subject without homework today
            subjects_with_homework = Homework.objects.filter(
                teacher=teacher, assigned_date=today
            ).values_list('subject_id', flat=True)
            available_subjects = Subject.objects.filter(expert_teachers=teacher).exclude(id__in=subjects_with_homework)
            return available_subjects.exists()
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or hasattr(request.user, 'teacher_profile'):
            if obj is None or request.user.is_superuser:
                return True
            return obj.teacher == request.user.teacher_profile
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser or hasattr(request.user, 'teacher_profile'):
            if obj is None or request.user.is_superuser:
                return True
            return obj.teacher == request.user.teacher_profile
        return False

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
    list_filter = (('subject', CustomSubjectListFilter), 'teacher')
    search_fields = ('title', 'content')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'teacher_profile'):
            teacher = request.user.teacher_profile
            return qs.filter(teacher=teacher)
        if hasattr(request.user, 'student_profile'):
            student = request.user.student_profile
            return qs.filter(subject__school_class=student.school_class)
        return qs.none()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "subject":
            if hasattr(request.user, 'teacher_profile'):
                teacher = request.user.teacher_profile
                kwargs["queryset"] = Subject.objects.filter(expert_teachers=teacher)
            elif hasattr(request.user, 'student_profile'):
                student = request.user.student_profile
                kwargs["queryset"] = Subject.objects.filter(school_class=student.school_class)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_add_permission(self, request):
        # Only teachers and superusers can add
        return request.user.is_superuser or hasattr(request.user, 'teacher_profile')

    def has_change_permission(self, request, obj=None):
        # Only teachers (for their own) and superusers can change
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'teacher_profile'):
            if obj is None:
                return True
            return obj.teacher == request.user.teacher_profile
        return False

    def has_delete_permission(self, request, obj=None):
        # Only teachers (for their own) and superusers can delete
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'teacher_profile'):
            if obj is None:
                return True
            return obj.teacher == request.user.teacher_profile
        return False

admin.site.register(Syllabus, SyllabusAdmin)
admin.site.register(Teacher, TeacherAdmin)
