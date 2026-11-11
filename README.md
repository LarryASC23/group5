# Shady Shop

CS 3773 parody storefront. Products, carts, accounts, orders, discounts, and inventory use Django and SQLite.

## Run locally

1. Install the packages in `requirements.txt`.
2. Run `python manage.py migrate`.
3. On a fresh database, run `python manage.py loaddata demo_catalog` to load the demo catalog.
4. Run `python manage.py restore_demo_images` to create local product illustrations for missing demo media files.
5. Run `python manage.py runserver` and open `/`.

Create an admin user with `python manage.py createsuperuser` to manage products, sales, discount codes, and orders. Checkout records a demo order and updates stock; it does not take a payment.

## Still to build

- Payment processing or a test payment flow, if the project needs one.
- Password reset and transactional email; the current email backend prints to the console.
- Production configuration for secrets, hosts, static files, and uploaded media.
- Stronger checkout concurrency handling before using a multi-user production database.
- Product name snapshots in order items if order history must survive later product edits.
