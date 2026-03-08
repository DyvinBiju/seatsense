from django.contrib import admin
from .models import Auditorium, Seat, Event, Booking, BookingSeat, Feedback

admin.site.register(Auditorium)
admin.site.register(Seat)
admin.site.register(Event)
admin.site.register(Booking)
admin.site.register(BookingSeat)
admin.site.register(Feedback)