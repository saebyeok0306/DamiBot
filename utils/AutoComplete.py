from discord import Interaction, app_commands
from sqlalchemy import select, distinct

from app import DamiBot
from db import SessionContext
from db.model.Music import Music


async def autocomplete_title(action: Interaction[DamiBot], current: str):
    with SessionContext() as session:
        stmt = select(distinct(Music.music_name))
        names = session.execute(stmt).scalars().all()
        return [
            app_commands.Choice(name=n, value=n)
            for n in names if current.lower() in n.lower()
        ][:25]  # 슬래시 명령어 자동완성은 최대 25개만 허용

async def autocomplete_dlc(action: Interaction[DamiBot], current: str):
    with SessionContext() as session:
        # all_dlc = session.query(DLC).all()
        # names = [dlc.dlc_name for dlc in all_dlc]

        stmt = select(distinct(Music.music_dlc))
        names = session.execute(stmt).scalars().all()
        return [
            app_commands.Choice(name=n, value=n)
            for n in names if current.lower() in n.lower()
        ][:25]  # 슬래시 명령어 자동완성은 최대 25개만 허용