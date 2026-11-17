from datetime import date
from io import StringIO
from smtplib import SMTPException
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .forms import ContactForm
from .models import Education, Experience, Project, SiteProfile, Skill

MESSAGE = {"name": "Visitor", "email": "visitor@example.test", "message": "Hello, Claudiu."}


@override_settings(SITE_URL="https://portfolio.example.test")
class PortfolioViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_portfolio", stdout=StringIO())

    def test_home_renders_seeded_content_and_form(self):
        response = self.client.get(reverse("home"))
        for text in (
            "Claudiu Tananau",
            "Morningstar",
            "Qualitest Spotlight Award",
            "BestPrice",
            "Tines",
            "University of Bucharest",
            "Completion unconfirmed",
            "csrfmiddlewaretoken",
        ):
            with self.subTest(text=text):
                self.assertContains(response, text)
        self.assertTemplateUsed(response, "portfolio/home.html")

    def test_admin_content_is_reflected_on_home(self):
        self.client.force_login(get_user_model().objects.create_superuser(username="admin"))
        profile = SiteProfile.objects.get()
        edit_url = reverse("admin:portfolio_siteprofile_change", args=[profile.pk])
        response = self.client.post(
            edit_url,
            {
                "name": profile.name,
                "headline": "Application Security Engineer",
                "intro": profile.intro,
                "bio": profile.bio,
                "location": profile.location,
                "github_url": profile.github_url,
                "linkedin_url": profile.linkedin_url,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertContains(self.client.get(reverse("home")), "Application Security Engineer")
        self.assertEqual(
            self.client.get(reverse("admin:portfolio_siteprofile_add")).status_code, 403
        )
        for model in ("experience", "project", "skill", "education"):
            with self.subTest(model=model):
                self.assertEqual(
                    self.client.get(reverse(f"admin:portfolio_{model}_changelist")).status_code,
                    200,
                )

    def test_project_detail_is_available_when_written(self):
        response = self.client.get(reverse("project", kwargs={"slug": "bestprice"}))
        self.assertContains(response, "I built BestPrice as a personal Django project.")
        self.assertContains(response, "https://portfolio.example.test/projects/bestprice/")
        for slug in ("security-workflow-automation", "unknown"):
            with self.subTest(slug=slug):
                self.assertEqual(
                    self.client.get(reverse("project", kwargs={"slug": slug})).status_code,
                    404,
                )

    def test_robots_and_sitemap_point_to_canonical_urls(self):
        robots = self.client.get(reverse("robots"))
        self.assertContains(robots, "Sitemap: https://portfolio.example.test/sitemap.xml")
        sitemap = self.client.get(reverse("sitemap"))
        self.assertContains(sitemap, "<loc>https://portfolio.example.test/</loc>")
        self.assertContains(
            sitemap, "<loc>https://portfolio.example.test/projects/bestprice/</loc>"
        )
        self.assertNotContains(sitemap, "security-workflow-automation")
        self.assertNotContains(sitemap, "/admin/")

    def test_seed_preserves_admin_edits(self):
        SiteProfile.objects.update(name="Edited Name")
        call_command("seed_portfolio", stdout=StringIO())
        self.assertEqual(SiteProfile.objects.get().name, "Edited Name")
        self.assertEqual(Experience.objects.count(), 2)


class ContactTests(TestCase):
    def test_form_rejects_invalid_email_and_oversized_message(self):
        form = ContactForm(MESSAGE | {"email": "invalid", "message": "a" * 4001})
        self.assertFalse(form.is_valid())
        self.assertEqual(set(form.errors), {"email", "message"})

    def test_form_strips_blank_input(self):
        form = ContactForm(MESSAGE | {"name": " ", "message": " "})
        self.assertFalse(form.is_valid())
        self.assertEqual(set(form.errors), {"name", "message"})

    def test_contact_sends_email_and_redirects(self):
        response = self.client.post(reverse("contact"), MESSAGE, follow=True)
        self.assertRedirects(response, reverse("home") + "#contact")
        self.assertContains(response, "Your message was sent.")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].reply_to, [MESSAGE["email"]])
        self.assertIn(MESSAGE["message"], mail.outbox[0].body)

    def test_bad_contact_shows_field_errors(self):
        response = self.client.post(reverse("contact"), MESSAGE | {"email": "invalid"})
        self.assertContains(response, "Enter a valid email address.", status_code=400)
        self.assertEqual(len(mail.outbox), 0)

    def test_contact_rejects_honeypot(self):
        form = ContactForm(MESSAGE | {"website": "https://example.test"})
        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error("website", "honeypot"))
        response = self.client.post(reverse("contact"), form.data, follow=True)
        self.assertRedirects(response, reverse("home") + "#contact")
        self.assertNotContains(response, "Your message was sent.")
        self.assertEqual(len(mail.outbox), 0)

    def test_contact_requires_post_and_csrf(self):
        url = reverse("contact")
        self.assertEqual(self.client.get(url).status_code, 405)
        csrf_client = Client(enforce_csrf_checks=True)
        self.assertEqual(csrf_client.post(url, MESSAGE).status_code, 403)
        csrf_client.get(reverse("home"))
        token = csrf_client.cookies["csrftoken"].value
        response = csrf_client.post(url, MESSAGE | {"csrfmiddlewaretoken": token})
        self.assertRedirects(response, reverse("home") + "#contact")

    def test_contact_handles_smtp_failure(self):
        with (
            patch("portfolio.views.EmailMessage.send", side_effect=SMTPException),
            self.assertLogs("portfolio.views", level="ERROR"),
        ):
            response = self.client.post(reverse("contact"), MESSAGE)
        self.assertContains(
            response, "The message could not be sent. Please try again.", status_code=503
        )


class ModelOrderingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_portfolio", stdout=StringIO())

    def test_experience_most_recent_first(self):
        self.assertEqual(
            list(Experience.objects.values_list("company", flat=True)),
            ["Morningstar", "Qualitest"],
        )

    def test_projects_by_position_then_title(self):
        first = Project.objects.first()
        earlier_title = Project.objects.create(
            title="A project", slug="a-project", position=first.position
        )
        self.assertEqual(list(Project.objects.all())[:2], [earlier_title, first])

    def test_skills_are_grouped_then_ordered(self):
        results = list(Skill.objects.values_list("category", "position", "name"))
        self.assertEqual(results, sorted(results))

    def test_education_dated_recent_first_then_undated(self):
        Education.objects.create(
            title="Undated", institution="Example", kind=Education.Kind.TRAINING
        )
        self.assertEqual(
            list(Education.objects.values_list("date", flat=True)),
            [date(2024, 9, 1), date(2023, 7, 1), date(2021, 5, 1), None],
        )

    def test_profile_is_a_database_singleton(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            SiteProfile.objects.create(id=2, name="Second profile")
