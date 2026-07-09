"""
Rigpix extension for qrm
---
Copyright (C) 2026 jaytotheay

SPDX-License-Identifier: LiLiQ-Rplus-1.1
"""

import aiohttp
from discord import IntegrationType, ApplicationContext, Embed, Option
from discord.ext import commands

from urllib.parse import urljoin
from typing import Union
import re
from bs4 import BeautifulSoup

import common as cmn

class RigpixCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.radios = cmn.BrandsGroup(cmn.paths.resources / "radios.1.json")
        self.session = aiohttp.ClientSession(connector=bot.qrm.connector)

    # region rigpix

    @commands.slash_command(
        name="rigpix",
        category=cmn.Cats.REF,
        integration_types={IntegrationType.guild_install, IntegrationType.user_install},
    )
    async def _rigpix_slash(self, ctx: ApplicationContext, brand: str = "", model: str = ""):
        """Looks up a equipment by make & model on RigPix and returns its specifications."""
        embed = await self._rigpix_core(ctx, brand, model)
        await ctx.send_response(embed=embed)

    @commands.command(
        name="rigpix", aliases=["equipment", "gear", "radio"], category=cmn.Cats.REF
    )
    async def _rigpix_prefix(self, ctx: commands.Context, brand: str = "", model: str = ""):
        """Looks up equipment by make & model on RigPix and returns its specifications."""
        embed = await self._rigpix_core(ctx, brand, model)
        await ctx.send(embed=embed)

    async def _rigpix_core(self, ctx: Union[ApplicationContext, commands.Context], brand: str = "", model: str = "") -> Embed:
        """Core logic for the rigpix command."""
        # slugify-but-not-really the brand and model to match the keys in the radios dict
        pattern = re.compile('[\\W_]+', re.UNICODE)
        brand = re.sub(pattern, '', brand.lower())
        model = re.sub(pattern, '', model.lower())

        model_obj = self.radios.get(brand, {}).get(model)
        if model_obj:
            model_name = model_obj[0]
            model_link = model_obj[1]
        else:
            embed = Embed()
            embed = cmn.embed_factory(ctx)
            embed.title = "Failed to find RigPix entry"
            embed.description = (
                f"Could not find a RigPix entry for {brand} {model}."
            )
            return embed

        async with self.session.get(model_link) as resp:
                if resp.status != 200:
                    raise cmn.BotHTTPError(resp)
                resp_body = await resp.read()
                soup = BeautifulSoup(resp_body, 'html.parser')
                for br in soup.find_all('br'):
                    br.replace_with('\n')

                images = soup.find_all('img')
                image, image_url = None, None
                if len(images) > 4:
                    image = str(images[4])
                    image_url = urljoin(model_link, image[image.find("src=") + 5:image.find('"/>')])

                specification_table = soup.find_all('table')[3]
                rows = specification_table.find_all('tr')

                table_dict = dict()
                for row in rows:
                    columns = row.find_all('td')
                    table_dict[columns[0].text if 0 < len(columns) else ''] = columns[1].text if 1 < len(columns) else ''

                frequency_range = table_dict.get('Frequency range:')
                modes = table_dict.get('Mode:')
                power_consumption = table_dict.get('Current drain / power consumption:')
                dimensions = table_dict.get('Dimensions (W*H*D):', '').replace("*", "\\*")
                weight = table_dict.get('Weight:')
                rf_power_output = table_dict.get('RF output power:')
                manufactured = table_dict.get('Manufactured:')

                return create_embed(
                    ctx,
                    model_name=model_name,
                    model_link=model_link,
                    image_url=image_url,
                    frequency_range=frequency_range,
                    modes=modes,
                    power_consumption=power_consumption,
                    dimensions=dimensions,
                    weight=weight,
                    rf_power_output=rf_power_output,
                    manufactured=manufactured
                )

    # endregion

def create_embed(
    ctx: Union[ApplicationContext, commands.Context],
    model_name: str | None,
    model_link: str | None,
    image_url: str | None,
    frequency_range: str | None,
    modes: str | None,
    power_consumption: str | None,
    dimensions: str | None,
    weight: str | None,
    rf_power_output: str | None,
    manufactured: str | None
) -> Embed:
    """Creates an embed for the model and its metadata."""
    embed = cmn.embed_factory(ctx)
    embed.title = f"RigPix Data for {model_name}"
    embed.colour = cmn.colours.good
    embed.url = model_link
    embed.thumbnail = image_url
    embed.add_field(name="Frequency Range", value=frequency_range, inline=True)
    embed.add_field(name="Mode", value=modes, inline=True)
    embed.add_field(name="Power Consumption", value=power_consumption, inline=True)
    embed.add_field(name="Dimensions", value=dimensions, inline=True)
    embed.add_field(name="Weight", value=weight, inline=True)
    embed.add_field(name="Manufactured", value=manufactured, inline=True)
    embed.add_field(name="RF Power Output", value=rf_power_output, inline=True)

    return embed


def setup(bot: commands.Bot):
    bot.add_cog(RigpixCog(bot))
