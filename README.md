# Telegram Members Extractor

A Python script to extract members from Telegram channels and send direct messages using a hybrid approach: user account for extraction, bot for messaging.

## Features

- Extract all members from Telegram channels you admin
- Export member data to CSV files
- Send direct messages using Telegram Bot (safer, faster, better rate limits)
- Hybrid architecture: Telethon for extraction, Bot API for messaging
- Rate limiting protection (20 messages/second)
- Progress tracking and detailed error reporting
- Test mode for sending messages without re-extraction

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up configuration
cp config.template.py config.py
# Edit config.py with your credentials

# 3. Extract members
python extract_members_send_dm.py

# 4. Extract and send messages
python extract_members_send_dm.py --send-messages

# 5. Test messaging with existing CSV
python extract_members_send_dm.py --test-messages "channel.csv"
```

## Prerequisites

- Python 3.7 or higher
- A Telegram account
- A Telegram Bot (from @BotFather)
- Admin access to the channels you want to extract members from

## Installation

### Step 1: Install Python

If you don't have Python installed, follow these instructions:

#### macOS

**Option 1: Using Homebrew (Recommended)**
1. Install Homebrew if you don't have it:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Install Python:
   ```bash
   brew install python3
   ```

3. Verify installation:
   ```bash
   python3 --version
   ```

**Option 2: Using Official Installer**
1. Go to [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Download the latest Python 3.x installer for macOS
3. Run the installer and follow the prompts
4. Open Terminal and verify:
   ```bash
   python3 --version
   ```

#### Windows

1. Go to [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Download the latest Python 3.x installer for Windows
3. Run the installer
4. **IMPORTANT:** Check the box "Add Python to PATH" during installation
5. Click "Install Now"
6. Open Command Prompt and verify:
   ```bash
   python --version
   ```

#### Linux (Ubuntu/Debian)

Python is usually pre-installed. To check or install:

1. Check current version:
   ```bash
   python3 --version
   ```

2. If not installed or outdated:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   ```

3. Verify installation:
   ```bash
   python3 --version
   pip3 --version
   ```

#### Linux (Fedora/CentOS/RHEL)

```bash
sudo dnf install python3 python3-pip
```

Or for older versions:
```bash
sudo yum install python3 python3-pip
```

### Step 2: Clone or Download the Project

If you haven't already, get the project files on your computer.

### Step 3: Set Up Python Virtual Environment (Recommended)

It's recommended to use a virtual environment to avoid conflicts with other Python projects.

**On macOS/Linux:**
```bash
cd /path/to/tg-extract
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
cd C:\path\to\tg-extract
python -m venv venv
venv\Scripts\activate
```

### Step 4: Install Dependencies

With your virtual environment activated, install the required packages:

```bash
pip install -r requirements.txt
```

This will install:
- `telethon` - The Telegram API library (for extracting members)
- `python-telegram-bot` - The Bot API library (for sending messages)

### Step 5: Get Your Telegram API Credentials

**For User Account (required for extracting members):**

1. Go to [https://my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Click on "API development tools"
4. Fill in the application details (you can use any name)
5. You'll receive:
   - `api_id` (a number)
   - `api_hash` (a string of letters and numbers)

**For Bot (required for sending messages):**

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the prompts:
   - Choose a name for your bot (e.g., "My Extract Bot")
   - Choose a username (must end in 'bot', e.g., "myextract_bot")
4. You'll receive a bot token that looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
5. **IMPORTANT:** Save this token securely - you'll need it for config.py

**Why do we need both?**
- User account credentials are needed to extract member lists (bots cannot do this)
- Bot token is used for sending messages (safer, better rate limits, more reliable)

### Step 6: Configure the Script

1. Copy the configuration template:
   ```bash
   cp config.template.py config.py
   ```

2. Edit `config.py` with your credentials:
   ```python
   # User account (for extracting members)
   api_id = 'YOUR_API_ID'           # Replace with your api_id
   api_hash = 'YOUR_API_HASH'       # Replace with your api_hash
   phone = 'YOUR_PHONE_NUMBER'      # Your phone with country code, e.g., '14388306837'
   channel = '$N'                   # Leave as is or change to your channel

   # Bot token (for sending messages)
   bot_token = 'YOUR_BOT_TOKEN'     # Replace with your bot token from BotFather
   ```

   **Example:**
   ```python
   api_id = '12345678'
   api_hash = 'abc123def456ghi789jkl012mno345pq'
   phone = '14388306837'
   channel = '$N'
   bot_token = '123456789:ABCdefGHIjklMNOpqrsTUVwxyz'
   ```

3. Save the file

**IMPORTANT:** Never share your `config.py` file or commit it to Git! It contains sensitive credentials.

## Usage

### Basic Usage: Extract Members Only

To extract members from all channels without sending messages:

```bash
python extract_members_send_dm.py
```

**What happens:**
1. The script connects to Telegram (you'll need to enter a verification code on first run)
2. Lists all available groups/channels
3. Extracts members from each channel
4. Saves member data to CSV files (one per channel)

### Advanced Usage: Extract Members and Send Messages

**Option 1: Using Bot (Safer, but users must start bot first)**

```bash
python extract_members_send_dm.py --send-messages
```

- ✓ Safe for your account
- ✓ Fast (20 messages/second)
- ✗ Users must start your bot first

**Option 2: Using Your User Account (Can reach anyone, but stricter limits)** ⚠️

```bash
python extract_members_send_dm.py --send-messages --use-user-account
```

- ✓ Can message users without them starting a bot
- ✓ Works for users in mutual groups/channels
- ⚠️ MUCH stricter rate limits
- ⚠️ Risk of account restriction if abused
- ⚠️ Conservative: 3-5 seconds between messages
- ⚠️ Recommended: 20-30 messages per batch

**What happens:**
1. Extracts members from a channel (same as basic usage)
2. Asks: "Do you want to send messages to members from this channel?"
   - Type `yes` to proceed with messaging
   - Type `no` to skip and continue to the next channel
3. If you choose yes:
   - You'll be prompted to write your message (press Enter twice when done)
   - The message will be displayed for review
   - Safety warnings will be shown (if using user account)
   - You can choose batch size (if using user account)
   - You'll be asked to type "CONFIRM" before sending
   - Messages will be sent with appropriate delays
   - Progress will be shown for each message sent
4. Repeats for each channel

### Test Mode: Send Messages to an Existing CSV

If you've already extracted members and want to test sending messages without re-extracting:

**With Bot:**
```bash
python extract_members_send_dm.py --test-messages your_file.csv
```

**With User Account:**
```bash
python extract_members_send_dm.py --test-messages your_file.csv --use-user-account
```

**What happens:**
1. The script loads the specified CSV file from the current directory
2. Asks: "Do you want to send messages to members from this CSV?"
   - Type `yes` to proceed with messaging
   - Type `no` to cancel
3. If you choose yes:
   - You'll be prompted to write your message (press Enter twice when done)
   - The message will be displayed for review
   - You'll be asked to confirm before sending
   - Messages will be sent to each member with a 2-second delay between sends
   - Progress will be shown for each message sent
4. Script completes

**Example:**
```bash
# Test with a previously extracted CSV file
python extract_members_send_dm.py --test-messages "test.csv"
```

**Use cases:**
- Test messaging functionality without extracting members again
- Send messages to a specific channel's members from a previous extraction
- Re-send messages if the first attempt had errors
- Test different messages on the same member list

## First-Time Authentication

The first time you run the script, Telegram will ask you to authenticate:

1. You'll receive a code via Telegram on another device
2. Enter the code when prompted
3. If you have 2FA enabled, enter your password
4. The script creates a session file (e.g., `14388306837.session`) so you don't need to authenticate again

## Output

### CSV Files

The script creates CSV files named after each channel, containing:
- `username` - The user's Telegram username
- `user id` - Unique user ID
- `access hash` - User's access hash
- `name` - Full name (first + last)
- `group` - Channel name
- `group id` - Channel ID

**Example:** `My Channel.csv`

### Message Sending Output

When sending messages, you'll see real-time progress:
```
[1/150] Sending to john_doe... ✓
[2/150] Sending to jane_smith... ✓
[3/150] Sending to bob_wilson... ✗ Error: User privacy settings prevent messaging

--- Message Sending Complete ---
Successfully sent: 148
Failed: 2
Total: 150
```

## Important Notes

### How the Script Works

This script uses a **hybrid approach** for optimal results:

1. **Member Extraction**: Uses your Telegram user account (Telethon)
   - Only user accounts can extract member lists from channels
   - You need admin privileges in the channels

2. **Message Sending**: Uses a Telegram Bot (python-telegram-bot)
   - More reliable and safer than user accounts
   - Better rate limits (30 messages/second for bots vs stricter limits for users)
   - Less risk of account restrictions

### Bot Messaging Limitation ⚠️

**IMPORTANT:** Telegram bots can only send messages to users who have:
1. Started a conversation with the bot first (by sending `/start` or any message)
2. Previously interacted with the bot

**What this means:**
- Users who haven't started your bot will receive an error: "User hasn't started bot"
- This is a Telegram API limitation, not a script issue
- To maximize delivery, you can:
  - Share your bot link with channel members first
  - Ask members to start the bot before sending messages
  - Use an incentive (e.g., "Start the bot for updates")

### Rate Limiting

#### Bot Mode
- **Rate limit**: 30 messages per second
- **Script uses**: 20 messages/second for safety
- **Delay**: 50ms between messages
- **Safety**: Very safe, unlikely to get restricted

#### User Account Mode ⚠️
- **Rate limit**: Variable, Telegram doesn't publish exact limits
- **Script uses**: 3-5 seconds between messages (conservative)
- **Daily limit**: ~40-50 messages safely, ~200 max (risky)
- **Recommended batch**: 20-30 messages per session
- **Rest period**: 10-15 minutes between batches
- **Safety**: Higher risk, can lead to restrictions

### How to Avoid Getting Banned (User Account Mode)

#### 🛡️ CRITICAL SAFETY RULES:

1. **Start Small**: Send 5-10 messages first, wait 30 minutes, check if your account is okay
2. **Use Batches**: Never send more than 20-30 messages in one session
3. **Take Breaks**: Wait 10-15 minutes between batches (script reminds you)
4. **Daily Limit**: Don't exceed 40-50 messages per day when starting
5. **Vary Timing**: Don't send at exactly same time every day
6. **Natural Behavior**: Make delays variable (script does this automatically: 3-5 seconds)

#### ⚠️ WARNING SIGNS:

If you see these, STOP immediately:
- "FloodWaitError" - You're rate limited, wait the specified time
- Messages take longer to send
- You get logged out randomly
- Any error mentioning "flood" or "limit"

#### 🚨 If You Get Restricted:
- **Temporary ban**: Usually 1-24 hours, sometimes longer
- **What to do**: Stop sending messages, wait it out
- **Prevention**: Follow the safety rules above
- **Appeal**: Only for serious cases via Telegram support

#### ✅ SAFER Alternative Workflow:

**Week 1:** Send 5 messages/day
**Week 2:** Send 10 messages/day
**Week 3:** Send 20 messages/day
**Week 4+:** Send 30-40 messages/day (split into 2 batches)

This "warming up" approach is much safer for your account.

### Privacy & Restrictions

Messages will fail for users who:
- Haven't started a conversation with your bot (bot mode only)
- Have blocked your bot/account
- Have deleted their account
- Have privacy settings preventing messages
- Don't share a group/channel with you (user account mode)

These failures are tracked separately in the output statistics.

### Best Practices

#### For Bot Mode:
1. **Share Bot First**: Post bot link in channel, encourage members to start it
2. **Offer Value**: Give reason to start bot (updates, exclusive content, etc.)
3. **Test First**: Run with `--test-messages` on small CSV first
4. **Bot Commands**: Set up `/start` command handler for better UX

#### For User Account Mode:
1. **ALWAYS Start Small**: 5-10 messages first time
2. **Use Batch Mode**: Enter batch size when prompted (20-30 max)
3. **Track Sending**: Keep log of when you sent messages
4. **Quality Over Quantity**: Better to reach 50 people safely than get banned reaching 200
5. **Message Relevance**: Only message users relevant to your content
6. **Respect Privacy**: If users ask to stop, remove them from CSV
7. **Monitor Account Health**: Check if you can still message normally after each batch

#### Universal:
8. **Message Content**: Keep professional, relevant, and valuable
9. **Spam Warning**: Unsolicited messages violate Telegram ToS
10. **Backup**: Keep CSV backups before campaigns
11. **Monitor Output**: Watch console for errors/warnings
12. **Legal Compliance**: Follow GDPR, CCPA, and local laws

### Legal & Ethical Considerations

- Only extract members from channels you have permission to access
- Comply with privacy laws (GDPR, CCPA, etc.) when handling user data
- Respect Telegram's Terms of Service
- Don't spam or harass users
- Consider implementing opt-out mechanisms

## Troubleshooting

### "Error: config.py file not found!"

**Solution:** You need to create the config.py file:
```bash
cp config.template.py config.py
```
Then edit it with your credentials.

### "FloodWaitError: A wait of X seconds is required"

**Solution:** You're sending too many requests too quickly. Wait the specified time and try again. Consider increasing the delay in the code.

### "SessionPasswordNeededError"

**Solution:** You have 2FA enabled. Enter your password when prompted.

### "ChatAdminRequiredError"

**Solution:** You need admin privileges in the channel to extract members.

### ImportError: No module named 'telethon'

**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### "TypeError: 'NoneType' object is not subscriptable"

**Solution:** Make sure you're an admin of the channel and have the necessary permissions.

### "Error: CSV file 'your_file.csv' not found!"

**Solution:** When using `--test-messages`, make sure:
1. The CSV file exists in the current directory
2. The filename is spelled correctly (case-sensitive)
3. You include the file extension (.csv)

Example:
```bash
# If your file is "My Channel.csv" in the current directory
python extract_members_send_dm.py --test-messages "My Channel.csv"
```

### "Forbidden: bot can't initiate conversation with a user"

**Solution:** This is expected behavior for Telegram bots. Users must start a conversation with your bot first before it can message them.

**How to fix:**
1. Share your bot link in the channel: `https://t.me/your_bot_username`
2. Post a message asking members to start the bot
3. Offer an incentive (e.g., "Start the bot to receive updates")
4. Wait for users to interact with your bot
5. Then run the message sending script

### "Invalid bot token" or bot_token errors

**Solution:**
1. Make sure you've added `bot_token` to your `config.py`
2. Get a new token from @BotFather if needed: `/newbot`
3. Ensure the token is in quotes and has no extra spaces
4. Format: `bot_token = '123456789:ABCdefGHIjklMNOpqrsTUVwxyz'`

### Most messages fail with "User hasn't started bot"

**Solution:** This is the bot limitation. To improve delivery rate:
1. Send a message to the channel with your bot link
2. Ask members to start the bot (e.g., "Click here to get updates: @your_bot")
3. Consider using a user account for sending (less safe, but no restriction)
4. Wait a few days for users to start the bot, then retry

## Switching Between Accounts

If you have multiple Telegram accounts configured in `config.py`:

1. Comment out the current credentials
2. Uncomment the credentials you want to use
3. Save the file

**Example:**
```python
# Simon's credentials (currently active)
api_id = '22570850'
api_hash = 'b20552868db6fc61c4225657e14cae30'
phone = '14388306837'

# Caro's credentials (commented out)
# api_id = '18835687'
# api_hash = 'e0a112cfc82e9d045a149ec3228a1bd8'
# phone = '14508069552'
```

## Deactivating Virtual Environment

When you're done, deactivate the virtual environment:

```bash
deactivate
```

## File Structure

```
tg-extract/
├── extract_members_send_dm.py       # Main script
├── get_my_id.py            # Helper script to get your user ID
├── config.py                # Your credentials (DO NOT COMMIT)
├── config.template.py       # Template for configuration
├── requirements.txt         # Python dependencies
├── .gitignore              # Prevents committing sensitive files
├── README.md               # This file
├── csv_exports/            # Extracted CSV files (auto-generated)
│   ├── Channel1.csv
│   └── Channel2.csv
└── *.session               # Telegram session files (auto-generated)
```

## Support

If you encounter issues:

1. Check the Troubleshooting section above
2. Ensure all prerequisites are met
3. Verify your API credentials are correct
4. Check that you have admin access to the channels

## License

This tool is for educational purposes. Use responsibly and ethically.

## Bot vs User Account: Quick Comparison

| Feature | Bot Mode | User Account Mode |
|---------|----------|-------------------|
| **Reach** | Only users who started bot | All users in mutual channels |
| **Speed** | 20 msg/sec (very fast) | 1 msg per 3-5 sec (slow) |
| **Daily Limit** | Thousands | 40-50 safely, 200 max |
| **Setup** | Need bot from @BotFather | Use existing account |
| **Ban Risk** | Very low | Medium-High if abused |
| **Best For** | Opt-in audiences | Targeted outreach |
| **Telegram Approval** | Official feature | Grey area |

**Recommendation:**
- **Start with Bot** for legitimate opt-in audiences
- **Use User Account** only if you can't get users to start bot AND you're willing to go slowly (5-10 messages first time)

## Changelog

### v2.1 (Current) - User Account Option
- **NEW:** Added `--use-user-account` flag to send via user account
- Can now reach users without them starting bot first
- Built-in safety measures: 3-5 second delays, batch mode, flood detection
- Comprehensive safety guidelines in README
- Warning prompts before sending with user account
- Automatic batch size limitation (prompts user)
- "CONFIRM" requirement before sending
- Detailed comparison: Bot vs User Account modes

### v2.0 - Hybrid Bot Architecture
- **BREAKING CHANGE:** Now uses Telegram Bot for sending messages (safer, better rate limits)
- Added bot token configuration requirement
- Hybrid approach: Telethon for extraction, Bot API for messaging
- Improved rate limiting: 20 messages/second (vs previous 0.5/second)
- Better error categorization: separates "user hasn't started bot" from other errors
- Added detailed statistics for failed deliveries
- Updated documentation with bot setup instructions
- Added troubleshooting for bot-specific issues

### v1.2
- Added `--test-messages` flag to test messaging with existing CSV files
- Improved workflow: test messages without re-extracting members
- Added troubleshooting section for test mode

### v1.1
- Added `--send-messages` flag for optional DM functionality
- Added configuration file support
- Improved error handling and user feedback
- Added rate limiting protection

### v1.0
- Initial release
- Basic member extraction to CSV
