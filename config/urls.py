from django.contrib import admin
from django.urls import path

from portfolio import views
from portfolio.sitemaps import portfolio_sitemap

urlpatterns = [
    path("", views.home, name="home"),
    path("contact/", views.contact, name="contact"),
    path("projects/<slug:slug>/", views.project_detail, name="project"),
    path("robots.txt", views.robots, name="robots"),
    path("sitemap.xml", portfolio_sitemap, name="sitemap"),
    path("admin/", admin.site.urls),
]
