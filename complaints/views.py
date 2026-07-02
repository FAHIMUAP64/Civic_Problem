from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.apps import apps
from .models import Complaint, Notification
from accounts.models import User
from locations.models import UnionWard


def _notify_authorities(complaint):
    """
    🆕 Geographic Jurisdiction Alert Routing System.
    Delivers real-time notifications strictly to verified authorities
    assigned to the specific UnionWard of the complaint.
    """
    # Grab only verified administrators and officials
    authorities = User.objects.filter(role__in=['authority', 'admin'], is_verified=True)

    # Safely look up the location name to prevent crashes during processing
    try:
        location_name = str(complaint.location)
    except Exception:
        location_name = "Unknown Location"

    message_text = (
        f"New complaint in {location_name}: "
        f'"{complaint.title}" '
        f"(Category: {complaint.get_category_display()})"
    )

    complaint_ward = complaint.location

    for auth in authorities:
        # 1. System Admins receive all notification cards globally
        if auth.role == 'admin':
            Notification.objects.create(
                recipient=auth,
                complaint=complaint,
                message=message_text,
            )

        # 2. Local Authorities ONLY receive the alert if they manage this specific ward
        elif auth.role == 'authority':
            try:
                # Check the backwards relationship to the authority_profile we set up
                if hasattr(auth, 'authority_profile') and auth.authority_profile.assigned_ward == complaint_ward:
                    Notification.objects.create(
                        recipient=auth,
                        complaint=complaint,
                        message=message_text,
                    )
            except Exception as e:
                print(f"Skipped notification for {auth.username} due to profile configuration: {e}")


def _ensure_real_database_locations():
    """
    Automatically builds a minimal real location chain in your database if empty.
    Bypasses all nested NOT NULL and Foreign Key constraints cleanly.
    """
    if not UnionWard.objects.exists():
        try:
            # Dynamically grab the models from your locations app
            Division = apps.get_model('locations', 'Division')
            District = apps.get_model('locations', 'District')
            Upazila = apps.get_model('locations', 'Upazila')

            # Build the cascade structure up from Division
            division, _ = Division.objects.get_or_create(id=1, defaults={'name': 'Default Division'})
            district, _ = District.objects.get_or_create(id=1,
                                                         defaults={'name': 'Default District', 'division': division})
            upazila, _ = Upazila.objects.get_or_create(id=1, defaults={'name': 'Default Upazila', 'district': district})

            # Create the actual usable UnionWard records
            dummy_wards = [
                "Ward 01 - Sector 3",
                "Ward 02 - Sector 5",
                "Ward 03 - Uttara",
                "Ward 04 - Mirpur",
                "Ward 05 - Dhanmondi",
            ]
            for i, ward_name in enumerate(dummy_wards, start=1):
                UnionWard.objects.get_or_create(
                    id=i,
                    defaults={'name': ward_name, 'upazila': upazila}
                )
        except Exception as e:
            print(f"Auto-seeding skipped or met an alternate schema layout: {e}")


# No @login_required — anyone can submit
def submit_complaint(request):
    # Ensure our database tables have real entries to display and select
    _ensure_real_database_locations()

    # Fetch real database rows
    locations = UnionWard.objects.all()

    if request.method == 'POST':
        description = request.POST.get('description', '').strip()
        location_id = request.POST.get('location', '')
        category = request.POST.get('category', 'other')
        media = request.FILES.get('media', None)

        # Capture the deadline input date string from the HTML form
        deadline_input = request.POST.get('deadline', '').strip()

        if not description:
            messages.error(request, 'Please describe the problem.')
            return render(request, 'submit_complaint.html', {'locations': locations})

        if not location_id:
            messages.error(request, 'Please select a location.')
            return render(request, 'submit_complaint.html', {'locations': locations})

        try:
            # Fetches the real saved database entry safely
            location = UnionWard.objects.get(id=location_id)
        except (UnionWard.DoesNotExist, ValueError):
            messages.error(request, 'Selected location does not exist in the system.')
            return render(request, 'submit_complaint.html', {'locations': locations})

        category_titles = {
            'broken_roads': 'Broken Roads',
            'street_lights': 'Street Lights',
            'water_supply': 'Water Supply',
            'garbage': 'Garbage Disposal',
            'public_safety': 'Public Safety',
            'other': 'Other Problem',
        }

        # Clean fallback: converts empty form strings into clean Python None fields for SQL compliance
        resolved_deadline = deadline_input if deadline_input else None

        complaint = Complaint(
            title=category_titles.get(category, 'General Complaint'),
            description=description,
            category=category,
            location=location,
            media=media,
            deadline=resolved_deadline,  # Save the deadline property directly into the instance row
            created_by=request.user if request.user.is_authenticated else None,
        )
        complaint.save()
        _notify_authorities(complaint)

        messages.success(request, 'Your complaint has been submitted! Authorities have been notified.')
        return redirect('/dashboard/')

    return render(request, 'submit_complaint.html', {'locations': locations})


@login_required
def view_complaints(request):
    if request.user.role == 'citizen':
        complaints = Complaint.objects.filter(created_by=request.user).order_by('-created_at')
    else:
        complaints = Complaint.objects.all().order_by('-created_at')

    return render(request, 'view_complaints.html', {
        'complaints': complaints,
        'today': timezone.now().date(),
    })


@login_required
def complaint_detail(request, complaint_id):
    """
    Fetches a single complaint by its unique ID and displays its complete details.
    """
    complaint = get_object_or_404(Complaint, id=complaint_id)
    return render(request, 'complaint_detail.html', {'complaint': complaint})


@login_required
def notifications_view(request):
    # Clear/Update unread states in the database BEFORE querying the current view count list
    request.user.notifications.filter(is_read=False).update(is_read=True)

    # Now pull down the clean, updated records
    notifs = request.user.notifications.all().order_by('-created_at')

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