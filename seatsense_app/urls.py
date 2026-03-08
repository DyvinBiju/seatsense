from django.urls import path
from . import views

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

    path("events/", views.explore_events, name="explore_events"),
    path("event/<int:event_id>/", views.event_detail, name="event_detail"),
    path("event/<int:event_id>/seats/", views.seat_layout, name="seat_layout"),


    path('news-single/', views.news_single, name='news_single'),
    path('news/', views.news, name='news'),
    path('pricing/', views.pricing, name='pricing'),
    path('schedule/', views.schedule, name='schedule'),
    path('single-speaker/', views.single_speaker, name='single_speaker'),
    path('speakers/', views.speakers, name='speakers'),
    path('sponsors/', views.sponsors, name='sponsors'),
    path('testimonial/', views.testimonial, name='testimonial'),
]
