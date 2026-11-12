# Shady Shop

CS 3773 storefront demo built with Django and SQLite.

## Run locally

1. Install the packages in `requirements.txt`.
2. Run `python manage.py migrate`.
3. On a fresh database, run `python manage.py loaddata demo_catalog`.
4. Run `python manage.py runserver` and open `/`.

Product images are included in `media/products/`. Their sources and licenses are recorded in `products/image_sources.json` and shown at `/image-credits/`.

Run `python manage.py createsuperuser` if you need the admin interface.
