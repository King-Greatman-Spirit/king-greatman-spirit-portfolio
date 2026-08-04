from django.urls import path
from django.conf import settings
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('contact/', views.contact, name='contact'),
    path('newsletter/subscribe/', views.subscribe, name='newsletter_subscribe'),
    path('newsletter/unsubscribe/<str:email>/', views.unsubscribe, name='newsletter_unsubscribe'),
]

if settings.DEBUG:
    urlpatterns += [
        path('emails/preview/<str:name>/', views.email_preview, name='email_preview'),
    ]
