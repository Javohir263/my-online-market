# My Online Market — Loyiha rejasi va texnik tafsilotlar

> **Bu fayl** — `my-online-market` loyihasining boshlang'ich
> reja-hujjati. Yangi chat sessiyasida menga aytsangiz, bu faylni
> o'qib chiqaman va aynan shu joydan davom etamiz.
>
> **Hozirgi holat:** reja tugadi, kod hali yozilmadi. Keyingi qadam → **B1** (Backend skeleton).

---

## 1. Loyiha haqida

**Nomi:** My Online Market
**Tipi:** Professional e-commerce platforma (Uzum.uz uslubida)
**Maqsad:** To'liq funksional, zamonaviy va premium "luxury" hissi beradigan online marketplace
**Referens sayt:** <https://uzum.uz/uz>

---

## 2. Tasdiqlangan biznes qarorlar

| Soha | Tanlov |
|---|---|
| **Vendor modeli** | Single-vendor MVP, lekin schema'da `vendor_id` hozirdan (multi-vendor extensibility) |
| **To'lov** | Simulatsiya (status workflow: pending → paid → ...). Real gateway integratsiyasi yo'q |
| **Admin panel** | Django Admin built-in + `django-admin-interface` bilan customize |
| **Tillar** | uz + ru + en (django-modeltranslation + next-intl) |

---

## 3. Texnologiyalar steki (tasdiqlangan)

### Backend
- **Framework**: Django 5 + Django REST Framework
- **Database**: PostgreSQL 16+
- **Cache + broker**: Redis 7
- **Async tasks**: Celery + Redis
- **API docs**: drf-spectacular (OpenAPI/Swagger)
- **Auth**: JWT in **httpOnly cookies** (XSS-safe), djangorestframework-simplejwt
- **i18n**: django-modeltranslation
- **Search**: PostgreSQL `pg_trgm` + full-text search
- **Image storage**: Cloudinary (free tier, CDN, auto WebP/AVIF)
- **Email**: django-anymail (transactional)
- **SMS**: Eskiz.uz (OTP, order updates)
- **Testing**: pytest-django + factory-boy
- **Linting**: Black + Ruff + mypy

### Frontend
- **Framework**: **Next.js 15 App Router** (SEO uchun majburiy — SSR + structured data)
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4 + **shadcn/ui** komponentlar
- **State (client)**: Zustand + persist
- **State (server)**: TanStack Query
- **Forms**: React Hook Form + Zod
- **i18n**: next-intl
- **Icons**: lucide-react
- **Notifications**: react-hot-toast
- **HTTP**: axios (cookie-based)
- **Fonts**: Inter (body) + Playfair Display (heading, premium feel)

### DevOps
- **Containerisation**: Docker + docker-compose
- **CI**: GitHub Actions (lint + test)
- **Deployment**: AWS EC2 (yoki backend uchun mavjud server) + Nginx
- **Monitoring (kelajak)**: Sentry

---

## 4. Loyiha tuzilishi

### Backend folder layout
```
my-online-market-backend/
├── config/
│   ├── settings/{base,development,production,test}.py
│   ├── urls.py, celery.py, wsgi.py, asgi.py
├── apps/
│   ├── core/         # BaseModel, mixins, exceptions, permissions
│   ├── accounts/     # User, Address, OTP
│   ├── auth/         # JWT cookie auth, register/login/refresh
│   ├── vendors/      # Vendor (single now, multi-ready)
│   ├── catalog/      # Category(tree), Brand, Product, Variant, Image, Attribute, Tag
│   ├── cart/         # Cart, CartItem (anonymous + auth, merge)
│   ├── orders/       # Order + OrderItem (snapshot pattern)
│   ├── reviews/      # Review, ReviewImage
│   ├── wishlist/
│   ├── promotions/   # Banner, Coupon, CouponUsage
│   ├── payments/     # Payment (simulated)
│   └── notifications/# Notification, EmailLog + Celery tasks
├── locale/ (uz, ru, en)
├── media/ (gitignored — Cloudinary'ga uploads)
├── requirements/{base,development,production}.txt
├── manage.py, Dockerfile, docker-compose.yml, pytest.ini, .env.example
```

### Frontend folder layout
```
my-online-market-frontend/
├── app/
│   ├── (storefront)/
│   │   ├── layout.tsx, page.tsx
│   │   ├── catalog/, product/[slug]/, cart/, checkout/, wishlist/, search/
│   │   └── account/ (profile, orders, addresses)
│   ├── (auth)/
│   │   ├── login/, register/, verify/
│   ├── api/, sitemap.ts, robots.ts, not-found.tsx, error.tsx
├── src/
│   ├── components/{ui,layout,product,cart,checkout,home,account}/
│   ├── api/, hooks/, store/, lib/{i18n,validations,format,utils}/
│   ├── types/
│   └── messages/{uz.json, ru.json, en.json}
├── middleware.ts (i18n + auth gate)
├── next.config.ts, tailwind.config.ts, components.json
```

---

## 5. Ma'lumotlar bazasi sxemasi (21 jadval)

### Accounts (3)
- **User** (custom AbstractUser): id (UUID), email (unique, USERNAME_FIELD), phone, full_name, password, language (uz/ru/en), role (customer/staff/admin), is_email_verified, is_phone_verified, timestamps
- **Address**: user, type (shipping/billing), recipient_name, recipient_phone, region, city, district, street, building, apartment, postal_code, is_default
- **OtpCode**: target (email/phone), code, purpose (email_verify/phone_verify/password_reset), expires_at, used_at, attempts

### Vendors (1)
- **Vendor**: id, slug, name, logo, owner (FK User), description (i18n), status, commission_rate
  - MVP'da bitta `DEFAULT_VENDOR` seed

### Catalog (7)
- **Category** (self-referencing tree): slug, parent_id, name (i18n), description (i18n), image, icon, order, products_count (denormalized)
- **Brand**: slug, name, logo, description (i18n)
- **Product**: UUID id, slug, sku, vendor_id, category_id, brand_id, name (i18n), description (i18n), short_description (i18n), base_price, sale_price, currency (UZS), stock_quantity, is_in_stock, ratings_avg (denormalized), ratings_count (denormalized), views_count, is_active, is_featured, is_new, is_bestseller, timestamps
- **ProductImage**: product_id, image (Cloudinary URL), alt_text (i18n), order, is_primary
- **ProductVariant**: product_id, sku, color, size, additional_price (default 0), stock_quantity, image
- **ProductAttribute**: product_id, name (i18n), value (i18n), order
- **ProductTag**: slug, name (i18n), color (label like "new", "hit", "sale")

### Cart (2)
- **Cart**: user_id (nullable), session_key (nullable for anonymous), timestamps. Anonymous → user MERGE on login
- **CartItem**: cart_id, product_id, variant_id, quantity, price_snapshot, added_at

### Orders (2, snapshot pattern)
- **Order**: number ("MOM-2026-000123"), user_id, status (pending/confirmed/shipped/delivered/cancelled), subtotal, shipping_cost, discount_amount, total, currency, shipping_address (JSONField snapshot), customer_note, coupon_id, timestamps for each status transition, cancel_reason
- **OrderItem**: order_id, product_id, variant_id, vendor_id, quantity, price_at_purchase, product_name_snapshot, product_image_snapshot

### Reviews (2)
- **Review**: product_id, user_id, rating (1-5), title, content, is_verified_purchase (auto), helpful_count, status (pending/approved/rejected). UNIQUE(product, user)
- **ReviewImage**: review_id, image

### Wishlist (1)
- **WishlistItem**: user_id, product_id, added_at. UNIQUE(user, product)

### Promotions (3)
- **Banner**: title (i18n), subtitle (i18n), image, link, position (hero/sidebar/category/footer), order, is_active, valid_from, valid_to
- **Coupon**: code (unique), type (percentage/fixed), value, min_order_amount, max_discount, usage_limit, per_user_limit, used_count, valid_from, valid_to, is_active
- **CouponUsage**: coupon_id, user_id, order_id, used_at

### Payments (1, simulated)
- **Payment**: order_id, method (simulation/cod/click/payme), status (pending/paid/failed/refunded), amount, currency, paid_at, refunded_at, gateway_response (JSONField)

### Notifications (2)
- **Notification**: user_id, type, title (i18n), message (i18n), data (JSON), is_read, created_at
- **EmailLog**: recipient, subject, template, status, sent_at, error_message

---

## 6. API endpointlar (~55 ta)

**Versioning**: `/api/v1/`. 🔒 = JWT cookie required. 👑 = admin.

### Auth (9)
- POST /auth/register/, /auth/login/, /auth/logout/, /auth/refresh/
- POST /auth/password/reset/{request,confirm}/
- POST /auth/email/verify/{send,confirm}/ 🔒
- GET /auth/me/ 🔒

### Accounts (5)
- GET/PUT /accounts/profile/ 🔒
- PUT /accounts/profile/password/ 🔒
- GET/POST /accounts/addresses/ 🔒
- GET/PUT/DELETE /accounts/addresses/<id>/ 🔒

### Catalog (10)
- GET /catalog/categories/ (tree), /categories/<slug>/
- GET /catalog/brands/
- GET /catalog/products/ (?category=&brand=&min_price=&max_price=&rating=&in_stock=&search=&sort=)
- GET /catalog/products/<slug>/, /products/<slug>/similar/
- GET /catalog/products/{featured,new-arrivals,bestsellers}/
- GET /catalog/search/, /catalog/search/suggest/

### Cart (7)
- GET /cart/, POST/PATCH/DELETE /cart/items/[id]/
- DELETE /cart/ (clear)
- POST /cart/merge/ 🔒
- POST /cart/coupon/apply/, DELETE /cart/coupon/

### Wishlist (3) 🔒
- GET /wishlist/, POST /wishlist/items/, DELETE /wishlist/items/<product_id>/

### Orders (4) 🔒
- GET /orders/, POST /orders/ (checkout)
- GET /orders/<number>/, POST /orders/<number>/cancel/

### Reviews (5)
- GET /products/<slug>/reviews/, POST 🔒
- PUT/DELETE /reviews/<id>/ 🔒
- POST /reviews/<id>/helpful/ 🔒

### Promotions (2)
- GET /promotions/banners/ (?position=)
- POST /promotions/coupons/validate/

### Payments (2) 🔒
- POST /payments/simulate/, GET /payments/<id>/

### Notifications (3) 🔒
- GET /notifications/, PATCH /notifications/<id>/read/, POST /notifications/read-all/

---

## 7. Roadmap (15+ bosqich, ~40 ish kuni)

| № | Bosqich | Davomiyligi | Mazmuni |
|---|---|---|---|
| **B1** | Backend skeleton | 1 kun | Django 5 + DRF + PG + Redis + Celery + settings split + Docker + .env |
| **B2** | Custom User + Accounts | 2 kun | AbstractUser, Address, OTP, manager, migrations, admin |
| **B3** | Auth (JWT cookies) | 2 kun | Register, login, logout, refresh, email verify via OTP |
| **B4** | i18n + locale middleware | 1 kun | django-modeltranslation, uz/ru/en setup |
| **B5** | Catalog models | 2 kun | Category tree, Brand, Product, Variant, Image, Attribute, Tag |
| **B6** | Catalog API + search | 3 kun | List/detail/filter/sort, pg_trgm fuzzy search |
| **B7** | Cart + Wishlist | 2 kun | Anonymous → authenticated merge, atomic ops |
| **B8** | Orders + Checkout + Stock lock | 3 kun | SELECT FOR UPDATE, snapshot pattern, FSM workflow |
| **B9** | Reviews | 1 kun | Verified-purchase auto-flag, moderation, helpful votes |
| **B10** | Promotions (Banner, Coupon) | 2 kun | Discount service, usage tracking |
| **B11** | Notifications + Celery | 2 kun | Order confirmation email, async tasks, structure for SMS |
| **B12** | Django Admin polish | 1 kun | `django-admin-interface`, inline editors, image preview, dashboard widgets |
| **B13** | Frontend skeleton + design system | 3 kun | Tailwind + shadcn/ui, palette, layout, header/footer, fonts |
| **B14** | Storefront: home + catalog + product | 4 kun | SSR pages, gallery, filters, search, pagination |
| **B15** | Storefront: cart + checkout + account | 4 kun | Cart drawer, multi-step checkout, dashboard |
| **B16** | i18n frontend + SEO | 2 kun | next-intl, sitemap, robots, OG meta, JSON-LD |
| **B17** | Tests + CI + Deployment | 3 kun | pytest, GitHub Actions, Docker, EC2 + Nginx |

---

## 8. Dizayn — rang palitra (premium luxury)

### Brand palette
```js
// Tailwind config'ga
primary: {  // BORDOVIY
  50: '#fdf2f4', 100: '#fce7eb', 200: '#f9cfd6',
  300: '#f3a3b1', 400: '#e96b83', 500: '#9b1c2d',
  600: '#7a142a', 700: '#6b0f1a', 800: '#5a0d18', 900: '#4a0a14',
},
neutral: {  // BEJ
  50:  '#fdfcf9', 100: '#f5f0e8', 200: '#efe5d5',
  300: '#e6d8c0', 400: '#c4b394', 500: '#a08967',
  600: '#8b7355', 700: '#6b5d3f', 800: '#4a4128', 900: '#2c2818',
},
accent: {  // TO'Q YASHIL
  500: '#2d5016', 600: '#1f3a10', 700: '#1b4332', 800: '#143025',
},
khaki: {  // XAKI
  500: '#8b7355', 600: '#7a6549', 700: '#6b5d3f',
},
```

### Typography
- **Heading**: Playfair Display yoki Cormorant Garamond (serif, luxury feel)
- **Body**: Inter (modern, readable)
- **Mono**: JetBrains Mono (code, prices)

### Vibe
- Bordoviy = brand, CTAs (Add to cart, Buy now)
- Bej = backgrounds, cards
- To'q yashil = secondary accents, success states, badges
- Xaki = subtle dividers, metadata text
- Generous whitespace, ko'p **hava** (premium hissi)
- Subtle gold/copper accents on hover
- Soft shadows, no harsh borders

---

## 9. Senior bo'yicha qo'shimcha tavsiyalar

### Xavfsizlik
- CSRF + SameSite=Lax cookies
- django-ratelimit (login, register, OTP, password reset)
- Idempotency keys for order creation
- `SELECT FOR UPDATE` on Product.stock (over-sell prevention)
- Argon2 password hashing
- HTTPS + HSTS in prod

### Performance
- Indexlar: (category, is_active, created_at), slug (unique), composite for listings
- `select_related` + `prefetch_related` har joyda
- Denormalized counters (ratings_avg, products_count, views_count)
- Redis cache: category_tree, featured_products, banners (TTL 5-10 min)
- Next.js ISR: product pages revalidate 60s, on-demand for stock changes
- Cloudinary CDN + auto-format (WebP/AVIF)

### SEO
- Slug-based hierarchical URLs (`/catalog/elektronika/telefonlar/iphone-15`)
- Meta tags, OG image (per product)
- JSON-LD Product schema → Google Rich Results
- Canonical URLs (filter params)
- Sitemap.ts + robots.ts (Next.js native)
- Hreflang for uz/ru/en versions

### Modullik (multi-vendor uchun)
- `vendor_id` har joyda hozirdan (Product, OrderItem, ...)
- Future: vendor onboarding, dashboard, payouts, commission

### Test strategy
- Backend: pytest-django, ~100 ta test
- Frontend: Vitest + React Testing Library (kritik flow'lar)
- E2E (optional): Playwright

---

## 10. Loyiha joylashuvi

| Komponent | Yo'l |
|---|---|
| Plan fayli | `C:\Najot ta'lim\loihalarim\my-online-market\PROJECT-PLAN.md` (siz hozir ko'rib turgan fayl) |
| Backend (yaratiladi) | `C:\Najot ta'lim\loihalarim\my-online-market-backend\` |
| Frontend (yaratiladi) | `C:\Najot ta'lim\loihalarim\my-online-market-frontend\` |

---

## 11. Yangi sessiyada qanday davom etish

**Yangi chat'ga shu xabarni nusxalab yuboring:**

```
Salom! my-online-market loyihasini davom ettiramiz.

Avval ushbu faylni o'qib chiq:
C:\Najot ta'lim\loihalarim\my-online-market\PROJECT-PLAN.md

Bu loyihaning to'liq reja-hujjati: biznes qarorlar, tech stack,
DB schema, API endpoint'lar, roadmap va dizayn palitra hammasi
bor. Hozir biz B1 (Backend skeleton) dan boshlamoqchimiz.

Bu loyihada men senior full-stack dasturchi yondashuvini kutaman —
clean code, modulli arxitektura, xavfsizlik, performance va SEO
ustida e'tibor bilan ish olib boramiz. Har bosqich oxirida
commit + push qilamiz, har bosqichni alohida tasdiqdan
keyin davom etamiz.

Reja ma'qul bo'lsa B1 dan boshla — Django 5 + DRF + PostgreSQL
+ Redis + Celery + Docker compose + .env + settings split bilan
backend skeletini quramiz.
```

Men buni o'qib, faylni tahlil qilib, B1 dan davom etaman.

---

**Sana**: 2026-05-25
**Holati**: Reja tugadi, kod hali yozilmadi
**Keyingi qadam**: B1 — Backend skeleton (Django 5 + DRF + PG + Redis + Celery + Docker)
