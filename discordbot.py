#!/usr/bin/env python
#discordbot.py
import asyncio
import os
import settings
import requests
from discord.ext.commands import Bot
import random
from discord.ext import commands
import openai

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
WLTOKEN = os.getenv('WARCRAFTLOGS_API_KEY')
openai.api_key = os.getenv('OPENAI_TOKEN')


client = Bot(command_prefix='!')


@client.command()
async def howto(ctx):
    message = "Commands: \n"
    message += "!ping- returns your ping\n"
    message += "!eightball message - let it decide your fate\n"
    message += "!cat - send a cat pic and a cat fact\n"
    message += "!bird - send a bird pic and a bird fact\n"
    message += "!weather cityname - self-explanatory\n"
    message += "!dadjoke - self-explanatory\n"
    message += "!logs charactername, or !logs charactername server, or !logs charactername server role [dps, hps, bossdps, tankhps, playerspeed] - retrieve >90% parses for Ny'alotha"
    await ctx.send(message)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.command(pass_context=True)
#@commands.check(is_animol)
async def birb(ctx):
    r = requests.get(f"https://some-random-api.ml/img/birb")
    if r.status_code != requests.codes.ok:
        await ctx.send(f'API seems to be down')
        return
    img = r.json()["link"]
    r = requests.get(f"https://some-random-api.ml/facts/bird")
    fact = r.json()["fact"]
    await ctx.send(f"{img}\n{fact}")


@client.command()
async def ping(ctx):
    await ctx.send(f'Your ping is {round(client.latency * 1000)}ms')

@client.command()
async def eightball(ctx):
    responses = ["Definitely", "Possible", "Nope", "Yes!", "I'm gonna have to say definitely maybe", "Not a chance", "Certainly", "Could go either way"]
    await ctx.send(random.choice(responses))

@client.command(pass_context=True)
async def cat(ctx):
    r = requests.get(f"https://api.thecatapi.com/v1/images/search")
    if r.status_code != requests.codes.ok:
        await ctx.send(f"API seems to be down")
        return
    img = r.json()[0]["url"]
    r = requests.get(f"https://cat-fact.herokuapp.com/facts")
    choice = random.choice(r.json()["all"])
    fact = choice["text"]
    await ctx.send(f"{img}\n{fact}")

@client.command()
async def dadjoke(ctx):
    r = requests.get(f"https://us-central1-dadsofunny.cloudfunctions.net/DadJokes/random/jokes")
    if r.status_code != requests.codes.ok:
        await ctx.send(f"API seems to be down")
        return
    data = r.json()
    joke = data['setup']
    punchline = data['punchline']
    await ctx.send(f"{joke}\n{punchline}")

@client.command()
async def hi(ctx):
    await ctx.send("What's up?")

@client.command()
async def weather(ctx, message):
    r = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={message}&units=metric&appid={settings.WEATHER_API_KEY}")
    if r.status_code != requests.codes.ok:
        await ctx.send(f'Invalid city')
        return
    data = r.json()
    city = data["name"]
    weather = data["weather"][0]["description"]
    temp = data["main"]["temp"]
    await ctx.send(f"Current weather for {city} is {weather} with a temperature of {round(temp)} degrees celsius")

@client.command()
async def openai(ctx, message):
    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=f"{message}",
        temperature=1,
        max_tokens=547,
        top_p=1,
        frequency_penalty=0.97,
        presence_penalty=1.35
    )
    await ctx.send(response)

@client.command()
async def logs(ctx, name, server = "nagrand", role="dps"):
    parse_dict = {}
    region = "eu"
    name = name.capitalize()
    r = requests.get(f"https://www.warcraftlogs.com:443/v1/rankings/character/{name}/{server}/{region}?zone=24&metric={role}&api_key={WLTOKEN}")
    if r.status_code != requests.codes.ok:
        await ctx.send(f'Unable to find parses for the data provided')
        return
    for i in r.json():
        bossname = i["encounterName"]
        if bossname not in parse_dict.keys():
            parse_dict[bossname] = {"rank":99999}
    print(parse_dict)
    for i in r.json():
        bossname = i["encounterName"]
        if parse_dict[bossname]["rank"] > i["rank"] and i["difficulty"] == 5:
            parse_dict[bossname] = {"rank":i["rank"],"outOf":i["outOf"],"percentile":i["percentile"]}

    try:
        for k, v in parse_dict.items():
            if v['percentile'] > 90:
                continue
    except KeyError:
        await ctx.send(f"{name} has no good parses for {role}")
        return
    await ctx.send(f"{name}\'s top parses as {role} are: ")
    message = ""
    for k, v in parse_dict.items():
        if v['percentile'] > 90:
            message += (f"{k} : rank {v['rank']} out of {v['outOf']}, {v['percentile']} percentile\n")
    await ctx.send(message)

client.run(TOKEN)
