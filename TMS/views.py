from dal_select2.views import Select2QuerySetView
from webportal.models import Student

class StudentAutocomplete(Select2QuerySetView):
    def get_queryset(self):
        qs = Student.objects.all()
        school_class_id = self.forwarded.get('school_class', None)
        if school_class_id:
            qs = qs.filter(school_class_id=school_class_id)
        else:
            qs = qs.none()
        return qs
