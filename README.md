# 📱 Anketa-Bot (LeoMatch/Davinchik uslubida)

Telegram uchun tanishuv-anketa boti. Foydalanuvchilar anketa to'ldiradi, boshqalarning
anketalarini ko'rib, layk bosadi yoki yozadi. Admin barcha anketalarni tasdiqlaydi,
reklama yuboradi va statistikani ko'radi.

## ⚙️ Texnologiyalar

- Python 3.10+
- [aiogram 3](https://docs.aiogram.dev/) — Telegram Bot framework
- SQLite (aiosqlite) — ma'lumotlar bazasi
- openpyxl — Excel fayl yaratish

## 📂 Loyiha tuzilishi

```
anketa_bot/
├── bot.py                  # Botni ishga tushiruvchi asosiy fayl
├── config.py                # Token, Admin ID va sozlamalar
├── database.py               # SQLite bilan ishlash (barcha SQL so'rovlar)
├── states.py                 # FSM holatlari (anketa to'ldirish, reklama)
├── keyboards.py               # Barcha reply/inline klaviaturalar
├── helpers.py                 # Anketa matnini shakllantirish funksiyalari
├── services.py                 # Admin uchun umumiy xabar yuborish funksiyasi
├── requirements.txt
├── .env.example                # Token/Admin ID namunasi
├── data/                        # SQLite baza va Excel fayl shu yerda saqlanadi
├── handlers/
│   ├── start.py                  # /start buyrug'i
│   ├── profile.py                 # Anketa to'ldirish, tahrirlash, o'chirish
│   ├── search.py                   # Anketa qidirish, layk/yoqmadi/yozish
│   ├── chat.py                      # Foydalanuvchilar orasidagi yozishma (relay)
│   └── admin.py                      # Admin panel
└── utils/
    ├── regions.py                    # O'zbekiston viloyatlari ro'yxati
    └── excel_export.py                # Excel fayl generatsiyasi
```

## 🚀 O'rnatish va ishga tushirish

1. Python 3.10 yoki undan yuqori versiyasi o'rnatilganligiga ishonch hosil qiling.
2. Loyiha papkasiga kiring va kerakli kutubxonalarni o'rnating:

   ```bash
   pip install -r requirements.txt
   ```

3. Bot toketi va Admin ID `config.py` faylida allaqachon **standart qiymat** sifatida
   o'rnatilgan, shuning uchun bot hech narsa sozlamasdan ham ishlaydi:

   - Bot token: `8757536170:AAGuOgtPy7Rl0djDcK_XF2sHX_SZOsBpp_s`
   - Admin ID: `7861165622`

   Agar token yoki admin ID ni o'zgartirish kerak bo'lsa, `.env.example` faylini
   `.env` nomiga o'zgartirib, ichidagi qiymatlarni yangilang.

4. Botni ishga tushiring:

   ```bash
   python bot.py
   ```

Bot ishga tushganda `data/database.db` fayli avtomatik yaratiladi — boshqa hech qanday
qo'shimcha sozlash kerak emas.

## ✨ Foydalanuvchi funksiyalari

- **/start** — birinchi marta kirganda bot avtomatik anketa to'ldirish jarayonini
  boshlaydi: Ism → Rasm → Yosh → Jins → Viloyat → O'zi haqida tarif → Tasdiqlash.
- Anketa to'ldirilgach, **admin** ko'rib chiqishi uchun yuboriladi. Admin javobini
  kutayotgan vaqtda ham foydalanuvchi boshqa anketalarni qidira oladi.
- **🔍 Anketa qidirish** — tasodifiy (ko'p layk olganlar birinchi navbatda) tasdiqlangan
  anketalar ko'rsatiladi: ism, yosh, rasm va tarif. Tugmalar: ❤️ Yoqdi, ✍️ Yozish,
  ❌ Yoqmadi, 👤 Mening anketam.
  - ❤️ **Yoqdi** — layklar soni hisoblanadi, anketa egasiga "❤️ X sizni yoqtirdi!"
    degan xabar uning anketasi bilan boradi, so'rovchi keyingi anketaga o'tadi.
  - ✍️ **Yozish** — bot orqali anketa egasi bilan to'g'ridan-to'g'ri yozishish
    boshlanadi (suhbatni tugatish: `/tugat`).
  - ❌ **Yoqmadi** — avtomatik keyingi tasodifiy anketaga o'tadi.
  - Bir xil anketa ikki marta takrorlanmaydi (barchasi ko'rilgach ro'yxat yangilanadi).
- **👤 Mening anketam** — o'z anketasi, layklar soni va holatini ko'rsatadi.
  Qo'shimcha tugmalar:
  - ❤️ Yoqtirganlar — anketani yoqtirgan foydalanuvchilar ro'yxati.
  - ✉️ Menga yozganlar — bot orqali yozgan foydalanuvchilar ro'yxati.
  - ✏️ Tahrirlash — anketani **butunlay** qaytadan to'ldirish (qayta admin tasdig'iga
    yuboriladi).
  - 🗑 O'chirish — anketani **butunlay** o'chirish (tasdiqlash so'raladi).

## 🛠 Admin funksiyalari

`/admin` buyrug'i orqali faqat **Admin ID** (`7861165622`) admin panelga kira oladi:

- **📊 Statistika** — jami foydalanuvchilar, tasdiqlangan/kutilayotgan/rad etilgan
  anketalar, jami layklar va xabarlar soni.
- **📢 Reklama yuborish** — istalgan matn/rasm/video postni botga `/start` bosgan
  **barcha** foydalanuvchilarga yuborish (bekor qilish: `/bekor`).
- **📥 Excel yuklab olish** — barcha foydalanuvchilarning (ism, yosh, jinsi, viloyat,
  tarif, holat, ID) ma'lumotlari `.xlsx` fayl ko'rinishida yuboriladi.

Yangi anketa kelganda admin'ga avtomatik ravishda **rasm + barcha ma'lumotlar**
(ism, rasm, yosh, jinsi, viloyat, tarif) bilan birga "✅ Tasdiqlash" / "❌ Rad etish"
tugmalari yuboriladi:

- ✅ Tasdiqlansa — anketa qidiruvga qo'shiladi, foydalanuvchiga xabar boradi.
- ❌ Rad etilsa — foydalanuvchiga yangi anketa to'ldirish kerakligi haqida xabar boradi.

## 📝 Muhim eslatmalar

- Anketa **tahrirlangandan** keyin ham (xavfsizlik/nazorat maqsadida) qaytadan admin
  tasdig'idan o'tadi — bu vaqt ichida anketa qidiruvda vaqtincha ko'rinmaydi, lekin
  foydalanuvchi o'zi boshqalarni qidirishda davom etishi mumkin.
- Bot ma'lumotlar bazasi sifatida SQLite ishlatadi (`data/database.db`) — kichik va
  o'rta hajmdagi loyihalar uchun yetarli, server qayta ishga tushirilganda ma'lumotlar
  yo'qolmaydi.
- Agar foydalanuvchi botni bloklagan bo'lsa, reklama/layk/xabar yuborishda xatolik
  avtomatik tutiladi va boshqa foydalanuvchilarga yuborish davom etadi.

## 🔒 Xavfsizlik

Admin paneliga va admin callback tugmalariga (tasdiqlash/rad etish/statistika/excel/
reklama) faqat `config.py` da ko'rsatilgan `ADMIN_ID` ga ega foydalanuvchi kira oladi —
boshqa foydalanuvchilar bu funksiyalarga kira olmaydi, hatto callback_data ni bilsa ham.

Omad! 🚀
