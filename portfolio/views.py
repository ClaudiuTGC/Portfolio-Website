from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_safe

from .models import Education, Experience, Project, SiteProfile, Skill


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


@require_safe
def home(request):
    experience = list(Experience.objects.all())
    context = profile_context() | {
        "experience": experience,
        "current_role": next((role for role in experience if role.end_date is None), None),
        "projects": Project.objects.all(),
        "skills": Skill.objects.all(),
        "education": Education.objects.all(),
        "canonical_url": settings.SITE_URL + reverse("home"),
    }
    return render(request, "portfolio/home.html", context)


@require_safe
def project_detail(request, slug):
    projects_with_details = Project.objects.exclude(details="")
    project = get_object_or_404(projects_with_details, slug=slug)
    context = profile_context() | {
        "project": project,
        "canonical_url": settings.SITE_URL + project.get_absolute_url(),
    }
    return render(request, "portfolio/project_detail.html", context)
