# -*- coding: utf-8 -*-
"""
Bot konfiguratsiyasi.
Token va Admin ID ni .env faylida ham belgilash mumkin (ustunlik .env ga beriladi),
lekin standart qiymat sifatida foydalanuvchi bergan ma'lumotlar o'rnatilgan,
shuning uchun bot .env bo'lmasa ham ishlaydi.
"""
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8757536170:AAGuOgtPy7Rl0djDcK_XF2sHX_SZOsBpp_s")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7861165622"))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "database.db")
EXCEL_PATH = os.path.join(DATA_DIR, "users.xlsx")

# Anketa cheklovlari
MIN_AGE = 14
MAX_AGE = 100
MAX_NAME_LEN = 50
MAX_BIO_LEN = 500
