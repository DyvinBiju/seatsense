from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .models import Event, Booking, Category, Speaker, User, Feedback, FeedbackReply, Auditorium
from django.db.models import Sum, Count, Q
from .forms import EventForm, CategoryForm, SpeakerForm, AuditoriumForm

# ... rest of file (I'll use multi-replace for cleaner injection)

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
    total_auditoriums = Auditorium.objects.all().count()

    # Charts Data
    # 1. Revenue by Category
    cat_stats = Category.objects.annotate(
        category_revenue=Sum('event__booking__total_amount', filter=Q(event__booking__status='CONFIRMED'))
    ).values('name', 'category_revenue').order_by('-category_revenue')[:5]
    
    cat_names = [c['name'] for c in cat_stats]
    cat_revenues = [float(c['category_revenue'] or 0) for c in cat_stats]

    # 2. Bookings by Event
    event_stats = Event.objects.annotate(
        booking_count=Count('booking', filter=Q(booking__status='CONFIRMED'))
    ).order_by('-booking_count')[:6]
    
    event_titles = [e.title[:15] + '...' if len(e.title) > 15 else e.title for e in event_stats]
    event_booking_counts = [e.booking_count for e in event_stats]

    # Recent Records
    recent_bookings = Booking.objects.all().order_by('-booking_date')[:5]
    top_events = Event.objects.annotate(num_bookings=Count('booking')).order_by('-num_bookings')[:5]

    context = {
        'total_events': total_events,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'total_users': total_users,
        'total_auditoriums': total_auditoriums,
        'recent_bookings': recent_bookings,
        'top_events': top_events,
        # Charts
        'cat_names': cat_names,
        'cat_revenues': cat_revenues,
        'event_titles': event_titles,
        'event_booking_counts': event_booking_counts,
    }
    return render(request, 'seatsense_app/admin/dashboard.html', context)

@user_passes_test(admin_required, login_url='login')
def admin_event_list(request):
    query = request.GET.get('q')
    cat_id = request.GET.get('category')
    
    events = Event.objects.all().order_by('-event_date')
    
    if query:
        events = events.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if cat_id:
        events = events.filter(category_id=cat_id)
        
    categories = Category.objects.all()
    return render(request, 'seatsense_app/admin/event_list.html', {
        'events': events, 
        'categories': categories,
        'search_query': query,
        'selected_cat': int(cat_id) if cat_id else None
    })

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
    old_auditorium = event.auditorium
    
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            new_auditorium = form.cleaned_data['auditorium']
            
            # Booking Guard: Block venue change if bookings exist
            if new_auditorium != old_auditorium and event.booking_set.filter(status='CONFIRMED').exists():
                messages.error(request, f"Cannot change the venue for '{event.title}' because seats have already been booked. Cancel the bookings or create a new event instead.")
                return render(request, 'seatsense_app/admin/event_form.html', {'form': form, 'title': 'Edit Event', 'edit': True})
                
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
        # Booking Guard: Block deletion if bookings exist
        if event.booking_set.filter(status='CONFIRMED').exists():
            messages.error(request, f"Cannot delete '{event.title}' because it has active bookings. Cancel the bookings first.")
            return redirect('admin_event_list')
            
        event.delete()
        messages.success(request, "Event deleted successfully!")
        return redirect('admin_event_list')
    return render(request, 'seatsense_app/admin/event_confirm_delete.html', {'event': event})

@user_passes_test(admin_required, login_url='login')
def admin_booking_list(request):
    query = request.GET.get('q')
    bookings = Booking.objects.all().order_by('-booking_date')
    
    if query:
        bookings = bookings.filter(
            Q(user__username__icontains=query) | 
            Q(event__title__icontains=query) |
            Q(id__icontains=query.replace('#BK-', '').lstrip('0'))
        )
    return render(request, 'seatsense_app/admin/booking_list.html', {'bookings': bookings, 'search_query': query})

# Categories
@user_passes_test(admin_required, login_url='login')
def admin_category_list(request):
    query = request.GET.get('q')
    categories = Category.objects.all()
    if query:
        categories = categories.filter(name__icontains=query)
    return render(request, 'seatsense_app/admin/category_list.html', {'categories': categories, 'search_query': query})

@user_passes_test(admin_required, login_url='login')
def admin_category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created!")
            return redirect('admin_category_list')
    else:
        form = CategoryForm()
    return render(request, 'seatsense_app/admin/generic_form.html', {'form': form, 'title': 'Add Category', 'back_url': 'admin_category_list'})

@user_passes_test(admin_required, login_url='login')
def admin_category_edit(request, cat_id):
    category = get_object_or_404(Category, id=cat_id)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated!")
            return redirect('admin_category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'seatsense_app/admin/generic_form.html', {'form': form, 'title': 'Edit Category', 'back_url': 'admin_category_list'})

@user_passes_test(admin_required, login_url='login')
def admin_category_delete(request, cat_id):
    category = get_object_or_404(Category, id=cat_id)
    category.delete()
    messages.success(request, "Category deleted!")
    return redirect('admin_category_list')

# Speakers
@user_passes_test(admin_required, login_url='login')
def admin_speaker_list(request):
    query = request.GET.get('q')
    speakers = Speaker.objects.all()
    if query:
        speakers = speakers.filter(Q(name__icontains=query) | Q(designation__icontains=query))
    return render(request, 'seatsense_app/admin/speaker_list.html', {'speakers': speakers, 'search_query': query})

@user_passes_test(admin_required, login_url='login')
def admin_speaker_create(request):
    if request.method == "POST":
        form = SpeakerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Speaker added!")
            return redirect('admin_speaker_list')
    else:
        form = SpeakerForm()
    return render(request, 'seatsense_app/admin/generic_form.html', {'form': form, 'title': 'Add Speaker', 'back_url': 'admin_speaker_list'})

@user_passes_test(admin_required, login_url='login')
def admin_speaker_edit(request, speaker_id):
    speaker = get_object_or_404(Speaker, id=speaker_id)
    if request.method == "POST":
        form = SpeakerForm(request.POST, request.FILES, instance=speaker)
        if form.is_valid():
            form.save()
            messages.success(request, "Speaker updated!")
            return redirect('admin_speaker_list')
    else:
        form = SpeakerForm(instance=speaker)
    return render(request, 'seatsense_app/admin/generic_form.html', {'form': form, 'title': 'Edit Speaker', 'back_url': 'admin_speaker_list'})

@user_passes_test(admin_required, login_url='login')
def admin_speaker_delete(request, speaker_id):
    speaker = get_object_or_404(Speaker, id=speaker_id)
    speaker.delete()
    messages.success(request, "Speaker deleted!")
    return redirect('admin_speaker_list')

# Users
@user_passes_test(admin_required, login_url='login')
def admin_user_list(request):
    query = request.GET.get('q')
    users = User.objects.all().order_by('-date_joined')
    if query:
        users = users.filter(
            Q(username__icontains=query) | 
            Q(email__icontains=query) |
            Q(profile__phone__icontains=query)
        )
    return render(request, 'seatsense_app/admin/user_list.html', {'users': users, 'search_query': query})

@user_passes_test(admin_required, login_url='login')
def admin_user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    bookings = Booking.objects.filter(user=user).order_by('-booking_date')
    return render(request, 'seatsense_app/admin/user_detail.html', {'target_user': user, 'bookings': bookings})

@user_passes_test(admin_required, login_url='login')
def admin_user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.is_superuser:
        messages.error(request, "Cannot delete a superuser.")
        return redirect('admin_user_list')
    if user == request.user:
        messages.error(request, "Cannot delete yourself.")
        return redirect('admin_user_list')
    
    user.delete()
    messages.success(request, f"User {user.username} deleted.")
    return redirect('admin_user_list')

# Feedback
@user_passes_test(admin_required, login_url='login')
def admin_feedback_list(request):
    feedback_list = Feedback.objects.all().order_by('-created_at')
    return render(request, 'seatsense_app/admin/feedback_list.html', {'feedback_list': feedback_list})

@user_passes_test(admin_required, login_url='login')
def admin_feedback_reply(request, feedback_id):
    if request.method == "POST":
        feedback = get_object_or_404(Feedback, id=feedback_id)
        reply_text = request.POST.get('reply')
        if reply_text:
            FeedbackReply.objects.create(
                feedback=feedback,
                user=request.user,
                reply=reply_text
            )
            messages.success(request, "Reply sent successfully!")
        return redirect('admin_feedback_list')
    return redirect('admin_feedback_list')

@user_passes_test(admin_required, login_url='login')
def admin_feedback_delete(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)
    feedback.delete()
    messages.success(request, "Feedback removed.")
    return redirect('admin_feedback_list')

# Auditoriums
@user_passes_test(admin_required, login_url='login')
def admin_auditorium_list(request):
    search_query = request.GET.get('q')
    if search_query:
        auditoriums = Auditorium.objects.filter(Q(name__icontains=search_query) | Q(location__icontains=search_query))
    else:
        auditoriums = Auditorium.objects.all()
    
    return render(request, 'seatsense_app/admin/auditorium_list.html', {
        'auditoriums': auditoriums,
        'search_query': search_query
    })

@user_passes_test(admin_required, login_url='login')
def admin_auditorium_create(request):
    if request.method == 'POST':
        form = AuditoriumForm(request.POST)
        if form.is_valid():
            auditorium = form.save()
            auditorium.generate_seats()
            messages.success(request, f"Auditorium '{auditorium.name}' created with seats.")
            return redirect('admin_auditorium_list')
    else:
        form = AuditoriumForm()
    
    return render(request, 'seatsense_app/admin/auditorium_form.html', {
        'form': form,
        'title': 'Add Auditorium'
    })

@user_passes_test(admin_required, login_url='login')
def admin_auditorium_edit(request, auditorium_id):
    auditorium = get_object_or_404(Auditorium, id=auditorium_id)
    old_rows = auditorium.total_rows
    old_seats_per_row = auditorium.seats_per_row
    
    if request.method == 'POST':
        form = AuditoriumForm(request.POST, instance=auditorium)
        if form.is_valid():
            new_rows = form.cleaned_data['total_rows']
            new_seats_per_row = form.cleaned_data['seats_per_row']
            
            # Inventory Guard: Block reduction if events are linked
            if auditorium.event_set.exists():
                if new_rows < old_rows or new_seats_per_row < old_seats_per_row:
                    messages.error(request, "Cannot reduce seating capacity while active events are scheduled in this venue.")
                    return render(request, 'seatsense_app/admin/auditorium_form.html', {'form': form, 'title': 'Edit Auditorium'})
            
            form.save()
            # If expanded, generate new seats (generate_seats handles get_or_create)
            auditorium.generate_seats()
            messages.success(request, f"Auditorium '{auditorium.name}' updated successfully.")
            return redirect('admin_auditorium_list')
    else:
        form = AuditoriumForm(instance=auditorium)
    
    return render(request, 'seatsense_app/admin/auditorium_form.html', {
        'form': form,
        'title': 'Edit Auditorium'
    })

@user_passes_test(admin_required, login_url='login')
def admin_auditorium_delete(request, auditorium_id):
    auditorium = get_object_or_404(Auditorium, id=auditorium_id)
    
    # Relational Guard: Block deletion if events are linked
    if auditorium.event_set.exists():
        messages.error(request, f"Cannot delete '{auditorium.name}' because it has active events. Delete the events first.")
        return redirect('admin_auditorium_list')
    
    auditorium.delete()
    messages.success(request, "Auditorium and its seats deleted successfully.")
    return redirect('admin_auditorium_list')
