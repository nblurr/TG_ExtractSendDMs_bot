from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from telegram import Bot
from telegram.error import TelegramError
import csv
import argparse
import time
import asyncio
import warnings
import sys
warnings.filterwarnings('ignore', category=RuntimeWarning)
# Suppress asyncio warnings
import logging
logging.getLogger('asyncio').setLevel(logging.CRITICAL)


# Parse command line arguments
parser = argparse.ArgumentParser(description='Extract members from Telegram channels')
parser.add_argument('--send-messages', action='store_true',
                    help='Enable sending DMs to extracted members after extraction')
parser.add_argument('--test-messages', type=str, metavar='CSV_FILE',
                    help='Test message sending with an existing CSV file (skips extraction)')
parser.add_argument('--use-user-account', action='store_true',
                    help='Send messages using your user account instead of bot (can reach more users but has stricter limits)')
args = parser.parse_args()

# Load configuration
try:
    from config import api_id, api_hash, phone, channel, bot_token
except ImportError:
    print("Error: config.py file not found!")
    print("Please copy config.template.py to config.py and fill in your credentials.")
    print("See README.md for instructions on how to get your API credentials.")
    exit(1)

# Initialize Telethon client (for extracting members)
client = TelegramClient(phone, api_id, api_hash)

# Connect to Telegram
client.connect()

# Check authorization and sign in if needed
if not client.is_user_authorized():
    client.send_code_request(phone)
    code = input("Enter the code: ")
    try:
        client.sign_in(phone, code)
    except Exception as e:
        if 'SessionPasswordNeeded' in str(type(e).__name__):
            pw = input("2-step verification password: ")
            client.sign_in(password=pw)
        
# Initialize Bot (for sending messages)
bot = Bot(token=bot_token)


chats = []
last_date = None
chunk_size = 200
groups=[]
 
result = client(GetDialogsRequest(
             offset_date=last_date,
             offset_id=0,
             offset_peer=InputPeerEmpty(),
             limit=chunk_size,
             hash = 0
         ))
chats.extend(result.chats)


for chat in chats:
    try:
        if chat.megagroup== True:
            groups.append(chat)
    except:
        continue
print('Parsing the following groups:')
i=0
for g in groups:
    print(str(i) + '- ' + g.title)
    i+=1

def send_messages_to_members_sync(csv_filename):
    """Send DMs using Telethon (user account) - sync version"""
    print(f'\nReading members from {csv_filename}...')

    members = []
    try:
        with open(csv_filename, 'r', encoding='UTF-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                members.append(row)
    except FileNotFoundError:
        print(f'Error: Could not find file {csv_filename}')
        return

    print(f'Found {len(members)} members in the CSV.')

    if len(members) == 0:
        print('No members to message.')
        return

    # Get the message to send
    print('\nEnter the message you want to send to all members:')
    print('(Press Enter twice when done)')
    message_lines = []
    while True:
        line = input()
        if line == '' and len(message_lines) > 0 and message_lines[-1] == '':
            message_lines.pop()
            break
        message_lines.append(line)

    message = '\n'.join(message_lines).strip()

    if not message:
        print('No message entered. Skipping message sending.')
        return

    print(f'\nMessage to send:\n---\n{message}\n---')
    confirm = input('\nConfirm sending this message to all members? (yes/no): ').lower()

    if confirm != 'yes':
        print('Message sending cancelled.')
        return

    # Display warnings
    print(f'\n{"="*60}')
    print(f'⚠️  USING USER ACCOUNT MODE - IMPORTANT SAFETY NOTES:')
    print(f'{"="*60}')
    print(f'✓ Can reach users without them starting a bot')
    print(f'✓ Works for users in mutual groups/channels')
    print(f'⚠️  MUCH stricter rate limits than bots')
    print(f'⚠️  Risk of account restriction if you send too many/too fast')
    print(f'⚠️  Telegram may flag as spam if users report messages')
    print(f'')
    print(f'SAFETY MEASURES ENABLED:')
    print(f'• Conservative delay: 3-5 seconds between messages')
    print(f'• Maximum 20-30 messages per batch recommended')
    print(f'• Take breaks between batches')
    print(f'{"="*60}\n')

    batch_size = input('How many messages to send in this batch? (recommended: 20-30, press Enter for all): ').strip()
    if batch_size and batch_size.isdigit():
        members = members[:int(batch_size)]
        print(f'Will send to first {len(members)} members only.')

    final_confirm = input(f'Send to {len(members)} members? Type "CONFIRM" to proceed: ')
    if final_confirm != 'CONFIRM':
        print('Cancelled.')
        return

    print(f'\nSending messages to {len(members)} members...')
    success_count = 0
    error_count = 0
    blocked_count = 0

    for i, member in enumerate(members, 1):
        try:
            user_id = int(member['user id'])
            username = member['username']
            name = member['name']

            display_name = username if username else name
            print(f'[{i}/{len(members)}] Sending to {display_name} (ID: {user_id})...', end=' ')

            # Send using Telethon (user account)
            # Using the sync wrapper from telethon.sync ensures proper execution
            try:
                message_obj = client.send_message(user_id, message)

                # Debug: Check what we got
                import inspect
                if inspect.iscoroutine(message_obj):
                    # It returned a coroutine - this shouldn't happen with sync wrapper
                    print(f'✗ Coroutine returned (sync wrapper failed)')
                    error_count += 1
                elif message_obj and hasattr(message_obj, 'id'):
                    # Success - we got a real message object
                    print(f'✓ (msg_id: {message_obj.id})')
                    success_count += 1
                elif message_obj:
                    # Something was returned but not what we expected
                    print(f'✗ Unexpected return: {type(message_obj).__name__}')
                    error_count += 1
                else:
                    # Nothing returned
                    print('✗ No confirmation received')
                    error_count += 1
            except Exception as send_error:
                # Catch send-specific errors
                error_msg = str(send_error)
                if 'privacy' in error_msg.lower():
                    print(f'✗ Privacy settings')
                    blocked_count += 1
                elif 'flood' in error_msg.lower():
                    print(f'⚠️ FLOOD LIMIT!')
                    print(f'\nStopping to protect account. Wait 1+ hour.')
                    break
                else:
                    print(f'✗ {error_msg[:50]}')
                error_count += 1
                continue

            # Conservative delay: 3-5 seconds
            delay = 3 + (i % 3)
            time.sleep(delay)

        except Exception as e:
            # Catch any other outer exceptions
            print(f'✗ Unexpected error: {str(e)[:50]}')
            error_count += 1
            continue

    print(f'\n{"="*60}')
    print(f'--- Message Sending Complete ---')
    print(f'Successfully sent: {success_count}')
    print(f'Failed (privacy): {blocked_count}')
    print(f'Failed (other errors): {error_count - blocked_count}')
    print(f'Total attempted: {len(members)}')
    print(f'\n⚠️  RECOMMENDATION: Wait at least 10-15 minutes before')
    print(f'sending another batch to avoid rate limits.')
    print(f'{"="*60}')

async def send_messages_to_members(csv_filename, use_user_account=False):
    """Send DMs to members listed in the CSV file using Bot API"""
    print(f'\nReading members from {csv_filename}...')

    members = []
    try:
        with open(csv_filename, 'r', encoding='UTF-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                members.append(row)
    except FileNotFoundError:
        print(f'Error: Could not find file {csv_filename}')
        return

    print(f'Found {len(members)} members in the CSV.')

    if len(members) == 0:
        print('No members to message.')
        return

    # Get the message to send
    print('\nEnter the message you want to send to all members:')
    print('(Press Enter twice when done)')
    message_lines = []
    while True:
        line = input()
        if line == '' and len(message_lines) > 0 and message_lines[-1] == '':
            message_lines.pop()  # Remove the last empty line
            break
        message_lines.append(line)

    message = '\n'.join(message_lines).strip()

    if not message:
        print('No message entered. Skipping message sending.')
        return

    print(f'\nMessage to send:\n---\n{message}\n---')
    confirm = input('\nConfirm sending this message to all members? (yes/no): ').lower()

    if confirm != 'yes':
        print('Message sending cancelled.')
        return

    # Display bot mode warnings
    print(f'\n{"="*60}')
    print(f'USING BOT MODE:')
    print(f'Users must have started a conversation with your bot first.')
    print(f'Messages to users who haven\'t will fail.')
    print(f'{"="*60}\n')

    final_confirm = input(f'Send to {len(members)} members? Type "CONFIRM" to proceed: ')
    if final_confirm != 'CONFIRM':
        print('Cancelled.')
        return

    print(f'\nSending messages to {len(members)} members...')
    success_count = 0
    error_count = 0
    blocked_count = 0

    for i, member in enumerate(members, 1):
        try:
            user_id = int(member['user id'])
            username = member['username']
            name = member['name']

            display_name = username if username else name
            print(f'[{i}/{len(members)}] Sending to {display_name}...', end=' ')

            # Send using Bot API
            await bot.send_message(chat_id=user_id, text=message)
            print('✓')
            success_count += 1

            # Bot delay: 50ms (20 messages/second)
            await asyncio.sleep(0.05)

        except TelegramError as e:
            error_msg = str(e)
            if 'bot can\'t initiate conversation' in error_msg.lower() or 'forbidden' in error_msg.lower():
                print(f'✗ User hasn\'t started bot')
                blocked_count += 1
            elif 'chat not found' in error_msg.lower():
                print(f'✗ User hasn\'t started bot (chat not found)')
                blocked_count += 1
            else:
                print(f'✗ Error: {error_msg}')
            error_count += 1
            continue
        except Exception as e:
            print(f'✗ Error: {str(e)}')
            error_count += 1
            continue

    print(f'\n{"="*60}')
    print(f'--- Message Sending Complete ---')
    print(f'Successfully sent: {success_count}')
    print(f'Failed (not started bot): {blocked_count}')
    print(f'Failed (other errors): {error_count - blocked_count}')
    print(f'Total attempted: {len(members)}')
    print(f'{"="*60}')

def get(chat_num):
    #print(chat_num)
    chats = []
    last_date = None
    chunk_size = 200
    groups=[]

    result = client(GetDialogsRequest(
                 offset_date=last_date,
                 offset_id=0,
                 offset_peer=InputPeerEmpty(),
                 limit=chunk_size,
                 hash = 0
             ))
    chats.extend(result.chats)

    for chat in chats:
        try:
            if chat.megagroup== True:
                groups.append(chat)
        except:
            continue

    g_index = chat_num
    target_group=groups[int(g_index)]
    filename = target_group.title
    print('Fetching Members from {} ...'.format(filename))
    all_participants = []
    all_participants = client.get_participants(target_group, aggressive=True)

    print('Saving In file...')

    # Create csv_exports directory if it doesn't exist
    import os
    csv_dir = 'csv_exports'
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)
        print(f'Created directory: {csv_dir}/')

    #print(target_group.title)
    filename = target_group.title
    csv_filepath = os.path.join(csv_dir, "{}.csv".format(filename))
    with open(csv_filepath, "w", encoding='UTF-8') as f:

        writer = csv.writer(f,delimiter=",",lineterminator="\n")
        writer.writerow(['username','user id', 'access hash','name','group', 'group id'])
        for user in all_participants:
            if user.username:
                username= user.username
            else:
                username= ""
            if user.first_name:
                first_name= user.first_name
            else:
                first_name= ""
            if user.last_name:
                last_name= user.last_name
            else:
                last_name= ""
            name= (first_name + ' ' + last_name).strip()
            writer.writerow([username,user.id,user.access_hash,name,target_group.title, target_group.id])
    print('Members scraped successfully from {} .'.format(filename))
    print(f'Saved to: {csv_filepath}')
    return csv_filepath

# Test mode: Send messages to an existing CSV file
if args.test_messages:
    import os
    csv_file = "./csv_exports/" + args.test_messages

    # Check if file exists
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found!")
        print(f"Make sure the file exists in the current directory.")
        exit(1)

    print(f"\n{'='*50}")
    print(f"TEST MODE: Using CSV file: {csv_file}")
    print(f"{'='*50}\n")

    # Ask if user wants to send messages
    send_choice = input('Do you want to send messages to members from this CSV? (yes/no): ').lower()

    if send_choice == 'yes':
        if args.use_user_account:
            # Call sync function directly, not through asyncio.run
            send_messages_to_members_sync(csv_file)
        else:
            # Use asyncio.run for bot mode
            asyncio.run(send_messages_to_members(csv_file, use_user_account=False))
    else:
        print('Message sending cancelled.')

    print("Done")
    # Suppress cleanup warnings completely
    import os
    import atexit

    # Redirect stderr before exit
    devnull = open(os.devnull, 'w')
    sys.stderr = devnull

    # Don't try to disconnect, just exit
    os._exit(0)

# Normal mode: Extract members and optionally send messages
chat_list_index = list(range(len(chats)))

for x in chat_list_index:
    try:
        csv_filename = get(x)

        # If --send-messages flag is set, ask user if they want to send messages
        if args.send_messages and csv_filename:
            print('\n' + '='*50)
            send_choice = input('Do you want to send messages to members from this channel? (yes/no): ').lower()

            if send_choice == 'yes':
                if args.use_user_account:
                    # Call sync function directly
                    send_messages_to_members_sync(csv_filename)
                else:
                    # Use asyncio.run for bot mode
                    asyncio.run(send_messages_to_members(csv_filename, use_user_account=False))
            else:
                print('Skipping message sending for this channel.')
            print('='*50 + '\n')

    except Exception as e:
        print(f"Error processing group: {e}", end = " ")

print("Done")
# Suppress cleanup warnings completely
import os
devnull = open(os.devnull, 'w')
sys.stderr = devnull
os._exit(0)
