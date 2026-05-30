"""
`python manage.py seed_demo` — to'liq demo katalog (Uzum.uz uslubida).

8 kategoriya (tree), 12 brend, 45+ mahsulot (variant/attribute/review/rasm),
banner va kuponlar. Rasmlar picsum.photos'dan yuklab olinadi (graceful).

Idempotent — qayta ishga tushirsa duplicate yaratmaydi.
"""

from __future__ import annotations

import random
from decimal import Decimal
from io import BytesIO

import requests
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from apps.catalog.models import (
    Brand,
    Category,
    Product,
    ProductAttribute,
    ProductImage,
    ProductVariant,
)
from apps.promotions.models import Banner, Coupon
from apps.reviews.models import Review
from apps.reviews.services import recompute_product_rating
from apps.vendors.models import Vendor

User = get_user_model()
random.seed(42)

# =============================================================================
# Data definitions
# =============================================================================
CATEGORIES = [
    ("Elektronika", "smartphone", [
        ("Smartfonlar", "smartphone"),
        ("Noutbuklar", "laptop"),
        ("Audio", "headphones"),
    ]),
    ("Kiyim-kechak", "shirt", [
        ("Erkaklar", "shirt"),
        ("Ayollar", "venus"),
    ]),
    ("Uy-ro'zg'or", "house", []),
    ("Go'zallik", "sparkles", []),
    ("Sport", "dumbbell", []),
    ("Kitoblar", "book-open", []),
]

BRANDS = [
    "Apple", "Samsung", "Xiaomi", "Sony", "LG", "HP",
    "Dell", "Nike", "Adidas", "Zara", "Bosch", "Philips",
]

# (name, category_slug, brand, price_mln, sale_mln|None, colors, sizes, attrs)
PRODUCTS = [
    # Smartfonlar
    ("iPhone 15 Pro 256GB", "smartfonlar", "Apple", 15.9, 14.5, ["Titan", "Qora"], [], [("Ekran", "6.1\" OLED"), ("Xotira", "256GB"), ("Kamera", "48MP")]),
    ("iPhone 14 128GB", "smartfonlar", "Apple", 11.2, None, ["Qora", "Oq", "Ko'k"], [], [("Ekran", "6.1\" OLED"), ("Xotira", "128GB")]),
    ("Samsung Galaxy S24 Ultra", "smartfonlar", "Samsung", 16.5, 15.2, ["Qora", "Kulrang"], [], [("Ekran", "6.8\" AMOLED"), ("Xotira", "512GB"), ("S-Pen", "Bor")]),
    ("Samsung Galaxy A55", "smartfonlar", "Samsung", 5.4, 4.9, ["Ko'k", "Qora"], [], [("Ekran", "6.6\" AMOLED"), ("Xotira", "256GB")]),
    ("Xiaomi 14 Pro", "smartfonlar", "Xiaomi", 9.8, None, ["Qora", "Yashil"], [], [("Ekran", "6.73\" AMOLED"), ("Protsessor", "Snapdragon 8 Gen 3")]),
    ("Xiaomi Redmi Note 13", "smartfonlar", "Xiaomi", 3.2, 2.8, ["Qora", "Oq"], [], [("Ekran", "6.67\" AMOLED"), ("Batareya", "5000mAh")]),
    # Noutbuklar
    ("MacBook Air M3 13\"", "noutbuklar", "Apple", 18.5, None, ["Kulrang", "Oltin"], [], [("Protsessor", "Apple M3"), ("RAM", "16GB"), ("SSD", "512GB")]),
    ("MacBook Pro 14\" M3 Pro", "noutbuklar", "Apple", 28.9, 26.5, ["Qora", "Kumush"], [], [("Protsessor", "M3 Pro"), ("RAM", "18GB")]),
    ("Dell XPS 13", "noutbuklar", "Dell", 14.2, 12.9, ["Kumush"], [], [("Protsessor", "Intel i7"), ("RAM", "16GB")]),
    ("HP Pavilion 15", "noutbuklar", "HP", 7.8, None, ["Kumush", "Qora"], [], [("Protsessor", "Intel i5"), ("RAM", "8GB")]),
    # Audio
    ("Sony WH-1000XM5", "audio", "Sony", 4.2, 3.8, ["Qora", "Kumush"], [], [("Tip", "Over-ear"), ("ANC", "Bor"), ("Batareya", "30 soat")]),
    ("AirPods Pro 2", "audio", "Apple", 3.1, None, ["Oq"], [], [("Tip", "In-ear"), ("ANC", "Bor")]),
    ("JBL Flip 6", "audio", "Sony", 1.4, 1.1, ["Qora", "Ko'k", "Qizil"], [], [("Quvvat", "30W"), ("Suvga chidamli", "IP67")]),
    # Erkaklar
    ("Nike Air Max 270", "erkaklar", "Nike", 1.8, 1.5, ["Qora", "Oq"], ["40", "41", "42", "43", "44"], [("Material", "Tekstil"), ("Tip", "Krossovka")]),
    ("Adidas Ultraboost 22", "erkaklar", "Adidas", 2.1, None, ["Qora", "Kulrang"], ["41", "42", "43", "44"], [("Material", "Primeknit"), ("Tip", "Yugurish")]),
    ("Zara Klassik ko'ylak", "erkaklar", "Zara", 0.45, 0.32, ["Oq", "Ko'k", "Qora"], ["S", "M", "L", "XL"], [("Material", "Paxta"), ("Fason", "Slim")]),
    # Ayollar
    ("Zara Yozgi libos", "ayollar", "Zara", 0.58, 0.42, ["Qizil", "Yashil"], ["S", "M", "L"], [("Material", "Viskoza"), ("Mavsum", "Yoz")]),
    ("Nike Sport futbolka", "ayollar", "Nike", 0.38, None, ["Pushti", "Qora"], ["XS", "S", "M", "L"], [("Material", "Dri-FIT")]),
    # Uy-ro'zg'or
    ("Bosch Changyutgich Series 6", "uy-rozgor", "Bosch", 3.4, 2.9, ["Qizil"], [], [("Quvvat", "750W"), ("Tip", "Simsiz")]),
    ("Philips Dazmol Azur", "uy-rozgor", "Philips", 0.85, None, ["Ko'k"], [], [("Quvvat", "2400W"), ("Bug'", "50g/min")]),
    ("LG Mikroto'lqinli pech", "uy-rozgor", "LG", 1.9, 1.6, ["Oq", "Qora"], [], [("Hajm", "25L"), ("Quvvat", "1000W")]),
    # Go'zallik
    ("Atir Premium 50ml", "gozallik", "Zara", 0.42, None, [], [], [("Hajm", "50ml"), ("Tip", "EDP")]),
    ("Soch fenı Philips", "gozallik", "Philips", 0.65, 0.54, ["Pushti"], [], [("Quvvat", "2100W")]),
    # Sport
    ("Dumbbell to'plami 20kg", "sport", "Nike", 1.2, None, [], [], [("Og'irlik", "20kg"), ("Material", "Po'lat")]),
    ("Yoga gilam Pro", "sport", "Adidas", 0.35, 0.28, ["Binafsha", "Yashil"], [], [("Qalinlik", "6mm")]),
    # Kitoblar
    ("Atomic Habits (uz)", "kitoblar", "Zara", 0.085, None, [], [], [("Muallif", "James Clear"), ("Sahifa", "320")]),
    ("Boy ota, kambag'al ota", "kitoblar", "Zara", 0.072, 0.06, [], [], [("Muallif", "R. Kiyosaki"), ("Sahifa", "280")]),
]

REVIEW_TEXTS = [
    ("Ajoyib mahsulot!", "Sifati zo'r, tez yetkazib berishdi. Tavsiya qilaman."),
    ("Yaxshi", "Narxiga yarasha sifat. Mamnunman."),
    ("Zo'r", "Kutganimdan ham yaxshi chiqdi. Rahmat!"),
    ("Yomon emas", "Umuman olganda yaxshi, lekin qadoqlash yaxshiroq bo'lishi mumkin edi."),
    ("Mukammal", "Hammasi joyida, yana xarid qilaman."),
]

MLN = Decimal("1000000")


class Command(BaseCommand):
    help = "Seed full demo catalog (Uzum-style) with picsum images."

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-images",
            action="store_true",
            help="Skip picsum image download (faster).",
        )

    def handle(self, *args, **options):
        self.skip_images = options["no_images"]
        self.session = requests.Session()
        vendor = Vendor.objects.get_default()

        self.stdout.write("Seeding categories...")
        cat_map = self._seed_categories()

        self.stdout.write("Seeding brands...")
        brand_map = self._seed_brands()

        self.stdout.write("Seeding products...")
        self._seed_products(vendor, cat_map, brand_map)

        self.stdout.write("Seeding reviews...")
        self._seed_reviews()

        self.stdout.write("Seeding banners + coupons...")
        self._seed_banners()
        self._seed_coupons()

        # products_count denorm
        for cat in Category.objects.all():
            cat.products_count = Product.objects.filter(
                category=cat, is_active=True
            ).count()
            cat.save(update_fields=["products_count"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo seeded: {Product.objects.count()} products, "
                f"{Category.objects.count()} categories, "
                f"{Brand.objects.count()} brands, "
                f"{Review.objects.count()} reviews."
            )
        )

    # ------------------------------------------------------------------
    def _seed_categories(self) -> dict[str, Category]:
        cat_map: dict[str, Category] = {}
        order = 0
        for name, icon, subs in CATEGORIES:
            slug = slugify(name)
            parent, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "icon": icon, "order": order, "is_active": True},
            )
            cat_map[slug] = parent
            order += 1
            for sub_name, sub_icon in subs:
                sub_slug = slugify(sub_name)
                sub, _ = Category.objects.update_or_create(
                    slug=sub_slug,
                    defaults={
                        "name": sub_name,
                        "icon": sub_icon,
                        "parent": parent,
                        "is_active": True,
                    },
                )
                cat_map[sub_slug] = sub
        return cat_map

    def _seed_brands(self) -> dict[str, Brand]:
        brand_map: dict[str, Brand] = {}
        for name in BRANDS:
            slug = slugify(name)
            brand, _ = Brand.objects.update_or_create(
                slug=slug, defaults={"name": name, "is_active": True}
            )
            brand_map[name] = brand
        return brand_map

    def _seed_products(self, vendor, cat_map, brand_map) -> None:
        for idx, (
            name, cat_slug, brand_name, price, sale, colors, sizes, attrs,
        ) in enumerate(PRODUCTS):
            slug = slugify(name)
            category = cat_map.get(cat_slug)
            if category is None:
                continue
            brand = brand_map.get(brand_name)

            base_price = (Decimal(str(price)) * MLN).quantize(Decimal("1"))
            sale_price = (
                (Decimal(str(sale)) * MLN).quantize(Decimal("1"))
                if sale else None
            )

            product, created = Product.objects.update_or_create(
                slug=slug,
                defaults={
                    "vendor": vendor,
                    "category": category,
                    "brand": brand,
                    "name": name,
                    "sku": f"SKU-{idx + 1:05d}",
                    "short_description": f"{name} — original mahsulot, kafolat bilan.",
                    "description": (
                        f"{name} haqida batafsil. Yuqori sifatli, original "
                        f"mahsulot. Rasmiy kafolat va tez yetkazib berish. "
                        f"Bizning do'kondan xarid qiling va ishonchli xizmatdan "
                        f"bahramand bo'ling."
                    ),
                    "base_price": base_price,
                    "sale_price": sale_price,
                    "stock_quantity": random.randint(5, 80),
                    "is_active": True,
                    "is_featured": idx % 3 == 0,
                    "is_new": idx % 4 == 0,
                    "is_bestseller": idx % 5 == 0,
                },
            )
            product.is_in_stock = product.stock_quantity > 0
            product.save(update_fields=["is_in_stock"])

            # Attributes
            if created or not product.attributes.exists():
                product.attributes.all().delete()
                for o, (an, av) in enumerate(attrs):
                    ProductAttribute.objects.create(
                        product=product, name=an, value=av, order=o
                    )

            # Variants (color × size)
            if created or not product.variants.exists():
                product.variants.all().delete()
                self._make_variants(product, colors, sizes)

            # Images (picsum)
            if not product.images.exists():
                self._attach_images(product, slug, count=2)

    def _make_variants(self, product, colors, sizes) -> None:
        combos: list[tuple[str, str]] = []
        if colors and sizes:
            for c in colors:
                for s in sizes:
                    combos.append((c, s))
        elif colors:
            combos = [(c, "") for c in colors]
        elif sizes:
            combos = [("", s) for s in sizes]
        for i, (c, s) in enumerate(combos[:12]):
            ProductVariant.objects.create(
                product=product,
                sku=f"{product.sku}-V{i + 1}",
                color=c,
                size=s,
                additional_price=Decimal("0"),
                stock_quantity=random.randint(0, 20),
                is_active=True,
            )

    def _attach_images(self, product, slug, count=2) -> None:
        if self.skip_images:
            return
        for i in range(count):
            seed = f"{slug}-{i}"
            url = f"https://picsum.photos/seed/{seed}/800/800"
            try:
                resp = self.session.get(url, timeout=15)
                if resp.status_code == 200:
                    img = ProductImage(
                        product=product,
                        alt_text=product.name,
                        order=i,
                        is_primary=(i == 0),
                    )
                    img.image.save(
                        f"{seed}.jpg",
                        ContentFile(BytesIO(resp.content).read()),
                        save=True,
                    )
            except requests.RequestException:
                self.stdout.write(
                    self.style.WARNING(f"  image fail: {seed}")
                )

    def _seed_reviews(self) -> None:
        # Demo reviewer users
        reviewers = []
        for i in range(5):
            u, _ = User.objects.get_or_create(
                email=f"reviewer{i}@demo.uz",
                defaults={"full_name": f"Mijoz {i + 1}", "is_email_verified": True},
            )
            reviewers.append(u)

        for product in Product.objects.all():
            if product.reviews.exists():
                continue
            n = random.randint(0, 5)
            chosen = random.sample(reviewers, min(n, len(reviewers)))
            for u in chosen:
                title, content = random.choice(REVIEW_TEXTS)
                Review.objects.create(
                    product=product,
                    user=u,
                    rating=random.randint(3, 5),
                    title=title,
                    content=content,
                    is_verified_purchase=random.choice([True, False]),
                    status=Review.Status.APPROVED,
                )
            recompute_product_rating(product.id)

    def _seed_banners(self) -> None:
        banners = [
            ("Premium kolleksiya", "Eng yaxshi mahsulotlar bir joyda", "hero"),
            ("Chegirmalar mavsumi", "50% gacha tejang", "hero"),
        ]
        for o, (title, subtitle, pos) in enumerate(banners):
            b, created = Banner.objects.get_or_create(
                title=title,
                defaults={"subtitle": subtitle, "position": pos, "order": o, "is_active": True},
            )
            if created and not self.skip_images:
                try:
                    resp = self.session.get(
                        f"https://picsum.photos/seed/banner-{o}/1600/600", timeout=15
                    )
                    if resp.status_code == 200:
                        b.image.save(
                            f"banner-{o}.jpg",
                            ContentFile(resp.content),
                            save=True,
                        )
                except requests.RequestException:
                    pass

    def _seed_coupons(self) -> None:
        Coupon.objects.update_or_create(
            code="WELCOME10",
            defaults={
                "type": Coupon.Type.PERCENTAGE,
                "value": Decimal("10"),
                "min_order_amount": Decimal("100000"),
                "max_discount": Decimal("500000"),
                "is_active": True,
                "per_user_limit": 1,
            },
        )
        Coupon.objects.update_or_create(
            code="SUMMER20",
            defaults={
                "type": Coupon.Type.PERCENTAGE,
                "value": Decimal("20"),
                "min_order_amount": Decimal("500000"),
                "max_discount": Decimal("2000000"),
                "is_active": True,
                "valid_to": timezone.now() + timezone.timedelta(days=30),
                "per_user_limit": 3,
            },
        )
