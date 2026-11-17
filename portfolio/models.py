from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


class SiteProfile(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)
    name = models.CharField(max_length=120)
    headline = models.CharField(max_length=150)
    intro = models.CharField(max_length=250)
    bio = models.TextField()
    location = models.CharField(max_length=100, blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)

    class Meta:
        verbose_name_plural = "site profile"
        constraints = [
            models.CheckConstraint(condition=models.Q(id=1), name="one_site_profile"),
        ]

    def __str__(self):
        return self.name


class Experience(models.Model):
    company = models.CharField(max_length=120)
    role = models.CharField(max_length=150)
    start_date = models.DateField(help_text="Use the first day when only the month is known.")
    end_date = models.DateField(blank=True, null=True, help_text="Leave blank for a current role.")
    highlights = models.TextField(help_text="One bullet per line.")

    class Meta:
        ordering = ["-start_date", "-pk"]
        verbose_name_plural = "experience"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_date__gte=models.F("start_date")) | models.Q(end_date=None),
                name="experience_dates_in_order",
            ),
        ]

    def __str__(self):
        return f"{self.role} at {self.company}"

    def clean(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "End date must be on or after the start date."})

    @property
    def bullets(self):
        return [line.strip() for line in self.highlights.splitlines() if line.strip()]


class Project(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    context = models.CharField(max_length=100, blank=True)
    summary = models.CharField(max_length=350)
    role = models.CharField(max_length=150)
    stack = models.CharField(max_length=250)
    details = models.TextField(blank=True, help_text="Fill in to publish a project detail page.")
    source_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    position = models.PositiveSmallIntegerField(default=0, help_text="Lower numbers appear first.")

    class Meta:
        ordering = ["position", "title", "pk"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("project", kwargs={"slug": self.slug})


class Skill(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    position = models.PositiveSmallIntegerField(
        default=0, help_text="Lower numbers appear first within each category."
    )

    class Meta:
        ordering = ["category", "position", "name", "pk"]
        constraints = [
            models.UniqueConstraint(fields=["category", "name"], name="unique_skill_in_category"),
        ]

    def __str__(self):
        return self.name


class Education(models.Model):
    class Kind(models.TextChoices):
        DEGREE = "degree", "Degree"
        TRAINING = "training", "Training"
        CERTIFICATE = "certificate", "Certificate"

    title = models.CharField(max_length=180)
    institution = models.CharField(max_length=150)
    kind = models.CharField(max_length=20, choices=Kind)
    date = models.DateField(
        null=True, blank=True, help_text="Use the first day when only the month is known."
    )
    status = models.CharField(max_length=180, blank=True)
    description = models.TextField(blank=True)
    credential_url = models.URLField(blank=True)

    class Meta:
        ordering = [models.F("date").desc(nulls_last=True), "-pk"]
        verbose_name_plural = "education"

    def __str__(self):
        return self.title
