from telethon.sync import TelegramClient
from config import api_id, api_hash, phone

# Initialize client
client = TelegramClient(phone, api_id, api_hash)
client.connect()

# Get your info
me = client.get_me()

print("="*50)
print("YOUR TELEGRAM INFO:")
print("="*50)
print(f"User ID: {me.id}")
print(f"Username: @{me.username if me.username else 'N/A'}")
print(f"First Name: {me.first_name}")
print(f"Last Name: {me.last_name if me.last_name else 'N/A'}")
print(f"Phone: {me.phone}")
print("="*50)

# Create a test CSV for yourself
import csv
csv_filename = "test_self.csv"
with open(csv_filename, "w", encoding='UTF-8') as f:
    writer = csv.writer(f, delimiter=",", lineterminator="\n")
    writer.writerow(['username','user id', 'access hash','name','group', 'group id'])
    writer.writerow([
        me.username if me.username else '',
        me.id,
        me.access_hash,
        f"{me.first_name} {me.last_name if me.last_name else ''}".strip(),
        'Self-Test',
        0
    ])

print(f"\nCreated {csv_filename} for self-testing!")
print(f"\nRun: python extract_members_send_dm.py --test-messages {csv_filename} --use-user-account")

client.disconnect()
