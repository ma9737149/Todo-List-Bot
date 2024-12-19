
import discord,os,datetime
from discord.ext import commands
from config import Token



client = commands.Bot(command_prefix="$", intents=discord.Intents.all(),help_command=None)
tree = client.tree


@client.event
async def setup_hook():
    try:
        for fn in os.listdir("./Cogs"):
            if fn.endswith(".py"):
                await client.load_extension(f"Cogs.{fn[:-3]}")
                print(f"{fn[:-3]} Loaded")


        

    except Exception as e:
        print(e)


        
@client.event
async def on_ready():
    sync = await tree.sync()
    await client.change_presence(status = discord.Status.idle,activity=discord.Activity(type=discord.ActivityType.listening,name="علي الفطرة نسير"))
    print(f'synced {len(sync)} command(s)')



    print(f"bot is logged as {client.user}")



class Help_view(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)



    @discord.ui.select(
    placeholder="Select A Category",
    min_values=1,
    max_values=1
    ,options=[
            discord.SelectOption(label="Todo",description="Show TodoList Commands With Description",value="Todo",emoji="📖"),
            discord.SelectOption(label="Rank",description="Show Rank Commands With Description",value="Rank",emoji="🏅") ,
            discord.SelectOption(label="Moderation",description="Show Moderation Commands With Description",value="Moderation",emoji="👑")       
    ]
    )

    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.select):
        
        await interaction.response.defer()

        embed = discord.Embed(title=f"{select.values[0]} Help",description="",colour=discord.Colour.dark_blue())
        cog_value = client.get_cog(select.values[0])
        embed.set_footer(text=f"requested by {interaction.user.name}",icon_url=interaction.user.avatar)
        commmands_in_cog = cog_value.walk_app_commands()
        for cmd in commmands_in_cog:
            embed.add_field(name=f'/{cmd.name}',value=f"`{cmd.description}`",inline=True)

        await interaction.edit_original_response(embed=embed)



@tree.command(name="help",description="أمر مساعده يظهر لك الأوامر مع الوصف ")
async def _help(interaction:discord.Interaction):
    embed = discord.Embed(title="أمر مساعدة",description="يمكنك اختيار ماتريد من قائمة الاختيار التي بالأسفل",color=discord.Colour.dark_blue())
    embed.set_footer(text=f"requested-by:{interaction.user.display_name}",icon_url=interaction.user.avatar)
    await interaction.response.send_message(embed=embed,view = Help_view(),ephemeral=True)


@client.command()
@commands.is_owner()
async def load(ctx,extention):
    await client.load_extension(f'Cogs.{extention}')
    await ctx.send(f"`{extention}` loaded")

 
@client.command()
@commands.is_owner()
async def unload(ctx,extention):
    await client.unload_extension(f'Cogs.{extention}')
    await ctx.send(f"`{extention}` unloaded")


@client.command()
@commands.is_owner()
async def reload(ctx,extention):
    await client.reload_extension(f'Cogs.{extention}')
    await ctx.send(f"`{extention}` reloaded")








client.run(Token)