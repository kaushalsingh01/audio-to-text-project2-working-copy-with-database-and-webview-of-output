import os, queue, json, sqlite3, time, threading, wave
import sounddevice as sd
import vosk

MODEL_PATH = "vosk-model-small-en-us-0.15"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("Download from: https://alphacephei.com/vosk/models")

model = vosk.Model(MODEL_PATH)
recognizer = vosk.KaldiRecognizer(model, 16000)

DB_FILE = "transcriptions.db"
AUDIO_DIR = "recordings"
os.makedirs(AUDIO_DIR, exist_ok=True)
q = queue.Queue()
teaching_messages = []
listeners = {}

def init_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transcripts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            timestamp TEXT,
            text TEXT,
            audio_path TEXT
        )
    """)
    conn.commit()
    return conn

# Avoid global connection reuse across threads
def get_conn():
    return sqlite3.connect(DB_FILE)

def save_transcript(user_id, text, audio_path):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO transcripts (user_id, timestamp, text, audio_path) VALUES (?, ?, ?, ?)",
            (user_id, ts, text, audio_path)
        )
        conn.commit()

def teaching_mode(text):
    lessons = {
        "hello": "Spanish: 'Hola' | Hindi: 'Namaste'",
        "data": "Data refers to raw facts or figures — foundation of Data Science.",
        "science": "Science is systematic knowledge obtained through observation and experiments.",
        "computer": "A computer processes data according to instructions — it's the brain of the digital world.",
        "math": "Mathematics is the study of numbers, shapes, and patterns (+,-,*,/)",
        "python": "Python 🐍 is a high-level programming language great for AI, web, and automation!",
        "algorithm": "An algorithm is a step-by-step procedure to solve a problem.",
        "machine": "In AI, a 'machine' often refers to software that learns from data.",
        "learning": "Machine Learning means teaching computers to learn patterns from data."
    }
    matches = []
    for word, lesson in lessons.items():
        if word in text.lower():
            matches.append(f"{word.capitalize()} -> {lesson}")
    if matches:
        print("\nTeaching Mode Activated:")
        for m in matches:
            print("#", m)
        print()
        teaching_messages.extend(matches)
        if len(teaching_messages) > 20:
            del teaching_messages[:-20]

def get_teaching_messages():
    return list(teaching_messages)

def audio_callback(indata, frames, time_info, status):
    if status:
        print("Audio status:", status, flush=True)
    q.put(bytes(indata))

def record_audio_chunk(user_id, data):
    user_dir = os.path.join(AUDIO_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(user_dir, f"{ts}.wav")
    with wave.open(file_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(data)
    return file_path

def transcribe_loop(user_id, stop_event):
    recognizer = vosk.KaldiRecognizer(model, 16000)
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16",
                           channels=1, callback=audio_callback):
        print(f"🎤 Listening for user {user_id}... Press Stop to end")
        while not stop_event.is_set():
            try:
                data = q.get(timeout=1)
            except queue.Empty:
                continue
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "")
                if text.strip():
                    audio_path = record_audio_chunk(user_id, data)
                    print(f"✅ User {user_id}: {text}")
                    save_transcript(user_id, text, audio_path)
                    teaching_mode(text)

def start_listening(user_id):
    if user_id in listeners:
        return False
    stop_event = threading.Event()
    thread = threading.Thread(target=transcribe_loop, args=(user_id, stop_event), daemon=True)
    thread.start()
    listeners[user_id] = (thread, stop_event)
    return True

def stop_listening(user_id):
    if user_id not in listeners:
        return False
    thread, stop_event = listeners[user_id]
    stop_event.set()
    thread.join(timeout=2)
    del listeners[user_id]
    print(f"Listening stopped for user {user_id}")
    return True