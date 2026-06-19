# -*- coding: utf-8 -*-
"""Handlerlar orasida umumiy ishlatiladigan servis funksiyalar."""
from aiogram import Bot

import database as db
from config import ADMIN_ID
from helpers import build_profile_caption
from keyboards import admin_review_kb


async def send_profile_to_admin(bot: Bot, user_id: int):
    """Yangi/tahrirlangan anketani admin ko'rib chiqishi uchun yuboradi."""
    user = await db.get_user(user_id)
    if not user:
        return
    caption = "🆕 <b>Yangi anketa tasdiqlash uchun yuborildi</b>\n\n" + build_profile_caption(user, show_id=True)
    try:
        await bot.send_photo(
            ADMIN_ID,
            photo=user["photo"],
            caption=caption,
            reply_markup=admin_review_kb(user_id),
        )
    except Exception:
        pass
