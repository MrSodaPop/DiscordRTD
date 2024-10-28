import discord
from discord.ext import commands, tasks
from random import randint

from dotenv import dotenv_values
config = dotenv_values(".env")



intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    
@commands.command(name="RTD")
async def RTD(self, ctx, max_players: int=5):
    """Rolls the dice to determine which players must be removed from a lobby

    Args:
        max_players: the maximum lobby size
    """
    if ctx.author.voice and ctx.author.voice.channel:
        voice_channel = ctx.author.voice.channel
        members = voice_channel.members
    
        if members:
            # Get display names of all members in the voice channel
            member_names = [member.display_name for member in members]
            view = CheckboxView(member_names, timeout=30)
            message = await ctx.send("*Select the members who are immune:*\n", view=view)
            
            await view.wait()

            if view.result is None:
                await ctx.send("You did not make a selection in time!")
            else:
                await message.delete()
                
                for name in view.result:
                    member_names.remove(name)
                required_len = max_players - len(view.result)
                
                while len(member_names) > required_len:
                    removed_player = member_names[randint(0, len(member_names) - 1)]
                    await ctx.send(f"{removed_player} has been eliminated!")
                    member_names.remove(removed_player)
        else:
            return await ctx.send(f"No membours vound in {voice_channel.name}")
    else:
        return await ctx.send("You must be in a voice channel to use this command.")
        


class CheckboxItem(discord.ui.Button):
    def __init__(self, label):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"[ ] {label}", custom_id=label)
        self.selected = False

    async def callback(self, interaction: discord.Interaction):
        self.selected = not self.selected
        self.label = f"[{'X' if self.selected else ' '}] {self.custom_id}"
        await interaction.response.edit_message(view=self.view)


class CheckboxView(discord.ui.View):
    def __init__(self, options, timeout=30):
        super().__init__(timeout=timeout)
        self.result = None
        self.options = options

        for option in options:
            self.add_item(CheckboxItem(label=option))

        # self.add_item(discord.ui.Button(label="Submit", style=discord.ButtonStyle.primary, custom_id="submit"))

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.primary)
    async def submit_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        selected_options = [item.custom_id for item in self.children if isinstance(item, CheckboxItem) and item.selected]
        self.result = selected_options
        self.stop()  # Stops listening for interactions

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return True
        
bot.run(config["BOT_TOKEN"])