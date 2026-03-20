from django.shortcuts import render, get_object_or_404
from .models import Event, Category, SeatLock, Feedback, FeedbackReply
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Booking, BookingSeat,Seat, SeatLock
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.contrib import  messages


def page_404(request):
    return render(request, 'seatsense_app/404.html')

def about_us(request):
    return render(request, 'seatsense_app/about-us.html')

def contact(request):
    return render(request, 'seatsense_app/contact.html')

def faq(request):
    return render(request, 'seatsense_app/FAQ.html')

def gallery_two(request):
    return render(request, 'seatsense_app/gallery-two.html')

def gallery(request):
    return render(request, 'seatsense_app/gallery.html')

def homepage_two(request):
    return render(request, 'seatsense_app/homepage-two.html')

def index(request):
    return render(request, 'seatsense_app/index.html')

def news_left_sidebar(request):
    return render(request, 'seatsense_app/news-left-sidebar.html')





from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime

from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime
from django.db.models import Q

def explore_events(request):

    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    show_past = request.GET.get('past', '') == '1'
    page_number = request.GET.get('page', 1)

    now = timezone.now()

    all_events = Event.objects.all()

    valid_events = []
    upcoming_events_count = 0
    past_events_count = 0
    
    # Track category counts dynamically based on the current mode
    category_counts = {}

    for event in all_events:
        event_datetime = datetime.combine(event.event_date, event.event_time)
        if timezone.is_naive(event_datetime):
            event_datetime = timezone.make_aware(event_datetime)

        is_event_past = event_datetime <= now

        # Count upcoming vs past
        if not is_event_past:
            upcoming_events_count += 1
        else:
            past_events_count += 1

        # Calculate counts for the sidebar categories
        # If show_past=True, count past events per category. If False, count upcoming events.
        if is_event_past == show_past:
            cat_id = event.category_id
            category_counts[cat_id] = category_counts.get(cat_id, 0) + 1

        # Filter depending on view mode
        if show_past:
            if is_event_past:
                valid_events.append(event)
        else:
            if not is_event_past:
                valid_events.append(event)

    # Order events correctly
    if show_past:
        valid_events.sort(key=lambda x: x.event_date, reverse=True)
    else:
        valid_events.sort(key=lambda x: x.event_date)

    active_category_name = "Past Events" if show_past else "All Events"

    # Search filter
    if query:
        valid_events = [
            event for event in valid_events if (
                query.lower() in event.title.lower()
                or query.lower() in event.description.lower()
                or query.lower() in event.auditorium.name.lower()
            )
        ]
        active_category_name = f"Search Results for '{query}'"

    # Category filter
    if category_id:
        valid_events = [
            event for event in valid_events if str(event.category_id) == category_id
        ]

        active_cat = Category.objects.filter(id=category_id).first()

        if active_cat:
            if query:
                active_category_name = f"{active_cat.name.title()} Results for '{query}'"
            else:
                active_category_name = active_cat.name.title()

    # Pagination
    paginator = Paginator(valid_events, 9)
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()
    # Apply the dynamic counts to categories
    for cat in categories:
        cat.display_count = category_counts.get(cat.id, 0)

    context = {
        "events": page_obj,
        "categories": categories,
        "current_query": query,
        "current_category": category_id,
        "show_past": show_past,
        "all_events_count": upcoming_events_count,
        "past_events_count": past_events_count,
        "active_category_name": active_category_name
    }

    return render(request, "seatsense_app/explore_events.html", context)





def event_detail(request, event_id):

    event = get_object_or_404(Event, id=event_id)

    event_datetime = datetime.combine(event.event_date, event.event_time)
    if timezone.is_naive(event_datetime):
        event_datetime = timezone.make_aware(event_datetime)

    is_past = event_datetime <= timezone.now()

    feedbacks = Feedback.objects.filter(event=event).order_by("-created_at")

    attended = False
    already_reviewed = False

    if request.user.is_authenticated:
        attended = Booking.objects.filter(
            user=request.user,
            event=event,
            status="CONFIRMED"
        ).exists()

        already_reviewed = Feedback.objects.filter(
            user=request.user,
            event=event
        ).exists()

        if request.method == "POST" and is_past and attended and not already_reviewed:
            rating = request.POST.get("rating")
            comment = request.POST.get("comment")

            if rating:
                Feedback.objects.create(
                    user=request.user,
                    event=event,
                    rating=rating,
                    comment=comment
                )
                messages.success(request, "Feedback submitted successfully.")
                return redirect("event_detail", event_id=event.id)
    
    context = {
        "event": event,
        "is_past": is_past,
        "feedbacks": feedbacks,
        "attended": attended,
        "already_reviewed": already_reviewed
    }

    return render(request, "seatsense_app/event_detail.html", context)




def seat_layout(request, event_id):

    event = get_object_or_404(Event, id=event_id)

    event_datetime = timezone.make_aware(
        datetime.combine(event.event_date, event.event_time)
    )

    if event_datetime < timezone.now():
        messages.error(request, "This event has already ended. Booking is closed.")
        return redirect("explore_events")

    # Remove expired locks
    SeatLock.objects.filter(
        locked_at__lt=timezone.now() - timedelta(minutes=5)
    ).delete()

    seats = Seat.objects.filter(
        auditorium=event.auditorium
    ).order_by("row_label", "seat_number")

    locked_seats = SeatLock.objects.filter(event=event)

    # Only CONFIRMED bookings should mark seats as booked
    booked_seats = BookingSeat.objects.filter(
        booking__event=event,
        booking__status="CONFIRMED"
    )

    locked_ids = [lock.seat.id for lock in locked_seats]
    booked_ids = [b.seat.id for b in booked_seats]

    seat_map = {}

    for seat in seats:

        seat.is_locked = seat.id in locked_ids
        seat.is_booked = seat.id in booked_ids

        seat_map.setdefault(seat.row_label, []).append(seat)

    context = {
        "event": event,
        "seat_map": seat_map
    }

    return render(
        request,
        "seatsense_app/seat_layout.html",
        context
    )




def signup(request):

    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully. Please log in.")
            return redirect("login")

    else:
        form = UserCreationForm()

    return render(request, "seatsense_app/signup.html", {"form": form})



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Event


@login_required
def confirm_booking(request, event_id):

    event = get_object_or_404(Event, id=event_id)

    event_datetime = timezone.make_aware(
        datetime.combine(event.event_date, event.event_time)
)

    if event_datetime <= timezone.now():
        messages.error(request, "This event has already ended. Booking is closed.")
        return redirect("explore_events")

    # First time coming from seat selection
    if request.method == "POST":

        seats = request.POST.get("selected_seats")

        if not seats:
            return redirect("seat_layout", event_id=event_id)

        seat_list = seats.split(",")

        request.session["selected_seats"] = seat_list

        for seat_code in seat_list:

            row = seat_code[0]
            number = seat_code[1:]

            seat = Seat.objects.get(
                auditorium=event.auditorium,
                row_label=row,
                seat_number=number
            )

            SeatLock.objects.get_or_create(
                seat=seat,
                event=event,
                user=request.user
            )

    # On refresh, use session seats
    seat_list = request.session.get("selected_seats")

    if not seat_list:
        return redirect("seat_layout", event_id=event_id)

    total_price = event.ticket_price * len(seat_list)

    # Calculate remaining time from SeatLock
    locks = SeatLock.objects.filter(
        user=request.user,
        event=event
    )

    if not locks.exists():
        return redirect("seat_layout", event_id=event_id)

    first_lock = locks.order_by("locked_at").first()

    expiry_time = first_lock.locked_at + timedelta(minutes=5)

    remaining_seconds = int(
        (expiry_time - timezone.now()).total_seconds()
    )

    if remaining_seconds < 0:
        remaining_seconds = 0

    context = {
        "event": event,
        "seats": seat_list,
        "total_price": total_price,
        "remaining_seconds": remaining_seconds
    }

    return render(
        request,
        "seatsense_app/confirm_booking.html",
        context
    )





from .models import Profile

from django.utils import timezone
from datetime import timedelta
from .models import SeatLock

@login_required
def payment_page(request, event_id):

    event = get_object_or_404(Event, id=event_id)

    seats = request.session.get("selected_seats")

    if not seats:
        return redirect("seat_layout", event_id=event_id)

    total_price = event.ticket_price * len(seats)

    profile = request.user.profile

    # Get earliest seat lock
    locks = SeatLock.objects.filter(
        user=request.user,
        event=event
    )

    if not locks.exists():
        return redirect("seat_layout", event_id=event_id)

    first_lock = locks.order_by("locked_at").first()

    expiry_time = first_lock.locked_at + timedelta(minutes=5)

    remaining_seconds = int(
        (expiry_time - timezone.now()).total_seconds()
    )

    if remaining_seconds < 0:
        remaining_seconds = 0

    context = {
        "event": event,
        "seats": seats,
        "total_price": total_price,
        "pin_exists": bool(profile.payment_pin),
        "remaining_seconds": remaining_seconds
    }

    return render(request, "seatsense_app/payment.html", context)



@login_required
def create_payment_pin(request, event_id):

    event = get_object_or_404(Event, id=event_id)

    seats = request.session.get("selected_seats")

    if not seats:
        return redirect("explore_events")

    total_price = event.ticket_price * len(seats)

    locks = SeatLock.objects.filter(user=request.user, event=event)
    first_lock = locks.order_by("locked_at").first()

    expiry_time = first_lock.locked_at + timedelta(minutes=5)
    remaining_seconds = int((expiry_time - timezone.now()).total_seconds())

    if remaining_seconds < 0:
        remaining_seconds = 0


    if request.method == "POST":

        new_pin = request.POST.get("new_pin")
        confirm_pin = request.POST.get("confirm_pin")

        if not new_pin.isdigit() or not confirm_pin.isdigit():
            return render(request, "seatsense_app/payment.html", {
                "event": event,
                "seats": seats,
                "total_price": total_price,
                "remaining_seconds": remaining_seconds,
                "pin_exists": False,
                "error": "PIN must contain only numbers."
            })

        if len(new_pin) < 4 or len(new_pin) > 6:
            return render(request, "seatsense_app/payment.html", {
                "event": event,
                "seats": seats,
                "total_price": total_price,
                "remaining_seconds": remaining_seconds,
                "pin_exists": False,
                "error": "PIN must be between 4 and 6 digits."
            })

        if new_pin != confirm_pin:
            return render(request, "seatsense_app/payment.html", {
                "event": event,
                "seats": seats,
                "total_price": total_price,
                "remaining_seconds": remaining_seconds,
                "pin_exists": False,
                "error": "PINs do not match."
            })

        profile = request.user.profile
        profile.payment_pin = new_pin
        profile.save()

        return redirect("payment_page", event_id=event_id)



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Event, Seat, Booking, BookingSeat, SeatLock


@login_required
def process_payment(request, event_id):

    if request.method != "POST":
        return redirect("explore_events")

    event = get_object_or_404(Event, id=event_id)

    entered_pin = request.POST.get("pin")

    profile = request.user.profile

    seats = request.session.get("selected_seats")

    if not seats:
        return redirect("explore_events")

    total_price = event.ticket_price * len(seats)

    # Initialize attempt counter
    if "pin_attempts" not in request.session:
        request.session["pin_attempts"] = 0

    # ❌ Wrong PIN
    if profile.payment_pin != entered_pin:

        request.session["pin_attempts"] += 1

        # Max attempts = 3
        if request.session["pin_attempts"] >= 3:

            # 🔴 Release seat locks immediately
            SeatLock.objects.filter(
                user=request.user,
                event=event
            ).delete()

            request.session["pin_attempts"] = 0

            if "selected_seats" in request.session:
                del request.session["selected_seats"]

            return redirect("explore_events")

        # Recalculate timer
        locks = SeatLock.objects.filter(user=request.user, event=event)

        first_lock = locks.order_by("locked_at").first()

        expiry_time = first_lock.locked_at + timedelta(minutes=5)

        remaining_seconds = int((expiry_time - timezone.now()).total_seconds())

        if remaining_seconds < 0:
            remaining_seconds = 0

        return render(request, "seatsense_app/payment.html", {
            "event": event,
            "seats": seats,
            "total_price": total_price,
            "remaining_seconds": remaining_seconds,
            "pin_exists": True,   # ✅ FIX: ensures Enter PIN form shows
            "error": f"Incorrect PIN. Attempts left: {3 - request.session['pin_attempts']}"
        })

    # ✅ Correct PIN
    request.session["pin_attempts"] = 0

    total_amount = event.ticket_price * len(seats)

    booking = Booking.objects.create(
        user=request.user,
        event=event,
        total_amount=total_amount
    )

    for seat_code in seats:

        row = seat_code[0]
        number = seat_code[1:]

        seat = Seat.objects.get(
            auditorium=event.auditorium,
            row_label=row,
            seat_number=number
        )

        BookingSeat.objects.create(
            booking=booking,
            seat=seat
        )

        SeatLock.objects.filter(
            seat=seat,
            event=event
        ).delete()

    if "selected_seats" in request.session:
        del request.session["selected_seats"]

    return redirect("payment_success", booking_id=booking.id)



@login_required
def payment_success(request, booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    seats = BookingSeat.objects.filter(
        booking=booking
    )

    seat_list = [str(seat.seat) for seat in seats]

    context = {
        "booking": booking,
        "event": booking.event,
        "seats": seat_list
    }

    return render(
        request,
        "seatsense_app/payment_success.html",
        context
    )





@login_required
def my_bookings(request):

    bookings = Booking.objects.filter(
        user=request.user
    ).order_by("-booking_date")

    for booking in bookings:
        event_datetime = datetime.combine(booking.event.event_date, booking.event.event_time)
        if timezone.is_naive(event_datetime):
            event_datetime = timezone.make_aware(event_datetime)

        booking.is_past = event_datetime <= timezone.now()
        if booking.is_past and booking.status == "CONFIRMED":
            booking.already_reviewed = Feedback.objects.filter(
                user=request.user,
                event=booking.event
            ).exists()

    context = {
        "bookings": bookings
    }

    return render(
        request,
        "seatsense_app/my_bookings.html",
        context
    )




import qrcode
import base64
from io import BytesIO


@login_required
def booking_detail(request, booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    booking_seats = BookingSeat.objects.filter(booking=booking)

    seat_list = [str(seat.seat) for seat in booking_seats]

    # QR Code Data (unique per booking)
    qr_data = f"""
SeatSense Ticket
User: {request.user.username}
Event: {booking.event.title}
Seats: {', '.join(seat_list)}
Date: {booking.event.event_date}
"""

    qr = qrcode.make(qr_data)

    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    # Calculate if event is past
    event_datetime = datetime.combine(booking.event.event_date, booking.event.event_time)
    if timezone.is_naive(event_datetime):
        event_datetime = timezone.make_aware(event_datetime)
    
    is_past = event_datetime <= timezone.now()

    context = {
        "booking": booking,
        "seats": seat_list,
        "qr_code": qr_base64,
        "is_past": is_past
    }

    return render(
        request,
        "seatsense_app/booking_detail.html",
        context
    )



from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib import messages


@login_required
def cancel_booking(request, booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    if booking.status == "CANCELLED":
        messages.warning(request, "This booking is already cancelled.")
        return redirect("my_bookings")

    event_datetime = timezone.make_aware(
        datetime.combine(
            booking.event.event_date,
            booking.event.event_time
        )
    )

    now = timezone.now()

    # Allow cancellation only until 6 hours before event
    if event_datetime - now < timedelta(hours=6):
        messages.error(
            request,
            "Cancellation is not allowed within 6 hours of the event."
        )
        return redirect("booking_detail", booking_id=booking.id)

    booking.status = "CANCELLED"

    booking.cancelled_at = timezone.now()

    booking.save()

    messages.success(
        request,
        "Booking cancelled successfully. Seats have been released. (No refund policy)"
    )

    return redirect("my_bookings")



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Profile, Booking

from django.contrib.auth.decorators import login_required
from .models import Profile, Booking

@login_required
def profile(request):

    # Ensure profile exists
    profile, created = Profile.objects.get_or_create(user=request.user)

    total_bookings = Booking.objects.filter(user=request.user).count()

    active_bookings = Booking.objects.filter(
        user=request.user,
        status="CONFIRMED"
    ).count()

    cancelled_bookings = Booking.objects.filter(
        user=request.user,
        status="CANCELLED"
    ).count()

    recent_replies = FeedbackReply.objects.filter(
        feedback__user=request.user
    ).exclude(
        user=request.user
    ).order_by("-created_at")[:5]

    context = {
        "profile": profile,
        "total_bookings": total_bookings,
        "active_bookings": active_bookings,
        "cancelled_bookings": cancelled_bookings,
        "recent_replies": recent_replies
    }

    return render(request, "seatsense_app/profile.html", context)



@login_required
def edit_profile(request):

    profile = request.user.profile

    if request.method == "POST":

        if request.POST.get("remove_photo") == "true":
            profile.profile_image = "profiles/default.png"
        else:
            phone = request.POST.get("phone")

            if phone:
                if len(phone) != 10 or not phone.isdigit():
                    messages.error(request, "Phone number must be exactly 10 digits.")
                    return render(request, "seatsense_app/edit_profile.html", {"profile": profile})
                profile.phone = phone

            if "profile_image" in request.FILES:
                profile.profile_image = request.FILES["profile_image"]

        profile.save()

        return redirect("profile")

    return render(request, "seatsense_app/edit_profile.html", {
        "profile": profile
    })





@login_required
def change_payment_pin(request):

    profile = request.user.profile

    if request.method == "POST":

        current_pin = request.POST.get("current_pin")
        new_pin = request.POST.get("new_pin")
        confirm_pin = request.POST.get("confirm_pin")

        if profile.payment_pin != current_pin:
            return render(request, "seatsense_app/change_pin.html", {
                "error": "Current PIN is incorrect"
            })

        if new_pin != confirm_pin:
            return render(request, "seatsense_app/change_pin.html", {
                "error": "PINs do not match"
            })

        if len(new_pin) < 4:
            return render(request, "seatsense_app/change_pin.html", {
                "error": "PIN must be at least 4 digits"
            })

        profile.payment_pin = new_pin
        profile.save()

        return redirect("profile")

    return render(request, "seatsense_app/change_pin.html")




@login_required
def add_reply(request, feedback_id):

    feedback = get_object_or_404(Feedback, id=feedback_id)

    if request.method == "POST":

        reply_text = request.POST.get("reply")

        if reply_text:

            FeedbackReply.objects.create(
                feedback=feedback,
                user=request.user,
                reply=reply_text
            )

    return redirect("event_detail", event_id=feedback.event.id)












def news_single(request):
    return render(request, 'seatsense_app/news-single.html')

def news(request):
    return render(request, 'seatsense_app/news.html')

def pricing(request):
    return render(request, 'seatsense_app/pricing.html')

def schedule(request):
    return render(request, 'seatsense_app/schedule.html')

def single_speaker(request):
    return render(request, 'seatsense_app/single-speaker.html')

def speakers(request):
    return render(request, 'seatsense_app/speakers.html')

def sponsors(request):
    return render(request, 'seatsense_app/sponsors.html')

def testimonial(request):
    return render(request, 'seatsense_app/testimonial.html')

