# Copyright (C) 2024, Kurzgesagt Community Devs
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

"""
This module contains the configuration settings for guild level items such as roles, channels and emojis.
"""

import discord


class Reference:
    botownerlist = [
        1346834364415217798,  # Luna
        196954731384537088,  # Koyomi
    ]
    botdevlist = [
        196954731384537088,  # Koyomi
        1346834364415217798,  # Luna
    ]
    guild = 1343332955120205945
    mainbot = 1352301326951776256
    bannsystembot = 1352306834580701336

    class Roles:

        moderator = 1343332955308818539
        administrator = 1344631002726793296
        kgsofficial = 1344632012782178365
        trainee_mod = 1343332955308818537
        robobird = 1343332955120205946
        stealthbot = 1343332955308818542

        nitro_bird = 1344017022517903462
        contributor = 1343332955271205021

        galacduck = 1344003570428674078  # GalacDuck
        legendary_duck = 1344003451855573052  # LegendDuck
        super_duck = 1344003393294696509  # SuperDuck
        duck = 1344003336038387875  # Duck
        smol_duck = 1344003294183292950  # Smol Duck
        duckling = 1344003239431110687  # Duckling
        duck_hatchling = 1344003165053522021  # Duck Hatchling
        duck_egg = 1344003080441827469  # Duck Egg

        english = 1343332955262550105

        @staticmethod
        def admin_and_above():
            return [Reference.Roles.administrator, Reference.Roles.kgsofficial]

        @staticmethod
        def moderator_and_above():
            return [
                Reference.Roles.trainee_mod,
                Reference.Roles.moderator,
                Reference.Roles.administrator,
                Reference.Roles.kgsofficial,
            ]

        @staticmethod
        def patreon():
            return [Reference.Roles.patreon_1, Reference.Roles.patreon_2, Reference.Roles.patreon_3]

    class Categories:
        moderation = 1343332955656949872
        server_logs = 1343332957288398965

    class Channels:
        general = 1343332956634353759
        bot_commands = 1344695570723241994
        bot_tests = 1344701667647553668
        new_members = 1343332956634353759
        humanities = 1162034723758034964
        server_moments = 960927545639972994
        mod_chat = 1092578562608988290
        intro_channel = 1343332956634353766

        class Logging:
            mod_actions = 1343332957594849350
            automod_actions = 1343332957594849350
            message_actions = 1343332957288398967
            member_actions = 1343332957594849351
            dev = 1343332957288398966
            misc_actions = 1343332957594849351
            bannsystem = 1343332957288398966

    class Emoji:
        kgsYes = 1345292416021823488
        kgsNo = 1352312901117022258

        class PartialString:
            kgsYes = "<:BlobYes:1345292416021823488>"
            kgsNo = "<:blobno:1352312901117022258>"
            kgsStop = "<:Stop_Sign:1352313646814068856>"
            kgsWhoAsked = "<:sorry_who_asked:1352314101405192243> "

        @staticmethod
        async def fetch(client: discord.Client, ref: int) -> discord.Emoji | None:
            """
            When given a client object and an emoji id, returns a discord.Emoji
            """

            if em := client.get_emoji(ref) is not None:
                return em  # type: ignore
            return None


class GiveawayBias:
    roles = [
        {
            "id": Reference.Roles.galacduck,
            "bias": 11,
        },
        {
            "id": Reference.Roles.legendary_duck,
            "bias": 7,
        },
        {
            "id": Reference.Roles.super_duck,
            "bias": 4,
        },
        {
            "id": Reference.Roles.duck,
            "bias": 3,
        },
        {
            "id": Reference.Roles.smol_duck,
            "bias": 2,
        },
    ]
    default = 1


class ExclusiveColors:
    """
    Contains a list of selectable colored roles that can be provided to a user if they have the role that unlocks the color.
    """

    exclusive_colors = {
        "Patreon Orange": {
            "id": 976158045639946300,
            "unlockers": [Reference.Roles.patreon_1, Reference.Roles.patreon_2, Reference.Roles.patreon_3],
        },
        "Patreon Green": {
            "id": 976158006616137748,
            "unlockers": [Reference.Roles.patreon_2, Reference.Roles.patreon_3],
        },
        "Patreon Blue": {"id": 976157262718582784, "unlockers": [Reference.Roles.patreon_3]},
        "Nitro Pink": {"id": 976157185971204157, "unlockers": [Reference.Roles.nitro_bird]},
        "Contributor Gold": {"id": 976176253826654329, "unlockers": [Reference.Roles.contributor]},
    }
