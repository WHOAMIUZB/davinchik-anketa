# -*- coding: utf-8 -*-
from aiogram.fsm.state import State, StatesGroup


class ProfileForm(StatesGroup):
    name = State()
    photo = State()
    age = State()
    gender = State()
    region = State()
    bio = State()
    confirm = State()


class AdminBroadcast(StatesGroup):
    waiting_post = State()
