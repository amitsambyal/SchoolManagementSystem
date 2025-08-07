from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html, strip_tags
from django.utils.safestring import mark_safe
from django import forms
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.contrib.admin.filters import RelatedFieldListFilter
from django.contrib import messages
from datetime import time
from django.urls import path
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from .models import favicon, logo, CarouselItem, SchoolClass, SchoolFacility, AboutUs, CallToAction, Teacher, Appointment, TeamMember, Testimonial, FooterNewsletter, FooterSocialLink, Student, Timetable, Homework, Subject, Syllabus, Attendance, StudentDiary
from .forms import TimetableGenerationForm
from django.forms.models import BaseInlineFormSet  # <-- Add this line
from django.utils import timezone
from django.contrib.admin.views.main import ChangeList
import re
from django.contrib.admin import SimpleListFilter
from django.contrib.admin import DateFieldListFilter

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
    list_display = ( 'name','image_tag','roll_no','pen_number')
    readonly_fields = ('image_tag',)
    list_filter = ('school_class',)
    search_fields = ('name', 'roll_no')
    
    class Media:
        css = {
            'all': ('admin/css/list_responsive.css',)
        }
   
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
            return format_html('<img src="{}" width="60" height="60" style="border-radius:8px;margin-bottom:4px;" />', obj.image.url)
        return "-"
    image_tag.short_description = 'Image'

    def age_display(self, obj):
        return obj.age
    age_display.short_description = 'Age'    
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_print_button'] = True
        return super().changelist_view(request, extra_context=extra_context)
  
    def get_list_filter(self, request):
        # Remove class filter for teachers
        if hasattr(request.user, 'teacher_profile'):
            return ()
        return super().get_list_filter(request)

    def has_add_permission(self, request):
        # Only allow class teachers and superusers to add students
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'teacher_profile'):
            # Only allow if the teacher is a class teacher of any class
            return SchoolClass.objects.filter(class_teacher=request.user.teacher_profile).exists()
        return False

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Restrict school_class dropdown to only the class where the teacher is class teacher
        if hasattr(request.user, 'teacher_profile'):
            school_classes = SchoolClass.objects.filter(class_teacher=request.user.teacher_profile)
            if 'school_class' in form.base_fields:
                form.base_fields['school_class'].queryset = school_classes
                if school_classes.count() == 1:
                    form.base_fields['school_class'].initial = school_classes.first()
                    form.base_fields['school_class'].disabled = True
        return form

    def save_model(self, request, obj, form, change):
        # Always set the class to the teacher's class, regardless of submitted data
        if hasattr(request.user, 'teacher_profile'):
            school_class = SchoolClass.objects.filter(class_teacher=request.user.teacher_profile).first()
            if school_class:
                obj.school_class = school_class
        super().save_model(request, obj, form, change)
        if not change:
            obj.create_user_account()

    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'teacher_profile'):
            # Show students in classes where the teacher is a subject expert
            expert_classes = SchoolClass.objects.filter(subjects__in=request.user.teacher_profile.subject_expert.all()).distinct()
            return qs.filter(school_class__in=expert_classes)
        return qs.none()
    
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if hasattr(request.user, 'teacher_profile'):
            # Remove 'school_class' from the form for teachers
            return [f for f in fields if f != 'school_class'] + ['school_class']
        return fields


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

class CustomTeacherListFilter(RelatedFieldListFilter):
    def field_choices(self, field, request, model_admin):
        if hasattr(request.user, 'teacher_profile'):
            teacher = request.user.teacher_profile
            return [(t.pk, str(t)) for t in Teacher.objects.filter(subject_expert__in=Subject.objects.filter(expert_teachers=teacher))]
        elif hasattr(request.user, 'student_profile'):
            student = request.user.student_profile
            subject_id = request.GET.get('subject__id__exact')
            if subject_id:
                subject = Subject.objects.get(pk=subject_id)
                return [(t.pk, str(t)) for t in Teacher.objects.filter(subject_expert=subject)]
            else:
                return [(t.pk, str(t)) for t in Teacher.objects.filter(subject_expert__in=Subject.objects.filter(school_class=student.school_class))]
        else:
            return super().field_choices(field, request, model_admin)        

@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ('responsive_subject', 'html_description')
    list_filter = (('subject', CustomSubjectListFilter), ('teacher', CustomTeacherListFilter), 'assigned_date', 'due_date')
    search_fields = ('description',)

    class Media:
        css = {
            'all': ('admin/css/list_responsive.css',)
        }

    def get_readonly_fields(self, request, obj=None):
        if hasattr(request.user, 'student_profile'):
            return ['subject', 'teacher', 'assigned_date', 'due_date', 'html_description', 'created_at', 'updated_at']
        return ['created_at', 'updated_at'] + list(super().get_readonly_fields(request, obj))

    def responsive_subject(self, obj):
        return mark_safe(f'<div class="responsive-subject" data-label="Subject">{obj.subject}</div>')
    responsive_subject.short_description = 'Subject'
    responsive_subject.admin_order_field = 'subject'

    def html_description(self, obj):              
        return mark_safe(f'<div class="responsive-description" data-label="Description">{obj.description}</div>')
    html_description.short_description = 'Description'

    
    def get_fields(self, request, obj=None):
        if hasattr(request.user, 'student_profile'):
            return ['subject', 'teacher', 'html_description', 'assigned_date', 'due_date']
        return ['subject', 'teacher', 'description', 'assigned_date', 'due_date']

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
    
    def get_list_filter(self, request):
        if hasattr(request.user, 'student_profile'):
            return (('subject', CustomSubjectListFilter), ('teacher', CustomTeacherListFilter), 'assigned_date', 'due_date')
        elif hasattr(request.user, 'teacher_profile'):
            return (('subject', CustomSubjectListFilter), 'assigned_date', 'due_date')
        else:
            return super().get_list_filter(request)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        from datetime import date
        if db_field.name == "subject":
            if hasattr(request.user, 'teacher_profile'):
                teacher = request.user.teacher_profile
                today = date.today()
                used_subjects = Homework.objects.filter(
                    teacher=teacher, assigned_date=today
                ).values_list('subject_id', flat=True)
                kwargs["queryset"] = Subject.objects.filter(expert_teachers=teacher).exclude(id__in=used_subjects)
            elif hasattr(request.user, 'student_profile'):
                student = request.user.student_profile
                kwargs["queryset"] = Subject.objects.filter(school_class=student.school_class)
        if db_field.name == "teacher":
            if hasattr(request.user, 'teacher_profile'):
                # Only show the logged-in teacher in the dropdown
                kwargs["queryset"] = Teacher.objects.filter(pk=request.user.teacher_profile.pk)
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
        # Only teachers (for their own) and superusers can change
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'teacher_profile'):
            if obj is None:
                return True  # Allow access to the change list
            return obj.teacher == request.user.teacher_profile  # Allow only if the teacher owns the object
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser or hasattr(request.user, 'teacher_profile'):
            if obj is None or request.user.is_superuser:
                return True
            return obj.teacher == request.user.teacher_profile
        return False

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

@admin.register(Teacher)    
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'mobile', 'image_tag',)
    filter_horizontal = ('subject_expert',)
    
    def image_tag(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="60" height="60" style="border-radius:8px;margin-bottom:4px;" />', obj.profile_picture.url)
        return "-"
    image_tag.short_description = 'Image'
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_print_button'] = True
        return super().changelist_view(request, extra_context=extra_context)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if hasattr(request.user, 'student_profile'):
            # Only teachers who teach subjects in the student's class
            student = request.user.student_profile
            subjects = student.school_class.subjects.all()
            return qs.filter(subject_expert__in=subjects).distinct()
        return qs
    
    def get_list_filter(self, request):
        if hasattr(request.user, 'student_profile'):
            return ('subject_expert',)
        return super().get_list_filter(request)

@admin.register(Syllabus)   
class SyllabusAdmin(admin.ModelAdmin):
    list_display = ('responsive_title', 'responsive_subject', 'teacher')
    list_filter = (('subject', CustomSubjectListFilter), ('teacher', CustomTeacherListFilter))
    search_fields = ('title', 'content')

    def responsive_title(self, obj):
        # Using strip_tags to avoid complex HTML in list view.
        return mark_safe(f'<div class="responsive-title" data-label="Title">{strip_tags(obj.title)}</div>')
    responsive_title.short_description = "Title"
    responsive_title.admin_order_field = 'title'

    def responsive_subject(self, obj):
        return mark_safe(f'<div class="responsive-subject" data-label="Subject">{obj.subject}</div>')
    responsive_subject.short_description = "Subject"
    responsive_subject.admin_order_field = 'subject'

    def get_readonly_fields(self, request, obj=None):
        # For students, make all fields readonly and show html_content instead of content
        if hasattr(request.user, 'student_profile'):
            return ['subject', 'teacher', 'title', 'html_content', 'created_at', 'updated_at']
        return super().get_readonly_fields(request, obj)

    def html_content(self, obj):
        return mark_safe(obj.content)
    html_content.short_description = "Content"

    def get_fields(self, request, obj=None):
        # For students, show only the specified fields, replacing 'content' with 'html_content'
        if hasattr(request.user, 'student_profile'):
            # Do NOT include created_at or updated_at here!
            return ['subject', 'teacher', 'title', 'html_content']
        # Only include editable fields for the form, not id/created_at/updated_at
        return ['subject', 'teacher', 'title', 'content']

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
    
    def get_list_filter(self, request):
        if hasattr(request.user, 'student_profile'):
            return (('subject', CustomSubjectListFilter), ('teacher', CustomTeacherListFilter))
        elif hasattr(request.user, 'teacher_profile'):
            return (('subject', CustomSubjectListFilter),)
        else:
            return super().get_list_filter(request)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "subject":
            if hasattr(request.user, 'teacher_profile'):
                teacher = request.user.teacher_profile
                kwargs["queryset"] = Subject.objects.filter(expert_teachers=teacher)
            elif hasattr(request.user, 'student_profile'):
                student = request.user.student_profile
                kwargs["queryset"] = Subject.objects.filter(school_class=student.school_class)
        if db_field.name == "teacher":
            if hasattr(request.user, 'teacher_profile'):
                # Only show the logged-in teacher in the dropdown
                kwargs["queryset"] = Teacher.objects.filter(pk=request.user.teacher_profile.pk)
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
                return True  # Allow access to the change list
            return obj.teacher == request.user.teacher_profile  # Allow only if the teacher owns the object
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

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('school_class', 'day', 'start_time', 'end_time', 'subject', 'teacher')
    list_filter = ('school_class', 'day')
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if hasattr(request.user, 'student_profile'):
            # Only show timetable for the student's class
            student = request.user.student_profile
            return qs.filter(school_class=student.school_class)
        return qs
    def get_list_filter(self, request):
        if hasattr(request.user, 'student_profile'):
            return ('day',)
        return super().get_list_filter(request)

    def filter_timetable_by_class(self, school_class_str):
        school_class = SchoolClass.objects.get(class_name=school_class_str)  # or use pk if you have it
        return Timetable.objects.filter(school_class=school_class)

@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('class_name', 'view_timetable_link')
    actions = ['generate_timetable_action']
 

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('generate-timetable/', self.admin_site.admin_view(self.generate_timetable_view), name='generate-timetable'),
            path('view-timetable/<int:class_id>/', self.admin_site.admin_view(self.view_timetable), name='view-timetable'),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        # Add a button to the changelist
        extra_context = extra_context or {}
        extra_context['generate_timetable_url'] = 'generate-timetable/'
        return super().changelist_view(request, extra_context=extra_context)

    def generate_timetable_view(self, request):
        if request.method == 'POST':
            form = TimetableGenerationForm(request.POST)
            if form.is_valid():
                start_hour = form.cleaned_data['start_hour']
                end_hour = form.cleaned_data['end_hour']
                period_minutes = form.cleaned_data['period_minutes']
                break_start_hour = form.cleaned_data['break_start_hour']
                break_minutes = form.cleaned_data['break_minutes']
                selected_ids = request.session.pop('selected_class_ids', None)
                if selected_ids:
                    classes = SchoolClass.objects.filter(id__in=selected_ids)
                else:
                    classes = SchoolClass.objects.all()  # fallback, or you can show a warning
                self._generate_timetable(
                    request, classes,
                    start_hour, end_hour, period_minutes,
                    break_start_hour, break_minutes
                )
                self.message_user(request, "Timetable generated with custom timings and break!", messages.SUCCESS)
                return redirect('..')
        else:
            form = TimetableGenerationForm()
        context = dict(
            self.admin_site.each_context(request),
            form=form,
        )
        return TemplateResponse(request, "admin/generate_timetable_form.html", context)

    def _generate_timetable(self, request, queryset, start_hour, end_hour, period_minutes, break_start_hour, break_minutes):
        from datetime import time, timedelta, datetime
        for school_class in queryset:
            # Delete existing timetable entries for this class
            Timetable.objects.filter(school_class=school_class).delete()
            subjects = list(Subject.objects.filter(school_class=school_class))
            teachers = Teacher.objects.filter(subject_expert__in=subjects).distinct()
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
            class_teacher = school_class.class_teacher
            if not class_teacher:
                self.message_user(request, f"Class '{school_class.class_name}' has no class teacher assigned!", messages.WARNING)
                continue
            total_periods = int(((end_hour - start_hour) * 60) / period_minutes)
            for day in days:
                assigned_subjects = set()
                period_start = datetime(2000, 1, 1, start_hour, 0)
                period = 0

                # Assign first period to class teacher if possible
                if class_teacher:
                    ct_subject = next((s for s in subjects if class_teacher.subject_expert.filter(pk=s.pk).exists()), None)
                    if ct_subject:
                        Timetable.objects.create(
                            school_class=school_class,
                            subject=ct_subject,
                            teacher=class_teacher,
                            day=day,
                            start_time=period_start.time(),
                            end_time=(period_start + timedelta(minutes=period_minutes)).time(),
                        )
                        assigned_subjects.add(ct_subject.pk)
                        period += 1
                        period_start += timedelta(minutes=period_minutes)

                # Assign remaining periods
                for _ in range(period, total_periods):
                    # Insert break if needed
                    if period_start.hour == break_start_hour:
                        period_start += timedelta(minutes=break_minutes)
                    # Find next unassigned subject and teacher
                    next_subject = next((s for s in subjects if s.pk not in assigned_subjects), None)
                    if not next_subject:
                        break
                    teacher = teachers.filter(subject_expert=next_subject).exclude(pk=getattr(class_teacher, 'pk', None)).first()
                    if not teacher:
                        assigned_subjects.add(next_subject.pk)  # Prevent infinite loop
                        continue
                    Timetable.objects.create(
                        school_class=school_class,
                        subject=next_subject,
                        teacher=teacher,
                        day=day,
                        start_time=period_start.time(),
                        end_time=(period_start + timedelta(minutes=period_minutes)).time(),
                    )
                    assigned_subjects.add(next_subject.pk)
                    period += 1
                    period_start += timedelta(minutes=period_minutes)

    def view_timetable_link(self, obj):
        return format_html(
            '<a class="button" href="{}">View Timetable</a>',
            f'view-timetable/{obj.pk}/'
        )
    view_timetable_link.short_description = "Timetable"

    def view_timetable(self, request, class_id):
        school_class = SchoolClass.objects.get(pk=class_id)
        timetable = Timetable.objects.filter(school_class=school_class).order_by('day', 'start_time')
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        timetable_dict = {day: [] for day in days}
        for entry in timetable:
            timetable_dict[entry.day].append(entry)
        context = dict(
            self.admin_site.each_context(request),
            school_class=school_class,
            timetable_dict=timetable_dict,
            days=days,
        )
        return TemplateResponse(request, "admin/class_timetable.html", context)

    def generate_timetable_action(self, request, queryset):
        """
        Admin action to generate timetable for selected classes.
        Prompts for timings using the same form as the custom view.
        """
        from django.http import HttpResponseRedirect
        from django.urls import reverse

        # Store selected IDs in session to use in the form view
        request.session['selected_class_ids'] = list(queryset.values_list('id', flat=True))
        return HttpResponseRedirect(reverse('admin:generate-timetable'))

    generate_timetable_action.short_description = "Generate timetable for selected classes"

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'date', 'status']

class AttendanceInlineFormSet(BaseInlineFormSet):
    def get_queryset(self):
        qs = super().get_queryset()
        # Only show attendance for students in the class teacher's class
        request = self.request
        if hasattr(request.user, 'teacher_profile'):
            school_class = request.user.teacher_profile.class_teacher_of
            return qs.filter(student__school_class=school_class)
        return qs

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'school_class', 'date', 'status', 'marked_by', 'marked_at')
    list_filter = (
        'school_class',
        ('date', DateFieldListFilter),
        'status',
    )
    search_fields = ('student__name', 'school_class__class_name')
    actions = ['mark_present', 'mark_absent', 'mark_leave', 'mark_all_present_today']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'teacher_profile'):
            # Only allow class teacher to view attendance for their class
            return qs.filter(school_class__class_teacher=request.user.teacher_profile)
        return qs.none()

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if hasattr(request.user, 'teacher_profile'):
            school_classes = SchoolClass.objects.filter(class_teacher=request.user.teacher_profile)
            form.base_fields['student'].queryset = Student.objects.filter(school_class__in=school_classes)
            if school_classes.count() == 1:
                form.base_fields['school_class'].initial = school_classes.first()
                form.base_fields['school_class'].disabled = True
            if 'marked_by' in form.base_fields:
                form.base_fields['marked_by'].queryset = Teacher.objects.filter(pk=request.user.teacher_profile.pk)
                form.base_fields['marked_by'].initial = request.user.teacher_profile
                form.base_fields['marked_by'].disabled = True
        return form

    def save_model(self, request, obj, form, change):
        if hasattr(request.user, 'teacher_profile'):
            school_classes = SchoolClass.objects.filter(class_teacher=request.user.teacher_profile)
            if school_classes.count() == 1:
                obj.school_class = school_classes.first()
            obj.marked_by = request.user.teacher_profile
        super().save_model(request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        # Only class teachers can pre-populate attendance
        if hasattr(request.user, 'teacher_profile'):
            today = timezone.now().date()
            school_classes = SchoolClass.objects.filter(class_teacher=request.user.teacher_profile)
            for school_class in school_classes:
                students = Student.objects.filter(school_class=school_class)
                for student in students:
                    Attendance.objects.get_or_create(
                        student=student,
                        school_class=school_class,
                        date=today,
                        defaults={'status': 'Absent', 'marked_by': request.user.teacher_profile}
                    )
        return super().changelist_view(request, extra_context)

    def has_add_permission(self, request):
        # Only allow class teachers and superusers to add attendance
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'teacher_profile'):
            return SchoolClass.objects.filter(class_teacher=request.user.teacher_profile).exists()
        return False

    def has_change_permission(self, request, obj=None):
        # Only allow class teachers to change attendance for their own class
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'teacher_profile'):
            if obj is None:
                return True
            return obj.school_class.class_teacher == request.user.teacher_profile
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if request.user.is_superuser:
            return actions
        if hasattr(request.user, 'teacher_profile'):
            if SchoolClass.objects.filter(class_teacher=request.user.teacher_profile).exists():
                return actions
        return {}

    def mark_all_present_today(self, request, queryset):
        today = timezone.now().date()
        for school_class in SchoolClass.objects.filter(class_teacher=request.user.teacher_profile):
            students = Student.objects.filter(school_class=school_class)
            for student in students:
                obj, created = Attendance.objects.get_or_create(
                    student=student,
                    school_class=school_class,
                    date=today,
                    defaults={'status': 'present', 'marked_by': request.user.teacher_profile}
                )
                if not created:
                    obj.status = 'present'
                    obj.marked_by = request.user.teacher_profile
                    obj.save()
        self.message_user(request, "All students marked present for today.")

    mark_all_present_today.short_description = "Mark all my students present for today"

    def changelist_view(self, request, extra_context=None):
        # Pre-populate attendance for all students in the teacher's class for today
        if hasattr(request.user, 'teacher_profile'):
            today = timezone.now().date()
            school_classes = SchoolClass.objects.filter(class_teacher=request.user.teacher_profile)
            for school_class in school_classes:
                students = Student.objects.filter(school_class=school_class)
                for student in students:
                    Attendance.objects.get_or_create(
                        student=student,
                        school_class=school_class,
                        date=today,
                        defaults={'status': 'Absent', 'marked_by': request.user.teacher_profile}
                    )
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(StudentDiary)
class StudentDiaryAdmin(admin.ModelAdmin):
    list_display = ('student', 'teacher', 'date', 'title')
    search_fields = ('student__name', 'title', 'entry')
    list_filter = ('date', 'teacher', 'student')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'teacher_profile'):
           # Only diaries added by this teacher, for students in classes where they are subject expert
            expert_classes = SchoolClass.objects.filter(subjects__in=request.user.teacher_profile.subject_expert.all()).distinct()
            return qs.filter(
                teacher=request.user.teacher_profile,
                student__school_class__in=expert_classes
            )
        if hasattr(request.user, 'student_profile'):
            # Student: show only their own diary entries
            return qs.filter(student=request.user.student_profile)
        return qs.none()

    def has_add_permission(self, request):
        # Only teachers and superusers can add
        return request.user.is_superuser or hasattr(request.user, 'teacher_profile')

    def has_change_permission(self, request, obj=None):
        # Only the teacher who wrote it or superuser can change
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'teacher_profile'):
            if obj is None:
                return True
            return obj.teacher == request.user.teacher_profile
        return False

    def has_delete_permission(self, request, obj=None):
        # Only the teacher who wrote it or superuser can delete
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'teacher_profile'):
            if obj is None:
                return True
            return obj.teacher == request.user.teacher_profile
        return False

    def get_readonly_fields(self, request, obj=None):
        # Students: all fields readonly except 'id' and 'updated_at'
        if hasattr(request.user, 'student_profile'):
            readonly = [f.name for f in self.model._meta.fields if f.name not in ('id', 'created_at')]
            return readonly
        return super().get_readonly_fields(request, obj)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Teachers: limit students to classes where they teach at least one subject
        if db_field.name == "student" and hasattr(request.user, 'teacher_profile'):
            # Find all classes where the teacher is an expert in at least one subject
            expert_classes = SchoolClass.objects.filter(
                subjects__in=request.user.teacher_profile.subject_expert.all()
            ).distinct()
            kwargs["queryset"] = Student.objects.filter(school_class__in=expert_classes)
        # Teachers: only themselves in teacher field
        if db_field.name == "teacher" and hasattr(request.user, 'teacher_profile'):
            kwargs["queryset"] = Teacher.objects.filter(pk=request.user.teacher_profile.pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        # Always set teacher to the logged-in teacher
        if hasattr(request.user, 'teacher_profile'):
            obj.teacher = request.user.teacher_profile
        super().save_model(request, obj, form, change)
    
    def get_list_filter(self, request):              
        # For students, show only relevant teachers in the filter
        if hasattr(request.user, 'student_profile'):
             return ('date', RelevantTeacherListFilter)
        elif hasattr(request.user, 'teacher_profile'):
        # For teachers, show only date and student filters (remove teacher filter)
            return ('date', RelevantStudentListFilter)
        return super().get_list_filter(request)  

class RelevantTeacherListFilter(SimpleListFilter):
    title = 'teacher'
    parameter_name = 'teacher'

    def lookups(self, request, model_admin):
        if hasattr(request.user, 'student_profile'):
            student = request.user.student_profile
            # Get teachers who teach subjects in the student's class
            teachers = Teacher.objects.filter(subject_expert__school_class=student.school_class).distinct()
            return [(t.pk, str(t)) for t in teachers]
        return []

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(teacher__pk=self.value())
        return queryset
    
class RelevantStudentListFilter(SimpleListFilter):
    title = 'student'
    parameter_name = 'student'

    def lookups(self, request, model_admin):
        if hasattr(request.user, 'teacher_profile'):
            teacher = request.user.teacher_profile
            expert_classes = SchoolClass.objects.filter(subjects__in=teacher.subject_expert.all()).distinct()
            students = Student.objects.filter(school_class__in=expert_classes)
            return [(s.pk, str(s)) for s in students]
        return []

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(student__pk=self.value())
        return queryset
