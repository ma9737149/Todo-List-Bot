import discord,sqlite3
from discord.ext import commands
from discord import app_commands


















class Moderation(commands.Cog):
    def __init__(self,client):
        self.client = client






    @app_commands.command(name="admin-set_points", description="جعل النقاط لعدد معين")
    @app_commands.checks.has_permissions(administrator=True)
    async def _set_points(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if member.bot:
            return await interaction.response.send_message("البوتات ليست لديها نقاط", ephemeral=True)

        if amount < 0:
            return await interaction.response.send_message("لايمكن اضافه قيمة سالبه")   

        con = sqlite3.connect("rank.db")
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS rank(points INTEGER,user_id INTEGER,guild_id INTEGER)")

        cur.execute("SELECT points FROM rank WHERE user_id = ? AND guild_id = ?", (member.id, interaction.guild.id))
        points = cur.fetchone()[0]
        if points >= 0:
            cur.execute("UPDATE rank SET points = ? WHERE user_id = ? AND guild_id = ?", (amount, member.id, interaction.guild.id))
            con.commit()
            con.close()

            await self.check_role(interaction, amount,member)
            await interaction.response.send_message(f"تم جعل النقاط إلي {amount}",ephemeral=True)

        else:
            
            await interaction.response.send_message("لايوجد أي نقاط عند هذا العضو", ephemeral=True)
    @app_commands.command(name="admin-inc_points",description="زيادة عدد النقاط")
    @app_commands.checks.has_permissions(administrator=True)
    async def _inc_points(self,interaction:discord.Interaction,member:discord.Member,amount:int):
        if member.bot:
            return await interaction.response.send_message("البوتات ليست لديها نقاط",ephemeral=True)

        if amount < 1:
            return await interaction.response.send_message("لايمكن اضافه قيمة سالبه")    

        con = sqlite3.connect("rank.db")
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS rank(points INTEGER,user_id INTEGER,guild_id INTEGER)")

        cur.execute("SELECT points FROM rank WHERE user_id = ? AND guild_id = ?",(member.id,interaction.guild.id))
        points = cur.fetchone()[0]
        if points == 0 or points >= 1:
           inc_points = points + amount
           cur.execute("UPDATE rank SET points = ? WHERE user_id = ? AND guild_id = ?",(inc_points,member.id,interaction.guild.id))
           con.commit()
           con.close()

           await self.check_role(interaction,inc_points,member)
           await interaction.response.send_message(f"تمت زياده نقاط العضو إلي {amount} نقطة")
        else:
            con.close()
            await interaction.response.send_message("لايوجد أي نقاط عند هذا العضو",ephemeral=True)

    @app_commands.command(name="admin-dec_points",description="تقليل عدد النقاط")
    @app_commands.checks.has_permissions(administrator=True)
    async def _dec_points(self,interaction:discord.Interaction,member:discord.Member,amount:int):
        if member.bot:
            return await interaction.response.send_message("البوتات ليست لديها نقاط",ephemeral=True)

        if amount < 1:
            return await interaction.response.send_message("لايمكن اضافه قيمة سالبه")    

        con = sqlite3.connect("rank.db")
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS rank(points INTEGER,user_id INTEGER,guild_id INTEGER)")


        cur.execute("SELECT points FROM rank WHERE user_id = ? AND guild_id = ?",(member.id,interaction.guild.id))
        points = cur.fetchone()[0]
        if points > 0:
           dec_points = points - amount
           cur.execute("UPDATE rank SET points = ? WHERE user_id = ? AND guild_id = ?",(dec_points,member.id,interaction.guild.id))
           con.commit()
           con.close()

           await self.check_role(interaction,dec_points,member)
           await interaction.response.send_message(f"تم تقليل {amount} من نقاط العضو",ephemeral=True)
        else:
            con.close()
            await interaction.response.send_message("لايوجد أي نقاط عند هذا العضو",ephemeral=True)

    @app_commands.command(name="admin-reset_points",description="إعاده نقاط العضو إلي 0")
    @app_commands.checks.has_permissions(administrator=True)
    async def _reset_points(self,interaction:discord.Interaction,member:discord.Member):
        if member.bot:
            return await interaction.response.send_message("البوتات ليست لديها نقاط",ephemeral=True)

        con = sqlite3.connect("rank.db")
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS rank(points INTEGER,user_id INTEGER,guild_id INTEGER)")

    
        cur.execute("SELECT points FROM rank WHERE user_id = ? AND guild_id = ?",(member.id,interaction.guild.id))
        points = cur.fetchone()[0]
        if points:
           reset_value = 0
           cur.execute("UPDATE rank SET points = ? WHERE user_id = ? AND guild_id = ?",(reset_value,member.id,interaction.guild.id))
           con.commit()
           con.close()

           db = sqlite3.connect("roles.db")
           cr = db.cursor()
           cr.execute("CREATE TABLE IF NOT EXISTS roles(role_id INTEGER,guild_id INTEGER,points INTEGER)")

           cr.execute('SELECT role_id, points FROM roles WHERE guild_id = ?', (interaction.guild.id,))
           my_data = cr.fetchall()
           for _role_id,points in my_data:
                role_to_remove = interaction.guild.get_role(_role_id)
                await member.remove_roles(role_to_remove)
           db.close()

           await interaction.response.send_message("تمت اعاده نقاط العضو إلي 0 نقطه",ephemeral=True)
        else:
            con.close()
            await interaction.response.send_message("لايوجد أي نقاط عند هذا العضو",ephemeral=True)


    @app_commands.command(name="admin-set_rank", description="جعل رتبه يتم اخذها تلقائياً حسب الزيادة في النقاط")
    @app_commands.checks.has_permissions(administrator=True)
    async def _set_rank(self, interaction: discord.Interaction, role: discord.Role, points: int):


        db = sqlite3.connect("roles.db")
        cr = db.cursor()
        cr.execute("CREATE TABLE IF NOT EXISTS roles(role_id INTEGER,guild_id INTEGER,points INTEGER)")


        cr.execute("SELECT role_id FROM roles WHERE guild_id=?", (interaction.guild.id,))
        my_data = cr.fetchall()

        if my_data:
            role_ids = [data[0] for data in my_data]  # Extract role IDs from the retrieved data
            if role.id in role_ids:
                db.close()
                return await interaction.response.send_message("هذه الرتبه موجودة بالفعل", ephemeral=True)
            else:
                cr.execute("INSERT INTO roles(role_id, guild_id, points) VALUES(?, ?, ?)",
                        (role.id, interaction.guild.id, points))
                db.commit()
                db.close()

                await interaction.response.send_message("تم وضع الرتبه بنجاح", ephemeral=True)
        else:
            cr.execute("INSERT INTO roles(role_id, guild_id, points) VALUES(?, ?, ?)",
                    (role.id, interaction.guild.id, points))
            db.commit()
            db.close()

            await interaction.response.send_message("تم وضع الرتبه بنجاح", ephemeral=True)
            
    @app_commands.command(name="admin-remove_rank",description="إزاله رتبه من الرتب")
    async def _remove_rank(self,interaction:discord.Interaction,role:discord.Role):
        db = sqlite3.connect("roles.db")
        cr = db.cursor()
        cr.execute("DELETE FROM roles WHERE role_id=? AND guild_id=?",(role.id,interaction.guild.id))
        db.commit()
        db.close()

        guild = interaction.guild
        role_to_remove = discord.utils.get(guild.roles, id=role.id)
        if role_to_remove:
            members_with_role = await guild.fetch_members()
            for member in members_with_role:
                await member.remove_roles(role_to_remove)



        await interaction.response.send_message(f"تمت العملية بنجاح وتم إزاله الرتب {role.mention}",ephemeral=True)

async def setup(client):
    await client.add_cog(Moderation(client))