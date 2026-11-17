from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from portfolio.models import Education, Experience, Project, SiteProfile, Skill

SKILLS = {
    "Application security": [
        "Secure code review",
        "Vulnerability assessment",
        "Checkmarx SAST",
        "CxQL",
        "Semgrep",
        "Black Duck",
        "OWASP Top 10",
        "CWE Top 25",
        "Threat modeling documentation",
    ],
    "Security operations": [
        "Identity and access management",
        "SailPoint",
        "ServiceNow",
        "UpGuard",
        "Phishing awareness",
    ],
    "Automation and development": [
        "Tines",
        "Python",
        "Django",
        "SQL",
        "C++",
        "Java",
        "JavaScript",
        "HTML and CSS",
    ],
    "Governance": ["Vendor risk assessment", "Third-party security assessment", "Transcend"],
}


class Command(BaseCommand):
    help = "Load the starting portfolio content into an empty database."

    @transaction.atomic
    def handle(self, *args, **options):
        if any(
            model.objects.exists()
            for model in (SiteProfile, Experience, Project, Skill, Education)
        ):
            self.stdout.write("Portfolio content already exists. No changes made.")
            return

        SiteProfile.objects.create(
            name="Claudiu Tananau",
            headline="Senior Security Analyst",
            intro="I automate end-to-end security workflows in Tines at Morningstar.",
            bio=(
                "I work in security operations at Morningstar, where I automate workflows "
                "with Tines and work across access management, security requests and vendor "
                "data governance.\n\n"
                "At Qualitest, I reviewed source code, wrote custom Checkmarx queries and "
                "helped clients understand what to fix and why."
            ),
            location="Bucharest, Romania",
            github_url="https://github.com/ClaudiuTGC",
            linkedin_url="https://www.linkedin.com/in/claudiu-tananau-619198202",
        )
        Experience.objects.create(
            company="Morningstar",
            role="Senior Security Analyst",
            start_date=date(2024, 10, 1),
            highlights=(
                "Automate end-to-end internal workflows with Tines.\n"
                "Review access to Black Duck, Semgrep and Checkmarx, and provision access "
                "through SailPoint.\n"
                "Resolve security requests in ServiceNow, review firewall changes and "
                "coordinate remediation from UpGuard monitoring.\n"
                "Map vendor data flows in Transcend and support internal phishing awareness "
                "campaigns."
            ),
        )
        Experience.objects.create(
            company="Qualitest",
            role="Application Security Analyst",
            start_date=date(2021, 6, 1),
            end_date=date(2024, 7, 1),
            highlights=(
                "Reviewed source code in Checkmarx and confirmed findings such as SQL "
                "injection and cross-site scripting.\n"
                "Wrote custom CxQL queries and added findings that automated scans missed.\n"
                "Explained findings, impact and remediation to clients and prepared "
                "security assessment reports.\n"
                "Received the Qualitest Spotlight Award in May 2022."
            ),
        )
        Project.objects.create(
            title="Security workflow automation",
            slug="security-workflow-automation",
            context="Morningstar",
            summary="End-to-end automation for internal workflows at Morningstar.",
            role="Senior Security Analyst",
            stack="Tines",
            position=1,
        )
        Project.objects.create(
            title="BestPrice",
            slug="bestprice",
            context="Personal project",
            summary="A Django web app with product pages, comments and wishlists.",
            role="Developer",
            stack="Python, Django",
            details=(
                "I built BestPrice as a personal Django project. The app organizes product "
                "listings into categories and stores each product’s price and link.\n\n"
                "The site has account registration, product comments and a wishlist where "
                "users can save products."
            ),
            source_url="https://github.com/ClaudiuTGC/Personal-Project---BestPrice",
            position=2,
        )
        Skill.objects.bulk_create(
            Skill(name=name, category=category, position=position)
            for category, names in SKILLS.items()
            for position, name in enumerate(names, start=1)
        )
        Education.objects.bulk_create(
            [
                Education(
                    title="Google Cybersecurity Certificate",
                    institution="Google",
                    kind=Education.Kind.CERTIFICATE,
                    date=date(2024, 9, 1),
                    status="In progress as of Sep 2024 · Completion unconfirmed",
                    description="Training in threat detection, risk management and network security.",
                ),
                Education(
                    title="Bachelor’s, Foreign Languages and Literatures",
                    institution="University of Bucharest",
                    kind=Education.Kind.DEGREE,
                    date=date(2023, 7, 1),
                ),
                Education(
                    title="Computer and Information Sciences",
                    institution="WellCode",
                    kind=Education.Kind.TRAINING,
                    date=date(2021, 5, 1),
                    description=(
                        "Mentorship in C++, data structures, Java, SQL and unit testing. "
                        "Solved over 150 algorithm problems."
                    ),
                ),
            ]
        )
        self.stdout.write(self.style.SUCCESS("Portfolio content loaded."))
