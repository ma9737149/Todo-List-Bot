import discord,sqlite3,random,datetime
from discord.ext import commands,tasks
from discord import app_commands
from config import channel



















class check_is_task(discord.ui.View):
    def __init__(self,user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

    async def check_role(self, interaction, point):
        db = sqlite3.connect("roles.db")
        cr = db.cursor()
        cr.execute("CREATE TABLE IF NOT EXISTS roles(role_id INTEGER,guild_id INTEGER,points INTEGER)")
        cr.execute('SELECT role_id, points FROM roles WHERE guild_id = ? ORDER BY points DESC', (interaction.guild.id,))

        my_data = cr.fetchall()

        con = sqlite3.connect("rank.db")
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS rank(points INTEGER,user_id INTEGER,guild_id INTEGER)")

        cur.execute('SELECT points FROM rank WHERE guild_id = ? AND user_id = ?', (interaction.guild.id, interaction.user.id))
        my_point = cur.fetchone()[0]


        for role_id, points in my_data:
            role_1 = interaction.guild.get_role(role_id)
            if point >= points:

                if role_1 not in interaction.user.roles:   

                    for _role_id,points in my_data:
                        role_to_remove = interaction.guild.get_role(_role_id)
                        await interaction.user.remove_roles(role_to_remove)

                    await interaction.user.add_roles(role_1)
                    db.close()
                    con.close()
                    return await interaction.channel.send(f"مبروك {interaction.user.mention} الآن معك الرتبة {role_1.mention} ونقاطك الآن هي {my_point}")
                break


    @discord.ui.button(label="نعم",style=discord.ButtonStyle.green,emoji="✅")
    async def _agree(self,interaction:discord.Interaction,button:discord.ui.button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لايمكنك استخدام هذا ال embed",ephemeral=True)
        
        con = sqlite3.connect("rank.db")
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS rank(points INTEGER,user_id INTEGER,guild_id INTEGER)")
        
        cur.execute("SELECT points FROM rank WHERE guild_id= ? AND user_id = ?",(interaction.guild.id,interaction.user.id))
        my_data = cur.fetchone()
        

        if my_data:
            point = my_data[0]

            db = sqlite3.connect("roles.db")
            cr = db.cursor()
            cr.execute("CREATE TABLE IF NOT EXISTS roles(role_id INTEGER,guild_id INTEGER,points INTEGER)") 

            my_random = random.randint(1,10)
            cur.execute("UPDATE rank SET points = ? WHERE guild_id = ? AND user_id = ?",(point+my_random,interaction.guild.id,interaction.user.id))
            
            db.commit()
            db.close()
            con.commit()
            con.close()

            await self.check_role(interaction,point+my_random)
            await interaction.response.send_message(f"تم اضافة {my_random} نقطة لك")

            w_db = sqlite3.connect("warn.db")
            w_cur = w_db.cursor()
            w_cur.execute("CREATE TABLE IF NOT EXISTS warn(user_id INTEGER,guild_id INTEGER,warns INTEGER,timestamp INTEGER)")


            w_cur.execute("SELECT timestamp FROM warn WHERE user_id=? AND guild_id=?", (interaction.user.id, interaction.guild.id))
            timestamp = w_cur.fetchone()

            if timestamp:
                w_cur.execute("UPDATE warn SET timestamp = ? WHERE user_id = ? AND guild_id = ?",(int(datetime.datetime.utcnow().timestamp()), interaction.user.id, interaction.guild.id))
                w_db.commit()
                w_db.close()

            else:
                w_cur.execute("INSERT INTO warn(user_id, guild_id,warns ,timestamp) VALUES(?, ?, ?,?)",(interaction.user.id, interaction.guild.id, 0 ,int(datetime.datetime.utcnow().timestamp())))
                w_db.commit()
                w_db.close()

        else:
            await interaction.response.send_message("لايوجد لديك نقاط حاليا يجب عليك استخدام الامر register",ephemeral=True)

    @discord.ui.button(label="لا",style=discord.ButtonStyle.red,emoji="❌")
    async def _disagree(self,interaction:discord.Interaction,button:discord.ui.button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لايمكنك استخدام هذا ال embed",ephemeral=True)
        await interaction.response.send_message("تم الغاء الامر",ephemeral=True)



class Rank(commands.Cog):
    def __init__(self,client):
        self.client = client

        


    async def check_role(self, interaction, point,member):
        db = sqlite3.connect("roles.db")
        cr = db.cursor()
        cr.execute("CREATE TABLE IF NOT EXISTS roles(role_id INTEGER,guild_id INTEGER,points INTEGER)")

        cr.execute('SELECT role_id, points FROM roles WHERE guild_id = ? ORDER BY points DESC', (interaction.guild.id,))
        my_data = cr.fetchall()

        con = sqlite3.connect("rank.db")
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS rank(points INTEGER,user_id INTEGER,guild_id INTEGER)")



        cur.execute('SELECT points FROM rank WHERE guild_id = ? AND user_id = ?', (interaction.guild.id, member.id))
        my_point = cur.fetchone()[0]


        for role_id, points in my_data:
                role_1 = interaction.guild.get_role(role_id)
                if point >= points:

                    if role_1 not in member.roles:   

                        for _role_id,points in my_data:
                            role_to_remove = interaction.guild.get_role(_role_id)
                            await member.remove_roles(role_to_remove)

                        await member.add_roles(role_1)
                        db.close()
                        con.close()
                        return await interaction.channel.send(f"مبروك {member.mention} الآن معك الرتبة {role_1.mention} ونقاطك الآن هي {my_point}")
                    break
                else:
                    for role_id, points in my_data:
                        if point < points:
                            role_1 = interaction.guild.get_role(role_id)
                            if role_1 in member.roles:
                                await member.remove_roles(role_1)








    @app_commands.command(name="leaderboard",description="إظهار أعلي اشخاص في عدد النقاط")
    async def _leaderboard(self,interaction:discord.Interaction,limit:int=2):

        con = sqlite3.connect("rank.db")
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS rank(points INTEGER,user_id INTEGER,guild_id INTEGER)")

        cur.execute(f"SELECT user_id,points FROM rank WHERE guild_id=? ORDER BY points DESC LIMIT {limit}", (interaction.guild.id,))
        my_data = cur.fetchall()

        if 0 < limit < 11 and my_data:
            embed = discord.Embed(title="Leaderboard", color=discord.Colour.dark_gold())
            embed.set_footer(text=f"requested-by:{interaction.user.display_name}", icon_url=interaction.user.avatar)

            for index, (user_id, points) in enumerate(my_data, start=1):
                member = interaction.guild.get_member(user_id)
                embed.add_field(name=f"`#{index}`|{member.display_name}:", value=f"**Points:{points}**", inline=False)

            con.close()
            await interaction.response.send_message(embed=embed)


        # [(user_id,points)]
        else:
            con.close()
            return await interaction.response.send_message(f"لايمكنك إدخال قيمة أكبر من عدد القيم او اصغر من ال1",ephemeral=True)




            
            


        


    @commands.Cog.listener()
    async def on_message(self, message):
            

            await self.client.process_commands(message)

            


            if message.channel.id == channel:
                if message.author.bot:
                    return

                con = sqlite3.connect("rank.db")
                cur = con.cursor()
                cur.execute("CREATE TABLE IF NOT EXISTS rank(points INTEGER,user_id INTEGER,guild_id INTEGER)")


                cur.execute("SELECT points FROM rank WHERE user_id=? AND guild_id=?", (message.author.id, message.guild.id))
                point = cur.fetchone()

                if point:
                    db = sqlite3.connect("roles.db")

                    cr = db.cursor()
                    cr.execute("CREATE TABLE IF NOT EXISTS roles(role_id INTEGER,guild_id INTEGER,points INTEGER)")

                    cr.execute('SELECT role_id, points FROM roles WHERE guild_id=?', (message.guild.id,))
                    my_data = cr.fetchall()

                    db.close()
                    con.close()

                    my_msg = await message.channel.send(f"{message.author.mention} هل هذا انجازك", view=check_is_task(message.author.id))
                    await my_msg.delete(delay=3)









    @app_commands.command(name="points",description="إظهار عدد النقاط التي تمتلكها")
    async def _points(self,interaction:discord.Interaction,user:discord.Member=None):
        if user is None:
            member = interaction.user
        elif user.bot:
            return await interaction.response.send_message("البوتات ليست لديها نقاط",ephemeral=True)
        else:
            member = user

        con = sqlite3.connect("rank.db")
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS rank(points INTEGER,user_id INTEGER,guild_id INTEGER)")

        points = cur.execute("SELECT points FROM rank WHERE user_id=? AND guild_id = ?",(member.id,interaction.guild.id)).fetchone()
  
        if points is not None:
            user_points = points[0]
            embed = discord.Embed(title="",description=f"{member.mention} هذه هي نقاطك {user_points}",colour=discord.Colour.dark_gold())
            embed.set_footer(text=f"requested-by:{interaction.user.name}",icon_url=interaction.user.avatar)
            await interaction.response.send_message(embed=embed)
            con.close()
        else:
            con.close()
            return await interaction.response.send_message(f"ليست لديك نقاط حالياً {member.mention}",ephemeral=True)

    #Admin_Cmds












        
        

    @app_commands.command(name="show_ranks",description="اظهار الرتب مع النقاط المطلوب")
    async def _show_ranks(self,interaction:discord.Interaction):

        db = sqlite3.connect("roles.db")
        cr = db.cursor()
        cr.execute("CREATE TABLE IF NOT EXISTS roles(role_id INTEGER,guild_id INTEGER,points INTEGER)")

        cr.execute("SELECT role_id,points FROM roles WHERE guild_id=?",(interaction.guild.id,))
        my_data = cr.fetchall()
        if my_data:
            embed = discord.Embed(title="الرتب الموجودة",color=discord.Colour.dark_blue())
            for role,points in my_data:
                role_ = interaction.guild.get_role(role)
                embed.add_field(name=f"Points `{points}`", value=f"Role: {role_.mention}", inline=True)
            
            db.close()
            await interaction.response.send_message(embed=embed)
        else:
            db.close()
            await interaction.response.send_message("لايوجد رتب",ephemeral=True)




async def setup(client):
    await client.add_cog(Rank(client))