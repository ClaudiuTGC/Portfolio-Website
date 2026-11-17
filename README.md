# Claudiu Tananau · Portfolio

A Django portfolio for Claudiu Tananau, Senior Security Analyst.

## Run locally

Use Python 3.12 or later.

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_portfolio
python manage.py createsuperuser
python manage.py runserver
```

Open http://localhost:8000. Contact submissions print to the server terminal in development.

## Edit content

Sign in at http://localhost:8000/admin/. Edit the hero, bio and links under **Site profile**. Experience and education entries sort newest first. Add one experience highlight per line. Skills group by category and sort by position within each group. Projects sort by position. Filling in a project’s details publishes its own page and adds it to the sitemap.

The seed command loads an empty portfolio database from the CV, the Tines update and public GitHub project files. Subsequent runs preserve changes made in admin.

## Check changes

```sh
python manage.py test
ruff check .
python manage.py makemigrations --check --dry-run
```

## Deploy on a VPS

Create a PostgreSQL database and a dedicated app user. Install `requirements.txt` in a Python 3.12+ virtual environment. Copy the settings in `.env.example` into your service environment or a private `.env` file.

- Set `DJANGO_DEBUG=False`, a strong unique `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, and an HTTPS `SITE_URL` without a trailing path.
- Set `DATABASE_URL` to the PostgreSQL connection URL.
- Set `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` and `CONTACT_EMAIL`. Configure TLS or SSL to match the SMTP provider.
- Set `DJANGO_CSRF_TRUSTED_ORIGINS` to the public HTTPS origin. Set `DJANGO_TRUST_PROXY_HTTPS=True` when Nginx is the trusted proxy and overwrites `X-Forwarded-Proto`.

Run these commands before starting the service. Create the superuser once.

```sh
python manage.py migrate --noinput
python manage.py seed_portfolio
python manage.py collectstatic --noinput
python manage.py createsuperuser
gunicorn config.wsgi:application --bind 127.0.0.1:8000
```

Run Gunicorn under systemd. In the Nginx HTTPS server block, proxy to Gunicorn and let WhiteNoise serve static files.

```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

Redirect HTTP to HTTPS in Nginx. Verify `/sitemap.xml`, an admin sign-in and a contact message after deployment.
