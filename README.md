# Personal Bot

A powerful Telegram bot designed to automate social media content creation and professional outreach. This project combines social media management with AI-driven content generation, securely handling tasks like posting to Instagram and sending professional emails.

## ✨ Features

* **Secure User Access:** A password and an approved users list restrict bot functionality to authorized users only.
* **AI-Powered Content Generation:**
    * **Instagram Reels:** Generates Hinglish captions, viral hashtags, and official guidelines for social media posts using a Large Language Model (LLM).
    * **Professional Emails:** Crafts tailored job application emails by referencing a pre-loaded CV and a company's description.
* **Automated Instagram Posting:**
    * Downloads Instagram Reels in the highest available quality using `yt-dlp`.
    * Allows users to preview the generated caption and choose to either **Post** or **Cancel**.
    * Automatically deletes downloaded reel files after a successful post or cancellation to save disk space and maintain security.
* **Secure & Logged Operations:**
    * All posting activities, including successes, failures, and cancellations, are securely logged to an encrypted file (`post_log.encrypted`).
    * Uses a strong **symmetric encryption** (`Fernet`) to protect sensitive log data from unauthorized access.
* **Secure Email Sending:** Requires a separate key phrase for access to the email generation and sending functionality.
* **Continuous Operation:** Designed to run 24/7 on a server, listening for commands and executing tasks asynchronously.

## 🛠️ Technology Stack

* **Programming Language:** Python
* **Bot Framework:** `python-telegram-bot`
* **AI Integration:** `LangChain` with `ChatOpenAI`
* **Social Media:** `instagrapi`
* **Video Processing:** `yt-dlp` & `FFmpeg`
* **Scheduling:** `apscheduler`
* **Security:** `cryptography`
* **Environment Management:** `python-dotenv`

## 🚀 Setup and Installation

### Prerequisites

* Python 3.12+
* FFmpeg installed on your system (e.g., `brew install ffmpeg` on macOS).
* A Telegram Bot Token (from `@BotFather`).
* An Instagram account with 2-Step Verification enabled.
* A Google account with a generated App Password for sending emails.

### Steps

1.  **Clone the Repository:**
    ```bash
    git clone <your-repo-url>
    cd Mem0nic
    ```

2.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure `.env` File:**
    Create a file named `.env` in the root directory and add your credentials. **Replace the placeholder values with your actual keys.**

    ```
    TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
    ADMIN_USER_ID="YOUR_TELEGRAM_USER_ID"
    PASSWORD="YOUR_POSTER_PASSWORD"
    EMAIL_KEY_PHRASE="YOUR_EMAIL_KEY_PHRASE"
    ENCRYPTION_KEY="YOUR_ENCRYPTION_KEY"
    IG_USERNAME="YOUR_INSTAGRAM_USERNAME"
    IG_PASSWORD="YOUR_INSTAGRAM_PASSWORD"
    IG_2FA_SECRET="YOUR_INSTAGRAM_2FA_SECRET"
    SENDER_EMAIL="YOUR_GMAIL_ADDRESS"
    SENDER_PASSWORD="YOUR_GOOGLE_APP_PASSWORD"
    OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
    OPENAI_API_BASE="YOUR_OPENAI_API_BASE"
    ```

    > **Note:** Generate your `ENCRYPTION_KEY` by running `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`.

5.  **Run the Bot:**
    ```bash
    python controller.py
    ```

## 🤖 Usage

### Getting Started
* Send `hey poster` to the bot to check your approval status and start the conversation.

### Posting an Instagram Reel
* First, send `hey poster` and select "Post a Reel".
* Send your request in the format: `URL | theme`
    * Example: `https://www.instagram.com/reel/C720kK3yP9I/ | funny cricket meme`
* The bot will process the request and show a preview of the generated caption.
* Click **Post Now** to upload the reel or **Cancel** to delete the files.

### Sending an Email
* First, send `hey poster` and select "Send a Mail".
* Enter your secret key phrase.
* Send your request in the format: `Company Email | Company Description | Designation`
    * Example: `hr@google.com | Google is a leading tech company known for innovation | Software Engineer`
* The bot will generate an email and ask for your final approval before sending.

## ⚠️ Security

This project implements robust security measures to protect your data:
* **File Deletion:** All downloaded media files are immediately and permanently deleted after being processed.
* **Encrypted Logs:** All activity logs are encrypted on disk using a unique key stored in your environment variables.
* **Role-Based Access:** All core functionality is restricted to approved users.
* **Secure Credentials:** Credentials are never hardcoded and are loaded from secure environment variables at runtime.

## ☁️ Deployment

This bot is designed for continuous deployment. A `requirements.txt` file and a `Procfile` are included in the repository, making it compatible with cloud services like **Railway** for seamless, 24/7 operation.