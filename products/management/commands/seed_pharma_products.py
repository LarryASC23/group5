"""Populate the parody storefront with 30 illustrated fictional products."""

from decimal import Decimal
from pathlib import Path
from textwrap import wrap
from xml.sax.saxutils import escape

from django.conf import settings
from django.core.management.base import BaseCommand

from products.models import Category, Product


CATEGORIES = {
    "Paperwork Relief": "Parody products for the bureaucracy of modern care.",
    "Premium Placebos": "Imaginary remedies with premium packaging.",
    "Executive Wellness": "Fictional boardroom wellness essentials.",
    "Lifestyle Rx": "Satirical everyday lifestyle products.",
    "Brand Therapy": "Imaginary products from the marketing department.",
    "Future Formulas": "Speculative science-fiction pharmacy goods.",
}

# name, category, description, price, stock, package style, accent color
PRODUCTS = [
    ("CopayCalm", "Paperwork Relief", "A tiny bottle of patience for the moment you see the copay. Entirely fictional.", "39.99", 42, "bottle", "#45d6af"),
    ("PriorAuth Plus", "Paperwork Relief", "For the brave soul entering page seven of the approval form. Parody only.", "89.00", 18, "box", "#75b8ff"),
    ("ClaimBalm", "Paperwork Relief", "A soothing imaginary balm for claims marked pending indefinitely.", "24.50", 27, "tube", "#a7d465"),
    ("RedTape Relief", "Paperwork Relief", "A fictional fix for the bureaucracy that somehow needs another signature.", "54.95", 33, "box", "#f18881"),
    ("Coverage Compass", "Paperwork Relief", "Points toward the nearest in-network unicorn. Decorative, not medical.", "74.00", 12, "vial", "#69c8ed"),
    ("Formulary Flex", "Paperwork Relief", "The imaginary flexibility your formulary keeps promising.", "61.25", 21, "blister", "#9b9df2"),
    ("Placebo Deluxe", "Premium Placebos", "Nothing active, everything expensive. A fictional collector's item.", "129.00", 35, "bottle", "#dfb867"),
    ("Confidence Capsules", "Premium Placebos", "A glossy box of imaginary confidence with extra fine print.", "99.99", 24, "blister", "#ec89ba"),
    ("Miracle Maybe", "Premium Placebos", "Results may vary because this product exists only in a parody shop.", "149.00", 16, "vial", "#a98cef"),
    ("HopeSpray", "Premium Placebos", "A fictional mist of optimism for the waiting room.", "47.00", 38, "dropper", "#6bd6cf"),
    ("Nothingol XR", "Premium Placebos", "Extended release nothing, wrapped in an unusually confident carton.", "179.00", 11, "box", "#e6ac70"),
    ("Expectation Tabs", "Premium Placebos", "A pocket-sized reminder to read the whole imaginary label.", "32.00", 46, "blister", "#e7cf77"),
    ("Boardroom Bliss", "Executive Wellness", "For fictional executives who schedule relaxation in fifteen-minute blocks.", "249.00", 8, "bottle", "#83c6e8"),
    ("Stakeholder Serenity", "Executive Wellness", "An imaginary calm amid an inbox full of quarterly forecasts.", "199.00", 14, "vial", "#9dbaee"),
    ("MarginMint", "Executive Wellness", "A minty parody of the bottom line, with no actual active ingredient.", "119.00", 29, "blister", "#85d2a8"),
    ("Synergy Drops", "Executive Wellness", "A fictional dropper for meetings that could have been an email.", "159.00", 17, "dropper", "#b4a0ef"),
    ("Executive Balance", "Executive Wellness", "An imaginary formula for balancing a calendar with too many calls.", "229.00", 9, "box", "#ebad79"),
    ("Refillfinity", "Lifestyle Rx", "The refill reminder that keeps coming back. Novelty product only.", "68.00", 31, "bottle", "#6acbd3"),
    ("QueueLess", "Lifestyle Rx", "Pretend to skip the line without actually going anywhere.", "44.00", 43, "tube", "#c3d579"),
    ("Nocturna Nebula", "Lifestyle Rx", "A dreamy sci-fi bottle for your nightstand, not a sleep aid.", "84.00", 22, "dropper", "#8e9eea"),
    ("FocusForecast", "Lifestyle Rx", "Predicts a productive afternoon with the accuracy of a weather app.", "72.00", 34, "blister", "#e6bd70"),
    ("Weekend Warranty", "Lifestyle Rx", "An imaginary guarantee that Monday can wait a little longer.", "58.00", 26, "box", "#e4a1a9"),
    ("BrandGlow", "Brand Therapy", "A radiant imaginary rebrand in one sleek tube.", "139.00", 20, "tube", "#e3a1d5"),
    ("AdSpend Advance", "Brand Therapy", "A satirical bottle with a very large marketing budget.", "189.00", 15, "bottle", "#f2ad83"),
    ("FinePrint Forte", "Brand Therapy", "Packaging that makes the tiny disclaimer the main event.", "95.00", 28, "box", "#86a9e2"),
    ("PatentEver", "Brand Therapy", "A fictional formula with an exceptionally long shelf life on paper.", "299.00", 7, "vial", "#ddbb7d"),
    ("DataDose", "Future Formulas", "Algorithmically imagined and scientifically unavailable.", "109.00", 25, "blister", "#71d9c6"),
    ("Quantum Quarterly", "Future Formulas", "A speculative serum that exists in every quarter at once.", "329.00", 6, "vial", "#b297ec"),
    ("Tomorrow Tonic", "Future Formulas", "The future of fictional wellness, bottled today.", "79.00", 37, "dropper", "#70cfe8"),
    ("Labyrinth Labs", "Future Formulas", "An experimental-looking box with absolutely no experiment inside.", "159.00", 19, "box", "#d3c579"),
]


def package_shape(style, accent):
    """Return original vector package art; all styles share a 800 x 600 canvas."""
    if style == "bottle":
        return f'''<rect x="300" y="114" width="200" height="54" rx="13" fill="#dce5e9"/>
<path d="M322 168h156v31c29 16 38 36 38 67v227c0 23-18 41-41 41H325c-23 0-41-18-41-41V266c0-31 9-51 38-67z" fill="#f7f7f1"/>
<rect x="284" y="262" width="232" height="182" fill="{accent}"/>
<rect x="300" y="452" width="200" height="16" rx="8" fill="#e3e9e7"/>'''
    if style == "vial":
        return f'''<rect x="330" y="96" width="140" height="51" rx="9" fill="#c9d1d9"/>
<rect x="349" y="139" width="102" height="43" fill="#e5e6df"/>
<rect x="294" y="176" width="212" height="356" rx="43" fill="#e9dbc6"/>
<rect x="294" y="262" width="212" height="177" fill="{accent}"/>
<path d="M318 220v238" stroke="#fff" stroke-opacity=".4" stroke-width="12" stroke-linecap="round"/>'''
    if style == "tube":
        return f'''<path d="M292 133h216l-23 340H315z" fill="#f1f4ef"/>
<path d="M303 208h194l-13 230H316z" fill="{accent}"/>
<rect x="329" y="474" width="142" height="55" rx="8" fill="#d8dedc"/>
<path d="M292 133h216" stroke="#d5deda" stroke-width="14" stroke-linecap="round"/>'''
    if style == "dropper":
        return f'''<rect x="355" y="91" width="90" height="84" rx="17" fill="#313a48"/>
<rect x="373" y="168" width="54" height="46" fill="#c9d7dc"/>
<rect x="302" y="204" width="196" height="324" rx="47" fill="#d8e1e1"/>
<rect x="302" y="278" width="196" height="178" fill="{accent}"/>
<path d="M326 246v240" stroke="#fff" stroke-opacity=".4" stroke-width="12" stroke-linecap="round"/>'''
    if style == "blister":
        pills = "".join(
            f'<circle cx="{x}" cy="{y}" r="32" fill="{accent}" stroke="#f8faf9" stroke-width="9"/>'
            for y in (260, 360, 460) for x in (344, 456)
        )
        return f'''<rect x="282" y="173" width="236" height="356" rx="20" fill="#dce3e6"/>
<rect x="301" y="193" width="198" height="317" rx="12" fill="#eef1f0"/>{pills}'''
    return f'''<path d="M269 137h238l25 390H294z" fill="#dae1e0"/>
<rect x="266" y="112" width="241" height="402" rx="8" fill="#f8f7f0"/>
<rect x="266" y="210" width="241" height="216" fill="{accent}"/>
<path d="M507 112l27 25v377h-27z" fill="#c6cecc"/>'''


def product_svg(name, category, style, accent):
    lines = wrap(name.upper(), width=16)
    label_y = 327 if style != "blister" else 132
    label_color = "#172333" if style != "blister" else "#f1f7f7"
    title = "".join(
        f'<text x="400" y="{label_y + i * 29}" text-anchor="middle" '
        f'font-family="Arial,sans-serif" font-size="25" font-weight="800" '
        f'fill="{label_color}">{escape(line)}</text>'
        for i, line in enumerate(lines[:2])
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" role="img" aria-label="Illustrated package of {escape(name)}">
<defs>
  <linearGradient id="bg" x2="1" y2="1"><stop stop-color="#1a2933"/><stop offset="1" stop-color="#0b161d"/></linearGradient>
  <filter id="shadow"><feGaussianBlur stdDeviation="17"/></filter>
</defs>
<rect width="800" height="600" fill="url(#bg)"/>
<circle cx="671" cy="86" r="155" fill="{accent}" opacity=".10"/>
<circle cx="114" cy="519" r="184" fill="{accent}" opacity=".07"/>
<path d="M0 534h800" stroke="{accent}" stroke-opacity=".33"/>
<ellipse cx="404" cy="541" rx="181" ry="25" fill="#000" opacity=".65" filter="url(#shadow)"/>
{package_shape(style, accent)}
{title}
<text x="400" y="{label_y + min(len(lines), 2) * 29 + 18}" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="700" letter-spacing="2" fill="{label_color}">SHADY SHOP LABS</text>
<text x="44" y="49" font-family="Arial,sans-serif" font-size="14" font-weight="700" letter-spacing="3" fill="{accent}">SHADY SHOP // PHARMA</text>
<text x="44" y="569" font-family="Arial,sans-serif" font-size="13" letter-spacing="2" fill="#adbac0">{escape(category.upper())}</text>
<text x="755" y="569" text-anchor="end" font-family="Arial,sans-serif" font-size="11" fill="#adbac0">FICTIONAL PARODY PRODUCT</text>
</svg>'''


class Command(BaseCommand):
    help = "Add 30 fictional pharma products and their original SVG package images. Safe to rerun."

    def handle(self, *args, **options):
        image_dir = Path(settings.MEDIA_ROOT) / "products"
        image_dir.mkdir(parents=True, exist_ok=True)
        categories = {
            name: Category.objects.get_or_create(name=name, defaults={"description": description})[0]
            for name, description in CATEGORIES.items()
        }

        created = 0
        for index, (name, category, description, price, stock, style, accent) in enumerate(PRODUCTS, start=1):
            filename = f"pharma-{index:02d}.svg"
            image_path = image_dir / filename
            if not image_path.exists():
                image_path.write_text(product_svg(name, category, style, accent), encoding="utf-8")

            product, was_created = Product.objects.get_or_create(
                name=name,
                defaults={
                    "description": description,
                    "price": Decimal(price),
                    "quantity": stock,
                    "image": f"products/{filename}",
                    "is_active": True,
                },
            )
            if was_created:
                product.categories.add(categories[category])
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Added {created} products; {len(PRODUCTS)} catalog entries available."))
