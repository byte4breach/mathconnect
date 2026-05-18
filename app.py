import requests
import random
import math
import os
import psycopg2
import psycopg2.extras
from datetime import datetime

# ── Telegram config ──────────────────────────────────────────────
BOT_TOKEN = "8831329165:AAHqhpGNLrzYBus-6seT1wxg49LcAQyvAKU"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ── Website link ─────────────────────────────────────────────────
WEBSITE_URL = "https://mathconnect-w5og.onrender.com"

# ── PostgreSQL config ─────────────────────────────────────────────
DATABASE_URL = "postgresql://mathconnect_user:5xYSIVsJmht5lZ5rLOGKaRPk6Lboi8F3@dpg-d85bh3brjlhs73drgmg0-a/mathconnect"


def get_db():
    """Open a new DB connection."""
    return psycopg2.connect(DATABASE_URL)


def init_db():
    """Create the leaderboard table if it doesn't exist."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS leaderboard (
                    id        SERIAL PRIMARY KEY,
                    name      TEXT    NOT NULL,
                    score     INTEGER NOT NULL,
                    total     INTEGER NOT NULL DEFAULT 6,
                    pct       INTEGER NOT NULL,
                    submitted TIMESTAMP DEFAULT NOW()
                );
            """)
        conn.commit()
    print("✅ Database tayyor.")


def db_save_score(name: str, score: int, total: int, pct: int):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO leaderboard (name, score, total, pct) VALUES (%s, %s, %s, %s)",
                (name, score, total, pct)
            )
        conn.commit()


def db_get_leaderboard(limit: int = 10) -> list[dict]:
    with get_db() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT name, score, total, pct,
                       TO_CHAR(submitted, 'HH24:MI') AS time
                FROM leaderboard
                ORDER BY score DESC, submitted DESC
                LIMIT %s
            """, (limit,))
            return [dict(row) for row in cur.fetchall()]


# ── 8th-grade math question bank ─────────────────────────────────
def generate_questions() -> list[dict]:
    qs = []

    a, b, c = random.randint(2, 9), random.randint(1, 20), random.randint(10, 50)
    x = round((c - b) / a, 2)
    qs.append({
        "topic": "Linear Equations",
        "question": f"Solve for x:  {a}x + {b} = {c}",
        "answer": x,
        "hint": f"Subtract {b} from both sides, then divide by {a}.",
        "explanation": f"{a}x = {c} - {b} = {c-b}, so x = {c-b}/{a} = {x}"
    })

    leg_a, leg_b = random.randint(3, 12), random.randint(3, 12)
    hyp = round(math.sqrt(leg_a**2 + leg_b**2), 2)
    qs.append({
        "topic": "Pythagorean Theorem",
        "question": f"A right triangle has legs a = {leg_a} and b = {leg_b}. Find the hypotenuse c.",
        "answer": hyp,
        "hint": "Use c² = a² + b²",
        "explanation": f"c = √({leg_a}² + {leg_b}²) = √{leg_a**2 + leg_b**2} ≈ {hyp}"
    })

    x0, y0 = random.randint(2, 10), random.randint(2, 10)
    S, D = x0 + y0, x0 - y0
    qs.append({
        "topic": "Systems of Equations",
        "question": f"Solve: x + y = {S} and x − y = {D}. Find x.",
        "answer": x0,
        "hint": "Add the two equations together.",
        "explanation": f"Adding: 2x = {S+D}, so x = {x0}; then y = {S} − {x0} = {y0}"
    })

    r = random.randint(3, 12)
    area = round(math.pi * r * r, 2)
    qs.append({
        "topic": "Geometry – Circles",
        "question": f"Find the area of a circle with radius r = {r}. (Use π ≈ 3.14159, round to 2 decimals)",
        "answer": area,
        "hint": "Area = πr²",
        "explanation": f"A = π × {r}² = π × {r*r} ≈ {area}"
    })

    original = random.randint(40, 200)
    new_val  = random.randint(20, 300)
    pct = round((new_val - original) / original * 100, 2)
    qs.append({
        "topic": "Percentages",
        "question": f"A price changed from ${original} to ${new_val}. What is the percent change? (positive = increase, negative = decrease)",
        "answer": pct,
        "hint": "% change = (new − old) / old × 100",
        "explanation": f"({new_val} − {original}) / {original} × 100 = {pct}%"
    })

    x1, y1 = random.randint(-5, 5), random.randint(-5, 5)
    x2, y2 = random.randint(-5, 5), random.randint(-5, 5)
    while x1 == x2:
        x2 = random.randint(-5, 5)
    slope = round((y2 - y1) / (x2 - x1), 2)
    qs.append({
        "topic": "Linear Functions",
        "question": f"Find the slope of the line through ({x1}, {y1}) and ({x2}, {y2}).",
        "answer": slope,
        "hint": "slope = (y₂ − y₁) / (x₂ − x₁)",
        "explanation": f"m = ({y2} − {y1}) / ({x2} − {x1}) = {y2-y1}/{x2-x1} = {slope}"
    })

    base = random.randint(2, 5)
    m, n = random.randint(2, 5), random.randint(2, 5)
    qs.append({
        "topic": "Exponents",
        "question": f"Simplify: {base}^{m} × {base}^{n} = {base}^?  (enter the exponent only)",
        "answer": m + n,
        "hint": "When multiplying same base: aᵐ × aⁿ = aᵐ⁺ⁿ",
        "explanation": f"{base}^{m} × {base}^{n} = {base}^({m}+{n}) = {base}^{m+n}"
    })

    l, w, h = random.randint(2, 10), random.randint(2, 10), random.randint(2, 10)
    vol = l * w * h
    qs.append({
        "topic": "3D Geometry",
        "question": f"Find the volume of a rectangular prism with l={l}, w={w}, h={h}.",
        "answer": vol,
        "hint": "V = l × w × h",
        "explanation": f"V = {l} × {w} × {h} = {vol}"
    })

    random.shuffle(qs)
    return qs[:6]


# ── Telegram helpers ──────────────────────────────────────────────
def tg_send(chat_id, text: str, parse_mode="Markdown") -> dict:
    r = requests.post(f"{TELEGRAM_API}/sendMessage",
                      json={"chat_id": chat_id, "text": text,
                            "parse_mode": parse_mode}, timeout=10)
    return r.json()


def format_leaderboard_text() -> str:
    top = db_get_leaderboard(10)
    if not top:
        return "_Hali natijalar yo'q. Birinchi bo'ling!_"
    lines = ["🏆 *MathConnect Leaderboard*\n"]
    medals = ["🥇", "🥈", "🥉"] + ["🔢"] * 10
    for i, entry in enumerate(top):
        lines.append(f"{medals[i]} {entry['name']} — {entry['score']}/6  ({entry['pct']}%)")
    return "\n".join(lines)


# ── Telegram update handler ───────────────────────────────────────
def handle_update(update):
    msg        = update.get("message", {})
    text       = msg.get("text", "")
    chat_id    = msg.get("chat", {}).get("id")
    first_name = msg.get("from", {}).get("first_name", "friend")

    if not chat_id:
        return

    if text.startswith("/start"):
        tg_send(chat_id,
            f"👋 Salom, *{first_name}*! *MathConnect* ga xush kelibsiz — 8-sinf matematika mashqi!\n\n"
            f"🌐 Veb-ilovani shu yerda oching:\n{WEBSITE_URL}\n\n"
            f"📌 Sizning Telegram Chat ID: `{chat_id}`\n"
            "Natijalaringiz shu yerga yuborilishi uchun uni veb-ilovaga kiriting!\n\n"
            "Buyruqlar:\n/leaderboard — Eng yuqori natijalar\n/quiz — Tezkor masala\n/help — Yordam"
        )

    elif text.startswith("/leaderboard"):
        tg_send(chat_id, format_leaderboard_text())

    elif text.startswith("/quiz"):
        q = generate_questions()[0]
        tg_send(chat_id,
            f"🧮 *Tezkor Masala — {q['topic']}*\n\n"
            f"{q['question']}\n\n"
            f"💡 Maslahat: _{q['hint']}_\n\n"
            f"||Javob: {q['answer']}||"
        )

    elif text.startswith("/help"):
        tg_send(chat_id,
            "📖 *MathConnect Bot Yordami*\n\n"
            f"🌐 Veb-ilova: {WEBSITE_URL}\n\n"
            "/start — Xush kelibsiz + Chat ID\n"
            "/quiz — Tasodifiy matematika masalasi\n"
            "/leaderboard — Top 10 natijalar\n\n"
            "Veb-ilovada mashq qiling va Telegram'ingizni ulab, batafsil ball hisobotini oling!"
        )

    else:
        tg_send(chat_id,
            f"🤔 Tushunmadim. Mavjud buyruqlarni ko'rish uchun /help ni sinab ko'ring, {first_name}!"
        )


# ── Long-polling ──────────────────────────────────────────────────
def polling_loop():
    import time
    requests.post(f"{TELEGRAM_API}/deleteWebhook", timeout=10)
    print("🤖 Telegram polling boshlandi...")
    offset = None
    while True:
        try:
            params = {"timeout": 30, "allowed_updates": ["message"]}
            if offset:
                params["offset"] = offset
            r = requests.get(f"{TELEGRAM_API}/getUpdates", params=params, timeout=40)
            data = r.json()
            for update in data.get("result", []):
                offset = update["update_id"] + 1
                handle_update(update)
        except Exception as e:
            print(f"⚠ Polling xatosi: {e}")
            time.sleep(3)


if __name__ == "__main__":
    init_db()
    print("🚀 MathConnect bot ishlamoqda...")
    print(f"🌐 Veb-sayt: {WEBSITE_URL}")
    polling_loop()
