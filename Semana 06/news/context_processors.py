from .models import Category, SiteSetting


def site_menu(request):
    """Categories and portal settings available on every template."""
    return {
        "categories": Category.objects.all(),
        "site": SiteSetting.current(),
    }
