from botkey import key
import discord as dc
from discord.ext import commands
from discord.utils import get
import databaseMain as DBM
import time
import requests

AllowedGuilds = [1218604950280601650, 1278753127667077120]
AllowedAdmins = [1218604950280601650]

intents = dc.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True
intents.voice_states = True
intents.guild_reactions = True
intents.reactions = True

custom_role = None
role_message_id = None
emoji_role_mapping = {}


ALLOWED_GUILDS = AllowedGuilds

bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command('help')

@bot.command()
@commands.has_permissions(manage_roles=True)
async def setrole(ctx, role: dc.Role):
    global custom_role
    custom_role = role
    await ctx.send(f"Role `{role.name}` has been set for ticket management.")

def is_allowed_guild():
    async def verify(ctx):
        return ctx.guild and ctx.guild.id in ALLOWED_GUILDS
    return commands.check(verify)

def is_allowed_admin():
    async def verify(ctx):
        return ctx.guild and ctx.guild.id in AllowedAdmins
    return commands.check(verify)

@bot.command()
async def identify_guild(ctx):
    guild = ctx.guild
    await ctx.send(guild.id)

@bot.command()
async def verify(ctx, guildID):
    Allowed = DBM.CheckForAccess(guildID)


@bot.command()
@is_allowed_guild()
async def bal(ctx, name : dc.Member):
    result = DBM.CheckAccount(name.id)
    
    embed = dc.Embed(title="Your silver balance", color=dc.Color.blue())
    embed.set_author(name=name.display_name, icon_url=name.avatar.url)
    embed.add_field(name="Silver Balance", value=f"{result}", inline=True)
    embed.set_thumbnail(url=name.avatar.url)
    embed.set_footer(text="Keep grindin " + ctx.author.display_name)
    
    await ctx.send(embed=embed)


@bot.command()
@is_allowed_guild()
@commands.has_permissions(manage_roles=True)
async def baladd(ctx, name : dc.Member, balance : int):
    result = DBM.AddBalance(name.id, balance)

    embed = dc.Embed(title="Silver Balance", color=dc.Color.blue())
    embed.set_author(name=name.display_name, icon_url=name.avatar.url)
    embed.add_field(name="Balance Before", value=f"{result[1]}       ", inline=True)
    embed.add_field(name="Balance After", value=f"{result[0]} 🪙", inline=True)
    embed.set_thumbnail(url=name.avatar.url)
    embed.set_footer(text="Keep grindin " + ctx.author.display_name)
    
    await ctx.send(embed=embed)

@bot.command()
@is_allowed_guild()
@commands.has_permissions(manage_roles=True)
async def balremove(ctx, name : dc.Member, balance : int):
    result = DBM.RemoveBalance(name.id, balance)

    embed = dc.Embed(title="Silver Balance", color=dc.Color.blue())
    embed.set_author(name=name.display_name, icon_url=name.avatar.url)
    embed.add_field(name="Balance Before", value=f"{result[1]}         ", inline=True)
    embed.add_field(name="Balance After", value=f"{result[0]} 🪙", inline=True)
    embed.set_thumbnail(url=name.avatar.url)
    embed.set_footer(text="Keep grindin " + ctx.author.display_name)
    
    await ctx.send(embed=embed)


@bot.command()
@is_allowed_guild()
@commands.has_permissions(manage_roles=True)
async def createrole(ctx, role_name: str, color: dc.Color = dc.Color.default()):
    guild = ctx.guild

    # Create the role with the specified name and color
    new_role = await guild.create_role(name=role_name, color=color)
    await ctx.send(f"Role **{new_role.name}** created successfully!")


@bot.command()
@is_allowed_guild()
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, role_name: str, *members: dc.Member):
    role = dc.utils.get(ctx.guild.roles, name=role_name)
    if role is None:
        await ctx.send(f"Role **{role_name}** not found.")
        return

    # Iterate over the list of members and add the role to each
    for member in members:
        await member.add_roles(role)
        await ctx.send(f"Role **{role_name}** added to {member.mention}!")

@bot.command()
@is_allowed_guild()
@commands.has_permissions(manage_roles=True)
async def deleterole(ctx, role_name: str):
    # Find the role by name
    role = dc.utils.get(ctx.guild.roles, name=role_name)
    
    # If the role exists, delete it
    if role:
        await role.delete()
        await ctx.send(f"Role **{role_name}** has been deleted.")
    else:
        await ctx.send(f"Role **{role_name}** not found.")

@bot.command()
@is_allowed_guild()
@commands.has_permissions(manage_roles=True)
async def baladdrole(ctx, role_name: str, balance: int):
    # Find the role by name
    role = dc.utils.get(ctx.guild.roles, name=role_name)
    
    if role is None:
        await ctx.send(f"Role `{role_name}` not found.")
        return
    
    # Get all members with the specified role
    members = [member for member in ctx.guild.members if role in member.roles]
    
    if not members:
        await ctx.send(f"No members found with the role `{role_name}`.")
        return
    
    # Iterate over the members and add to their balance
    for member in members:
        result = DBM.AddBalance(member.id, balance)
        if not DBM.CheckForAccount(member.id):
            DBM.CreateAccount(member.id, balance)
    
    await ctx.send(f"Added {balance} to the balance of all members with the **{role_name}** role.")
    return

@bot.command()
@is_allowed_guild()
@commands.has_permissions(manage_roles=True)  # Restrict command to administrators
async def info(ctx, user: dc.Member = None):
    user = user or ctx.author
    
    embed = dc.Embed(title="User Information", color=dc.Color.blue())
    embed.set_author(name=user.display_name, icon_url=user.avatar.url)
    embed.add_field(name="Joined", value=user.joined_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="ID", value=user.id, inline=True)
    embed.set_thumbnail(url=user.avatar.url)
    embed.set_footer(text="User information requested by " + ctx.author.display_name)
    
    await ctx.send(embed=embed)

custom_creation_text = "React with 🎟️ to create an application ticket!"
custom_instructions_text = (
    "1. Post a screenshot of your character stats from EU and West or Asia if below requirements\n"
    "2. What roles do you play? (healer, def tank, dps, support, battlemount, etc.)\n"
    "3. Do you know anyone inside the guild?\n"
    "4. What device do you usually play on? (mobile, PC, etc.)\n"
    "5. On a scale of 1-10, what would you rate your English?\n"
    "6. Are you able to record VODs of fights?\n"
    "7. What content are you looking for?\n"
    "**Please change your Discord name to your in-game name.**"
)


@bot.command()
@is_allowed_guild()
@commands.has_permissions(manage_roles=True)
async def setcreatetext(ctx, *, text: str):
    #Sets the custom text for ticket creation.
    global custom_creation_text
    custom_creation_text = text
    await ctx.send("Updated")

@bot.command()
@is_allowed_guild()
@commands.has_permissions(manage_roles=True)
async def setinstructions(ctx, *, text: str):
    #Sets the custom instructions for tickets.
    global custom_instructions_text
    custom_instructions_text = text
    await ctx.send("Updated")
    await ctx.send(custom_instructions_text)


@bot.command()
@is_allowed_guild()
@commands.has_permissions(manage_roles=True)
async def createticket(ctx):
    # Sends a message that users can react to for creating a ticket.
    embed = dc.Embed(title="Create a ticket", color=dc.Color.blue())
    embed.add_field(name="", value=custom_creation_text)
    ticket_msg = await ctx.send(embed=embed)
    # Add the ticket emoji to the message
    await ticket_msg.add_reaction("🎟️")

@bot.event
async def openTicket(reaction, user):

    if user.bot:
        return

    if reaction.message.author == bot.user and reaction.emoji == "🎟️":
        guild = reaction.message.guild

        # Define the specific roles to add to the channel
        role1 = dc.utils.get(guild.roles, name="Owner")  # Replace with actual role name

        # Define the permissions for the new channel
        overwrites = {
            guild.default_role: dc.PermissionOverwrite(read_messages=False),  # Deny access to everyone by default
            user: dc.PermissionOverwrite(read_messages=True, send_messages=True),  # Allow access to the ticket creator
            role1: dc.PermissionOverwrite(read_messages=True, send_messages=True),  # Allow access to Role1
            guild.me: dc.PermissionOverwrite(read_messages=True, send_messages=True)  # Allow the bot to access the channel
        }

        # Create the new text channel with the specified permissions
        ticket_channel = await guild.create_text_channel(f'ticket-{user.name}', overwrites=overwrites)
        await ticket_channel.send(f'Ticket created by {user.mention}')

        print(custom_instructions_text)
        # Create an embed with instructions
        embed = dc.Embed(title="Application", color=dc.Color.light_gray())
        embed.add_field(name="Instructions:", value=custom_instructions_text)

        embed_msg = await ticket_channel.send(embed=embed)

        # Add a reaction to the embed for closing the ticket
        await embed_msg.add_reaction("🔒")

    elif reaction.message.author == bot.user and reaction.emoji == "🔒":
        if reaction.message.channel.name.startswith('ticket-'):
            await reaction.message.channel.send("Ticket will be closed in 5 seconds...")
            time.sleep(5)
            await reaction.message.channel.delete()


channel_settings = {}


@bot.command()
@is_allowed_guild()
@commands.has_permissions(administrator=True)
async def channelcreate(ctx, channel_id: int, rolenames: str, category: str):
    """Sets up the channel creation configuration."""
    guild_id = ctx.guild.id
    
    # Convert mentions to role names
    roles = []
    for role in rolenames.split(','):
        role = role.strip()
        if role.startswith("<@&") and role.endswith(">"):
            role_id = int(role[3:-1])
            role_obj = ctx.guild.get_role(role_id)
            if role_obj:
                roles.append(role_obj.name)
        else:
            roles.append(role)
    
    channel_settings[guild_id] = {
        'trigger_channel_id': channel_id,
        'role_names': roles,
        'category_name': category
    }
    
    await ctx.send(f'Channel creation settings updated: Trigger Channel ID: {channel_id}, Roles: {", ".join(roles)}, Category: {category}')


@bot.event
async def on_voice_state_update(member, before, after):
    guild = member.guild
    guild_id = guild.id

    # Retrieve the settings for the guild
    if guild_id not in channel_settings:
        return  # If no settings found, do nothing

    settings = channel_settings[guild_id]
    trigger_channel_id = settings['trigger_channel_id']
    role_names = settings['role_names']
    category_name = settings['category_name']

    # Get the category object
    category = dc.utils.get(guild.categories, name=category_name)

    # Check if the user joined the trigger channel
    if after.channel and after.channel.id == trigger_channel_id:
        # Define permissions overwrites for the new channel
        role_overwrites = {}

        for role_name in role_names:
            role = dc.utils.get(guild.roles, name=role_name)
            if role:
                role_overwrites[role] = dc.PermissionOverwrite(
                    view_channel=True,
                    connect=True,
                    speak=True
                )
            else:
                print(f"Role '{role_name}' not found in the guild.")

        # Combine overwrites with member and bot permissions
        overwrites = {
            guild.default_role: dc.PermissionOverwrite(read_messages=False, connect=False),  # Deny access to everyone by default
            member: dc.PermissionOverwrite(view_channel=True, connect=True, speak=True),  # Allow access to the channel creator
            guild.me: dc.PermissionOverwrite(view_channel=True, connect=True, speak=True)  # Allow the bot to access the channel
        }
        
        overwrites.update(role_overwrites)

        # Create a new voice channel with the specified permissions
        new_channel = await guild.create_voice_channel(
            f'{member.name}-channel',
            overwrites=overwrites,
            category=category)
        
        # Move the user to the newly created channel
        await member.move_to(new_channel)

    # Check if the user left the created channel and it's now empty
    if before.channel and len(before.channel.members) == 0:
        # Check if the channel name matches the pattern for auto-created channels
        if before.channel.name.endswith('-channel'):
            # Delete the empty channel
            await before.channel.delete()

role_message_id = None
emoji_role_mapping = {}


@bot.command()
@is_allowed_guild()
@commands.has_permissions(administrator=True)
async def reactionrole(ctx, emoji: str, role: dc.Role, message_id: int):
    global role_message_id
    emoji_role_mapping[emoji] = role.name
    role_message_id = message_id

    # Fetch the message to react to
    try:
        message = await ctx.channel.fetch_message(message_id)
        await message.add_reaction(emoji)
        await ctx.send(f"Reaction role setup complete: {emoji} -> {role.name}")
    except dc.NotFound:
        await ctx.send(f'Error: Message with ID {message_id} not found.')
    except dc.Forbidden:
        await ctx.send('Error: I do not have permission to react to that message.')
    except dc.HTTPException:
        await ctx.send('Error: Failed to react to the message.')

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    guild = reaction.message.guild

    # Handle ticket creation with 🎟️ emoji
    if reaction.message.author == bot.user and reaction.emoji == "🎟️":
        if not custom_role:
            await reaction.message.channel.send("No role has been set for ticket management. Please set a role using the `!setrole` command.")
            return

        overwrites = {
            guild.default_role: dc.PermissionOverwrite(read_messages=False),
            user: dc.PermissionOverwrite(read_messages=True, send_messages=True),
            custom_role: dc.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: dc.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        ticket_channel = await guild.create_text_channel(f'ticket-{user.name}', overwrites=overwrites)
        await ticket_channel.send(f'Ticket created by {user.mention}')

        embed = dc.Embed(title="Application", color=dc.Color.light_gray())
        embed.add_field(name="Instructions:", value=custom_instructions_text)
        embed_msg = await ticket_channel.send(embed=embed)
        await embed_msg.add_reaction("🔒")

    # Handle ticket closing with 🔒 emoji
    elif reaction.message.author == bot.user and reaction.emoji == "🔒":
        if reaction.message.channel.name.startswith('ticket-'):
            await reaction.message.channel.send("Ticket will be closed in 5 seconds...")
            time.sleep(5)
            await reaction.message.channel.delete()

    # Handle reaction role assignment
    if reaction.message.id == role_message_id:
        emoji = str(reaction.emoji)
        role_name = emoji_role_mapping.get(emoji)

        if role_name:
            role = dc.utils.get(guild.roles, name=role_name)
            if role:
                member = guild.get_member(user.id)
                if member:
                    try:
                        await member.add_roles(role)
                    except dc.Forbidden:
                        print(f"Failed to add role {role_name} to {user.name}: Missing permissions.")
                    except dc.HTTPException:
                        print(f"Failed to add role {role_name} to {user.name}: HTTP exception.")
                        
@bot.event
async def on_reaction_remove(reaction, user):
    if user.bot:
        return

    global role_message_id
    if reaction.message.id != role_message_id:
        return

    guild = reaction.message.guild
    emoji = str(reaction.emoji)

    role_name = emoji_role_mapping.get(emoji)
    if role_name:
        role = dc.utils.get(guild.roles, name=role_name)
        if role:
            member = guild.get_member(user.id)
            if member:
                try:
                    await member.remove_roles(role)
                except dc.Forbidden:
                    return
                except dc.HTTPException:
                    return

@bot.command()
@is_allowed_guild()
async def items(ctx):
    await ctx.send("Open the link, press CTRL+F and type in your item name, pick the Id and use it in the price"
             "https://github.com/ao-data/ao-bin-dumps/blob/master/formatted/items.txt")


@bot.command(name='priceE')
@is_allowed_guild()
async def priceE(ctx, item: str):
    api_url = f'https://www.albion-online-data.com/api/v2/stats/prices/{item}.json?server=eu'

    try:
        response = requests.get(api_url)
        data = response.json()

        if not data:
            await ctx.send(f'No data found for item: {item}')
            return

        # Filter out entries with both prices as 0 and group by city
        prices_by_city = {}
        for entry in data:
            city = entry.get('city')
            sell_price = entry.get('sell_price_min', 0)
            buy_price = entry.get('buy_price_max', 0)

            if sell_price == 0 and buy_price == 0:
                continue

            if city not in prices_by_city:
                prices_by_city[city] = {'sell_price': sell_price, 'buy_price': buy_price}
            else:
                # Update if new sell price is lower or buy price is higher
                if sell_price < prices_by_city[city]['sell_price']:
                    prices_by_city[city]['sell_price'] = sell_price
                if buy_price > prices_by_city[city]['buy_price']:
                    prices_by_city[city]['buy_price'] = buy_price

        if not prices_by_city:
            await ctx.send(f'No valid prices found for item: {item}')
            return

        # Create an embed to display the prices
        embed = dc.Embed(title=f"Prices for {item.capitalize()}", color=dc.Color.blue())
        for city, prices in prices_by_city.items():
            embed.add_field(name=city, value=f"**Sell Price**: {prices['sell_price']}\n**Buy Price**: {prices['buy_price']}", inline=False)

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"An error occurred: {e}")


@bot.command(name='priceW')
@is_allowed_guild()
async def priceW(ctx, item: str):
    api_url = f'https://www.albion-online-data.com/api/v2/stats/prices/{item}.json?server=west'

    try:
        response = requests.get(api_url)
        data = response.json()

        if not data:
            await ctx.send(f'No data found for item: {item}')
            return

        # Filter out entries with both prices as 0 and group by city
        prices_by_city = {}
        for entry in data:
            city = entry.get('city')
            sell_price = entry.get('sell_price_min', 0)
            buy_price = entry.get('buy_price_max', 0)

            if sell_price == 0 and buy_price == 0:
                continue

            if city not in prices_by_city:
                prices_by_city[city] = {'sell_price': sell_price, 'buy_price': buy_price}
            else:
                # Update if new sell price is lower or buy price is higher
                if sell_price < prices_by_city[city]['sell_price']:
                    prices_by_city[city]['sell_price'] = sell_price
                if buy_price > prices_by_city[city]['buy_price']:
                    prices_by_city[city]['buy_price'] = buy_price

        if not prices_by_city:
            await ctx.send(f'No valid prices found for item: {item}')
            return

        # Create an embed to display the prices
        embed = dc.Embed(title=f"Prices for {item.capitalize()}", color=dc.Color.blue())
        for city, prices in prices_by_city.items():
            embed.add_field(name=city, value=f"**Sell Price**: {prices['sell_price']}\n**Buy Price**: {prices['buy_price']}", inline=False)

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"An error occurred: {e}")


@bot.command(name='priceA')
@is_allowed_guild()
async def priceA(ctx, item: str):
    api_url = f'https://www.albion-online-data.com/api/v2/stats/prices/{item}.json?server=asia'

    try:
        response = requests.get(api_url)
        data = response.json()

        if not data:
            await ctx.send(f'No data found for item: {item}')
            return

        # Filter out entries with both prices as 0 and group by city
        prices_by_city = {}
        for entry in data:
            city = entry.get('city')
            sell_price = entry.get('sell_price_min', 0)
            buy_price = entry.get('buy_price_max', 0)

            if sell_price == 0 and buy_price == 0:
                continue

            if city not in prices_by_city:
                prices_by_city[city] = {'sell_price': sell_price, 'buy_price': buy_price}
            else:
                # Update if new sell price is lower or buy price is higher
                if sell_price < prices_by_city[city]['sell_price']:
                    prices_by_city[city]['sell_price'] = sell_price
                if buy_price > prices_by_city[city]['buy_price']:
                    prices_by_city[city]['buy_price'] = buy_price

        if not prices_by_city:
            await ctx.send(f'No valid prices found for item: {item}')
            return

        # Create an embed to display the prices
        embed = dc.Embed(title=f"Prices for {item.capitalize()}", color=dc.Color.blue())
        for city, prices in prices_by_city.items():
            embed.add_field(name=city, value=f"**Sell Price**: {prices['sell_price']}\n**Buy Price**: {prices['buy_price']}", inline=False)

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"An error occurred: {e}")


@bot.command()
@is_allowed_admin()
async def setAccess(ctx, new_value: int):
    global my_variable
    my_variable = new_value
    ALLOWED_GUILDS.append(my_variable)

@bot.command()
@is_allowed_admin()
async def remAccess(ctx, rem_value: int):
    global my_variable
    my_variable = rem_value
    ALLOWED_GUILDS.remove(my_variable)

@bot.command()
@is_allowed_admin()
async def GuildList(ctx):
    await ctx.send(ALLOWED_GUILDS)


# The custom help command
@bot.command()
async def help(ctx):
    embed = dc.Embed(
        title="Bot Commands",
        description="Here are the available commands you can use:",
        color=dc.Color.blue()
    )

    # Section 1: Get your guild id
    embed.add_field(
        name="Get your guild id:",
        value="`!identify_guild`: Gives you the ID of the guild. If you have not paid, the bot will not work.",
        inline=False
    )

    # Section 2: Manage balances
    embed.add_field(
        name="Manage balances:",
        value=(
            "`!bal @user`: Retrieves and displays the balance of the mentioned user.\n"
            "`!baladd @user amount`: Adds a specified amount to the mentioned user’s account. **MANAGE ROLES PERM**\n"
            "`!balremove @user amount`: Removes a specified amount from the mentioned user’s account. **MANAGE ROLES PERM**"
        ),
        inline=False
    )

    # Section 3: Manage roles and balances
    embed.add_field(
        name="Manage roles and balances:",
        value=(
            "`!createrole rolename color`: Creates a new role with the specified name and optional color. **MANAGE ROLES PERM**\n"
            "`!addrole rolename @user1 @user2 ...`: Assigns an existing role to one or more mentioned users. **MANAGE ROLES PERM**\n"
            "`!deleterole rolename`: Deletes the specified role from the server. **MANAGE ROLES PERM**\n"
            "`!baladdrole rolename amount`: Adds the specified balance to all members who have the specified role. **MANAGE ROLES PERM**"
        ),
        inline=False
    )

    # Section 4: Get user info
    embed.add_field(
        name="Get user info:",
        value="`!info @user`: Displays information about the mentioned user, such as when they joined the server and their ID. **ADMIN PERM**",
        inline=False
    )

    # Section 5: Albion Market
    embed.add_field(
        name="Albion Market:",
        value=(
            "`!items`: Gives you a link to the item ID sheet to find your items.\n"
            "`!priceA ITEM_ID`: Use the correct ID, it will give you all recent sell/buy prices for all markets/cities. Asia server.\n"
            "`!priceE ITEM_ID`: Use the correct ID, it will give you all recent sell/buy prices for all markets/cities. Europe server.\n"
            "`!priceW ITEM_ID`: Use the correct ID, it will give you all recent sell/buy prices for all markets/cities. West server."
        ),
        inline=False
    )

    # Section 6: Ticket Tool
    embed.add_field(
        name="Ticket Tool:",
        value=(
            "`!setinstructions TEXT TEXT TEXT`: Adds instructions to the ticket page. **MANAGE ROLES PERM**\n"
            "Example: `!setinstructions 1.Don't break any rules 2.Send screenshots of necessary things 3.Don't act like a fool`\n"
            "`!setcreatetext TEXT`: Adds the specified text to the ticket people react to. **MANAGE ROLES PERM**\n"
            "Example: `!setcreatetext React with the emoji below to open a ticket!`\n"
            "`!setrole @Staff`: Gives access to tickets to the specified role. **MANAGE ROLES PERM**\n"
            "`!createticket`: Creates an embedded message where users can react with an emoji to open a support ticket channel. **MANAGE ROLES PERM**"
        ),
        inline=False
    )

    # Section 7: Auto Voice Channel Creation
    embed.add_field(
        name="Auto Voice Channel Creation:",
        value=(
            "`!channelcreate channel_id 'role' category_name`: Configures the bot to create a voice channel when a user joins a specified trigger channel. "
            "The new channel is created in the specified category with permissions set for the mentioned roles. **ADMIN PERM**\n"
            "Example: `!channelcreate 59234139219 @Member VoiceChannels`"
        ),
        inline=False
    )

    # Section 8: Reaction Roles
    embed.add_field(
        name="Reaction Roles:",
        value=(
            "`!reactionrole emoji @role message_id`: Sets up a reaction role, where users reacting to a message with a specific emoji will be assigned a specified role. **ADMIN PERM**\n"
            "Example: `!reactionrole :red_circle: @Member 123456789123456`"
        ),
        inline=False
    )

    # Send the embedded message
    await ctx.send(embed=embed)



bot.run(key)