from threading import Thread, Event
from time import sleep
import discord
import sched
import time
import asyncio
import os
import random

from discord.ext import commands
from jokes import jokes, sexual_jokes
from opus_loader import load_opus_lib
from boto.s3.connection import S3Connection


description = 'I like trains.'
prefix = '!'

# token = open('token.txt', 'r').read()
token = os.environ['DISCORD_TOKEN']

print("")
print('Launching bot...', end="", flush=True)

client = commands.Bot(description=description, command_prefix=prefix)
scheduler = sched.scheduler(time.time, time.sleep)
load_opus_lib()

lfg_channels = ['lfg', 'raid', 'looking-for-group', 'testing', '🍕-dense-pizza-🍕']
syrion_channels = ["That's a wipe", "⭐ Lamingtions ⭐"]

options = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫"]

active_activity = {}
reaction_monitor_message = {}

activity_types = ['Raid', 'Strike', 'Milestones', 'Other']
raid_types = ['Leviathan', 'Prestige Leviathan', 'Eater of Worlds', 'Prestige EoW', 'Spire of Stars', 'Prestige SoS']
strike_types = ['Vanguard', 'Nightfall', 'Heroic']
milestone_types = ['Any', 'Flashpoint', 'Clan XP', 'Crucible', 'Other']
other_types = ['Anything', 'Escalation Protocol', 'Storyline', 'A Cry']
players_needed = ['1', '2', '3', '4', '5']

raid_messages = {}
time_options = ["+30 Minutes", "+1 Hour", "+2 Hours", "+4 Hours", "Reset", "Confirm"]

default_volume = 0.03

players = {}
queues = {}
volumes = {}
voice_clients = {}

@client.event
async def on_ready():
    global lfg_channels, scheduler

    print(" success!")
    scheduler.enter(1, 1, test)
    scheduler.run()


def test():
    print('{} is running.'.format(client.user.name))
    print('')


@client.event
async def on_voice_state_update(before, after):
    if not after.bot:
        if before.voice_channel != after.voice_channel:
            if after.voice_channel is not None and after.voice_channel.type == discord.ChannelType.voice:
                if after.voice_channel.name in syrion_channels:
                    sleep(1)
                    await join_syrion_message(after)


@client.event
async def on_message(message):
    global lfg_channels

    await check_commands(message)


async def check_commands(message):
    command_params = message.content.strip().split(' ')
    command_called = command_params[0].lower()
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

        elif "music" in message.channel.name.lower() or "beat" in message.channel.name.lower():
            if command_called[1:] == 'youtube' or \
                    command_called[1:] == 'play' or \
                    command_called[1:] == 'yt':
                await youtube(message, command_params)

            elif command_called[1:] == 'syrion':
                await syrion(message)

            elif command_called[1:] == 'queue':
                await show_queue(message)

            elif command_called[1:] == 'volume':
                await volume(message, command_params)

            elif command_called[1:] == 'next' or \
                    command_called[1:] == 'skip':
                next_song(message.channel.server.id)


commands = {
    'Destiny': [
        {
            'name': 'fireteam',
            'description': 'Creates a fireteam for others to join.',
            'aliases': ['ft', 'activity']
        },
        {
            'name': 'raid',
            'description': 'Creates a raid specific group.',
            'aliases': ['raids']
        },
        {
            'name': 'strike',
            'description': 'Creates a strike specific group.',
            'aliases': ['strikes']
        },
        {
            'name': 'milestones',
            'description': 'Creates a milestones specific group.'
        },
        {
            'name': 'complete',
            'description': 'Completes a fireteam if no longer needed.',
            'aliases': '!cancel'
        }
    ],
    'Music': [
        {
            'name': 'play',
            'description': 'Play a song from youtube.',
            'aliases': ['youtube', 'yt']
        },
        {
            'name': 'next',
            'description': 'Skips to the next song in the queue.',
            'aliases': ['skip']
        },
        {
            'name': 'queue',
            'description': 'Shows queued music.'
        },
        {
            'name': 'volume',
            'description': 'Adjust/shows volume of music bot.'
        },
        {
            'name': 'syrion',
            'description': 'Gets Syrion\'s thoughts.'
        }
    ],
    'Others': [
        {
            'name': 'joke',
            'description': 'Tells a joke.',
            'aliases': ['jokes']
        },
        {
            'name': 'sexual',
            'description': 'This does nothing, you filthy minded person.'
        },
        {
            'name': 'help',
            'description': 'Shows this message.'
        }
    ]
}


async def help_command(message):
    channel = message.channel
    await delete_if_can(message)
    message_content = "```\n"
    message_content += "Hi there,\n"
    message_content += "My name is {} and I'm a magical unicorn!\n".format(client.user.name)
    message_content += "Here's what I can do:\n\n"
    for group in commands.keys():
        message_content += group + ':\n'
        for command in commands[group]:
            message_content += '    !{}: {}\n'.format(command['name'], command['description'])
            if 'aliases' in command.keys():
                aliasString = ''
                for aliasName in command['aliases']:
                    if aliasString
                        aliasString += ', '
                    aliasString += '!{}'.format(aliasName)
                message_content += '        *Aliases: {}\n'.format(aliasString)
        message_content += '\n'
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
    # if message.author.permissions_in(message.channel).administrator:
    await clear_command_with_channel(message.channel)

    await delete_if_can(message)
    # else:
    #     await client.start_private_message(message.author)
    #     message_content = 'Sorry, you do not have administration rights to this channel,\n'
    #     message_content += 'so you cannot clear the messages.'
    #     await client.send_message(message.author, message_content)


def get_activity_info_template(user):
    global active_activity

    raid_info = user.mention + " is {}. 👍 if you're interested. @here\n\n"
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

    players_needed_val = int(item_list['Players_Needed'])
    player_objects = item_list['Player_List']

    fireteam_members = []
    fill_members = []

    if active_activity[user.id]["Time"] == -100:
        time_string = "TBA"
    elif active_activity[user.id]["Time"] == 0:
        time_string = "Now"
    elif active_activity[user.id]["Time"] < 0:
        time_string = "Might've already started"
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
        if sent_channel.name == channel_item:
            found = True

    found = True # Override to allow any channel
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
                    await clear_command_with_channel(active_activity[user.id]["Channel"])


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
    await clear_command_with_channel(message.channel)


async def clear_fireteam(user):
    global raid_messages, active_activity

    if user.id in active_activity.keys():
        print("Deleting {}'s Fireteam".format(user.name))
        await delete_if_can(active_activity[user.id]['Message'])
        del raid_messages[active_activity[user.id]['Message'].id]
        del active_activity[user.id]
        return True
    return False


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
                if active_activity[self.user.id]['Time'] == 0:
                    self._stop.set()
                else:
                    self.loop.create_task(update_main_message(self.user))
            else:
                self._stop.set()


def check_queue(server_id):
    if len(queues[server_id]):
        player = queues[server_id].pop(0)
        players[server_id] = player
        set_player_volume(player, server_id)
        player.start()
    # else:
    # disconnect(server_id)


async def volume(message, params):
    bot_volume = None
    if len(params):
        bot_volume = params[0]
    if not bot_volume or not bot_volume.isdigit():
        if message.channel.server in volumes:
            volume_value = volumes[message.channel.server] * 100
        else:
            volume_value = default_volume * 100

        text_message = "Volume is currently set to {}%.".format(int(volume_value))
    elif int(bot_volume) > 100 or int(bot_volume) < 0:
        text_message = "Volume can be set between 0-100%."
    else:
        bot_volume = int(bot_volume)
        volumes[message.channel.server] = bot_volume / 100

        if message.channel.server.id in players.keys():
            players[message.channel.server.id].volume = bot_volume / 100
            print("Setting player to " + str(bot_volume / 100))

        text_message = "Volume set to " + str(bot_volume) + "%."

    await client.send_message(message.channel, text_message)


async def show_queue(message):
    text_message = ''
    index = 0
    server_id = message.author.voice_channel.server.id
    print(server_id)
    print(queues)
    print(queues.keys())
    if server_id in queues.keys() or server_id in players.keys():
        if server_id in players.keys():
            index_prefix = 'Currently Playing: '
            duration = get_duration(players[server_id])
            text_message += "**" + index_prefix + "**" + players[server_id].title + " " + duration + "\n\n"
        if len(queues[server_id]):
            for queue_item in queues[server_id]:
                duration = get_duration(queue_item)

                index += 1
                index_prefix = str(index) + ": "
                text_message += "**" + index_prefix + "**" + queue_item.title + " " + duration + "\n\n"
                print(text_message)
        if text_message != '':
            await client.send_message(message.channel, "🎶 Music Queue 🎶\n\n" + text_message)

    print("No items queued")
    return


def get_duration(queue_item):
    hours = queue_item.duration // 3600
    minutes = "{:02}".format((queue_item.duration // 60) - (hours * 60))
    seconds = "{:02}".format(queue_item.duration - (hours * 3600) - (int(minutes) * 60))

    duration = "** ["
    if hours > 0:
        duration += str(hours) + ":"
    duration += str(minutes) + ":" + str(seconds)
    duration += "]**"
    return duration


async def play_syrion_audio(channel):
    items = os.listdir('Syrion')
    random_number = random.randint(0, len(items) - 1)
    line_name = items[random_number]

    await pause_to_play(channel, "Syrion/" + line_name)


async def syrion(message):
    await play_syrion_audio(message.author.voice_channel)


async def youtube(message, params):
    await add_to_queue(message.author.voice_channel, params[0])


async def join_syrion_message(user):
    await play_syrion_audio(user.voice_channel)


async def pause_to_play(voice_channel, url):
    pause_player(voice_channel.server.id)

    await set_voice_client(voice_channel)

    voice_clients[voice_channel.server.id] \
        .create_ffmpeg_player(url, after=lambda: resume_player(voice_channel.server.id)) \
        .start()


def resume_player(server_id):
    if server_id in players.keys():
        players[server_id].resume()


def pause_player(server_id):
    if server_id in players.keys():
        players[server_id].pause()


async def set_voice_client(voice_channel):
    if voice_channel.server.id in voice_clients and voice_clients[voice_channel.server.id] is not None:
        if voice_clients[voice_channel.server.id].channel != voice_channel:
            voice_clients[voice_channel.server.id].move_to(voice_channel)
    else:
        voice_clients[voice_channel.server.id] = await client.join_voice_channel(voice_channel)


async def add_to_queue(voice_channel, url):
    global voice_clients
    server_id = voice_channel.server.id

    await set_voice_client(voice_channel)

    player = await voice_clients[voice_channel.server.id]\
        .create_ytdl_player(url,
                            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                            after=lambda: check_queue(server_id))

    if server_id not in queues:
        queues[server_id] = []

    set_player_volume(player, server_id)

    if server_id not in players:
        players[server_id] = player
        player.start()
    else:
        queues[server_id].append(player)
        if not players[server_id].is_playing():
            check_queue(server_id)


def set_player_volume(player, server_id):
    if server_id in volumes:
        player.volume = volumes[server_id]
    else:
        player.volume = default_volume


def next_song(server_id):
    if server_id in players:
        players[server_id].stop()


# TODO setup disconnect monitor
# async def disconnect(server_id):
#     await voice_clients[server_id].disconnect()


client.run(token)
