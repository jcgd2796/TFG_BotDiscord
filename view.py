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
                    permissions = {guild.default_role: discord.PermissionOverwrite(read_messages=False),
                            message.author: discord.PermissionOverwrite(read_messages=True)}
                    channel = await guild.create_text_channel("New Incident #"+str(len(guild.channels))+"", overwrites=permissions)
                    await sendMessage(message.channel,"Go to channel 'New Incident #"+str(len(guild.channels)-1)+" to create the incident.")
                    await newIncident(channel)
                else:
                    await sendMessage(channnel,"Service Manager is not available right now. Try again later")

            elif(getCommand(message.content)=="updateIncident"):
                if control.checkSMAvailability():
                    guild = message.guild
                    permissions = {guild.default_role: discord.PermissionOverwrite(read_messages=False),
                            message.author: discord.PermissionOverwrite(read_messages=True)}
                    channel = await guild.create_text_channel("Update Incident #"+str(len(guild.channels))+"", overwrites=permissions)
                    await sendMessage(message.channel,"Go to channel 'Update Incident #"+str(len(guild.channels)-1)+" to update the incident.")
                    await updateIncident(channel)
                else:
                    await sendMessage(channnel,"Service Manager is not available right now. Try again later")

            elif(getCommand(message.content)=="closeIncident"):
                closeIncident()
            elif(getCommand(message.content)=="checkIncident"):
                checkIncident()
            elif(getCommand(message.content)=="getKpi"):
                getKpi()
            else: #help or other invalid message
                await sendMessage(message.channel,"Avalable actions: \n !help: shows available actions. \n !newIncident: starts the incident creation. \n !updateIncident: modify an incident.\n !closeIncident: Close an incident. \n !checkIncident: get an incident. \n !getKpi: get one or more KPIs (Key Performance Indicator)")

def getCommand(content):
    return content.split('!')[1].split('\n')[0]

async def getOperator(channel):
    await sendMessage(channel,"Enter your Service Manager Login: ")
    operator = await client.wait_for("message")
    while (operator.channel.id != channel.id) or (not (control.validateLogin(operator.content))) or (operator.author == client.user):
        if(operator.channel.id == channel.id) and (operator.author != client.user):
            await sendMessage(channel,"User not found, enter your Service Manager Login")
        operator = await client.wait_for("message")
    return control.getOperatorName(operator.content)


async def getTitle(channel):
    await sendMessage(channel,"Enter Incident title")
    title = await client.wait_for("message")
    while (title.channel.id != channel.id) or (not (control.validateTitle(title.content))) or (title.author == client.user):
        if(title.channel.id == channel.id) and (title.author != client.user):
            await sendMessage(channel,"Title not valid, enter Incident title")
        title = await client.wait_for("message")
    return title.content

async def getDescription(channel):
    await sendMessage(channel,"Enter Incident description")
    description = await client.wait_for("message")
    while (description.channel.id != channel.id) or (not (control.validateTitle(description.content))) or (description.author == client.user):
        if(description.channel.id == channel.id) and (description.author != client.user):
            await sendMessage(channel,"Description not valid, try again")
        description = await client.wait_for("message")
    return description.content

async def getCI(channel):
    await sendMessage(channel,"Enter name of the Affected CI.")
    ci = await client.wait_for("message")
    while (ci.channel.id != channel.id) or (not (control.validateCI(ci.content))) or (ci.author == client.user):
        if(ci.channel.id == channel.id) and (ci.author != client.user):
            await sendMessage(channel,"CI with that name not found, try again")
        ci = await client.wait_for("message")
    return control.getCI(ci.content)['content'][0]['Device']['ConfigurationItem']


async def getImpact(channel):
    await sendMessage(channel,"Enter Incident impact value (from 2-High to 4-Low)")
    impact = await client.wait_for("message")
    while (impact.channel.id != channel.id) or (not (control.validateImpact(impact.content))) or (impact.author == client.user):
        if(impact.channel.id == channel.id) and (impact.author != client.user):
            await sendMessage(channel,"Impact value not valid, try again")
        impact = await client.wait_for("message")
    return impact.content

async def getSeverity(channel):
    await sendMessage(channel,"Enter Incident severity value (from 2-High to 4-Low)")
    severity = await client.wait_for("message")
    while (severity.channel.id != channel.id) or (not (control.validateImpact(severity.content))) or (severity.author == client.user):
        if(severity.channel.id == channel.id) and (severity.author != client.user):
            await sendMessage(channel,"Severity value not valid, try again")
        severity = await client.wait_for("message")
    return severity.content

async def sendCancelMessage(channel):
    await sendMessage(channel,"Incident creation cancelled. No Incident submitted")
    return


async def newIncident(channel):
    try:
        operator = await getOperator(channel)
        if (operator == "!exit" or operator == "!Exit"):
            await sendCancelMessage(channel)
            return

        title = await getTitle(channel)
        if (title == "!exit" or title == "!Exit"):
            await sendCancelMessage(channel)
            return

        description = await getDescription(channel)
        if (description == "!exit" or description == "!Exit"):
            await sendCancelMessage(channel)
            return

        ci = await getCI(channel)
        if (ci == "!exit" or ci == "!Exit"):
            await sendCancelMessage(channel)
            return

        impact = await getImpact(channel)
        if (impact == "!exit" or impact == "!Exit"):
            await sendCancelMessage(channel)
            return

        severity = await getSeverity(channel)
        if (severity == "!exit" or severity == "!Exit"):
            await sendCancelMessage(channel)
            return

        await sendMessage(channel,"Submitting incident to Service Manager")
        response = control.createIncident(operator,title,description,ci,impact,severity)
        await sendMessage(channel,"Incident created succesfully")
        msg = 'Incident ID: '+response['Incident']['IncidentID']+'\n'+'Incident Title: '+response['Incident']['Title']+'\n'+'Incident Description: '+response['Incident']['Description'][0]+'\n'+'Incident Impact: '+response['Incident']['Impact']+'\n'+'Incident Severity: '+response['Incident']['Urgency']
        await sendMessage(channel,msg)
    except Exception as exception:
        await sendMessage(channel,"There was a problem connecting to Service Manager. Try again later")
        raise exception
        print(str(exception))

async def getIncident(channel):
    await sendMessage(channel,"Enter the ID of the incident you want to update")
    incId = await client.wait_for("message")
    while (incId.channel.id != channel.id) or (not (control.validateIncident(incId.content))) or (incId.author == client.user):
        if(incId.channel.id == channel.id) and (incId.author != client.user):
            await sendMessage(channel,"Incident ID not valid. Try again")
        incId = await client.wait_for("message")
    return control.getIncident(incId.content)

async def getUpdateList(channel):
    await sendMessage(channel,"Enter the values you want to update, separated by commas")
    values = await client.wait_for("message")
    while (values.channel.id != channel.id) or (not (control.validateList(values.content))) or (values.author == client.user):
        if(values.channel.id == channel.id) and (values.author != client.user):
            await sendMessage(channel,"At least one of the values is not valid, Accepted values are operator, title, description, impact and severity")
        values = await client.wait_for("message")
    return control.getValuesList(values.content)

async def updateIncident(channel):
    try:
        incident = await getIncident(channel)
        updateList = await getUpdateList(channel)
        print (updateList)
        if ("!exit" in updateList):
            return
        
        for field in updateList:
            if field == 'operator':
                operator = await getOperator(channel)
                if (operator == "!exit" or operator == "!Exit"):
                    await sendCancelMessage(channel)
                    return
                incident.setOperator(operator)

            elif field == 'title':
                title = await getTitle(channel)
                if (title == "!exit" or title == "!Exit"):
                    await sendCancelMessage(channel)
                    return
                incident.setTitle(title)

            elif field == 'description':
                description = await getDescription(channel)
                if (description == "!exit" or description == "!Exit"):
                    await sendCancelMessage(channel)
                    return
                incident.setDescription(description)

            elif field == 'impact':
                impact = await getImpact(channel)
                if (impact == "!exit" or impact == "!Exit"):
                    await sendCancelMessage(channel)
                    return
                incident.setImpact(impact)
            
            elif field == 'severity':
                severity = await getSeverity(channel)
                if (severity == "!exit" or severity == "!Exit"):
                    await sendCancelMessage(channel)
                    return
                incident.setSeverity(severity)

        await sendMessage(channel,"Submitting incident to Service Manager")
        response = control.updateIncident(incident.toJsonObject())
        await sendMessage(channel,"Incident updated succesfully")
        msg = 'Incident ID: '+response['Incident']['IncidentID']+'\n'+'Incident Title: '+response['Incident']['Title']+'\n'+'Incident Description: '+response['Incident']['Description'][0]+'\n'+'Incident Impact: '+response['Incident']['Impact']+'\n'+'Incident Severity: '+response['Incident']['Urgency']
        await sendMessage(channel,msg)
    except Exception as exception:
        await sendMessage(channel,"There was a problem connecting to Service Manager. Try again later")
        raise exception
        print(str(exception))

async def closeIncident(channel):
    await sendMessage(channel,"Not implemented yet")

async def checkIncident(channel):
    await sendMessage(channel,"Not implemented yet")

async def getKpi(channel):
    await sendMessage(channel,"Not implemented yet")

async def sendMessage(channel,message):
    await channel.send(message)

client.run(TOKEN)
