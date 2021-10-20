import discord
import config
import datetime

GUILD = config.GUILD
TOKEN = config.TOKEN

client = discord.Client()
questions = ["Pergunta 1/7\nQual sua idade?",
             "Pergunta 2/7\nTem microfone?",
             "Pergunta 3/7\nQual seu nick no game?",
             "Pergunta 4/7\nEscolheu as armas que vai usar? Se sim, quais?",
             "Pergunta 5/7\nQual estilo de jogo mais te agrada? ex. Crafting, PvE, PvP, GvG...",
             "Pergunta 6/7\nSe compromete em ler e seguir as regras da guild?",
             "Pergunta 7/7\nSe compromete em ficar atento ao canal de comunicados da guild?",
             "Você completou o formulário, entraremos em contato."]


@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

        print(f'{client.user} is connected to the following guild:\n'
              f'{guild.name}(id: {guild.id})')

    register_chat = client.get_channel(config.REGISTER)
    messages = await register_chat.history().flatten()

    for message in messages:
        await check_reactions(message.reactions)


async def check_reactions(reactions):
    id_list = []
    guild = await client.fetch_guild(config.GUILD_ID)
    for reaction in reactions:
        people_who_reacted = await reaction.users().flatten()

        for human_being in people_who_reacted:
            id_list.append(human_being.id)

        for discriminator in id_list:
            member = await guild.fetch_member(discriminator)
            if len(member.roles) == 1 and member.bot is False:
                await start_form(member)


async def send_form(register_chat):
    start_embed = discord.Embed(title='**Bem-vindo ao servidor da Laughing Coffin**', color=0x220f21)
    start_embed.add_field(name='Somos uma guilda 4Fun de New World.',
                          value='Se estiver procurando um ambiente tranquilo pra __**aproveitar AEternum**__ '
                                'e __**fazer novas amizades**__, clique no pergaminho e torne-se membro.',
                          inline=False)
    start_embed.set_thumbnail(url='https://i2.wp.com/ebonwingcourt.shopsmallus.com/wp-content/uploads/sites/5/2021/07/syndicate-icon.png?w=720')
    start_embed.set_image(url="https://wallpapercave.com/wp/wp7045893.png")
    start_embed.set_footer(text='caxao risadinha kkkkk', icon_url='https://media.discordapp.net/attachments/470259225613041695/888652445532688384/unknown.png')

    await register_chat.send(embed=start_embed)


async def start_form(user):
    for role in user.roles:
        if role.name == 'Membro':
            print(f'O esquisito do {user.name} ta tentando criar um form e falhando miseravelmente.')
            return

    await clear_dm_with_user(user)
    await send_question(user, 0)


async def flush_channel(channel):
    messages = await channel.history().flatten()
    if len(messages) != 0:
        await channel.delete_messages(messages)


async def clear_dm_with_user(user):
    message_history = await user.history().flatten()
    for message in message_history:
        if message.author.discriminator == config.DISCRIMINATOR:
            try:
                await message.delete()
            except discord.errors.NotFound:
                continue


async def send_question(user, number):
    await user.send(questions[number])


async def check_form(user, message):
    history = await message.channel.history().flatten()
    for i in history:
        if '1/7' in i.content:
            await send_question(user, 1)
            break
        elif '2/7' in i.content:
            await send_question(user, 2)
            break
        elif '3/7' in i.content:
            await send_question(user, 3)
            break
        elif '4/7' in i.content:
            await send_question(user, 4)
            break
        elif '5/7' in i.content:
            await send_question(user, 5)
            break
        elif '6/7' in i.content:
            await send_question(user, 6)
            break
        elif '7/7' in i.content:
            history = await message.channel.history().flatten()
            answers = collect(history)

            await clear_dm_with_user(user)

            await send_question(user, 7)
            await send_to_log(user, answers)
            break


@client.event
async def on_message(message):
    print(f'Message Received:   {message.content}', f'   From:   {message.author}')
    if message.author.discriminator == config.DISCRIMINATOR and message.channel.id == config.REGISTER:
        await message.add_reaction('\N{SCROLL}')

    if message.author.discriminator != config.DISCRIMINATOR:
        if type(message.channel) == discord.DMChannel:
            await check_form(message.author, message)


@client.event
async def on_raw_reaction_add(payload):
    print(f'Raw Reaction Received:  {str(payload.emoji)}', f'   From:   {payload.member}')

    if payload.member.discriminator != config.DISCRIMINATOR and str(payload.emoji) == '📜':
        await start_form(payload.member)


def collect(history):
    answers = []
    for i in range(len(history)):
        if i == 0:
            answers.append(history[i].content)
        elif '/7' in history[i].content and '1/7' not in history[i].content:
            answers.append(history[i+1].content)
    answers.reverse()
    return answers


async def send_to_log(user, answers):
    embed_answer = discord.Embed(title=user, color=0x220f21, timestamp=datetime.datetime.utcnow())
    backlog = await client.fetch_channel(config.BACKLOG)
    if len(answers) < 6:
        print('Tentaram mandar um formulário muito pequeno')
        return
    for i in range(len(answers)):
        embed_answer.add_field(name=questions[i],
                               value=answers[i],
                               inline=False)
    await backlog.send(user.mention, embed=embed_answer)

client.run(TOKEN)
