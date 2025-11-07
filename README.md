# 🎙️ Audio-to-Text Project with Basic Teaching Mode

A Flask-based application that converts speech to text using the **Vosk** speech recognition engine. The project also includes a **basic Teaching Mode**, which provides simple responses or translations based on recognized audio commands.

---

## 🚀 Features

* 🎧 **Speech-to-Text Conversion** using Vosk
* 🔁 **Continuous Listening** (keeps listening until stopped)
* 💾 **User Data Storage**

  * Audio files stored locally
  * Transcribed text stored in SQLite database
* 🧩 **Basic Teaching Mode**

  * Responds to simple teaching-related commands
  * Example: Translate English to Hindi or explain simple terms
* 🌐 **Flask-based Web UI** for easy use and testing

---

## ⚙️ Setup Instructions

1. **Clone this repository**

   ```bash
   git clone https://github.com/brajesh2020/audio-to-text-project2-working-copy-with-database-and-webview-of-output.git
   cd audio-to-text-project2-working-copy-with-database-and-webview-of-output
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Download a Vosk Model**

   * Visit [Vosk Models](https://alphacephei.com/vosk/models)
   * Download a small model (e.g., `vosk-model-small-en-us-0.15`)
   * Extract it inside a folder named `model/` in the project directory

5. **Run the app**

   ```bash
   python app.py
   ```

   Then open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

---

## 🧠 Basic Teaching Mode

Currently, the teaching mode works in a **simple and experimental** way:

* Detects keywords like “hello”, “data”, or “math”
* Provides short text-based responses or translations
* Ideal as a **proof of concept** for future interactive learning features

Example:

> You say: “What is math?”
> App replies: “Mathematics is the study of numbers, shapes, and patterns (+,-,*,/)”

---

## 🧰 Tech Stack

* **Python**
* **Flask**
* **Vosk** (for offline speech recognition)
* **SQLite** (local database)

