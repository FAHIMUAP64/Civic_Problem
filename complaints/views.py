from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Complaint, Notification
from accounts.models import User
from locations.models import UnionWard


def _notify_authorities(complaint):
    authorities = User.objects.filter(role__in=['authority', 'admin'])
    for auth in authorities:
        Notification.objects.create(
            recipient=auth,
            complaint=complaint,
            message=(
                f"New complaint in {complaint.location}: "
                f'"{complaint.title}" '
                f"(Category: {complaint.get_category_display()})"
            ),
        )


# No @login_required — anyone can submit
def submit_complaint(request):
    locations = UnionWard.objects.all()

    if request.method == 'POST':
        description = request.POST.get('description', '').strip()
        location_id = request.POST.get('location', '')
        category = request.POST.get('category', 'other')
        media = request.FILES.get('media', None)

        if not description:
            messages.error(request, 'Please describe the problem.')
            return render(request, 'submit_complaint.html', {'locations': locations})

        if not location_id:
            messages.error(request, 'Please select a location.')
            return render(request, 'submit_complaint.html', {'locations': locations})

        try:
            location = UnionWard.objects.get(id=location_id)
        except UnionWard.DoesNotExist:
            messages.error(request, 'Invalid location selected.')
            return render(request, 'submit_complaint.html', {'locations': locations})

        # Map category to a readable title
        category_titles = {
            'broken_roads': 'Broken Roads',
            'street_lights': 'Street Lights',
            'water_supply': 'Water Supply',
            'garbage': 'Garbage Disposal',
            'public_safety': 'Public Safety',
            'other': 'Other Problem',
        }

        complaint = Complaint(
            title=category_titles.get(category, 'General Complaint'),
            description=description,
            category=category,
            location=location,
            media=media,
            created_by=request.user if request.user.is_authenticated else None,
        )
        complaint.save()
        _notify_authorities(complaint)

        # Success message will show up on the dashboard page after redirecting
        messages.success(request, 'Your complaint has been submitted! Authorities have been notified.')

        # FIXED: Smoothly redirects to your active dashboard URL pattern
        return redirect('/dashboard/')

    return render(request, 'submit_complaint.html', {'locations': locations})


@login_required
def view_complaints(request):
    # If user is a citizen, filter by their account.
    # If user is authority/admin, fetch all citizens' complaints, sorted by newest first.
    if request.user.role == 'citizen':
        complaints = Complaint.objects.filter(created_by=request.user).order_by('-created_at')
    else:
        complaints = Complaint.objects.all().order_by('-created_at')

    return render(request, 'view_complaints.html', {
        'complaints': complaints,
        'today': timezone.now().date(),
    })


@login_required
def notifications_view(request):
    notifs = request.user.notifications.all().order_by('-created_at')
    notifs.filter(is_read=False).update(is_read=True)
    overdue = Complaint.objects.filter(
        status__in=['pending', 'in_progress'],
        deadline__lt=timezone.now().date(),
    )
    return render(request, 'notifications.html', {
        'notifications': notifs,
        'overdue_complaints': overdue,
    })


@login_required
def mark_notification_read(request, notif_id):
    Notification.objects.filter(id=notif_id, recipient=request.user).update(is_read=True)
    return redirect('notifications')