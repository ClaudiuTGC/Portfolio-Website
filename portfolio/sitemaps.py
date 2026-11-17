from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import reverse
from django.views.decorators.http import require_safe

from .models import Project


class PortfolioSitemap(Sitemap):
    def items(self):
        return [
            reverse("home"),
            *(project.get_absolute_url() for project in Project.objects.exclude(details="")),
        ]

    def location(self, item):
        return item

    def get_protocol(self, protocol=None):
        return urlsplit(settings.SITE_URL).scheme

    def get_domain(self, site=None):
        return urlsplit(settings.SITE_URL).netloc


@require_safe
def portfolio_sitemap(request):
    return sitemap(
        request,
        {"portfolio": PortfolioSitemap},
        template_name="sitemap.xml",
    )
