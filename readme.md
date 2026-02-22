# 🎮 Steam Price Tracker Telegram Bot

A powerful Telegram bot that tracks Steam game prices in Indian Rupees (₹) and automatically notifies users when a price drops.

This project is lightweight, fast, and easy to deploy while still providing professional-level features like inline buttons, automatic link detection, and background price monitoring.

---

## 🚀 Features

### ✅ Core Features

• Track Steam game prices using store URLs  
• Automatic hourly price monitoring  
• Instant Telegram notifications on price drops  
• Displays prices in INR (₹)  
• Persistent tracking using a database  
• Supports multiple users independently  

---

### 🎯 Smart UX Features

• Auto-detects Steam links (no command needed)  
• Inline buttons:
  - View game on Steam
  - Stop tracking instantly  
• Clean formatted messages with emojis  
• Per-user numbering for tracked games  
• Command suggestions via Telegram menu  

---

## 🤖 Bot Commands

/track <url> → Start tracking a Steam game  
/list → Show all tracked games  
/remove <number> → Stop tracking a game  
/ping → Check if bot is online  

---

## 🧠 How It Works

1. User sends a Steam store URL.  
2. Bot extracts the AppID from the link.  
3. Bot fetches current price from Steam’s public store API.  
4. Game is saved in the database.  
5. Background scheduler checks prices hourly.  
6. If price drops → user gets notified automatically.  

---

## 🛠 Tech Stack

Python 3  
python-telegram-bot (async)  
SQLAlchemy ORM  
SQLite database  
APScheduler (background jobs)  
Steam Store API endpoint  

---

## 📦 Project Structure

steam-price-bot/

│── bot.py            → Main Telegram bot logic  
│── scheduler.py      → Background price checker  
│── steam_api.py      → Steam API helper functions  
│── models.py         → Database models  
│── database.py       → DB configuration  
│── config.py         → Environment settings  
│── requirements.txt  
└── Procfile  

---

## ⚙️ Installation (Local Setup)

### 1️⃣ Clone the repository
```
git clone https://github.com/yourusername/steam-price-bot.git  
cd game_bot  
```
---

### 2️⃣ Create virtual environment
```
python -m venv venv  
source venv/bin/activate  
```
---

### 3️⃣ Install dependencies
```
pip install -r requirements.txt  
```
---

### 4️⃣ Create `.env` file

Create a file named `.env` in the root folder:

BOT_TOKEN=your_telegram_bot_token_here  

---

### 5️⃣ Run the bot
```
python bot.py  
```
---

## 📸 Example Usage

User sends:

/track https://store.steampowered.com/app/1245620/

Bot replies:

🎮 ELDEN RING  
💰 Price: ₹3599  
📉 You'll be notified on drops.  

When price drops:

🔥 PRICE DROP!  
🎮 ELDEN RING  
Old Price: ₹3599  
New Price: ₹2399  

---

## 🤝 Contributing

Pull requests are welcome. Feel free to open issues for bugs or feature requests.

---

## 📜 License

This project is licensed under the GNU GPL v3 License.

---

## ⭐ Support

If you like this project, consider giving it a star on GitHub!