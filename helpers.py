# -*- coding: utf-8 -*-
"""Umumiy yordamchi funksiyalar."""

GENDER_EMOJI = {"Erkak": "👨", "Ayol": "👩"}


def build_profile_caption(user: dict, show_id: bool = False) -> str:
    """Anketa ma'lumotlaridan chiroyli caption matn yasaydi."""
    gender = user.get("gender") or "-"
    emoji = GENDER_EMOJI.get(gender, "⚧")
    text = (
        f"👤 <b>Ism:</b> {user.get('name', '-')}\n"
        f"🎂 <b>Yosh:</b> {user.get('age', '-')}\n"
        f"{emoji} <b>Jins:</b> {gender}\n"
        f"📍 <b>Viloyat:</b> {user.get('region', '-')}\n"
        f"📝 <b>O'zi haqida:</b> {user.get('bio', '-')}"
    )
    if show_id:
        text += f"\n\n🆔 ID: {user.get('telegram_id')}"
    return text


def build_search_caption(user: dict) -> str:
    """Qidiruvda ko'rsatiladigan anketa - faqat ism, yosh, tarif (rasm alohida)."""
    return (
        f"👤 <b>{user.get('name', '-')}</b>, {user.get('age', '-')} yosh\n\n"
        f"📝 {user.get('bio', '-')}"
    )


STATUS_LABELS = {
    "none": "Anketa to'ldirilmagan",
    "pending": "⏳ Ko'rib chiqilmoqda",
    "approved": "✅ Tasdiqlangan",
    "rejected": "❌ Rad etilgan",
}
