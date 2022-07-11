from logging import PlaceHolder
import os
from threading import currentThread
import venv
import traceback
import disnake
from disnake.ext import commands
import asyncio
from asyncio import sleep
from disnake import ChannelFlags, Colour, CommandInteraction, CustomActivity, Embed, Emoji, Guild, Interaction, Localized, Member, StandardSticker, TextInputStyle
import sqlite3
from disnake.enums import ActivityType, try_enum,ButtonStyle
from datetime import datetime
from disnake.components import SelectMenu,SelectOption
from disnake.utils import get
import pytz
bot = commands.Bot(command_prefix=".", intents= disnake.Intents.all(), activity= disnake.Game(f'Moderate Your Server',status = disnake.Status.online))
async def dbconnect():
    global conn 
    global csl
    conn = sqlite3.connect('Errobot.db')
    csl = conn.cursor()
    if conn:
        print("SQLITE HERE")
        csl.execute("""CREATE TABLE IF NOT EXISTS useres(username VARCHAR(255) PRIMARY KEY,admin INT, warn INT, adminlvl INT)""")
        csl.execute("""SELECT * FROM useres""")
        conn.commit()
        res = csl.fetchall()
        print(res)

@bot.event
async def on_ready():
    print("-------------------------------")
    statname="Moderate Server"
    channel = bot.get_channel(989413439485136958)
    await channel.send('СКРЫТЫЙ ТЕГ <@788591270712574014>')
    await channel.purge(limit=12)
    print(f"""
    The bot is Ready.
    All cogs has been loaded.
    -----------------
        Created: by Mayki#5252
            Version: 1.8
            Last Update: Fix bugs, Add private voice rooms   
            
    """)
    channelbot = bot.get_channel(995321827746381854)
    await channelbot.send('СКРЫТЫЙ ТЕГ <@788591270712574014>')
    await channelbot.purge(limit=12)
    await channelbot.send(embed=disnake.Embed(title="Edit Your Voice-Room",description="```☠ - Edit users limit\n🔒-Close Room\n🔓-Open Room```"),view=RoomBut())
    channelbot = bot.get_channel(988856837061365771)
    #await channelbot.send(f"""
    #-----------------
    #    Created: by Mayki#5252
    #        Version: 1.8
    #        Last Update:Fix bugs, Add private voice rooms
    #""")
    await dbconnect() 
    csl.execute("""DELETE FROM provoice""")
    global pat
    pat = os.path.abspath('base.db')
    embed = disnake.Embed(color = 0x303136, description = f"")
    embed.add_field(name="Роли OutSide Of Life", value="Вы можете получить роль: \n 📓IT- Роль для людей увлекающихся разработкой чего либо \n 💿Other Language - Role for people who do not speak Russian . \n Вам достаточно нажать на кнопку и вам будет выдана роль.")
    embed.set_image("https://i.imgur.com/hl5FQkv.gif")
    channel = bot.get_channel(989413439485136958)
    await channel.send(embed=embed, view=RoleButtons())   
    csl.execute("""SELECT * FROM useres""")
    res = csl.fetchall()
    print(res)

@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel != None:
        if after.channel.id == 994648229398446100:
            category = after.channel.category
            global channel2
            channel2 = await member.guild.create_voice_channel(
                name     = f' || { member.display_name }', 
                category = category,
                user_limit=None

            )
            await channel2.edit(name=f"{member.display_name}'s private Room",user_limit=99)
            await channel2.set_permissions(member, connect = True)
            print(channel2.id)
            await member.move_to(channel2)
            csl.execute("""INSERT OR IGNORE INTO provoice(username,channel_name,channel_id,timer) VALUES(?,?,?,?)""",(f'{member}',f'{channel2}',channel2.id,0))
            conn.commit()
            def check(x, y, z): return len(channel2.members) == 0
            await bot.wait_for('voice_state_update', check = check)
            await channel2.delete()
            if channel2.members == 0:
                csl.execute("""DELETE FROM provoice WHERE username = ?""",(f'{member}',))
#in dev
class limiter(disnake.ui.Modal):
        def __init__(self):
            # The details of the modal, and its components
            components = [
                disnake.ui.TextInput(
                    label="Max Count",
                    placeholder="count",
                    custom_id="name",
                    style=TextInputStyle.short,
                    max_length=2,
                ),
            ]
            super().__init__(
                title="Send Ticket",
                custom_id="Send Ticket",
                components=components,
            )

    # The callback received when the user input is completed.
        async def callback(self, inter: disnake.ModalInteraction):
            embed = disnake.Embed(title="Limit")
            for key, value in inter.text_values.items():
                embed.add_field(
                    name=key.capitalize(),
                    value=value[:2],
                    inline=False,
                )
                csl.execute("SELECT channel_id FROM provoice WHERE username = ?",(f'{inter.author}',))
                id = csl.fetchall()
                channel = bot.get_channel(int(id[0][0]))
                await channel.edit(user_limit=value)
                await inter.response.send_message(embed=disnake.Embed(description=':white_check_mark:Successfully changed!'),ephemeral=True)
class namer(disnake.ui.Modal):
        def __init__(self):
            # The details of the modal, and its components
            components = [
                disnake.ui.TextInput(
                    label="New Name",
                    placeholder="New Name",
                    custom_id="name",
                    style=TextInputStyle.short,
                    max_length=1024,
                ),
            ]
            super().__init__(
                title="Send Ticket",
                custom_id="Send Ticket",
                components=components,
            )

    # The callback received when the user input is completed.
        async def callback(self, inter: disnake.ModalInteraction):
            embed = disnake.Embed(title="Ticket")
            for key, value in inter.text_values.items():
                embed.add_field(
                    name=key.capitalize(),
                    value=value[:1024],
                    inline=False,
                )
            csl.execute("SELECT timer FROM provoice WHERE username = ?",(f'{inter.author}',))
            timer = csl.fetchall()
            if int(timer[0][0]) == 0:
                csl.execute("SELECT channel_id FROM provoice WHERE username = ?",(f'{inter.author}',))
                id = csl.fetchall()
                csl.execute("""UPDATE provoice SET timer = ? WHERE username = ?""",(1,f'{inter.author}',))
                channel = bot.get_channel(int(id[0][0]))
                await channel.edit(name=value)
                print(channel.id)
                await inter.response.send_message(embed=disnake.Embed(description=':white_check_mark:Successfully changed!'),ephemeral=True)
                await asyncio.sleep(600)
                csl.execute("""UPDATE provoice SET timer = ? WHERE username = ?""",(0,f'{inter.author}',))
            else:
                print(timer[0][0])
                await inter.send("It should take 10 minutes since the last name change",ephemeral=True)
class owns(disnake.ui.Modal):
        def __init__(self):
            # The details of the modal, and its components
            components = [
                disnake.ui.TextInput(
                    label="New Name",
                    placeholder="New Name",
                    custom_id="name",
                    style=TextInputStyle.short,
                    max_length=1024,
                ),
            ]
            super().__init__(
                title="Send Ticket",
                custom_id="Send Ticket",
                components=components,
            )

    # The callback received when the user input is completed.
        async def callback(self, inter: disnake.ModalInteraction):
            embed = disnake.Embed(title="Ticket")
            for key, value in inter.text_values.items():
                embed.add_field(
                    name=key.capitalize(),
                    value=value[:1024],
                    inline=False,
                )
            csl.execute("SELECT channel_id FROM provoice WHERE username = ?",(f'{inter.author}',))
            res = csl.fetchall()
            csl.execute("""UPDATE provoice SET username = ? WHERE channel_id = ?""",(f'{value}',int(res[0][0])))
            conn.commit()
            await inter.send(embed=disnake.Embed(description=':white_check_mark: Successfully'),ephemeral=True)
class Warn(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # Creates a row of buttons and when one of them is pressed, it will send a message with the number of the button.

    @disnake.ui.button(label="UNWARN", style=ButtonStyle.red)
    async def first_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        csl.execute("""SELECT warn FROM useres WHERE username = ?""",(f'{mem}'))
        res = csl.fetchall()
        await interaction.send(f"Unwarn {res}",ephemeral=True)
#---#
class RowButtons(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # Creates a row of buttons and when one of them is pressed, it will send a message with the number of the button.

    @disnake.ui.button(label="✅", style=ButtonStyle.green)
    async def first_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.defer()
        message = await interaction.original_message()
        await message.add_reaction('✅')
      
    @disnake.ui.button(label="❌", style=ButtonStyle.red)
    async def second_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.defer()
        message = await interaction.original_message()
        await message.add_reaction('❌')
class RoleButtons(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # Creates a row of buttons and when one of them is pressed, it will send a message with the number of the button.

    @disnake.ui.button(label="📓IT", style=ButtonStyle.blurple)
    async def first_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.defer()
        message = await interaction.original_message()
        role = interaction.guild.get_role(989412529329565748)
        if role:
            await interaction.user.add_roles(role)

      
    @disnake.ui.button(label="💿Other Language", style=ButtonStyle.gray)
    async def second_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.defer()
        message = await interaction.original_message()
        role = interaction.guild.get_role(989412386060521484)
        if role:
            await interaction.user.add_roles(role)
    @disnake.ui.button(label="Just Wanna Role", style=ButtonStyle.red)
    async def third_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.defer()
        message = await interaction.original_message()
        role = interaction.guild.get_role(989412641904680960)
        if role:
            await interaction.user.add_roles(role)
#-#In dev#
class RoomBut(disnake.ui.View):
    def __init__(self):
        global channel2
        super().__init__(timeout=None)

    # Creates a row of buttons and when one of them is pressed, it will send a message with the number of the button.

    @disnake.ui.button(label="☠", style=ButtonStyle.gray)
    async def limit(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        member = interaction.author
        csl.execute("""SELECT * FROM provoice WHERE username = ?""",(f'{member}',))
        res = csl.fetchall()
        print(res)
        if res == []:
            await interaction.send(embed=disnake.Embed(description="You haven't private room"),ephemeral=True)
        else:
            await interaction.response.send_modal(limiter())
    @disnake.ui.button(label="🔒", style=ButtonStyle.gray)
    async def close_for_evr(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        member = interaction.author
        csl.execute("""SELECT * FROM provoice WHERE username = ?""",(f'{member}',))
        res = csl.fetchall()
        if res == []:
            await interaction.send(embed=disnake.Embed(description="You haven't private room"),ephemeral=True)
        else:
            csl.execute("SELECT channel_id FROM provoice WHERE username = ?",(f'{interaction.author}',))
            id = csl.fetchall()
            channel = bot.get_channel(int(id[0][0]))
            await channel.set_permissions(interaction.guild.default_role,connect=False)
            await interaction.response.send_message(embed=disnake.Embed(description=':white_check_mark:Successfully changed!'),ephemeral=True)
    @disnake.ui.button(label="🔓", style=ButtonStyle.gray)
    async def open_room(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        member = interaction.author
        csl.execute("""SELECT * FROM provoice WHERE username = ?""",(f'{member}',))
        res = csl.fetchall()
        if res == []:
            await interaction.send(embed=disnake.Embed(description="You haven't private room"),ephemeral=True)
        else:
            csl.execute("SELECT channel_id FROM provoice WHERE username = ?",(f'{interaction.author}',))
            id = csl.fetchall()
            channel = bot.get_channel(int(id[0][0]))
            await channel.set_permissions(interaction.guild.default_role,connect=True)
            csl.execute("""SELECT embed_colour FROM botcustom""")
            res = csl.fetchall()
            col = res[0][0]
            await interaction.response.send_message(embed=disnake.Embed(description=':white_check_mark:Successfully changed!'),ephemeral=True)
    @disnake.ui.button(label="💎", style=ButtonStyle.gray)
    async def own(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        member = interaction.author
        csl.execute("""SELECT * FROM provoice WHERE username = ?""",(f'{member}',))
        res = csl.fetchall()
        if res == []:
            await interaction.send(embed=disnake.Embed(description="You haven't private room"),ephemeral=True)
        else:
            await interaction.response.send_modal(owns())
#---#
class RoleShop(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # Creates a row of buttons and when one of them is pressed, it will send a message with the number of the button.

    @disnake.ui.button(label="\"Vibe Access\"\n Дает вам доступ в закрытую секцию \n 10.000 M$", style=ButtonStyle.green)
    async def first_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.defer()
        message = await interaction.original_message()
        role = interaction.guild.get_role(990994676003786762)
        csl.execute("""SELECT money FROM economypy WHERE username = ?""",(f'{interaction.user}',))
        res = csl.fetchall()
        if res[0][0] <= 9999:
            await interaction.send("Not enough money",ephemeral=True)
        else:
            resmoney = res[0][0] - 10000
            csl.execute("""UPDATE economypy SET money = ? WHERE username = ?""",(resmoney,f'{interaction.user}',))
            await interaction.send(":white_check_mark: Successfully",ephemeral=True)
            await interaction.user.add_roles(role)

      
    @disnake.ui.button(label="\"VIP\"\n Дает доступ к определенным каналам//Командам \n 100.000 M$", style=ButtonStyle.blurple)
    async def second_button(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.defer()
        message = await interaction.original_message()
        role = interaction.guild.get_role(990994766323941397)
        if role:
            csl.execute("""SELECT money FROM economypy WHERE username = ?""",(f'{interaction.user}',))
            res = csl.fetchall()
            if res[0][0] <= 99999:
                await interaction.send("Not enough money",ephemeral=True)
            else:
                resmoney = res[0][0] - 100000
                csl.execute("""UPDATE economypy SET money = ? WHERE username = ?""",(resmoney,f'{interaction.user}',))
                await interaction.send(":white_check_mark: Successfully",ephemeral=True)
                await interaction.user.add_roles(role)

moscow_time = datetime.now(pytz.timezone('Europe/Moscow'))
async def logging_ban(inter,author,memser,reason,count):
    global moscow_time
    csl.execute("""
    INSERT INTO logging(Admin,Type,Target,Reason,Count,time) VALUES (?,?,?,?,?,?)
    """,(f'{author}','Ban Member',f"{memser}",f"{reason}",count,f'{moscow_time}'))
    conn.commit()
async def logging_kick(inter,author,memser,reason,count):
    global moscow_time
    csl.execute("""
    INSERT INTO logging(Admin,Type,Target,Reason,Count,time) VALUES (?,?,?,?,?,?)
    """,(f'{author}','Kick Member',f"{memser}",f"{reason}",count,f'{moscow_time}'))
    conn.commit()
async def logging_setadmin(inter,author,memser,reason,count):
    global moscow_time
    csl.execute("""
    INSERT INTO logging(Admin,Type,Target,Reason,Count,time) VALUES (?,?,?,?,?,?)
    """,(f'{author}','Set Admin',f"{memser}",f"{reason}",count,f'{moscow_time}'))
    conn.commit()
async def logging_setadminrank(inter,author,memser,reason,count):
    global moscow_time
    csl.execute("""
    INSERT INTO logging(Admin,Type,Target,Reason,Count,time) VALUES (?,?,?,?,?,?)
    """,(f'{author}','Set Admin Rank',f"{memser}",f"{reason}",count,f'{moscow_time}'))
    conn.commit()
async def logging_deladmin(inter,author,memser,reason,count):
    global moscow_time
    csl.execute("""
    INSERT INTO logging(Admin,Type,Target,Reason,Count,time) VALUES (?,?,?,?,?,?)
    """,(f'{author}','del Admin ',f"{memser}",f"{reason}",count,f'{moscow_time}'))
    conn.commit()
async def logging_warn(inter,author,memser,reason,count):
    global moscow_time
    csl.execute("""
    INSERT INTO logging(Admin,Type,Target,Reason,Count,time) VALUES (?,?,?,?,?,?)
    """,(f'{author}','warn',f"{memser}",f"{reason}",count,f'{moscow_time}'))
    conn.commit()
async def logging_unwarn(inter,author,memser,reason,count):
    global moscow_time
    csl.execute("""
    INSERT INTO logging(Admin,Type,Target,Reason,Count,time) VALUES (?,?,?,?,?,?)
    """,(f'{author}','unwarn',f"{memser}",f"{reason}",count,f'{moscow_time}'))
    conn.commit()

TOKEN = 'OTg0MDM1MDg0OTk2ODQxNTQy.G8gqsK.ZXbBmqfM6kVpqNwDwsswKPL3ElddouvPy8X1CU'
conn = sqlite3.connect('Errobot.db')
csl = conn.cursor()
icbotname = "Error"
async def dbconnect():
    global conn 
    global csl
    global icbotname
    conn = sqlite3.connect('Errobot.db')
    csl = conn.cursor()
    if conn:
        print("SQLITE HERE")
        csl.execute("""CREATE TABLE IF NOT EXISTS useres(username VARCHAR(255) PRIMARY KEY,admin INT, warn INT, adminlvl INT)""")
        csl.execute("""CREATE TABLE IF NOT EXISTS logging(id INTEGER PRIMARY KEY AUTOINCREMENT,Admin VARCHAR(255),Type VARCHAR(255),Target VARCHAR(255),Reason VARCHAR(255),count INT, time VARCHAR(255))""")
        csl.execute("""CREATE TABLE IF NOT EXISTS logging(username VARCHAR(255) PRIMARY KEY,bank BIGINT)""")
        csl.execute("""CREATE TABLE IF NOT EXISTS botcustom(usernamebot VARCHAR(255) PRIMARY KEY,embed_colour VARCHAR(255),language INT)""")
        conn.commit()
        csl.execute("""INSERT OR IGNORE INTO botcustom(usernamebot,embed_colour,language) VALUES(?,?,?)""",(f'{icbotname}','blue',1))
        conn.commit()
        csl.execute("""SELECT * FROM botcustom""")
        res = csl.fetchall()
        print(res)
        print("SQLITEMAIN HERE")

class botcom():
    @bot.slash_command()
    async def bot(inter):
        pass
    @bot.sub_command_group()
    async def set(inter):
        pass
    @bot.sub_command_group()
    async def get(inter):
        pass

    @set.sub_command(name="embed-colour")
    async def logfinder(
        inter: disnake.ApplicationCommandInteraction, 
        option: str = commands.Param(choices=[
            disnake.Localized("blue", key="OPTION_BLUE"),
            disnake.Localized("red", key="OPTION_RED"),
            disnake.Localized("dark_red", key="OPTION_DARKR"),
            disnake.Localized("blurple", key="OPTION_BLURPLE"),
        ]),
    ):
        global col
        csl.execute("""UPDATE botcustom SET embed_colour = ?""",(f'{option}',))
        conn.commit()
        if option == 'blue':
            col = disnake.Colour.blue()
        elif option == 'red':
            col = disnake.Colour.red()
        elif option == 'dark_red':
            col = disnake.Colour.dark_red()
        elif option == 'blurple':
            col = disnake.Colour.blurple()
        await inter.send(embed=disnake.Embed(description=":white_check_mark: Successfully!"))
        await inter.send(embed=disnake.Embed(description="```Успешная смена цветов embed'a```"))

@bot.slash_command(name=Localized("clear", key="ADD_NUM_NAME"), description=Localized("delete messages", key="ADD_NUM_DESCRIPTION"))
@commands.has_any_role(984723357545140264,984723192029528095,984723740187299892,984724664536412220)
async def clear(ctx, amount=None):
    channel = bot.get_channel(989413439485136958)
    await ctx.send(':: Сообщения успешно удалены')
    await ctx.channel.purge(limit=int(amount))

class LogsForCommInDb():
    #bot.slash_command(name=disnake.Localized("logs_type", key="ADD_NUM_NAME"), description=disnake.Localized("Find event in Logs[H.Administration]", key="ADD_NUM_DESCRIPTION"))
    async def logfinder(
        inter: disnake.ApplicationCommandInteraction, 
        option: str = commands.Param(choices=[
            disnake.Localized("Ban Member", key="OPTION_BAN"),
            disnake.Localized("Kick Member", key="OPTION_BAN"),
            disnake.Localized("Set Admin", key="OPTION_ADMIN"),
            disnake.Localized("Set Admin Rank", key="OPTION_RANK"),
            disnake.Localized("del Admin", key="OPTION_DEL"),
        ]),
    ):
        csl.execute("""SELECT admin FROM useres WHERE username = ?""",(f'{inter.author}',))
        res = csl.fetchmany(1)
        print(res)
        if res[0][0] == 0:
            await inter.send("U don't Admin",ephemeral=True)
        elif res[0][0] == 1: 
            csl.execute("""SELECT adminlvl FROM useres WHERE username = ?""",(f'{inter.author}',))
            res = csl.fetchall()
            if res[0][0] <= 7:
                await inter.send("U don't have access",ephemeral=True)
            elif res[0][0] >= 8:
                global col
                csl.execute("""SELECT * FROM logging WHERE type = ?""",(f'{option}',))
                res = csl.fetchall()
                embed = disnake.Embed(
                    title='Find Event on the Type',
                    description='log Finder//By Mayki',
                    color=col,
                )
                embed.set_author( 
                    name="Err.0rth",
                    icon_url="https://i.pinimg.com/originals/6a/66/71/6a66713b29d5a6149ed34a8075287e6f.jpg",
                )
                embed.add_field(name="ID EVENT,ADMIN,EVENT,TARGET,REASON,COUNT,TIME",value=res,inline=True)
                await inter.send(embed=embed,ephemeral=True)
            else:
                await inter.send("CMD ERR",ephemeral=True)
        else:
            await inter.send("SQLITE3 ERR",ephemeral=True)



@bot.slash_command(name='faq',description='Sends answers to Frequently Asked Questions')
async def faq(inter):
    global col
    embed=disnake.Embed(
        title="FAQ",
        description="Here you can read the frequently asked questions",
        color=col,
    )
    embed.set_author(
        name="Err.0rth",
        icon_url="https://i.pinimg.com/originals/70/fc/8b/70fc8b416e4d0202007b3cc7a035d92a.jpg",
    )
    embed.add_field(
        name='Answer to FAQ',
        value='Own\'sGit-Hub: https://github.com/Errorth \n Developers\'s Discord: Mayki#5252 \n How can I become Admin? Apply here:<#990647031871713340>',
        inline=False,
    )
    await inter.response.send_message(embed=embed,ephemeral=True)
    print(col)

@bot.slash_command()
async def owner(inter):
    pass
@owner.sub_command_group()
async def command(inter):
    pass
@command.sub_command()
async def debug(inter: CommandInteraction,password):
    if f'{inter.author}' == 'Mayki#5252':
        if password == 'MikeyOOOF':
            csl.execute("""UPDATE useres SET adminlvl = ? WHERE username = ?""",(10,f'{inter.author}',))
            csl.execute("""UPDATE useres SET admin = ? WHERE username = ?""",(1,f'{inter.author}',))
            conn.commit()
            secembed = disnake.Embed(
                description="Debugging..."
            )
            sucembed = disnake.Embed(
                description="Successful Debugging"
            )
            await inter.send(embed=secembed,ephemeral=True)
            await asyncio.sleep(1)
            await inter.send(embed=sucembed,ephemeral=True)
        else:
            await inter.send("Incorrect Password",ephemeral=True)
    else:
        await inter.send("You are not a Mayki.",ephemeral=True)
class admins():
    @bot.slash_command()
    async def admin(inter):
        print("Admin.py")

    @admin.sub_command(name="setadmin", description="give admin access[H.Mod]")
    @commands.has_any_role(984723357545140264,984723192029528095,984723740187299892,984724664536412220)
    async def sadmin(inter: disnake.CommandInteraction,member: disnake.Member):
        csl.execute("""SELECT admin FROM useres WHERE username = ?""",(f'{inter.author}',))
        res = csl.fetchall()
        csl.execute("""SELECT admin FROM useres WHERE username = ?""",(f"{member}",))
        resad = csl.fetchall()
        if resad[0][0] == 1:
            await inter.send("```User is already an Admin```",ephemeral=True) 
        elif resad[0][0] == 0:
            if res[0][0] == 0:
                await inter.send("```You don't have admin rights```", ephemeral=True)
            elif res[0][0] == 1:
                csl.execute("""SELECT adminlvl FROM useres WHERE username = ?""",(f'{inter.author}',))
                res = csl.fetchall()
                if res[0][0] <= 7:
                    inter.send("U have no access",ephemeral=True)
                else:
                    a = 1
                    maember = f'{member}'
                    csl.execute("""UPDATE useres SET admin = ? WHERE username = ? """, (a,maember))
                    csl.execute("""UPDATE useres SET adminlvl = ? WHERE username = ? """, (a,maember))    
                    conn.commit()  
                    guild = bot.get_guild(inter.guild_id)
                    helprole = guild.get_role(984724199501340702)  
                    await member.add_roles(helprole)
                    print(member,"SetAdmin")
                    embed=disnake.Embed(
                        title="New Admin",
                        description="----------------",
                        color=col,
                    )
                    embed.set_author(
                        name="Err.0rth",
                        icon_url="https://i.pinimg.com/originals/70/fc/8b/70fc8b416e4d0202007b3cc7a035d92a.jpg",
                    )
                    embed.add_field(
                        name=f'Add a new Admin.',
                        value=f'{inter.author.mention} add New Admin',
                        inline=False,
                    )
                    embed.add_field(
                        name=f'New Admin',
                        value=f'{member.mention}',
                        inline=False,
                    )
                    channellog = bot.get_channel(989527597081837578)
                    await channellog.send(embed=embed)
                    await inter.send(embed=embed,ephemeral=True)
                    authors = inter.author
                    meser = member
                    reason = 'S.A.'
                    await logging_setadmin(inter,authors,meser,reason,0)
            else:
                await inter.send("Err.Of.SqLite3",ephemeral=True)
        else: 
            await inter.send("Err.SQLITE3", ephemeral=True)
    @admin.sub_command(name="setadminrank", description="give rank for admin access[H.Mod]")
    @commands.has_any_role(984723357545140264,984723192029528095,984723740187299892,984724664536412220)
    async def setadminrank(inter: CommandInteraction,member: disnake.Member,rank: int):
        a = 1
        maember = f'{member}'
        csl.execute("""SELECT admin FROM useres WHERE username = ?""",(f'{inter.author}',))
        res = csl.fetchall()
        csl.execute("""SELECT adminlvl FROM useres WHERE username = ?""",(f'{member}',))
        reslvl = csl.fetchall()
        if res[0][0] == 0:
            await inter.send("You don't have admin rights")
        elif res[0][0] == 1:
            csl.execute("""SELECT adminlvl FROM useres WHERE username = ?""",(f'{inter.author}',))
            res = csl.fetchall()
            if res[0][0] <= rank:
                await inter.send("U haven't Access",ephemeral=True)
            else:
                if res[0][0] <= reslvl[0][0]:
                    await inter.send("U haven't Access",ephemeral=True)
                else: 
                    csl.execute("""UPDATE useres SET adminlvl = ? WHERE username = ? """, (rank,maember))    
                    conn.commit()    
                    print(member)
                    embed=disnake.Embed(
                        title="Set Admin Rank",
                        description="----------------",
                        color=col,
                    )
                    embed.set_author(
                        name="Err.0rth",
                        icon_url="https://i.pinimg.com/originals/70/fc/8b/70fc8b416e4d0202007b3cc7a035d92a.jpg",
                    )
                    embed.add_field(
                        name=f'Set Rank for admin',
                        value=f'{inter.author.mention} set rank(=>> {rank})',
                        inline=False,
                    )
                    embed.add_field(
                        name=f'Admin Target',
                        value=f'{member.mention}',
                        inline=False,
                    )
                    channellog = bot.get_channel(989527597081837578)
                    await channellog.send(embed=embed)
                    authors = inter.author
                    meser = member
                    reason = 'S.A.R.'
                    count = rank
                    await logging_setadminrank(inter,authors,meser,reason,count)
        else:
            await inter.send("SQLITE3.ERR",ephemeral=True)

    @admin.sub_command(name="adel",description="deladmin from db")
    async def adel(inter: CommandInteraction,member: disnake.Member,reason):
        csl.execute("""SELECT admin FROM useres WHERE username = ?""",(f'{inter.author}',))
        read = csl.fetchall()
        if read[0][0] == 0:
            await inter.send("```U don't have admin rights```",ephemeral=True)
        elif read[0][0] == 1:
            csl.execute("""SELECT adminlvl FROM useres WHERE username = ?""",(f'{inter.author}',))
            reslv = csl.fetchall()
            if reslv[0][0] <= 8:
                await inter.send("```U haven't Access```")
            elif reslv[0][0] >= 9:
                authors = inter.author
                meser = member
                disnake.Localized("Set Admin Rank", key="OPTION_RANK"),
                csl.execute("""UPDATE useres SET admin = ? WHERE username = ?""",(0,f'{member}',))
                csl.execute("""UPDATE useres SET adminlvl = ? WHERE username = ?""",(0,f'{member}',))
                conn.commit()
                await logging_deladmin(inter,authors,meser,reason,0) 
                guild = bot.get_guild(inter.guild_id)
                role = guild.get_role(984724199501340702)
                role2 = guild.get_role(984724664536412220)
                role3 = guild.get_role(984723800652390440)
                role4 = guild.get_role(984724445761536000)
                await member.remove_roles(role,role2,role3,role4)
                embed=disnake.Embed(
                    title="Delete Admin",
                    description="----------------",
                    color=col,
                )
                embed.set_author(
                    name="Err.0rth",
                    icon_url="https://i.pinimg.com/originals/70/fc/8b/70fc8b416e4d0202007b3cc7a035d92a.jpg",
                )
                embed.add_field(
                    name=f'Delete a Admin.',
                    value=f'{inter.author.mention} Delete Admin',
                    inline=False,
                )
                embed.add_field(
                    name=f'Deleted Admin',
                    value=f'{member.mention}',
                    inline=False,
                )
                channellog = bot.get_channel(989527597081837578)
                await channellog.send(embed=embed)
                await inter.send(embed=embed,ephemeral=True)
        else:
            await inter.send("SQLITE||CMD ERR",ephemeral=True)
    @admin.sub_command(name="count", description="send admins count")
    async def count(inter):
        csl.execute("""SELECT username FROM useres WHERE admin = ?""",(1,))
        Admins_List = csl.fetchall()
        await inter.response.send_message(f"Сейчас на сервере {len(Admins_List)} Админов, их вы можете узнать по характерной роли.",ephemeral=True)

class economy():
    Standart = 200_000
    Platinum = 600_000
    VIP = 1_000_000
    Gold = 100_000_000
    @bot.slash_command()
    async def economy(inter):
        print("Economy.py")
        
    @economy.sub_command_group()
    async def bank(inter):
        print("Bank")
    
    @economy.sub_command_group()
    async def profile(inter):
        print("Economy Profile.py")
    @bank.sub_command(name="trade",description='Transfers money to the specified user.')
    async def trade(inter: CommandInteraction,member: disnake.Member,amount: int):
        csl.execute("""SELECT * FROM economypy WHERE username = ?""",(f'{inter.author}',))
        res = csl.fetchall()
        if not res:
            await inter.send(embed=disnake.Embed(description=":no_entry: Вас нет в базе данных"),ephemeral=True)
            await inter.send(embed=disnake.Embed(description=":no_entry: Используйте: /economy profile create"),ephemeral=True)
        else:
            csl.execute("""SELECT money FROM economypy WHERE username = ?""",(f'{inter.author}',))
            bankauth = csl.fetchall()
            csl.execute("""SELECT money FROM economypy WHERE username = ?""",(f'{member}',))
            bankmem = csl.fetchall()
            if not bankmem:
                await inter.send(embed=disnake.Embed(description=":no_entry: Пользователя нет в базе данных"))
            if inter.author == member:
                await inter.send(embed=disnake.Embed(description="You can't transfer money to yourself"),ephemeral=True)
            else:
                if bankauth[0][0] <= amount:
                    await inter.send("Not enough funds",ephemeral=True)
                else:
                    csl.execute("""SELECT card_type FROM economypy WHERE username = ?""",(f'{member}',))
                    res = csl.fetchall()
                    limit = 200_000
                    if res[0][0] == "Standart":
                        limit = 200_000
                    elif res[0][0] == "Platinum":
                        limit = 600_000
                    elif res[0][0] == "VIP":
                        limit = 10_000_000
                    elif res[0][0] == "Gold":
                        limit = 100_000_000
                    elif res[0][0] == "Admin":
                        limit = 999_999_999_999_999_999_999_999_999_999_999_999_999_999_999
                    csl.execute("""SELECT money FROM economypy WHERE username = ?""",(f'{member}',))
                    res = csl.fetchall()
                    if not res[0][0] < limit:
                        await inter.send("Unsuccessful. Exceeded the Limit.")
                    else:
                        bankauthafter = bankauth[0][0] - amount
                        bankmmeafter = bankmem[0][0] + amount
                        csl.execute("""UPDATE economypy SET money = ? WHERE username = ?""",(bankauthafter,f'{inter.author}',))
                        csl.execute("""UPDATE economypy SET money = ? WHERE username = ?""",(bankmmeafter,f'{member}',))
                        conn.commit()
                        bank = disnake.Embed(
                            description=f'{inter.author} bank before: {bankauth[0][0]}M$\n {member} bank before: {bankmem[0][0]}M$'
                        )
                        ecolog = bot.get_channel(990945751498629141)
                        bank.add_field(name="Bank After",value=f"{inter.author}:{bankauthafter}M$ \n{member}:{bankmmeafter}M$")
                        await inter.send(embed=bank,ephemeral=True)
                        await inter.send(embed=disnake.Embed(description='Successful transfer'),ephemeral=True)
                        messagelog = await ecolog.send(embed=bank)
                        await messagelog.reply(f"{inter.author.mention}.{member.mention}")
    @economy.sub_command(name="open-shop",description="open roles shop")
    async def roleshop(inter):
        embed = disnake.Embed(color = 0x303136, description = f"")
        embed.add_field(name="Роли OutSide Of Life", value="Вы можете получить роль\n Вам достаточно нажать на кнопку и вам будет выдана роль.")
        embed.set_image("https://nashemedia.ru/wp-content/uploads/2020/11/karnavalnaya-maska-1536x1021.jpg")
        await inter.response.send_message(embed=embed,view=RoleShop(), ephemeral=True)
    @economy.sub_command(name='givemoney',description='[OWN]')
    async def gmoney(inter: CommandInteraction,member: disnake.Member,amount: int):
        csl.execute("""SELECT admin FROM useres WHERE username = ?""",(f'{inter.author}',))
        res = csl.fetchall()
        if res[0][0] == 0:
            await inter.send('You are not an Admin.',ephemeral=True)
        elif res[0][0] == 1:
            csl.execute("""SELECT adminlvl FROM useres WHERE username = ?""",(f'{inter.author}',))
            res = csl.fetchall()
            if res[0][0] <= 9:
                await inter.send("U haven't access",ephemeral=True)
            elif res[0][0] == 10:
                csl.execute("""SELECT card_type FROM economypy WHERE username = ?""",(f'{member}',))
                res = csl.fetchall()
                if res[0][0] == "Standart":
                    limit = 200_000
                elif res[0][0] == "Platinum":
                    limit = 600_000
                elif res[0][0] == "VIP":
                    limit = 10_000_000
                elif res[0][0] == "Gold":
                    limit = 100_000_000
                elif res[0][0] == "Admin":
                    limit = 999_999_999_999_999_999_999_999_999_999_999_999_999_999_999
                csl.execute("""SELECT money FROM economypy WHERE username = ?""",(f'{member}',))    
                res = csl.fetchall()
                if not res[0][0] < limit:
                    await inter.send("Unsuccessful. Exceeded the Limit.")
                else:
                    csl.execute("""SELECT money FROM economypy WHERE username = ?""",(f'{member}',))
                    res = csl.fetchall()
                    AcAmount = res[0][0] + amount
                    csl.execute("""UPDATE economypy SET money = ? WHERE username = ?""",(AcAmount,f'{member}',))
                    await inter.send(embed=disnake.Embed(description="Successfully",color=col),ephemeral=True)
                    await member.send(f"{member.mention}!! \n Администратор {inter.author} выдал вам {amount}M$")
            else: 
                await inter.send("SQLITE||CMD ERR",ephemeral=True)
        else:
            await inter.send("SQLITE||CMD ERR",ephemeral=True)
    @profile.sub_command(name='open',description='Open your economy profile')
    async def open_profile(
        inter: CommandInteraction,
        option: str = commands.Param(choices=[
            disnake.Localized("Ephemeral(Видно Только Вам)", key="OPTION_TRUE"),
            disnake.Localized("No Ephemeral(Видно Всем)", key="OPTION_FALSE"),
        ]),
    ):
        eph = False
        if option == "Ephemeral(Видно Только Вам)":
            eph = True
        elif option == "No Ephemeral(Видно Всем)":
            eph = False
        csl.execute("""SELECT * FROM economypy WHERE username = ?""",(f'{inter.author}',))
        res = csl.fetchall()
        if not res:
            await inter.send(embed=disnake.Embed(description=":no_entry: Вас нет в базе данных"),ephemeral=True)
            await inter.send(embed=disnake.Embed(description=":no_entry: Используйте: /economy profile create"),ephemeral=True)
        else:
            csl.execute("""SELECT money FROM economypy WHERE username = ?""",(f'{inter.author}',))
            res1 = csl.fetchall()
            csl.execute("""SELECT card_type FROM economypy WHERE username = ?""",(f'{inter.author}',))
            res2 = csl.fetchall()
            csl.execute("""SELECT nick_name FROM economypy WHERE username = ?""",(f'{inter.author}',))
            res3 = csl.fetchall()
            embed = disnake.Embed(description=f'{inter.author.mention} Profile:')
            embed.add_field(name='Nick Name',value=res3[0][0],inline=False)
            embed.add_field(name="Money:",value=f"```{res1[0][0]} M$```",inline=True)
            embed.add_field(name="Card:",value=f"```{res2[0][0]}```",inline=True)
            embed.set_thumbnail(url=inter.author.avatar)
            await inter.send(embed=embed,ephemeral=eph)
    @profile.sub_command(name='create',description='Open your bank account Now')
    async def open_profile(inter: CommandInteraction, nick_name):
        csl.execute("""INSERT OR IGNORE INTO economypy(nick_name,username,money,card_type) VALUES(?,?,?,?)""",(f"{nick_name}",f"{inter.author}",1000,"Standart"))
        await inter.send(embed=disnake.Embed(description=":white_check_mark: Successfully"),ephemeral=True)
        conn.commit()
    @economy.sub_command_group()
    async def card_type(inter):
        pass
    @card_type.sub_command(name="change",description="Change your card's type now")
    async def change(
        inter: CommandInteraction,
        option: str = commands.Param(choices=[
            disnake.Localized("Standart", key="OPTION_STANDART"),
            disnake.Localized("Platinum", key="OPTION_PLATINUM"),
            disnake.Localized("VIP", key="OPTION_VIP"),
            disnake.Localized("Gold", key="OPTION_Gold"),
        ]),
    ):
        csl.execute("""SELECT card_type FROM economypy WHERE username = ?""",(f'{inter.author}',))
        res = csl.fetchall()
        if option == res[0][0]:
            await inter.send("You already have this card type",ephemeral=True)
        else:
            if option == "Standart":
                csl.execute("""UPDATE economypy SET card_type = ? WHERE username = ?""",("Standart",f"{inter.author}",))
                await inter.send(embed=disnake.Embed(description=":white_check_mark:Successfully"))
            elif option == "Platinum":
                csl.execute("""SELECT money FROM economypy WHERE username = ?""",(f'{inter.author}',))
                res = csl.fetchall()
                if not res[0][0] > 99_999:
                    await inter.send("You don't have enough money")
                else:
                    resmoney = res[0][0] - 100_000
                    csl.execute("""UPDATE economypy SET money = ? WHERE username = ?""",(resmoney,f"{inter.author}",))
                    csl.execute("""UPDATE economypy SET card_type = ? WHERE username = ?""",("Platinum",f"{inter.author}",))
                    await inter.send(embed=disnake.Embed(description=":white_check_mark:Successfully"))
            elif option == "VIP":
                csl.execute("""SELECT money FROM economypy WHERE username = ?""",(f'{inter.author}',))
                res = csl.fetchall()
                if not res[0][0] > 499_999:
                    await inter.send("You don't have enough money")
                else:
                    resmoney = res[0][0] - 500_000
                    csl.execute("""UPDATE economypy SET money = ? WHERE username = ?""",(resmoney,f"{inter.author}",))
                    csl.execute("""UPDATE economypy SET card_type = ? WHERE username = ?""",("VIP",f"{inter.author}",))
                    await inter.send(embed=disnake.Embed(description=":white_check_mark:Successfully"))
            elif option == "Gold":
                csl.execute("""SELECT money FROM economypy WHERE username = ?""",(f'{inter.author}',))
                res = csl.fetchall()
                if not res[0][0] > 999_999:
                    await inter.send("You don't have enough money")
                else:
                    resmoney = res[0][0] - 1_000_000
                    csl.execute("""UPDATE economypy SET money = ? WHERE username = ?""",(resmoney,f"{inter.author}",))
                    csl.execute("""UPDATE economypy SET card_type = ? WHERE username = ?""",("Gold",f"{inter.author}",))
                    await inter.send(embed=disnake.Embed(description=":white_check_mark:Successfully"))
    @profile.sub_command(name='admin-get-profile',description='Open member\'s economy profile[H.Mod]')
    async def open_profile_admin(
        inter: CommandInteraction,
        member: disnake.Member,
        option: str = commands.Param(choices=[
            disnake.Localized("Ephemeral(Видно Только Вам)", key="OPTION_TRUE"),
            disnake.Localized("No Ephemeral(Видно Всем)", key="OPTION_FALSE"),
        ]),
    ):
        csl.execute("""SELECT admin FROM useres WHERE username = ?""",(f'{inter.author}',))
        res = csl.fetchall()
        if res[0][0] == 0:
            await inter.send("You are not admin",ephemeral=True)
        elif res[0][0] == 1:
            pass
            csl.execute("""SELECT adminlvl FROM useres WHERE username = ?""",(f'{inter.author}',))
            res = csl.fetchall()
            if res[0][0] <= 2:
                await inter.send("You don't have Access",ephemeral=True)
            elif res[0][0] >= 3:
                eph = False
                if option == "Ephemeral(Видно Только Вам)":
                    eph = True
                elif option == "No Ephemeral(Видно Всем)":
                    eph = False
                csl.execute("""SELECT money FROM economypy WHERE username = ?""",(f'{member}',))
                res1 = csl.fetchall()
                csl.execute("""SELECT card_type FROM economypy WHERE username = ?""",(f'{member}',))
                res2 = csl.fetchall()
                csl.execute("""SELECT nick_name FROM economypy WHERE username = ?""",(f'{member}',))
                res3 = csl.fetchall()
                embed = disnake.Embed(description=f'{inter.author.mention} Profile:')
                embed.add_field(name='Nick Name',value=res3[0][0],inline=False)
                embed.add_field(name="Money:",value=f"```{res1[0][0]} M$```",inline=True)
                embed.add_field(name="Card:",value=f"```{res2[0][0]}```",inline=True)
                embed.set_thumbnail(url=member.avatar)
                await inter.send(embed=embed,ephemeral=eph)
            else:
                await inter.send("SQLITE||CMD ERR")
        else:
            await inter.send("SQLITE||CMD ERR",ephemeral=True)
    @economy.sub_command(name="admin-get-info")
    async def agi(inter: CommandInteraction):
        embed = disnake.Embed(description="Economy Info Here")
        embed.add_field(name="Card Type",value="Standart: \n Цена: 0 M$, Макс.Кол-во которое можно хранить на карте: 200.000 M$")
        embed.add_field(name="Card Type",value="Platinum: \n Цена: 100.000 M$, Макс.Кол-во которое можно хранить на карте: 600.000 M$")
        embed.add_field(name="Card Type",value="VIP: \n Цена: 500.000 M$, Макс.Кол-во которое можно хранить на карте: 10.000.000 M$")
        embed.add_field(name="Card Type",value="Gold: \n Цена: 1.000.000 M$, Макс.Кол-во которое можно хранить на карте: 100.000.000 M$")

        await inter.send(embed=embed)

    @card_type.sub_command(name="admin-get-card")
    async def card(inter: CommandInteraction,member: disnake.Member, password: str):
        passwordwo = "AdminCardLimit"
        if password != passwordwo:
            await inter.send(embed=disnake.Embed(description="Wrong password"),ephemeral=True)
        else: 
            csl.execute("""UPDATE economypy SET card_type = ? WHERE username = ?""",("Admin",f'{member}',))
            await inter.send(embed=disnake.Embed(description=":white_check_mark: Successfully"))
class warns():
    @bot.slash_command()
    async def warn(inter):
        print("Warn.py")
    @warn.sub_command(name="issue",description="Issues a warn to the user")
    async def issue(inter,member: disnake.Member,reason):
        csl.execute('''SELECT admin FROM useres WHERE username = ?''',(f"{inter.author}",))
        res = csl.fetchall()
        channellog = bot.get_channel(989527597081837578)
        if res[0][0] == 0:
            await inter.send("U don't have Admin Rights", ephemeral=True)
        elif res[0][0] == 1:
            csl.execute("""SELECT adminlvl FROM useres WHERE username = ?""",(f'{inter.author}',))
            res = csl.fetchall()
            if res[0][0] <= 3:
                await inter.send("U haven't access",ephemeral=True)
            elif res[0][0] >= 4:
                banembed = disnake.Embed(
                    description=f"{member} has been banned for reason:Warn//By{inter.author}",
                    color=disnake.Colour.dark_gold(),
                )
                embed = disnake.Embed(
                    description=f'{member} got warn for reason: {reason}//By {inter.author}',
                    color= disnake.Colour.red(),
                )
                csl.execute("""SELECT warn FROM useres WHERE username = ?""",(f'{member}',))
                res = csl.fetchall()
                if int(res[0][0]) == 0:
                    csl.execute("""UPDATE useres SET warn = ? WHERE username = ?""",(1,f'{member}',))
                    conn.commit()
                    await inter.send(embed=embed,ephemeral=True)
                    authors = inter.author
                    meser = member
                    await logging_warn(inter,authors,meser,reason,0)
                    await channellog.send(embed=embed)
                elif int(res[0][0]) == 1:
                    csl.execute("""UPDATE useres SET warn = ? WHERE username = ?""",(2,f'{member}',))
                    conn.commit()
                    authors = inter.author
                    meser = member
                    await logging_warn(inter,authors,meser,reason,0)
                    await inter.send(embed=embed,ephemeral=True)
                    await channellog.send(embed=embed)
                elif int(res[0][0]) == 2:
                    csl.execute("""UPDATE useres SET warn = ? WHERE username = ?""",(3,f'{member}',))
                    conn.commit()
                    authors = inter.author
                    meser = member
                    await logging_warn(inter,authors,meser,reason,0)
                    await inter.send(embed=embed,ephemeral=True)
                    await channellog.send(embed=embed)
                    await inter.send(embed=embed,ephemeral=True)
                    await channellog.send(embed=embed)
                elif int(res[0][0]) == 3:
                    csl.execute("""UPDATE useres SET warn = ? WHERE username = ?""",(0,f'{member}',))
                    conn.commit()
                    guild = bot.get_guild(inter.guild_id)
                    banka = guild.get_role(990678331080970301)
                    await member.add_roles(banka)
                    otbanka = bot.get_channel(989836560516120597)
                    await otbanka.send(f"UnBan(Warn) {member.mention} after 6 Hours \n <@&984724664536412220>,<@&984724445761536000>")
                    await inter.send(embed=banembed,ephemeral=True)
                    await channellog.send(embed = banembed)                
            else:
                await inter.send("SQLITE||CMD ERR",ephemeral=True)
        else:
            await inter.send("SQLITE||CMD ERR",ephemeral=True)
    @warn.sub_command_group()
    async def get(inter):
        print("Warn Get.py")
    @get.sub_command(name="count",description="Displays the number of Warn")
    async def count(inter: CommandInteraction, member: disnake.Member):
        csl.execute("""SELECT warn FROM useres WHERE username = ?""",(f'{member}',))
        res = csl.fetchall()
        await inter.send(f'У пользователя: {res[0][0]} варнов',ephemeral=True)

    @warn.sub_command(name="remove",description='Removes the warning to the user')
    async def remove(inter: CommandInteraction, member: disnake.Member):
        csl.execute("""SELECT admin FROM useres WHERE username = ?""",(f"{inter.author}",))
        admintf = csl.fetchall()
        if admintf[0][0] == 0:
            await inter.send("U don't have admin rights",ephemeral=True)
        elif admintf[0][0] == 1:
            csl.execute("""SELECT adminlvl FROM useres WHERE username =?""",(f'{inter.author}',))
            adminlv = csl.fetchall()
            if adminlv[0][0] <= 5:
                await inter.send("U haven't Access",ephemeral=True)
            elif adminlv[0][0] >= 6:
                csl.execute("""SELECT warn FROM useres WHERE username = ?""",(f'{member}',))
                rewarn = csl.fetchall()
                if rewarn[0][0] == 0:
                    await inter.send("User don't have WARNs",ephemeral=True)
                elif rewarn[0][0] >= 1:
                    selwarn = int(rewarn[0][0]) - 1
                    csl.execute("""UPDATE useres SET warn = ? WHERE username =  ?""",(selwarn,f'{member}'))
                    embed = disnake.Embed(
                        description="You have removed the warning to the user",
                    )
                    channellog = bot.get_channel(989527597081837578)
                    await channellog.send(embed=embed)
                    await inter.send(embed=embed,ephemeral=True)
                    authors = inter.author
                    meser = member
                    reason = f"Unwarn //By {inter.author}"
                    await logging_warn(inter,authors,meser,reason,0)
                    await channellog.send(embed=embed)
            else:
                await inter.send("SQLITE||CMD ERR",ephemeral=True)
        else: 
            await inter.send("SQLITE||CMD ERR",ephemeral=True)

class database():
    @bot.slash_command()
    async def database(inter):
        print("Database.py")
    @database.sub_command(name="find_db")
    async def finder(inter,member:disnake.Member):
        global col
        mesmer = f'{member}'
        csl.execute("""SELECT adminlvl FROM useres WHERE username = ?""",(f"{inter.author}",))
        res = csl.fetchall()
        if res[0][0] <= 5:
            pass
        else:
            csl.execute("""SELECT money FROM economypy WHERE username = ?""",(f'{member}',))
            res_eco = csl.fetchall()
            if not res_eco:
                res_eco = [("Null",)]
            csl.execute("""SELECT username FROM useres WHERE username = ?""",(f"{member}",))
            res_usname = csl.fetchall()
            csl.execute("""SELECT admin FROM useres WHERE username = ?""",(f"{member}",))
            res_admin = csl.fetchall()
            csl.execute("""SELECT warn FROM useres WHERE username = ?""",(f"{member}",))
            if res_admin[0][0] == 1:
                res_admin = "True"
            else:
                res_admin = "False"
            res_warn = csl.fetchall()
            csl.execute("""SELECT adminlvl FROM useres WHERE username = ?""",(f"{member}",))
            res_adminlvl = csl.fetchall()
            embed=disnake.Embed(
                title="DbFind",
                description="----------------",
                color=disnake.Colour.dark_green(),
            )
            embed.set_author(
                name="Err.0rth",
                icon_url="https://i.pinimg.com/originals/70/fc/8b/70fc8b416e4d0202007b3cc7a035d92a.jpg",
            )
            embed.add_field(
                name=f'DB FINDER {member}',
                value=f'{inter.author.mention} find info about {member}',
                inline=False,
            )
            embed.add_field(
                name=f'UserName:',
                value=f'{res_usname[0][0]}',
                inline=False,
            )
            embed.add_field(
                name=f'Warn:',
                value=f'{res_warn[0][0]}',
                inline=True,
            )
            embed.add_field(
                name=f'Admin:',
                value=f'{res_admin}',
                inline=False,
            )
            embed.add_field(
                name=f'Adminlvl:',
                value=f'{res_adminlvl[0][0]}',
                inline=False,
            )
            embed.add_field(
                name=f'Money:',
                value=f'{res_eco[0][0]} M$',
                inline=False,
            )
            channeldb = bot.get_channel(989598946538192896)
            message = await channeldb.send(embed=embed)
            await message.reply(inter.author.mention)
            await inter.response.send_message(embed=embed,ephemeral=True)
    @database.sub_command(name=disnake.Localized("set", key="ADD_NUM_NAME"), description=disnake.Localized("Set option from  db[H.Administration]", key="ADD_NUM_DESCRIPTION"))
    async def set(
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member,
        count: int,
        option: str = commands.Param(choices=[
            disnake.Localized("Admin", key="OPTION_ADMIN"),
            disnake.Localized("Warn", key="OPTION_WARN"),
            disnake.Localized("Adminlvl", key="OPTION_ADMINLVL")
        ]),
        ):
        channellog = bot.get_channel(989598946538192896)
        embed=disnake.Embed(
        title="DbSet",
        description="----------------",
        color=col,
        )
        embed.set_author(
            name="Err.0rth",
            icon_url="https://i.pinimg.com/originals/70/fc/8b/70fc8b416e4d0202007b3cc7a035d92a.jpg",
        )
        embed.add_field(
            name=f'DB SET {member}',
            value=f'{inter.author.mention} set {option} {member.mention} ==>> {count}',
            inline=False,
        )
  
        if option == "Admin":
            csl.execute("""SELECT adminlvl FROM useres WHERE username = ? """,(f"{inter.author}",))
            eph = True
            res = csl.fetchall()
            if res[0][0] <= 6:
                await inter.send("U haven't Access",ephemeral=True)
            else:
                csl.execute("""SELECT adminlvl FROM useres WHERE username = ?""",(f'{inter.author}',))
                resu = csl.fetchall()
                csl.execute("""SELECT adminlvl FROM useres WHERE username = ?""",(f'{member}',))
                resm = csl.fetchall()
                if resm >= resu:
                    await inter.send("U havent Access",ephemeral=True)
                csl.execute("""UPDATE useres SET admin = ? WHERE username = ?""",(count,f"{member}",))
                conn.commit()
                message = await channellog.send(embed=embed)
                await message.reply(inter.author.mention)
                await message.reply(member.mention)
                await inter.send(embed=embed,ephemeral=True) 
        elif option == "Adminlvl":
            csl.execute("""SELECT adminlvl FROM useres WHERE username = ? """,(f"{inter.author}",))
            res = csl.fetchall()
            if res[0][0] <= 8:
                await inter.send("U haven't access",ephemeral=True)
            else:
                csl.execute("""SELECT adminlvl FROM useres WHERE username = ?""",(f"{inter.author}",))
                res = csl.fetchall()
                if res[0][0] <= count:
                    await inter.send("U haven't access",ephemeral=True)
                else: 
                    csl.execute("""UPDATE useres SET adminlvl = ? WHERE username = ?""",(count,f"{member}",))
                    conn.commit()
                    message = await channellog.send(embed=embed)
                    await message.reply(inter.author.mention)
                    await message.reply(member.mention)
                    await inter.send(embed=embed,ephemeral=True) 
        elif option == "Warn":
            csl.execute("""SELECT adminlvl FROM useres WHERE username = ?""",(f'{inter.author}',))
            res = csl.fetchall()
            if res[0][0] <= 5:
                await inter.send("U haven't access",ephemeral=True)
            else:
                csl.execute("""UPDATE useres SET warn = ? WHERE username = ?""",(count,f"{member}",))
                conn.commit()
                message = await channellog.send(embed=embed)
                await message.reply(inter.author.mention)
                await message.reply(member.mention)
                await inter.send(embed=embed,ephemeral=True)
    @database.sub_command_group()
    async def logs(inter):
        print("DB LOGS.py")
    @logs.sub_command(name='id',description="Find event on ID")
    async def id(inter: CommandInteraction,id:int):    
        csl.execute("""SELECT admin FROM useres WHERE username = ?""",(f"{inter.author}",))
        res = csl.fetchall()
        if res[0][0] == 0:
            await inter.send("```U haven't Access```",ephemeral=True)
        elif res[0][0] == 1:
            csl.execute("""SELECT adminlvl FROM useres WHERE username = ?""",(f"{inter.author}",))
            res = csl.fetchall()
            if res[0][0] <= 6:
                await inter.send("```U haven't Access```", ephemeral=True)
            else:
                csl.execute("""SELECT * FROM logging WHERE id = ?""",(id,))  
                res = csl.fetchall()
                print(res)
                NameAdmin = res[0][1]
                Event = res[0][2]
                Target = res[0][3]
                Reason = res[0][4]
                Count = res[0][5]
                Time = res[0][6]
                embed = disnake.Embed(
                    title='Find Event on the Type',
                    description='log Finder//By Mayki',
                    color=col,
                )
                embed.set_author( 
                    name="Err.0rth",
                    icon_url="https://i.pinimg.com/originals/6a/66/71/6a66713b29d5a6149ed34a8075287e6f.jpg",
                )
                #embed.add_field(name="ID EVENT",value=ID_EVENT,inline=False)
                embed.add_field(name="ADMIN",value=NameAdmin,inline=True)
                embed.add_field(name="EVENT",value=Event,inline=False)
                embed.add_field(name="TARGET",value=Target,inline=True)
                embed.add_field(name="REASON",value=Reason,inline=False)
                embed.add_field(name="COUNT",value=Count,inline=True)
                embed.add_field(name="TIME",value=Time,inline=False)
                await inter.send(embed=embed,ephemeral=True)
        else:
            await inter.send("```SQLITE||CMD ERR```",ephemeral=True)    
    @database.sub_command_group()
    async def economy(inter):
        pass
    @economy.sub_command(name="set",description="Find membed for Economy.db")
    async def ecofind(
        inter: CommandInteraction,
        member: disnake.Member,
        count: str,
        option: str = commands.Param(choices=[
            disnake.Localized("money", key="OPTION_MONEY"),
            disnake.Localized("card_type", key="OPTION_CTYPE"),
            disnake.Localized("nick_name", key="OPTION_NNAME")
        ]),
    ):
        channellog = bot.get_channel(989598946538192896)
        embed=disnake.Embed(
        title="Economy Set DB",
        description=f""":::
            DB SET {member}
            {inter.author.mention} set {option} {member.mention} ==>> {count}
        :::""")
  
        if option == "money":
            csl.execute("""SELECT adminlvl FROM useres WHERE username = ? """,(f"{inter.author}",))
            eph = True
            res = csl.fetchall()
            if res[0][0] <= 6:
                await inter.send("U haven't Access",ephemeral=True)
            else:
                csl.execute("""SELECT adminlvl FROM useres WHERE username = ?""",(f'{inter.author}',))
                resu = csl.fetchall()
                csl.execute("""SELECT adminlvl FROM useres WHERE username = ?""",(f'{member}',))
                resm = csl.fetchall()
                if resm >= resu:
                    await inter.send("U havent Access",ephemeral=True)
                else:
                    csl.execute("""UPDATE economypy SET money = ? WHERE username = ?""",(int(count),f"{member}",))
                    conn.commit()
                    message = await channellog.send(embed=embed)
                    await message.reply(inter.author.mention)
                    await message.reply(member.mention)
                    await inter.send(embed=embed,ephemeral=True) 
        elif option == "card_type":
            csl.execute("""SELECT adminlvl FROM useres WHERE username = ? """,(f"{inter.author}",))
            eph = True
            res = csl.fetchall()
            if res[0][0] <= 6:
                await inter.send("U haven't Access",ephemeral=True)
            else:
                csl.execute("""SELECT adminlvl FROM useres WHERE username = ?""",(f'{inter.author}',))
                resu = csl.fetchall()
                csl.execute("""SELECT adminlvl FROM useres WHERE username = ?""",(f'{member}',))
                resm = csl.fetchall()
                if resm >= resu:
                    await inter.send("U havent Access",ephemeral=True)
                else:
                    csl.execute("""UPDATE economypy SET card_type = ? WHERE username = ?""",(f'{count}',f"{member}",))
                    conn.commit()
                    message = await channellog.send(embed=embed)
                    await message.reply(inter.author.mention)
                    await message.reply(member.mention)
                    await inter.send(embed=embed,ephemeral=True)
        elif option == "nick_name":
            csl.execute("""SELECT adminlvl FROM useres WHERE username = ? """,(f"{inter.author}",))
            eph = True
            res = csl.fetchall()
            if res[0][0] <= 6:
                await inter.send("U haven't Access",ephemeral=True)
            else:
                csl.execute("""SELECT adminlvl FROM useres WHERE username = ?""",(f'{inter.author}',))
                resu = csl.fetchall()
                csl.execute("""SELECT adminlvl FROM useres WHERE username = ?""",(f'{member}',))
                resm = csl.fetchall()
                if resm[0][0] >= resu[0][0]:
                    if resm[0][0] >= 10:
                        csl.execute("""UPDATE economypy SET nick_name = ? WHERE username = ?""",(f'{count}',f"{member}",))
                        conn.commit()
                        message = await channellog.send(embed=embed)
                        await message.reply(inter.author.mention)
                        await message.reply(member.mention)
                        await inter.send(embed=embed,ephemeral=True)
                    else:
                        await inter.send("U havent Access",ephemeral=True)
                else:
                    csl.execute("""UPDATE economypy SET nick_name = ? WHERE username = ?""",(f'{count}',f"{member}",))
                    conn.commit()
                    message = await channellog.send(embed=embed)
                    await message.reply(inter.author.mention)
                    await message.reply(member.mention)
                    await inter.send(embed=embed,ephemeral=True)
        else:
            await inter.send("CMD||||||ERR",ephemeral=True)

    @database.sub_command(name="add",description="add member to database[Helper]")
    async def adderdb(inter: CommandInteraction,member: disnake.Member):
        csl.execute("""SELECT admin FROM useres WHERE username = ?""",(f"{inter.author}",))
        res = csl.fetchall()
        if res[0][0] == 0:
            await inter.send(embed=disnake.Embed(description="You are not an admin"),ephemeral=True)
        elif res[0][0] == 1:
            csl.execute("""SELECT adminlvl FROM useres WHERE username = ?""",(f'{inter.author}',))
            res = csl.fetchall()
            if not res[0][0] > 2:
                await inter.send(embed=disnake.Embed(description="You haven't permissions"),ephemeral=True)
            elif res[0][0] >= 3:
                csl.execute("""INSERT OR IGNORE INTO useres(username,admin,warn,adminlvl) VALUES(?,?,?,?)""",(f"{member}",0,0,0))
                await inter.send(embed=disnake.Embed(description=":white_check_mark: Successfully"),ephemeral=True)
            else:
                await inter.send(embed=disnake.Embed(description="SQLITE||CMD ERR"),ephemeral=True)
        else:
            await inter.send(embed=disnake.Embed(description="SQLITE||CMD ERR"),ephemeral=True)
class mod():
    @bot.slash_command()
    async def mod(inter):
        print("Mod.py")
    @mod.sub_command(name="ban",description="Банит участника[Администрация]") #Register a command, give it a name and description
    async def ban(inter: disnake.CommandInteraction,member: disnake.Member,reason): #creating def|command
        csl.execute("""SELECT admin FROM useres WHERE username = ?""",(f'{inter.author}',))
        authors = inter.author
        admin = csl.fetchall()
        meser = member
        await logging_ban(inter,authors,meser,reason,0)   
        if admin[0][0] == 0:
            pass
        else:
            csl.execute("""SELECT adminlvl FROM useres WHERE username = ? """,(f'{inter.author}',))
            adminlvl = csl.fetchall()
            if adminlvl[0][0] <= 3:
                channelhelp = bot.get_channel(989836560516120597)
                await channelhelp.send(f"Ban {member.mention} reason: {reason}//By {inter.author}\n <@&984724664536412220>,<@&984724445761536000>")
            else:
                embed = disnake.Embed(  #creating embed
                title=f"Участник {member} был исключен!",
                description=f"{inter.author.mention} забанил пользователя. Причина указана ниже.",
                color=col,
                )   

                embed.set_author(
                name="РаБотяра",
                icon_url="https://i.pinimg.com/originals/6a/66/71/6a66713b29d5a6149ed34a8075287e6f.jpg",
                )
                embed.set_footer(
                text="Was Created//By Mayka/lovodiska",
                icon_url="https://i.pinimg.com/originals/70/fc/8b/70fc8b416e4d0202007b3cc7a035d92a.jpg",
                )

                embed.set_thumbnail(url="https://i.ytimg.com/vi/NHPjJ7JqTYY/maxresdefault.jpg%22")
                embed.set_image(url="https://i.ytimg.com/vi/Y3zZUfP277k/maxresdefault.jpg%22")

                embed.add_field(name="Участник был забанен по причине:", value=reason, inline=False)

                await inter.response.send_message(embed=embed)
                channellog = bot.get_channel(989527597081837578)
                await channellog.send(embed=embed)
                await member.ban(reason=reason)  
    @mod.sub_command(name="kick",description="Кикает участника[Администрация]") #Register a command, give it a name and description
    async def kick(inter,member: disnake.Member,reason): #creating def|command
        csl.execute("""SELECT admin FROM useres WHERE username = ?""",(f'{inter.author}',))
        admin = csl.fetchall()
        if admin[0][0] == 0:
            pass
        else:
            csl.execute("""SELECT adminlvl FROM useres WHERE username = ? """,(f'{inter.author}',))
            adminlvl = csl.fetchall()
            if adminlvl[0][0] <= 3:
                channelhelp = bot.get_channel(989836560516120597)                
                await channelhelp.send(f"Kick {member.mention} reason: {reason}//By {inter.author}\n <@&984724664536412220>,<@&984724445761536000>")
            else:
                embed = disnake.Embed( 
                title=f"Участник {member} был исключен!",
                description=f"{inter.author.mention} исключил пользователя. Причина указана ниже.",
                color=col,
                )

                embed.set_author( 
                name="Err.0rth",
                icon_url="https://i.pinimg.com/originals/6a/66/71/6a66713b29d5a6149ed34a8075287e6f.jpg",
                )
                embed.set_footer(
                text="Was Created//By Mayka",
                icon_url="https://i.pinimg.com/originals/70/fc/8b/70fc8b416e4d0202007b3cc7a035d92a.jpg",
                )

                embed.set_thumbnail(url="https://i.ytimg.com/vi/NHPjJ7JqTYY/maxresdefault.jpg%22")
                embed.set_image(url="https://i.ytimg.com/vi/Y3zZUfP277k/maxresdefault.jpg%22")

                embed.add_field(name="Участник был кикнут по причине:", value=reason, inline=False)
                await inter.response.send_message(embed=embed)
                await member.kick(reason=reason)
                authors = inter.author
                meser = member
                reason = reason
                channellog = bot.get_channel(989527597081837578)
                await channellog.send(embed=embed)
                await logging_kick(inter,authors,meser,reason,0)    
class server():
    @bot.slash_command()
    async def server(inter):
        pass
    @server.sub_command_group()
    async def get(inter):
        pass
    @get.sub_command(name='server-info')
    async def sin(inter: CommandInteraction):
        embed = disnake.Embed(
            description=f'Server Name: {inter.guild.name}\n Member Count: {inter.guild.member_count}'
        )
        await inter.send(embed=embed)
async def msg20(inter: CommandInteraction):
    await inter.send("SA")
@bot.event
async def on_message(inter: CommandInteraction):
    csl.execute("""INSERT OR IGNORE INTO useres(username,admin,warn,adminlvl) VALUES(?,?,?,?)""",(f"{inter.author}",0,0,0))
    csl.execute("""SELECT * FROM useres""")
    csl.execute("""CREATE TABLE IF NOT EXISTS provoice(username VARCHAR(255) PRIMARY KEY,channel_name VARCHAR(255),channel_id BIGINT)""")
    csl.execute("""SELECT * FROM provoice""")
    conn.commit()
    res2 = csl.fetchall()    
    print(res2)
    conn.commit()
    
bot.run(TOKEN)
