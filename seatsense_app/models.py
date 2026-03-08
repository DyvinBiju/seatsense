from django.db import models
from django.contrib.auth.models import User


class Auditorium(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)

    total_rows = models.IntegerField()
    seats_per_row = models.IntegerField()

    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Seat(models.Model):
    auditorium = models.ForeignKey(Auditorium, on_delete=models.CASCADE)

    row_label = models.CharField(max_length=5)
    seat_number = models.IntegerField()

    def __str__(self):
        return f"{self.row_label}{self.seat_number}"


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

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

    image = models.ImageField(upload_to="events/", blank=True)

    def __str__(self):
        return self.title


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

    def __str__(self):
        return f"Booking {self.id}"


class BookingSeat(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)

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

    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.user.username