# -*- coding: utf-8 -*-
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import database as db
from helpers import build_search_caption
from keyboards import profile_card_kb, BTN_SEARCH

router = Router(name="search")


async def send_next_profile(bot, viewer_id: int, chat_id: int):
    profile = await db.get_random_profile(viewer_id)
    if not profile:
        await bot.send_message(
            chat_id,
            "😔 Hozircha ko'rsatish uchun boshqa anketalar yo'q.\nKeyinroq qaytadan urinib ko'ring.",
        )
        return
    await db.mark_viewed(viewer_id, profile["telegram_id"])
    caption = build_search_caption(profile)
    await bot.send_photo(
        chat_id,
        photo=profile["photo"],
        caption=caption,
        reply_markup=profile_card_kb(profile["telegram_id"]),
    )


@router.message(F.text == BTN_SEARCH)
async def search_start(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user or not user.get("name"):
        await message.answer("🙁 Avval o'zingiz anketa to'ldiring. /start bosing.")
        return
    await send_next_profile(message.bot, message.from_user.id, message.chat.id)


@router.callback_query(F.data.startswith("dislike_"))
async def dislike_profile(callback: CallbackQuery):
    await callback.answer()
    await send_next_profile(callback.bot, callback.from_user.id, callback.message.chat.id)


@router.callback_query(F.data.startswith("like_"))
async def like_profile(callback: CallbackQuery):
    target_id = int(callback.data.split("_", 1)[1])
    is_new = await db.add_like(callback.from_user.id, target_id)
    await callback.answer("❤️ Yoqtirildi!" if is_new else "Siz allaqachon yoqtirgansiz")

    if is_new:
        liker = await db.get_user(callback.from_user.id)
        if liker:
            caption = f"❤️ <b>{liker['name']}</b> sizni yoqtirdi!\n\n" + build_search_caption(liker)
            try:
                await callback.bot.send_photo(
                    target_id,
                    photo=liker["photo"],
                    caption=caption,
                    reply_markup=profile_card_kb(callback.from_user.id),
                )
            except Exception:
                pass

    await send_next_profile(callback.bot, callback.from_user.id, callback.message.chat.id)


@router.callback_query(F.data.startswith("write_"))
async def write_to_profile(callback: CallbackQuery):
    target_id = int(callback.data.split("_", 1)[1])
    target = await db.get_user(target_id)
    if not target or not target.get("name"):
        await callback.answer("Foydalanuvchi topilmadi", show_alert=True)
        return

    await db.set_active_chat(callback.from_user.id, target_id)
    await callback.answer()
    await callback.message.answer(
        f"✍️ Endi <b>{target['name']}</b>ga xabar yozishingiz mumkin.\n"
        "Yuborgan xabaringiz bot orqali unga yetkaziladi.\n\n"
        "Suhbatni tugatish uchun /tugat buyrug'ini yuboring."
    )
