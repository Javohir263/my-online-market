"""
`python manage.py seed_demo` — to'liq demo katalog (Uzum.uz uslubida).

✅ 10 root + 15 sub kategoriya (uz/ru/en tarjima bilan)
✅ 18 brend
✅ ~543 ta noyob mahsulot (`_products_data.py` da)
✅ Banner + kupon + demo akkaunt
✅ Rasm strategiyasi (priority tartib):
   1. Unsplash API (`--unsplash-key` yoki `UNSPLASH_ACCESS_KEY` env) — studio darajasi
   2. loremflickr — Flickr foydalanuvchi fotolari (default)
   3. picsum — universal chiroyli
   4. media/products/ pool'i — offline fallback

Foydalanish:
  python manage.py seed_demo --fresh
  python manage.py seed_demo --fresh --unsplash-key=YOUR_KEY  # eng yaxshi sifat
  python manage.py seed_demo --no-images                       # rasmsiz, tez
  python manage.py seed_demo --no-fetch                        # offline (pool)
"""

from __future__ import annotations

import json
import os
import random
from decimal import Decimal
from pathlib import Path

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
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
# Kategoriyalar — (slug bo'lib yagona uz nomidan slugify orqali olinadi)
# (uz, ru, en, icon, [(sub_uz, sub_ru, sub_en, icon, img_kw)])
# =============================================================================
CATEGORIES = [
    ("Elektronika", "Электроника", "Electronics", "smartphone", [
        ("Smartfonlar", "Смартфоны", "Smartphones", "smartphone", "smartphone"),
        ("Noutbuklar", "Ноутбуки", "Laptops", "laptop", "laptop"),
        ("Audio", "Аудио", "Audio", "headphones", "headphones"),
        ("Televizorlar", "Телевизоры", "TVs", "tv", "television"),
    ]),
    ("Kiyim-kechak", "Одежда", "Clothing", "shirt", [
        ("Erkaklar", "Мужская", "Men", "shirt", "menswear"),
        ("Ayollar", "Женская", "Women", "venus", "dress"),
        ("Bolalar kiyimi", "Детская одежда", "Kids' clothing", "baby", "kids-clothing"),
    ]),
    ("Oziq-ovqat", "Продукты", "Groceries", "apple", [
        ("Mevalar", "Фрукты", "Fruits", "apple", "fruit"),
        ("Ichimliklar", "Напитки", "Drinks", "cup-soda", "drink"),
        ("Shirinliklar", "Сладости", "Sweets", "cookie", "sweets"),
    ]),
    ("Go'zallik", "Красота", "Beauty", "sparkles", [
        ("Parfyumeriya", "Парфюмерия", "Perfumery", "spray-can", "perfume"),
        ("Kosmetika", "Косметика", "Cosmetics", "palette", "cosmetics"),
    ]),
    ("Uy va bog'", "Дом и сад", "Home & Garden", "house", [
        ("Oshxona", "Кухня", "Kitchen", "cooking-pot", "kitchen"),
        ("Tekstil", "Текстиль", "Textile", "bed", "home-textile"),
    ]),
    ("Bolalar", "Детям", "Kids", "baby", [
        ("O'yinchoqlar", "Игрушки", "Toys", "blocks", "toys"),
    ]),
    ("Sport", "Спорт", "Sports", "dumbbell", []),
    ("Kitoblar", "Книги", "Books", "book-open", []),
    ("Avtotovarlar", "Автотовары", "Auto", "car", []),
    ("Hayvonlar uchun", "Для животных", "Pet supplies", "paw-print", []),
]

BRANDS = [
    "Apple", "Samsung", "Xiaomi", "Sony", "LG", "HP", "Dell",
    "Nike", "Adidas", "Zara", "Bosch", "Philips",
    "Nestle", "Coca-Cola", "Lego", "Loreal", "Artel", "Mevasevar",
]

# =============================================================================
# Mahsulot shablonlari — alohida faylda (~500 ta noyob mahsulot, uz/ru/en).
# =============================================================================
from ._products_data import PRODUCT_SEEDS  # noqa: E402

REVIEW_TEXTS = [
    ("Ajoyib mahsulot!", "Sifati zo'r, tez yetkazib berishdi. Tavsiya qilaman."),
    ("Yaxshi", "Narxiga yarasha sifat. Mamnunman."),
    ("Zo'r", "Kutganimdan ham yaxshi chiqdi. Rahmat!"),
    ("Yomon emas", "Umuman yaxshi, qadoqlash yaxshiroq bo'lsa edi."),
    ("Mukammal", "Hammasi joyida, yana xarid qilaman."),
    ("Tavsiya qilaman", "Oilam uchun oldim, hammaga yoqdi."),
]

DESC_TEMPLATES = {
    "uz": (
        "{name} — yuqori sifatli, original mahsulot. Rasmiy kafolat, tez "
        "yetkazib berish va ishonchli xizmat. My Online Market'da xarid qiling."
    ),
    "ru": (
        "{name} — высококачественный оригинальный товар. Официальная "
        "гарантия, быстрая доставка и надежный сервис. Покупайте на My Online Market."
    ),
    "en": (
        "{name} — premium quality original product. Official warranty, fast "
        "delivery and reliable service. Shop on My Online Market."
    ),
}
SHORT_DESC = {
    "uz": "Original, kafolat bilan. Tez yetkazib berish.",
    "ru": "Оригинал, с гарантией. Быстрая доставка.",
    "en": "Original, with warranty. Fast delivery.",
}


class Command(BaseCommand):
    help = "Seed full demo catalog (uz/ru/en) with ~50 products per root category."

    def add_arguments(self, parser):
        parser.add_argument("--no-images", action="store_true",
                            help="Mahsulotlarga rasm biriktirmaslik (eng tez).")
        parser.add_argument("--no-fetch", action="store_true",
                            help="Internet'dan rasm yuklab olmasdan, mavjud "
                                 "media/products/ pool'idan tasodifiy biriktirish (tez, offline).")
        parser.add_argument("--fresh", action="store_true",
                            help="Eski katalogni tozalab qayta seed.")
        parser.add_argument("--unsplash-key",
                            default=os.environ.get("UNSPLASH_ACCESS_KEY"),
                            help="Unsplash Access Key. Berilsa, professional "
                                 "darajadagi real foto yuklab olamiz (loremflickr "
                                 "o'rniga). Demo tarif: 50 req/soat, lekin per-keyword "
                                 "kesh tufayli ~50-80 ta unique keyword yetadi.")

    def handle(self, *args, **options):
        self.no_images = options["no_images"]
        self.no_fetch = options["no_fetch"]
        self.unsplash_key = options.get("unsplash_key")
        self.unsplash_disabled = False  # rate-limit'da True bo'ladi
        self.session = requests.Session()

        # Disk cache: keyword → [photo_urls]. Bir necha run orasida saqlanadi
        # va har soatlik 50-limit'ni samarali ishlatish imkonini beradi.
        self.unsplash_cache_file = Path(settings.MEDIA_ROOT) / ".unsplash_cache.json"
        self.unsplash_cache: dict[str, list[str]] = self._load_unsplash_cache()
        if self.unsplash_cache:
            self.stdout.write(
                f"  [unsplash] disk cache: {len(self.unsplash_cache)} ta keyword yuklandi"
            )

        if options["fresh"]:
            self.stdout.write("Eski katalog tozalanmoqda...")
            Review.objects.all().delete()
            ProductImage.objects.all().delete()
            ProductVariant.objects.all().delete()
            ProductAttribute.objects.all().delete()
            Product.objects.all().delete()
            for _ in range(6):
                if not Category.objects.exists():
                    break
                Category.objects.filter(children__isnull=True).delete()

        vendor = Vendor.objects.get_default()

        self.stdout.write("Kategoriyalar (uz/ru/en)...")
        cat_map = self._seed_categories()
        self.stdout.write(f"Brendlar ({len(BRANDS)})...")
        brand_map = self._seed_brands()

        # Mavjud media/products/ ichidagi rasmlardan pool tuzamiz
        self.image_pool = self._scan_image_pool()
        if self.image_pool:
            self.stdout.write(
                f"Rasm pool: {len(self.image_pool)} ta fayl topildi "
                "(internet'siz tez seed)."
            )

        self.stdout.write("Mahsulotlar (~110 noyob, internet'dan rasm yuklash 3-5 daq)...")
        self._seed_products(vendor, cat_map, brand_map)

        self.stdout.write("Sharhlar...")
        self._seed_reviews()
        self.stdout.write("Banner + kuponlar...")
        self._seed_banners()
        self._seed_coupons()
        self._seed_demo_user()

        # Unsplash disk cache'ni saqlaymiz (keyingi run'lar uchun)
        self._save_unsplash_cache()

        self.stdout.write("products_count (denorm) qayta hisoblanmoqda...")
        for cat in Category.objects.all():
            cat.products_count = Product.objects.filter(
                category_id__in=cat.get_descendant_ids(), is_active=True
            ).count()
            cat.save(update_fields=["products_count"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Tayyor: {Product.objects.count()} mahsulot, "
                f"{Category.objects.count()} kategoriya, "
                f"{Brand.objects.count()} brend, "
                f"{Review.objects.count()} sharh, "
                f"{ProductImage.objects.count()} rasm."
            )
        )

    # ----------------------------------------------------------------------
    def _seed_categories(self) -> dict[str, Category]:
        cat_map: dict[str, Category] = {}
        for order, (uz, ru, en, icon, subs) in enumerate(CATEGORIES):
            slug = slugify(uz)
            parent, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": uz, "name_uz": uz, "name_ru": ru, "name_en": en,
                    "icon": icon, "order": order, "is_active": True,
                },
            )
            cat_map[slug] = parent
            for sub_order, (suz, sru, sen, sicon, _kw) in enumerate(subs):
                sslug = slugify(suz)
                sub, _ = Category.objects.update_or_create(
                    slug=sslug,
                    defaults={
                        "name": suz, "name_uz": suz, "name_ru": sru, "name_en": sen,
                        "icon": sicon, "parent": parent, "order": sub_order,
                        "is_active": True,
                    },
                )
                cat_map[sslug] = sub
        return cat_map

    def _seed_brands(self) -> dict[str, Brand]:
        m: dict[str, Brand] = {}
        for name in BRANDS:
            b, _ = Brand.objects.update_or_create(
                slug=slugify(name),
                defaults={
                    "name": name, "name_uz": name, "name_ru": name, "name_en": name,
                    "is_active": True,
                },
            )
            m[name] = b
        return m

    def _scan_image_pool(self) -> list[Path]:
        """Return list of existing media/products/*.jpg files."""
        media_root = Path(settings.MEDIA_ROOT)
        products_dir = media_root / "products"
        if not products_dir.exists():
            return []
        return sorted(p for p in products_dir.iterdir()
                      if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"})

    # ----------------------------------------------------------------------
    def _seed_products(self, vendor, cat_map, brand_map) -> None:
        """Har PRODUCT_SEEDS yozuvi → AYNAN bitta noyob mahsulot. Takror yo'q."""
        global_idx = 0
        for leaf_slug, templates in PRODUCT_SEEDS.items():
            category = cat_map.get(leaf_slug)
            if category is None:
                continue
            for (name_uz, name_ru, name_en, base_price, img_kw) in templates:
                global_idx += 1
                slug = slugify(name_uz) or f"product-{global_idx}"

                # Har 3-mahsulotda chegirma — varying realistic
                sale = None
                if global_idx % 3 == 0:
                    sale = int(base_price * random.uniform(0.75, 0.95))

                brand = random.choice(list(brand_map.values()))

                product, _ = Product.objects.update_or_create(
                    slug=slug,
                    defaults={
                        "vendor": vendor,
                        "category": category,
                        "brand": brand,
                        "name": name_uz,
                        "name_uz": name_uz,
                        "name_ru": name_ru,
                        "name_en": name_en,
                        "short_description": SHORT_DESC["uz"],
                        "short_description_uz": SHORT_DESC["uz"],
                        "short_description_ru": SHORT_DESC["ru"],
                        "short_description_en": SHORT_DESC["en"],
                        "description": DESC_TEMPLATES["uz"].format(name=name_uz),
                        "description_uz": DESC_TEMPLATES["uz"].format(name=name_uz),
                        "description_ru": DESC_TEMPLATES["ru"].format(name=name_ru),
                        "description_en": DESC_TEMPLATES["en"].format(name=name_en),
                        "sku": f"SKU-{global_idx:05d}",
                        "base_price": Decimal(base_price),
                        "sale_price": Decimal(sale) if sale else None,
                        "stock_quantity": random.randint(8, 120),
                        "is_active": True,
                        "is_featured": global_idx % 5 == 0,
                        "is_new": global_idx % 4 == 0,
                        "is_bestseller": global_idx % 6 == 0,
                    },
                )
                product.is_in_stock = product.stock_quantity > 0
                product.save(update_fields=["is_in_stock"])

                if not product.attributes.exists():
                    ProductAttribute.objects.create(
                        product=product, name="Brend", value=brand.name, order=0,
                        name_uz="Brend", name_ru="Бренд", name_en="Brand",
                        value_uz=brand.name, value_ru=brand.name, value_en=brand.name,
                    )

                if not product.images.exists():
                    self._attach_images(product, slug, img_kw)
                    if global_idx % 10 == 0:
                        self.stdout.write(f"  ...{global_idx} mahsulot tayyor")

    def _attach_images(self, product, slug: str, img_kw: str, count: int = 1) -> None:
        """Mahsulotga rasm biriktirish. Strategiya (tartib bo'yicha):

        1) `--no-images`:  hech narsa.
        2) `--no-fetch`:   media/products/ pool'idan (offline, tasodifiy).
        3) Unsplash:       agar `--unsplash-key` berilgan bo'lsa, birinchi navbatda
                           Unsplash'dan kalit so'zga mos professional foto.
        4) loremflickr:    fallback (Flickr foydalanuvchi fotolari).
        5) picsum:         oxirgi chora (chiroyli, lekin kalit so'zga mos emas).
        6) Pool:           hech qaysi internet manbai ishlamasa.
        """
        if self.no_images:
            return

        if self.no_fetch:
            self._attach_from_pool(product, slug, count)
            return

        attached = 0
        for i in range(count):
            # Tartib: Unsplash → loremflickr → picsum
            candidates: list[str] = []
            if self.unsplash_key and not self.unsplash_disabled:
                u = self._get_unsplash_url(img_kw, slug, i)
                if u:
                    candidates.append(u)
            candidates.extend([
                f"https://loremflickr.com/700/700/{img_kw}?lock={abs(hash(slug)) % 1000 + i}",
                f"https://picsum.photos/seed/{slug}-{i}/700/700",
            ])

            for url in candidates:
                try:
                    resp = self.session.get(url, timeout=20, allow_redirects=True)
                    if resp.status_code == 200 and len(resp.content) > 1000:
                        img = ProductImage(
                            product=product,
                            alt_text=product.name,
                            alt_text_uz=product.name_uz,
                            alt_text_ru=product.name_ru,
                            alt_text_en=product.name_en,
                            order=i,
                            is_primary=(i == 0),
                        )
                        img.image.save(
                            f"{slug}-{i}.jpg",
                            ContentFile(resp.content),
                            save=True,
                        )
                        attached += 1
                        break
                except requests.RequestException:
                    continue

        # Pool fallback
        if attached == 0 and self.image_pool:
            self._attach_from_pool(product, slug, count)

    def _get_unsplash_url(self, keyword: str, slug: str, index: int) -> str | None:
        """Unsplash'dan kalit so'zga mos foto URL'ini olish.

        Per-keyword kesh: har noyob kalit so'z uchun bir martagina API chaqiriladi
        (5 ta foto olinadi), keyin shu kalit so'zli barcha mahsulotlar shu pool'dan
        deterministik (slug+index hash bo'yicha) tanlaydi. Bu 543 mahsulotni
        50/soat limitiga sig'dirish uchun kerak.
        """
        if self.unsplash_disabled:
            return None

        if keyword not in self.unsplash_cache:
            try:
                r = self.session.get(
                    "https://api.unsplash.com/search/photos",
                    params={
                        "query": keyword,
                        "per_page": 5,
                        "orientation": "squarish",
                        "content_filter": "high",
                    },
                    headers={"Authorization": f"Client-ID {self.unsplash_key}"},
                    timeout=15,
                )
                if r.status_code == 200:
                    results = r.json().get("results", [])
                    urls = [p["urls"]["regular"] for p in results if p.get("urls", {}).get("regular")]
                    # Cache ham bo'sh, ham urls'lik natijalar — keyingi run'lar
                    # qaytadan API chaqirmasligi uchun. Faqat foto YO'Q deb
                    # tasdiqlangan keyword shu xolatda saqlanadi.
                    self.unsplash_cache[keyword] = urls
                    if not urls:
                        self.stdout.write(f"    [unsplash] '{keyword}' uchun foto topilmadi")
                elif r.status_code == 403:
                    # Rate-limit. Cache'ga YOZMAYMIZ — keyingi run'da qaytadan
                    # urinish uchun. Hozircha shu run uchun Unsplash o'chiriladi.
                    rem = r.headers.get("X-Ratelimit-Remaining", "?")
                    self.stdout.write(self.style.WARNING(
                        f"    [unsplash] RATE LIMIT (403, remaining={rem}) — "
                        "loremflickr/picsum'ga o'tamiz, keyingi run'da qayta urinamiz"
                    ))
                    self.unsplash_disabled = True
                elif r.status_code == 401:
                    # Key noto'g'ri — cache'ga yozish ma'nosiz.
                    self.stdout.write(self.style.ERROR(
                        "    [unsplash] Access Key noto'g'ri (401) — loremflickr'ga o'tamiz"
                    ))
                    self.unsplash_disabled = True
                else:
                    # Boshqa xatolar — cache'ga yozmaymiz, keyingi run qayta urinadi.
                    self.stdout.write(f"    [unsplash] xato {r.status_code}: {keyword}")
            except requests.RequestException as exc:
                # Tarmoq xatosi — cache'ga yozmaymiz.
                self.stdout.write(f"    [unsplash] tarmoq xatosi: {exc}")

        photos = self.unsplash_cache.get(keyword) or []
        if not photos:
            return None
        # Deterministik tanlash (slug + index)
        idx = (abs(hash(slug)) + index) % len(photos)
        return photos[idx]

    # ----------------------------------------------------------------------
    def _load_unsplash_cache(self) -> dict[str, list[str]]:
        """media/.unsplash_cache.json dan keshlanga keyword→URLs'ni o'qish."""
        if not self.unsplash_cache_file.exists():
            return {}
        try:
            with self.unsplash_cache_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except (OSError, ValueError):
            return {}

    def _save_unsplash_cache(self) -> None:
        """Joriy unsplash_cache'ni diskka yozish — keyingi run'da qayta ishlatish uchun."""
        if not self.unsplash_cache:
            return
        try:
            self.unsplash_cache_file.parent.mkdir(parents=True, exist_ok=True)
            with self.unsplash_cache_file.open("w", encoding="utf-8") as f:
                json.dump(self.unsplash_cache, f, ensure_ascii=False, indent=2)
            self.stdout.write(
                f"  [unsplash] disk cache saqlandi: {len(self.unsplash_cache)} ta keyword"
            )
        except OSError as exc:
            self.stdout.write(self.style.WARNING(
                f"  [unsplash] cache saqlanmadi: {exc}"
            ))

    def _attach_from_pool(self, product, slug: str, count: int) -> None:
        """Mavjud media/products/ pool'idan deterministik tanlash (offline)."""
        if not self.image_pool:
            return
        h = abs(hash(slug))
        for i in range(count):
            src = self.image_pool[(h + i) % len(self.image_pool)]
            try:
                with src.open("rb") as f:
                    content = f.read()
                img = ProductImage(
                    product=product,
                    alt_text=product.name,
                    alt_text_uz=product.name_uz,
                    alt_text_ru=product.name_ru,
                    alt_text_en=product.name_en,
                    order=i,
                    is_primary=(i == 0),
                )
                img.image.save(
                    f"{slug}-{i}-pool.jpg",
                    ContentFile(content),
                    save=True,
                )
            except OSError:
                continue

    def _seed_reviews(self) -> None:
        reviewers = []
        for i in range(8):
            u, _ = User.objects.get_or_create(
                email=f"mijoz{i}@demo.uz",
                defaults={"full_name": f"Mijoz {i + 1}", "is_email_verified": True},
            )
            reviewers.append(u)
        for product in Product.objects.all():
            if product.reviews.exists():
                continue
            for u in random.sample(reviewers, random.randint(0, 4)):
                title, content = random.choice(REVIEW_TEXTS)
                Review.objects.create(
                    product=product, user=u, rating=random.randint(3, 5),
                    title=title, content=content,
                    is_verified_purchase=random.choice([True, False]),
                    status=Review.Status.APPROVED,
                )
            recompute_product_rating(product.id)

    def _seed_banners(self) -> None:
        items = [
            ("Premium kolleksiya", "Премиум коллекция", "Premium collection",
             "Eng yaxshi mahsulotlar bir joyda",
             "Лучшие товары в одном месте",
             "Top products in one place"),
            ("Chegirmalar mavsumi", "Сезон скидок", "Sale season",
             "50% gacha tejang", "Экономия до 50%", "Save up to 50%"),
        ]
        for o, (t_uz, t_ru, t_en, s_uz, s_ru, s_en) in enumerate(items):
            b, created = Banner.objects.get_or_create(
                title=t_uz,
                defaults={
                    "subtitle": s_uz,
                    "position": "hero", "order": o, "is_active": True,
                },
            )
            # Always sync translations (idempotent)
            b.title_uz = t_uz; b.title_ru = t_ru; b.title_en = t_en
            b.subtitle_uz = s_uz; b.subtitle_ru = s_ru; b.subtitle_en = s_en
            b.save()
            if created and not self.no_images and not self.no_fetch:
                try:
                    r = self.session.get(
                        f"https://picsum.photos/seed/banner-{o}/1600/600", timeout=15,
                    )
                    if r.status_code == 200:
                        b.image.save(f"banner-{o}.jpg",
                                     ContentFile(r.content), save=True)
                except requests.RequestException:
                    pass

    def _seed_coupons(self) -> None:
        for code, value in [("WELCOME10", 10), ("SUMMER20", 20)]:
            Coupon.objects.get_or_create(
                code=code,
                defaults={
                    "type": Coupon.Type.PERCENTAGE,
                    "value": Decimal(value),
                    "is_active": True,
                    "usage_limit": 1000,
                    "used_count": 0,
                },
            )

    def _seed_demo_user(self) -> None:
        u, created = User.objects.get_or_create(
            email="demo@demo.uz",
            defaults={
                "full_name": "Demo Customer",
                "is_email_verified": True,
                "language": "uz",
            },
        )
        if created:
            u.set_password("Demo1234!")
            u.save(update_fields=["password"])
