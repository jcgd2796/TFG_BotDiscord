'''view.py
Main file of the bot. Acts as the view, connects with the controller and the model.
Author:
    Juan Carlos Gil Díaz'''
import sys
sys.path.append('/home/jcarlos/TFGDiscordBot') # root folder of the project, to enable imports
import os
import dotenv
import controller.Controller as control
import discord 
from dotenv import load_dotenv  #for the environment file, which stores passwords and tokens.

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GENERAL_CHANNEL_ID = int(os.getenv('GENERAL_CHANNEL'))
client = discord.Client()

'''Prints a message on the console when connected to Discord.'''
@client.event
async def on_ready():
    print(f'{client.user} is online and ready to work')

'''Method to redirect the users' requests to the required channel, after getting a message in the General channel.

This method is executed every time a message is received in the server. 
We use it only for the general channel, as the other channels have their methods.
First, it checks if the message was sent by the bot or in a different channel than general. If so, does nothing.
Else, it checks if the message starts with the mandatory command character, ignoring the message otherwise.
If the first character is a !, it checks the rest of the command. If it's an identified command, creates a private channel
and calls the method, displays help message otherwise.

Args: 
    message: The Message object containing the message sent by the user. Must be a discord.Message and cannot be None
Exceptions thrown:
    ValueError: if the message is None
'''
@client.event
async def on_message(message):
    if (message == None):
        raise ValueError('message is None')
    elif(message.author == client.user or message.channel.id != GENERAL_CHANNEL_ID):
        return
    else:
        #Private channel permissions
        PERMISSIONS = {message.guild.default_role: discord.PermissionOverwrite(read_messages=False),message.author: discord.PermissionOverwrite(read_messages=True)}
        if(message.content[0]=="!"):
            if(getCommand(message.content)=="newIncident"):
                if control.checkSMAvailability(): #Always check if SM Server is available before doing anything
                    channel = await message.guild.create_text_channel("New Incident #"+str(len(message.guild.channels))+"", overwrites=PERMISSIONS)
                    await sendMessage(message.channel,"Go to channel "+channel.mention +" to create the incident.")
                    await newIncident(channel)
                else:
                    await sendMessage(message.channel,"Service Manager is not available right now. Try again later")

            elif(getCommand(message.content)=="updateIncident"):
                if control.checkSMAvailability():
                    channel = await message.guild.create_text_channel("Update Incident #"+str(len(message.guild.channels))+"", overwrites=PERMISSIONS)
                    await sendMessage(message.channel,"Go to channel "+channel.mention +" to update the incident.")
                    await updateIncident(channel)
                else:
                    await sendMessage(message.channel,"Service Manager is not available right now. Try again later")

            elif(getCommand(message.content)=="closeIncident"):
                if control.checkSMAvailability():
                    channel = await message.guild.create_text_channel("Close Incident #"+str(len(message.guild.channels))+"", overwrites=PERMISSIONS)
                    await sendMessage(message.channel,"Go to channel "+channel.mention +" to close the incident.")
                    await closeIncident(channel)
                else:
                    await sendMessage(message.channel,"Service Manager is not available right now. Try again later")

            elif(getCommand(message.content)=="checkIncident"):
                if control.checkSMAvailability():
                    channel = await message.guild.create_text_channel("Check Incident #"+str(len(message.guild.channels))+"", overwrites=PERMISSIONS)
                    await sendMessage(message.channel,"Go to channel "+channel.mention +" to get the incident data.")
                    await checkIncident(channel)
                else:
                    await sendMessage(message.channel,"Service Manager is not available right now. Try again later")
            
            elif(getCommand(message.content)=="getKpi"):
                if control.checkSMAvailability():
                    channel = await message.guild.create_text_channel("Get KPI #"+str(len(message.guild.channels))+"", overwrites=PERMISSIONS)
                    await sendMessage(message.channel,"Go to channel "+channel.mention +" to get the desired KPIs.")
                    await getKpi(channel)
                else:
                    await sendMessage(message.channel,"Service Manager is not available right now. Try again later")
            else: #!help or an invalid command
                await sendMessage(message.channel,"Avalable actions: \n !help: shows available actions. \n !newIncident: starts the incident creation. \n !updateIncident: modify an incident.\n !closeIncident: Close an incident. \n !checkIncident: get an incident. \n !getKpi: get one or more KPIs (Key Performance Indicator)")
    return

'''Returns the first line of the message given as argument without the ! symbol

Args:
    content: The string representing the message to process. Must be a string and cannot be None.
Exceptions thrown:
    ValueError: if the content is None
Return:
The command entered by the user without the ! symbol and on a single line'''
def getCommand(content):
    if content == None:
        raise ValueError('The content is None')
    return content.split('!')[1].split('\n')[0]

'''Create a new Incident and submit it to Service Manager Server in the channel given as argument. 
It gathers and validates all the data and then send it to SM.
Args:
    channel: The channel where the method will listen the user messages. Must be an existing channel in the actual server and cannot be None.
Exceptions thrown:
    ValueError: if the channel is None
'''
async def newIncident(channel):
    if channel == None:
        raise ValueError('The channel is None')
    else:
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
        except Exception:
            await sendMessage(channel,"There was a problem connecting to Service Manager. Try again later")
        finally:
            await sendFinishMessage(channel)
            return

'''Request the Operator login in the channel given as argument in order to get it from SM
Args:
    channel: The channel where the method will listen the user messages. Must be an existing channel in the actual server and cannot be None.
Exceptions thrown:
    ValueError: if the channel is None
Return:
    The name of the operator whose login was provided by the user
'''
async def getOperator(channel):
    if channel == None:
        raise ValueError('The channel is None')
    else:
        await sendMessage(channel,"Enter your Service Manager Login: ")
        operator = await client.wait_for("message")
        #Keeps requesting for the login while the message is sent in a different channel than the one created, the message is sent by the bot, or if it's not valid
        while (operator.channel.id != channel.id) or (operator.author == client.user) or (not (control.validateLogin(operator.content))): 
            #Only displays a message if the message was sent in the right channel and not by the bot.
            if(operator.channel.id == channel.id) and (operator.author != client.user):
                await sendMessage(channel,"User not found, enter your Service Manager Login")
            operator = await client.wait_for("message")
        #If the user wants to interrupt the process, no SM search is performed.
        if operator.content.lower() == '!exit':
            return operator.content.lower()
        #Gets the operator's name. Will be used as the "requested by" field of the Incident
        return control.getOperatorName(operator.content)

'''Request a title for the Incident in the channel given as argument, in a similar way as for the Operator login
Args:
    channel: The channel where the method will listen the user messages. Must be an existing channel in the actual server and cannot be None.
Exceptions thrown:
    ValueError: if the channel is None
Return:
    The title string provided by the user'''
async def getTitle(channel):
    if channel == None:
        raise ValueError('The channel is None')
    else:
        await sendMessage(channel,"Enter Incident title")
        title = await client.wait_for("message")
        while (title.channel.id != channel.id) or (not (control.validateTitle(title.content))) or (title.author == client.user):
            if(title.channel.id == channel.id) and (title.author != client.user):
                await sendMessage(channel,"Title not valid, enter Incident title")
            title = await client.wait_for("message")
        if title.content.lower() == '!exit':
            return title.content.lower()
        return title.content

'''Request a title for the Incident in the channel given as argument, in a similar way as for the Incident title
Args:
    channel: The channel where the method will listen the user messages. Must be an existing channel in the actual server and cannot be None.
Exceptions thrown:
    ValueError: if the channel is None
Return:
    The description string provided by the user'''
async def getDescription(channel):
    if channel == None:
        raise ValueError('The channel is None')
    else:
        await sendMessage(channel,"Enter Incident description")
        description = await client.wait_for("message")
        while (description.channel.id != channel.id) or (not (control.validateTitle(description.content))) or (description.author == client.user):
            if(description.channel.id == channel.id) and (description.author != client.user):
                await sendMessage(channel,"Description not valid, try again")
            description = await client.wait_for("message")
        if description.content.lower() == '!exit':
            return description.content.lower()
        return description.content

'''Request a CI (Configuration Item) for the Incident in the channel given as argument, in a similar way as for the Operator login
Args:
    channel: The channel where the method will listen the user messages. Must be an existing channel in the actual server and cannot be None.
Exceptions thrown:
    ValueError: if the channel is None
Return:
    The CI as a Json string'''
async def getCI(channel):
    if channel == None:
        raise ValueError('The channel is None')
    else:
        await sendMessage(channel,"Enter name of the Affected CI.")
        ci = await client.wait_for("message")
        while (ci.channel.id != channel.id) or (not (control.validateCI(ci.content))) or (ci.author == client.user):
            if(ci.channel.id == channel.id) and (ci.author != client.user):
                await sendMessage(channel,"CI with that name not found, try again")
            ci = await client.wait_for("message")
        if ci.content.lower() == '!exit':
            return ci.content.lower()
        return control.getCI(ci.content)['content'][0]['Device']['ConfigurationItem']

'''Request an impact value for the Incident in the channel given as argument, in a similar way as for the Operator login
Args:
    channel: The channel where the method will listen the user messages. Must be an existing channel in the actual server and cannot be None.
Exceptions thrown:
    ValueError: if the channel is None
Return:
    The impact value provided by the user.'''
async def getImpact(channel):
    if channel == None:
        raise ValueError('The channel is None')
    else:
        await sendMessage(channel,"Enter Incident impact value (from 2-High to 4-Low)")
        impact = await client.wait_for("message")
        while (impact.channel.id != channel.id) or (not (control.validateImpact(impact.content))) or (impact.author == client.user):
            if(impact.channel.id == channel.id) and (impact.author != client.user):
                await sendMessage(channel,"Impact value not valid, try again")
            impact = await client.wait_for("message")
        if impact.content.lower() == '!exit':
            return impact.content.lower()
        return impact.content

'''Request a severity for the Incident in the channel given as argument, in a similar way as for the impact value
Args:
    channel: The channel where the method will listen the user messages. Must be an existing channel in the actual server and cannot be None.
Exceptions thrown:
    ValueError: if the channel is None
Return:
    The severity value provided by the user.'''
async def getSeverity(channel):
    if channel == None:
        raise ValueError('The channel is None')
    else:
        await sendMessage(channel,"Enter Incident severity value (from 2-High to 4-Low)")
        severity = await client.wait_for("message")
        while (severity.channel.id != channel.id) or (not (control.validateImpact(severity.content))) or (severity.author == client.user):
            if(severity.channel.id == channel.id) and (severity.author != client.user):
                await sendMessage(channel,"Severity value not valid, try again")
            severity = await client.wait_for("message")
        if severity.content.lower() == '!exit':
            return severity.content.lower()
        return severity.content

'''Update an Incident's fields. The communication with the user is done through the Discord channel given as argument.
The only fields of an incident that can be updated are the "Requested by", "title", "description", "impact" and "severity" ones.
Args:
    channel: The channel where the method will listen the user messages. Must be an existing channel in the actual server and cannot be None.
Exceptions thrown:
    ValueError: if the channel is None'''
async def updateIncident(channel):
    if channel == None:
        raise ValueError('The channel is None')
    else:
        try:
            #We allow the user to update more than one incidents on the same channel, reducing the number of channels created over time
            finished = False
            while not finished:
                #First the user is asked for the Incident ID. Already closed/in review phase incidents cannot be modified
                incident = await getIncident(channel)
                if incident == "!exit":
                    await sendCancelMessage(channel)
                    return
                if incident.getPhase() == 'Closure' or incident.getPhase == 'Review':
                    await sendMessage(channel,"The incident is closed or on Review phase. You can't update incidents in that phase")
                    continue
                
                #Ask the user which fields wants to update
                updateList = await getUpdateList(channel)
                if ("!exit" in updateList):
                    await sendCancelMessage(channel)
                    return
            
                #Ask the user for the new values for the fields to update
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

                #After all the new data is gathered, the Incident is updated in SM server.
                await sendMessage(channel,"Submitting incident to Service Manager")
                response = control.updateIncident(incident)
                await sendMessage(channel,"Incident updated succesfully. Remember to save the ID for future actions.")
                #The data of the updated Incident is displayed for the user
                msg = '**__Incident ID: '+response['Incident']['IncidentID']+'__**\n'+'Incident Title: '+response['Incident']['Title']+'\n'+'Incident Description: '+response['Incident']['Description'][0]+'\n'+'Incident Impact: '+response['Incident']['Impact']+'\n'+'Incident Severity: '+response['Incident']['Urgency']+'\n'+ 'Incident Status: '+response['Incident']['Status']
                await sendMessage(channel,msg)
                #Ask the user if he wants to continue modifying incidents.
                await sendMessage(channel,'Do you want to modify more incidents? (Yes/No)')
                finishMessage = await client.wait_for("message")
                while (finishMessage.channel.id != channel.id) or (finishMessage.author == client.user) or not(control.validateFinishMessage(finishMessage.content)):
                    if(finishMessage.channel.id == channel.id) and (finishMessage.author != client.user):
                        await sendMessage(channel,"Entry not valid. Must be \"Yes\" or \"No\"")
                    finishMessage = await client.wait_for("message")
                if (finishMessage.content.lower() == 'no'):
                    finished = True
        except Exception:
            await sendMessage(channel,"There was a problem connecting to Service Manager, or the Incident ID provided doesn't exist. Try again later")
        finally:
            await sendFinishMessage(channel)
            return

'''Get an Incident from SM server by its ID.  The communication with the user is done through a Discord channel given as argument.
Args:
    channel: The channel where the method will listen the user messages. Must be an existing channel in the actual server and cannot be None.
Exceptions thrown:
    ValueError: if the channel is None
Return:
    The Incident as an Incident object.'''
async def getIncident(channel):
    if channel == None:
        raise ValueError('The channel is None')
    else:
        await sendMessage(channel,"Enter the ID of the incident")
        incId = await client.wait_for("message")
        while (incId.channel.id != channel.id) or (not (control.validateIncident(incId.content))) or (incId.author == client.user):
            if(incId.channel.id == channel.id) and (incId.author != client.user):
                await sendMessage(channel,"Incident ID not valid. Try again")
            incId = await client.wait_for("message")
        if incId.content.lower() == '!exit':
            return incId.content.lower()
        return control.getIncident(incId.content)

'''Get the list of the Incident fields to update. The communication with the user is done through a Discord channel given as argument.
Args:
    channel: The channel where the method will listen the user messages. Must be an existing channel in the actual server and cannot be None.
Exceptions thrown:
    ValueError: if the channel is None
Return:
    The list of the fields to update, without repeated elements.'''
async def getUpdateList(channel):
    if channel == None:
        raise ValueError('The channel is None')
    else:
        await sendMessage(channel,"Enter the values you want to update, separated by commas. Accepted values are operator, title, description, impact and severity")
        values = await client.wait_for("message")
        while (values.channel.id != channel.id) or (not (control.validateFieldsList(values.content))) or (values.author == client.user):
            if(values.channel.id == channel.id) and (values.author != client.user):
                await sendMessage(channel,"At least one of the values is not valid, Accepted values are operator, title, description, impact and severity")
            values = await client.wait_for("message")
        return control.getFieldValuesList(values.content)

'''Get an Incident values, including its status and (if have them) solution and closure code. The communication with the user is done through a Discord channel given as argument.
Args:
    channel: The channel where the method will listen the user messages. Must be an existing channel in the actual server and cannot be None.
Exceptions thrown:
    ValueError: if the channel is None'''
async def checkIncident(channel):
    if channel == None:
        raise ValueError('The channel is None')
    else:
        try:
            #First, ask the user for the Incident ID in the Discord channel created for the process.
            response = await getIncidentData(channel)
            if (response == "!exit"):
                return
            try:
                msg = 'Incident ID: '+response['Incident']['IncidentID']+'\n'+'Incident Title: '+response['Incident']['Title']+'\n'+'Incident Description: '+response['Incident']['Description'][0]+'\n'+'Incident Impact: '+response['Incident']['Impact']+'\n'+'Incident Severity: '+response['Incident']['Urgency']+'\n'+'Incident Status: '+response['Incident']['Status']+'\n'+'Incident Solution: '+response['Incident']['Solution'][0]+'\n'+'Incident Closure Code: '+response['Incident']['ClosureCode']
                await sendMessage(channel,msg)
            except KeyError:
                msg = 'Incident ID: '+response['Incident']['IncidentID']+'\n'+'Incident Title: '+response['Incident']['Title']+'\n'+'Incident Description: '+response['Incident']['Description'][0]+'\n'+'Incident Impact: '+response['Incident']['Impact']+'\n'+'Incident Severity: '+response['Incident']['Urgency']+'\n'+'Incident Status: '+response['Incident']['Status']
                await sendMessage(channel,msg)
        except Exception:
            await sendMessage(channel,"There was a problem connecting to Service Manager, or the identifier doesn't belong to any Incident. Try again later")
        finally:
            await sendFinishMessage(channel)
            return

'''Gets an Incident from SM server.
Args:
    channel: The channel where the method will listen the user messages. Must be an existing channel in the actual server and cannot be None.
Exceptions thrown:
    ValueError: if the channel is None
Return:
    The Incident as a Json string'''
async def getIncidentData(channel):
    if channel == None:
        raise ValueError('The channel is None')
    else:
        await sendMessage(channel,"Enter the ID of the incident")
        incId = await client.wait_for("message")
        while (incId.channel.id != channel.id) or (not (control.validateIncident(incId.content))) or (incId.author == client.user):
            if (incId.content.lower() == '!exit' and channel.id == incId.channel.id):
                return incId.content.lower()
            if(incId.channel.id == channel.id) and (incId.author != client.user):
                await sendMessage(channel,"Incident ID not valid. Try again")
            incId = await client.wait_for("message")
        if (incId.content.lower() == '!exit' and channel.id == incId.channel.id):
            return incId.content.lower()
        return control.getIncidentData(incId.content)

'''Closes an opened Incident, providing a solution and a closure code. The communication with the user is done through a Discord channel given as argument.
Args:
    channel: The channel where the method will listen the user messages. Must be an existing channel in the actual server and cannot be None.
Exceptions thrown:
    ValueError: if the channel is None'''
async def closeIncident(channel):
    if channel == None:
        raise ValueError('The channel is None')
    else:
        try:
            incident = await getIncident(channel)
            if incident == '!exit':
                await sendCancelMessage(channel)
                return
            #Already closed incidents cannot be updated.
            if incident.getPhase() == 'Closure' or incident.getPhase == 'Review':
                await sendMessage(channel,'The incident is already closed or in review phase')
                return
            #In order to be closed, an Incident must hava a solution and a closure code.
            solution = await getSolution(channel)
            if solution == '!Exit' or solution == '!exit':
                return
            closureCode = await getClosureCode(channel)
            if closureCode == '!Exit' or closureCode == '!exit':
                return

            incident.setSolution(solution)
            incident.setClosureCode(closureCode)
            await sendMessage(channel,"Submitting incident to Service Manager")
            response = control.closeIncident(incident)
            await sendMessage(channel,"Incident closed succesfully")
            msg = 'Incident ID: '+response['Incident']['IncidentID']+'\n'+'Incident Title: '+response['Incident']['Title']+'\n'+'Incident Description: '+response['Incident']['Description'][0]+'\n'+'Incident Impact: '+response['Incident']['Impact']+'\n'+'Incident Severity: '+response['Incident']['Urgency']+'\n'+'Incident Status: '+response['Incident']['Status']+'\n'+'Incident Solution: '+response['Incident']['Solution'][0]+'\n'+'Incident Closure Code: '+response['Incident']['ClosureCode']
            await sendMessage(channel,msg)
        except Exception:
            await sendMessage(channel,"There was a problem connecting to Service Manager, or the ID of the incident wasn't correct. Try again later")
        finally:
            await sendFinishMessage(channel)
            return

'''Ask the user for a solution for the Incident. The communication with the user is done through a Discord channel given as argument.
Args:
    channel: The channel where the method will listen the user messages. Must be an existing channel in the actual server and cannot be None.
Exceptions thrown:
    ValueError: if the channel is None
Return:
    The string containing the solution provided by the user.'''
async def getSolution(channel):
    if channel == None:
        raise ValueError('The channel is None')
    else:
        await sendMessage(channel,"Enter the solution of the Incident")
        solution = await client.wait_for("message")
        while (solution.channel.id != channel.id) or (not (control.validateTitle(solution.content))) or (solution.author == client.user):
            if(solution.channel.id == channel.id) and (solution.author != client.user):
                await sendMessage(channel,"Solution not valid. Try again")
            solution = await client.wait_for("message")
            if solution.content.lower() == '!exit':
                return solution.content.lower()
        return solution.content

'''Ask the user for a closure code for the Incident. The communication with the user is done through a Discord channel given as argument.
Args:
    channel: The channel where the method will listen the user messages. Must be an existing channel in the actual server and cannot be None.
Exceptions thrown:
    ValueError: if the channel is None
Return:
    The string value matching the number of the closure code.'''
async def getClosureCode(channel):
    if channel == None:
        raise ValueError('The channel is None')
    else:
        await sendMessage(channel,"Enter the number of the closure code of the Incident: \n 0-Diagnosed Succesfully \n 1-No Fault Found \n 2-No User Response \n 3-Not Reproducible \n 4-Out of Scope \n 5-Request Rejected \n 6-Resolved Succesfully \n 7-Unable to Solve \n 8-Withdrawn by User \n 9-Automatically Closed \n 10-Solved by Change/Service Request \n 11-Solved by User Instruction \n 12-Solved by Workaround")
        code = await client.wait_for("message")
        while (code.channel.id != channel.id) or (code.author == client.user) or (not (control.validateClosureCode(code.content))):
            if(code.channel.id == channel.id) and (code.author != client.user):
                await sendMessage(channel,"Closure code not valid. Must be a number between 0 and 12")
            code = await client.wait_for("message")
            if code.content.lower() == '!exit':
                return code.content.lower()
        return control.getClosureCode(code.content)

'''Get the KPIs to be requested by the user. The communication with the user is done through a Discord channel given as argument.
Args:
    channel: The channel where the method will listen the user messages. Must be an existing channel in the actual server and cannot be None.
Exceptions thrown:
    ValueError: if the channel is None'''
async def getKpi(channel):
    if channel == None:
        raise ValueError('The channel is None')
    else:
        finished = False
        #User can request more than one KPI at once using the same channel.
        try:
            while not (finished):
                kpiList = await getKpiList(channel)
                if '!exit' in kpiList:
                    await sendCancelMessage(channel)
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
        except Exception:
            await sendMessage(channel,"There was a problem connecting to Service Manager. Try again later")
        finally:
            await sendFinishMessage(channel)
            return

'''Gets the list of KPIs to be obtained from SM server The communication with the user is done through a Discord channel given as argument.  
Args:
    channel: The channel where the method will listen the user messages. Must be an existing channel in the actual server and cannot be None.
Exceptions thrown:
    ValueError: if the channel is None
Return:
    The list containing all the requested KPIs'''
async def getKpiList(channel):
    if channel == None:
        raise ValueError('The channel is None')
    else:
        await sendMessage(channel,"Enter the number assigned to the KPIs you want to get, separated by commas, or enter \"\*\" to get all of them: \n 0-Average group reassignments \n 1-Average number of incidents solved per employee daily \n 2-Average days between Incident opening and closure \n 3-Number of incidents closed \n 4-Number of incidents closed this month \n 5-Number of incidents daily closed this month \n 6-Number of incidents created this month \n 7-Average number of incidents created daily this month \n 8-Number of incidents solved \n 9-Most common Incident priority \n 10-Percentage of critical Incidents \n 11-Percentage of Incidents escalated"+'\n For example: *\"1,2,3\"*; *\"5,2,1,9\"*; *\"1\"*;*\"\*\"*')
        kpis = await client.wait_for("message")
        while (kpis.channel.id != channel.id) or (kpis.author == client.user) or (not (control.validateKpiList(kpis.content))):
            if(kpis.channel.id == channel.id) and (kpis.author != client.user):
                await sendMessage(channel,"Kpi list not valid. Must be one or more numbers **from 0 to 11, or an asterisk**")
            kpis = await client.wait_for("message")
        if "!exit" in kpis.content.lower():
            return "!exit"
        return control.getKpis(kpis.content)

'''Sends a message to a channel, both given as arguments.
Args:
    channel: The Channel where the method will listen the user messages. Must be an existing channel in the actual server and cannot be None.
    message: The message to be sent in the channel. Must be a string and cannot be None
Exceptions thrown:
    ValueError: if the channel or the message are None'''
async def sendMessage(channel,message):
    if channel == None or message == None:
        raise ValueError('The channel or the message are None')
    else:
        await channel.send(message)
        return

'''ends an error message to the channel given as argument.
Args:
    channel: The channel where the method will listen the user messages. Must be an existing channel in the actual server and cannot be None.
Exceptions thrown:
    ValueError: if the channel is None'''
async def sendCancelMessage(channel):
    if channel == None:
        raise ValueError('The channel is None')
    else:
        await sendMessage(channel,"Operation canceled, no changes performed.")
        return

'''Sends a finished process message to the channel given as argument
Args:
    channel: The channel where the method will listen the user messages. Must be an existing channel in the actual server and cannot be None.
Exceptions thrown:
    ValueError: if the channel is None'''
async def sendFinishMessage(channel):
    if channel == None:
        raise ValueError('The channel is None')
    else:
        await sendMessage(channel,"My job here is done, I won't interact with this channel again. Go to the "+client.get_channel(GENERAL_CHANNEL_ID).mention+" channel to start a new request." )
        return

#Starts the bot
client.run(TOKEN)
