from django.db import models
from webportal.models import Student
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import requests

from webportal.models import Student, Teacher

class ExpoPushToken(models.Model):
	token = models.CharField(max_length=255, unique=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"{self.token[:10]}..."



class Notification(models.Model):
	title = models.CharField(max_length=255)
	message = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	is_read = models.BooleanField(default=False)

	def __str__(self):
		return self.title

	class Meta:
		ordering = ['-created_at']

# --- Expo push notification logic ---
from django.db.models.signals import post_save
from django.dispatch import receiver

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"

def send_expo_notification(token, title, message):
	headers = {
		'Content-Type': 'application/json',
	}
	payload = {
		'to': token,
		'title': title,
		'body': message,
		'priority': 'high',
	}
	try:
		response = requests.post(EXPO_PUSH_URL, json=payload, headers=headers)
		response.raise_for_status()
	except Exception as e:
		print(f"Expo send error: {e}")

@receiver(post_save, sender=Notification)
def push_notification_to_expo(sender, instance, created, **kwargs):
	if created:
		# Send to all tokens, no filters
		for token_obj in ExpoPushToken.objects.all():
			send_expo_notification(token_obj.token, instance.title, instance.message)

# --- API endpoint to save Expo token ---
@method_decorator(csrf_exempt, name='dispatch')
class SaveExpoTokenView(View):
	def post(self, request, *args, **kwargs):
		import json
		data = json.loads(request.body.decode('utf-8'))
		token = data.get('token')
		if not token:
			return JsonResponse({'error': 'No token provided'}, status=400)
		ExpoPushToken.objects.update_or_create(token=token, defaults={})
		return JsonResponse({'status': 'success'})
