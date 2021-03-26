# bot.py
import os
import dotenv
import threading
import controller.controller as control

import discord
from dotenv import load_dotenv  #for the environment file

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if(message.author == client.user or message.channel.id != 817086994672517133):
        return
    else:
        if(message.content[0]=="!"):
            if(getCommand(message.content)=="newIncident"):
                if control.checkSMAvailability():
                    guild = message.guild
                    permissions = {
                            guild.default_role: discord.PermissionOverwrite(read_messages=False),
                            message.author: discord.PermissionOverwrite(read_messages=True)
                            }
                    channel = await guild.create_text_channel("New Incident #"+str(len(guild.channels))+"", overwrites=permissions)
                    await message.channel.send("Go to channel 'New Incident #"+str(len(guild.channels)-1)+" to create the incident.")
                    await newIncident(channel)
                else:
                    await channel.send("Service Manager is not available right now. Try again later")

            elif(getCommand(message.content)=="updateIncident"):
                updateIncident()
            elif(getCommand(message.content)=="closeIncident"):
                closeIncident()
            elif(getCommand(message.content)=="checkIncident"):
                checkIncident()
            elif(getCommand(message.content)=="getKpi"):
                getKpi()
            else: #help or other invalid message
                await message.channel.send("Avalable actions: \n !help: shows available actions. \n !newIncident: starts the incident creation. \n !updateIncident: modify an incident.\n !closeIncident: Close an incident. \n !checkIncident: get an incident. \n !getKpi: get one or more KPIs (Key Performance Indicator)")

def getCommand(content):
    return content.split('!')[1].split('\n')[0]

async def getOperator(channel):
    await channel.send("----------INCIDENT CREATION----------\n Enter your Service Manager Login: ")
    operator = await client.wait_for("message")
    while (operator.channel.id != channel.id) or (not (control.validateLogin(operator.content))) or (operator.author == client.user):
        if(operator.channel.id == channel.id):
            await channel.send("User not found, enter your Service Manager Login")
        operator = await client.wait_for("message")
    print(control.validateLogin(operator.content))
    return operator.content


async def getTitle(channel):
    await channel.send("Enter Incident title")
    title = await client.wait_for("message")
    while(not control.validateTitle(title.content)):
        await channel.send("Title not valid, enter Incident title")
        title = await client.wait_for("message")
    return title.content

async def getDescription(channel):
    await channel.send("Enter Incident description")
    description = await client.wait_for("message")
    while(not control.validateTitle(description.content)):
        await channel.send("Description not valid, try again")
        description = await client.wait_for("message")
    return description.content

async def getCI(channel):
    await channel.send("Enter Affected CI ID. \n List of CIs")
    cis = control.getCIs()
    ids = list()
    for ci in cis['content']:
        await channel.send(ci)
        ids.append(ci['Device']['ConfigurationItem'])
    ciId = await client.wait_for("message")
    while(ciId.content not in ids):
        await channel.send("CI id not valid, try again")
        ciId = await client.wait_for("message")
    return ciId.content

async def getImpact(channel):
    await channel.send("Enter Incident impact value (from 1-Highest to 4-Lowest)")
    impact = await client.wait_for("message")
    while(not control.validateImpact(impact.content)):
        await channel.send("Impact value not valid, try again")
        impact = await client.wait_for("message")
    return impact.content

async def getSeverity(channel):
    await channel.send("Enter Incident severity value (from 1-Highest to 4-Lowest)")
    severity = await client.wait_for("message")
    while(not control.validateImpact(severity.content)):
        await channel.send("Severity value not valid, try again")
        severity = await client.wait_for("message")
    return severity.content

async def newIncident(channel):
    try:
        operator = await getOperator(channel)
        if (operator == "exit" or operator == "Exit"):
            return

        title = await getTitle(channel)
        if (title == "exit" or title == "Exit"):
            return

        description = await getDescription(channel)
        if (description == "exit" or description == "Exit"):
            return

        ci = await getCI(channel)
        if (ci == "exit" or ci == "Exit"):
            return

        impact = await getImpact(channel)
        if (impact == "exit" or impact == "Exit"):
            return

        severity = await getSeverity(channel)
        if (severity == "exit" or severity == "Exit"):
            return

        await channel.send("Submitting incident to Service Manager")
        response = control.createIncident(operator,title,description,ci,impact,severity)
        await channel.send("Incident created succesfully")
        await channel.send(response)
    except Exception as exception:
        await channel.send("There was a problem connecting to Service Manager. Try again later")
        print(str(exception))


client.run(TOKEN)
