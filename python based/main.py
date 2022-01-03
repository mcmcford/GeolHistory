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
    scope=guilds)
async def ping(ctx):
    latency = interactions.ping
    latency = latency * 1000
    latency = round(latency)
    await ctx.send("My ping is **{}ms**!".format(latency))

#summon a rule for the bot
@bot.command(
    name="rule",
    description="Summon a specific rule",
    scope=guilds,
    options=[
        interactions.Option(    
            type=interactions.OptionType.INTEGER,
            name="rule_number",
            description="The number of the rule you would like to summon",
            required=True,
        )
    ])
async def rule(ctx,rule_number): 
    
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
        thumbnail=interactions.EmbedImageStruct(url="https://service.lmwn.co.uk/brandkit/geolhistory/background-logo-square.png")._json,
        author=interactions.EmbedAuthor(name="Geol History")._json,
        fields=[
            interactions.EmbedField(name="/rule {rule number}", value="Summon a rule for the bot", inline=False)._json,
            interactions.EmbedField(name="/removeadmin {@user / userid}", value="Remove an admin", inline=False)._json,
            interactions.EmbedField(name="/addadmin {@user / userid}", value="Add an admin", inline=False)._json,
            interactions.EmbedField(name="/setrulechannel {#channel / channelid}", value="Change the rule channel", inline=False)._json,
            interactions.EmbedField(name="/setchannel", value="Change the notification channel for new articles", inline=False)._json,
            interactions.EmbedField(name="/setmessage {message}", value="Change the message sent alongside the articles embed", inline=False)._json,
            interactions.EmbedField(name="/setchecking {True / False}", value="Change whether you want the bot to automatically check for new articles or not", inline=False)._json,
            interactions.EmbedField(name="/rule {rule}", value="Display a specific rule", inline=False)._json,
            interactions.EmbedField(name="/addrule {ruleID} {description}", value="Create a new rule", inline=False)._json,
            interactions.EmbedField(name="/delrule {ruleID}", value="Delete a rule", inline=False)._json,
            interactions.EmbedField(name="/config", value="Show the bots configuration file", inline=False)._json,
            interactions.EmbedField(name="/update", value="Manually check for new updates", inline=False)._json,
            interactions.EmbedField(name="/help", value="Show this help message", inline=False)._json,
        ]
    )

    await ctx.send("These commands may not all work, the bot is currently still being transitioned over to a new APIWrapper",embeds=help_embed)

#delete a rule
@bot.command(    
    name="delrule",
    description="Delete a rule from the database",
    scope=guilds,
    options=[
        interactions.Option(    
            type=interactions.OptionType.INTEGER,
            name="rule_number",
            description="The number of the rule you would like to remove from the database",
            required=True,
        )
    ])
async def delrule(ctx,rule_number): 
        
    allowed = check_permissions(ctx.author.user.id,"admin")
    
    if allowed == True:
        try:
            
            #find if rule is in the db already
            cursor.execute("SELECT count(*) FROM rules WHERE number = ?",(str(rule_number),))
            find = cursor.fetchone()[0]

            if find>0:
                cursor.execute("DELETE FROM rules WHERE number = " + str(rule_number))
                db.commit()
                await ctx.send("The rule " + str(rule_number) + " has been deleted")
                #await ctx.send("The rule " + str(rule_number) + " has been deleted", delete_after=6.0) # need to find the new way to delete messages
            
            else:
                
                await ctx.send("That rule ID (" + str(rule_number) + ") doesn't exist, please use an existing one or create rule " + str(rule_number) + ".")
                #await ctx.send("That rule ID (" + str(rule_number) + ") doesn't exist, please use an existing one or create rule " + str(rule_number) + ".", delete_after=6.0)
                return
        except:
            await ctx.send("Please ensure you have formatted the command correctly\n`/delrule {id} {description}` eg. `/delrule 15`")
            traceback.print_exc()
    else:
        await ctx.send("You don't have permission to use the command `delrule`")

#add a rule
@bot.command(    
    name="addrule",
    description="Add a rule to the database",
    scope=guilds,
    options=[
        interactions.Option(    
            type=interactions.OptionType.INTEGER,
            name="rule_number",
            description="The number of the rule you would like to add to the database",
            required=True,
        ),
        interactions.Option(    
            type=interactions.OptionType.STRING,
            name="rule_description",
            description="The description of the rule you would like to add to the database",
            required=True,
        )
    ])
async def addrule(ctx,rule_number,rule_description): 
    
    allowed = check_permissions(ctx.author.user.id,"admin")

    if allowed == True:
        try:
            
            #find if rule is in the db already
            cursor.execute("SELECT count(*) FROM rules WHERE number = ?",(str(rule_number),))
            find = cursor.fetchone()[0]

            if find>0:
                await ctx.send("That rule ID (" + str(rule_number) + ") is already assigned, please use a different one or delete rule " + str(rule_number) + ".")
                #await ctx.send("That rule ID (" + str(rule_number) + ") is already assigned, please use a different one or delete rule " + str(rule_number) + ".", delete_after=6.0)
                return  
            elif len(rule_description) < 4096:
                #updating the database
                cursor.execute("INSERT INTO rules VALUES(?,?)",(str(rule_number),rule_description))
                db.commit()
                Send = await ctx.send("the rule \"" + str(rule_number) + "\" has been created, below is it's description:\n" + rule_description)
            else:
                await ctx.send("The rule must be less than 4096 characters")
        except:
            await ctx.send("Please ensure you have formatted the command correctly\n`/addrule {id} {description}` eg. `/addrule 15 Follow Discord TOS`")
            traceback.print_exc()
    else:
        await ctx.send("You don't have permission to use the command `addrule`")

#see all the current configs for the bot
@bot.command(
    name="config",
    description="View all the config values for the bot",
    scope=guilds)
async def config(ctx):
    
    allowed = check_permissions(ctx.author.user.id,"admin")

    if allowed == True:
        #get all the values from db
        cursor.execute("SELECT * FROM config;")
        config_truple = cursor.fetchall()
        config_array = np.array(config_truple)
                        
        fields_list = []

        #loop to add all values from DB to the embed
        for x in range(len(config_array)):
            
            fields_list.append(interactions.EmbedField(name= str(config_array[x][0]) + "\n(" + str(config_array[x][2]) + "):" , value= "`" + str(config_array[x][1]) + "`", inline=False)._json)
        
        #building the embed
        config_embed = interactions.Embed(
            title="Current Configuration",  
            color=0x28a4fd,
            fields=fields_list)

        await ctx.send(embeds=config_embed)
    
    else:
        await ctx.send("You don't have permission to use the command `config`")

#change message sent with the embed when a new article is released for the bot
@bot.command(    
    name="setmessage",
    description="change message sent with the embed when a new article is released",
    scope=guilds,
    options=[
        interactions.Option(    
            type=interactions.OptionType.STRING,
            name="message",
            description="The message you would like to be sent",
            required=True,
        )
    ])
async def setmessage(ctx,message): 
    
    allowed = check_permissions(ctx.author.user.id,"admin")
    
    if allowed == True:
        try:
            
            if len(message) < 2000:
                #updating the database
                cursor.execute("UPDATE config SET value_key = (?) WHERE value = (?)",(message,"new_article_message"))
                db.commit()
                await ctx.send("new artice message updated to \"" + message + "\"")
            else:
                await ctx.send("The message must be less than 2000 characters")
        except:
            await ctx.send("Please ensure you have formatted the command correctly\n`/setmessage {message}` eg. `/setmessage Hey, a new article has been released!`")
    else:
        await ctx.send("You don't have permission to use the command `setmessage`")

#change the auto refresh interval for the bot
@bot.command(    
    name="setinterval",
    description="change the auto refresh interval for the RSS feeds",
    scope=guilds,
    options=[
        interactions.Option(    
            type=interactions.OptionType.INTEGER,
            name="seconds",
            description="The interval (in seconds) you would like to set",
            required=True,
            min_value = 1,
            max_value = 31536002,
        )
    ])
async def setinterval(ctx,seconds): 
    
    # check if the user has admin permissions or higher
    allowed = check_permissions(ctx.author.user.id,"admin")
    
    # if true, allow them to change the interval
    if allowed == True:
        try:
            # check if the user has owner permissions (for if they want to change the interval below the minimum of 60)
            owner = check_permissions(ctx.author.user.id,"owner")
            
            if int(seconds) > 31536001 or int(seconds) < 1:
                # the bot shouldn't allow the user to enter values outside of these bounds but just in case
                await ctx.send("Please ensure you have set the interval within the bounds listed below\n**Min** = `1`\n**Max** = `31,536,001`")

            # if anyone other than the owner tries to set the interval below 60, tell them they can't as this may cause issues such as excessive network traffic
            elif int(seconds) < 60 and owner == False:

                # get the owner ID from the db so it can be used below when mentioning them
                cursor.execute("SELECT value_key FROM config WHERE value = ?",("owner_id",))
                ownerID = cursor.fetchone()

                await ctx.send("Only the bot owner (<@!" + ownerID[0] + ">) can set the interval below 60 seconds")
            # if the interval is out of bounds but set by the owner, allow it
            elif int(seconds) < 60 and int(seconds) > 0 and owner == True:
                #updating the database
                cursor.execute("UPDATE config SET value_key = (?) WHERE value = (?)",(seconds,"timeperiod"))
                db.commit()
                await ctx.send("Auto checking interval updated to " + str(seconds))
            # if the interval is within bounds, allow it
            elif int(seconds) > 59 and int(seconds) < 31536002:
                #updating the database
                cursor.execute("UPDATE config SET value_key = (?) WHERE value = (?)",(seconds,"timeperiod"))
                db.commit()
                await ctx.send("Auto checking interval updated to " + str(seconds))
        except:
            # if there was any kind of error print this
            await ctx.send("Please ensure you have formatted the command correctly\n`/setinterval 123`")
    # if the user simply doesn't have permissions, print this message
    else:
        await ctx.send("You don't have permission to use the command `setinterval`")

#change the status of auto_checking for the bot
@bot.command( 
    name="setchecking",
    description="Whether RSS feeds are checked or not",
    scope=guilds,
    options=[
        interactions.Option(    
            type=interactions.OptionType.BOOLEAN,
            name="enabled_bool",
            description="True / False",
            required=True,
        )
    ])
async def setchecking(ctx,enabled_bool): 

    # check if the user has admin permissions or higher
    allowed = check_permissions(ctx.author.user.id,"admin")
        
    if allowed == True:
        try:
            if enabled_bool == True:
                #updating the database
                cursor.execute("UPDATE config SET value_key = (?) WHERE value = (?)",("True","auto_checking"))
                db.commit()
                await ctx.send("Auto checking updated to " + str(enabled_bool))
            elif enabled_bool == False:
                #updating the database
                cursor.execute("UPDATE config SET value_key = (?) WHERE value = (?)",("False","auto_checking"))
                db.commit()
                await ctx.send("Auto checking updated to " + str(enabled_bool))
        except:
            # this will most likely mean a server side issue opposed to a user issue so this should probably be changed
            await ctx.send("Please ensure you have formatted the command correctly\n`/setchecking True` or `/setchecking False`")
    else:
        await ctx.send("You don't have permission to use the command `setchecking`")

#change the notification channel for the bot
@bot.command(
    name="setchannel",
    description="Change the channel that new articles are sent to",
    scope=guilds,
    options=[
        interactions.Option(    
            type=interactions.OptionType.CHANNEL,
            name="channel",
            description="The channel you would like to send new articles to",
            required=True,
        )
    ])
async def setchannel(ctx,channel): 
    
    # check if the user has admin permissions or higher
    allowed = check_permissions(ctx.author.user.id,"admin")
    
    if allowed == True:

        #updating the database
        cursor.execute("UPDATE config SET value_key = (?) WHERE value = (?)",(channel,"notification_channel"))
        db.commit()
        Send = await ctx.send("Notification channel updated to <#" + str(channel) + ">")                
    else:
        Send = await ctx.send("You don't have permission to use the command `setchannel`")

#change the notification channel for the bot
@bot.command(
    name="setrulechannel",
    description="Change the channel that the server rules are shown in",
    scope=guilds,
    options=[
        interactions.Option(    
            type=interactions.OptionType.CHANNEL,
            name="channel",
            description="The channel you would like to declare as the rules channel",
            required=True,
        )
    ])
async def setrulechannel(ctx,channel): 
    
    # check if the user has admin permissions or higher
    allowed = check_permissions(ctx.author.user.id,"admin")
    
    if allowed == True:
        #updating the database
        cursor.execute("UPDATE config SET value_key = (?) WHERE value = (?)",(channel,"rules_channel"))
        db.commit()
        await ctx.send("Rules channel updated to <#" + str(channel) + ">")
    else:
        Send = await ctx.send("You don't have permission to use the command `setrulechannel`")

#change remove an admin ID for the bot
@bot.command(
    name="removeadmin",
    description="Remove a user from the admin list",
    scope=guilds,
    options=[
        interactions.Option(    
            type=interactions.OptionType.USER,
            name="admin",
            description="The admin you would like to remove privileges from",
            required=True,
        )
    ])
async def removeadmin(ctx,admin): 
            
    # check if the user has lead admin permissions or higher
    allowed = check_permissions(ctx.author.user.id,"lead_admin")
    
    if allowed == True:
        
        try:
            #get admin IDs from db
            cursor.execute("SELECT value_key FROM config WHERE value = ?",("admin_ids",))
            admin_ids_array = cursor.fetchone()

            admin_ids_array = admin_ids_array[0].split(",")
            
            in_array_bool = False

            # check if the admin ID is in the array
            for x in admin_ids_array:
                if str(admin) == x:
                    in_array_bool = True
            

            if in_array_bool == True:
                
                # remove the admin ID from the array
                admin_ids_array.remove(str(admin))
                
                # declare the blank string 'admin_ids_string'
                admin_ids_string = ""

                # create a new string of admins to be added to the db
                for x in admin_ids_array:
                    if x == admin_ids_array[-1]:
                        admin_ids_string += x
                    else:
                        admin_ids_string += x + ","
                
                #updating the database
                cursor.execute("UPDATE config SET value_key = (?) WHERE value = (?)",(admin_ids_string,"admin_ids"))
                db.commit()
                await ctx.send("the user <@!" + str(admin) + "> is no longer an admin in relation to the bot")
            else:
                await ctx.send("the user <@!" + str(admin) + "> isn't an admin therefore cannot be removed")
        except:
            await ctx.send("Looks like there has been an error on our side, please try again later")
    else:
        await ctx.send("You don't have permission to use the command `removeadmin`")

#change add an admin ID for the bot
@bot.command(
    name="addadmin",
    description="Add a user to the admin list",
    scope=guilds,
    options=[
        interactions.Option(    
            type=interactions.OptionType.USER,
            name="admin",
            description="The user you would like to give admin privileges to",
            required=True,
        )
    ])
async def addadmin(ctx,admin): 
    
    # check if the user has lead admin permissions or higher
    allowed = check_permissions(ctx.author.user.id,"lead_admin")

    if allowed == True:
       
        try:

            #get admin IDs from db
            cursor.execute("SELECT value_key FROM config WHERE value = ?",("admin_ids",))
            admin_ids_array = cursor.fetchone()

            admin_ids_array = admin_ids_array[0].split(",")
            
            in_array_bool = False

            # check if the admin ID is in the array
            for x in admin_ids_array:
                if str(admin) == x:
                    in_array_bool = True

            if in_array_bool == True:
                await ctx.send("the user <@!" + str(admin) + "> is already an admin in relation to the bot")
            else:
                admin_ids_string = ""

                # create a new string of admins to be added to the db
                if len(admin_ids_array) > 0 and len(admin_ids_array[0]) > 16:
                    for x in admin_ids_array:
                        admin_ids_string += x + ","
                
                admin_ids_string += str(admin)
                
                #updating the database
                cursor.execute("UPDATE config SET value_key = (?) WHERE value = (?)",(admin_ids_string,"admin_ids"))
                db.commit()
                await ctx.send("the user <@!" + str(admin) + "> is now an admin in relation to the bot")
                
        except:
            await ctx.send("Looks like there has been an error on our side, please try again later")
    else:
        await ctx.send("You don't have permission to use the command `addadmin`")


def check_permissions(user,required_perms):
    # this checks three permission levels, admin, lead_admin and owner

    # if the function has requested to check if the user is an admin, use the statement below
    if required_perms.lower() == "admin":
        # compare the given user's ID to the admin permissions and all those that rank above them
        admin_bool = check_if_admin(user)
        lead_admin_bool = check_if_leadadmin(user)
        owner_bool = check_if_owner(user)

        # if the user is any of the above, return true, confirming the user has the required permissions
        if admin_bool or lead_admin_bool or owner_bool:
            return True
        else:
            # otherwise return false
            return False
    elif required_perms.lower() == "lead_admin":

        # for lead admin, do the same as above but this time don't check for the admin permission (as lead admin obviously has high permissions than admin)
        lead_admin_bool = check_if_leadadmin(user)
        owner_bool = check_if_owner(user)

        # if the user is a lead admin or the owner, return true, confirming the user has the required permissions
        if lead_admin_bool or owner_bool:
            return True
        else:
            # otherwise return false
            return False
    elif required_perms.lower() == "owner":

        # for owner, do the same as above but this time don't check for the admin or lead admin permission (as owner obviously has high permissions than lead admin and admin, mainly for fixing issues and whatnot)
        owner_bool = check_if_owner(user)

        # if the user is the owner, return true, confirming the user has the required permissions
        if owner_bool:
            return True
        else:
            # otherwise return false
            return False
    else:
        # if there has been any issue such as the function being called to check a non-existent permission level, return None
        return None

def check_if_owner(user):

    # get the owners id from the db
    cursor.execute("SELECT value_key FROM config WHERE value = ?",("owner_id",))
    ownerID = cursor.fetchone()

    # compare the ID passed into this function with the ID collected above
    if str(user) == ownerID[0]:
        # if it matches, return true
        return True
    else:
        # otherwise return false
        return False

def check_if_leadadmin(user):
    #get lead admins ID from db
    cursor.execute("SELECT value_key FROM config WHERE value = ?",("lead_admin",))
    leadAdmin = cursor.fetchone()

    # compare the ID passed into this function with the ID collected above
    if str(user) == leadAdmin[0]:
        # if it matches, return true
        return True
    else:
        # otherwise return false
        return False

def check_if_admin(user):

    # this should be recieving the users ID

    #get admin IDs from db
    cursor.execute("SELECT value_key FROM config WHERE value = ?",("admin_ids",))
    admin_ids = cursor.fetchone()
    admin_ids_array = str(admin_ids[0]).split(",")

    # use this boolean to check if it has been found after looping through the array
    admin = False

    # for each ID in the array, check if the ID passed into this function matches
    for x in admin_ids_array:
        if x == str(user):
            # if it matches, set the boolean to true
            admin = True
    
    # if the boolean has been set to true, return true
    if admin == True:
        return True
    else:
        # otherwise return false
        return False

bot.start()