# Shady Shop

CS 3773 parody storefront. Products, carts, accounts, orders, discounts, and inventory use Django and SQLite.

## Run locally

1. Install the packages in `requirements.txt`.
2. Run `python manage.py migrate`.
3. On a fresh database, run `python manage.py loaddata demo_catalog` to load the demo catalog.
4. Run `python manage.py runserver` and open `/`. The sourced product images are included in `media/products/`.

The demo catalog uses real-world objects and photos in a fictional, shady-looking storefront. It has 17 active listings across five categories and an active 20% sale on every listing. Image sources, creators, and licenses are listed in `products/image_sources.json` and at `/image-credits/`.

Create an admin user with `python manage.py createsuperuser` to manage products, sales, discount codes, and orders. Checkout records a demo order and updates stock; it does not take a payment.

## Put the demo online with PythonAnywhere

PythonAnywhere's free web app is a practical fit for this class demo because the project already uses SQLite and stores its image files locally. Free web apps expire after one month, so check that yours is active before grading. Choose a system image that supports Python 3.13 and use that version for both the virtual environment and web app.

1. Push this repository to GitHub. Do not commit `db.sqlite3`, `.venv/`, or `staticfiles/`.
2. In a PythonAnywhere Bash console, clone the repository, then run `cd group5`, `python3.13 -m venv .venv`, `source .venv/bin/activate`, and `pip install -r requirements.txt`.
3. Still in that console, run `python manage.py migrate`, `python manage.py loaddata demo_catalog`, and `python manage.py collectstatic --noinput`. Create an admin user with `python manage.py createsuperuser` if needed.
4. In the **Web** tab, create a **Manual configuration** web app with Python 3.13 and set its virtualenv to `/home/YOUR_USERNAME/group5/.venv` (adjust the clone folder if needed).
5. Edit the Web tab's WSGI file. Use the example below, replacing `YOUR_USERNAME` and the secret. You can generate a secret in the console with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`. Keep the secret in the PythonAnywhere WSGI file, never in GitHub.
6. In the Web tab's **Static files** section, map `/static/` to `/home/YOUR_USERNAME/group5/staticfiles` and `/media/` to `/home/YOUR_USERNAME/group5/media`. Reload the web app and visit `https://YOUR_USERNAME.pythonanywhere.com/`.

```python
import os
import sys

project_path = "/home/YOUR_USERNAME/group5"
if project_path not in sys.path:
    sys.path.insert(0, project_path)

os.environ["DJANGO_DEBUG"] = "False"
os.environ["DJANGO_ALLOWED_HOSTS"] = "YOUR_USERNAME.pythonanywhere.com"
os.environ["DJANGO_SECRET_KEY"] = "PASTE_A_NEW_RANDOM_SECRET_HERE"
from appProto.wsgi import application
```

The included images are regular files in `media/products/`, so the `/media/` mapping is needed for them to appear when `DEBUG=False`. The SQLite setup is suitable for showing the project to a class; for a busy public store, move to a production database and storage service.

## Still to build

- Payment processing or a test payment flow, if the project needs one.
- Password reset and transactional email; the current email backend prints to the console.
- A production database and storage service if the site will handle heavy traffic or user uploads.
- Stronger checkout concurrency handling before using a multi-user production database.
- Product name snapshots in order items if order history must survive later product edits.
