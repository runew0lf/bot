# coding=utf-8
from aiohttp import ClientSession

from discord import Embed, Member
from discord.ext.commands import (
    AutoShardedBot, BadArgument, BotMissingPermissions,
    CommandError, CommandInvokeError, Context,
    NoPrivateMessage, UserInputError
)

from bot.constants import (
    ADMIN_ROLE, DEVLOG_CHANNEL, DEVOPS_ROLE, MODERATOR_ROLE, OWNER_ROLE, PYTHON_GUILD, SITE_API_KEY, SITE_API_USER_URL
)


class Events:
    """
    No commands, just event handlers
    """

    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    async def send_updated_users(self, *users):
        try:
            with ClientSession(headers={"X-API-Key": SITE_API_KEY}) as session:
                response = await session.post(
                    url=SITE_API_USER_URL,
                    json=list(users)
                )

                return await response.json()
        except Exception as e:
            print(f"Failed to send role updates: {e}")
            return {}

    async def on_command_error(self, ctx: Context, e: CommandError):
        command = ctx.command
        parent = None

        if command is not None:
            parent = command.parent

        if parent and command:
            help_command = (self.bot.get_command("help"), parent.name, command.name)
        elif command:
            help_command = (self.bot.get_command("help"), command.name)
        else:
            help_command = (self.bot.get_command("help"),)

        if isinstance(e, BadArgument):
            await ctx.send(f"Bad argument: {e}\n")
            await ctx.invoke(*help_command)
        elif isinstance(e, UserInputError):
            await ctx.invoke(*help_command)
        elif isinstance(e, NoPrivateMessage):
            await ctx.send("Sorry, this command can't be used in a private message!")
        elif isinstance(e, BotMissingPermissions):
            await ctx.send(
                f"Sorry, it looks like I don't have the permissions I need to do that.\n\n"
                f"Here's what I'm missing: **{e.missing_perms}**"
            )
        elif isinstance(e, CommandInvokeError):
            await ctx.send(
                f"Sorry, an unexpected error occurred. Please let us know!\n\n```{e}```"
            )
            raise e.original
        print(e)

    async def on_ready(self):
        users = []

        for member in self.bot.get_guild(PYTHON_GUILD).members:  # type: Member
            roles = [r.id for r in member.roles]  # type: List[int]

            if OWNER_ROLE in roles:
                users.append({
                    "user_id": member.id,
                    "role": OWNER_ROLE
                })
            elif ADMIN_ROLE in roles:
                users.append({
                    "user_id": member.id,
                    "role": ADMIN_ROLE
                })
            elif MODERATOR_ROLE in roles:
                users.append({
                    "user_id": member.id,
                    "role": MODERATOR_ROLE
                })
            elif DEVOPS_ROLE in roles:
                users.append({
                    "user_id": member.id,
                    "role": DEVOPS_ROLE
                })

        if users:
            data = await self.send_updated_users(*users)  # type: dict

            if any(data.values()):
                embed = Embed(
                    title="User roles updated"
                )

                for key, value in data.items():
                    if value:
                        embed.add_field(
                            name=key.title(), value=str(value)
                        )

                await self.bot.get_channel(DEVLOG_CHANNEL).send(
                    embed=embed
                )

    async def on_member_update(self, before: Member, after: Member):
        if before.roles == after.roles:
            return

        roles = [r.id for r in after.roles]  # type: List[int]

        if OWNER_ROLE in roles:
            self.send_updated_users({
                "user_id": after.id,
                "role": OWNER_ROLE
            })
        elif ADMIN_ROLE in roles:
            self.send_updated_users({
                "user_id": after.id,
                "role": ADMIN_ROLE
            })
        elif MODERATOR_ROLE in roles:
            self.send_updated_users({
                "user_id": after.id,
                "role": MODERATOR_ROLE
            })
        elif DEVOPS_ROLE in roles:
            self.send_updated_users({
                "user_id": after.id,
                "role": DEVOPS_ROLE
            })


def setup(bot):
    bot.add_cog(Events(bot))
    print("Cog loaded: Events")
