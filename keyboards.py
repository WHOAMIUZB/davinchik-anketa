# -*- coding: utf-8 -*-
"""Bot uchun barcha klaviaturalar."""
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from utils.regions import REGIONS

BTN_SEARCH = "🔍 Anketa qidirish"
BTN_MY_PROFILE = "👤 Mening anketam"


def main_menu_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=BTN_SEARCH)
    builder.button(text=BTN_MY_PROFILE)
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def gender_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="👨 Erkak", callback_data="gender_Erkak")
    builder.button(text="👩 Ayol", callback_data="gender_Ayol")
    builder.adjust(2)
    return builder.as_markup()


def region_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for idx, region in enumerate(REGIONS):
        builder.button(text=region, callback_data=f"region_{idx}")
    builder.adjust(2)
    return builder.as_markup()


def confirm_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Tasdiqlash va yuborish", callback_data="profile_confirm")
    builder.button(text="🔄 Qaytadan to'ldirish", callback_data="profile_restart")
    builder.adjust(1)
    return builder.as_markup()


def profile_card_kb(target_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="❤️ Yoqdi", callback_data=f"like_{target_id}")
    builder.button(text="✍️ Yozish", callback_data=f"write_{target_id}")
    builder.button(text="❌ Yoqmadi", callback_data=f"dislike_{target_id}")
    builder.button(text="👤 Mening anketam", callback_data="myprofile")
    builder.adjust(2, 2)
    return builder.as_markup()


def my_profile_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="❤️ Yoqtirganlar", callback_data="my_likes")
    builder.button(text="✉️ Menga yozganlar", callback_data="my_writers")
    builder.button(text="✏️ Tahrirlash", callback_data="edit_profile")
    builder.button(text="🗑 O'chirish", callback_data="delete_profile")
    builder.adjust(2, 2)
    return builder.as_markup()


def delete_confirm_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Ha, o'chirish", callback_data="delete_confirm_yes")
    builder.button(text="❌ Bekor qilish", callback_data="delete_confirm_no")
    builder.adjust(2)
    return builder.as_markup()


def write_back_kb(target_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="↩️ Javob yozish", callback_data=f"write_{target_id}")
    builder.adjust(1)
    return builder.as_markup()


def admin_panel_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Statistika", callback_data="admin_stats")
    builder.button(text="📢 Reklama yuborish", callback_data="admin_broadcast")
    builder.button(text="📥 Excel yuklab olish", callback_data="admin_excel")
    builder.adjust(1)
    return builder.as_markup()


def admin_review_kb(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Tasdiqlash", callback_data=f"approve_{user_id}")
    builder.button(text="❌ Rad etish", callback_data=f"reject_{user_id}")
    builder.adjust(2)
    return builder.as_markup()
