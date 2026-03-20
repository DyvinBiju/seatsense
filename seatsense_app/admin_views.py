from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .models import Event, Booking, Category, Speaker, User
from django.db.models import Sum, Count
from .forms import EventForm
from django.contrib import messages

def admin_required(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(admin_required, login_url='login')
def admin_dashboard(request):
    # Stats Calculation
    total_events = Event.objects.all().count()
    total_bookings = Booking.objects.filter(status='CONFIRMED').count()
    total_revenue = Booking.objects.filter(status='CONFIRMED').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_users = User.objects.all().count()

    # Recent Data
    recent_bookings = Booking.objects.all().order_by('-booking_date')[:5]
    top_events = Event.objects.annotate(num_bookings=Count('booking')).order_by('-num_bookings')[:5]

    context = {
        'total_events': total_events,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'total_users': total_users,
        'recent_bookings': recent_bookings,
        'top_events': top_events,
    }
    return render(request, 'seatsense_app/admin/dashboard.html', context)

@user_passes_test(admin_required, login_url='login')
def admin_event_list(request):
    events = Event.objects.all().order_by('-event_date')
    return render(request, 'seatsense_app/admin/event_list.html', {'events': events})

@user_passes_test(admin_required, login_url='login')
def admin_event_create(request):
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Event created successfully!")
            return redirect('admin_event_list')
    else:
        form = EventForm()
    return render(request, 'seatsense_app/admin/event_form.html', {'form': form, 'title': 'Add New Event'})

@user_passes_test(admin_required, login_url='login')
def admin_event_edit(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated successfully!")
            return redirect('admin_event_list')
    else:
        form = EventForm(instance=event)
    return render(request, 'seatsense_app/admin/event_form.html', {'form': form, 'title': 'Edit Event', 'edit': True})

@user_passes_test(admin_required, login_url='login')
def admin_event_delete(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == "POST":
        event.delete()
        messages.success(request, "Event deleted successfully!")
        return redirect('admin_event_list')
    return render(request, 'seatsense_app/admin/event_confirm_delete.html', {'event': event})
