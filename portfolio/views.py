import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST, require_safe

from .forms import ContactForm
from .models import Education, Experience, Project, SiteProfile, Skill

logger = logging.getLogger(__name__)


def profile_context():
    profile = SiteProfile.objects.first()
    name = profile.name if profile else "Portfolio"
    given_name, _, family_name = name.partition(" ")
    return {
        "profile": profile,
        "name": name,
        "given_name": given_name,
        "family_name": family_name,
        "monogram": "".join(word[0] for word in name.split()[:2]).upper(),
        "site_url": settings.SITE_URL,
    }


def render_home(request, form, *, status=200):
    experience = list(Experience.objects.all())
    context = profile_context() | {
        "form": form,
        "experience": experience,
        "current_role": next((role for role in experience if role.end_date is None), None),
        "projects": Project.objects.all(),
        "skills": Skill.objects.all(),
        "education": Education.objects.all(),
        "canonical_url": settings.SITE_URL + reverse("home"),
    }
    return render(request, "portfolio/home.html", context, status=status)


@require_safe
def home(request):
    return render_home(request, ContactForm())


@require_POST
def contact(request):
    form = ContactForm(request.POST)
    destination = reverse("home") + "#contact"
    if not form.is_valid():
        if form.has_error("website", "honeypot"):
            return redirect(destination)
        return render_home(request, form, status=400)

    name = form.cleaned_data["name"]
    email = form.cleaned_data["email"]
    message = form.cleaned_data["message"]
    try:
        EmailMessage(
            subject="Portfolio contact",
            body=f"From: {name} <{email}>\n\n{message}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.CONTACT_EMAIL],
            reply_to=[email],
        ).send()
    except OSError:
        logger.exception("Portfolio contact delivery failed")
        form.add_error(None, "The message could not be sent. Please try again.")
        return render_home(request, form, status=503)

    messages.success(request, "Your message was sent.")
    return redirect(destination)


@require_safe
def robots(request):
    sitemap_url = settings.SITE_URL + reverse("sitemap")
    return HttpResponse(
        f"User-agent: *\nDisallow: /admin/\nSitemap: {sitemap_url}\n",
        content_type="text/plain; charset=utf-8",
    )


@require_safe
def project_detail(request, slug):
    projects_with_details = Project.objects.exclude(details="")
    project = get_object_or_404(projects_with_details, slug=slug)
    context = profile_context() | {
        "project": project,
        "canonical_url": settings.SITE_URL + project.get_absolute_url(),
    }
    return render(request, "portfolio/project_detail.html", context)
