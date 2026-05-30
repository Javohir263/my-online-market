"""
`python manage.py seed_demo` — to'liq demo katalog (Uzum.uz uslubida).

10 bo'lim (tree), 18 brend, ~70 mahsulot (o'zbekcha nomlar, variant/
attribute/review/rasm), banner va kuponlar. Rasmlar mahsulot turiga mos
ravishda loremflickr/picsum'dan yuklab olinadi (graceful).

  python manage.py seed_demo            # qo'shadi (idempotent)
  python manage.py seed_demo --fresh    # eski katalogni tozalab qayta
  python manage.py seed_demo --no-images
"""

from __future__ import annotations

import random
from decimal import Decimal

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
# Kategoriyalar (Uzum.uz uslubi) — (nom, lucide-icon, [(sub, icon, img_kw)])
# =============================================================================
CATEGORIES = [
    ("Elektronika", "smartphone", [
        ("Smartfonlar", "smartphone", "smartphone"),
        ("Noutbuklar", "laptop", "laptop"),
        ("Audio", "headphones", "headphones"),
        ("Televizorlar", "tv", "television"),
    ]),
    ("Kiyim-kechak", "shirt", [
        ("Erkaklar", "shirt", "menswear"),
        ("Ayollar", "venus", "dress"),
        ("Bolalar kiyimi", "baby", "kids-clothing"),
    ]),
    ("Oziq-ovqat", "apple", [
        ("Mevalar", "apple", "fruit"),
        ("Ichimliklar", "cup-soda", "drink"),
        ("Shirinliklar", "cookie", "sweets"),
    ]),
    ("Go'zallik", "sparkles", [
        ("Parfyumeriya", "spray-can", "perfume"),
        ("Kosmetika", "palette", "cosmetics"),
    ]),
    ("Uy va bog'", "house", [
        ("Oshxona", "cooking-pot", "kitchen"),
        ("Tekstil", "bed", "home-textile"),
    ]),
    ("Bolalar", "baby", [
        ("O'yinchoqlar", "blocks", "toys"),
    ]),
    ("Sport", "dumbbell", []),
    ("Kitoblar", "book-open", []),
    ("Avtotovarlar", "car", []),
    ("Hayvonlar uchun", "paw-print", []),
]

BRANDS = [
    "Apple", "Samsung", "Xiaomi", "Sony", "LG", "HP", "Dell",
    "Nike", "Adidas", "Zara", "Bosch", "Philips",
    "Nestle", "Coca-Cola", "Lego", "Loreal", "Artel", "Mevasevar",
]

# (name, category_slug, brand, price_uzs, sale|None, colors, sizes, attrs, img_kw)
PRODUCTS = [
    # --- Smartfonlar ---
    ("iPhone 15 Pro 256GB", "smartfonlar", "Apple", 15_900_000, 14_500_000, ["Titan", "Qora"], [], [("Ekran", "6.1\" OLED"), ("Xotira", "256GB")], "iphone"),
    ("Samsung Galaxy S24 Ultra", "smartfonlar", "Samsung", 16_500_000, 15_200_000, ["Qora", "Kulrang"], [], [("Ekran", "6.8\" AMOLED"), ("S-Pen", "Bor")], "samsung-phone"),
    ("Xiaomi Redmi Note 13", "smartfonlar", "Xiaomi", 3_200_000, 2_800_000, ["Qora", "Oq"], [], [("Batareya", "5000mAh")], "xiaomi-phone"),
    ("iPhone 14 128GB", "smartfonlar", "Apple", 11_200_000, None, ["Qora", "Ko'k"], [], [("Xotira", "128GB")], "iphone-14"),
    ("Samsung Galaxy A55", "smartfonlar", "Samsung", 5_400_000, 4_900_000, ["Ko'k"], [], [("Xotira", "256GB")], "phone"),
    # --- Noutbuklar ---
    ("MacBook Air M3 13\"", "noutbuklar", "Apple", 18_500_000, None, ["Kulrang", "Oltin"], [], [("Protsessor", "Apple M3"), ("RAM", "16GB")], "macbook"),
    ("Dell XPS 13", "noutbuklar", "Dell", 14_200_000, 12_900_000, ["Kumush"], [], [("Protsessor", "Intel i7")], "laptop-dell"),
    ("HP Pavilion 15", "noutbuklar", "HP", 7_800_000, None, ["Kumush"], [], [("RAM", "8GB")], "laptop-hp"),
    # --- Audio ---
    ("Sony WH-1000XM5", "audio", "Sony", 4_200_000, 3_800_000, ["Qora"], [], [("ANC", "Bor"), ("Batareya", "30 soat")], "headphones"),
    ("AirPods Pro 2", "audio", "Apple", 3_100_000, None, ["Oq"], [], [("ANC", "Bor")], "earbuds"),
    ("JBL Flip 6", "audio", "Sony", 1_400_000, 1_100_000, ["Qora", "Ko'k"], [], [("Suvga chidamli", "IP67")], "speaker"),
    # --- Televizorlar ---
    ("Samsung 55\" QLED 4K", "televizorlar", "Samsung", 9_500_000, 8_700_000, [], [], [("Diagonal", "55\""), ("4K", "Bor")], "tv"),
    ("LG OLED 65\"", "televizorlar", "LG", 14_900_000, None, [], [], [("Diagonal", "65\""), ("OLED", "Bor")], "led-tv"),
    ("Artel 43\" Smart TV", "televizorlar", "Artel", 3_400_000, 2_990_000, [], [], [("Diagonal", "43\"")], "smart-tv"),
    # --- Erkaklar kiyimi ---
    ("Nike Air Max 270", "erkaklar", "Nike", 1_800_000, 1_500_000, ["Qora", "Oq"], ["40", "41", "42", "43", "44"], [("Tip", "Krossovka")], "sneakers"),
    ("Adidas Ultraboost 22", "erkaklar", "Adidas", 2_100_000, None, ["Qora", "Kulrang"], ["41", "42", "43"], [("Tip", "Yugurish")], "running-shoes"),
    ("Zara Klassik ko'ylak", "erkaklar", "Zara", 450_000, 320_000, ["Oq", "Ko'k"], ["S", "M", "L", "XL"], [("Material", "Paxta")], "shirt"),
    ("Erkaklar kurtka", "erkaklar", "Zara", 890_000, None, ["Qora", "Jigarrang"], ["M", "L", "XL"], [("Mavsum", "Qish")], "jacket"),
    # --- Ayollar kiyimi ---
    ("Zara Yozgi libos", "ayollar", "Zara", 580_000, 420_000, ["Qizil", "Yashil"], ["S", "M", "L"], [("Material", "Viskoza")], "dress"),
    ("Nike Sport futbolka", "ayollar", "Nike", 380_000, None, ["Pushti", "Qora"], ["XS", "S", "M"], [("Material", "Dri-FIT")], "tshirt"),
    ("Ayollar sumkasi", "ayollar", "Zara", 720_000, 599_000, ["Qora", "Bej"], [], [("Material", "Eko-charm")], "handbag"),
    # --- Bolalar kiyimi ---
    ("Bolalar krossovkasi", "bolalar-kiyimi", "Adidas", 520_000, 450_000, ["Ko'k", "Pushti"], ["28", "30", "32", "34"], [("Yosh", "3-7")], "kids-shoes"),
    ("Bolalar futbolkasi", "bolalar-kiyimi", "Nike", 180_000, None, ["Sariq", "Yashil"], ["2-3", "4-5", "6-7"], [("Material", "Paxta")], "kids-shirt"),
    # --- Mevalar ---
    ("Olma (Simirenko) 1kg", "mevalar", "Mevasevar", 18_000, 15_000, [], [], [("Kelib chiqishi", "O'zbekiston"), ("Vazn", "1kg")], "apple-fruit"),
    ("Banan 1kg", "mevalar", "Mevasevar", 22_000, None, [], [], [("Kelib chiqishi", "Ekvador")], "banana"),
    ("Apelsin 1kg", "mevalar", "Mevasevar", 25_000, 21_000, [], [], [("Kelib chiqishi", "Misr")], "orange-fruit"),
    ("Uzum (Husayni) 1kg", "mevalar", "Mevasevar", 32_000, None, [], [], [("Kelib chiqishi", "Samarqand")], "grapes"),
    ("Anor 1kg", "mevalar", "Mevasevar", 28_000, 24_000, [], [], [("Kelib chiqishi", "O'zbekiston")], "pomegranate"),
    # --- Ichimliklar ---
    ("Coca-Cola 1.5L", "ichimliklar", "Coca-Cola", 14_000, None, [], [], [("Hajm", "1.5L")], "cola"),
    ("Tabiiy suv 5L", "ichimliklar", "Nestle", 9_000, 7_500, [], [], [("Hajm", "5L")], "water-bottle"),
    ("Apelsin sharbati 1L", "ichimliklar", "Nestle", 18_000, None, [], [], [("Hajm", "1L")], "juice"),
    # --- Shirinliklar ---
    ("Shokolad assorti 400g", "shirinliklar", "Nestle", 65_000, 55_000, [], [], [("Vazn", "400g")], "chocolate"),
    ("Pechenye 300g", "shirinliklar", "Nestle", 22_000, None, [], [], [("Vazn", "300g")], "cookies"),
    # --- Parfyumeriya ---
    ("Atir Premium 50ml", "parfyumeriya", "Loreal", 420_000, None, [], [], [("Hajm", "50ml"), ("Tip", "EDP")], "perfume"),
    ("Erkaklar atiri 100ml", "parfyumeriya", "Loreal", 540_000, 460_000, [], [], [("Hajm", "100ml")], "cologne"),
    # --- Kosmetika ---
    ("Yuz kremi", "kosmetika", "Loreal", 145_000, 120_000, [], [], [("Hajm", "50ml")], "cream-cosmetic"),
    ("Lab bo'yog'i to'plami", "kosmetika", "Loreal", 230_000, None, ["Qizil", "Pushti"], [], [("Soni", "3 dona")], "lipstick"),
    # --- Oshxona ---
    ("Bosch Changyutgich", "oshxona", "Bosch", 3_400_000, 2_900_000, ["Qizil"], [], [("Quvvat", "750W")], "vacuum"),
    ("Philips Dazmol", "oshxona", "Philips", 850_000, None, ["Ko'k"], [], [("Quvvat", "2400W")], "iron-appliance"),
    ("Choynak elektr", "oshxona", "Artel", 320_000, 270_000, ["Oq", "Qora"], [], [("Hajm", "1.7L")], "kettle"),
    ("Tovoq to'plami 12 dona", "oshxona", "Artel", 480_000, None, [], [], [("Material", "Chinni")], "dishes"),
    # --- Tekstil ---
    ("Ko'rpa-to'shak to'plami", "tekstil", "Artel", 650_000, 540_000, ["Oq", "Bej"], [], [("O'lcham", "2 kishilik")], "bedding"),
    ("Sochiq to'plami", "tekstil", "Artel", 180_000, None, ["Ko'k", "Yashil"], [], [("Soni", "4 dona")], "towels"),
    # --- O'yinchoqlar ---
    ("Lego Classic 500", "oyinchoqlar", "Lego", 420_000, 360_000, [], [], [("Bo'laklar", "500")], "lego"),
    ("Masofadan boshqariladigan mashina", "oyinchoqlar", "Lego", 280_000, None, ["Qizil", "Ko'k"], [], [("Yosh", "6+")], "toy-car"),
    ("Yumshoq o'yinchoq ayiq", "oyinchoqlar", "Lego", 150_000, 120_000, ["Jigarrang"], [], [("Balandlik", "40sm")], "teddy-bear"),
    # --- Sport ---
    ("Dumbbell to'plami 20kg", "sport", "Nike", 1_200_000, None, [], [], [("Og'irlik", "20kg")], "dumbbell"),
    ("Yoga gilam Pro", "sport", "Adidas", 350_000, 280_000, ["Binafsha", "Yashil"], [], [("Qalinlik", "6mm")], "yoga-mat"),
    ("Velosiped Mountain", "sport", "Artel", 3_200_000, 2_800_000, ["Qora", "Qizil"], [], [("G'ildirak", "26\"")], "bicycle"),
    # --- Kitoblar ---
    ("Atomic Habits (uz)", "kitoblar", "Mevasevar", 85_000, None, [], [], [("Muallif", "James Clear")], "book"),
    ("Boy ota, kambag'al ota", "kitoblar", "Mevasevar", 72_000, 60_000, [], [], [("Muallif", "R. Kiyosaki")], "books"),
    ("O'tkan kunlar — A.Qodiriy", "kitoblar", "Mevasevar", 65_000, None, [], [], [("Til", "O'zbek")], "old-book"),
    # --- Avtotovarlar ---
    ("Motor moyi 4L", "avtotovarlar", "Bosch", 280_000, 240_000, [], [], [("Hajm", "4L")], "motor-oil"),
    ("Avtomobil shinasi R16", "avtotovarlar", "Bosch", 750_000, None, [], [], [("O'lcham", "R16")], "car-tire"),
    # --- Hayvonlar uchun ---
    ("It uchun ozuqa 3kg", "hayvonlar-uchun", "Nestle", 145_000, 120_000, [], [], [("Vazn", "3kg")], "dog-food"),
    ("Mushuk o'yinchog'i", "hayvonlar-uchun", "Nestle", 45_000, None, [], [], [("Tur", "Sichqon")], "cat-toy"),
]

REVIEW_TEXTS = [
    ("Ajoyib mahsulot!", "Sifati zo'r, tez yetkazib berishdi. Tavsiya qilaman."),
    ("Yaxshi", "Narxiga yarasha sifat. Mamnunman."),
    ("Zo'r", "Kutganimdan ham yaxshi chiqdi. Rahmat!"),
    ("Yomon emas", "Umuman yaxshi, qadoqlash yaxshiroq bo'lsa edi."),
    ("Mukammal", "Hammasi joyida, yana xarid qilaman."),
    ("Tavsiya qilaman", "Oilam uchun oldim, hammaga yoqdi."),
]


class Command(BaseCommand):
    help = "Seed full demo catalog (Uzum-style) with images."

    def add_arguments(self, parser):
        parser.add_argument("--no-images", action="store_true")
        parser.add_argument(
            "--fresh",
            action="store_true",
            help="Eski katalogni (Product/Category/Brand) tozalab qayta seed.",
        )

    def handle(self, *args, **options):
        self.skip_images = options["no_images"]
        self.session = requests.Session()

        if options["fresh"]:
            self.stdout.write("Eski katalog tozalanmoqda...")
            Review.objects.all().delete()
            ProductImage.objects.all().delete()
            ProductVariant.objects.all().delete()
            ProductAttribute.objects.all().delete()
            Product.objects.all().delete()
            # Category.parent PROTECT — leaf'dan boshlab o'chiramiz
            for _ in range(6):
                if not Category.objects.exists():
                    break
                Category.objects.filter(children__isnull=True).delete()

        vendor = Vendor.objects.get_default()

        self.stdout.write("Kategoriyalar...")
        cat_map = self._seed_categories()
        self.stdout.write("Brendlar...")
        brand_map = self._seed_brands()
        self.stdout.write(f"Mahsulotlar ({len(PRODUCTS)} ta)...")
        self._seed_products(vendor, cat_map, brand_map)
        self.stdout.write("Sharhlar...")
        self._seed_reviews()
        self.stdout.write("Banner + kuponlar...")
        self._seed_banners()
        self._seed_coupons()

        for cat in Category.objects.all():
            cat.products_count = Product.objects.filter(
                category=cat, is_active=True
            ).count()
            cat.save(update_fields=["products_count"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Tayyor: {Product.objects.count()} mahsulot, "
                f"{Category.objects.count()} kategoriya, "
                f"{Brand.objects.count()} brend, "
                f"{Review.objects.count()} sharh."
            )
        )

    # ------------------------------------------------------------------
    def _seed_categories(self) -> dict[str, Category]:
        cat_map: dict[str, Category] = {}
        for order, (name, icon, subs) in enumerate(CATEGORIES):
            slug = slugify(name)
            parent, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "icon": icon, "order": order, "is_active": True},
            )
            cat_map[slug] = parent
            for sname, sicon, _kw in subs:
                sslug = slugify(sname)
                sub, _ = Category.objects.update_or_create(
                    slug=sslug,
                    defaults={"name": sname, "icon": sicon, "parent": parent, "is_active": True},
                )
                cat_map[sslug] = sub
        return cat_map

    def _seed_brands(self) -> dict[str, Brand]:
        m: dict[str, Brand] = {}
        for name in BRANDS:
            b, _ = Brand.objects.update_or_create(
                slug=slugify(name), defaults={"name": name, "is_active": True}
            )
            m[name] = b
        return m

    def _seed_products(self, vendor, cat_map, brand_map) -> None:
        for idx, (
            name, cat_slug, brand_name, price, sale, colors, sizes, attrs, img_kw,
        ) in enumerate(PRODUCTS):
            category = cat_map.get(cat_slug)
            if category is None:
                continue
            slug = slugify(name) or f"product-{idx}"
            product, created = Product.objects.update_or_create(
                slug=slug,
                defaults={
                    "vendor": vendor,
                    "category": category,
                    "brand": brand_map.get(brand_name),
                    "name": name,
                    "sku": f"SKU-{idx + 1:05d}",
                    "short_description": f"{name} — original, kafolat bilan. Tez yetkazib berish.",
                    "description": (
                        f"{name} — yuqori sifatli original mahsulot. Rasmiy "
                        f"kafolat, tez yetkazib berish va ishonchli xizmat. "
                        f"My Online Market'da xarid qiling."
                    ),
                    "base_price": Decimal(price),
                    "sale_price": Decimal(sale) if sale else None,
                    "stock_quantity": random.randint(8, 120),
                    "is_active": True,
                    "is_featured": idx % 3 == 0,
                    "is_new": idx % 4 == 0,
                    "is_bestseller": idx % 5 == 0,
                },
            )
            product.is_in_stock = product.stock_quantity > 0
            product.save(update_fields=["is_in_stock"])

            if not product.attributes.exists():
                for o, (an, av) in enumerate(attrs):
                    ProductAttribute.objects.create(product=product, name=an, value=av, order=o)

            if not product.variants.exists():
                self._make_variants(product, colors, sizes)

            if not product.images.exists():
                self._attach_images(product, slug, img_kw, count=2)

    def _make_variants(self, product, colors, sizes) -> None:
        combos: list[tuple[str, str]] = []
        if colors and sizes:
            combos = [(c, s) for c in colors for s in sizes]
        elif colors:
            combos = [(c, "") for c in colors]
        elif sizes:
            combos = [("", s) for s in sizes]
        for i, (c, s) in enumerate(combos[:15]):
            ProductVariant.objects.create(
                product=product, sku=f"{product.sku}-V{i + 1}",
                color=c, size=s, additional_price=Decimal("0"),
                stock_quantity=random.randint(0, 25), is_active=True,
            )

    def _attach_images(self, product, slug, img_kw, count=2) -> None:
        if self.skip_images:
            return
        for i in range(count):
            # loremflickr — mavzuga mos rasm; fallback picsum
            urls = [
                f"https://loremflickr.com/700/700/{img_kw}?lock={abs(hash(slug)) % 1000 + i}",
                f"https://picsum.photos/seed/{slug}-{i}/700/700",
            ]
            for url in urls:
                try:
                    resp = self.session.get(url, timeout=15)
                    if resp.status_code == 200 and len(resp.content) > 1000:
                        img = ProductImage(
                            product=product, alt_text=product.name,
                            order=i, is_primary=(i == 0),
                        )
                        img.image.save(f"{slug}-{i}.jpg", ContentFile(resp.content), save=True)
                        break
                except requests.RequestException:
                    continue

    def _seed_reviews(self) -> None:
        reviewers = []
        for i in range(6):
            u, _ = User.objects.get_or_create(
                email=f"mijoz{i}@demo.uz",
                defaults={"full_name": f"Mijoz {i + 1}", "is_email_verified": True},
            )
            reviewers.append(u)
        for product in Product.objects.all():
            if product.reviews.exists():
                continue
            for u in random.sample(reviewers, random.randint(0, 5)):
                title, content = random.choice(REVIEW_TEXTS)
                Review.objects.create(
                    product=product, user=u, rating=random.randint(3, 5),
                    title=title, content=content,
                    is_verified_purchase=random.choice([True, False]),
                    status=Review.Status.APPROVED,
                )
            recompute_product_rating(product.id)

    def _seed_banners(self) -> None:
        for o, (title, subtitle) in enumerate([
            ("Premium kolleksiya", "Eng yaxshi mahsulotlar bir joyda"),
            ("Chegirmalar mavsumi", "50% gacha tejang"),
        ]):
            b, created = Banner.objects.get_or_create(
                title=title,
                defaults={"subtitle": subtitle, "position": "hero", "order": o, "is_active": True},
            )
            if created and not self.skip_images:
                try:
                    r = self.session.get(f"https://picsum.photos/seed/banner-{o}/1600/600", timeout=15)
                    if r.status_code == 200:
                        b.image.save(f"banner-{o}.jpg", ContentFile(r.content), save=True)
                except requests.RequestException:
                    pass

    def _seed_coupons(self) -> None:
        Coupon.objects.update_or_create(
            code="WELCOME10",
            defaults={"type": Coupon.Type.PERCENTAGE, "value": Decimal("10"),
                      "min_order_amount": Decimal("100000"), "max_discount": Decimal("500000"),
                      "is_active": True, "per_user_limit": 1},
        )
        Coupon.objects.update_or_create(
            code="SUMMER20",
            defaults={"type": Coupon.Type.PERCENTAGE, "value": Decimal("20"),
                      "min_order_amount": Decimal("500000"), "max_discount": Decimal("2000000"),
                      "is_active": True, "valid_to": timezone.now() + timezone.timedelta(days=30),
                      "per_user_limit": 3},
        )
