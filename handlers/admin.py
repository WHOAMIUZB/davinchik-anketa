# -*- coding: utf-8 -*-
import asyncio

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile

import database as db
from config import ADMIN_ID
from states import AdminBroadcast
from keyboards import admin_panel_kb
from utils.excel_export import export_users_excel

router = Router(name="admin")


def _is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not _is_admin(message.from_user.id):
        return
    await message.answer("🛠 <b>Admin panel</b>\n\nKerakli bo'limni tanlang:", reply_markup=admin_panel_kb())


@router.callback_query(F.data == "admin_stats")
async def admin_stats_cb(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        return await callback.answer()
    stats = await db.get_stats()
    text = (
        "📊 <b>Bot statistikasi</b>\n\n"
        f"👥 Jami foydalanuvchilar (/start bosganlar): {stats['total']}\n"
        f"✅ Tasdiqlangan anketalar: {stats['approved']}\n"
        f"⏳ Kutilayotgan anketalar: {stats['pending']}\n"
        f"❌ Rad etilgan anketalar: {stats['rejected']}\n"
        f"❤️ Jami yoqtirishlar: {stats['likes']}\n"
        f"✉️ Jami yuborilgan xabarlar: {stats['messages']}"
    )
    await callback.message.answer(text)
    await callback.answer()


@router.callback_query(F.data == "admin_excel")
async def admin_excel_cb(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        return await callback.answer()
    await callback.answer("Tayyorlanmoqda...")
    path = await export_users_excel()
    await callback.message.answer_document(
        FSInputFile(path, filename="foydalanuvchilar.xlsx"),
        caption="📥 Foydalanuvchilar ro'yxati (Excel)",
    )


@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_cb(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        return await callback.answer()
    await callback.answer()
    await callback.message.answer(
        "📢 Yubormoqchi bo'lgan reklama postini yuboring "
        "(matn, rasm, video — caption bilan bo'lishi mumkin).\n\n"
        "Bekor qilish uchun /bekor buyrug'ini yuboring."
    )
    await state.set_state(AdminBroadcast.waiting_post)


@router.message(Command("bekor"), StateFilter(AdminBroadcast.waiting_post))
async def cancel_broadcast(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Bekor qilindi.")


@router.message(AdminBroadcast.waiting_post)
async def do_broadcast(message: Message, state: FSMContext):
    if not _is_admin(message.from_user.id):
        return
    await state.clear()
    user_ids = await db.get_all_user_ids()
    status_msg = await message.answer(f"⏳ Yuborilmoqda... (0/{len(user_ids)})")

    sent, failed = 0, 0
    for uid in user_ids:
        if uid == message.from_user.id:
            continue
        try:
            await message.copy_to(chat_id=uid)
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)

    await status_msg.edit_text(f"✅ Reklama yuborildi: {sent} ta\n❌ Yuborilmadi: {failed} ta")


@router.callback_query(F.data.startswith("approve_"))
async def approve_profile(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        return await callback.answer()
    uid = int(callback.data.split("_", 1)[1])
    await db.set_status(uid, "approved")
    try:
        await callback.bot.send_message(
            uid, "✅ Anketangiz tasdiqlandi!\nEndi siz qidiruvda boshqa foydalanuvchilarga ko'rinasiz. 🎉"
        )
    except Exception:
        pass
    try:
        await callback.message.edit_caption(
            caption=(callback.message.caption or "") + "\n\n✅ <b>TASDIQLANDI</b>"
        )
    except Exception:
        pass
    await callback.answer("Tasdiqlandi ✅")


@router.callback_query(F.data.startswith("reject_"))
async def reject_profile(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        return await callback.answer()
    uid = int(callback.data.split("_", 1)[1])
    await db.set_status(uid, "rejected")
    try:
        await callback.bot.send_message(
            uid,
            "❌ Anketangiz rad etildi.\n"
            "Iltimos, «👤 Mening anketam» bo'limidagi «✏️ Tahrirlash» tugmasi orqali "
            "yangi anketa to'ldiring.",
        )
    except Exception:
        pass
    try:
        await callback.message.edit_caption(
            caption=(callback.message.caption or "") + "\n\n❌ <b>RAD ETILDI</b>"
        )
    except Exception:
        pass
    await callback.answer("Rad etildi ❌")
