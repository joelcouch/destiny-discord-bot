from threading import Thread, Event
from time import sleep
import discord
import random
import sched
import time
import asyncio

from discord.ext import commands

description = 'I like trains.'
prefix = '!'

print("")
print('Launching bot...', end="", flush=True)
client = commands.Bot(description=description, command_prefix=prefix)
scheduler = sched.scheduler(time.time, time.sleep)

lfg_channels = []
monitoring_channels = [
    'lfg', 'raid', 'looking-for-group', 'testing'
]

options = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫"]

active_activity = {}
reaction_monitor_message = {}

activity_types = ['Raid', 'Strike', 'Milestones', 'Other']
raid_types = ['Leviathan', 'Eater of Worlds', 'Spire of Stars']
strike_types = ['Vanguard', 'Nightfall', 'Heroic']
milestone_types = ['Any', 'Flashpoint', 'Clan XP', 'Crucible', 'Other']
other_types = ['Anything', 'Storyline', 'Cry']
players_needed = ['1', '2', '3', '4', '5']

raid_messages = {}
time_options = ["+30 Minutes", "+1 Hour", "+2 Hours", "+4 Hours", "Reset", "Confirm"]

sexual_jokes = [
    "When do you kick a midget in the balls?\n\nWhen he is standing next to your girlfriend saying her hair smells nice",
    "What's the difference between your job and a dead prostitute?\n\nYour job still sucks!",
    "What did the hurricane say to the coconut palm tree?\n\nHold on to your nuts, this is no ordinary blow job!",
    "How does a woman scare a gynecologist?\n\nBy becoming a ventriloquist!",
    "Did you hear about the guy who died of a Viagra overdose?\n\nThey couldn't close his casket.",
    "What's 6 inches long, 2 inches wide and drives women wild?\n\na $100 bill!",
    "Whats long and hard and has cum in it?\n\na cucumber",
    "How do you kill a circus clown?\n\nGo for the juggler!",
    "Who was the worlds first carpenter?\n\nEve, because she made Adams banana stand",
    "Why does Dr. Pepper come (cum) in a bottle?\n\nBecause his wife died!",
    "If a dove is the 'bird of peace' then what's the bird of 'true love'?\n\nThe swallow.",
    "What do you call a cheap circumcision?\n\na rip off Girl: 'Hey, what's up?' Boy: 'If I tell you, will you sit" +
    " on it?",
    "How do you get a nun pregnant?\n\nDress her up as an alter boy.",
    "Why can't you play Uno with a Mexican?\n\nThey steal all the green cards.",
    "Why don't orphans play baseball?\n\nThey don't know where home is",
    "What's the difference between a Catholic priest and a zit?\n\nAt least a zit waits until you're a teenager " +
    "before it cums on your face!",
    "What does it mean when your boyfriend is in your bed gasping for breath and calling your name?\n\nYou didn't" +
    " hold the pillow down long enough. Boy: 'Want to hear a joke about my dick? Never mind, its too long.' Girl: " +
    "'Wanna hear a joke about my pussy? Never mind, you won't get it.",
    "How do you tell if a chick is too fat to fuck ?\n\nWhen you pull her pants down her ass is still in them",
    "What do you call 2 guys fighting over a slut?\n\nTug-of-whore.",
    "If the world is a Jacket where do poor people live?\n\nIn the hood.",
    "What's the cure for marriage?\n\nAlcoholism.",
    "What do you call an anorexic bitch with a yeast infection?\n\nA Quarter Ponder with Cheese.",
    "Why do they call it PMS?\n\nBecause Mad Cow Disease was already taken",
    "How do you stop a dog from humping your leg?\n\nPick him up and suck on his cock!",
    "Why did the chicken cross the road?\n\nBecause North Korean long-range missiles can't go that far.",
    "What's slimy cold long and smells like pork?\n\nKermit the frogs finger",
    "What's a porn star's favorite drink?\n\n7 Up in cider.",
    "What's the difference between a bowling ball and a blonde?\n\nYou can only fit three fingers inside a bowling " +
    "ball!",
    "What do preists and McDonalds have in common?\n\nThey both stick there meat in 10 year old buns",
    "What do you call a white guy surrounded by 9 black guys?\n\nSteve Nash.",
    "Why can't Jesus play hockey?\n\nHe keeps getting nailed to the boards.",
    "How do you circumcise a hillbilly?\n\nKick his sister in the jaw.",
    "Why is the IRS going after Stormy Daniels?\n\nBecause she didn't declare all her 'gross' income.",
    "Why do men get their great ideas in bed?\n\nBecause their plugged into a genius!",
    "What do you call an artist with a brown finger?\n\nPiccassole",
    "Did you guys hear about the cannibal that made a bunch of businessmen into Chili?\n\nI guess he liked seasoned" +
    " professionals.",
    "What's the difference between a hooker and a drug dealer?\n\nA hooker can wash her crack and sell it again.",
    "Why was the guitar teacher arrested?\n\nFor fingering A minor.",
    "Three words to ruin a man's ego...?\n\n'Is it in?",
    "Whats 72?\n\n69 with three people watching",
    "What do the Mafia and a pussy have in common?\n\nOne slip of the tongue, and you're in deep shit. A redhead " +
    "tells her blonde stepsister, 'I slept with a Brazilian....' The blonde replies, 'Oh my God! You slut! How many " +
    "is a brazilian?",
    "Why don't black people go on cruises?\n\nThey already fell for that trick once.",
    "What's the difference between a dead baby and a pizza?\n\nI don't fuck a pizza before I eat it."
]

jokes = [
    "Crime in multi-storey car parks. That is wrong on so many different levels.",
    "I have downloaded this new app. Its great, it tells you what to wear, what to eat and if you've put on weight. " +
    "Its called the Daily Mail.",
    "When I was younger I felt like a man trapped inside a woman's body. Then I was born.",
    "I was playing chess with my friend and he said, 'Let's make this interesting'. So we stopped playing chess.",
    "I usually meet my girlfriend at 12:59 because I like that one-to-one time.",
    "I really wanted kids when I was in my early 20s but I could just never… lure them into my car. No, I'm kidding…" +
    " I don't have a licence.",
    "I was very naive sexually. My first boyfriend asked me to do missionary and I buggered off to Africa for six" +
    " months.",
    "One in four frogs is a leap frog.",
    "Love is like a fart. If you have to force it it's probably shit.",
    "I used to be addicted to swimming but I'm very proud to say I've been dry for six years.",
    "My grandad has a chair in his shower which makes him feel old, so in order to feel young he sits on it" +
    " backwards like a cool teacher giving an assembly about drugs.",
    "My girlfriend is absolutely beautiful. Body like a Greek statue – completely pale, no arms.",
    "My husband's penis is like a semi colon. I can't remember what it's for and I never use it anyway.",
    "Is it possible to mistake schizophrenia for telepathy? I hear you ask.",
    "I was raised as an only child, which really annoyed my sister.",
    "I bought myself some glasses. My observational comedy improved.",
    "You know you're working class when your TV is bigger than your book case.",
    "Most of my life is spent avoiding conflict. I hardly ever visit Syria.",
    "Life is like a box of chocolates. It doesn't last long if you're fat.",
    "I was thinking of running a marathon, but I think it might be too difficult getting all the roads closed and" +
    " providing enough water for everyone.",
    "You can't lose a homing pigeon. If your homing pigeon doesn't come back, then what you've lost is a pigeon.",
    "My Dad said, always leave them wanting more. Ironically, that's how he lost his job in disaster relief.",
    "I really wish ISIS would stop playing violent video games and listening to Marilyn Manson.",
    "There's only one thing I can't do that white people can do, and that's play pranks at international airports.",
    "How do people make new mates? Asking for a friend.",
    "I wanted to do a show about feminism. But my husband wouldn't let me.",
    "One thing you'll never hear a Hindu say… 'Ah well, you only live once.",
    "My Dad told me to invest my money in bonds. So I bought 100 copies of Goldfinger.",
    "I've decided to stop masturbating, since then I've not really felt myself.",
    "I always thought Trojan was a bad name for a condom brand because of course the Trojans were a people whose" +
    " lives were ruined when a vessel containing little warriors unexpectedly exploded inside their city walls.",
    "My wife told me: 'Sex is better on holiday.' That wasn't a nice postcard to receive.",
    "The first time I met my wife, I knew she was a keeper. She was wearing massive gloves.",
    "As a kid I was made to walk the plank. We couldn't afford a dog.",
    "Money can't buy you happiness? Well, check this out, I bought myself a Happy Meal.",
    "My father was never sexist, he beat my brothers and I equally.",
    "The Scots invented hypnosis, chloroform and the hypodermic syringe. Wouldn't it just be easier to talk to" +
    " a woman?",
    "If you arrive fashionably late in Crocs, you're just late.",
    "I can't exercise for long periods. When I get back from a run my girlfriend usually asks if I've forgotten" +
    " something.",
    "I saw a documentary on how ships are kept together. Riveting!",
    "I'm learning the hokey cokey. Not all of it. But – I've got the ins and outs.",
    "Today… I did seven press ups: not in a row.",
    "Stephen Hawking had his first date for 10 years last week. He came back, his glasses were smashed, he had" +
    " a broken wrist, a twisted ankle and grazed knees; apparently she stood him up!",
    "People say I've got no willpower but I've quit smoking loads of times.",
    "My friend got a personal trainer a year before his wedding. I thought: 'Bloody hell, how long's the aisle " +
    "going to be'.",
    "Golf is not just a good walk ruined, it's also the act of hitting things violently with a stick ruined.",
    "Feminism is not a fad. It's not like Angry Birds. Although it does involve a lot of Angry Birds. Bad example.",
    "I love languages. The way nationalities have different takes on the same thing. Like the way an Irish person" +
    " or a Scottish person would say that the band Snow Patrol are boring but an Eskimo has a hundred words for" +
    " how crap Snow Patrol are.",
    "Oh my god, mega drama the other day: My dishwasher stopped working! Yup, his visa expired.",
    "'I think jokes about learning difficulties are OK so long as they're clever' is like saying 'I think jokes" +
    " about blind people are OK so long as they're visual'",
    "I just bought underwater headphones and it's made me loads faster. Do you know how motivating it is swimming" +
    " to the theme song from Jaws? I mean my anxiety is through the roof but record times.",
    "I'm single. By choice. Her choice. No it was a mutual thing. We came to the mutual agreement that she would" +
    " marry her ex boyfriend.",
    "My mother told me, you don't have to put anything in your mouth you don't want to. Then she made me eat" +
    " broccoli, which felt like double standards.",
    "Red sky at night: shepherd's delight. Blue sky at night: day.",
    "It all starts innocently, mixing chocolate and Rice Krispies, but before you know it you're adding raisins" +
    " and marshmallows – it's a rocky road.",
    "I was watching the London Marathon and saw one runner dressed as a chicken and another runner dressed as an " +
    "egg. I thought: 'This could be interesting.",
    "The anti-ageing advert that I would like to see is a baby covered in cream saying, 'Aah, I've used too much'",
    "I'm sure wherever my Dad is: he's looking down on us. He's not dead, just very condescending.",
    "Looking at my face is like reading in the car. It's all right for 10 minutes, then you start to feel sick",
    "Doctor, doctor! Sorry mate. It's a Saturday.",
    "Whenever I see a man with a beard, moustache and glasses, I think, 'There's a man who has taken every" +
    " precaution to avoid people doodling on photographs of him",
    "Miley Cyrus. You know when she was born? 1992. I've got condiments in my cupboard older than that.",
    "'What's a couple?' I asked my mum. She said, 'Two or three'. Which probably explains why her marriage collapsed",
    "My friend said she was giving up drinking from Monday to Friday. I'm just worried she's going to dehydrate",
    "I have the woman-flu. Which is like the manflu but worse because I also regularly have periods and I get " +
    "paid less.",
    "Kim Kardashian tried to break the internet. She didn't succeed but she did leave a large visible crack.",
    "I like Jesus but he loves me, so it's awkward.",
    "My granny was recently beaten to death by my grandad. Not as in, with a stick – he just died first",
    "I think if you were hardcore anti-feminism, surely you wouldn't call yourself 'anti-feminism' would you?" +
    " You'd call yourself 'Uncle Feminism'.",
    "My mate is called Liam, but we call him 'Two Legs Liam'. The reason for that is because he only has one arm.",
    "I am writing a film script about going back in time to stop Hitler's parents meeting at the Austrian " +
    "Enchantment 'Under The Sea' dance. It's called 'Back to the Fuhrer'!",
    "My Mum was always saying that thing parents say growing up 'Wait until your dad gets home'. 'Wait until " +
    "your dad gets home, we'll have a chat introduce you and see if he'll start paying maintenance'",
    "'Son, I don't think you're cut out to be a mime.'\n" +
    "'Was it something I said?' asks the son.\n" +
    "'Yes.'",
    "I heard a rumour that Cadbury is bringing out an oriental chocolate bar. Could be a Chinese Wispa.",
    "I needed a password eight characters long so I picked Snow White and the Seven Dwarves.",
    "Crash Investigations is my favourite TV show, I've seen every episode. Here's a tip for the new viewers:" +
    " if the show starts with the pilots being interviewed… it will be a boring episode.",
    "I think the bravest thing I've ever done is misjudge how much shopping I want to buy and still not go back" +
    " to get a basket.",
    "Drug use gets an unfair reputation considering all the beautiful things in life it has given us like rock" +
    " 'n' roll and sporting achievement.",
    "I'm not a very muscular man; the strongest thing about me is my password.",
    "I don't have the Protestant work ethic, I have the Catholic work ethic; in that I don't work but I do feel" +
    " very guilty about that.",
    "I love Snapchat. I could talk about classic card games all day.",
    "People who use selfie sticks really need to have a good, long look at themselves.",
    "You just know Chilcot was up until 4am, downing Red Bulls and trying to crank out the last 800,000 words.",
    "Yo Mamma's so fat… that other people have to pay for the health consequences of this via general taxation," +
    " even though it's her responsibility.",
    "Jokes about white sugar are rare. Jokes about brown sugar, Demerara.",
    "A rescue cat is like recycled toilet paper. Good for the planet, but scratchy.",
    "I bumped into my French teacher the other day who asked me what I'm up to now. I told her I go to the cinema" +
    " and play football with my brother.",
    "My cat is recovering from a massive stroke.",
    "My sister had a baby and they took a while to name her and I was like, 'Hurry up!' because I didn't want my " +
    "niece to grow up to be one of these kids you hear about on the news where it says, 'The 17 year old defendant," +
    " who hasn't been named'.",
    "I've always considered myself more of a lover than a fighter. Which has confused a lot of guys that have tried" +
    " to start fights with me. They'll raise their fists, I'll whip my knob out.",
    "I went to Waterstones and asked the woman for a book about turtles, she said 'hardback?' and I was like," +
    " 'yeah and little heads",
    "I learned about method acting at drama school, when all my classmates stayed in character as posh, patronising" +
    " twats for the entire three years I was there.",
    "My ex-girlfriend would always ask me to text her when I got in. That's how small my penis is.",
    "I'm a comedian with irritable bowel syndrome… It's shits and giggles.",
    "Maybe Hitler wouldn't have been so grumpy if people hadn't left him hanging for high fives all the time.",
    "Hey, if anyone knows how to fix some broken hinges, my door's always open.",
    "If you don't know what Morris dancing is, imagine eight guys from the KKK got lost, ended up at gay pride" +
    " and just tried to style it out.",
    "Hedgehogs – why can't they just share the hedge?",
    "I think the worst thing about driving a time machine is your kids are always in the back moaning 'Are we" +
    " then yet?'",
    "If you don't know what introspection is, you need to take a long, hard look at yourself.",
    "Insomnia is awful. But on the plus side – only three more sleeps till Christmas.",
    "Centaurs shop at Topman. And Bottomhorse.",
    "Oregon leads America in both marital infidelity and clinical depression. What a sad state of affairs.",
    "I'm very conflicted by eye tests. I want to get the answers right but I really want to win the glasses.",
    "Relationships are like mobile phones. You'll look at your iPhone 5 and think, it used to be a lot quicker" +
    " to turn this thing on."
]


@client.event
async def on_ready():
    global monitoring_channels, lfg_channels, scheduler
    print(" success!")
    scheduler.enter(1, 1, test)
    scheduler.run()
    for item in monitoring_channels:
        channel = discord.utils.get(client.get_all_channels(), name=item)
        if hasattr(channel, 'type') and channel.type.name == 'text':
            lfg_channels.append(channel)


def test():
    print('{} is running.'.format(client.user.name))
    print('')


@client.event
async def on_message(message):
    global lfg_channels

    await check_commands(message)


async def check_commands(message):
    command_params = message.content.lower().strip().split(' ')
    command_called = command_params[0]
    command_params.pop(0)

    if command_called[:1] == '!':

        if command_called[1:] == 'activity' or \
                command_called[1:] == 'fireteam' or \
                command_called[1:] == 'ft':
            await activity_command(message, command_params)

        if command_called[1:] == 'raid':
            await activity_command(message, command_params, "Raid")

        if command_called[1:] == 'strike' or \
                command_called[1:] == 'strikes':
            await activity_command(message, command_params, "Strike")

        if command_called[1:] == 'milestones':
            await activity_command(message, command_params, "Milestones")

        elif command_called[1:] == 'clear':
            await clear_command_with_message(message, command_params)

        elif command_called[1:] == 'sexual':
            await sexual(message)

        elif command_called[1:] == 'complete':
            await complete_fireteam_command(message)

        elif command_called[1:] == 'cancel':
            await cancel_fireteam_command(message)

        elif command_called[1:] == 'joke' or \
                command_called[1:] == 'jokes':
            await joke(message)

        elif command_called[1:] == 'help':
            await help_command(message)


commands = [
    {
        'name': 'fireteam',
        'description': 'Creates a fireteam for others to join.',
        'aliases': '!ft, !activity'
    },
    {
        'name': 'raid',
        'description': 'Creates a raid specific group.',
        'aliases': '!raids'
    },
    {
        'name': 'strike',
        'description': 'Creates a strike specific group.',
        'aliases': '!strikes'
    },
    {
        'name': 'milestones',
        'description': 'Creates a milestones specific group.'
    },
    {
        'name': 'complete',
        'description': 'Completes a fireteam if no longer needed.',
        'aliases': '!cancel'
    },
    {
        'name': 'joke',
        'description': 'Tells a joke.',
        'aliases': '!jokes'
    },
    {
        'name': 'help',
        'description': 'Shows this message.',
    }
]


async def help_command(message):
    channel = message.channel
    await delete_if_can(message)
    message_content = "```\n"
    message_content += "Hi there,\n"
    message_content += "My name is {} and I'm here to help!\n\n".format(client.user.name)
    message_content += "Here's what I can do:\n\n"
    for command in commands:
        message_content += '!{}: {}\n'.format(command['name'], command['description'])
        if 'aliases' in command.keys():
            message_content += '    *Aliases: {}\n\n'.format(command['aliases'])
        else:
            message_content += '\n'
    message_content += "\nPlease note: This bot is being tested on this server, so if you encounter any errors," + \
                       " please inform MrCouchy."
    message_content += '```'

    await client.send_message(channel, message_content)


async def sexual(message):
    global sexual_jokes

    if message.channel.type == discord.ChannelType.text:
        await delete_if_can(message)
        user = await client.start_private_message(message.author)

        await client.send_message(user, "```" + random.choice(sexual_jokes) + "```")


async def joke(message):
    global sexual_jokes

    if message.channel.type == discord.ChannelType.text:
        await delete_if_can(message)
        await client.send_message(message.channel, "```" + random.choice(jokes) + "```")


async def clear_command_with_channel(channel):
    messages = []  # Empty list to put all the messages in the log
    async for message in client.logs_from(channel):
        if message.id not in raid_messages.keys():
            messages.append(message)

    messages = messages[1:]

    if len(messages) == 1:
        await delete_if_can(messages[0])
    elif len(messages) > 0:
        if channel_is_public(channel):
            await client.delete_messages(messages)


async def clear_command_with_message(message, command_params):
    if message.author.permissions_in(message.channel).administrator:
        await clear_command_with_channel(message.channel)

        await delete_if_can(message)
    else:
        await client.start_private_message(message.author)
        message_content = 'Sorry, you do not have administration rights to this channel,\n'
        message_content += 'so you cannot clear the messages.'
        await client.send_message(message.author, message_content)


def get_activity_info_template(user):
    global active_activity

    raid_info = user.mention + " is {}, who's interested?\n\n"
    raid_info += "For: {}\n\n"
    raid_info += "Time: {}\n\n"
    raid_info += "Players Needed: {}\n\n"
    raid_info += "So far, here's who's keen:\n"
    raid_info += "{}"
    raid_info += "{}"

    item_list = active_activity[user.id]

    if item_list['Type'] == 'Raid':
        type_replace = 'putting together a raid'
    elif item_list['Type'] == 'Strike':
        type_replace = 'wanting to do some strikes'
    elif item_list['Type'] == 'Milestones':
        type_replace = 'in need of some milestones'
    else:
        type_replace = "organising a fireteam"

    players_list = ''
    players_needed_val = int(item_list['Players_Needed'])
    player_objects = item_list['Player_List']

    fireteam_members = []
    fill_members = []

    if active_activity[user.id]["Time"] == -100:
        time_string = "TBA"
    elif active_activity[user.id]["Time"] == 0:
        time_string = "Now"
    else:
        hours = int(active_activity[user.id]["Time"])
        minutes = (active_activity[user.id]["Time"] * 60) % 60

        time_string = "about "
        if hours:
            time_string += str(hours) + " hour"
            if hours > 1:
                time_string += "s"
            if minutes:
                time_string += " and "
        if minutes:
            time_string += str(int(minutes)) + " minute"
            if minutes > 1:
                time_string += "s"

    if len(player_objects) != 0:
        if len(player_objects) == 1:
            fireteam_members = [player_objects[0]]
        else:
            result = filter_players(player_objects, players_needed_val)
            fireteam_members = result[0]
            fill_members = result[1]
    results = format_players(user, fireteam_members, fill_members)
    fireteam_members_string = results[0]
    fill_members_string = results[1]

    if item_list['Players_Needed'] == -1:
        needed_players = "TBA"
    else:
        needed_players = int(players_needed_val) - len(player_objects)
        if needed_players < 0:
            needed_players = 0

    return raid_info.format(type_replace, item_list['For'], time_string, needed_players,
                            fireteam_members_string, fill_members_string)


def filter_players(players, required_count):
    if len(players) > required_count >= 0:
        fireteam_members = []
        fill_members = []
        for index in range(0, required_count):
            fireteam_members.append(players[index])
        for index in range(required_count, len(players)):
            fill_members.append(players[index])

        return [fireteam_members, fill_members]
    else:
        return [players, []]


def format_players(user, fireteam_members, fill_members):
    fireteam_string = ''
    fill_string = ''

    if len(fireteam_members) == 0:
        fireteam_string = 'No one. ' + user.mention + ' is a loner.'
    elif len(fireteam_members) == 1:
        fireteam_string = user.mention + ' and ' + fireteam_members[0].mention
    else:
        fireteam_string += user.mention
        for member in fireteam_members:
            if member.id != fireteam_members[len(fireteam_members) - 1].id:
                fireteam_string += ', '
            else:
                fireteam_string += ' and '
            fireteam_string += member.mention

    if len(fill_members):
        fill_string += "\n\nHere's who's happy to fill:\n"
        index = 1
        for member in fill_members:
            fill_string += str(index) + ". "
            fill_string += member.mention + "\n"
            index += 1

    return [fireteam_string, fill_string]


def is_lfg_channel(sent_channel):
    global lfg_channels
    found = False

    for channel_item in lfg_channels:
        if sent_channel == channel_item:
            found = True
    return found


async def activity_command(message, command_params, type_override=None):
    global active_activity

    user = message.author

    if is_lfg_channel(message.channel):
        await delete_if_can(message)
        await send_intro_message(message.author)
        if user.id not in active_activity.keys():
            active_activity[user.id] = {
                "Owner": user,
                "Channel": message.channel,
                "Message": None,
                "Type": type_override,
                "For": "TBA",
                "Time": -100,
                "Time_Message": None,
                "Players_Needed": -1,
                "Player_List": [],
                "Temp_Time": 0
            }

            await send_main_message(user, message.channel)
            await send_related_message(user)
        else:
            message_content = "You already have an active fireteam.\n\n"
            message_content += "Do you want to delete it?"
            delete_message = await client.send_message(user, message_content)
            await client.add_reaction(delete_message, '👍')
            await client.add_reaction(delete_message, '👎')

            reaction_monitor_message[delete_message.id] = {
                "reference": "delete_activity",
                "owner": user,
                "message": delete_message,
                "options": ['👍', '👎'],
                "answers": {'👍': "Consider it done!", '👎': "Okay, keeping it."}
            }
    else:
        await delete_if_can(message)
        await client.start_private_message(user)
        reply = "You can only use this command in designated 'looking-for-group' channels.\n"
        if not message.channel.is_private:
            reply += "The channel '" + message.channel.name + "' has not been set as one of these channels."
        else:
            reply += "This one is not a public channel."
        await client.send_message(user, reply)


async def delete_if_can(message):
    if channel_is_public(message.channel) or client.user.id == message.author.id:
        await client.delete_message(message)


def channel_is_public(channel):
    if channel.type != discord.ChannelType.private:
        return True
    return False


async def send_intro_message(user):
    await client.start_private_message(user)

    intro_message = "------------------------------------------------\n\n"
    intro_message += "Follow the prompts to fill out your activity\n\n"
    intro_message += "------------------------------------------------"

    await client.send_message(user, intro_message)


async def send_main_message(user, channel):
    global active_activity, raid_messages

    main_message_info = get_activity_info_template(user)

    active_activity[user.id]['Message'] = await client.send_message(channel, main_message_info)

    raid_messages[active_activity[user.id]['Message'].id] = {
        "user": user,
        "message": active_activity[user.id]['Message']
    }
    await client.pin_message(active_activity[user.id]['Message'])
    await client.add_reaction(active_activity[user.id]['Message'], '👍')
    await client.add_reaction(active_activity[user.id]['Message'], '👎')


async def send_related_message(user):
    global active_activity

    activity_object = active_activity[user.id]

    if activity_object['Type'] is None:
        await send_activity_message(user)
    else:
        if activity_object['For'] == "TBA":
            await send_for_message(user)
        else:
            if activity_object['Time'] == -100:
                await send_time_message(user)
            else:
                if activity_object['Players_Needed'] == -1:
                    await send_players_needed_message(user)
                else:
                    await client.send_message(user, "Event is all setup!")
                    print(user.name + " has setup an event.")


async def add_options(user, message, types_list, sub_name):
    global active_activity, options, reaction_monitor_message

    items = {}

    option_count = len(types_list)

    for count in range(0, option_count):
        items[options[count]] = types_list[count]

    reaction_monitor_message[message.id] = {
        "reference": sub_name,
        "owner": user,
        "message": message,
        "options": options[:option_count],
        "answers": items
    }

    for count in range(0, option_count):
        try:
            await client.add_reaction(message, options[count])
        except discord.NotFound as error:
            error = "NOT FOUND (status code: 404): Unknown Message"


@client.event
async def on_reaction_remove(reaction, member):
    global active_activity

    if not member.bot:
        if reaction.message.id in raid_messages.keys():
            if reaction.emoji == '👍':
                raid_message = raid_messages[reaction.message.id]
                raid_owner = raid_message["user"]
                if member in active_activity[raid_owner.id]['Player_List']:
                    active_activity[raid_owner.id]['Player_List'].remove(member)
                    await update_main_message(raid_owner)


@client.event
async def on_reaction_add(reaction, member):
    global active_activity

    if not member.bot:
        if reaction.message.id in reaction_monitor_message.keys():
            message_info = reaction_monitor_message[reaction.message.id]
            user = message_info['owner']

            if reaction.emoji in message_info['options']:
                if message_info['reference'] == "delete_activity":
                    if reaction.emoji == '👍':
                        await clear_fireteam(user)
                        await delete_if_can(message_info['message'])
                        await client.send_message(member, "Consider it done!")
                    elif reaction.emoji == '👎':
                        await delete_if_can(message_info['message'])
                        await client.send_message(member, "Okay, keeping it!")
                elif message_info['reference'] == "Time":
                    await set_temp_time(message_info, reaction, user)
                else:
                    active_activity[user.id][message_info['reference']] = message_info['answers'][reaction.emoji]
                    await delete_if_can(message_info['message'])

                if user.id in active_activity.keys():
                    await update_main_message(member)
                    await send_related_message(user)
            else:
                print("Invalid emoji.")
        elif reaction.message.id in raid_messages.keys():
            if reaction.emoji == '👍':
                raid_message = raid_messages[reaction.message.id]
                raid_owner = raid_message["user"]
                if member.id != raid_owner.id:
                    if member not in active_activity[raid_owner.id]['Player_List']:
                        active_activity[raid_owner.id]['Player_List'].append(member)
                        await update_main_message(raid_owner)


async def set_temp_time(message_info, reaction, user):
    if reaction.emoji in message_info['answers']:
        if message_info['answers'][reaction.emoji] == "+30 Minutes":
            active_activity[user.id]["Temp_Time"] += 0.5
        elif message_info['answers'][reaction.emoji] == "+1 Hour":
            active_activity[user.id]["Temp_Time"] += 1
        elif message_info['answers'][reaction.emoji] == "+2 Hours":
            active_activity[user.id]["Temp_Time"] += 2
        elif message_info['answers'][reaction.emoji] == "+4 Hours":
            active_activity[user.id]["Temp_Time"] += 4
        elif message_info['answers'][reaction.emoji] == "Reset":
            active_activity[user.id]["Temp_Time"] = 0
        elif message_info['answers'][reaction.emoji] == "Confirm":
            await event_countdown(user, active_activity[user.id]["Temp_Time"])
            active_activity[user.id]["Time"] = active_activity[user.id]["Temp_Time"]
            await delete_if_can(reaction.message)
    else:
        print("Invalid Emoji " + reaction.emoji)


async def event_countdown(user, hours):
    count = Counter(user, asyncio.get_event_loop())
    count.start()
    print("Counter started for {}'s fireteam.".format(user.name))
    print("Total time of {} hours\n".format(hours))


async def complete_fireteam_command(message):
    message_content = "You're fireteam has been completed."
    await user_request_clear_fireteam(message, message_content)


async def cancel_fireteam_command(message):
    message_content = "You're fireteam has been removed."
    await user_request_clear_fireteam(message, message_content)


async def user_request_clear_fireteam(message, message_content):
    user = message.author
    await delete_if_can(message)
    result = await clear_fireteam(user)
    if result:
        await client.send_message(user, message_content)
    else:
        message_content = "You don't have an active fireteam."
        await client.send_message(user, message_content)


async def clear_fireteam(user):
    global raid_messages, active_activity

    if user.id in active_activity.keys():
        print("Deleting {}'s Fireteam".format(user.name))
        await delete_if_can(active_activity[user.id]['Message'])
        del raid_messages[active_activity[user.id]['Message'].id]
        del active_activity[user.id]


async def update_main_message(user):
    global active_activity

    content = get_activity_info_template(user)

    await client.edit_message(active_activity[user.id]['Message'], content)


async def send_optional_message(user, message_content, types, type_name, modify_message=None):
    if modify_message:
        message = modify_message
        await client.edit_message(modify_message, message_content)
    else:
        message = await client.send_message(user, message_content)
    await add_options(user, message, types, type_name)
    return message


async def send_activity_message(user):
    global activity_types

    message_content = await get_for_activity_message()
    await send_optional_message(user, message_content, activity_types, 'Type')


async def send_players_needed_message(user):
    global players_needed

    message_content = await get_players_needed_message()
    await send_optional_message(user, message_content, players_needed, 'Players_Needed')


async def get_for_activity_message():
    global activity_types

    raid_info = "What type of activity?\n\n"
    raid_info += get_list_items(activity_types)

    return raid_info


async def get_players_needed_message():
    global players_needed

    raid_info = "How many people do you need?\n\n"
    raid_info += get_list_items(players_needed)

    return raid_info


async def get_for_raid_message():
    global raid_types

    raid_info = "Which raid would you like to do?\n\n"
    raid_info += get_list_items(raid_types)

    return raid_info


async def get_for_strike_message():
    global strike_types

    raid_info = "Which strike would you like to do?\n\n"
    raid_info += get_list_items(strike_types)

    return raid_info


async def get_for_milestones_message():
    global milestone_types

    raid_info = "Which milestone do you plan to do?\n\n"
    raid_info += get_list_items(milestone_types)

    return raid_info


async def get_for_other_message():
    global other_types

    raid_info = "What do you plan to do?\n\n"
    raid_info += get_list_items(other_types)

    return raid_info


def get_list_items(type_list):
    global options

    text = ''
    for index in range(0, len(type_list)):
        text += "{} {}\n\n".format(options[index], type_list[index])

    return text


async def send_for_message(user):
    global active_activity
    global raid_types
    global strike_types
    global milestone_types
    global other_types

    activity_type = active_activity[user.id]['Type']
    if activity_type == 'Raid':
        type_list = raid_types
        message_content = await get_for_raid_message()
    elif activity_type == 'Strike':
        type_list = strike_types
        message_content = await get_for_strike_message()
    elif activity_type == 'Milestones':
        type_list = milestone_types
        message_content = await get_for_milestones_message()
    elif activity_type == 'Other':
        type_list = other_types
        message_content = await get_for_other_message()
    else:
        active_activity[user.id]['Type'] = None
        await send_related_message(user)
        return

    await send_optional_message(user, message_content, type_list, 'For')


async def send_time_message(user):
    global time_options

    message_content = get_for_time_message(user)
    if active_activity[user.id]['Time_Message']:
        await send_optional_message(user, message_content, time_options, 'Time',
                                    active_activity[user.id]['Time_Message'])
    else:
        active_activity[user.id]['Time_Message'] = \
            await send_optional_message(user, message_content, time_options, 'Time')


def get_for_time_message(user):
    global time_options, active_activity

    raid_info = "How soon do you want to start?\n\n"
    raid_info += get_list_items(time_options)

    raid_info += "Currently set to: {} hours from now".format(active_activity[user.id]['Temp_Time'])
    return raid_info


class Counter(Thread):
    def __init__(self, user, loop):
        global active_activity

        Thread.__init__(self)
        self.user = user
        self.loop = loop
        self._stop = Event()

    def run(self):
        global active_activity
        while not self._stop.is_set():
            sleep(1800)
            if self.user.id in active_activity.keys():
                active_activity[self.user.id]['Time'] -= 0.5
                if active_activity[self.user.id]['Time'] < 0:
                    self._stop.set()
                else:
                    self.loop.create_task(update_main_message(self.user))
            else:
                self._stop.set()


client.run('NDYxODA1MDE2NTU0OTMwMTkx.DhYo9Q.k58KKLIrUZGkuwxodg7v-CLOGLs')
