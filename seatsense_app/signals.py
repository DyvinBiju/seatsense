from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps


@receiver(post_save, sender=apps.get_model('seatsense_app', 'Auditorium'))
def create_seats_for_auditorium(sender, instance, created, **kwargs):

    Seat = apps.get_model('seatsense_app', 'Seat')

    # Prevent duplicate seats
    if Seat.objects.filter(auditorium=instance).exists():
        return

    rows = "ABCDEFGH"
    seats_per_row = 10

    for row in rows:
        for number in range(1, seats_per_row + 1):

            Seat.objects.create(
                auditorium=instance,
                row_label=row,
                seat_number=number
            )