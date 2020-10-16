from django import forms
from django.template import loader
from django.utils.safestring import mark_safe

class EmployeeWidget(forms.Widget):
    template_name = 'employee_widget.html'

    def __init__(self, attrs = None, persons = None):
        self.persons =  []
        if persons: self.persons = persons

        super().__init__(attrs)

    def get_context(self, name, value, attrs = None):
        context = super().get_context(name, value, attrs)
        context['widget']['persons'] = self.persons
        return context

    def format_value(self, value):
        return [] if value is None else value

    def value_from_datadict(self, data, files, name):
        try: getter = data.getlist
        except AttributeError:
            getter = data.get
        return getter(name)