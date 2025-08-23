from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django_ckeditor_5.fields import CKEditor5Field
import random
import string
from django.utils.timezone import now
import logging

# Create your models here.
class favicon(models.Model):
    favicon=models.ImageField(upload_to='icon')
    appletouchicon=models.ImageField(upload_to='icon')
    
    def __str__(self):
        return str(self.favicon)
    
class logo(models.Model):
    logo= models.ImageField(upload_to='logo')
    logo_text=models.CharField(max_length=100,default='')    
    
    def __str__(self):
       return str(self.logo)   
       
class CarouselItem(models.Model):
    image = models.ImageField(upload_to='carousel_images/', help_text="Upload the image for the carousel item.")
    heading = models.CharField(max_length=255, help_text="Heading for the carousel item.")
    description = models.TextField(help_text="Short description or paragraph for the carousel item.")
    link_1_text = models.CharField(max_length=255, blank=True, null=True, help_text="Text for the first button link.")
    link_1_url = models.URLField(blank=True, null=True, help_text="URL for the first button.")
    link_2_text = models.CharField(max_length=255, blank=True, null=True, help_text="Text for the second button link.")
    link_2_url = models.URLField(blank=True, null=True, help_text="URL for the second button.")

    def __str__(self):
        return self.heading
       
class SchoolFacility(models.Model):
    # Fields for the facility item
    name = models.CharField(max_length=255, help_text="Name of the facility")
    description = models.TextField(help_text="Description of the facility")
    icon_class = models.CharField(max_length=255, help_text="FontAwesome icon class for the facility")
    background_color = models.CharField(max_length=20, choices=[
        ('primary', 'Primary'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('info', 'Info'),
    ], help_text="Background color for the facility item.")
    
    def clean(self):
        # Split the description into words and count them
        words = self.description.split()
        if len(words) > 15:
            raise ValidationError('Description cannot have more than 15 words.')
    
    def __str__(self):
        return self.name

class AboutUs(models.Model):
    title = models.CharField(max_length=200, help_text="Title for the About section")
    content = models.TextField(help_text="Main content for the About section")
    additional_content = models.TextField(help_text="Additional content to describe the organization's work", blank=True, null=True)
    ceo_name = models.CharField(max_length=100, help_text="CEO's Name")
    ceo_title = models.CharField(max_length=100, help_text="CEO's title (e.g., CEO & Founder)")
    ceo_image = models.ImageField(upload_to='about_us/ceo/', help_text="Image of the CEO", blank=True, null=True)
    image_1 = models.ImageField(upload_to='about_us/images/', help_text="First image for About section")
    image_2 = models.ImageField(upload_to='about_us/images/', help_text="Second image for About section", blank=True, null=True)
    image_3 = models.ImageField(upload_to='about_us/images/', help_text="Third image for About section", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title   
        
class CallToAction(models.Model):
    title = models.CharField(max_length=200, help_text="Title for the Call to Action section")
    description = models.TextField(help_text="Description for the Call to Action section")
    cta_image = models.ImageField(upload_to='cta_images/', help_text="Image for the Call to Action section")
    cta_button_text = models.CharField(max_length=100, help_text="Text for the CTA button")
    cta_button_link = models.URLField(max_length=200, help_text="Link for the CTA button")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title      

    
class Subject(models.Model):
    name = models.CharField(max_length=255)
    school_class = models.ForeignKey('SchoolClass', on_delete=models.CASCADE, related_name='subjects')

    def __str__(self):
        return f"{self.name} ({self.school_class.class_name})"
    

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile', null=True, blank=True)
    name = models.CharField(max_length=255)
    profile_picture = models.ImageField(upload_to='teacher_profiles/', help_text="Teacher's profile picture")
    subject_expert = models.ManyToManyField('Subject', related_name='expert_teachers', blank=True)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        creating = self._state.adding
        super().save(*args, **kwargs)
        if creating:
            self.create_user_account()

    def create_user_account(self):
        if not self.user:
            username = self.email.split('@')[0]
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            try:
                user = User.objects.create_user(username=username, email=self.email, password=password)
                self.user = user
                self.save()
                # Here you might want to send an email to the teacher with their login credentials
                print(f"User account created for {self.name}. Username: {username}, Password: {password}")
                logging.getLogger(__name__).info(f"User  account created for {self.name}. Username: {username}, Password: {password}")
            except Exception as e:
                logging.getLogger(__name__).error(f"Error creating user account for {self.name}: {e}")
                raise

@receiver(post_save, sender=Teacher)
def update_user_account(sender, instance, created, **kwargs):
    if not created and instance.user:
        instance.user.email = instance.email
        instance.user.save()
        
class TeamMember(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='team_members')
    designation = models.CharField(max_length=255)
    facebook_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='team_profiles/', blank=True, null=True)

    def __str__(self):
        if self.teacher:
            return self.teacher.name
        return "Team Member"

class SchoolClass(models.Model):
    class_name = models.CharField(max_length=255, help_text="The name of the class (e.g., 'Class1,Class2')")
    class_image = models.ImageField(upload_to='class_images/', help_text="Image representing the class")
    age_group = models.CharField(max_length=50, help_text="Age group for the class (e.g., '3-5 Years')")
    #time = models.CharField(max_length=50, help_text="Time when the class is held (e.g., '9-10 AM')")
    capacity = models.IntegerField(help_text="Maximum capacity of students in the class")
    class_teacher = models.ForeignKey(
        'Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='class_teacher_for'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.class_name 
    
class Appointment(models.Model):
    guardian_name = models.CharField(max_length=255)
    guardian_email = models.EmailField()
    child_name = models.CharField(max_length=255)
    child_age = models.IntegerField()
    message = models.TextField()

    def __str__(self):
        return f"Appointment for {self.child_name} by {self.guardian_name}"
     
    
# Testimonial Model

class Testimonial(models.Model):
    client_name = models.CharField(max_length=255)
    profession = models.CharField(max_length=255)
    message = models.TextField()
    profile_picture = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    
    def clean(self):
        # Validate that the message contains no more than 40 words
        word_count = len(self.message.split())
        if word_count > 40:
            raise ValidationError("The message cannot exceed 40 words.")

    def __str__(self):
        return f"Testimonial from {self.client_name}"

# Footer Social Media Links Model
class FooterSocialLink(models.Model):
    name = models.CharField(max_length=100)  # Name of the social platform (e.g., 'Facebook', 'Twitter')
    url = models.URLField()
    
    def __str__(self):
        return self.name

# Footer Newsletter Subscription Model
class FooterNewsletter(models.Model):
    email = models.EmailField()

    def __str__(self):
        return self.email

# New models for attendance, timetable, and homework management

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile', null=True, blank=True)
    roll_no = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=255)
    phone_no = models.CharField(max_length=20, unique=True)  # New phone number field
    date_of_birth = models.DateField(null=True, blank=True)
    gender_choices = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    gender = models.CharField(max_length=10, choices=gender_choices, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    parent_guardian_name = models.CharField(max_length=255, null=True, blank=True)
    parent_guardian_contact = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(unique=True,default='')  # New email field
    image = models.ImageField(upload_to='student_images/', null=True, blank=True)
    school_class = models.ForeignKey('SchoolClass', on_delete=models.CASCADE, related_name='students')
    pen_number = models.CharField(max_length=12, unique=True,default='')
    
    class Meta:
        unique_together = ('roll_no', 'school_class')

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        creating = self._state.adding
        super().save(*args, **kwargs)
        if creating:
            self.create_user_account()
            
   
    def create_user_account(self):
        if not self.user:
            username = self.pen_number
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            try:
                user = User.objects.create_user(username=username, email=self.email, password=password)
                self.user = user
                self.save()
            # Here you might want to send an email to the teacher with their login credentials
                print(f"User account created for {self.name}. Username: {username}, Password: {password}")
                logging.getLogger(__name__).info(f"User  account created for {self.name}. Username: {username}, Password: {password}")
            except Exception as e:
                logging.getLogger(__name__).error(f"Error creating user account for {self.name}: {e}")
                raise
    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            age = today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
            return age
        return None        

@receiver(post_save, sender=Student)
def update_user_account(sender, instance, created, **kwargs):
    if not created and instance.user:
        instance.user.email = instance.email
        instance.user.save()


class Homework(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='homeworks')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='homeworks')
    description = CKEditor5Field(help_text="Detailed description of the homework", config_name='extends', default="No description provided.")
    assigned_date = models.DateField(help_text="Date when the homework was assigned", default=date.today)
    due_date = models.DateField(help_text="Date when the homework is due", default=date.today)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Homeworks"
        unique_together = ('subject', 'assigned_date')  # Changed from ('subject', 'title')

    def __str__(self):
        return f"{self.subject.name} Homework ({self.assigned_date})"

    def clean(self):
        # Ensure the teacher is an expert in the subject
        if not self.teacher.subject_expert.filter(id=self.subject.id).exists():
            raise ValidationError("You can only add homework for subjects you are an expert in.")

class Syllabus(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='syllabi')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='syllabi')
    title = models.CharField(max_length=255, help_text="Title of the syllabus section")
    content = CKEditor5Field(help_text="Detailed content of the syllabus", config_name='extends')
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Syllabi"
        unique_together = ('subject', 'title')

    def __str__(self):
        return f"{self.subject.name} Syllabus: {self.title}"

    def clean(self):
        if not self.teacher.subject_expert.filter(id=self.subject.id).exists():
            raise ValidationError("You can only add syllabus for subjects you are an expert in.")

class Timetable(models.Model):
    DAY_CHOICES = [
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'),
        ('Fri', 'Friday'),
        ('Sat', 'Saturday'),
    ]
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='timetables')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='timetables')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='timetables')
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ('school_class', 'day', 'start_time')
        ordering = ['school_class', 'day', 'start_time']

    def __str__(self):
        return f"{self.school_class} | {self.day} {self.start_time}-{self.end_time} | {self.subject} ({self.teacher})"
    
class Attendance(models.Model):
    ATTENDANCE_STATUS = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('leave', 'Leave'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=ATTENDANCE_STATUS)
    marked_by = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='marked_attendances')
    marked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'date')
        ordering = ['-date', 'student']

    def clean(self):
        # Only class teacher can mark attendance for their class
        if self.school_class.class_teacher != self.marked_by:
            raise ValidationError("Only the class teacher can mark attendance for this class.")

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"

class StudentDiary(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='diary_entries')
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='diary_entries')
    date = models.DateField(default=date.today)
    title = models.CharField(max_length=255, help_text="Title or subject of the diary entry")
    entry = models.TextField(help_text="Diary entry or note")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Student Diaries"
        ordering = ['-date', 'student']

    def __str__(self):
        return f"{self.student.name} - {self.title} ({self.date})"

