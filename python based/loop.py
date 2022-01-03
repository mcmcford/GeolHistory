import os
import time
import sqlite3
import discord
import datetime
import requests
import traceback
import configparser
from discord import Member
from discord.ext import commands
import xml.etree.ElementTree as ET
from discord.ext.commands import Bot
from discord.ext.commands import has_permissions, MissingPermissions


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
bots_prefix = "!"

#####################

#check if database is made and load it
db = sqlite3.connect('GeolHistory.db')
cursor = db.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS articles(message_id TEXT primary key, title TEXT, link TEXT, description TEXT, author TEXT, image TEXT)')
cursor.execute('CREATE TABLE IF NOT EXISTS config(value TEXT primary key, value_key TEXT, description TEXT)')
db.commit()


# setting bot prefix
bot = commands.Bot(command_prefix=commands.when_mentioned_or(bots_prefix))
@bot.event
async def on_ready():

    # this just helps to know if the bot is connected when running tests
    """On ready event!"""
    print("Logged in as " + str(bot.user))
    print("User ID: " + str(bot.user.id))
    await bot.change_presence(activity=discord.Game(name="Now with slash commands!"))

    # Infinite loop since this script should never really stop
    while True:
        #get auto refresh status from db
        cursor.execute("SELECT value_key FROM config WHERE value = ?",("auto_checking",))
        active = cursor.fetchone()
                
        #get refresh time from db
        cursor.execute("SELECT value_key FROM config WHERE value = ?",("timeperiod",))
        find = cursor.fetchone()
        
        time.sleep(int(find[0]))
        
        if str(active[0]) == "True":
            
            
            print(str(datetime.datetime.now()) + " - checking (interval of "+ find[0] +" seconds)")
            
            #get channel ID from db
            cursor.execute("SELECT value_key FROM config WHERE value = ?",("notification_channel",))
            # it was stupid to name all these 'find'
            channel = cursor.fetchone()
                        
            # declare url 
            url = 'https://geolhistory.org/rss/articles'
            
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
                    print('New article found')

                    #get the string that will be added onto the end of the cutdown description
                    cursor.execute("SELECT value_key FROM config WHERE value = ?",("desc_extention",))
                    desc_ext = cursor.fetchone()[0]

                    # shorten the description from in the XML to 400 chars
                    cut_description = desc[:400] + desc_ext
                    
                    # removing email from author
                    cut_author_array = author.split("(")
                    cut_author = cut_author_array[1].rstrip((cut_author_array[1])[-1]) # remove the ending bracket from the sting
                    
                    #getting the message ID
                    message_id = await send_notification(title,cut_description,image,cut_author,str(link),int(channel[0]))
                    
                    print('adding to database')
                    #insert into database
                    cursor.execute("INSERT INTO articles VALUES(?,?,?,?,?,?)",(message_id,title,URL,desc,author,"N/A"))
                    db.commit()
                elif (is_title_already_in_db == True and is_link_already_in_db == True and is_desc_already_in_db == False):
                    # update description
                    pass 
        else:
            print("not active")

async def send_notification(title,cut_description,image_url,cut_author,link_url,channel_id):
    
    #building the embed
    style = discord.Embed(name="Article Notification", title=title, description=cut_description, timestamp=datetime.datetime.utcnow(), color=0x28a4fd)
    style.set_image(url=image_url)
    style.add_field(name="Author", value=cut_author, inline=True)
    style.add_field(name="To Read More", value="[Click Here](" + link_url + ")", inline=True)
    style.set_footer(text = "Version 2.0.1")
    
    print('sending message')

    #get new article message from db, this will be added above the embed
    cursor.execute("SELECT value_key FROM config WHERE value = ?",("new_article_message",))
    find = cursor.fetchone()

    # the message's channel
    channel = bot.get_channel(channel_id) 
    
    #sending the embed
    Send = await channel.send(find[0], embed=style)
    message_id = Send.id
    return message_id


bot.run(bot_token) 