from typing import Literal

from arclet.alconna import Alconna, Args
from loguru import logger
from nonebot.plugin import get_plugin_config
from nonebot_plugin_alconna import on_alconna, At, Match
from nonebot_plugin_saa import MessageFactory
from pydglab_ws import Channel

from ..client_manager import client_manager
from ..config import Config
from ..model import custom_pulse_data

__all__ = ["append_pulse", "reset_pulse"]

config = get_plugin_config(Config)


async def pulse_control(
        mode: Literal["reset", "append"],
        at: Match[At],
        pulse_name: Match[float]
):
    if not at.available:
        await MessageFactory(
            config.dg_lab_play.reply_text.please_at_target
        ).finish(at_sender=True)
    elif pulse_name.available:
        if pulse_data := custom_pulse_data.root.get(pulse_name.result):
            target_user_id = at.result.target
            if play_client := client_manager.user_id_to_client.get(target_user_id):
                if mode == "reset":
                    await play_client.setup_pulse_job(pulse_data, Channel.A, Channel.B)
                elif mode == "append":
                    await play_client.setup_pulse_job(play_client.pulse_data + pulse_data, Channel.A, Channel.B)
                else:
                    logger.error("strength_control - mode 参数不正确")
                    return
                await MessageFactory(
                    config.dg_lab_play.reply_text.successfully_set_pulse
                ).finish(at_sender=True)
            else:
                await MessageFactory(
                    config.dg_lab_play.reply_text.invalid_target
                ).finish(at_sender=True)
        else:
            await MessageFactory(
                config.dg_lab_play.reply_text.invalid_pulse_param
            ).finish(at_sender=True)
    else:
        await MessageFactory(
            config.dg_lab_play.reply_text.invalid_pulse_param
        ).finish(at_sender=True)


append_pulse = on_alconna(
    Alconna(
        config.dg_lab_play.command_text.append_pulse,
        Args["at?", At],
        Args["pulse_name?", str]
    ),
    block=True
)


@append_pulse.handle()
async def handle_append_pulse(at: Match[At], pulse_name: Match[float]):
    await pulse_control("append", at, pulse_name)


reset_pulse = on_alconna(
    Alconna(
        config.dg_lab_play.command_text.reset_pulse,
        Args["at?", At],
        Args["pulse_name?", str]
    ),
    block=True
)


@reset_pulse.handle()
async def handle_reset_pulse(at: Match[At], pulse_name: Match[float]):
    await pulse_control("reset", at, pulse_name)
