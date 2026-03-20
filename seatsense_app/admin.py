from django.contrib import admin
from .models import Auditorium, Seat, Category, Event, Booking, BookingSeat, Feedback, Profile, Speaker, FeedbackReply

admin.site.register(Auditorium)
admin.site.register(Seat)
admin.site.register(Category)
admin.site.register(Booking)
admin.site.register(BookingSeat)
admin.site.register(Feedback)
admin.site.register(Profile)
admin.site.register(Speaker)
admin.site.register(FeedbackReply)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    filter_horizontal = ('speakers',)
