from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.
class favicon(models.Model):
    favicon=models.ImageField(upload_to='icon')
    appletouchicon=models.ImageField(upload_to='icon')
    
class logo(models.Model):
    logo= models.ImageField(upload_to='logo')
    logo_text=models.CharField(max_length=100,default='')    
    
    #def _str_(self):
       # return f"{self.logo, self.logo.text}"   
       
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
    
class Teacher(models.Model):
    name = models.CharField(max_length=255)
    profile_picture = models.ImageField(upload_to='teacher_profiles/', help_text="Teacher's profile picture")
    
    def __str__(self):
        return self.name
    
class SchoolClass(models.Model):
    class_name = models.CharField(max_length=255, help_text="The name of the class (e.g., 'Art & Drawing')")
    class_image = models.ImageField(upload_to='class_images/', help_text="Image representing the class")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="classes", help_text="The teacher for the class")
    age_group = models.CharField(max_length=50, help_text="Age group for the class (e.g., '3-5 Years')")
    time = models.CharField(max_length=50, help_text="Time when the class is held (e.g., '9-10 AM')")
    capacity = models.IntegerField(help_text="Maximum capacity of students in the class")
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


class TeamMember(models.Model):
    full_name = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    facebook_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='team_profiles/', blank=True, null=True)

    def __str__(self):
        return self.full_name          
    
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