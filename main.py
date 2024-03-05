import nextcord
from nextcord.ext import commands, tasks
import json
import os
import random
from fasteners import InterProcessLock


file_lock = InterProcessLock(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Logs.lock'))

data = []
eligible_messages = []

def load_data():
    global data, eligible_messages
    try:
        with open('Logs.json', 'r') as f:
            data = json.load(f)

        eligible_messages = [
            msg["content"]
            for msg in data
            if not msg["content"].startswith("a!") and len(msg["content"]) < 10
        ]

    except FileNotFoundError:
        data = []
        eligible_messages = []

project_directory = os.path.dirname(os.path.abspath(__file__))

file_path = os.path.join(project_directory, 'Logs.json') 

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='a!', intents=intents)

def write_to_data(message):
    new_message = {
        "author": str(message.author),
        "content": message.content,
        "timestamp": str(message.created_at),
    }
    data.append(new_message)

    if not message.content.startswith("a!"):
        eligible_messages.append(message.content)

@tasks.loop(minutes=0.1) 
async def save_data_to_file():
    with open('Logs.json', 'w') as f:
        json.dump(data, f, indent=4)

@bot.command()
async def troll(ctx):
    if ctx.author == bot.user:
        return

    TrollMessage = " "
    if eligible_messages:
        for x in range(random.randrange(1, 50)):
            selected = random.choice(eligible_messages)
            TrollMessage += selected + " "
        await ctx.send(TrollMessage)
    else:
        print("Cannot Execute [a!troll]: No eligible data in JSON!")

@bot.event
async def on_ready():

    load_data()

    save_data_to_file.start()

    print("BOT IS NOW READY!!!!")
    print("----------------------------------------")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    write_to_data(message)

    await bot.process_commands(message)

## bot.run(BOT TOKEN HERE)
