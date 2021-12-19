import os
import sqlite3
import datetime
import traceback
import numpy as np
import configparser
import interactions

config = configparser.ConfigParser()

# since i have a tendency to leak bot tokens through github, probably best to store them externally
if os.path.exists('config.ini') == False:
    config['DEFAULT'] = {'bot_token': '123xyz'}
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    
    print("Please go to config.ini and enter your bots details and preferences")
    exit()

config.read('config.ini')

##### Variables #####

bot_token = config['DEFAULT']['bot_token']
guilds = [713068366419722300,816000848445571073]
#####################

#check if database is made and load it
db = sqlite3.connect('GeolHistory.db')
cursor = db.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS articles(message_id TEXT primary key, title TEXT, link TEXT, description TEXT, author TEXT, image TEXT)')
cursor.execute('CREATE TABLE IF NOT EXISTS config(value TEXT primary key, value_key TEXT, description TEXT)')
cursor.execute('CREATE TABLE IF NOT EXISTS rules(number TEXT primary key,  description TEXT)')


# setting bot prefix
bot = interactions.Client(token=bot_token)

@bot.event
async def on_ready():
    print("Bot Connected!")
    
#ping commmand
@bot.command(
    name="ping",
    description="This command will return the bots ping",
    scope=guilds
)
async def ping(ctx):
    latency = ctx.bot.latency
    latency = latency * 1000
    latency = round(latency)
    await ctx.send("My ping is **{}ms**!".format(latency))

#summon a rulefor the bot
@bot.command(
    name="rule",
    description="Summon a specific rule",
    scope=guilds,
    options=[
        interactions.Option(    
            type=interactions.OptionType.INTEGER,
            name="rule_number",
            description="The numbe of the rule you would like to summon",
            required=True,
        )
    ]
)
async def rule(ctx,rule_number): 

    try:
        #delete the senders message
        await ctx.message.delete()
    except Exception:
        print("not deleting message due to it being in a DM")
    
    try:
        # get the rule from the db based on the users input
        cursor.execute("SELECT number,description FROM rules WHERE number=(?)",(str(rule_number),))
        query = cursor.fetchall()
        number_of_rules_named_that = len(query)
                
        if number_of_rules_named_that < 1:

            # if the number the user has requested doesn't exist, direct them to the rules channel
            cursor.execute("SELECT value_key FROM config WHERE value = ?",("rules_channel",))
            rule_channel_ID_array = cursor.fetchone()

            await ctx.send("The rule " + str(rule_number) + " does not exist. To see what rules you can summon with this command, please see <#" + rule_channel_ID_array[0] + ">", delete_after=10.0)
        else:
            # build the embed for the rule
            embed = interactions.Embed(
                title="Rule " + str(query[0][0]),
                description=str(query[0][1]), 
                timestamp=str(datetime.datetime.utcnow()), 
                color=0x28a4fd)
            await ctx.send(embeds=embed)
    except:
        await ctx.send("Please ensure you have formatted the command correctly\n`/rule {rule number}` eg. `/rule 5` ")
        traceback.print_exc()

#change a help command for the bot
@bot.command(
    name="help",
    description="This command will provide information on all the bots commands",
    scope=guilds)
async def help(ctx): 
    print("Running help command") # for debugging
        
    help_embed = interactions.Embed(
        title="Geol History commands:",
        thumbnail="https://service.lmwn.co.uk/brandkit/geolhistory/background-logo-square.png",
        author="Geol History",
        description="This bot is designed to help you keep track of the history of the Geol History Discord server.\n\nTo see a list of commands, please see <#715984100907959808>",
        fields=[
            interactions.EmbedField(name="/rule {rule number}", value="Summon a rule for the bot", inline=False)._json,
            interactions.EmbedField(name="!removeadmin {@user / userid}", value="Remove an admin", inline=False)._json,
            interactions.EmbedField(name="!addadmin {@user / userid}", value="Add an admin", inline=False)._json,
            interactions.EmbedField(name="!setrulechannel {#channel / channelid}", value="Change the rule channel", inline=False)._json
        ]
    )

    print("Embed is built") # for debugging
    await ctx.send(embeds=help_embed)
    await ctx.send("test text")
    await ctx.send("test text",embeds=help_embed)
    print("Embed sent") # for debugging


    #embed.EmbedField(name="!removeadmin {@user / userid}", value="Remove an admin", inline=False)
    #embed.EmbedField(name="!addadmin {@user / userid}", value="Add an admin", inline=False)
    #embed.EmbedField(name="!setrulechannel {#channel / channelid}", value="Change the rule channel", inline=False)
    #embed.EmbedField(name="!setchannel", value="Change the notification channel for new articles", inline=False)
    #embed.EmbedField(name="!setmessage {message}", value="Change the message sent alongside the articles embed", inline=False)
    #embed.EmbedField(name="!setchecking {True / False}", value="Change whether you want the bot to automatically check for new articles or not", inline=False)
    #embed.EmbedField(name="!setinterval {int}", value="Change how often the bot checks for new articles (in seconds)", inline=False)
    #embed.EmbedField(name="!rule {rule}", value="Display a specific rule", inline=False)
    #embed.EmbedField(name="!addrule {ruleID} {description}", value="Create a new rule", inline=False)
    #embed.EmbedField(name="!delrule {ruleID}", value="Delete a rule", inline=False)
    #embed.EmbedField(name="!config", value="Show the bots configuration file", inline=False)
    #embed.EmbedField(name="!update", value="Manually check for new updates", inline=False)
    #embed.EmbedField(name="!ghelp", value="Show this help message", inline=False)
    
    #embed.set_thumbnail(url="https://service.lmwn.co.uk/brandkit/geolhistory/background-logo-square.png")
    


'''
#delete a rule
@bot.command()
async def delrule(ctx): 
    
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
            rule_number = split_command[0] 
            
            #find if rule is in the db already
            cursor.execute("SELECT count(*) FROM rules WHERE number = ?",(rule_number,))
            find = cursor.fetchone()[0]

            if find>0:
                cursor.execute("DELETE FROM rules WHERE number = " + rule_number)
                db.commit()
                await ctx.send("The rule " + rule_number + " has been deleted", delete_after=6.0)
            
            else:
                
                await ctx.send("That rule ID (" + rule_number + ") doesn't exist, please use an existing one or create rule " + rule_number + ".", delete_after=6.0)
                return
        except:
            Send = await ctx.send("Please ensure you have formatted the command correctly\n`!delrule {id} {description}` eg. `!delrule 15`")
            traceback.print_exc()
    else:
        Send = await ctx.send("You don't have permission to use the command `delrule`")

#add a rule
@bot.command()
async def addrule(ctx): 
    
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
            rule_number = split_command[0]
            del split_command[0]
            
            #find if rule is in the db already
            cursor.execute("SELECT count(*) FROM rules WHERE number = ?",(rule_number,))
            find = cursor.fetchone()[0]

            if find>0:
                await ctx.send("That rule ID (" + rule_number + ") is already assigned, please use a different one or delete rule " + rule_number + ".", delete_after=6.0)
                return

            #join the message back together
            text = " ".join(split_command)
            
            
            if len(text) < 4096:
                #updating the database
                cursor.execute("INSERT INTO rules VALUES(?,?)",(rule_number,text))
                db.commit()
                Send = await ctx.send("the rule \"" + rule_number + "\" has been created, below is it's description:\n" + text)
            else:
                Send = await ctx.send("The rule must be less than 4096 characters")
        except:
            Send = await ctx.send("Please ensure you have formatted the command correctly\n`!addrule {id} {description}` eg. `!addrule 15 Follow Discord TOS`")
            traceback.print_exc()
    else:
        Send = await ctx.send("You don't have permission to use the command `addrule`")

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

#change the notification channel for the bot
@bot.command()
async def setrulechannel(ctx): 
    
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
                    cursor.execute("UPDATE config SET value_key = (?) WHERE value = (?)",(split_command[1],"rules_channel"))
                    db.commit()
                    Send = await ctx.send("Rules channel updated to <#" + split_command[1] + ">")
                else:
                    Send = await ctx.send("Please ensure you have formatted the command correctly\n`!setrulechannel #channel` or `!setrulechannel 123456789012345678`")
            elif len(split_command[1]) == 21:
                if str((split_command[1])[0]) == "<" and str((split_command[1])[1]) == "#":
                    new_channel_array = (split_command[1]).split("#")
                    new_channel_array_final = (new_channel_array[1]).split(">")
                    
                    #updating the database
                    cursor.execute("UPDATE config SET value_key = (?) WHERE value = (?)",(new_channel_array_final[0],"rules_channel"))
                    db.commit()
                    Send = await ctx.send("Rules channel updated to " + split_command[1])
                else:
                    Send = await ctx.send("Please ensure you have formatted the command correctly\n`!setrulechannel #channel` or `!setrulechannel 123456789012345678`")
                
            else:
                Send = await ctx.send("Please ensure you have formatted the command correctly\n`!setrulechannel #channel` or `!setrulechannel 123456789012345678`")
            
        except:
            Send = await ctx.send("Please ensure you have formatted the command correctly\n`!setrulechannel #channel` or `!setrulechannel 123456789012345678`")
    else:
        Send = await ctx.send("You don't have permission to use the command `setrulechannel`")

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

'''
    
bot.start()