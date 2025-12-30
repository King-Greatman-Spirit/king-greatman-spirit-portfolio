from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import EmailMessage
from datetime import datetime
from decouple import config
from django.conf import settings

from .models import ContactMessage, Socials, CHANNEL_CHOICES
from service.models import Service


def contact(request):
    title = "Contact Us"
    socials = Socials.objects.first()
    services = Service.objects.all()

    if request.method == "POST":
        data = request.POST

        contact = ContactMessage.objects.create(
            full_name=data.get("full_name"),
            email=data.get("email"),
            phone_number=data.get("phone_number"),
            company_name=data.get("company_name"),
            service_id=data.get("service") or None,
            channel=data.get("channel"),
            message=data.get("message"),
        )

        current_time = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")

        # ================= ADMIN EMAIL (HTML) =================
        try:
            admin_html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; background:#f4f6f8; padding:20px;">
                <div style="max-width:650px; margin:auto; background:#ffffff; padding:25px; border-radius:8px;">
                    <h2 style="color:#0d6efd;">📩 New Contact Form Submission</h2>
                    <p><strong>Received:</strong> {current_time}</p>

                    <table width="100%" cellpadding="8" cellspacing="0" style="border-collapse:collapse;">
                        <tr><td><strong>Name:</strong></td><td>{contact.full_name}</td></tr>
                        <tr><td><strong>Email:</strong></td><td>{contact.email}</td></tr>
                        <tr><td><strong>Phone:</strong></td><td>{contact.phone_number or 'N/A'}</td></tr>
                        <tr><td><strong>Company:</strong></td><td>{contact.company_name or 'N/A'}</td></tr>
                        <tr><td><strong>Service:</strong></td><td>{contact.service or 'N/A'}</td></tr>
                        <tr><td><strong>Channel:</strong></td><td>{contact.channel}</td></tr>
                    </table>

                    <hr style="margin:20px 0;">

                    <h3>Message</h3>
                    <div style="background:#f8f9fa; padding:15px; border-left:4px solid #0d6efd;">
                        {contact.message}
                    </div>

                    <p style="margin-top:20px; font-size:13px; color:#6c757d;">
                        Reply directly to this email to respond to the client.
                    </p>
                </div>
            </body>
            </html>
            """

            admin_email = EmailMessage(
                subject="📩 New Lead | King Greatman Spirit Website",
                body=admin_html,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.EMAIL_HOST_USER],
                reply_to=[contact.email],
            )
            admin_email.content_subtype = "html"
            admin_email.send(fail_silently=False)

        except Exception as e:
            print("Admin email failed:", e)

        # ================= AUTO-REPLY TO USER (HTML) =================
        try:
            user_html = f"""
            <html>
            <body style="font-family:'Segoe UI', Arial, sans-serif; background:#f4f6f8; padding:30px;">
                <div style="max-width:600px; margin:auto; background:#ffffff; border-radius:10px; overflow:hidden;">
                    
                    <div style="background:linear-gradient(135deg,#0d6efd,#6610f2); color:#fff; padding:25px; text-align:center;">
                        <h2 style="margin:0;">Message Received Successfully ✅</h2>
                    </div>

                    <div style="padding:30px; color:#333; line-height:1.6;">
                        <p>Hello <strong>{contact.full_name}</strong>,</p>

                        <p>
                            Thank you for contacting <strong>King Greatman Spirit</strong>.
                            Your message has been received and is currently under review.
                        </p>

                        <div style="background:#f1f5ff; padding:15px; border-left:4px solid #0d6efd; margin:20px 0;">
                            “{contact.message}”
                        </div>

                        <p>
                            I focus on delivering <strong>clear, strategic, and value-driven solutions</strong>.
                            If clarification is needed, I’ll reach out shortly.
                        </p>

                        <a href="https://www.linkedin.com/in/greatman-pydev"
                        style="display:inline-block; margin-top:20px; padding:12px 22px;
                        background:#0d6efd; color:#ffffff; text-decoration:none; border-radius:6px;">
                        View My Professional Profile
                        </a>
                    </div>

                    <div style="background:#f8f9fa; padding:22px; text-align:center; font-size:13px; line-height:1.8;">
                        <strong style="font-size:14px;">King Greatman Spirit</strong><br>
                        Software Engineering • AI & Machine Learning Specialist • Data Analyst<br><br>

                        <span style="color:#6c757d;">🌐 Connect with me:</span><br>

                        <a href="https://www.linkedin.com/in/greatman-pydev">LinkedIn</a> |
                        <a href="https://github.com/King-Greatman-Spirit">GitHub</a> |
                        <a href="https://wa.me/2349014155705">WhatsApp</a> |
                        <a href="https://www.facebook.com/FAMOUSGREATMAN">Facebook</a> |
                        <a href="https://www.twitter.com/greatestmaneva">X (Twitter)</a> |
                        <a href="https://www.instagram.com/king_greatman_spirit/">Instagram</a><br>

                        <a href="https://t.me/greatestmaneva">Telegram</a> |
                        <a href="https://www.youtube.com/@greatestmaneva">YouTube</a> |
                        <a href="https://www.tiktok.com/@king_greatman_spirit">TikTok</a> |
                        <a href="https://www.threads.net/@king_greatman_spirit">Threads</a>

                        <br><br>

                        <span style="color:#6c757d;">
                            📱 Direct WhatsApp: <strong>+234 901-415-5705</strong>
                        </span>
                    </div>
                </div>
            </body>
            </html>
            """

            user_email = EmailMessage(
                subject="✅ We’ve received your message — King Greatman Spirit",
                body=user_html,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[contact.email],
            )
            user_email.content_subtype = "html"
            user_email.send(fail_silently=False)

        except Exception as e:
            print("Auto-reply email failed:", e)

        messages.success(
            request,
            "Thank you for reaching out to King Greatman Spirit. Your message has been " \
            "received successfully and is currently under review. We will respond shortly " \
            "with a tailored and value-driven response."
        )

        return redirect("contact")

    context = {
        "title": title,
        "socials": socials,
        "services": services,
        "channel_choices": CHANNEL_CHOICES,
    }
    return render(request, "home.html", context)
