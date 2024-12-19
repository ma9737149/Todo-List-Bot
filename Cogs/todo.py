from typing import Any
import discord,sqlite3,random,datetime
from discord.ext import commands,tasks
from discord import app_commands
from discord.interactions import Interaction
from config import channel












class Todo(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.check_sent.start()

    @tasks.loop(seconds=10)
    async def check_sent(self):

        w_db = sqlite3.connect("warn.db")
        w_cur = w_db.cursor()
        w_cur.execute("CREATE TABLE IF NOT EXISTS warn(user_id INTEGER,guild_id INTEGER,warns INTEGER,timestamp INTEGER)")

        w_cur.execute("SELECT timestamp,user_id,warns,guild_id FROM warn")
        my_data = w_cur.fetchall()#[(timestamp,user_id,warns,guild_id)]
        for timestamp,user_id,warns,guild_id in my_data:
            if (int(datetime.datetime.utcnow().timestamp()) - timestamp)/3600 >= 24*3:
                if warns == 1:
                    continue
                else:
                    my_new_warns = warns+1
                    w_cur.execute("UPDATE warn SET warns=? WHERE user_id=? AND guild_id=?",(my_new_warns,user_id,guild_id))
                    w_db.commit()
                    w_db.close()

                    channel_ = self.client.get_channel(channel) 

                    await channel_.send(f"<@{user_id}> لماذا لم ترسل لمده 3 أيام؟")

            elif (int(datetime.datetime.utcnow().timestamp()) - timestamp)/3600 >= 24*7:
                if warns == 2:
                    continue
                else:
                    my_new_warns = warns+1
                    w_cur.execute("UPDATE warn SET warns=? WHERE user_id=? AND guild_id=?",(my_new_warns,user_id,guild_id))
                    w_db.commit()
                    w_db.close()

                    channel_ = self.client.get_channel(channel)                   
                    await channel_.send(f"<@{user_id}> لماذا لم ترسل لمده 7 أيام؟")

            elif (int(datetime.datetime.utcnow().timestamp()) - timestamp)/3600 >= 24*8:

                    con = sqlite3.connect("rank.db")
                    cur = con.cursor()
                    cur.execute("CREATE TABLE IF NOT EXISTS rank(points INTEGER,user_id INTEGER,guild_id INTEGER)")

                    db = sqlite3.connect("todo.db")
                    cr = db.cursor()
                    cr.execute("CREATE TABLE IF NOT EXISTS tasks(task TEXT,task_description VARCHAR,is_checked VARCHAR,user_id INTEGER,guild_id INTEGER,id INTEGER AUTOINCREMENT)")

                    w_cur.execute("UPDATE warn SET warns=? WHERE user_id=? AND guild_id=?",(0,user_id,guild_id))
                    cr.execute("DELETE FROM tasks WHERE user_id=? AND guild_id = ?",(user_id,guild_id))
                    cur.execute("DELETE FROM rank WHERE user_id=? AND guild_id = ?",(user_id,guild_id))

                    con.commit()
                    w_db.commit()
                    db.commit()

                    con.close()
                    w_db.close()
                    db.close()


                    channel_ = self.client.get_channel(channel)     

                    await channel_.send(f"<@{user_id}> لماذا لم ترسل لمده 8 أيام؟")
            





    @app_commands.command(name="register",description="التسجيل في البوت وضبط قائمة المهام")
    async def _register(self,interaction:discord.Interaction):
        db = sqlite3.connect("todo.db")
        cr = db.cursor()
        cr.execute("CREATE TABLE IF NOT EXISTS tasks(task TEXT,task_description VARCHAR,is_checked VARCHAR,user_id INTEGER,guild_id INTEGER,id INTEGER PRIMARY KEY AUTOINCREMENT)")   

        cr.execute("SELECT * FROM tasks WHERE user_id=? AND guild_id = ?",(interaction.user.id,interaction.guild.id))
        data0 = cr.fetchall()
        if data0:
            db.close()
            await interaction.response.send_message(f"أنت جهزت قائمة المهام من قبل يمكنك استدعائها بإستخدام الأمر <list> وتعديل القائمة",ephemeral=True)

        else:
            data = [
                ("دوبامين ديتوكس","هل قللت استهلاكك للدوبامين؟","❌",interaction.user.id,interaction.guild.id),
                ("صلاة","هل صليت كل الصلوات؟","❌",interaction.user.id,interaction.guild.id),
                ("تدوين","هل اجبت علي اهم اسئلتك","❌",interaction.user.id,interaction.guild.id),
                ("النوم","هل رتبت السرير ونمت بعدد ساعات كافية؟","❌",interaction.user.id,interaction.guild.id),
                ("استحمام بماء بارد","هل استحميت بماء بارد؟","❌",interaction.user.id,interaction.guild.id),
                ("رياضة","هل سويت تمارين وكارديو؟","❌",interaction.user.id,interaction.guild.id),
                ("قراءة","هل قرأت او استمعت لكتاب، مقال،..؟","❌",interaction.user.id,interaction.guild.id),
                ("تنوير","هل قاومت او واجهت كل شيء صعب؟","❌",interaction.user.id,interaction.guild.id)

            ]



            cr.executemany("INSERT INTO tasks(task,task_description,is_checked,user_id,guild_id) VALUES(?,?,?,?,?)",data)
            db.commit()
            db.close()

            con = sqlite3.connect("rank.db")
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS rank(points INTEGER,user_id INTEGER,guild_id INTEGER)")

            cur.execute("INSERT INTO rank(points,guild_id,user_id) VALUES(?,?,?)",(0,interaction.guild.id,interaction.user.id))
            con.commit()
            con.close()


            await interaction.response.send_message("يمكنك الأن استخدام الأمر <list> لتعديل مهامك والقيام بها وحذفها وإلخ",ephemeral=True)

    @app_commands.command(name="quit",description="الخروج وحذف قائمة المهام")
    async def _quit(self,interaction:discord.Interaction):

        w_db = sqlite3.connect("warn.db")
        w_cur = w_db.cursor()
        w_cur.execute("CREATE TABLE IF NOT EXISTS warn(user_id INTEGER,guild_id INTEGER,warns INTEGER,timestamp INTEGER)")

        db = sqlite3.connect("todo.db")
        cr = db.cursor()
        cr.execute("CREATE TABLE IF NOT EXISTS tasks(task TEXT,task_description VARCHAR,is_checked VARCHAR,user_id INTEGER,guild_id INTEGER,id INTEGER PRIMARY KEY AUTOINCREMENT)")   

        
        w_cur.execute("DELETE FROM warn WHERE user_id=? AND guild_id=?",(interaction.user.id,interaction.guild.id))
        cr.execute("DELETE FROM tasks WHERE user_id=? AND guild_id = ?",(interaction.user.id,interaction.guild.id))

        con = sqlite3.connect("rank.db")
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS rank(points INTEGER,user_id INTEGER,guild_id INTEGER)")



        cur.execute("DELETE FROM rank WHERE user_id=? AND guild_id = ?",(interaction.user.id,interaction.guild.id))

        con.commit()
        w_db.commit()            
        db.commit()

        con.close()
        w_db.close()
        db.close()


        await interaction.response.send_message("تم الخروج والحذف بالكامل وتصفير كل شئ",ephemeral=True)





    @app_commands.command(name="list",description="إظهار قائمة المهام")
    async def _list(self,interaction:discord.Interaction):
        

        db = sqlite3.connect("todo.db")
        cr = db.cursor()
        cr.execute("CREATE TABLE IF NOT EXISTS tasks(task TEXT,task_description VARCHAR,is_checked VARCHAR,user_id INTEGER,guild_id INTEGER,id INTEGER PRIMARY KEY AUTOINCREMENT)")


        cr.execute("SELECT task,task_description,is_checked,id FROM tasks WHERE user_id=? AND guild_id = ?",(interaction.user.id,interaction.guild.id))
        data = cr.fetchall()
        db.close()
        if data:
                embed = discord.Embed(title="قائمة المهام",description="",colour=discord.Colour.dark_gold())
                embed.set_author(name=interaction.user.name,icon_url=interaction.user.avatar)
                
                for i in range(len(data)):
                    embed.add_field(name=f"{data[i][3]}-{data[i][0]}|{data[i][2]}",value=data[i][1])



                
                await interaction.response.send_message(embed=embed, view=btns_view(interaction.user.id))
        else:
            db.close()
            await interaction.response.send_message("استخدم الامر register\nليتم تنظيم قائمة المهام لك ووضع المهام الافتراضية",ephemeral=True)




        




        



class check_task_modal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="انجاز مهمه",timeout=None)


    async def check_role(self, interaction, point):

        conn = sqlite3.connect("roles.db")
        cursor = conn.cursor()
        conn.execute("CREATE TABLE IF NOT EXISTS roles(role_id INTEGER,guild_id INTEGER,points INTEGER)")


        cursor.execute('SELECT role_id, points FROM roles WHERE guild_id = ? ORDER BY points DESC', (interaction.guild.id,))
        my_data = cursor.fetchall()

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
                    conn.close()
                    con.close()
                    await interaction.user.add_roles(role_1)
                    return await interaction.channel.send(f"مبروك {interaction.user.mention} الآن معك الرتبة {role_1.mention} ونقاطك الآن هي {my_point}")
                break


    

    task_id = discord.ui.TextInput(label="أدخل رقم المهمه",style=discord.TextStyle.short,required=True)
# 
    async def on_submit(self, interaction: discord.Interaction):

        db = sqlite3.connect("todo.db")
        cr = db.cursor()
        cr.execute("CREATE TABLE IF NOT EXISTS tasks(task TEXT,task_description VARCHAR,is_checked VARCHAR,user_id INTEGER,guild_id INTEGER)")        



        user_data_task = cr.execute("SELECT * FROM tasks WHERE id=? AND user_id=? AND guild_id=?",(self.task_id.value,interaction.user.id,interaction.guild.id)).fetchone()

        if not user_data_task:
            db.close()
            return await interaction.response.send_message("عذراً لايمكن إنجاز مهمة غير موجودة",ephemeral=True)
        
        con = sqlite3.connect("rank.db")
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS rank(points INTEGER,user_id INTEGER,guild_id INTEGER)")



        cur.execute("SELECT points FROM rank WHERE user_id = ? AND guild_id = ?",(interaction.user.id,interaction.guild.id))
    
        the_points_which_added = random.randint(1,10)
        the_new_points = cur.fetchone()[0] + the_points_which_added
        cur.execute("UPDATE rank SET points = ? WHERE user_id =? AND guild_id = ?",(the_new_points,interaction.user.id,interaction.guild.id))

        con.commit()
        con.close()


        await self.check_role(interaction,the_new_points)

        




        cr.execute('UPDATE tasks SET is_checked=? WHERE user_id=? AND guild_id=? AND id=?',("✅",interaction.user.id,interaction.guild.id,self.task_id.value))
        db.commit()






        
        


        cr.execute("SELECT * FROM tasks WHERE guild_id=? AND user_id=?",(interaction.guild.id,interaction.user.id))
        data = cr.fetchall()

        embed = discord.Embed(title="قائمة المهام",description="",colour=discord.Colour.dark_gold())
        embed.set_author(name=interaction.user.name,icon_url=interaction.user.avatar)
        for i in range(len(data)):
            embed.add_field(name=f"{data[i][5]}-{data[i][0]}|{data[i][2]}",value=data[i][1])
        
        await interaction.message.edit(embed=embed)
        await interaction.response.send_message(f"تم إنجاز المهمة وتمت إضافة {the_points_which_added} لنقاطك",ephemeral=True)










        


class add_task_modal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="إضافه مهمه",timeout=None)

    task_name = discord.ui.TextInput(label="أدخل إسم المهمه",style=discord.TextStyle.short,required=True)
    task_description = discord.ui.TextInput(label="أدخل وصف للمهمه",style=discord.TextStyle.short,required=True,min_length=10,max_length=40)

    async def on_submit(self, interaction: discord.Interaction):

        db = sqlite3.connect("todo.db")
        cr = db.cursor()
        cr.execute("CREATE TABLE IF NOT EXISTS tasks(task TEXT,task_description VARCHAR,is_checked VARCHAR,user_id INTEGER,guild_id INTEGER,id INTEGER PRIMARY KEY AUTOINCREMENT)")     



        cr.execute("SELECT task FROM tasks WHERE guild_id= ? AND user_id=?",(interaction.guild.id,interaction.user.id))
        data = cr.fetchall()

        print(len(data))

        if len(data)+1 >= 16:
            db.close()
            return await interaction.response.send_message("لايمنك اضافه مهمات اكثر من 16 مهمة",ephemeral=True)

        for i in range(len(data)):
            if data[i][0] == self.task_name.value:
                db.close()
                return await interaction.response.send_message(f"{interaction.user.mention} هذه المهمه موجودة بالفعل",ephemeral=True)


        cr.execute("INSERT INTO tasks(task,task_description,is_checked,user_id,guild_id) VALUES(?,?,?,?,?)",(self.task_name.value,self.task_description.value,"❌",interaction.user.id,interaction.guild.id))
        db.commit()

        cr.execute('SELECT * FROM tasks WHERE user_id=? AND guild_id=?',(interaction.user.id,interaction.guild.id))
        task_data = cr.fetchall()
        db.close()

        embed = discord.Embed(title="قائمة المهام",description="",colour=discord.Colour.dark_gold())
        embed.set_author(name=interaction.user.name,icon_url=interaction.user.avatar)
            

        for i in range(len(task_data)):
            embed.add_field(name=f"{task_data[i][5]}-{task_data[i][0]}|{task_data[i][2]}",value=task_data[i][1])

        await interaction.message.edit(embed=embed)





class btns_view(discord.ui.View):
    def __init__(self,user_id):
        super().__init__(timeout=None)

        self.user_id = user_id


        self.cooldown = commands.CooldownMapping.from_cooldown(1, 86400, commands.BucketType.member)





    @discord.ui.button(label="إضافة",style=discord.ButtonStyle.green)
    async def add_task(self,interaction:discord.Interaction,button:discord.ui.button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(f"{interaction.user.mention} هذه ليست قائمة مهامك",ephemeral=True)
        
        await interaction.response.send_modal(add_task_modal())

    @discord.ui.button(label="انجاز مهمه",style=discord.ButtonStyle.green)
    async def _check_task(self,interaction:discord.Interaction,button:discord.ui.button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(f"{interaction.user.mention} هذه ليست قائمة مهامك",ephemeral=True)

        await interaction.response.send_modal(check_task_modal())

    @discord.ui.button(label="تعديل",style=discord.ButtonStyle.blurple)
    async def _edit_btn(self,interaction:discord.Interaction,button:discord.ui.button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(f"{interaction.user.mention} هذه ليست قائمة مهامك",ephemeral=True)

        await interaction.response.send_modal(edit_task_modal())       



    @discord.ui.button(label="إزالة",style=discord.ButtonStyle.red)
    async def _remove_btn(self,interaction:discord.Interaction,button:discord.ui.button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(f"{interaction.user.mention} هذه ليست قائمة مهامك",ephemeral=True)
        await interaction.response.send_modal(remove_task_modal())



    @discord.ui.button(label="إزالة الجميع",style=discord.ButtonStyle.red)
    async def _del_all_tasks(self,interaction:discord.Interaction,button:discord.ui.button):
        if interaction.user.id != self.user_id:
            return  await interaction.response.send_message(f"{interaction.user.mention} هذه ليست قائمة مهامك",ephemeral=True)
        
        db = sqlite3.connect("todo.db")
        cr = db.cursor()
        cr.execute("SELECT task FROM tasks WHERE user_id=? AND guild_id = ?",(interaction.user.id,interaction.guild.id))

        main_tasks = [
                ("دوبامين ديتوكس"),
                ("صلاة"),
                ("تدوين"),
                ("النوم"),
                ("استحمام بماء بارد"),
                ("رياضة"),
                ("قراءة"),
                ("تنوير")

            ]

        tasks_what_user_have = cr.fetchall()  

        task_which_gonna_deleted = [x for x in tasks_what_user_have if x[0] not in main_tasks]

        if not task_which_gonna_deleted:
            return await interaction.response.send_message("لايوجد مهمات غير أساسية مضافة لقائمة المهام",ephemeral=True)

        else:
            for i in range(len(task_which_gonna_deleted)):
                cr.execute("DELETE FROM tasks WHERE task = ? AND user_id = ? AND guild_id = ?",(task_which_gonna_deleted[i][0],interaction.user.id,interaction.guild.id))


            data2 = cr.execute("SELECT * FROM tasks WHERE user_id = ? AND guild_id = ?",(interaction.user.id,interaction.guild.id)).fetchall()
            db.commit()
            db.close()    
            
                    
            embed = discord.Embed(title="قائمة المهام",description="",colour=discord.Colour.dark_gold())
            embed.set_author(name=interaction.user.name,icon_url=interaction.user.avatar)
                    
            for i in range(len(data2)):
                embed.add_field(name=f"{data2[i][0]}|{data2[i][2]}",value=data2[i][1])

            await interaction.message.edit(embed=embed)
            await interaction.response.send_message("تمت العمليه بنجاح",ephemeral=True)




    @discord.ui.button(label="إزالة جميع الإنجازات", style=discord.ButtonStyle.red)
    async def _un_check_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(f"{interaction.user.mention} هذه ليست قائمة مهامك",ephemeral=True)

        bucket = self.cooldown.get_bucket(interaction.message)
        retry = bucket.update_rate_limit()


        db = sqlite3.connect("todo.db")
        cr = db.cursor()

        cr.execute("SELECT task, is_checked FROM tasks WHERE user_id = ? AND guild_id = ?", (interaction.user.id, interaction.guild.id))
        lst_of_checked_or_not_data = cr.fetchall()

        tasks_updated = False

        for task, check in lst_of_checked_or_not_data:
            if check == "✅":
                cr.execute("UPDATE tasks SET is_checked = ? WHERE task = ? AND user_id = ? AND guild_id = ?", ("❌", task, interaction.user.id, interaction.guild.id))
                tasks_updated = True

            if retry:
                return await interaction.response.send_message(f"لا يمكنك استخدام هذا الزر إلا بعد {round(retry/3600, 1)} ساعة", ephemeral=True)



        if not tasks_updated:

            db.close()
            return await interaction.response.send_message("فشل في العثور على المهام التي تمت إنجازها", ephemeral=True)

        db.commit()  

        data2 = cr.execute("SELECT task,task_description,is_checked  FROM tasks WHERE user_id = ? AND guild_id = ?", (interaction.user.id, interaction.guild.id)).fetchall()
        db.close()


        options = [discord.SelectOption(label=task, description=task_desc,value=task) for task,task_desc,is_checked in data2 if task[2] == "❌"]



        embed = discord.Embed(title="قائمة المهام", description="", colour=discord.Colour.dark_gold())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)

        for i in range(len(data2)):
            embed.add_field(name=f"{data2[i][0]}|{data2[i][2]}", value=data2[i][1])

        await interaction.message.edit(embed=embed,view=self)
        await interaction.response.send_message("تمت العملية بنجاح", ephemeral=True)

        






    

class remove_task_modal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="احذف مهمه",timeout=None)
    
    task_id = discord.ui.TextInput(label="أدخل رقم المهمه",style=discord.TextStyle.short,required=True)


    async def on_submit(self, interaction: discord.Interaction):
        main_tasks = [
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    7,
                    8

                    ]
        if self.task_id in main_tasks:
            return await interaction.response.send_message("لايمكنك ازاله المهام الاساسيه",ephemeral=True)

        db = sqlite3.connect("todo.db")
        cursor = db.cursor()
        cursor.execute("SELECT task FROM tasks WHERE guild_id= ? AND user_id=? AND id=?",(interaction.guild.id,interaction.user.id,self.task_id.value))
        data = cursor.fetchone()

        if data :
            cursor.execute("DELETE FROM tasks WHERE guild_id=? AND user_id=? AND id=?",(interaction.guild.id,interaction.user.id,self.task_id.value))
            
            db.commit()
            cursor.execute("SELECT * FROM tasks WHERE guild_id = ? AND user_id = ?",(interaction.guild.id,interaction.user.id))
            edited_data = cursor.fetchall()
            db.close()
            embed = discord.Embed(title="قائمة المهام",description="",colour=discord.Colour.dark_gold())
            embed.set_author(name=interaction.user.name,icon_url=interaction.user.avatar)
            

            for i in range(len(edited_data)):
                embed.add_field(name=f"{edited_data[i][5]}-{edited_data[i][0]}|{edited_data[i][2]}",value=edited_data[i][1])

            await interaction.message.edit(embed =embed ,view=self.view)
            await interaction.response.send_message("تم بنجاح",ephemeral=True)

        else:
            db.close()
            return await interaction.response.send_message("لم يتم  العثور علي المهمة",ephemeral=True)

        


class edit_task_modal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Edit_Task",timeout=None)

    task_id = discord.ui.TextInput(label="ادخل رقم المهمة",style = discord.TextStyle.short,min_length=1,max_length=2,required=True)
    task_name = discord.ui.TextInput(label="ادخل اسم المهمة لتعديلها",style = discord.TextStyle.short,required=True)
    task_description = discord.ui.TextInput(label=" ادخل وصف المهمة التي تريد تعديلها",style = discord.TextStyle.short,min_length=10,max_length=40,required = True)

    async def on_submit(self, interaction: discord.Interaction):
        main_tasks = [
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    7,
                    8

                    ]


        #checking
        if int(self.task_id.value) in main_tasks:
            return await interaction.response.send_message("لايمكنك تعديل المهام الأساسية")
         
        if isinstance(self.task_id.value , int):
            db.close()
            return await interaction.response.send_message("ادخل رقم المهمه صحيحاً ليس حروفاً")


        db = sqlite3.connect("todo.db")
        cur = db.cursor()

        cur.execute("SELECT * FROM tasks WHERE user_id = ? AND guild_id = ?",(interaction.user.id,interaction.guild.id))
        data = cur.fetchall()

        asin_data = cur.execute("SELECT id FROM tasks WHERE user_id = ? AND guild_id = ?",(interaction.user.id,interaction.guild.id)).fetchone()



        
        if self.task_name.value in data or self.task_description.value in data:
            db.close()
            return await interaction.response.send_message("لايمكنك تعديل لإسم او وصف موجود بقائمة المهام")



        if not asin_data:
            db.close()
            return await interaction.response.send_message("لايوجد مهمة بهذا الرقم")


        cur.execute("UPDATE tasks SET task = ? , task_description = ? WHERE id=? AND guild_id = ? AND user_id = ?",(self.task_name.value,self.task_description.value,self.task_id.value,interaction.guild.id,interaction.user.id))
        db.commit()

        cur.execute("SELECT * FROM tasks WHERE user_id = ? AND guild_id=?",(interaction.user.id,interaction.guild.id))
        _data = cur.fetchall()

        db.close()
        
        embed = discord.Embed(title="قائمة المهام",description="",colour=discord.Colour.dark_gold())
        embed.set_author(name=interaction.user.name,icon_url=interaction.user.avatar)
                
        for i in range(len(_data)):
            embed.add_field(name=f"{_data[i][5]}-{_data[i][0]}|{_data[i][2]}",value=_data[i][1])



        await interaction.message.edit(embed=embed)
        await interaction.response.send_message("تمت العملية بنجاح",ephemeral=True)

    











async def setup(client):
    await client.add_cog(Todo(client))