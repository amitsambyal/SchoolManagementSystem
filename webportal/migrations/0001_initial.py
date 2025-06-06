# Generated by Django 5.1.7 on 2025-03-16 17:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AboutUs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Title for the About section', max_length=200)),
                ('content', models.TextField(help_text='Main content for the About section')),
                ('additional_content', models.TextField(blank=True, help_text="Additional content to describe the organization's work", null=True)),
                ('ceo_name', models.CharField(help_text="CEO's Name", max_length=100)),
                ('ceo_title', models.CharField(help_text="CEO's title (e.g., CEO & Founder)", max_length=100)),
                ('ceo_image', models.ImageField(blank=True, help_text='Image of the CEO', null=True, upload_to='about_us/ceo/')),
                ('image_1', models.ImageField(help_text='First image for About section', upload_to='about_us/images/')),
                ('image_2', models.ImageField(blank=True, help_text='Second image for About section', null=True, upload_to='about_us/images/')),
                ('image_3', models.ImageField(blank=True, help_text='Third image for About section', null=True, upload_to='about_us/images/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guardian_name', models.CharField(max_length=255)),
                ('guardian_email', models.EmailField(max_length=254)),
                ('child_name', models.CharField(max_length=255)),
                ('child_age', models.IntegerField()),
                ('message', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='backgroundImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img', models.ImageField(upload_to='slider_bg')),
            ],
        ),
        migrations.CreateModel(
            name='CallToAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Title for the Call to Action section', max_length=200)),
                ('description', models.TextField(help_text='Description for the Call to Action section')),
                ('cta_image', models.ImageField(help_text='Image for the Call to Action section', upload_to='cta_images/')),
                ('cta_button_text', models.CharField(help_text='Text for the CTA button', max_length=100)),
                ('cta_button_link', models.URLField(help_text='Link for the CTA button')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='CarouselItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(help_text='Upload the image for the carousel item.', upload_to='carousel_images/')),
                ('heading', models.CharField(help_text='Heading for the carousel item.', max_length=255)),
                ('description', models.TextField(help_text='Short description or paragraph for the carousel item.')),
                ('link_1_text', models.CharField(blank=True, help_text='Text for the first button link.', max_length=255, null=True)),
                ('link_1_url', models.URLField(blank=True, help_text='URL for the first button.', null=True)),
                ('link_2_text', models.CharField(blank=True, help_text='Text for the second button link.', max_length=255, null=True)),
                ('link_2_url', models.URLField(blank=True, help_text='URL for the second button.', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='favicon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('favicon', models.ImageField(upload_to='icon')),
                ('appletouchicon', models.ImageField(upload_to='icon')),
            ],
        ),
        migrations.CreateModel(
            name='FooterNewsletter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='FooterQuickLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('url', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='FooterSocialLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('url', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='logo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logo', models.ImageField(upload_to='logo')),
                ('logo_text', models.CharField(default='', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='SchoolFacility',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the facility', max_length=255)),
                ('description', models.TextField(help_text='Description of the facility')),
                ('icon_class', models.CharField(help_text='FontAwesome icon class for the facility', max_length=255)),
                ('background_color', models.CharField(choices=[('bg-primary', 'Primary'), ('bg-success', 'Success'), ('bg-warning', 'Warning'), ('bg-info', 'Info')], help_text='Background color for the facility item.', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('profile_picture', models.ImageField(help_text="Teacher's profile picture", upload_to='teacher_profiles/')),
            ],
        ),
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255)),
                ('designation', models.CharField(max_length=255)),
                ('facebook_url', models.URLField(blank=True, null=True)),
                ('twitter_url', models.URLField(blank=True, null=True)),
                ('instagram_url', models.URLField(blank=True, null=True)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='team_profiles/')),
            ],
        ),
        migrations.CreateModel(
            name='Testimonial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_name', models.CharField(max_length=255)),
                ('profession', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='testimonials/')),
            ],
        ),
        migrations.CreateModel(
            name='SchoolClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('class_name', models.CharField(help_text="The name of the class (e.g., 'Art & Drawing')", max_length=255)),
                ('class_image', models.ImageField(help_text='Image representing the class', upload_to='class_images/')),
                ('price', models.DecimalField(decimal_places=2, help_text='Price of the class', max_digits=10)),
                ('age_group', models.CharField(help_text="Age group for the class (e.g., '3-5 Years')", max_length=50)),
                ('time', models.CharField(help_text="Time when the class is held (e.g., '9-10 AM')", max_length=50)),
                ('capacity', models.IntegerField(help_text='Maximum capacity of students in the class')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('teacher', models.ForeignKey(help_text='The teacher for the class', on_delete=django.db.models.deletion.CASCADE, related_name='classes', to='webportal.teacher')),
            ],
        ),
    ]
