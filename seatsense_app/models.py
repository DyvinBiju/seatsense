from django.db import models
from django.contrib.auth.models import User
import string

class Auditorium(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)

    total_rows = models.IntegerField()
    seats_per_row = models.IntegerField()

    # description = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
    def generate_seats(self):

        for i in range(self.total_rows):

            row = string.ascii_uppercase[i]

            for seat_num in range(1, self.seats_per_row + 1):

                Seat.objects.get_or_create(
                    auditorium=self,
                    row_label=row,
                    seat_number=seat_num
                )


class Seat(models.Model):
    auditorium = models.ForeignKey(Auditorium, on_delete=models.CASCADE)

    row_label = models.CharField(max_length=5)
    seat_number = models.IntegerField()

    def __str__(self):
        return f"{self.row_label}{self.seat_number}"


class Category(models.Model):
    name = models.CharField(max_length=100)
    # description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Speaker(models.Model):
    name = models.CharField(max_length=200)
    designation = models.CharField(max_length=200)
    image = models.ImageField(upload_to="speakers/")

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()

    event_date = models.DateField()
    event_time = models.TimeField()

    auditorium = models.ForeignKey(Auditorium, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    ticket_price = models.DecimalField(max_digits=8, decimal_places=2)

    DURATION_CHOICES = [
        ('1', '1 Hour'),
        ('1.5', '1.5 Hours'),
        ('2', '2 Hours'),
        ('2.5', '2.5 Hours'),
        ('3', '3 Hours'),
        ('3.5', '3.5 Hours'),
        ('4', '4 Hours'),
        ('5', '5 Hours'),
        ('6', '6 Hours'),
        ('8', '8 Hours / Full Day'),
        ('12', '12 Hours / Half Day'),
        ('24', '1 Day (24 Hours)'),
        ('48', '2 Days (48 Hours)'),
        ('72', '3 Days (72 Hours)'),
    ]

    image = models.ImageField(upload_to="events/")
    duration = models.CharField(max_length=50, blank=True, null=True, choices=DURATION_CHOICES, help_text="Select the estimated duration of the event")
    speakers = models.ManyToManyField(Speaker, related_name="events", blank=True)

    def __str__(self):
        return self.title

    @property
    def total_seats(self):
        return self.auditorium.seat_set.count()

    @property
    def booked_seats(self):
        return BookingSeat.objects.filter(booking__event=self, booking__status='CONFIRMED').count()

    @property
    def remaining_seats(self):
        return self.total_seats - self.booked_seats

    @property
    def booking_percentage(self):
        total = self.total_seats
        if total > 0:
            return (self.booked_seats / total) * 100
        return 0

    @property
    def is_past(self):
        from django.utils import timezone
        from datetime import datetime
        event_datetime = datetime.combine(self.event_date, self.event_time)
        if timezone.is_naive(event_datetime):
            event_datetime = timezone.make_aware(event_datetime)
        return event_datetime <= timezone.now()


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    booking_date = models.DateTimeField(auto_now_add=True)

    total_amount = models.DecimalField(max_digits=8, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=[
            ("CONFIRMED", "Confirmed"),
            ("CANCELLED", "Cancelled"),
        ],
        default="CONFIRMED",
    )
    cancelled_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Booking {self.id}"


class BookingSeat(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("booking", "seat")


    def __str__(self):
        return f"{self.seat}"


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    rating = models.IntegerField()
    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"
    

class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    profile_image = models.ImageField(
        upload_to="profiles/",
        default="profiles/default.png",
        blank=True
    )

    phone = models.CharField(max_length=10, blank=True)

    payment_pin = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return self.user.username
    
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User

class SeatLock(models.Model):

    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    locked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("seat", "event")

    def is_expired(self):
        return timezone.now() > self.locked_at + timedelta(minutes=5)

    def __str__(self):
        return f"{self.seat} locked by {self.user}"
    

from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class FeedbackReply(models.Model):

    feedback = models.ForeignKey(
        Feedback,
        on_delete=models.CASCADE,
        related_name="replies"
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    reply = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply by {self.user.username}"