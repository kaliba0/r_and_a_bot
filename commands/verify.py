import discord
import os
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

class VerifyView(discord.ui.View):
    def __init__(self, role_id: int, channel_id: int):
        super().__init__(timeout=None)
        self.role_id = role_id
        self.channel_id = channel_id

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green)
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(self.role_id)
        await interaction.user.add_roles(role)
        channel = interaction.guild.get_channel(self.channel_id)
        await channel.set_permissions(interaction.user, read_messages=False, send_messages=False)
        await interaction.response.send_message("You are now verified", ephemeral=True)
        for c in interaction.guild.channels:
            if c.id != self.channel_id:
                await c.set_permissions(interaction.user, overwrite=None)

class VerifyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        load_dotenv()
        self.verify_channel_id = int(os.getenv("VERIFY_CHANNEL_ID"))
        self.verified_role_id = int(os.getenv("VERIFIED_ROLE_ID"))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        for c in member.guild.channels:
            if c.id == self.verify_channel_id:
                await c.set_permissions(member, read_messages=True, send_messages=True)
            else:
                await c.set_permissions(member, read_messages=False, send_messages=False)

    @app_commands.command(name="verify", description="Send the Get Verified embed")
    async def verify_command(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Verification", description="Click the button below to verify your account and access the server", color=0x000)
        view = VerifyView(self.verified_role_id, self.verify_channel_id)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="unverify", description="User to unverify. If not specified, removes the verified role from everyone.")
    async def unverify_command(self, interaction: discord.Interaction, user: discord.Member = None):
        role = interaction.guild.get_role(self.verified_role_id)
        if not role:
            return await interaction.response.send_message("Verified role not found", ephemeral=True)

        await interaction.response.defer(ephemeral=True)

        if user:
            if role in user.roles:
                await user.remove_roles(role)
                for c in interaction.guild.channels:
                    if c.id == self.verify_channel_id:
                        await c.set_permissions(user, read_messages=True, send_messages=True)
                    else:
                        await c.set_permissions(user, read_messages=False, send_messages=False)
                return await interaction.followup.send(f"{user.mention} has been unverified", ephemeral=True)
            else:
                return await interaction.followup.send(f"{user.mention} does not have the verified role", ephemeral=True)
        else:
            count = 0
            for member in interaction.guild.members:
                if role in member.roles:
                    await member.remove_roles(role)
                    for c in interaction.guild.channels:
                        if c.id == self.verify_channel_id:
                            await c.set_permissions(member, read_messages=True, send_messages=True)
                        else:
                            await c.set_permissions(member, read_messages=False, send_messages=False)
                    count += 1
            return await interaction.followup.send(f"Removed verified role from {count} members", ephemeral=True)




class PermissionsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        load_dotenv()
        self.verified_role_id = int(os.getenv("VERIFIED_ROLE_ID"))

    @app_commands.command(name="limit_channel", description="Make a channel only readable by everyone except the admins")
    async def limit_channel(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.verified_role_id)
        overwrite = discord.PermissionOverwrite()
        overwrite.read_messages = True
        overwrite.add_reactions = True
        overwrite.send_messages = False
        await interaction.channel.set_permissions(role, overwrite=overwrite)
        await interaction.response.send_message("Members with the verified role can now only read and react in this channel", ephemeral=True)


async def setup(bot):
    await bot.add_cog(VerifyCog(bot))
    await bot.add_cog(PermissionsCog(bot))
