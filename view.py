# bot.py
import os
import dotenv
import threading
import controller.controller as control

import discord
from dotenv import load_dotenv  #for the environment file

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GENERAL_CHANNEL_ID = 817086994672517133
client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if(message.author == client.user or message.channel.id != GENERAL_CHANNEL_ID):
        return
    else:
        if(message.content[0]=="!"):
            if(getCommand(message.content)=="newIncident"):
                if control.checkSMAvailability():
                    guild = message.guild
                    permissions = {guild.default_role: discord.PermissionOverwrite(read_messages=False),
                            message.author: discord.PermissionOverwrite(read_messages=True)}
                    channel = await guild.create_text_channel("New Incident #"+str(len(guild.channels))+"", overwrites=permissions)
                    await sendMessage(message.channel,"Go to channel "+channel.mention +" to create the incident.")
                    await newIncident(channel)
                else:
                    await sendMessage(channnel,"Service Manager is not available right now. Try again later")

            elif(getCommand(message.content)=="updateIncident"):
                if control.checkSMAvailability():
                    guild = message.guild
                    permissions = {guild.default_role: discord.PermissionOverwrite(read_messages=False),
                            message.author: discord.PermissionOverwrite(read_messages=True)}
                    channel = await guild.create_text_channel("Update Incident #"+str(len(guild.channels))+"", overwrites=permissions)
                    await sendMessage(message.channel,"Go to channel "+channel.mention +" to update the incident.")
                    await updateIncident(channel)
                else:
                    await sendMessage(channnel,"Service Manager is not available right now. Try again later")

            elif(getCommand(message.content)=="closeIncident"):
                if control.checkSMAvailability():
                    guild = message.guild
                    permissions = {guild.default_role: discord.PermissionOverwrite(read_messages=False),
                            message.author: discord.PermissionOverwrite(read_messages=True)}
                    channel = await guild.create_text_channel("Close Incident #"+str(len(guild.channels))+"", overwrites=permissions)
                    await sendMessage(message.channel,"Go to channel "+channel.mention +" to close the incident.")
                    await closeIncident(channel)
                else:
                    await sendMessage(channnel,"Service Manager is not available right now. Try again later")

            elif(getCommand(message.content)=="checkIncident"):
                if control.checkSMAvailability():
                    guild = message.guild
                    permissions = {guild.default_role: discord.PermissionOverwrite(read_messages=False),
                            message.author: discord.PermissionOverwrite(read_messages=True)}
                    channel = await guild.create_text_channel("Check Incident #"+str(len(guild.channels))+"", overwrites=permissions)
                    await sendMessage(message.channel,"Go to channel "+channel.mention +" to get the incident data.")
                    await checkIncident(channel)
                else:
                    await sendMessage(channnel,"Service Manager is not available right now. Try again later")
            
            elif(getCommand(message.content)=="getKpi"):
                if control.checkSMAvailability():
                    guild = message.guild
                    permissions = {guild.default_role: discord.PermissionOverwrite(read_messages=False),
                            message.author: discord.PermissionOverwrite(read_messages=True)}
                    channel = await guild.create_text_channel("Get KPI #"+str(len(guild.channels))+"", overwrites=permissions)
                    await sendMessage(message.channel,"Go to channel "+channel.mention +" to get the desired KPIs.")
                    await getKpi(channel)
                else:
                    await sendMessage(channnel,"Service Manager is not available right now. Try again later")
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
    if operator.content.lower() == '!exit':
        return operator.content.lower()
    return control.getOperatorName(operator.content)


async def getTitle(channel):
    await sendMessage(channel,"Enter Incident title")
    title = await client.wait_for("message")
    while (title.channel.id != channel.id) or (not (control.validateTitle(title.content))) or (title.author == client.user):
        if(title.channel.id == channel.id) and (title.author != client.user):
            await sendMessage(channel,"Title not valid, enter Incident title")
        title = await client.wait_for("message")
    if title.content.lower() == '!exit':
        return title.content.lower()
    return title.content

async def getDescription(channel):
    await sendMessage(channel,"Enter Incident description")
    description = await client.wait_for("message")
    while (description.channel.id != channel.id) or (not (control.validateTitle(description.content))) or (description.author == client.user):
        if(description.channel.id == channel.id) and (description.author != client.user):
            await sendMessage(channel,"Description not valid, try again")
        description = await client.wait_for("message")
    if description.content.lower() == '!exit':
        return description.content.lower()
    return description.content

async def getCI(channel):
    await sendMessage(channel,"Enter name of the Affected CI.")
    ci = await client.wait_for("message")
    while (ci.channel.id != channel.id) or (not (control.validateCI(ci.content))) or (ci.author == client.user):
        if(ci.channel.id == channel.id) and (ci.author != client.user):
            await sendMessage(channel,"CI with that name not found, try again")
        ci = await client.wait_for("message")
    if ci.content.lower() == '!exit':
        return ci.content.lower()
    return control.getCI(ci.content)['content'][0]['Device']['ConfigurationItem']


async def getImpact(channel):
    await sendMessage(channel,"Enter Incident impact value (from 2-High to 4-Low)")
    impact = await client.wait_for("message")
    while (impact.channel.id != channel.id) or (not (control.validateImpact(impact.content))) or (impact.author == client.user):
        if(impact.channel.id == channel.id) and (impact.author != client.user):
            await sendMessage(channel,"Impact value not valid, try again")
        impact = await client.wait_for("message")
    if impact.content.lower() == '!exit':
        return impact.content.lower()
    return impact.content

async def getSeverity(channel):
    await sendMessage(channel,"Enter Incident severity value (from 2-High to 4-Low)")
    severity = await client.wait_for("message")
    while (severity.channel.id != channel.id) or (not (control.validateImpact(severity.content))) or (severity.author == client.user):
        if(severity.channel.id == channel.id) and (severity.author != client.user):
            await sendMessage(channel,"Severity value not valid, try again")
        severity = await client.wait_for("message")
    if severity.content.lower() == '!exit':
        return severity.content.lower()
    return severity.content

async def sendMessage(channel,message):
    await channel.send(message)
    return

async def sendCancelMessage(channel):
    await sendMessage(channel,"Operation canceled, no changes performed.")
    await sendFinishMessage(channel)
    return

async def sendFinishMessage(channel):
    await sendMessage(channel,"My job here is done, I won't interact with this channel again. Go to the "+client.get_channel(GENERAL_CHANNEL_ID).mention+" channel to start a new request." )
    return

async def newIncident(channel):
    try:
        operator = await getOperator(channel)
        if (operator == "!exit"):
            await sendCancelMessage(channel)
            return

        title = await getTitle(channel)
        if (title == "!exit"):
            await sendCancelMessage(channel)
            return

        description = await getDescription(channel)
        if (description == "!exit"):
            await sendCancelMessage(channel)
            return

        ci = await getCI(channel)
        if (ci == "!exit"):
            await sendCancelMessage(channel)
            return

        impact = await getImpact(channel)
        if (impact == "!exit"):
            await sendCancelMessage(channel)
            return

        severity = await getSeverity(channel)
        if (severity == "!exit"):
            await sendCancelMessage(channel)
            return

        await sendMessage(channel,"Submitting incident to Service Manager")
        response = control.createIncident(operator,title,description,ci,impact,severity)
        await sendMessage(channel,"Incident created succesfully. Take note of the Incident ID as it will be requested for some operations")
        msg = '__**Incident ID: '+response['Incident']['IncidentID']+'**__\n'+'Incident Title: '+response['Incident']['Title']+'\n'+'Incident Description: '+response['Incident']['Description'][0]+'\n'+'Incident Impact: '+response['Incident']['Impact']+'\n'+'Incident Severity: '+response['Incident']['Urgency']
        await sendMessage(channel,msg)
    except Exception as exception:
        raise exception
        await sendMessage(channel,"There was a problem connecting to Service Manager. Try again later")
    finally:
        await sendFinishMessage(channel)

async def getIncident(channel):
    await sendMessage(channel,"Enter the ID of the incident")
    incId = await client.wait_for("message")
    while (incId.channel.id != channel.id) or (not (control.validateIncident(incId.content))) or (incId.author == client.user):
        if(incId.channel.id == channel.id) and (incId.author != client.user):
            await sendMessage(channel,"Incident ID not valid. Try again")
        incId = await client.wait_for("message")
    if incId.content.lower() == '!exit':
        return incId.content.lower()
    return control.getIncident(incId.content)

async def getIncidentData(channel):
    await sendMessage(channel,"Enter the ID of the incident")
    incId = await client.wait_for("message")
    while (incId.channel.id != channel.id) or (not (control.validateIncident(incId.content))) or (incId.author == client.user):
        if(incId.channel.id == channel.id) and (incId.author != client.user):
            await sendMessage(channel,"Incident ID not valid. Try again")
        incId = await client.wait_for("message")
        if incId.content.lower() == '!exit':
            return incId.content.lower()
    return control.getIncidentData(incId.content)

async def getUpdateList(channel):
    await sendMessage(channel,"Enter the values you want to update, separated by commas. Accepted values are operator, title, description, impact and severity")
    values = await client.wait_for("message")
    while (values.channel.id != channel.id) or (not (control.validateList(values.content))) or (values.author == client.user):
        if(values.channel.id == channel.id) and (values.author != client.user):
            await sendMessage(channel,"At least one of the values is not valid, Accepted values are operator, title, description, impact and severity")
        values = await client.wait_for("message")
    return control.getValuesList(values.content)

async def updateIncident(channel):
    try:
        finished = False
        while not finished:
            incident = await getIncident(channel)
            if incident.getPhase() == 'Closure':
                await sendMessage(channel,"The incident is closed. You can't update a closed incident")
                return
            updateList = await getUpdateList(channel)
            if ("!exit" in updateList):
                await sendCancelMessage(channel)
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
            await sendMessage(channel,"Incident updated succesfully. Remember to note the ID for future actions.")
            msg = '**__Incident ID: '+response['Incident']['IncidentID']+'__**\n'+'Incident Title: '+response['Incident']['Title']+'\n'+'Incident Description: '+response['Incident']['Description'][0]+'\n'+'Incident Impact: '+response['Incident']['Impact']+'\n'+'Incident Severity: '+response['Incident']['Urgency']+'\n'+ 'Incident Status: '+response['Incident']['Status']
            await sendMessage(channel,msg)
            await sendMessage(channel,'Do you want to modify more incidents? (Yes/No)')
            finishMessage = await client.wait_for("message")
            while (finishMessage.channel.id != channel.id) or (finishMessage.author == client.user) or not(control.validateFinishMessage(finishMessage.content)):
                if(finishMessage.channel.id == channel.id) and (finishMessage.author != client.user):
                    await sendMessage(channel,"Entry not valid. Must be \"Yes\" or \"No\"")
                finishMessage = await client.wait_for("message")
            if (finishMessage.content.lower() == 'no'):
                finished = True
    except Exception as exception:
        raise exception
        await sendMessage(channel,"There was a problem connecting to Service Manager. Try again later")
    finally:
        await sendFinishMessage(channel)

async def getSolution(channel):
    await sendMessage(channel,"Enter the solution of the Incident")
    solution = await client.wait_for("message")
    while (solution.channel.id != channel.id) or (not (control.validateTitle(solution.content))) or (solution.author == client.user):
        if(solution.channel.id == channel.id) and (solution.author != client.user):
            await sendMessage(channel,"Solution not valid. Try again")
        solution = await client.wait_for("message")
        if solution.content.lower() == '!exit':
            return solution.content.lower()
    return solution.content

async def getClosureCode(channel):
    await sendMessage(channel,"Enter the number of the closure code of the Incident: \n 0-Diagnosed Succesfully \n 1-No Fault Found \n 2-No User Response \n 3-Not Reproducible \n 4-Out of Scope \n 5-Request Rejected \n 6-Resolved Succesfully \n 7-Unable to Solve \n 8-Withdrawn by User \n 9-Automatically Closed \n 10-Solved by Change/Service Request \n 11-Solved by User Instruction \n 12-Solved by Workaround")
    code = await client.wait_for("message")
    while (code.channel.id != channel.id) or (code.author == client.user) or (not (control.validateClosureCode(code.content))):
        if(code.channel.id == channel.id) and (code.author != client.user):
            await sendMessage(channel,"Closure code not valid. Must be a number between 0 and 12")
        code = await client.wait_for("message")
        if code.content.lower() == '!exit':
            return code.content.lower()
    return control.getClosureCode(code.content)


async def closeIncident(channel):
    try:
        incident = await getIncident(channel)
        if incident == '!exit':
            await sendCancelMessage(channel)
            return
        if incident.getPhase() == 'Closure':
            await sendMessage(channel,'The incident is already closed')
            return
        solution = await getSolution(channel)
        if solution == '!Exit' or solution == '!exit':
            return
        closureCode = await getClosureCode(channel)
        if closureCode == '!Exit' or closureCode == '!exit':
            return

        incident.setSolution(solution)
        incident.setClosureCode(closureCode)
        await sendMessage(channel,"Submitting incident to Service Manager")
        incidentJson = incident.toJsonObject()
        response = control.closeIncident(incident.toJsonObject())
        await sendMessage(channel,"Incident closed succesfully")
        msg = 'Incident ID: '+response['Incident']['IncidentID']+'\n'+'Incident Title: '+response['Incident']['Title']+'\n'+'Incident Description: '+response['Incident']['Description'][0]+'\n'+'Incident Impact: '+response['Incident']['Impact']+'\n'+'Incident Severity: '+response['Incident']['Urgency']+'\n'+'Incident Solution: '+response['Incident']['Solution'][0]+'\n'+'Incident Closure Code: '+response['Incident']['ClosureCode']
        await sendMessage(channel,msg)
    except Exception as exception:
        raise exception
        await sendMessage(channel,"There was a problem connecting to Service Manager. Try again later")
    finally:
        await sendFinishMessage(channel)

async def checkIncident(channel):
    try:
        response = await getIncidentData(channel)
        msg = 'Incident ID: '+response['Incident']['IncidentID']+'\n'+'Incident Title: '+response['Incident']['Title']+'\n'+'Incident Description: '+response['Incident']['Description'][0]+'\n'+'Incident Impact: '+response['Incident']['Impact']+'\n'+'Incident Severity: '+response['Incident']['Urgency']+'\n'+'Incident Solution: '+response['Incident']['Solution'][0]+'\n'+'Incident Closure Code: '+response['Incident']['ClosureCode']
        await sendMessage(channel,msg)
    except Exception as exception:
        raise exception
        await sendMessage(channel,"There was a problem connecting to Service Manager. Try again later")
    finally:
        await sendFinishMessage(channel)

async def getKpiList(channel):
    await sendMessage(channel,"Enter the number assigned to the KPIs you want to get, separated by commas, or enter \"\*\" to get all of them: \n 0-Average group reassignments \n 1-Average number of incidents solved per employee daily \n 2-Average days between Incident opening and closure \n 3-Number of incidents closed \n 4-Number of incidents closed this month \n 5-Number of incidents daily closed this month \n 6-Number of incidents created this month \n 7-Average number of incidents created daily this month \n 8-Number of incidents solved \n 9-Most common Incident priority \n 10-Percentage of critical Incidents \n 11-Percentage of Incidents escalated"+'\n For example: *\"1,2,3\"*; *\"5,2,1,9\"*; *\"1\"*;*\"\*\"*')

    kpis = await client.wait_for("message")
    while (kpis.channel.id != channel.id) or (kpis.author == client.user) or (not (control.validateKpiList(kpis.content))):
        if(kpis.channel.id == channel.id) and (kpis.author != client.user):
            await sendMessage(channel,"Kpi list not valid. Must be one or more numbers **from 0 to 11, or an asterisk**")
            kpis = await client.wait_for("message")
    return control.getKpis(kpis.content)


async def getKpi(channel):
    finished = False
    while not (finished):
        try:
            kpiList = await getKpiList(channel)
            if '!Exit' in kpiList or '!exit' in kpiList:
                return
            for kpi in kpiList:
                msg = 'KPI name: '+kpi.getName()+'\n'+'KPI value: '+str(kpi.getValue())+'\n'+'Date (dd/mm/yyyy hh:mm UTC+0): '+kpi.getFormattedDate()+'\n'+'-----------------------------------------'
                await sendMessage(channel,msg)
            await sendMessage(channel,'Do you want to get more KPIs? (Yes/No)')
            finishMessage = await client.wait_for("message")
            while (finishMessage.channel.id != channel.id) or (finishMessage.author == client.user) or not(control.validateFinishMessage(finishMessage.content)):
                if(finishMessage.channel.id == channel.id) and (finishMessage.author != client.user):
                    await sendMessage(channel,"Entry not valid. Must be \"Yes\" or \"No\"")
                finishMessage = await client.wait_for("message")
            if (finishMessage.content.lower() == 'no'):
                finished = True

        except Exception as exception:
            raise exception
            await sendMessage(channel,"There was a problem connecting to Service Manager. Try again later")
        finally:
             await sendFinishMessage(channel)


client.run(TOKEN)
