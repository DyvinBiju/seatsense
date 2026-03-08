from django.contrib import admin
from .models import Auditorium, Seat,Category, Event, Booking, BookingSeat, Feedback, Profile

admin.site.register(Auditorium)
admin.site.register(Seat)
admin.site.register(Category)
admin.site.register(Event)
admin.site.register(Booking)
admin.site.register(BookingSeat)
admin.site.register(Feedback)
admin.site.register(Profile)
