from django.urls import path
from . import views, admin_views

urlpatterns = [
    path('404/', views.page_404, name='page_404'),
    path('about-us/', views.about_us, name='about_us'),
    path('contact/', views.contact, name='contact'),
    path('FAQ/', views.faq, name='faq'),
    path('gallery-two/', views.gallery_two, name='gallery_two'),
    path('gallery/', views.gallery, name='gallery'),
    path('homepage-two/', views.homepage_two, name='homepage_two'),
    path('', views.index, name='index'),
    path('news-left-sidebar/', views.news_left_sidebar, name='news_left_sidebar'),
    path('admin-panel/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/events/', admin_views.admin_event_list, name='admin_event_list'),
    path('admin-panel/events/create/', admin_views.admin_event_create, name='admin_event_create'),
    path('admin-panel/events/<int:event_id>/edit/', admin_views.admin_event_edit, name='admin_event_edit'),
    path('admin-panel/events/<int:event_id>/delete/', admin_views.admin_event_delete, name='admin_event_delete'),

    path("events/", views.explore_events, name="explore_events"),
    path("event/<int:event_id>/", views.event_detail, name="event_detail"),
    path("event/<int:event_id>/seats/", views.seat_layout, name="seat_layout"),
    path('event/<int:event_id>/confirm-booking/', views.confirm_booking, name='confirm_booking'),
    path('event/<int:event_id>/payment/', views.payment_page, name='payment_page'),
    path("event/<int:event_id>/create-pin/", views.create_payment_pin, name="create_payment_pin"),
    path('event/<int:event_id>/process-payment/', views.process_payment, name='process_payment'),
    path("payment-success/<int:booking_id>/", views.payment_success, name="payment_success"),
    path("my-bookings/", views.my_bookings, name="my_bookings"),
    path("booking/<int:booking_id>/", views.booking_detail, name="booking_detail"),
    path("cancel-booking/<int:booking_id>/", views.cancel_booking, name="cancel_booking"),
    path("signup/", views.signup, name="signup"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("reset-password/", views.reset_password, name="reset_password"),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("profile/change-pin/", views.change_payment_pin, name="change_payment_pin"),


    path("feedback/<int:feedback_id>/reply/", views.add_reply, name="add_reply"),





    path('news-single/', views.news_single, name='news_single'),
    path('news/', views.news, name='news'),
    path('pricing/', views.pricing, name='pricing'),
    path('schedule/', views.schedule, name='schedule'),
    path('single-speaker/', views.single_speaker, name='single_speaker'),
    path('speakers/', views.speakers, name='speakers'),
    path('sponsors/', views.sponsors, name='sponsors'),
    path('testimonial/', views.testimonial, name='testimonial'),
]
