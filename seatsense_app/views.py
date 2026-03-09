from django.shortcuts import render, get_object_or_404
from .models import Event, Category, SeatLock
from django.utils import timezone
from datetime import timedelta
from .models import Booking, BookingSeat,Seat, SeatLock
from django.contrib import messages

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





def explore_events(request):

    events = Event.objects.all().order_by("event_date")
    categories = Category.objects.all()

    context = {
        "events": events,
        "categories": categories
    }

    return render(request, "seatsense_app/explore_events.html", context)





def event_detail(request, event_id):

    event = get_object_or_404(Event, id=event_id)

    context = {
        "event": event
    }

    return render(request, "seatsense_app/event_detail.html", context)




def seat_layout(request, event_id):

    event = get_object_or_404(Event, id=event_id)

    # Remove expired locks
    SeatLock.objects.filter(
        locked_at__lt=timezone.now() - timedelta(minutes=5)
    ).delete()

    locked_seats = SeatLock.objects.filter(event=event)
    booked_seats = BookingSeat.objects.filter(booking__event=event)

    locked_ids = [lock.seat.id for lock in locked_seats]
    booked_ids = [bs.seat.id for bs in booked_seats]

    seats = Seat.objects.filter(
        auditorium=event.auditorium
    ).order_by("row_label", "seat_number")

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


from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect

def signup(request):

    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("login")

    else:
        form = UserCreationForm()

    return render(request, "seatsense_app/signup.html", {"form": form})



from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

@login_required
def confirm_booking(request, event_id):

    event = get_object_or_404(Event, id=event_id)

    seats = request.POST.get("selected_seats")

    seat_list = seats.split(",")

    locked_seats = []

    for seat_code in seat_list:

        row = seat_code[0]
        number = seat_code[1:]

        seat = Seat.objects.get(
            auditorium=event.auditorium,
            row_label=row,
            seat_number=number
        )

        SeatLock.objects.create(
            seat=seat,
            event=event,
            user=request.user
        )

        locked_seats.append(seat)

    context = {
        "event": event,
        "seats": seat_list
    }

    return render(
        request,
        "seatsense_app/confirm_booking.html",
        context
    )





@login_required
def finalize_booking(request, event_id):

    event = get_object_or_404(Event, id=event_id)

    seats = request.POST.get("selected_seats")
    seat_list = seats.split(",")

    booking = Booking.objects.create(
        user=request.user,
        event=event,
        total_amount=event.ticket_price * len(seat_list)
    )

    for seat_code in seat_list:

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

    messages.success(request, "Booking confirmed!")

    return redirect("index")







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

