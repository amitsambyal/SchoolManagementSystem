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
from .models import favicon, logo, CarouselItem, SchoolClass, SchoolFacility, AboutUs, CallToAction, Teacher, Appointment, TeamMember, Testimonial, FooterNewsletter, FooterSocialLink, Student, Timetable, Homework, Subject, Syllabus
from .forms import TimetableGenerationForm

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
    list_display = ('name', 'roll_no', 'phone_no', 'age_display', 'school_class', 'pen_number')
    readonly_fields = ('image_tag', 'syllabus_homework_overview')
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
        ('Syllabus & Homework', {
            'fields': ('syllabus_homework_overview',)
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
    
    def syllabus_homework_overview(self, obj):
        html = '<div style="padding:10px;">'
        subjects = obj.school_class.subjects.all()
        for subject in subjects:
            html += f'<div style="margin-bottom:20px;padding:10px;border:1px solid #eee;border-radius:6px;background:#f9f9fc;">'
            html += f'<h4 style="color:#007bff;">{subject.name}</h4>'
            # Syllabus
            syllabus = subject.syllabi.all()
            html += '<div><strong>Syllabus:</strong>'
            if syllabus:
                for s in syllabus:
                    clean_content = strip_tags(s.content)
                    html += f'<div style="margin:5px 0 10px 0;padding:8px;background:#f1f3f6;border-radius:4px;">'
                    html += f'<b>{s.title}</b><br>{clean_content}'
                    html += f'<br><em>Teacher: {s.teacher.name}</em>'
                    html += '</div>'
            else:
                html += '<div style="color:#888;">No syllabus available.</div>'
            html += '</div>'
            # Homework
            homeworks = subject.homeworks.filter(subject__school_class=obj.school_class).order_by('-assigned_date')
            html += '<div style="margin-top:10px;"><strong>Homework:</strong>'
            if homeworks:
                for hw in homeworks:
                    clean_desc = strip_tags(hw.description)
                    html += f'<div style="margin:5px 0 10px 0;padding:8px;background:#f8f9fa;border-radius:4px;">'
                    html += f'<b>{hw.title}</b><br>{clean_desc}'
                    html += f'<br><span style="font-size:0.95em;color:#888;">Assigned: {hw.assigned_date} | Due: {hw.due_date}</span>'
                    html += '</div>'
            else:
                html += '<div style="color:#888;">No homework assigned.</div>'
            html += '</div>'
            html += '</div>'
        html += '</div>'
        return mark_safe(html)
    syllabus_homework_overview.short_description = "Syllabus & Homework Overview"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:  # This is a new student
            obj.create_user_account()


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

    def get_readonly_fields(self, request, obj=None):
        if hasattr(request.user, 'student_profile'):
            return ['subject', 'teacher', 'title', 'assigned_date', 'due_date', 'html_description', 'created_at', 'updated_at']
        # For teachers and superusers, show created_at and updated_at as read-only
        return ['created_at', 'updated_at'] + list(super().get_readonly_fields(request, obj))

    def html_description(self, obj):
        return mark_safe(obj.description)
    html_description.short_description = "Description"

    def get_fields(self, request, obj=None):
        if hasattr(request.user, 'student_profile'):
            return ['subject', 'teacher', 'title', 'html_description', 'assigned_date', 'due_date']
        # Only include editable fields for the form, not id/created_at/updated_at
        return ['subject', 'teacher', 'title', 'description', 'assigned_date', 'due_date']

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

admin.site.register(Syllabus, SyllabusAdmin)
admin.site.register(Teacher, TeacherAdmin)

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('school_class', 'day', 'start_time', 'end_time', 'subject', 'teacher')
    list_filter = ('school_class', 'day')
    
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
