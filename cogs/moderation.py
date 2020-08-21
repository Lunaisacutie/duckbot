import json
import os
from time import sleep
import re
import logging

import typing
import sys
sys.path.append('..')
import helper
import custom_converters

import discord
from discord.ext import commands

from hastebin_client.utils import *
import asyncio

# from custom_converters import *
class Moderation(commands.Cog):
    def __init__(self, bot):
        self.logger = logging.getLogger('Moderation')
        self.bot = bot

        config_file = open(os.path.join(os.path.dirname(__file__), os.pardir, 'config.json'), 'r')
        self.config_json = json.loads(config_file.read())

        self.logging_channel = self.config_json['logging']['logging-channel']
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info('loaded Moderation')
    
    
    @commands.command(aliases=['purge', 'prune'])
    @commands.has_guild_permissions(manage_messages=True)
    async def clean(self, ctx, msg_count: int = None, member: commands.Greedy[discord.Member] = None, channel: discord.TextChannel = None):
        """ Clean messages. \nUsage: clean number_of_messages <@member(s)> <#channel>"""

        if msg_count is None:
            await ctx.send(f'**Usage:** `clean number_of_messages <@member(s)> <#channel>`')
        
        elif msg_count > 200:
            await ctx.send(f'Provided number is too big. (Max limit 200)')

        elif msg_count == 0:
            await ctx.channel.purge(limit=1)
        
        if channel is None:
            channel = ctx.channel

        if member is None:
            if msg_count == 1:
                msg = await channel.purge(limit=2)

                logging_channel = discord.utils.get(ctx.guild.channels, id=self.logging_channel)

                embed = helper.create_embed(author=ctx.author, users=None, action='1 message deleted', reason="None", extra=f'Message Content: { msg[-1].content } \nSender: { msg[-1].author } \nTime: { msg[-1].created_at } \nID: { msg[-1].id } \nChannel: #{ channel }', color=discord.Color.green())
                
                await logging_channel.send(embed=embed)
                

            else:
                deleted_msgs = await channel.purge(limit=msg_count+1)

                try:
                    haste_data = "Author (ID)".ljust(70) + " | " + "Message Creation Time (UTC)".ljust(30) + " | " + "Content" + "\n\n"
                    for msg in deleted_msgs:

                        author = f'{ msg.author.name }#{ msg.author.discriminator } ({ msg.author.id })'.ljust(70)
                        time = f'{ msg.created_at }'.ljust(30)
                        content = f'{ msg.content }'
                        haste_data = haste_data + author + " | " + time + " | " + content + "\n"
                        
                    key = upload(haste_data)
                    cache_file_url = create_url(key) + ".txt"

                except ValueError as ve:
                    cache_file_url = str(ve)
                    self.logger.error(str(ve))

                except Exception as e:
                    cache_file_url = str(e)
                    self.logger.error(str(e))


                logging_channel = discord.utils.get(ctx.guild.channels, id=self.logging_channel)

                embed = helper.create_embed(author=ctx.author, users=None, action=f'{ msg_count+1 } messages deleted', reason="None", extra=cache_file_url + f'\nChannel: #{ channel }', color=discord.Color.green())

                await logging_channel.send(embed=embed)

                m = await ctx.send(f'Deleted { msg_count+1 } messages.')
                sleep(3)
                await m.delete()

        else:

            deleted_msgs = []
            count = msg_count 
            async for m in channel.history(limit=200, oldest_first=False):
                if ctx.message.id == m.id:
                    continue

                deleted_msgs.append(m)
                for mem in member:
                    if m.author.id == mem.id:
                        count = count - 1
                        await m.delete()
                if count <= 0:
                    break


            try:
                haste_data = "Author (ID)".ljust(70) + " | " + "Message Creation Time (UTC)".ljust(30) + " | " + "Content" + "\n\n"
                for msg in deleted_msgs:

                    author = f'{ msg.author.name }#{ msg.author.discriminator } ({ msg.author.id })'.ljust(70)
                    time = f'{ msg.created_at }'.ljust(30)
                    content = f'{ msg.content }'
                    haste_data = haste_data + author + " | " + time + " | " + content + "\n"
                    
                key = upload(haste_data)
                cache_file_url = create_url(key) + ".txt"

            except ValueError as ve:
                cache_file_url = str(ve)
                self.logger.error(str(ve))

            except Exception as e:
                cache_file_url = str(e)
                self.logger.error(str(e))


            logging_channel = discord.utils.get(ctx.guild.channels, id=self.logging_channel)

            embed = helper.create_embed(author=ctx.author, users=member, action=f'{ msg_count } messages deleted', reason="None", extra=cache_file_url + f'\nChannel: #{ channel }', color=discord.Color.green())


            await logging_channel.send(embed=embed)

            await ctx.message.delete()

            m = await ctx.send(f'Deleted { msg_count } messages.')
            sleep(3)
            await m.delete()



    @commands.command(aliases = ['yeet'])
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, *args):
        """ Ban a member.\nUsage: ban @member(s) <time> reason """

        tot_time = 0
        is_banned = False
        mem_id = []

        try:

            logging_channel = discord.utils.get(ctx.guild.channels, id=self.logging_channel)

            members, extra = custom_converters.get_members(ctx, *args)

            if members is None:
                return await ctx.send('Provide member(s) to ban.\n **Usage:** `ban @member(s) <time> reason`')

            tot_time, reason, time_str = helper.calc_time(extra)     

            if reason is None:
                return await ctx.send('Provide a reason for banning.\n **Usage:** `ban @member(s) <time> reason`')



            for m in members:
                mem_id.append(m.id)
                await m.ban(reason=reason)
                await ctx.send(f'Banned { m.name } for { time_str }.\nReason: { reason }')

            is_banned = True
            
            embed = helper.create_embed(author=ctx.author, users=members, action='Ban', extra=f'Ban Duration: { time_str } or { tot_time } seconds', reason=reason, color=discord.Color.dark_red())
            await logging_channel.send(embed=embed)

            helper.create_infraction(author=ctx.author, users=members, action='ban', reason=reason, time=tot_time)
               

        except Exception as e:
            self.logger.error(str(e))
            await ctx.send('Unable to ban member(s).')

        if is_banned:
            try:
                if tot_time != 0:
                    # TIMED
                    ids = helper.create_timed_action(users=members, action='ban', time=tot_time)
                    await asyncio.sleep(tot_time)
                    await self.unban(ctx=ctx, member_id=mem_id, reason=reason)
                    # TIMED
                    helper.delete_time_action(ids=ids)
            except Exception as e:
                self.logger.error(str(e))


    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    async def unban(self, ctx, member_id: commands.Greedy[int] = None, *, reason: str = None):
        """ Unban a member. \nUsage: unban member_id <reason> """
        try:
            if member_id is None:
                return await ctx.send('Provide member id(s).\n**Usage:** `unban member_id <reason>`')

            logging_channel = discord.utils.get(ctx.guild.channels,id=self.logging_channel)

            ban_list = await ctx.guild.bans()

            mem = []    # for listing members in embed

            for b in ban_list:
                if b.user.id in member_id:
                    mem.append(b.user)
                    if reason is None:
                        reason = b.reason

                    await ctx.guild.unban(b.user, reason=reason)
                    await ctx.send(f'Unbanned { b.user.name }.')
                    member_id.remove(b.user.id)

            for m in member_id:
                await ctx.send(f'Member with ID { m } has not been banned before.')

            embed = helper.create_embed(author=ctx.author, users=mem, action='Unban', reason=reason, color=discord.Color.dark_red())
            await logging_channel.send(embed=embed)
                    

        except Exception as e:
            self.logger.exception(str(e))


    @commands.command()
    @commands.has_permissions(kick_members=True)
    # async def kick(self,ctx,members: commands.Greedy[discord.Member],*,reason: str = None):
    async def kick(self, ctx, *args):
        """ Kick member(s).\nUsage: kick @member(s) reason """
        try:

            members, reason = custom_converters.get_members(ctx, *args)

            if reason is None:
                return await ctx.send('Provide a reason.\n**Usage:** `kick @member(s) reason`')

            if members is None:
                return await ctx.send('Provide member(s).\n**Usage:** `kick @member(s) reason`')

            reason = " ".join(reason)
            logging_channel = discord.utils.get(ctx.guild.channels, id=self.logging_channel)
            
            for i in members:
                await i.kick(reason=reason)
                await ctx.send(f'Kicked { i.name }.\nReason: { reason }')

            embed = helper.create_embed(author=ctx.author, users=members, action='Kick', reason=reason, color=discord.Color.red())
            await logging_channel.send(embed=embed)


            helper.create_infraction(author=ctx.author, users=members, action='kick', reason=reason)


        except Exception as e:
            self.logger.error(str(e))
            await ctx.send('Unable to kick member(s).')

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def mute(self, ctx, *args):
        """ Mute member(s). \nUsage: mute @member(s) <time> reason """

        tot_time = 0
        is_muted = False

        try:
            logging_channel = discord.utils.get(ctx.guild.channels,id=self.logging_channel)
            mute_role = discord.utils.get(ctx.guild.roles, id=self.config_json['roles']['mute-role']) 

            members, extra = custom_converters.get_members(ctx, *args)

            if members == None:
                return await ctx.send('Provide member(s) to mute.\n**Usage:** `mute @member(s) <time> reason`')


            tot_time, reason, time_str = helper.calc_time(extra)     

            if reason is None:
                return await ctx.send('Provide reason to mute.\n**Usage:** `mute @member(s) <time> reason`')

            
            for i in members:
                await i.add_roles(mute_role, reason=reason)
                await ctx.send(f'Muted { i.name } for { time_str }.\nReason: { reason }')

            is_muted = True

            embed = helper.create_embed(author=ctx.author, users=members, action='Mute', reason=reason, extra=f'Mute Duration: { time_str } or { tot_time } seconds' ,color=discord.Color.red())
            await logging_channel.send(embed=embed)

            helper.create_infraction(author=ctx.author, users=members, action='mute', reason=reason, time=time_str)
     

        except Exception as e:
            self.logger.error(str(e))
            await ctx.send('Unable to mute users.')

        if is_muted:
            try: 
                if tot_time != 0:
                    # TIMED
                    ids = helper.create_timed_action(users=members, action='mute', time=tot_time)
                    await asyncio.sleep(tot_time)
                    await self.unmute(ctx=ctx, members=members, reason=reason)
                    # TIMED
                    helper.delete_time_action(ids=ids)
            except Exception as e:
                self.logger.error(str(e))
            

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def unmute(self,ctx,members: commands.Greedy[discord.Member],*,reason: str = None):
        """ Unmute member(s). \nUsage: unmute @member(s) <reason> """

        try:
            if members == []:
                return await ctx.send('Provide members to unmute.\n**Usage:** `unmute @member(s) <reason>`')

            logging_channel = discord.utils.get(ctx.guild.channels, id=self.logging_channel)
            mute_role = discord.utils.get(ctx.guild.roles, id=self.config_json['roles']['mute-role'])
            for i in members:
                await i.remove_roles(mute_role, reason=reason)
                # TIMED
                helper.delete_time_actions_uid(u_id=i.id, action='mute')
                
                await ctx.send(f'Unmuted { i.name }.')


        except Exception as e:
            logging.error(str(e))
            await ctx.send('Unable to unmute users.')
        
        embed = helper.create_embed(author=ctx.author, users=members, action='Unmute', reason=reason, color=discord.Color.red())

        await logging_channel.send(embed=embed)
    


    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def role(self, ctx, member: discord.Member = None, *, role_name: str = None):
        """ Add/Remove a role to member. \nUsage: addrole @member role_name """

        logging_channel = discord.utils.get(ctx.guild.channels,id=self.logging_channel)

        try:
            if member is None:
                return await ctx.send('Provide member.\n**Usage:** `addrole @member role_name`')
            if role_name is None:
                return await ctx.send('Provide role name.\n**Usage:** `addrole @member role_name`')

            role = discord.utils.get(ctx.guild.roles, name=role_name)

            if role is None:
                return await ctx.send('Role not found')

            if ctx.author.top_role < role:
                await ctx.send(f'Your role is lower than { role.name }.')

            else:
                r = discord.utils.get(member.roles, name=role.name)
                if r is None:
                    await member.add_roles(role)
                    await ctx.send(f'Gave role { role.name } to { member.name }')
                    
                    embed = helper.create_embed(author=ctx.author, users=[member], action='Gave role', reason="None", extra=f'Role: { role.name }\nRole ID: { role.id }', color=discord.Color.purple())
                    return await logging_channel.send(embed=embed)

                else:
                    await member.remove_roles(role)
                    await ctx.send(f'Removed role { role.name } from { member.name }')
                    embed = helper.create_embed(author=ctx.author, users=[member], action='Removed role', reason="None", extra=f'Role: { role.name }\nRole ID: {role.id}', color=discord.Color.purple())
                    return await logging_channel.send(embed=embed)

        except Exception as e:
            self.logger.error(str(e))
            await ctx.send('Unable to give role.')
    

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def warn(self, ctx, *args):
        """ Warn user(s) \nUsage: warn @member(s) reason """
        try:
            
            members, reason = custom_converters.get_members(ctx, *args)

            if members is None:
                return await ctx.send('Provide member(s) to warn.\n**Usage:** `warn @member(s) reason`')

            if reason is None:
                return await ctx.send('Provide a reason.\n**Usage:** `warn @member(s) reason`')
            
            reason = " ".join(reason)

            helper.create_infraction(author=ctx.author, users=members, action='warn', reason=reason)

            for m in members:
                await ctx.send(f'Warned { m.name }.\nReason: { reason }')

        except Exception as e:
            self.logger.error(str(e))
            await ctx.send('Unable to warn member(s).')

    @commands.command(aliases=['infr'])
    @commands.has_permissions(ban_members=True)
    async def infractions(self, ctx, member: typing.Optional[discord.Member] = None, mem_id: typing.Optional[int] = None, inf_type: str = None):
        """ Get Infractions. \nUsage: infr <page_no> OR infr <@member / member_id> <infraction_type>"""
        try:

            page_no = 1
            if mem_id is not None:
                if len(str(mem_id)) != 18:
                    page_no = mem_id
            
            if inf_type is not None:
                if inf_type == 'w' or inf_type == 'W' or re.match('warn', inf_type, re.IGNORECASE):
                    inf_type = 'warn'
                elif inf_type == 'm' or inf_type == 'M' or re.match('mute', inf_type, re.IGNORECASE):
                    inf_type = 'mute'
                elif inf_type == 'b' or inf_type == 'B' or re.match('ban', inf_type, re.IGNORECASE):
                    inf_type = 'ban'
                elif inf_type == 'k' or inf_type == 'K' or re.match('kick', inf_type, re.IGNORECASE):
                    inf_type = 'kick'

            m = None
            if member is not None:
                m = member
            elif mem_id is not None:
                m = discord.utils.get(ctx.guild.members, id=mem_id)

            infs_embed = helper.get_infractions(member=m, inf_type=inf_type, page_no=page_no)

            await ctx.send(embed=infs_embed)


        except Exception as e:
            self.logger.error(str(e))
            await ctx.send('Unable to fetch infractions.')


    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, time: typing.Optional[int] = None, channel: typing.Optional[discord.TextChannel] = None, *, reason: str = None):
        """ Add/Remove slowmode. \nUsage: slowmode <slowmode_time> <#channel> <reason>"""
        try:
            
            if time is None or time < 0:
                return await ctx.send('Provide a valid time.\n**Usage:** `slowmode <slowmode_time> <#channel> <reason>`')

            ch = ctx.channel

            if channel is not None:
                ch = channel

            await ch.edit(slowmode_delay=time)


            logging_channel = discord.utils.get(ctx.guild.channels,id=self.logging_channel)
            embed = helper.create_embed(author=ctx.author, users=None, action='Added slow mode.', reason=reason, extra=f'Channel: { ch }\nTime: { time } seconds', color=discord.Color.orange())
            await logging_channel.send(embed=embed)


            await ctx.send(f'Slowmode of { time } added to { channel.name }.')

        except Exception as e:
            self.logger.error(str(e))       
            await ctx.send('Unable to add slowmode.')

    


def setup(bot):
    bot.add_cog(Moderation(bot))
    

