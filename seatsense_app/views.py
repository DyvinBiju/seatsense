from django.shortcuts import render, get_object_or_404

from .models import Event, Category

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




from .models import Event, Category

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

    auditorium = event.auditorium

    rows = auditorium.total_rows
    seats_per_row = auditorium.seats_per_row

    row_labels = [chr(65 + i) for i in range(rows)]

    context = {
        "event": event,
        "rows": row_labels,
        "seats_per_row": range(1, seats_per_row + 1)
    }

    return render(request, "seatsense_app/seat_layout.html", context)







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

