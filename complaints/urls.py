from django.urls import path
from .views import submit_complaint, view_complaints

urlpatterns = [
    path('submit/', submit_complaint, name='submit_complaint'),
    path('view/', view_complaints, name='view_complaints'),
]