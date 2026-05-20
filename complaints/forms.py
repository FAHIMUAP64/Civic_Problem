from django import forms
from .models import Complaint


class ComplaintForm(forms.ModelForm):
    class Meta:
        model  = Complaint
        fields = ['title', 'category', 'description', 'media', 'location', 'deadline']
        widgets = {
            'deadline':    forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe the problem in detail...',
                'required': True,
            }),
            'title': forms.TextInput(attrs={
                'placeholder': 'Give your complaint a short title',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make description and location mandatory
        self.fields['description'].required = True
        self.fields['location'].required    = True
        self.fields['media'].required       = False  # photo/video optional
        self.fields['deadline'].required    = False