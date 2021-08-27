import requests
import json
import time
import datetime
import traceback
import hashlib
import sqlite3
import numpy as np
import xml.etree.ElementTree as ET
import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions

##### Variables #####

bot_token = ''
bots_prefix = "!"

#####################

#check if database is made and load it
db = sqlite3.connect('GeolHistory.db')
cursor = db.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS articles(message_id TEXT primary key, title TEXT, link TEXT, description TEXT, author TEXT, image TEXT)')
cursor.execute('CREATE TABLE IF NOT EXISTS config(value TEXT primary key, value_key TEXT, description TEXT)')


# setting bot prefix
bot = commands.Bot(command_prefix=commands.when_mentioned_or(bots_prefix))

# remove default help command
bot.remove_command('help')

@bot.event
async def on_ready():
    """On ready event!"""
    print("Logged in as " + str(bot.user))
    print("User ID: " + str(bot.user.id))
    await bot.change_presence(activity=discord.Game(name="Version 2.0.1"))
    
#ping commmand
@bot.command(pass_context=True)
async def ping(ctx):
    latency = ctx.bot.latency
    latency = latency * 1000
    latency = round(latency)
    await ctx.send("My ping is **{}ms**!".format(latency))

#change a help command for the bot
@bot.command()
async def ghelp(ctx): 
    try:
        #delete the senders message
        await ctx.message.delete()
    except Exception:
        print("not deleting message due to it being in a DM")
    
    #getting the nickname of the person who ran the command / made the quote
    userValue = await bot.fetch_user((ctx.message.author).id)
    summonersName = userValue.name
    
    embed = discord.Embed(name="help")
    embed.set_author(name="Quotebot commands:")
    embed.add_field(name="!removeadmin {@user / userid}", value="remove an admin", inline=False)
    embed.add_field(name="!addadmin {@user / userid}", value="add an admin", inline=False)
    embed.add_field(name="!setchannel {#channel / channelid}", value="change the notification channel", inline=False)
    embed.add_field(name="!setmessage {message}", value="change the message sent alongside the articles embed", inline=False)
    embed.add_field(name="!setchecking {True / False}", value="change whether you want the bot to automatically check for new articles or not", inline=False)
    embed.add_field(name="!setinterval {int}", value="change how often the bot checks for new articles (in seconds)", inline=False)
    embed.add_field(name="!config", value="show the bots configuration file", inline=False)
    embed.add_field(name="!update", value="manually check for new updates", inline=False)
    
    embed.set_footer(text = "summoned by: " + summonersName)
    embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/797768317170614272/f5dead14dbdc6f78416fd19eb948ad60.png?size=1024")
    await ctx.send(embed=embed)

#change remove an admin ID for the bot
@bot.command()
async def removeadmin(ctx): 
    try:
        #delete the senders message
        await ctx.message.delete()
    except Exception:
        print("not deleting message due to it being in a DM")
    
    #get admin IDs from db
    cursor.execute("SELECT value_key FROM config WHERE value = ?",("admin_ids",))
    admin_ids_array = cursor.fetchone()
    
    admin_ids_sting = ""
    
    for x in admin_ids_array:
        admin_ids_sting = admin_ids_sting + x + ","
        
    
    #get lead admins ID from db
    cursor.execute("SELECT value_key FROM config WHERE value = ?",("lead_admin",))
    leadAdmin = cursor.fetchone()
    
    #get owners ID from db
    cursor.execute("SELECT value_key FROM config WHERE value = ?",("owner_id",))
    ownerID = cursor.fetchone()
    
    allowed = False
    

    if str((ctx.message.author).id) == ownerID[0]:
        allowed = True

    elif str((ctx.message.author).id) == leadAdmin[0]:
        allowed = True
    
    if allowed == True:
        split_command = ctx.message.content.split()
        
        
        try:
            if len(split_command[1]) == 18:
                
                if split_command[1] in admin_ids_sting:
                    
                
                    admin_ids_sting = admin_ids_sting.replace(str(split_command[1]) + ",", '')
                    
                    if admin_ids_sting[-1] == ',':
                        admin_ids_sting = admin_ids_sting.rstrip(admin_ids_sting[-1])
                    
                    #updating the database
                    cursor.execute("UPDATE config SET value_key = (?) WHERE value = (?)",(admin_ids_sting,"admin_ids"))
                    db.commit()
                    Send = await ctx.send("the user <@!" + split_command[1] + "> is no longer an admin in relation to the bot")
                else:
                    Send = await ctx.send("the user <@!" + split_command[1] + "> isn't an admin therefore cannot be removed")
            
            elif len(split_command[1]) == 22:
                id_array_start = split_command[1].split("<@!")
                id_final = id_array_start[1].split(">")
                
                if id_final[0] in admin_ids_sting:
                    admin_ids_sting = admin_ids_sting.replace(str(id_final[0]) + ",", '')
                    
                    
                    if admin_ids_sting[-1] == ',':
                        admin_ids_sting = admin_ids_sting.rstrip(admin_ids_sting[-1])
                    
                    
                    #updating the database
                    cursor.execute("UPDATE config SET value_key = (?) WHERE value = (?)",(admin_ids_sting,"admin_ids"))
                    db.commit()
                    Send = await ctx.send("the user <@!" + id_final[0] + "> is no longer an admin in relation to the bot")
                else:
                    Send = await ctx.send("the user <@!" + id_final[0] + "> isn't an admin therefore cannot be removed")
                
            else:
                Send = await ctx.send("Please ensure you have formatted the command correctly\n`!removeadmin @user` or `!removeadmin 123456789012345678`")
        except:
            Send = await ctx.send("Please ensure you have formatted the command correctly\n`!removeadmin @user` or `!removeadmin 123456789012345678`")
    else:
        Send = await ctx.send("You don't have permission to use the command `removeadmin`")

#change add an admin ID for the bot
@bot.command()
async def addadmin(ctx): 
    try:
        #delete the senders message
        await ctx.message.delete()
    except Exception:
        print("not deleting message due to it being in a DM")
    
    #get admin IDs from db
    cursor.execute("SELECT value_key FROM config WHERE value = ?",("admin_ids",))
    admin_ids_array = cursor.fetchone()
    
    admin_ids_sting = ""
    
    for x in admin_ids_array:
        admin_ids_sting = admin_ids_sting + x + ","
        
    
    #get lead admins ID from db
    cursor.execute("SELECT value_key FROM config WHERE value = ?",("lead_admin",))
    leadAdmin = cursor.fetchone()
    
    #get owners ID from db
    cursor.execute("SELECT value_key FROM config WHERE value = ?",("owner_id",))
    ownerID = cursor.fetchone()
    
    allowed = False
    

    if str((ctx.message.author).id) == ownerID[0]:
        allowed = True

    elif str((ctx.message.author).id) == leadAdmin[0]:
        allowed = True
    
    if allowed == True:
        split_command = ctx.message.content.split()
        
        try:
            if len(split_command[1]) == 18:
                if split_command[1] in admin_ids_sting:
                    Send = await ctx.send("the user <@!" + split_command[1] + "> is already an admin in relation to the bot")
                else:
                    admin_ids_sting = admin_ids_sting + split_command[1]
                    
                    #updating the database
                    cursor.execute("UPDATE config SET value_key = (?) WHERE value = (?)",(admin_ids_sting,"admin_ids"))
                    db.commit()
                    Send = await ctx.send("the user <@!" + split_command[1] + "> is now an admin in relation to the bot")
            elif len(split_command[1]) == 22:
                id_array_start = split_command[1].split("<@!")
                id_final = id_array_start[1].split(">")
                
                if id_final[0] in admin_ids_sting:
                    Send = await ctx.send("the user " + split_command[1] + " is already an admin in relation to the bot")
                else:
                    admin_ids_sting = admin_ids_sting + id_final[0]
                    
                    #updating the database
                    cursor.execute("UPDATE config SET value_key = (?) WHERE value = (?)",(admin_ids_sting,"admin_ids"))
                    db.commit()
                    Send = await ctx.send("the user " + split_command[1] + " is now an admin in relation to the bot")
                
        except:
            Send = await ctx.send("Please ensure you have formatted the command correctly\n`!addadmin @user` or `!addadmin 123456789012345678`")
    else:
        Send = await ctx.send("You don't have permission to use the command `addadmin`")



#change the notification channel for the bot
@bot.command()
async def setchannel(ctx): 
    
    try:
        #delete the senders message
        await ctx.message.delete()
    except Exception:
        print("not deleting message due to it being in a DM")
    
    #get admin IDs from db
    cursor.execute("SELECT value_key FROM config WHERE value = ?",("admin_ids",))
    admin_ids = cursor.fetchone()
    admin_ids_array = str(admin_ids[0]).split(",")
    
    #get lead admins ID from db
    cursor.execute("SELECT value_key FROM config WHERE value = ?",("lead_admin",))
    leadAdmin = cursor.fetchone()
    
    #get owners ID from db
    cursor.execute("SELECT value_key FROM config WHERE value = ?",("owner_id",))
    ownerID = cursor.fetchone()
    
    allowed = False
    owner = False
    
    for x in admin_ids_array:
        if x == str((ctx.message.author).id):
            allowed = True
    
    if str((ctx.message.author).id) == ownerID[0]:
        allowed = True
        owner = True
    elif str((ctx.message.author).id) == leadAdmin[0]:
        allowed = True
    
    if allowed == True:
        #print(ctx.message.content)
        
        split_command = ctx.message.content.split()
        
        try:
            if len(split_command[1]) == 18:
                if type(int(split_command[1])) is int:
                    #updating the database
                    cursor.execute("UPDATE config SET value_key = (?) WHERE value = (?)",(split_command[1],"notification_channel"))
                    db.commit()
                    Send = await ctx.send("Notification channel updated to <#" + split_command[1] + ">")
                else:
                    Send = await ctx.send("Please ensure you have formatted the command correctly\n`!setchannel #channel` or `!setchannel 123456789012345678`")
            elif len(split_command[1]) == 21:
                if str((split_command[1])[0]) == "<" and str((split_command[1])[1]) == "#":
                    new_channel_array = (split_command[1]).split("#")
                    new_channel_array_final = (new_channel_array[1]).split(">")
                    
                    #updating the database
                    cursor.execute("UPDATE config SET value_key = (?) WHERE value = (?)",(new_channel_array_final[0],"notification_channel"))
                    db.commit()
                    Send = await ctx.send("Notification channel updated to " + split_command[1])
                else:
                    Send = await ctx.send("Please ensure you have formatted the command correctly\n`!setchannel #channel` or `!setchannel 123456789012345678`")
                
            else:
                Send = await ctx.send("Please ensure you have formatted the command correctly\n`!setchannel #channel` or `!setchannel 123456789012345678`")
            
        except:
            Send = await ctx.send("Please ensure you have formatted the command correctly\n`!setchannel #channel` or `!setchannel 123456789012345678`")
    else:
        Send = await ctx.send("You don't have permission to use the command `setchannel`")

#change message sent with the embed when a new article is released for the bot
@bot.command()
async def setmessage(ctx): 
    
    try:
        #delete the senders message
        await ctx.message.delete()
    except Exception:
        print("not deleting message due to it being in a DM")
    
    #get admin IDs from db
    cursor.execute("SELECT value_key FROM config WHERE value = ?",("admin_ids",))
    admin_ids = cursor.fetchone()
    admin_ids_array = str(admin_ids[0]).split(",")
    
    #get lead admins ID from db
    cursor.execute("SELECT value_key FROM config WHERE value = ?",("lead_admin",))
    leadAdmin = cursor.fetchone()
    
    #get owners ID from db
    cursor.execute("SELECT value_key FROM config WHERE value = ?",("owner_id",))
    ownerID = cursor.fetchone()
    
    allowed = False
    owner = False
    
    for x in admin_ids_array:
        if x == str((ctx.message.author).id):
            allowed = True
    
    if str((ctx.message.author).id) == ownerID[0]:
        allowed = True
        owner = True
    elif str((ctx.message.author).id) == leadAdmin[0]:
        allowed = True
    
    if allowed == True:
        try:
            split_command = ctx.message.content.split()
            del split_command[0]

            #join the message back together
            text = " ".join(split_command)
            
            if len(text) < 2000:
                #updating the database
                cursor.execute("UPDATE config SET value_key = (?) WHERE value = (?)",(text,"new_article_message"))
                db.commit()
                Send = await ctx.send("new artice message updated to \"" + text + "\"")
            else:
                Send = await ctx.send("The message must be less than 2000 characters")
        except:
            Send = await ctx.send("Please ensure you have formatted the command correctly\n`!setmessage {message}` eg. `!setmessage Hey, a new article has been released!`")
    else:
        Send = await ctx.send("You don't have permission to use the command `setmessage`")


#change the status of auto_checking for the bot
@bot.command()
async def setchecking(ctx): 
    
    try:
        #delete the senders message
        await ctx.message.delete()
    except Exception:
        print("not deleting message due to it being in a DM")
    
    #get admin IDs from db
    cursor.execute("SELECT value_key FROM config WHERE value = ?",("admin_ids",))
    admin_ids = cursor.fetchone()
    admin_ids_array = str(admin_ids[0]).split(",")
    
    #get lead admins ID from db
    cursor.execute("SELECT value_key FROM config WHERE value = ?",("lead_admin",))
    leadAdmin = cursor.fetchone()
    
    #get owners ID from db
    cursor.execute("SELECT value_key FROM config WHERE value = ?",("owner_id",))
    ownerID = cursor.fetchone()
    
    allowed = False
    owner = False
    
    for x in admin_ids_array:
        if x == str((ctx.message.author).id):
            allowed = True
    
    if str((ctx.message.author).id) == ownerID[0]:
        allowed = True
        owner = True
    elif str((ctx.message.author).id) == leadAdmin[0]:
        allowed = True
    
    if allowed == True:
        try:
            split_command = ctx.message.content.split()
            print(split_command)
            if split_command[1].lower() == "true":
                #updating the database
                cursor.execute("UPDATE config SET value_key = (?) WHERE value = (?)",("True","auto_checking"))
                db.commit()
                Send = await ctx.send("Auto checking updated to " + split_command[1])
            elif split_command[1].lower() == "false":
                #updating the database
                cursor.execute("UPDATE config SET value_key = (?) WHERE value = (?)",("False","auto_checking"))
                db.commit()
                Send = await ctx.send("Auto checking updated to " + split_command[1])
            else:
                Send = await ctx.send("Please ensure you have formatted the command correctly\n`!setchecking True` or `!setchecking False`")
        except:
            Send = await ctx.send("Please ensure you have formatted the command correctly\n`!setchecking True` or `!setchecking False`")
    else:
        Send = await ctx.send("You don't have permission to use the command `setchecking`")



#change the auto refresh interval for the bot
@bot.command()
async def setinterval(ctx): 
    
    try:
        #delete the senders message
        await ctx.message.delete()
    except Exception:
        print("not deleting message due to it being in a DM")
    
    #get admin IDs from db
    cursor.execute("SELECT value_key FROM config WHERE value = ?",("admin_ids",))
    admin_ids = cursor.fetchone()
    admin_ids_array = str(admin_ids[0]).split(",")
    
    #get lead admins ID from db
    cursor.execute("SELECT value_key FROM config WHERE value = ?",("lead_admin",))
    leadAdmin = cursor.fetchone()
    
    #get owners ID from db
    cursor.execute("SELECT value_key FROM config WHERE value = ?",("owner_id",))
    ownerID = cursor.fetchone()
    
    allowed = False
    owner = False
    
    for x in admin_ids_array:
        if x == str((ctx.message.author).id):
            allowed = True
    
    if str((ctx.message.author).id) == ownerID[0]:
        allowed = True
        owner = True
    elif str((ctx.message.author).id) == leadAdmin[0]:
        allowed = True
    
    if allowed == True:
        try:
            split_command = ctx.message.content.split()
            
            if int(split_command[1]) > 31536001 or int(split_command[1]) < 1:
                Send = await ctx.send("Please ensure you have set the interval within the bounds listed below\n**Min** = `1`\n**Max** = `31,536,001`")
            elif int(split_command[1]) < 60 and owner == False:
                Send = await ctx.send("Only the bot owner (<@!" + ownerID[0] + ">) can set the interval below 60 seconds")
            elif int(split_command[1]) < 60 and int(split_command[1]) > 0 and owner == True:
                #updating the database
                cursor.execute("UPDATE config SET value_key = (?) WHERE value = (?)",(split_command[1],"timeperiod"))
                db.commit()
                Send = await ctx.send("Auto checking interval updated to " + split_command[1])
            elif int(split_command[1]) > 59 and int(split_command[1]) < 31536002:
                #updating the database
                cursor.execute("UPDATE config SET value_key = (?) WHERE value = (?)",(split_command[1],"timeperiod"))
                db.commit()
                Send = await ctx.send("Auto checking interval updated to " + split_command[1])
        except:
            Send = await ctx.send("Please ensure you have formatted the command correctly\n`!setinterval 123`")
        
    else:
        Send = await ctx.send("You don't have permission to use the command `setinterval`")

#see all the current configs for the bot
@bot.command()
async def config(ctx):
    try:
        #delete the senders message
        await ctx.message.delete()
    except Exception:
        print("not deleting message due to it being in a DM")
        
    
    #get admin IDs from db
    cursor.execute("SELECT value_key FROM config WHERE value = ?",("admin_ids",))
    admin_ids = cursor.fetchone()
    admin_ids_array = str(admin_ids[0]).split(",")
    
    #get lead admins ID from db
    cursor.execute("SELECT value_key FROM config WHERE value = ?",("lead_admin",))
    leadAdmin = cursor.fetchone()
    
    #get owners ID from db
    cursor.execute("SELECT value_key FROM config WHERE value = ?",("owner_id",))
    ownerID = cursor.fetchone()
    
    allowed = False
    owner = False
    
    for x in admin_ids_array:
        if x == str((ctx.message.author).id):
            allowed = True
    
    if str((ctx.message.author).id) == ownerID[0]:
        allowed = True
        owner = True
    elif str((ctx.message.author).id) == leadAdmin[0]:
        allowed = True
    
    if allowed == True:
        #get all the values from db
        cursor.execute("SELECT * FROM config;")
        config_truple = cursor.fetchall()
        config_array = np.array(config_truple)
        
        
        #getting the nickname of the person who ran the command / made the quote
        userValue = await bot.fetch_user((ctx.message.author).id)
        summonersName = userValue.name
        
        #building the embed
        style = discord.Embed(name="config notification", title="Current Configuration", timestamp=datetime.datetime.utcnow(), color=0x28a4fd)
        style.set_footer(text = "summoned by " + summonersName)
        
        #loop to add all values from DB to the embed
        for x in range(len(config_array)):
            value_one = str(config_array[x][0])
            value_two = str(config_array[x][1])
            value_three = str(config_array[x][2])
            
            style.add_field(name= value_one + "\n(" + value_three + "):" , value= "`" + value_two + "`", inline=False)
        
        Send = await ctx.send(embed=style)
    
    else:
        Send = await ctx.send("You don't have permission to use the command `config`")
    

#manually check for new article
@bot.command()
async def update(ctx):
    
    try:
        #delete the senders message
        await ctx.message.delete()
    except Exception:
        print("not deleting message due to it being in a DM")
    
    #get channel ID from db
    cursor.execute("SELECT value_key FROM config WHERE value = ?",("notification_channel",))
    channelID = cursor.fetchone()
    channel = bot.get_channel(int(channelID[0])) # the message's channel
    
    #get admin IDs from db
    cursor.execute("SELECT value_key FROM config WHERE value = ?",("admin_ids",))
    admin_ids = cursor.fetchone()
    admin_ids_array = str(admin_ids[0]).split(",")
    
    #get lead admins ID from db
    cursor.execute("SELECT value_key FROM config WHERE value = ?",("lead_admin",))
    leadAdmin = cursor.fetchone()
    
    #get owners ID from db
    cursor.execute("SELECT value_key FROM config WHERE value = ?",("owner_id",))
    ownerID = cursor.fetchone()
    
    allowed = False
    owner = False
    
    for x in admin_ids_array:
        if x == str((ctx.message.author).id):
            allowed = True
    
    if str((ctx.message.author).id) == ownerID[0]:
        allowed = True
        owner = True
    elif str((ctx.message.author).id) == leadAdmin[0]:
        allowed = True
    
    if allowed == True:
        
        
        # declare url
        url = 'https://geolhistory.org/rss/articles.php'
        
        # http response
        resp = requests.get(url)
        
        # save response
        with open('feed.xml', 'wb') as f:
            f.write(resp.content)
        
        # start parsing through the file by creating tree object
        tree = ET.parse('feed.xml')
        
        # get root element
        root = tree.getroot()
        
        # create empty list for news items
        articles = []
        
        # go through each article in the XML file
        for x in root[0].findall('item'):
            title =x.find('title').text
            link =x.find('link').text
            URL = "\"" + str(link) + "\""
            
            desc =x.find('description').text
            author =x.find('author').text
            image = "https://service.lmwn.co.uk/brandkit/geolhistory/background-dinosaur-logo.png"
            # once image is added to XML, it needs to be added to replace the above
            
            # checking if any part of the article is already in the database (bar the author as that will come up multiple times)
            
            is_title_already_in_db = False
            is_link_already_in_db = False
            is_desc_already_in_db = False
            
            
            # checking title
            cursor.execute("SELECT count(*) FROM articles WHERE title = ?",(title,))
            find = cursor.fetchone()[0]
            
            if find>0:
                is_title_already_in_db = True
            

            # checking link
            cursor.execute("SELECT count(*) FROM articles WHERE link = ?",(URL,))
            find = cursor.fetchone()[0]
            
            if find>0:
                is_link_already_in_db = True
            

            # checking description
            cursor.execute("SELECT count(*) FROM articles WHERE description = ?",(desc,))
            find = cursor.fetchone()[0]
            
            if find>0:
                is_desc_already_in_db = True
            
            # seeing how many values are already in the database and carrying out the appropriate actions
            
            if (is_title_already_in_db == False and is_link_already_in_db == False and is_desc_already_in_db == False):
                #sending notification
                
                # modifying the XML description to remove copyright and URL at end
                cut_description_array = desc.split("Read more at GeolHistory.org")
                cut_description = cut_description_array[0]
                
                # removing email from author
                cut_author_array = author.split("(")
                cut_author = cut_author_array[1].rstrip((cut_author_array[1])[-1]) # remove the ending bracket from the sting
                
                
                #building the embed
                style = discord.Embed(name="Article Notification", title=title, description=cut_description, timestamp=datetime.datetime.utcnow(), color=0x28a4fd)
                style.set_image(url=image)
                style.add_field(name="Author", value=cut_author, inline=True)
                style.add_field(name="To Read More", value="[Click Here](" + link + ")", inline=True)
                style.set_footer(text = "Version 2.0.1")
                
                #get new article message from db
                cursor.execute("SELECT value_key FROM config WHERE value = ?",("new_article_message",))
                find = cursor.fetchone()
                
                
                #sending the embed
                Send = await channel.send(find[0], embed=style)
                
                #getting the message ID
                message_id = Send.id
                
                
                #insert into database
                cursor.execute("INSERT INTO articles VALUES(?,?,?,?,?,?)",(message_id,title,URL,desc,author,"N/A"))
                db.commit()
            
            elif (is_title_already_in_db == True and is_link_already_in_db == True and is_desc_already_in_db == False):
                # update description
                print("placeholder")
    
    else:
        Send = await ctx.send("You don't have permission to use the command `update`")



bot.run(bot_token) 