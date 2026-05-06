from django.shortcuts import render, redirect
from .forms import ComplaintForm
from .models import Complaint

def submit_complaint(request):
    if not request.user.is_verified:
        return render(request, 'not_verified.html')

    form = ComplaintForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        complaint = form.save(commit=False)
        complaint.created_by = request.user
        complaint.save()
        return redirect('dashboard')

    return render(request, 'submit_complaint.html', {'form': form})


def view_complaints(request):
    complaints = Complaint.objects.all()
    return render(request, 'view_complaints.html', {'complaints': complaints})