from django.urls import path
from .views import (
    submit_complaint,
    view_complaints,
    complaint_detail,  # 🆕 Imported the detail view function here
    notifications_view,
    mark_notification_read
)

urlpatterns = [
    path('submit/', submit_complaint, name='submit_complaint'),
    path('view/', view_complaints, name='view_complaints'),

    # 🆕 Registered the dynamic ID path to handle clicking individual complaints
    path('<int:complaint_id>/', complaint_detail, name='complaint_detail'),

    path('notifications/', notifications_view, name='notifications'),
    path('notifications/<int:notif_id>/read/', mark_notification_read, name='mark_notification_read'),
]