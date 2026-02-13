"""
Contest Calendar extension for qrm
---
Copyright (C) 2021-2023 classabbyamp, 0x5c

SPDX-License-Identifier: LiLiQ-Rplus-1.1
"""

import discord.ext.commands as commands
from discord import IntegrationType, Embed, ApplicationContext

import common as cmn


class ContestCalendarCog(commands.Cog):

    @commands.slash_command(
        name="contests",
        category=cmn.Cats.LOOKUP,
        integration_types={IntegrationType.guild_install, IntegrationType.user_install},
    )
    async def _contests(self, ctx: ApplicationContext, private: bool = False):
        embed = Embed()
        embed = cmn.embed_factory(ctx)
        embed.title = "Contest Calendar"
        embed.description = (
            "*We are currently rewriting the old, Chrome-based `contests` command. In the meantime, "
            "use [the website](https://www.contestcalendar.com/weeklycont.php).*"
        )
        embed.colour = cmn.colours.good
        await ctx.send_response(embed=embed, ephemeral=private)


def setup(bot: commands.Bot):
    bot.add_cog(ContestCalendarCog(bot))
