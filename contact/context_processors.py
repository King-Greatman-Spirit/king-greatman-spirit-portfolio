from .models import Socials

def socials_links(request):
    """
    Returns the first Socials object to make social links available globally.
    """
    socials = Socials.objects.first()  # Use the first Socials object
    return {
        'socials_links': socials
    }
