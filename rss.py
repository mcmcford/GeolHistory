import requests
import json
import time
import datetime
import traceback
import hashlib
import sqlite3
import xml.etree.ElementTree as ET
import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions

##### Variables #####

rss_channel_id = 
your_nickname = ''  # so people know who to ping if there is an issue, included as a part of the help command
your_user_id = ''
admin_user_ids = []
bot_token = ''
bots_prefix = "!"

#####################

#check if database is made and load it
db = sqlite3.connect('GeolHistory.db')
cursor = db.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS articles(message_id TEXT primary key, title TEXT, link TEXT, description TEXT, author TEXT, image TEXT)')


# setting bot prefix
bot = commands.Bot(command_prefix=commands.when_mentioned_or(bots_prefix))

@bot.event
async def on_ready():
    """On ready event!"""
    print("Logged in as " + str(bot.user))
    print("User ID: " + str(bot.user.id))
    await bot.change_presence(activity=discord.Game(name="Version 1.0.3"))
    
#ping commmand
@bot.command(pass_context=True)
async def ping(ctx):
    latency = ctx.bot.latency
    latency = latency * 1000
    latency = round(latency)
    await ctx.send("My ping is **{}ms**!".format(latency))
    

#testing things
@bot.command()
async def update(ctx):
    
    try:
        #delete the senders message
        await ctx.message.delete()
    except Exception:
        print("not deleting message due to it being in a DM")
    
    channel = bot.get_channel(rss_channel_id) # the message's channel
    
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
            style.set_footer(text = "Version 1.0.3")
            
            #sending the embed
            Send = await channel.send("Hey, a new article has been released!", embed=style)
            
            #getting the message ID
            message_id = Send.id
            
            
            #insert into database
            cursor.execute("INSERT INTO articles VALUES(?,?,?,?,?,?)",(message_id,title,URL,desc,author,"N/A"))
            db.commit()
        
        elif (is_title_already_in_db == True and is_link_already_in_db == True and is_desc_already_in_db == False):
            # update description
            print("placeholder")
        
        
    


bot.run(bot_token) 