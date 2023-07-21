import discord
from decouple import config
import requests
import validators

intents = discord.Intents(messages=True, guilds=True, reactions=True, message_content=True)
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print("Joined")
    print(discord.__version__)


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if client.user.mention not in message.content:
        return

    if len(message.attachments) > 1:
        await message.channel.send(f"Only one file attachment can be sent at a time")
        return
    elif len(message.attachments) == 1:
        try:
            contents = await message.attachments[0].read()
            with open("file", 'wb') as f:
                f.write(contents)
                f.close()
        except Exception:
            return {"message": "There was an error uploading the file"}

        with open('file', 'rb') as f:
            r = requests.post('http://127.0.0.1:8000/post_file_report', files={'file': f})
            print(r)
            f.close()

        r = requests.get('http://127.0.0.1:8000/get_file_report').json()
        print(r)

        file_name = str(message.attachments[0]).split('/')[6]
        file_type = r['attributes']['type_description']
        sha256_hash = r['attributes']['sha256']
        stats = r['attributes']['last_analysis_stats']

        await message.channel.send(f"```File Name:  {file_name}\n"
                                   f"File Type:  {file_type}\n"
                                   f"SHA-256:    {sha256_hash}\n"
                                   f"Stats:      {stats}```")
        return

    array = message.content.split(" ")

    if str(array[1]).lower() == 'help' or str(array[1]).lower() == 'h' or str(array[1]).lower() == 'man':
        await message.channel.send(
            f"```Name:\n"
            f"      @MDS - Scan URL or File suspected to be malicious\n\n"
            f"Synopsis:\n"
            f"      @MDS [Hyperlink]\n"
            f"      @MDS [File Attachment]\n\n"
            f"Description:\n"
            f"      MDS allows users to analyse URLs and Files to receive a report on any malicious content\n```"
        )

        return

    if not validators.url(array[1]):
        await message.channel.send("Invalid URL")
        return

    url = f"http://127.0.0.1:8000/get_url_report?url={array[1]}"

    r = requests.get(url).json()

    site_name = 'Unknown'
    if 'html_meta' in r['attributes']:
        if 'og:site_name' in r['attributes']['html_meta'] and r['attributes']['html_meta']['og:site_name'][0] is not None:
            site_name = r['attributes']['html_meta']['og:site_name'][0]
        elif 'og:title' in r['attributes']['html_meta'] and r['attributes']['html_meta'] is not None:
            site_name = r['attributes']['html_meta']['og:title'][0]

    if 'title' in r['attributes']:
        site_name = r['attributes']['title']

    try:
        site_trackers_list = list(r['attributes']['trackers'].keys())
        site_trackers_string = ', '.join(site_trackers_list)
    except Exception:
        site_trackers_string = 'No Trackers'

    stats = r['attributes']['last_analysis_stats']

    await message.channel.send(f"```Site Name: {site_name}\n"
                               f"URL:       {array[1]}\n"
                               f"Trackers:  {site_trackers_string}\n"
                               f"Stats:     {stats}```")


client.run(config('BOT_KEY'))
