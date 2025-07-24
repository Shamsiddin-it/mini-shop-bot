## Telegram mini shop Bot

This is a Telegram bot mini shop. Functionalities will be soon⏳.

### Getting Started

To run this bot on your machine:

1. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `config.py` file** in the root directory and add the following:

   ```python
   BOT_TOKEN = 'your_bot_token_here'
   DATABASE_URL = 'sqlite+aiosqlite:///db.sqlite3' in this project i am using sqlite you can use any other.
   ```

That's it! Now you can run the bot.
