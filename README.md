# Telegram Google Account Creator Bot

A powerful Telegram bot to automate Google Workspace user account creation, leveraging the Google Admin Directory API. Designed for admins to streamline onboarding and user management with a conversational interface.

## Features
- Create Google Workspace users directly from Telegram
- Duplicate username prevention with instant feedback
- Typing indicators for a smooth user experience
- Optional fields: recovery email, phone, org unit
- Secure credential management
- Extensible for advanced Google Workspace automation

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/TelegramGoogleAccountCreatorBot.git
cd TelegramGoogleAccountCreatorBot/pre-beta
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file with the following:
```
BOT_TOKEN=your_telegram_bot_token
ADMIN_CHAT_ID=your_telegram_user_id
```

### 4. Google Workspace API Setup
- Enable the Admin SDK API in your Google Cloud project
- Download your `token.json` and place it in the project directory
- Ensure your service account has domain-wide delegation

### 5. Run the Bot
```bash
python bot.py
```

## File Structure
```
pre-beta/
├── bot.py                  # Main Telegram bot logic
├── create_workspace_user.py # Google Workspace user management
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── token.json              # Google API credentials
├── domain.txt              # Domain configuration
```

## Security
- Never commit your `.env` or `token.json` to public repositories.
- Use strong passwords and restrict bot access to admins only.

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License
MIT