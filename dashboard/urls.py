from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    # Auth
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Home
    path("", views.dashboard_home, name="home"),

    # Profile & settings
    path("profile/", views.profile_view, name="profile"),
    path("password/", views.change_password, name="password"),

    # Generic content CRUD
    path("crud/<str:key>/", views.crud_list, name="crud_list"),
    path("crud/<str:key>/add/", views.crud_form, name="crud_add"),
    path("crud/<str:key>/<int:pk>/edit/", views.crud_form, name="crud_edit"),
    path("crud/<str:key>/<int:pk>/delete/", views.crud_delete, name="crud_delete"),

    # Contacts
    path("contacts/", views.contacts_list, name="contacts_list"),
    path("contacts/<int:pk>/delete/", views.contact_delete, name="contact_delete"),

    # Newsletter
    path("newsletter/", views.newsletter_list, name="newsletter_list"),
    path("newsletter/<int:pk>/toggle/", views.newsletter_toggle, name="newsletter_toggle"),
    path("newsletter/<int:pk>/delete/", views.newsletter_delete, name="newsletter_delete"),
    path("newsletter/export/", views.newsletter_export, name="newsletter_export"),

    # Payments
    path("payments/", views.payments_list, name="payments_list"),
    path("payments/<int:pk>/status/", views.payment_status, name="payment_status"),
    path("payments/<int:pk>/delete/", views.payment_delete, name="payment_delete"),

    # Support tickets
    path("tickets/", views.tickets_list, name="tickets_list"),
    path("tickets/<int:pk>/status/", views.ticket_status, name="ticket_status"),
    path("tickets/<int:pk>/delete/", views.ticket_delete, name="ticket_delete"),

    # Public ticket creation (chatbot handoff)
    path("ticket/create/", views.ticket_create, name="ticket_create"),
]
