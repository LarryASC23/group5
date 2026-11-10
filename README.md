# group5
project for cs3773

## Demo catalog

Run `python manage.py migrate`, then `python manage.py seed_pharma_products` to add
30 fictional pharma products to the SQLite catalog. The seed command creates
original SVG package illustrations in `media/products/` and is safe to rerun.
Start the development server with `python manage.py runserver`; the products
appear at `/products/` and the first four appear on the home page.
