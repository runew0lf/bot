# coding=utf-8
from discord.ext import commands
from discord.ext.commands import Context


def with_role(*role_ids: int):
    async def predicate(ctx: Context):
        if not ctx.guild:  # Return False in a DM
            return False

        for role in ctx.author.roles:
            if role.id in role_ids:
                return True
        return False
    return commands.check(predicate)


def without_role(*role_ids: int):
    async def predicate(ctx: Context):
        if not ctx.guild:  # Return False in a DM
            return False

        author_roles = [role.id for role in ctx.author.roles]
        return all(role not in author_roles for role in role_ids)
    return commands.check(predicate)


def in_channel(channel_id):
    async def predicate(ctx: Context):
        return ctx.channel.id == channel_id
    return commands.check(predicate)
