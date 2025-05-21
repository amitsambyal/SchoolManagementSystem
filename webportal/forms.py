from django import forms

class TimetableGenerationForm(forms.Form):
    start_hour = forms.IntegerField(label="Start Hour (24h)", min_value=0, max_value=23, initial=9)
    end_hour = forms.IntegerField(label="End Hour (24h)", min_value=1, max_value=23, initial=14)
    period_minutes = forms.IntegerField(label="Class Period Duration (minutes)", min_value=1, max_value=180, initial=60)
    break_start_hour = forms.IntegerField(label="Break Start Hour (24h)", min_value=0, max_value=23, initial=11)
    break_minutes = forms.IntegerField(label="Break Duration (minutes)", min_value=1, max_value=60, initial=20)