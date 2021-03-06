import discord
import json
from geocode import get_gridpoints
from geocode import getAlerts
from geocode import getForecast
from geocode import getForecastHourly

client = discord.Client()

@client.event
async def on_ready():
    print('Logged on as {0.user} '.format(client), end='')
    print(f'in {len(client.guilds)} guilds!')
    await client.change_presence(activity=discord.Activity(name='National Weather Service', type=discord.ActivityType.watching))

@client.event    
async def on_message(message):
    if message.content.startswith("!coords"):
        client_location = message.content[len("!coords") +1 :]
        location = get_gridpoints(client_location)
        channel = client.get_channel(message.channel.id)
        if location != None:
            await coordsEmbed(channel, location)
        else:
            await channel.send("Please input a valid location")
    if message.content.startswith("!areas"):
        channel = client.get_channel(message.channel.id)
        await channel.send("Available areas (for !alerts): ``AL, AK, AS, AR, AZ, CA, CO, CT, DE, DC, FL, GA, GU, HI, ID, IL, IN, IA, KS, KY, LA, ME, MD, MA, MI, MN, MS, MO, MT, NE, NV, NH, NJ, NM, NY, NC, ND, OH, OK, OR, PA, PR, RI, SC, SD, TN, TX, UT, VT, VI, VA, WA, WV, WI, WY, PZ, PK, PH, PS, PM, AN, AM, GM, LS, LM, LH, LC, LE, LO``")
    if message.content.startswith("!forecast"):
        client_location = message.content[len("!forecast") +1 :]
        channel = client.get_channel(message.channel.id)
        wait = await channel.send("Please wait, fetching data")
        forecast = getForecast(client_location)
        await wait.delete()
        if forecast == None:
            await channel.send("Please input a valid location")
        else:    
            i = 0
            for data in forecast:
                if i > 2:
                    break
                await forecastEmbed(channel, client_location, data)
                i = i+1
    if message.content.startswith("!alerts"):
        client_area = message.content[len("!alerts") +1 :]
        channel = client.get_channel(message.channel.id)
        wait = await channel.send("Please wait, fetching data")
        alerts = getAlerts(client_area)
        await wait.delete()
        if alerts != None:
            await alertsEmbed(channel, alerts, client_area)
        else:
            await channel.send("Please enter a valid area.\nUse !areas to list the areas")
    if message.content.startswith("!commands"):
        channel = client.get_channel(message.channel.id)
        await cmdsEmbed(channel)
    if message.content.startswith("!cmds"):
        channel = client.get_channel(message.channel.id)
        await cmdsEmbed(channel)
    if message.content.startswith("!hourly"):
        client_location = message.content[len("!hourly") +1 :]
        channel = client.get_channel(message.channel.id)
        wait = await channel.send("Please wait, fetching data")
        forecast = getForecastHourly(client_location)
        await wait.delete()
        if forecast == None:
            await channel.send("Please input a valid location")
        else:    
            i = 0
            for data in forecast:
                if i > 3:
                    break
                await forecastHourlyEmbed(channel, client_location, data)
                i = i+1
    if message.content.startswith("!info"):
        channel = client.get_channel(message.channel.id)
        await infoEmbed(channel)
    if message.content.startswith("!shutdown"):
        if message.author.id == 189405094452789257: # Enter Discord IDs of Users who can Shut Down Bot
            await client.logout()

@client.event
async def forecastEmbed(channel, location, data):
    embed = discord.Embed(
        title = data['name'],
        description = "Forecast for " + location,
        colour = 0x4285F4
    )
    embed.set_thumbnail(url=data['icon'])
    embed.set_footer(text="Visit weather.gov for official information")
    embed.add_field(name="Weather", value=data['shortForecast'], inline=False)
    embed.add_field(name="Temperature", value=str(data['temperature']) + " °F", inline=False)
    embed.add_field(name="Wind", value=data['windSpeed'] + " " + data['windDirection'], inline=False)
    await channel.send(embed=embed)

@client.event
async def alertsEmbed(channel, data, area):
    embed = discord.Embed(
        title = "Current watches, warnings, and advisories for " + area,
        colour = 0xFF7F50
    )
    embed.set_footer(text="Visit weather.gov for official information")
    i = 0
    for ndata in data:
        if i > 4:
            break
        i = i + 1
        embed.add_field(name=ndata['properties']['event'], value="**" + ndata['properties']['severity'] + "** - *" + ndata['properties']['areaDesc'] + "*\n" + ndata['properties']['headline'], inline=False)
    if i == 0:
        embed.add_field(name="No Alerts", value="There are currently no alerts in " + area + ". Visit weather.gov for official information")
    await channel.send(embed=embed)

@client.event
async def coordsEmbed(channel, data):
    embed = discord.Embed(
        title = data[2] + ", " + data[3],
        description = str(data[5]) + ", " + str(data[6]),
        colour = 0x006400
    )
    embed.set_footer(text="Visit weather.gov for official information")
    embed.add_field(name="NWS Gridpoint", value="X = " + str(data[0]) + ", Y = " + str(data[1]), inline=True)
    embed.add_field(name="NWS Office", value=data[4], inline=True)
    await channel.send(embed=embed)

@client.event
async def cmdsEmbed(channel):
    embed = discord.Embed(
        title = "Available Commands",
        colour = 0x006400
    )
    embed.set_footer(text="Visit weather.gov for official information")
    embed.add_field(name="!alerts [area]", value="Returns first five alerts for a specified area", inline=False)
    embed.add_field(name="!areas", value="Returns list of areas for !alerts command", inline=False)
    embed.add_field(name="!coords [location]", value="Returns coorditates, NWS gridpoint, and NWS office for a specified location", inline=False)
    embed.add_field(name="!forecast [location]", value="Returns forecast for next ~36 hours for a specified location", inline=False)
    embed.add_field(name="!hourly [location]", value="Returns hourly forecast for next ~4 hours for a specified location", inline=False)
    embed.add_field(name="!info", value="Returns list of information about bot and dependencies", inline=False)
    await channel.send(embed=embed)

@client.event
async def infoEmbed(channel):
    embed = discord.Embed(
        title = "Information",
        description = "Information about bot, libraries, and APIs",
        colour = 0x006400
    )
    embed.set_footer(text="Project for MLH RookieHacks 2020")
    embed.add_field(name="Project GitHub", value="https://github.com/MichaelRP1/rookiehacks. BSD-3-Clause License. Made for MLH RookieHacks 2020", inline=False)
    embed.add_field(name="National Weather Service API", value="https://api.weather.gov/. In the public domain.", inline=False)
    embed.add_field(name="Discord.py", value="https://github.com/Rapptz/discord.py. MIT License", inline=False)
    embed.add_field(name="Python Geocoder", value="https://github.com/DenisCarriere/geocoder. MIT License", inline=False)
    embed.add_field(name="Nominatim API", value="https://nominatim.org/. ODbL License", inline=False)
    await channel.send(embed=embed)

@client.event
async def forecastHourlyEmbed(channel, location, data):
    embed = discord.Embed(
        title = data['startTime'][len("0000-00-00T") : len("0000-00-00T00:00")],
        description = "Hourly Forecast for " + location,
        colour = 0x4285F4
    )
    embed.set_thumbnail(url=data['icon'])
    embed.set_footer(text="Visit weather.gov for official information")
    embed.add_field(name="Weather", value=data['shortForecast'], inline=False)
    embed.add_field(name="Temperature", value=str(data['temperature']) + " °F", inline=False)
    embed.add_field(name="Wind", value=data['windSpeed'] + " " + data['windDirection'], inline=False)
    await channel.send(embed=embed)

token = ""
with open('creds.json') as json_file:
    data = json.load(json_file)
    token = data['token']

client.run(token)