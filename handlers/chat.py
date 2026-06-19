# -*- coding: utf-8 -*-
from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import database as db
from keyboards import write_back_kb

router = Router(name="chat")


@router.message(Command("tugat"))
async def end_chat(message: Message):
    partner_id = await db.get_active_chat(message.from_user.id)
    if not partner_id:
        await message.answer("Sizda hozir faol suhbat yo'q.")
        return
    await db.clear_active_chat(message.from_user.id)
    await message.answer("✅ Suhbat tugatildi.")


@router.message(StateFilter(None))
async def relay_message(message: Message, state: FSMContext):
    partner_id = await db.get_active_chat(message.from_user.id)
    if not partner_id:
        # Foydalanuvchi hech qanday faol holatda emas va chatda emas
        await message.answer(
            "ℹ️ Iltimos, asosiy menyudagi tugmalardan foydalaning yoki /start bosing."
        )
        return

    sender = await db.get_user(message.from_user.id)
    sender_name = sender["name"] if sender and sender.get("name") else message.from_user.first_name

    try:
        await message.bot.send_message(partner_id, f"✉️ <b>{sender_name}</b> dan yangi xabar:")
        await message.copy_to(chat_id=partner_id, reply_markup=write_back_kb(message.from_user.id))
    except Exception:
        await message.answer(
            "⚠️ Xabaringiz yetib bormadi. Foydalanuvchi botni bloklagan bo'lishi mumkin."
        )
        return

    await db.add_message(message.from_user.id, partner_id, message.text or "[media]")
    await message.answer("✅ Xabaringiz yuborildi.")
