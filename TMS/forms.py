from dal_select2.widgets import ModelSelect2
from django import forms
from .models import TransportAssignment

class TransportAssignmentForm(forms.ModelForm):
    class Meta:
        model = TransportAssignment
        fields = '__all__'
        widgets = {
            'student': ModelSelect2(
                url='student-autocomplete',
                forward=['school_class']
            ),
        }