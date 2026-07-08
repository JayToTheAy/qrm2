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
from bs4 import BeautifulSoup

import common as cmn

import data.options as opt

class RigpixCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.radios = cmn.BrandsGroup(cmn.paths.resources / "radios.1.json")
        self.session = aiohttp.ClientSession(connector=bot.qrm.connector)

    # region radio

    @commands.slash_command(
        name="radio",
        category=cmn.Cats.REF,
        integration_types={IntegrationType.guild_install, IntegrationType.user_install},
    )
    async def _radio_slash(self, ctx: ApplicationContext, brand: str = "", radio: str = ""):
        """Gets the frequency allocations chart for a given country."""
        embed = await self._radio_core(ctx, brand, radio)
        await ctx.send_response(
            embed=embed
        )

    @commands.command(
        name="radio", aliases=["equipment", "gear"], category=cmn.Cats.REF
    )
    async def _radio_prefix(self, ctx: commands.Context, brand: str = "", radio: str = ""):
        """Looks up a radio make & model on RigPix and returns its specifications."""
        embed = await self._radio_core(ctx, brand, radio)
        await ctx.send(embed=embed)

    async def _radio_core(self, ctx: Union[ApplicationContext, commands.Context], brand: str = "", radio: str = "") -> Embed:
        radio_link = self.radios[brand.lower()][radio]

        async with self.session.get(radio_link) as resp:
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
                    image_url = urljoin(radio_link, image[image.find("src=") + 5:image.find('"/>')])

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

                # embed
                
                embed = cmn.embed_factory(ctx)
                embed.title = f"RigPix Data for {radio}"
                embed.colour = cmn.colours.good
                embed.url = radio_link
                embed.thumbnail = image_url
                embed.add_field(name="Frequency Range", value=frequency_range, inline=True)
                embed.add_field(name="Mode", value=modes, inline=True)
                embed.add_field(name="Power Consumption", value=power_consumption, inline=True)
                embed.add_field(name="Dimensions", value=dimensions, inline=True)
                embed.add_field(name="Weight", value=weight, inline=True)
                embed.add_field(name="RF Power Output", value=rf_power_output, inline=True)

                return embed

    # endregion

def create_embed(
    ctx: Union[ApplicationContext, commands.Context],
    not_found_name: str,
    db: cmn.ImagesGroup,
    img_id: str,
) -> Embed:
    """Creates an embed for the image and its metadata, or list available images in the group."""
    img_id = img_id.lower()
    embed = cmn.embed_factory(ctx)
    if img_id not in db:
        desc = "Possible arguments are:\n"
        for key, img in db.items():
            desc += f"`{key}`: {img.name}{('  ' + img.emoji if img.emoji else '')}\n"
        embed.title = f"{not_found_name} Not Found!"
        embed.description = desc
        embed.colour = cmn.colours.bad
        return embed
    metadata = db[img_id]
    if metadata.description:
        embed.description = metadata.description
    if metadata.source:
        embed.add_field(name="Source", value=metadata.source)
    embed.title = metadata.long_name + ("  " + metadata.emoji if metadata.emoji else "")
    embed.colour = cmn.colours.good
    embed.set_image(url=opt.resources_url + metadata.filename)
    return embed


def setup(bot: commands.Bot):
    bot.add_cog(RigpixCog(bot))
