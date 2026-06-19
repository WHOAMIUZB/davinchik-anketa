# -*- coding: utf-8 -*-
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

import database as db
from states import ProfileForm
from keyboards import main_menu_kb
from helpers import STATUS_LABELS

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await db.create_user_if_not_exists(message.from_user.id)
    user = await db.get_user(message.from_user.id)

    status = user["status"] if user else "none"

    if status == "none" or not user.get("name"):
        await message.answer(
            "Salom! 👋 <b>Anketa-Bot</b>ga xush kelibsiz!\n\n"
            "Bu yerda siz o'zingiz haqingizda anketa to'ldirib, boshqalarning "
            "anketalarini ko'rib, fikr bildira olasiz (LeoMatch uslubida).\n\n"
            "Avval anketangizni to'ldiramiz.\n\n"
            "✏️ <b>Ismingizni</b> kiriting:",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.set_state(ProfileForm.name)
        return

    extra = ""
    if status == "pending":
        extra = "\n\n⏳ Anketangiz hozircha admin tomonidan ko'rib chiqilmoqda."
    elif status == "rejected":
        extra = (
            "\n\n❌ Avvalgi anketangiz rad etilgan. "
            "Yangi anketa to'ldirish uchun «👤 Mening anketam» bo'limidagi "
            "«✏️ Tahrirlash» tugmasidan foydalaning."
        )

    await message.answer(
        f"Salom, {message.from_user.first_name}! 👋{extra}\n\n"
        f"📌 Anketa holati: {STATUS_LABELS.get(status, status)}\n\n"
        "Quyidagi menyudan birini tanlang:",
        reply_markup=main_menu_kb(),
    )
