# -*- coding: utf-8 -*-
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

import database as db
from config import MIN_AGE, MAX_AGE, MAX_NAME_LEN, MAX_BIO_LEN
from states import ProfileForm
from keyboards import (
    main_menu_kb, gender_kb, region_kb, confirm_kb, my_profile_kb,
    delete_confirm_kb, BTN_MY_PROFILE,
)
from helpers import build_profile_caption, STATUS_LABELS
from utils.regions import REGIONS
from services import send_profile_to_admin

router = Router(name="profile")


# ---------------------------------------------------------------------------
# ANKETA TO'LDIRISH WIZARD
# ---------------------------------------------------------------------------

@router.message(ProfileForm.name)
async def process_name(message: Message, state: FSMContext):
    if not message.text or len(message.text.strip()) < 2:
        await message.answer("Iltimos, to'g'ri ism kiriting (kamida 2 ta harf):")
        return
    await state.update_data(name=message.text.strip()[:MAX_NAME_LEN])
    await message.answer("📷 Endi anketangiz uchun bitta <b>rasm (foto)</b> yuboring:")
    await state.set_state(ProfileForm.photo)


@router.message(ProfileForm.photo, F.photo)
async def process_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo=photo_id)
    await message.answer(f"🎂 Yoshingizni kiriting (raqamda, {MIN_AGE}-{MAX_AGE}):")
    await state.set_state(ProfileForm.age)


@router.message(ProfileForm.photo)
async def process_photo_invalid(message: Message, state: FSMContext):
    await message.answer("Iltimos, faqat 📷 rasm (foto) ko'rinishida yuboring.")


@router.message(ProfileForm.age)
async def process_age(message: Message, state: FSMContext):
    if not message.text or not message.text.strip().isdigit():
        await message.answer("Iltimos, yoshingizni faqat raqamda kiriting:")
        return
    age = int(message.text.strip())
    if age < MIN_AGE or age > MAX_AGE:
        await message.answer(f"Yosh {MIN_AGE} dan {MAX_AGE} gacha bo'lishi kerak. Qaytadan kiriting:")
        return
    await state.update_data(age=age)
    await message.answer("⚧ Jinsingizni tanlang:", reply_markup=gender_kb())
    await state.set_state(ProfileForm.gender)


@router.callback_query(ProfileForm.gender, F.data.startswith("gender_"))
async def process_gender(callback: CallbackQuery, state: FSMContext):
    gender = callback.data.split("_", 1)[1]
    await state.update_data(gender=gender)
    await callback.message.edit_text("📍 Yashash viloyatingizni tanlang:", reply_markup=region_kb())
    await state.set_state(ProfileForm.region)
    await callback.answer()


@router.callback_query(ProfileForm.region, F.data.startswith("region_"))
async def process_region(callback: CallbackQuery, state: FSMContext):
    idx = int(callback.data.split("_", 1)[1])
    region = REGIONS[idx]
    await state.update_data(region=region)
    await callback.message.edit_text(
        f"📍 Viloyat: <b>{region}</b> ✅\n\n"
        "📝 O'zingiz haqingizda qisqacha ma'lumot (tarif) yozing:"
    )
    await state.set_state(ProfileForm.bio)
    await callback.answer()


@router.message(ProfileForm.bio)
async def process_bio(message: Message, state: FSMContext):
    if not message.text or len(message.text.strip()) < 5:
        await message.answer("Iltimos, kamida 5 ta belgidan iborat tarif yozing:")
        return
    await state.update_data(bio=message.text.strip()[:MAX_BIO_LEN])
    data = await state.get_data()

    caption = (
        "👀 <b>Anketangiz shunday ko'rinishda bo'ladi:</b>\n\n"
        + build_profile_caption(data)
    )
    await message.answer_photo(photo=data["photo"], caption=caption, reply_markup=confirm_kb())
    await state.set_state(ProfileForm.confirm)


@router.callback_query(ProfileForm.confirm, F.data == "profile_restart")
async def restart_profile(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("✏️ Ismingizni qaytadan kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(ProfileForm.name)
    await callback.answer()


@router.callback_query(ProfileForm.confirm, F.data == "profile_confirm")
async def confirm_profile(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback.from_user.id

    await db.save_profile(
        telegram_id=user_id,
        name=data["name"],
        photo=data["photo"],
        age=data["age"],
        gender=data["gender"],
        region=data["region"],
        bio=data["bio"],
        status="pending",
    )
    await state.clear()

    try:
        await callback.message.edit_caption(
            caption=(callback.message.caption or "") + "\n\n⏳ Yuborildi, admin javobini kutamiz."
        )
    except Exception:
        pass

    await callback.answer("Yuborildi! ✅")
    await callback.message.answer(
        "✅ Anketangiz qabul qilindi va admin ko'rib chiqishi uchun yuborildi.\n"
        "⏳ Iltimos, kuting. Bu orada boshqalarning anketalarini qidirishingiz mumkin!",
        reply_markup=main_menu_kb(),
    )

    await send_profile_to_admin(callback.bot, user_id)


# ---------------------------------------------------------------------------
# MENING ANKETAM
# ---------------------------------------------------------------------------

@router.message(F.text == BTN_MY_PROFILE)
async def my_profile_message(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user or not user.get("name"):
        await message.answer("🙁 Sizda hali anketa yo'q. Anketa to'ldirish uchun /start bosing.")
        return
    likes_count = await db.get_likes_count(message.from_user.id)
    status_text = STATUS_LABELS.get(user["status"], user["status"])
    caption = (
        build_profile_caption(user)
        + f"\n\n❤️ Yoqtirishlar soni: <b>{likes_count}</b>"
        + f"\n📌 Holat: {status_text}"
    )
    await message.answer_photo(photo=user["photo"], caption=caption, reply_markup=my_profile_kb())


@router.callback_query(F.data == "myprofile")
async def my_profile_callback(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    await callback.answer()
    if not user or not user.get("name"):
        await callback.message.answer("🙁 Sizda hali anketa yo'q. Anketa to'ldirish uchun /start bosing.")
        return
    likes_count = await db.get_likes_count(callback.from_user.id)
    status_text = STATUS_LABELS.get(user["status"], user["status"])
    caption = (
        build_profile_caption(user)
        + f"\n\n❤️ Yoqtirishlar soni: <b>{likes_count}</b>"
        + f"\n📌 Holat: {status_text}"
    )
    await callback.message.answer_photo(photo=user["photo"], caption=caption, reply_markup=my_profile_kb())


@router.callback_query(F.data == "my_likes")
async def my_likes_cb(callback: CallbackQuery):
    likes = await db.get_likes_received(callback.from_user.id)
    await callback.answer()
    if not likes:
        await callback.message.answer("😔 Hozircha hech kim anketangizni yoqtirmagan.")
        return
    text = "❤️ <b>Sizni yoqtirganlar:</b>\n\n"
    for i, u in enumerate(likes, start=1):
        text += f"{i}. {u['name']}, {u['age']} yosh\n"
    await callback.message.answer(text)


@router.callback_query(F.data == "my_writers")
async def my_writers_cb(callback: CallbackQuery):
    writers = await db.get_writers(callback.from_user.id)
    await callback.answer()
    if not writers:
        await callback.message.answer("😔 Hozircha sizga hech kim yozmagan.")
        return
    text = "✉️ <b>Sizga yozganlar:</b>\n\n"
    for i, w in enumerate(writers, start=1):
        text += f"{i}. {w['name']}\n"
    await callback.message.answer(text)


@router.callback_query(F.data == "edit_profile")
async def edit_profile_cb(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await callback.message.answer(
        "✏️ Anketangizni to'liq qaytadan to'ldiramiz.\n\nIsmingizni kiriting:",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(ProfileForm.name)


@router.callback_query(F.data == "delete_profile")
async def delete_profile_cb(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "⚠️ Anketangizni butunlay o'chirishni tasdiqlaysizmi?",
        reply_markup=delete_confirm_kb(),
    )


@router.callback_query(F.data == "delete_confirm_yes")
async def delete_confirm_yes_cb(callback: CallbackQuery):
    await db.delete_profile(callback.from_user.id)
    await callback.answer("O'chirildi")
    await callback.message.answer(
        "🗑 Anketangiz butunlay o'chirildi.\nYangi anketa yaratish uchun /start bosing.",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.callback_query(F.data == "delete_confirm_no")
async def delete_confirm_no_cb(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("Bekor qilindi. Anketangiz saqlanib qoldi.")
