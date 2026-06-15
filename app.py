import os
import sqlite3
import datetime
from flask import Flask, render_template_string, request, redirect, url_for, jsonify

try:
    from google.cloud import translate_v3 as translate
    GOOGLE_TRANSLATE_AVAILABLE = True
except Exception:
    GOOGLE_TRANSLATE_AVAILABLE = False
    translate = None

APP_NAME = "Mamam Linker"
DB_FILE = os.environ.get("MAMAM_DB", "mamam_linker.db")
DEFAULT_LANG = "en"

SUPPORTED_LANGUAGES = {
    "en": "English",
    "ko": "한국어",
    "vi": "Tiếng Việt",
    "zh": "中文",
    "ph": "Filipino"
}

UI_TEXT = {
    "en": {
        "title": "Mamam Linker",
        "subtitle": "Multilingual parenting and jobs platform",
        "profile": "Profile",
        "roadmap": "My Roadmap",
        "spots": "Mamam Spot",
        "cast": "Mamam Cast",
        "gov": "Gov Match",
        "register": "Save Profile",
        "reset": "Reset Profile",
        "apply": "Apply",
        "start_session": "Start Session",
        "remove": "Remove",
        "add": "Add",
        "selected_lang": "Selected language",
        "child_name": "Child name",
        "nationality": "Nationality",
        "region": "Region",
        "birth_date": "Birth date",
        "language": "Language",
        "no_child": "Register a child profile to see personalized content.",
        "no_gov": "Register a child profile to see matched government support.",
        "translation": "Translation",
        "translation_demo": "Google Translate Demo",
        "default_badge": "English default / Multilingual enabled",
    },
    "ko": {
        "title": "마맘링커",
        "subtitle": "다국어 육아·일자리 플랫폼",
        "profile": "프로필",
        "roadmap": "맞춤 로드맵",
        "spots": "문화 스팟",
        "cast": "로컬 미니 발표장",
        "gov": "정부지원 매칭",
        "register": "프로필 저장",
        "reset": "프로필 초기화",
        "apply": "적용",
        "start_session": "세션 시작",
        "remove": "제거",
        "add": "추가",
        "selected_lang": "선택 언어",
        "child_name": "아이 이름",
        "nationality": "국적",
        "region": "거주지역",
        "birth_date": "출생일",
        "language": "언어",
        "no_child": "자녀 프로필을 등록하면 맞춤 콘텐츠가 표시됩니다.",
        "no_gov": "자녀 프로필을 등록하면 지원사업이 매칭됩니다.",
        "translation": "번역",
        "translation_demo": "구글 번역 데모",
        "default_badge": "기본 언어 English / 다국어 지원",
    },
    "vi": {
        "title": "Mamam Linker",
        "subtitle": "Nền tảng nuôi con và việc làm đa ngôn ngữ",
        "profile": "Hồ sơ",
        "roadmap": "Lộ trình của tôi",
        "spots": "Mamam Spot",
        "cast": "Mamam Cast",
        "gov": "Gov Match",
        "register": "Lưu hồ sơ",
        "reset": "Đặt lại hồ sơ",
        "apply": "Áp dụng",
        "start_session": "Bắt đầu phiên",
        "remove": "Xóa",
        "add": "Thêm",
        "selected_lang": "Ngôn ngữ đã chọn",
        "child_name": "Tên bé",
        "nationality": "Quốc tịch",
        "region": "Khu vực",
        "birth_date": "Ngày sinh",
        "language": "Ngôn ngữ",
        "no_child": "Đăng ký hồ sơ bé để xem nội dung cá nhân hóa.",
        "no_gov": "Đăng ký hồ sơ bé để xem gói hỗ trợ phù hợp.",
        "translation": "Bản dịch",
        "translation_demo": "Demo Google Translate",
        "default_badge": "Mặc định English / Hỗ trợ đa ngôn ngữ",
    },
    "zh": {
        "title": "Mamam Linker",
        "subtitle": "多语言育儿与就业平台",
        "profile": "资料",
        "roadmap": "我的路线图",
        "spots": "文化地点",
        "cast": "本地小讲台",
        "gov": "政府支持匹配",
        "register": "保存资料",
        "reset": "重置资料",
        "apply": "应用",
        "start_session": "开始会话",
        "remove": "删除",
        "add": "添加",
        "selected_lang": "所选语言",
        "child_name": "孩子姓名",
        "nationality": "国籍",
        "region": "地区",
        "birth_date": "出生日期",
        "language": "语言",
        "no_child": "注册孩子资料后即可查看个性化内容。",
        "no_gov": "注册孩子资料后即可查看匹配的政府支持。",
        "translation": "翻译",
        "translation_demo": "Google 翻译演示",
        "default_badge": "默认英语 / 支持多语言",
    },
    "ph": {
        "title": "Mamam Linker",
        "subtitle": "Multilingual parenting at trabaho platform",
        "profile": "Profile",
        "roadmap": "Aking Roadmap",
        "spots": "Mamam Spot",
        "cast": "Mamam Cast",
        "gov": "Gov Match",
        "register": "I-save ang profile",
        "reset": "I-reset ang profile",
        "apply": "Apply",
        "start_session": "Start Session",
        "remove": "Remove",
        "add": "Add",
        "selected_lang": "Napiling wika",
        "child_name": "Pangalan ng bata",
        "nationality": "Nasyonalidad",
        "region": "Rehiyon",
        "birth_date": "Petsa ng kapanganakan",
        "language": "Wika",
        "no_child": "Magrehistro ng profile ng bata para makita ang personalized content.",
        "no_gov": "Magrehistro ng profile ng bata para makita ang tugmang tulong ng gobyerno.",
        "translation": "Salin",
        "translation_demo": "Google Translate Demo",
        "default_badge": "English default / may multilingual support",
    }
}

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")
app.latest_translation = None
app.latest_notice = None

SCHEMA = """
CREATE TABLE IF NOT EXISTS children (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    birth_date TEXT NOT NULL,
    nationality TEXT NOT NULL,
    language TEXT NOT NULL,
    region TEXT NOT NULL,
    age_months INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS roadmap_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    month INTEGER NOT NULL,
    description TEXT NOT NULL,
    active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cultural_spots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    region TEXT NOT NULL,
    lat REAL NOT NULL,
    lng REAL NOT NULL,
    radius_m INTEGER DEFAULT 100,
    audio_script TEXT NOT NULL,
    quiz_answer TEXT NOT NULL,
    mileage INTEGER DEFAULT 10
);

CREATE TABLE IF NOT EXISTS gov_supports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    region TEXT NOT NULL,
    description TEXT NOT NULL,
    documents TEXT NOT NULL,
    max_amount INTEGER DEFAULT 0,
    eligibility TEXT NOT NULL,
    hotline TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cast_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_code TEXT NOT NULL,
    host_name TEXT NOT NULL,
    profile_lang TEXT NOT NULL,
    status TEXT NOT NULL,
    attendee_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL
);
"""

HTML = """
<!DOCTYPE html>
<html lang="{{ ui_lang }}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ title }}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root{
    --bg:#08101d;
    --panel:rgba(17,26,46,.84);
    --panel2:rgba(22,33,58,.9);
    --line:rgba(255,255,255,.08);
    --text:#edf3ff;
    --muted:#a0b2d4;
    --primary:#7c6cff;
    --primary2:#35d2ff;
    --success:#23d18b;
    --danger:#ff6b8a;
    --shadow:0 20px 60px rgba(0,0,0,.4);
}
*{box-sizing:border-box;font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
body{
    margin:0;
    background:radial-gradient(circle at top,#15213d 0,#08101d 55%,#04070d 100%);
    color:var(--text);
}
.shell{
    max-width:460px;
    min-height:100vh;
    margin:0 auto;
    background:linear-gradient(180deg,rgba(255,255,255,.03),rgba(255,255,255,.01));
    box-shadow:var(--shadow);
}
.top{
    padding:22px 18px 16px;
    background:linear-gradient(135deg,rgba(124,108,255,.24),rgba(53,210,255,.14));
    border-bottom:1px solid var(--line);
}
.badge{
    display:inline-flex;
    align-items:center;
    gap:8px;
    padding:7px 12px;
    border-radius:999px;
    background:rgba(255,255,255,.05);
    border:1px solid var(--line);
    color:var(--muted);
    font-size:12px;
}
.h1{
    margin:14px 0 6px;
    font-size:28px;
    line-height:1.1;
    font-weight:800;
    letter-spacing:-.03em;
}
.sub{
    color:var(--muted);
    font-size:13px;
    line-height:1.5;
}
.content{
    padding:16px 14px 92px;
}
.card{
    background:linear-gradient(180deg,rgba(255,255,255,.04),rgba(255,255,255,.025));
    border:1px solid var(--line);
    border-radius:22px;
    padding:16px;
    margin-bottom:14px;
    backdrop-filter:blur(12px);
}
.sec{
    display:flex;
    align-items:center;
    justify-content:space-between;
    margin:0 0 12px;
    font-size:15px;
    font-weight:700;
}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.input,.select,.btn{
    width:100%;
    border-radius:16px;
    border:1px solid var(--line);
    background:rgba(255,255,255,.05);
    color:var(--text);
    padding:13px 14px;
    font-size:14px;
    outline:none;
}
.input::placeholder{color:#8396ba}
.btn{
    background:linear-gradient(135deg,var(--primary),var(--primary2));
    border:none;
    color:#07111f;
    font-weight:800;
    cursor:pointer;
}
.btn.secondary{
    background:rgba(255,255,255,.06);
    color:var(--text);
    border:1px solid var(--line);
}
.pill{
    display:inline-flex;
    align-items:center;
    gap:6px;
    padding:7px 10px;
    border-radius:999px;
    background:rgba(255,255,255,.06);
    border:1px solid var(--line);
    color:var(--muted);
    text-decoration:none;
    font-size:12px;
}
.row{display:flex;gap:10px;align-items:center}
.avatar{
    width:48px;height:48px;border-radius:16px;
    background:linear-gradient(135deg,var(--primary),var(--primary2));
    color:#07111f;
    display:flex;align-items:center;justify-content:center;
    font-weight:800;
}
.muted{color:var(--muted);font-size:12px;line-height:1.45}
.timeline{display:flex;flex-direction:column;gap:10px}
.timeline-item{
    padding:14px;
    border-radius:18px;
    background:rgba(255,255,255,.03);
    border:1px solid var(--line);
}
.k{
    display:inline-flex;
    padding:4px 8px;
    border-radius:999px;
    font-size:11px;
    background:rgba(124,108,255,.14);
    color:#d6d0ff;
    margin-bottom:8px;
}
.k.health{background:rgba(35,209,139,.14);color:#9ef1c8}
.k.support{background:rgba(53,210,255,.12);color:#a5eeff}
.k.culture{background:rgba(255,202,92,.12);color:#ffe29b}
.title{font-size:14px;font-weight:700;margin:0 0 6px}
.desc{font-size:12px;color:var(--muted);line-height:1.5;margin:0}
.split{display:grid;grid-template-columns:1fr auto;gap:10px;align-items:center}
.nav{
    position:fixed;
    bottom:0;
    left:50%;
    transform:translateX(-50%);
    width:min(460px,100%);
    display:grid;
    grid-template-columns:repeat(4,1fr);
    background:rgba(8,16,29,.92);
    backdrop-filter:blur(18px);
    border-top:1px solid var(--line);
}
.nav a{
    padding:12px 6px;
    text-align:center;
    text-decoration:none;
    color:var(--muted);
    font-size:11px;
}
.nav a b{
    display:block;
    margin-top:4px;
    font-size:12px;
    color:inherit;
}
.notice{
    padding:12px 14px;
    border-radius:16px;
    background:rgba(35,209,139,.12);
    border:1px solid rgba(35,209,139,.3);
    color:#b9ffe0;
    font-size:13px;
    line-height:1.5;
}
hr{border:none;border-top:1px solid var(--line);margin:14px 0}
.small{padding:10px 12px;font-size:12px;border-radius:12px}
</style>
</head>
<body>
<div class="shell">
  <div class="top">
    <div class="badge">{{ badge }}</div>
    <div class="h1">{{ title }}</div>
    <div class="sub">{{ subtitle }}</div>
  </div>

  <div class="content">
    {% if notice %}
    <div class="notice">{{ notice }}</div>
    <div style="height:12px"></div>
    {% endif %}

    <div class="card">
      <div class="sec">{{ labels.language }}</div>
      <form method="get" action="/">
        <div class="grid">
          <select class="select" name="lang" onchange="this.form.submit()">
            {% for code,name in languages.items() %}
            <option value="{{ code }}" {% if code == ui_lang %}selected{% endif %}>{{ name }}</option>
            {% endfor %}
          </select>
          <button class="btn secondary" type="submit">{{ labels.apply }}</button>
        </div>
      </form>
    </div>

    <div class="card">
      <div class="sec">{{ labels.profile }}</div>
      {% if child %}
      <div class="row">
        <div class="avatar">{{ child.name[:1]|upper }}</div>
        <div style="flex:1">
          <div style="font-weight:700">{{ child.name }} · {{ child.age_months }}m</div>
          <div class="muted">{{ child.region }} · {{ child.language }} · {{ child.nationality }}</div>
        </div>
        <a class="pill" href="/clear?lang={{ ui_lang }}">{{ labels.reset }}</a>
      </div>
      {% else %}
      <form method="post" action="/register?lang={{ ui_lang }}">
        <div class="grid">
          <input class="input" name="name" placeholder="{{ labels.child_name }}" required>
          <input class="input" name="birth_date" type="date" required>
        </div>
        <div style="height:10px"></div>
        <div class="grid">
          <select class="select" name="region">
            {% for r in regions %}
            <option value="{{ r }}">{{ r }}</option>
            {% endfor %}
          </select>
          <input class="input" name="nationality" placeholder="{{ labels.nationality }}" value="Korea" required>
        </div>
        <div style="height:10px"></div>
        <select class="select" name="language">
          {% for code,name in languages.items() %}
          <option value="{{ code }}" {% if code == default_lang %}selected{% endif %}>{{ name }}</option>
          {% endfor %}
        </select>
        <div style="height:10px"></div>
        <button class="btn" type="submit">{{ labels.register }}</button>
      </form>
      {% endif %}
    </div>

    <div class="card">
      <div class="sec">{{ labels.roadmap }}</div>
      <div class="timeline">
        {% for item in roadmap %}
        <div class="timeline-item">
          <div class="k {{ item.category|lower }}">{{ item.category }}</div>
          <div class="title">[{{ item.month }}m] {{ item.title }}</div>
          <p class="desc">{{ item.description }}</p>
          <div style="display:flex;gap:8px;margin-top:10px">
            {% if item.active %}
            <a class="pill" href="/roadmap/remove/{{ item.id }}?lang={{ ui_lang }}">{{ labels.remove }}</a>
            {% else %}
            <a class="pill" href="/roadmap/add/{{ item.id }}?lang={{ ui_lang }}">{{ labels.add }}</a>
            {% endif %}
          </div>
        </div>
        {% endfor %}
      </div>
    </div>

    <div class="card">
      <div class="sec">{{ labels.spots }}</div>
      {% for s in spots %}
      <div class="timeline-item" style="margin-bottom:10px">
        <div class="split">
          <div>
            <div class="title">{{ s.name }}</div>
            <div class="muted">{{ s.region }} · {{ s.radius_m }}m</div>
          </div>
          <a class="pill" href="/spot/{{ s.id }}?lang={{ ui_lang }}">AR</a>
        </div>
      </div>
      {% endfor %}
    </div>

    <div class="card">
      <div class="sec">{{ labels.cast }}</div>
      <form method="post" action="/cast/start?lang={{ ui_lang }}">
        <div class="grid">
          <input class="input" name="host_name" placeholder="Guide name" required>
          <select class="select" name="profile_lang">
            {% for code,name in languages.items() %}
            <option value="{{ code }}">{{ name }}</option>
            {% endfor %}
          </select>
        </div>
        <div style="height:10px"></div>
        <button class="btn" type="submit">{{ labels.start_session }}</button>
      </form>
      {% if cast_session %}
      <div style="height:12px"></div>
      <div class="notice">Session {{ cast_session.session_code }} · {{ cast_session.attendee_count }} attendees</div>
      {% endif %}
    </div>

    <div class="card">
      <div class="sec">{{ labels.gov }}</div>
      {% if child %}
      {% for g in govs %}
      <div class="timeline-item" style="margin-bottom:10px">
        <div class="title">{{ g.title }}</div>
        <div class="muted">{{ g.description }}</div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px">
          <span class="pill">{{ g.max_amount }} KRW</span>
          <span class="pill">{{ g.documents }}</span>
          <span class="pill">{{ g.hotline }}</span>
        </div>
      </div>
      {% endfor %}
      {% else %}
      <div class="muted">{{ labels.no_gov }}</div>
      {% endif %}
    </div>

    {% if latest_translation %}
    <div class="card">
      <div class="sec">{{ labels.translation }}</div>
      <div class="timeline-item">
        <div class="title">{{ latest_translation.source }}</div>
        <p class="desc">{{ latest_translation.translation }}</p>
        <div class="muted" style="margin-top:8px">{{ latest_translation.note }}</div>
      </div>
    </div>
    {% endif %}
  </div>

  <div class="nav">
    <a href="/?lang={{ ui_lang }}"><b>Home</b>App</a>
    <a href="/translate-demo?lang={{ ui_lang }}"><b>Translate</b>Google</a>
    <a href="/?lang={{ ui_lang }}#spots"><b>Spot</b>Map</a>
    <a href="/?lang={{ ui_lang }}#gov"><b>Gov</b>Match</a>
  </div>
</div>
</body>
</html>
"""

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.executescript(SCHEMA)

    cur.execute("SELECT COUNT(*) FROM roadmap_cards")
    if cur.fetchone()[0] == 0:
        now = datetime.datetime.now().isoformat(timespec="seconds")
        cur.executemany(
            "INSERT INTO roadmap_cards (title, category, month, description, active, created_at) VALUES (?,?,?,?,?,?)",
            [
                ("BCG vaccination guidance", "Health", 0, "Show local vaccination schedule and nearest clinic.", 1, now),
                ("100-day celebration customs", "Culture", 3, "Localized family tradition guide in the selected language.", 1, now),
                ("Infant health checkup", "Health", 6, "Recommended developmental checkup and follow-up reminders.", 1, now),
                ("Bilingual development track", "Support", 12, "Monthly bilingual story mission cards for the child.", 0, now),
            ],
        )

    cur.execute("SELECT COUNT(*) FROM cultural_spots")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO cultural_spots (name, region, lat, lng, radius_m, audio_script, quiz_answer, mileage) VALUES (?,?,?,?,?,?,?,?)",
            [
                ("National Folk Museum", "Seoul", 37.576, 126.986, 100, "This is a historic cultural site.", "museum", 15),
                ("Mapo Heritage Walk", "Seoul", 37.556, 126.913, 100, "A short story about local heritage.", "walk", 10),
            ],
        )

    cur.execute("SELECT COUNT(*) FROM gov_supports")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO gov_supports (title, region, description, documents, max_amount, eligibility, hotline) VALUES (?,?,?,?,?,?,?)",
            [
                ("Childcare Support Voucher", "Seoul", "Monthly childcare benefit for eligible families.", "ID, Family relation certificate", 300000, "Income and residence criteria", "129"),
                ("Multicultural Family Center Program", "Seoul", "Language and parenting support program.", "ID, Residence proof", 0, "Multicultural family", "1577-1366"),
            ],
        )

    conn.commit()
    conn.close()

def calculate_months(birth_date_str):
    try:
        birth = datetime.datetime.strptime(birth_date_str, "%Y-%m-%d").date()
        today = datetime.date.today()
        return (today.year - birth.year) * 12 + today.month - birth.month - (1 if today.day < birth.day else 0)
    except Exception:
        return 0

def get_lang():
    lang = request.args.get("lang", DEFAULT_LANG).lower().strip()
    return lang if lang in SUPPORTED_LANGUAGES else DEFAULT_LANG

def translate_google(text, target_lang):
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not GOOGLE_TRANSLATE_AVAILABLE or not project_id:
        return None
    client = translate.TranslationServiceClient()
    parent = f"projects/{project_id}/locations/global"
    response = client.translate_text(
        request={
            "parent": parent,
            "contents": [text],
            "mime_type": "text/plain",
            "target_language_code": target_lang,
            "source_language_code": "en",
        }
    )
    if response.translations:
        return response.translations[0].translated_text
    return None

@app.route("/")
def index():
    lang = get_lang()
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM children ORDER BY id DESC LIMIT 1")
    child_row = cur.fetchone()
    child = None
    if child_row:
        child = dict(child_row)
        child["age_months"] = calculate_months(child["birth_date"])

    cur.execute("SELECT * FROM roadmap_cards ORDER BY month ASC, id ASC")
    roadmap = cur.fetchall()

    cur.execute("SELECT * FROM cultural_spots ORDER BY id ASC")
    spots = cur.fetchall()

    cur.execute("SELECT * FROM gov_supports ORDER BY max_amount DESC, id ASC")
    govs = cur.fetchall()

    cur.execute("SELECT * FROM cast_sessions ORDER BY id DESC LIMIT 1")
    cast_session = cur.fetchone()

    conn.close()

    return render_template_string(
        HTML,
        ui_lang=lang,
        title=UI_TEXT[lang]["title"],
        subtitle=UI_TEXT[lang]["subtitle"],
        badge=UI_TEXT[lang]["default_badge"],
        languages=SUPPORTED_LANGUAGES,
        default_lang=DEFAULT_LANG,
        labels=UI_TEXT[lang],
        regions=["Seoul", "Busan", "Incheon", "Gyeonggi"],
        child=child,
        roadmap=roadmap,
        spots=spots,
        govs=govs,
        cast_session=cast_session,
        latest_translation=app.latest_translation,
        notice=app.latest_notice,
    )

@app.route("/register", methods=["POST"])
def register():
    lang = get_lang()
    name = request.form.get("name", "").strip()
    birth_date = request.form.get("birth_date", "").strip()
    nationality = request.form.get("nationality", "Korea").strip()
    language = request.form.get("language", DEFAULT_LANG).strip().lower()
    region = request.form.get("region", "Seoul").strip()
    age_months = calculate_months(birth_date)

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM children")
    cur.execute(
        "INSERT INTO children (name, birth_date, nationality, language, region, age_months) VALUES (?,?,?,?,?,?)",
        (name, birth_date, nationality, language, region, age_months),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("index", lang=lang))

@app.route("/clear")
def clear():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM children")
    conn.commit()
    conn.close()
    app.latest_translation = None
    app.latest_notice = None
    return redirect(url_for("index", lang=get_lang()))

@app.route("/roadmap/remove/<int:item_id>")
def roadmap_remove(item_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("UPDATE roadmap_cards SET active=0 WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index", lang=get_lang()))

@app.route("/roadmap/add/<int:item_id>")
def roadmap_add(item_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("UPDATE roadmap_cards SET active=1 WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index", lang=get_lang()))

@app.route("/spot/<int:spot_id>")
def spot_detail(spot_id):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM cultural_spots WHERE id=?", (spot_id,))
    spot = cur.fetchone()
    conn.close()
    if not spot:
        return jsonify({"error": "not found"}), 404
    return jsonify({
        "name": spot["name"],
        "region": spot["region"],
        "audio_script": spot["audio_script"],
        "quiz_answer": spot["quiz_answer"],
        "mileage": spot["mileage"]
    })

@app.route("/cast/start", methods=["POST"])
def cast_start():
    lang = get_lang()
    host_name = request.form.get("host_name", "").strip()
    profile_lang = request.form.get("profile_lang", DEFAULT_LANG).strip().lower()
    code = datetime.datetime.now().strftime("CS%Y%m%d%H%M%S")

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO cast_sessions (session_code, host_name, profile_lang, status, attendee_count, created_at) VALUES (?,?,?,?,?,?)",
        (code, host_name, profile_lang, "live", 1, datetime.datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()

    app.latest_notice = f"Cast session created: {code}"
    return redirect(url_for("index", lang=lang))

@app.route("/translate-demo")
def translate_demo():
    lang = get_lang()
    text = "Welcome to Mamam Linker"
    translated = translate_google(text, lang)
    if translated is None:
        fallback = {
            "en": "Welcome to Mamam Linker",
            "ko": "마맘링커에 오신 것을 환영합니다.",
            "vi": "Chào mừng bạn đến với Mamam Linker",
            "zh": "欢迎来到 Mamam Linker",
            "ph": "Maligayang pagdating sa Mamam Linker",
        }
        translated = fallback.get(lang, text)

    app.latest_translation = {
        "source": text,
        "translation": translated,
        "note": "Google Cloud Translation API will be used when credentials are configured."
    }
    return redirect(url_for("index", lang=lang))

@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "app": APP_NAME,
        "db": DB_FILE,
        "google_translate_available": GOOGLE_TRANSLATE_AVAILABLE
    })

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
