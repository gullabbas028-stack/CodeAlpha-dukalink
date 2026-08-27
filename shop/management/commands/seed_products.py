from django.core.management.base import BaseCommand
from django.db import transaction

from shop.models import Category, Product

CATEGORY_DEFS = [
    ("Electronics", "💻"),
    ("Mobile Accessories", "📱"),
    ("Fashion", "👕"),
    ("Shoes", "👟"),
    ("Beauty", "💄"),
    ("Home & Kitchen", "🍳"),
    ("Accessories", "⌚"),
    ("Sports", "🏸"),
]

PRODUCT_IMAGE_URLS = {
    "headphones": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e",
    "watch": "https://images.unsplash.com/photo-1523275335684-37898b6baf30",
    "speaker": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1",
    "camera": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32",
    "keyboard": "https://images.unsplash.com/photo-1587829741301-dc798b83add3",
    "mouse": "https://images.unsplash.com/photo-1527814050087-3793815479db",
    "monitor": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf",
    "phone": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9",
    "cycling": "https://images.unsplash.com/photo-1558981806-ec527fa84c39",
    "resistance": "https://images.unsplash.com/photo-1598289431512-b97b0917affc",
    "badminton": "https://images.unsplash.com/photo-1626224583764-f87db24ac4ea",
    "football": "https://images.unsplash.com/photo-1579952363873-27f3bade9f55",
    "dumbbell": "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61",
    "yoga": "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b",
    "card": "https://images.unsplash.com/photo-1627123424574-724758594e93",
    "shirt": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf",
    "dress": "https://images.unsplash.com/photo-1496747611176-843222e1e57c",
    "jeans": "https://images.unsplash.com/photo-1542272604-787c3835535d",
    "jacket": "https://images.unsplash.com/photo-1551028719-00167b16eac5",
    "hoodie": "https://images.unsplash.com/photo-1556821840-3a63f95609a7",
    "shoes": "https://images.unsplash.com/photo-1542291026-7eec264c27ff",
    "lipstick": "https://images.unsplash.com/photo-1586495777744-4413f21062fa",
    "face": "https://images.unsplash.com/photo-1556229010-6c3f2c9ca5f8",
    "hair": "https://images.unsplash.com/photo-1522338242992-e1a54906a8da",
    "serum": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be",
    "cookware": "https://images.unsplash.com/photo-1556911220-e15b29be8c8f",
    "kettle": "https://images.unsplash.com/photo-1556911220-e15b29be8c8f",
    "pillow": "https://images.unsplash.com/photo-1584100936595-c0654b55a2e2",
    "dinner": "https://images.unsplash.com/photo-1603199506016-b9a594b593c0",
    "vacuum": "https://images.unsplash.com/photo-1558317374-067fb5f30001",
    "lunch": "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519",
    "sunglasses": "https://images.unsplash.com/photo-1511499767150-a48a237f0083",
    "backpack": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62",
    "fitness": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438",
}


def product_image_url(name):
    name_lower = name.lower()
    image_url = next(
        (url for keyword, url in PRODUCT_IMAGE_URLS.items() if keyword in name_lower),
        "https://images.unsplash.com/photo-1523275335684-37898b6baf30",
    )
    return f"{image_url}?auto=format&fit=crop&w=600&h=600&q=85"

# (name, short_description, description, price, discount_price or None,
#  stock, rating, features[list], flags: featured/new/popular/sale)
PRODUCTS = {
    "Electronics": [
        ("Wireless Bluetooth Headphones", "Over-ear ANC headphones with 30h battery",
         "Immerse yourself in rich, balanced sound with active noise cancellation that "
         "cuts out the daily commute. A 30-hour battery and quick-charge port mean they "
         "keep up with long travel days.",
         4999, 3999, 24, 4.6,
         ["Active noise cancellation", "30-hour battery life", "Bluetooth 5.3", "Foldable design"],
         True, False, True, True),
        ("Smart Watch Series X", "Fitness tracking smartwatch with AMOLED display",
         "Track heart rate, sleep, and workouts on a crisp AMOLED display that stays "
         "readable in direct sunlight. Notifications, calls, and 7-day battery life keep "
         "you connected without a charger in sight.",
         8999, 7499, 15, 4.5,
         ["1.4\" AMOLED display", "7-day battery life", "Heart rate & SpO2 monitor", "5ATM water resistance"],
         True, True, False, True),
        ("Portable Bluetooth Speaker", "Compact speaker with deep bass and IPX7 rating",
         "A pocket-sized speaker that punches above its weight — deep bass, clear "
         "mids, and an IPX7 rating that shrugs off pool splashes and rain.",
         3499, None, 30, 4.3,
         ["12-hour playtime", "IPX7 waterproof", "TWS pairing", "Built-in mic for calls"],
         False, True, True, False),
        ("4K Action Camera", "Waterproof action camera with image stabilization",
         "Capture trail runs and rooftop views in crisp 4K with built-in stabilization "
         "that smooths out the bumps. Waterproof to 10m without a case.",
         12999, 10999, 8, 4.4,
         ["4K/30fps recording", "Waterproof to 10m", "Electronic image stabilization", "Wi-Fi transfer"],
         False, False, False, True),
        ("Mechanical Gaming Keyboard", "RGB backlit keyboard with hot-swappable switches",
         "Tactile hot-swappable switches under a durable aluminum frame, with per-key "
         "RGB that syncs to your setup instead of just looking busy.",
         6499, None, 18, 4.7,
         ["Hot-swappable switches", "Per-key RGB lighting", "Aluminum top plate", "Detachable USB-C cable"],
         True, False, True, False),
        ("Wireless Mouse Pro", "Ergonomic wireless mouse with silent clicks",
         "An ergonomic shape that doesn't fatigue your wrist by hour three, with "
         "silent clicks your officemates will thank you for.",
         2299, 1799, 40, 4.2,
         ["Silent click switches", "2.4GHz + Bluetooth", "3-month battery life", "Adjustable DPI up to 4000"],
         False, False, False, True),
        ("27-inch LED Monitor", "Full HD monitor with slim bezels",
         "A slim-bezel 27-inch panel that makes a two-monitor setup feel like one wide "
         "canvas — sharp text, accurate color, and a stand that actually tilts.",
         21999, None, 6, 4.5,
         ["Full HD 1920x1080", "75Hz refresh rate", "Slim bezel design", "VESA mount compatible"],
         False, True, False, False),
        ("Power Bank 20000mAh", "Fast-charging power bank with dual USB output",
         "20,000mAh of backup power with fast charging on two ports at once, so you "
         "and a friend never have to argue over the cable.",
         2999, None, 50, 4.3,
         ["20,000mAh capacity", "18W fast charging", "Dual USB-A + USB-C", "LED charge indicator"],
         False, False, True, False),
    ],
    "Mobile Accessories": [
        ("Tempered Glass Screen Protector", "9H hardness glass for scratch protection",
         "Edge-to-edge coverage at 9H hardness — the kind of protector you forget is "
         "even there until your phone survives a drop.",
         499, None, 100, 4.1,
         ["9H hardness", "Oleophobic coating", "Bubble-free installation", "Case-friendly edges"],
         False, False, False, False),
        ("Shockproof Phone Case", "Military-grade drop protection case",
         "Military-grade drop protection wrapped in a slim profile, so your phone "
         "survives the fall without living in a brick.",
         899, 699, 60, 4.4,
         ["Military-grade drop tested", "Raised bezel for screen/camera", "Slim profile", "Wireless charging compatible"],
         True, False, False, True),
        ("Fast Charging Cable Type-C", "Braided nylon charging cable, 1.2m",
         "A braided nylon cable built to survive backpack tangles and daily plugging, "
         "rated for fast charging on any USB-C device.",
         399, None, 150, 4.0,
         ["Braided nylon jacket", "1.2m length", "60W fast charging support", "10,000+ bend lifespan"],
         False, False, False, False),
        ("Car Phone Mount Holder", "360° rotating dashboard phone mount",
         "A one-hand-squeeze mount that locks your phone in place on the dash and "
         "rotates a full 360° for either orientation.",
         799, None, 45, 4.2,
         ["360° rotation", "One-hand operation", "Strong suction base", "Fits 4-7 inch phones"],
         False, True, False, False),
        ("Wireless Charging Pad", "10W fast wireless charger for Qi-enabled phones",
         "Set your phone down and it starts charging — 10W of Qi-certified power with "
         "a non-slip surface so it doesn't wander off the pad.",
         1499, 1199, 35, 4.3,
         ["10W fast wireless charging", "Qi-certified", "Non-slip surface", "LED charge indicator"],
         False, False, True, True),
        ("Bluetooth Earbuds Mini", "Compact TWS earbuds with charging case",
         "Compact enough to forget in your pocket, with a charging case that adds "
         "three extra full charges when you're away from an outlet.",
         2499, None, 28, 4.1,
         ["Touch controls", "20-hour total battery (with case)", "IPX4 sweat resistant", "Auto-pair"],
         False, False, False, False),
    ],
    "Fashion": [
        ("Men's Casual Cotton Shirt", "Breathable slim-fit cotton shirt",
         "Soft, breathable cotton cut in a slim fit that layers well under a jacket "
         "or stands on its own for a casual Friday.",
         2499, 1999, 22, 4.2,
         ["100% cotton", "Slim fit", "Machine washable", "Available in 5 colors"],
         True, False, False, True),
        ("Women's Floral Summer Dress", "Lightweight flowy dress for warm days",
         "A flowy silhouette in a lightweight fabric that moves with you — built for "
         "warm days and long lunches.",
         3499, None, 16, 4.5,
         ["Lightweight breathable fabric", "Flowy A-line cut", "Hand or machine wash", "Lined bodice"],
         True, True, False, False),
        ("Men's Slim Fit Jeans", "Stretch denim jeans in classic wash",
         "Stretch denim that keeps its shape through the day, cut slim without "
         "fighting you when you sit down.",
         3299, 2799, 30, 4.3,
         ["Stretch denim blend", "Slim fit", "Classic 5-pocket styling", "Mid-rise waist"],
         False, False, True, True),
        ("Women's Denim Jacket", "Classic oversized denim jacket",
         "An oversized cut you can throw over anything, in a wash that only gets "
         "better with wear.",
         4499, None, 12, 4.4,
         ["Oversized fit", "Button front closure", "Chest and side pockets", "100% cotton denim"],
         False, True, False, False),
        ("Unisex Hooded Sweatshirt", "Fleece-lined pullover hoodie",
         "Fleece-lined warmth for cool evenings, with a kangaroo pocket built for "
         "cold hands and phone storage alike.",
         2999, 2399, 40, 4.6,
         ["Fleece-lined interior", "Kangaroo pocket", "Ribbed cuffs and hem", "Unisex sizing"],
         True, False, True, True),
        ("Men's Formal Blazer", "Tailored two-button blazer",
         "A tailored two-button cut that goes from the boardroom to dinner without "
         "changing — a wardrobe staple, not a costume.",
         7999, None, 8, 4.5,
         ["Tailored fit", "Two-button closure", "Interior pockets", "Dry clean recommended"],
         False, False, False, False),
    ],
    "Shoes": [
        ("Men's Running Shoes", "Lightweight breathable running sneakers",
         "A breathable mesh upper and a cushioned midsole built for the miles you "
         "actually run, not just the ones on the box.",
         5999, 4999, 25, 4.6,
         ["Breathable mesh upper", "Cushioned EVA midsole", "Rubber outsole grip", "Lightweight 260g"],
         True, False, True, True),
        ("Women's Casual Sneakers", "Everyday comfort sneakers",
         "The sneaker that ends up on your feet every day — soft, supportive, and "
         "unfussy about what you pair it with.",
         4499, None, 20, 4.4,
         ["Memory foam insole", "Breathable canvas upper", "Non-slip sole", "Available in 4 colors"],
         False, True, False, False),
        ("Men's Formal Leather Shoes", "Genuine leather oxford shoes",
         "Genuine leather oxfords with a hand-stitched sole — the kind of shoe that "
         "gets better with a little polish and a lot of wear.",
         6999, 5999, 10, 4.5,
         ["Genuine leather upper", "Hand-stitched sole", "Cushioned footbed", "Classic oxford styling"],
         False, False, False, True),
        ("Kids' Sports Shoes", "Durable and flexible sneakers for kids",
         "Flexible, durable, and easy to pull on — built for a kid who doesn't sit "
         "still, with a sole that grips the playground.",
         2999, None, 18, 4.3,
         ["Flexible sole", "Easy velcro closure", "Reinforced toe cap", "Machine washable"],
         False, False, True, False),
        ("Women's Wedge Sandals", "Comfortable everyday wedge sandals",
         "A low wedge with real cushioning underfoot, so 'dressy' doesn't mean "
         "sore feet by evening.",
         3799, 2999, 14, 4.2,
         ["Cushioned footbed", "Adjustable ankle strap", "Non-slip outsole", "3cm wedge height"],
         False, False, False, True),
    ],
    "Beauty": [
        ("Matte Liquid Lipstick Set", "Long-lasting matte lipstick — pack of 3",
         "Three long-wear matte shades that don't need a midday touch-up, in a "
         "formula that feels lightweight instead of drying.",
         1999, 1499, 35, 4.4,
         ["Long-lasting matte finish", "Set of 3 shades", "Transfer-resistant", "Enriched with vitamin E"],
         True, False, True, True),
        ("Herbal Face Wash", "Gentle daily cleanser with neem extract",
         "A gentle daily cleanser with neem extract that clears without stripping "
         "your skin's natural balance.",
         899, None, 60, 4.2,
         ["Neem extract formula", "Suitable for daily use", "Soap-free", "For all skin types"],
         False, False, False, False),
        ("Professional Hair Dryer", "1800W ionic hair dryer with diffuser",
         "1800W of ionic drying power that cuts frizz and drying time, with a "
         "diffuser attachment for curls that keep their shape.",
         3499, 2999, 16, 4.5,
         ["1800W ionic technology", "3 heat / 2 speed settings", "Includes diffuser attachment", "Cool shot button"],
         False, True, False, True),
        ("Vitamin C Serum", "Brightening facial serum with hyaluronic acid",
         "A brightening serum that layers hyaluronic acid under vitamin C for glow "
         "without the sting some formulas leave behind.",
         1799, None, 40, 4.6,
         ["10% Vitamin C", "Hyaluronic acid for hydration", "Lightweight, fast-absorbing", "Suitable for daily use"],
         True, False, True, False),
        ("Electric Facial Cleansing Brush", "Silicone sonic facial brush",
         "Sonic vibration on a soft silicone head, gentle enough for daily use and "
         "thorough enough to actually clear your pores.",
         2499, 1999, 22, 4.3,
         ["Sonic vibration cleansing", "Silicone bristle head", "USB rechargeable", "Waterproof for shower use"],
         False, False, False, True),
    ],
    "Home & Kitchen": [
        ("Non-Stick Cookware Set", "5-piece non-stick pot and pan set",
         "Five pieces that cover everything from a quick omelet to a family-sized "
         "curry, with a coating that actually holds up to a metal spoon slip.",
         6999, 5499, 12, 4.5,
         ["5-piece set", "Non-stick coating", "Compatible with all stovetops", "Heat-resistant handles"],
         True, False, False, True),
        ("Electric Kettle 1.7L", "Fast-boil stainless steel kettle",
         "Boils a full kettle in under four minutes, with an auto shut-off so you "
         "can walk away without a second thought.",
         2299, None, 30, 4.3,
         ["1.7L capacity", "Auto shut-off", "Stainless steel body", "Boil-dry protection"],
         False, True, True, False),
        ("Memory Foam Bed Pillow", "Contour pillow with cooling gel layer",
         "A contour shape that actually supports your neck, topped with a cooling "
         "gel layer for the nights that run warm.",
         2999, 2499, 25, 4.4,
         ["Memory foam core", "Cooling gel top layer", "Removable washable cover", "Hypoallergenic"],
         False, False, False, True),
        ("Ceramic Dinner Set", "16-piece ceramic dinnerware set",
         "Sixteen pieces in a glaze that resists chipping through years of Sunday "
         "dinners and everyday breakfasts alike.",
         5499, None, 9, 4.6,
         ["16-piece set (4 settings)", "Chip-resistant glaze", "Microwave & dishwasher safe", "Neutral everyday design"],
         True, True, False, False),
        ("Robot Vacuum Cleaner", "Smart robotic vacuum with app control",
         "Maps your floor plan, avoids the stairs, and empties itself into a "
         "compact dustbin — cleaning you genuinely forget is happening.",
         18999, 15999, 5, 4.4,
         ["App & voice control", "Auto-recharge & resume", "Anti-fall sensors", "Slim design fits under furniture"],
         False, False, False, True),
        ("Stainless Steel Lunch Box", "Insulated 3-compartment lunch box",
         "Three insulated compartments that keep hot food hot until lunch, with a "
         "leak-proof seal that survives the bottom of a bag.",
         1499, None, 45, 4.2,
         ["3 insulated compartments", "Leak-proof seal", "Stainless steel interior", "Carry handle included"],
         False, False, True, False),
    ],
    "Accessories": [
        ("Leather Analog Wrist Watch", "Classic leather strap watch",
         "A classic round face on a genuine leather strap — the kind of watch that "
         "works with a suit and a t-shirt equally well.",
         4999, 3999, 20, 4.5,
         ["Genuine leather strap", "Quartz movement", "Water-resistant to 30m", "Scratch-resistant glass"],
         True, False, False, True),
        ("Polarized Sunglasses", "UV400 protection unisex sunglasses",
         "Polarized lenses that actually cut glare off pavement and water, with "
         "UV400 protection you won't have to think about again.",
         1999, None, 38, 4.3,
         ["Polarized UV400 lenses", "Lightweight frame", "Unisex design", "Includes protective case"],
         False, True, True, False),
        ("Genuine Leather Wallet", "Slim bifold wallet with card slots",
         "A slim bifold that carries what you actually need — six card slots and a "
         "bill compartment, without the bulge.",
         1799, 1399, 30, 4.4,
         ["Genuine leather", "6 card slots + bill compartment", "Slim bifold design", "RFID blocking"],
         False, False, False, True),
        ("Canvas Travel Backpack", "35L water-resistant backpack",
         "35 liters of water-resistant carry with a padded laptop sleeve — built "
         "for a weekend trip or a daily commute.",
         3999, None, 18, 4.6,
         ["35L capacity", "Padded 15\" laptop sleeve", "Water-resistant canvas", "Multiple organizer pockets"],
         True, True, False, False),
        ("Minimalist Card Holder", "Slim aluminum card case",
         "An aluminum case that carries five cards flat in a shirt pocket, with a "
         "quick-eject slider for the one you need right now.",
         999, 799, 50, 4.1,
         ["Aluminum construction", "Holds up to 8 cards", "Quick-eject slider", "RFID blocking"],
         False, False, False, True),
    ],
    "Sports": [
        ("Yoga Mat Premium", "6mm non-slip exercise mat",
         "A 6mm cushion with a grip that holds through a sweaty flow, rolled up "
         "small enough to actually fit in your bag.",
         1999, 1599, 40, 4.5,
         ["6mm thickness", "Non-slip textured surface", "Includes carry strap", "Eco-friendly TPE material"],
         True, False, True, True),
        ("Adjustable Dumbbell Set", "5-25kg adjustable dumbbell pair",
         "One pair that replaces a rack of them — dial from 5 to 25kg per side "
         "without a wrench in sight.",
         12999, None, 7, 4.6,
         ["5-25kg adjustable per dumbbell", "Quick-lock dial system", "Space-saving design", "Sold as a pair"],
         False, False, False, False),
        ("Football Size 5", "Match-quality outdoor football",
         "A match-quality build with a textured panel grip that holds up to "
         "concrete pitches, not just manicured grass.",
         1499, 1199, 33, 4.3,
         ["Official size 5", "Textured panel grip", "Durable synthetic leather", "All-surface use"],
         False, True, True, True),
        ("Badminton Racket Set", "Pair of carbon-fiber rackets with shuttlecocks",
         "A pair of carbon-fiber rackets light enough for quick net play, "
         "shuttlecocks included so the game starts tonight.",
         2999, None, 20, 4.4,
         ["Carbon-fiber shaft", "Pair of rackets", "3 shuttlecocks included", "Comes with carry bag"],
         False, False, False, False),
        ("Resistance Bands Set", "5-piece resistance band set with handles",
         "Five resistance levels that cover a full home workout, with handles and "
         "a door anchor for the moves a mat alone can't do.",
         1299, 999, 45, 4.2,
         ["5 resistance levels", "Includes handles & door anchor", "Portable carry pouch", "Latex construction"],
         True, False, False, True),
        ("Cycling Helmet", "Ventilated adjustable safety helmet",
         "Deep vents that keep your head cool on a climb, with a dial-adjust fit "
         "that doesn't slip on the downhill.",
         2499, None, 15, 4.3,
         ["16 ventilation ports", "Dial-adjust fit system", "Lightweight EPS foam", "Reflective safety strip"],
         False, True, False, False),
    ],
}


class Command(BaseCommand):
    help = "Seed the database with demo categories and ~36 realistic DukaLink products (PKR pricing)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing products and categories before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["flush"]:
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared existing products and categories."))

        categories = {}
        for name, icon in CATEGORY_DEFS:
            category, _ = Category.objects.get_or_create(name=name, defaults={"icon": icon})
            categories[name] = category

        created_count = 0
        for category_name, product_rows in PRODUCTS.items():
            category = categories[category_name]
            for row in product_rows:
                (
                    name, short_desc, desc, price, discount_price, stock, rating,
                    features, is_featured, is_new_arrival, is_popular, is_on_sale,
                ) = row

                if Product.objects.filter(name=name).exists():
                    continue

                Product.objects.create(
                    name=name,
                    category=category,
                    short_description=short_desc,
                    description=desc,
                    price=price,
                    discount_price=discount_price,
                    stock=stock,
                    rating=rating,
                    features="\n".join(features),
                    image_url=product_image_url(name),
                    is_featured=is_featured,
                    is_new_arrival=is_new_arrival,
                    is_popular=is_popular,
                    is_on_sale=is_on_sale,
                )
                created_count += 1

        total = Product.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {created_count} new products ({total} total across {len(categories)} categories)."
            )
        )
