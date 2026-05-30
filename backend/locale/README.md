# Locale (i18n) papkasi

Bu yerda **uz / ru / en** tillariga tarjimalar saqlanadi.

## Tarjimalarni jamlash (makemessages)

Django'ning `gettext` xabarlarini (`_("...")` ko'rinishidagi) avtomatik
yig'ish va `.po` fayllarga yozish:

```powershell
python manage.py makemessages -l uz -l ru -l en --ignore=.venv --ignore=staticfiles
```

> ⚠️ **Windows uchun gettext kerak** — <https://mlocati.github.io/articles/gettext-iconv-windows.html>
> dan yuklab oling, `bin/` ni PATH'ga qo'shing.

## Tarjima qilish

`locale/uz/LC_MESSAGES/django.po` (va ru, en) fayllarini ochib `msgstr ""` qatorlariga tarjimalarni yozing:

```po
msgid "Email yoki parol noto'g'ri."
msgstr "Email or password is incorrect."   # en
```

## Kompilatsiya (.po → .mo)

```powershell
python manage.py compilemessages
```

`.mo` fayllar Django runtime'ida ishlatiladi. **`.mo` fayllar Git'ga commit qilinmaydi** (`.gitignore`'da).
