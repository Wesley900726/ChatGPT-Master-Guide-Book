
import os
from threading import Thread

import discord
from dotenv import load_dotenv
from flask import Flask
import opencc

from models import OpenAIModel
from discordBot import DiscordClient, Sender


load_dotenv()
app = Flask('ChatGPT-Discord-Bot')

s2t_converter = opencc.OpenCC('s2t')
model = OpenAIModel(api_key=os.getenv('OPENAI_API_TOKEN'), model_engine=os.getenv('OPENAI_MODEL_ENGINE'))


def run():
    client = DiscordClient()
    sender = Sender()

    @client.tree.command(name='brainstorming', description='ChatGPT help you brainstorm and come up with ten ideas.')
    async def brainstorming(interaction: discord.Interaction, *, message: str):
        if interaction.user == client.user:
            return
        await interaction.response.defer()
        try:
            messages = [{
                'role': 'system', 'content': os.getenv('BRAINSTORMING_SYSTEM_MESSAGE')
            }, {
                'role': 'user', 'content': os.getenv('BRAINSTORMING_PROMPT').format(message)
            }]
            _, content = model.chat_completion(messages)
            content = s2t_converter.convert(content)
            await sender.send_message(interaction, message, content)
        except Exception as e:
            await sender.send_message(interaction, message, str(e))

    @client.tree.command(name="translate", description="ChatGPT help you translate English into Chinese.")
    async def translate(interaction: discord.Interaction, *, message: str):
        if interaction.user == client.user:
            return
        await interaction.response.defer()

        try:
            messages = [{
                'role': 'system', 'content': os.getenv('TRANSLATE_SYSTEM_MESSAGE')
            }, {
                'role': 'user', 'content': os.getenv('TRANSLATE_PROMPT').format(message)
            }]
            _, content = model.chat_completion(messages)
            content = s2t_converter.convert(content)
            await sender.send_message(interaction, message, content)
        except Exception as e:
            await sender.send_message(interaction, message, str(e))
    client.run(os.getenv('DISCORD_TOKEN'))


def server_run():
    app.run(host='0.0.0.0', port=5000)


@app.route('/')
def home():
    return "Hello World!"


if __name__ == '__main__':
    t = Thread(target=server_run)
    t.start()
    run()
