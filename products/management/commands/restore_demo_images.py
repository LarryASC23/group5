"""Create local illustrations for demo products whose uploaded files are absent."""

from pathlib import Path
from textwrap import wrap
from xml.sax.saxutils import escape

from django.conf import settings
from django.core.management.base import BaseCommand

from products.models import Product


PALETTE = ("#52d6ae", "#88b9f5", "#dba3eb", "#f0ad79", "#b8d775", "#e793af")


def artwork(name, category, index):
    accent = PALETTE[index % len(PALETTE)]
    title_lines = wrap(name.upper(), width=15)[:2]
    title = "".join(
        f'<text x="400" y="{307 + line * 34}" text-anchor="middle" '
        f'font-family="Arial,sans-serif" font-size="28" font-weight="800" '
        f'fill="#15212a">{escape(text)}</text>'
        for line, text in enumerate(title_lines)
    )
    shape = index % 3
    if shape == 0:
        package = f'''<rect x="302" y="134" width="196" height="51" rx="10" fill="#d7dfdf"/>
<path d="M325 184h150v36c27 13 40 34 40 68v205c0 23-19 42-42 42H327c-23 0-42-19-42-42V288c0-34 13-55 40-68z" fill="#f3f5ef"/>
<rect x="285" y="251" width="230" height="186" fill="{accent}"/>'''
    elif shape == 1:
        package = f'''<path d="M282 132h250v386H282z" fill="#c9d3d3"/>
<rect x="264" y="111" width="247" height="408" rx="9" fill="#f4f5ef"/>
<rect x="264" y="220" width="247" height="218" fill="{accent}"/>'''
    else:
        package = f'''<rect x="337" y="108" width="126" height="54" rx="10" fill="#c4cdd0"/>
<rect x="351" y="158" width="98" height="42" fill="#e2e6e2"/>
<rect x="292" y="195" width="216" height="335" rx="45" fill="#e4e7de"/>
<rect x="292" y="263" width="216" height="180" fill="{accent}"/>'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" role="img" aria-label="Illustration of {escape(name)}">
<defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#1c2c35"/><stop offset="1" stop-color="#0d171d"/></linearGradient></defs>
<rect width="800" height="600" fill="url(#bg)"/>
<circle cx="670" cy="90" r="167" fill="{accent}" opacity=".09"/>
<circle cx="120" cy="518" r="151" fill="{accent}" opacity=".07"/>
<ellipse cx="400" cy="541" rx="165" ry="20" fill="#05090c" opacity=".6"/>
{package}
{title}
<text x="400" y="{332 + len(title_lines) * 34}" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="700" letter-spacing="2" fill="#15212a">SHADY SHOP LABS</text>
<text x="43" y="50" font-family="Arial,sans-serif" font-size="14" font-weight="700" letter-spacing="3" fill="{accent}">SHADY SHOP // PHARMA</text>
<text x="43" y="568" font-family="Arial,sans-serif" font-size="13" fill="#b5c2c4">{escape(category.upper())}</text>
<text x="756" y="568" text-anchor="end" font-family="Arial,sans-serif" font-size="11" fill="#b5c2c4">FICTIONAL PARODY PRODUCT</text>
</svg>'''


class Command(BaseCommand):
    help = "Restore original SVG demo art for products with missing media files."

    def handle(self, *args, **options):
        directory = Path(settings.MEDIA_ROOT) / "products"
        directory.mkdir(parents=True, exist_ok=True)
        restored = 0
        for index, product in enumerate(Product.objects.prefetch_related("categories").order_by("pk")):
            if not (
                product.image.name.startswith(("products/pharma-", "products/demo-"))
                or product.image.name in ("products/images.jpg", "products/Blue_Sky_meth.webp")
            ):
                continue
            current = Path(settings.MEDIA_ROOT) / product.image.name if product.image else None
            if current and current.exists():
                continue
            filename = f"demo-{product.pk:03d}.svg"
            destination = directory / filename
            category = next(iter(product.categories.all()), None)
            destination.write_text(artwork(product.name, category.name if category else "Demo product", index), encoding="utf-8")
            product.image.name = f"products/{filename}"
            product.save(update_fields=["image"])
            restored += 1
        self.stdout.write(self.style.SUCCESS(f"Restored {restored} product images."))
