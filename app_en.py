import datetime
import io
import sqlite3
from flask import Flask, redirect, render_template_string, request, url_for, make_response

app = Flask(__name__)
DB_FILE = "mother_all.db"

# ==========================================
# 1. 다국어 기본 설정
# ==========================================
LANGUAGES = {
    "en": "English",
    "ko": "한국어",
    "vi": "Tiếng Việt",
    "zh": "中文",
    "ph": "Filipino"
}

TRANSLATIONS = {
    "en": {
        "title": "MOA (Mother-All) - K-Parenting Navigation",
        "subtitle": "K-Culture Parenting Integrated Navigation",
        "child_section": "Child Info and AI Personalization",
        "community_section": "Nearby Language-Matched Mom Network",
        "timeline_section": "Age-Based Integrated Timeline",
        "idiom_section": "AI K-Parenting Idiom Translator",
        "support_section": "Local Infrastructure Status",
        "document_section": "One-Click Administrative Document Helper",
        "register_button": "Start Personalized Parenting Ecosystem",
        "reset_button": "Reset",
        "language_label": "Language",
        "region_label": "Region",
        "nationality_label": "Nationality",
        "birth_label": "Birth Date",
        "name_label": "Child Name",
    },
    "ko": {
        "title": "모아 (Mother-All) - K-컬처 육아 내비게이션",
        "subtitle": "K-컬처 육아 통합 내비게이션",
        "child_section": "자녀 정보 및 AI 맞춤화 설정",
        "community_section": "주변 동일 언어 맘 소통 네트워크",
        "timeline_section": "월령별 맞춤형 융합 타임라인",
        "idiom_section": "AI K-육아 관용구 의역기",
        "support_section": "전국 지자체 실시간 인프라 현황",
        "document_section": "원클릭 행정 서류 자동 도우미",
        "register_button": "맞춤형 육아 에코시스템 가동",
        "reset_button": "재설정하기",
        "language_label": "사용 언어 선택",
        "region_label": "거주 지역",
        "nationality_label": "어머니 국적 배경",
        "birth_label": "출생일",
        "name_label": "아이 이름 (또는 태명)",
    },
    "vi": {
        "title": "MOA (Mother-All) - Điều hướng nuôi con Hàn Quốc",
        "subtitle": "Điều hướng nuôi con tích hợp văn hóa Hàn",
        "child_section": "Thông tin bé và cá nhân hóa AI",
        "community_section": "Mạng lưới mẹ cùng ngôn ngữ gần đây",
        "timeline_section": "Lộ trình tích hợp theo tháng tuổi",
        "idiom_section": "Công cụ diễn giải thành ngữ nuôi con Hàn",
        "support_section": "Tình trạng hạ tầng địa phương",
        "document_section": "Trợ lý giấy tờ hành chính một chạm",
        "register_button": "Kích hoạt hệ sinh thái nuôi con cá nhân hóa",
        "reset_button": "Đặt lại",
        "language_label": "Chọn ngôn ngữ",
        "region_label": "Khu vực sinh sống",
        "nationality_label": "Quốc tịch mẹ",
        "birth_label": "Ngày sinh",
        "name_label": "Tên bé (hoặc tên thai nhi)",
    },
    "zh": {
        "title": "MOA (Mother-All) - 韩国育儿导航",
        "subtitle": "韩国文化育儿综合导航",
        "child_section": "儿童信息与AI个性化设置",
        "community_section": "附近同语言妈妈交流网络",
        "timeline_section": "按月龄定制融合时间线",
        "idiom_section": "AI韩国育儿俗语翻译器",
        "support_section": "全国地方设施实时状态",
        "document_section": "一键行政文件助手",
        "register_button": "启动个性化育儿生态系统",
        "reset_button": "重置",
        "language_label": "选择语言",
        "region_label": "居住地区",
        "nationality_label": "母亲国籍背景",
        "birth_label": "出生日期",
        "name_label": "孩子姓名（或胎名）",
    },
    "ph": {
        "title": "MOA (Mother-All) - Gabay sa Parenting sa Korea",
        "subtitle": "Pinagsamang gabay sa pag-aalaga ng bata sa kulturang Koreano",
        "child_section": "Impormasyon ng bata at AI personalization",
        "community_section": "Komunidad ng mga nanay na pareho ng wika",
        "timeline_section": "Timeline ayon sa buwan ng edad",
        "idiom_section": "AI translator ng Korean parenting idioms",
        "support_section": "Real-time na local infrastructure status",
        "document_section": "One-click na assistant sa dokumento",
        "register_button": "I-activate ang personalized parenting ecosystem",
        "reset_button": "I-reset",
        "language_label": "Pumili ng wika",
        "region_label": "Lugar ng tirahan",
        "nationality_label": "Bansang pinagmulan ng ina",
        "birth_label": "Petsa ng kapanganakan",
        "name_label": "Pangalan ng bata (o nickname)",
    }
}

DEFAULT_UI_LANG = "en"

# ==========================================
# 2. 데이터베이스 초기화
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS children (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    birth_date TEXT NOT NULL,
                    nationality TEXT NOT NULL,
                    language TEXT NOT NULL,
                    region TEXT NOT NULL,
                    age_months INTEGER DEFAULT 0
                 )''')

    c.execute('''CREATE TABLE IF NOT EXISTS master_timeline (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_month INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT NOT NULL,
                    source_asset TEXT NOT NULL
                 )''')

    c.execute('''CREATE TABLE IF NOT EXISTS cultural_dictionary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    idiom TEXT NOT NULL,
                    target_lang TEXT NOT NULL,
                    translation TEXT NOT NULL,
                    explanation TEXT NOT NULL,
                    cultural_tip TEXT NOT NULL
                 )''')

    c.execute('''CREATE TABLE IF NOT EXISTS support_centers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    region TEXT NOT NULL,
                    facility_name TEXT NOT NULL,
                    toy_inventory INTEGER NOT NULL,
                    playroom_status TEXT NOT NULL
                 )''')

    c.execute('''CREATE TABLE IF NOT EXISTS culture_groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_name TEXT NOT NULL,
                    region TEXT NOT NULL,
                    target_language TEXT NOT NULL,
                    host_name TEXT NOT NULL,
                    member_count INTEGER DEFAULT 1,
                    description TEXT NOT NULL
                 )''')

    c.execute('''CREATE TABLE IF NOT EXISTS reservations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    child_name TEXT NOT NULL,
                    facility_name TEXT NOT NULL,
                    reserved_at TEXT NOT NULL
                 )''')

    c.execute("SELECT count(*) FROM master_timeline")
    if c.fetchone()[0] == 0:
        timeline_data = [
            (0, "BCG vaccination guidance", "Health", "The BCG vaccine should be given within 4 weeks after birth. Check local health center information.", "Ministry of Health and Welfare guideline v1.2"),
            (3, "21-day and 100-day celebration customs", "Culture", "In Korea, families share baekseolgi rice cake with neighbors on the 100th day to wish the baby health and longevity.", "National Folk Museum of Korea lifecycle archive"),
            (6, "3rd hepatitis B vaccination and infant checkup", "Health", "Six months after birth is a period when immunity may drop. Don't miss the developmental checkup.", "Childcare Policy Research Institute guide"),
            (6, "Multicultural mentoring program at family center", "Support", "Connect with experienced migrant mothers for support in adapting to Korean parenting culture.", "Ministry of Gender Equality and Family support data"),
            (12, "Traditional doljanchi and doljabi experience", "Culture", "At the first birthday, families celebrate and predict the child's future through doljabi items.", "National Folk Museum of Korea folklore archive")
        ]
        c.executemany("INSERT INTO master_timeline (target_month, title, category, description, source_asset) VALUES (?, ?, ?, ?, ?)", timeline_data)

        dict_data = [
            ("등센서", "vi", "Cảm biến lưng", "Từ lóng chỉ việc em bé khóc ngay khi đặt nằm xuống.", "Người Hàn thường dùng gối ôm chữ U để tạo cảm giác an toàn."),
            ("돌치레", "vi", "Sốt mọc răng / ốm nhẹ đầu đời", "Tình trạng trẻ bị sốt hoặc ốm nhẹ quanh sinh nhật đầu tiên.", "Hiện tượng sinh lý thường gặp khi kháng thể từ mẹ giảm đi."),
            ("우쭈쭈", "vi", "Âu yếm, cưng nựng", "Âm thanh dỗ dành hoặc thể hiện tình yêu thương với trẻ nhỏ.", "Tương tự cách nói cưng nựng trẻ em trong tiếng Việt."),
            ("등센서", "ko", "등센서", "아기를 눕히자마자 바로 우는 상황을 뜻하는 신조어입니다.", "공감 육아 표현으로 자주 사용됩니다.")
        ]
        c.executemany("INSERT INTO cultural_dictionary (idiom, target_lang, translation, explanation, cultural_tip) VALUES (?, ?, ?, ?, ?)", dict_data)

        center_data = [
            ("서울시 마포구", "마포 영유아 장난감 도서관", 14, "예약 가능"),
            ("부산시 해운대구", "해운대 놀이체험실", 3, "마감 임박"),
            ("인천시 부평구", "부평 육아종합지원센터", 25, "예약 가능")
        ]
        c.executemany("INSERT INTO support_centers (region, facility_name, toy_inventory, playroom_status) VALUES (?, ?, ?, ?)", center_data)

        group_data = [
            ("국립민속박물관 다문화 백일 문화 체험", "서울시 마포구", "vi", "흐엉 (베트남)", 3, "같은 베트남 엄마들끼리 모여서 한국 백일 떡 만들기 체험 같이 가요!"),
            ("해운대 육아종합지원센터 유아 놀이방 모임", "부산시 해운대구", "vi", "마이티 (베트남)", 2, "6개월 전후 아기 데리고 같이 수다 떨며 정보 공유해요.")
        ]
        c.executemany("INSERT INTO culture_groups (event_name, region, target_language, host_name, member_count, description) VALUES (?, ?, ?, ?, ?, ?)", group_data)

    conn.commit()
    conn.close()

# ==========================================
# 3. 헬퍼 함수
# ==========================================
def calculate_months(birth_date_str):
    try:
        birth_date = datetime.datetime.strptime(birth_date_str, "%Y-%m-%d").date()
        today = datetime.date.today()
        return (today.year - birth_date.year) * 12 + today.month - birth_date.month - (1 if today.day < birth_date.day else 0)
    except Exception:
        return 0

def get_ui_lang():
    lang = request.args.get("ui_lang", DEFAULT_UI_LANG).strip().lower()
    return lang if lang in LANGUAGES else DEFAULT_UI_LANG

def t(key):
    lang = get_ui_lang()
    return TRANSLATIONS.get(lang, TRANSLATIONS[DEFAULT_UI_LANG]).get(key, key)

# ==========================================
# 4. 템플릿
# ==========================================
HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="{{ ui_lang }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>{{ ui_title }}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #FF7A94;
            --primary-light: #FFEBF0;
            --secondary: #6C5CE7;
            --secondary-light: #EEECFB;
            --dark: #2D3436;
            --gray-bg: #F8F9FD;
            --success: #00B894;
        }
        * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { margin: 0; padding: 0; background-color: #E9ECEF; display: flex; justify-content: center; min-height: 100vh; }
        .app-frame { width: 100%; max-width: 430px; background-color: var(--gray-bg); min-height: 100vh; position: relative; padding-bottom: 90px; box-shadow: 0 0 30px rgba(0,0,0,0.15); display: flex; flex-direction: column; }
        header { background: linear-gradient(135deg, var(--secondary), var(--primary)); padding: 35px 24px 25px; border-radius: 0 0 32px 32px; color: white; }
        header .brand-zone { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
        header .brand-zone h2 { margin: 0; font-size: 20px; font-weight: 800; letter-spacing: -0.5px; }
        header .brand-zone .badge { background: rgba(255,255,255,0.2); padding: 4px 10px; border-radius: 12px; font-size: 11px; }
        header h1 { margin: 0; font-size: 24px; font-weight: 700; line-height: 1.3; }
        .container { padding: 20px; flex: 1; }
        h3 { font-size: 18px; color: var(--dark); margin: 24px 0 14px; display: flex; align-items: center; gap: 8px; }
        .app-card { background: white; border-radius: 24px; padding: 20px; margin-bottom: 20px; box-shadow: 0 8px 16px rgba(0,0,0,0.02); border: 1px solid rgba(0,0,0,0.03); }
        .form-group { margin-bottom: 16px; }
        .form-group label { display: block; font-size: 13px; font-weight: 600; color: #64748B; margin-bottom: 6px; }
        .form-control { width: 100%; padding: 14px; border-radius: 14px; border: 1.5px solid #E2E8F0; font-size: 15px; background: #F8FAFC; transition: 0.2s; }
        .form-control:focus { outline: none; border-color: var(--primary); background: white; }
        .btn-submit { width: 100%; background: var(--dark); color: white; border: none; padding: 15px; border-radius: 14px; font-size: 16px; font-weight: 700; cursor: pointer; transition: 0.2s; }
        .btn-submit:hover { background: var(--primary); }
        .btn-sm { padding: 6px 12px; border-radius: 8px; font-size: 11px; font-weight: 700; border: none; cursor: pointer; color: white; }
        .baby-profile { display: flex; align-items: center; gap: 16px; background: white; padding: 16px; border-radius: 20px; border-left: 5px solid var(--primary); }
        .baby-avatar { width: 50px; height: 50px; background: var(--primary-light); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: var(--primary); font-size: 22px; }
        .baby-info h4 { margin: 0; font-size: 16px; color: var(--dark); }
        .baby-info p { margin: 4px 0 0; font-size: 13px; color: #64748B; }
        .timeline-stream { position: relative; padding-left: 20px; border-left: 2px dashed #E2E8F0; margin-left: 10px; }
        .timeline-node { position: relative; margin-bottom: 24px; }
        .timeline-icon { position: absolute; left: -31px; top: 2px; width: 20px; height: 20px; border-radius: 50%; background: white; border: 3px solid var(--primary); }
        .timeline-node.health .timeline-icon { border-color: var(--secondary); }
        .timeline-node.support .timeline-icon { border-color: var(--success); }
        .timeline-body { background: white; padding: 16px; border-radius: 18px; }
        .timeline-tag { font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 8px; display: inline-block; margin-bottom: 8px; }
        .timeline-tag.culture { background: var(--primary-light); color: var(--primary); }
        .timeline-tag.health { background: var(--secondary-light); color: var(--secondary); }
        .timeline-tag.support { background: #E6F9F5; color: var(--success); }
        .timeline-title { font-size: 15px; font-weight: 700; color: var(--dark); margin: 0 0 6px; }
        .timeline-text { font-size: 13px; color: #4A5568; margin: 0 0 8px; line-height: 1.4; }
        .match-card { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 16px; padding: 14px; margin-bottom: 12px; }
        .match-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
        .match-lang-tag { background: #E2E8F0; color: var(--dark); font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 6px; }
        .match-title { font-size: 14px; font-weight: 700; color: var(--dark); margin-bottom: 4px; }
        .match-desc { font-size: 12px; color: #4A5568; line-height: 1.4; margin-bottom: 10px; }
        .match-footer { display: flex; justify-content: space-between; align-items: center; font-size: 11px; color: #94A3B8; }
        .dict-result-box { background: #F1F2F6; border-radius: 16px; padding: 16px; margin-top: 14px; border-left: 4px solid var(--secondary); }
        .dict-title { font-size: 15px; font-weight: 700; color: var(--secondary); margin-bottom: 4px; }
        .dict-trans { font-size: 13px; font-weight: 600; color: var(--dark); margin-bottom: 6px; }
        .dict-desc { font-size: 12px; color: #4E5968; margin-bottom: 8px; line-height: 1.4; }
        .dict-tip { font-size: 11px; color: #FF7A94; font-weight: 600; background: white; padding: 8px; border-radius: 8px; }
        .api-badge { font-size: 11px; background: #EDF2F7; color: #4A5568; padding: 4px 8px; border-radius: 6px; }
        .doc-preview { background: #FAF9F6; border: 1px dashed #D3D3D3; border-radius: 12px; padding: 16px; font-family: monospace; font-size: 11px; line-height: 1.4; }
        .bottom-nav { position: fixed; bottom: 0; width: 100%; max-width: 430px; height: 74px; background: rgba(255, 255, 255, 0.94); backdrop-filter: blur(12px); display: flex; justify-content: space-around; align-items: center; border-top: 1px solid rgba(0,0,0,0.06); border-radius: 24px 24px 0 0; z-index: 100; }
        .nav-item { text-decoration: none; color: #94A3B8; display: flex; flex-direction: column; align-items: center; gap: 4px; font-size: 11px; font-weight: 600; }
        .nav-item.active { color: var(--primary); }
        .nav-item i { font-size: 20px; }
    </style>
</head>
<body>
    <div class="app-frame">
        <header>
            <div class="brand-zone">
                <h2>MOA (Mother-All)</h2>
                <div class="badge"><i class="fa-solid fa-earth-asia"></i> Live Network v1.2</div>
            </div>
            <h1>{{ ui_subtitle }}</h1>
        </header>

        <div class="container">
            <h3><i class="fa-solid fa-baby"></i> {{ ui_child_section }}</h3>
            <div class="app-card">
                {% if child %}
                <div class="baby-profile">
                    <div class="baby-avatar"><i class="fa-solid fa-child-reaching"></i></div>
                    <div class="baby-info">
                        <h4>{{ child.name }} ({{ child.nationality }})</h4>
                        <p>{{ ui_region_label }}: <strong>{{ child.region }}</strong> | <strong>{{ child.age_months }} months</strong></p>
                        <p style="font-size:11px; margin-top:2px;">{{ ui_language_label }}: <span style="color:var(--secondary); font-weight:700;">{{ child.language }}</span></p>
                    </div>
                </div>
                <div style="margin-top:12px; text-align:right;">
                    <a href="{{ url_for('clear_child') }}?ui_lang={{ ui_lang }}" style="font-size:12px; color:#94A3B8; text-decoration:none;"><i class="fa-solid fa-rotate-left"></i> {{ ui_reset_button }}</a>
                </div>
                {% else %}
                <form action="/register?ui_lang={{ ui_lang }}" method="POST">
                    <div class="form-group">
                        <label>{{ ui_name_label }}</label>
                        <input type="text" name="name" class="form-control" placeholder="Example: Sarah" required>
                    </div>
                    <div class="form-group">
                        <label>{{ ui_birth_label }}</label>
                        <input type="date" name="birth_date" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label>{{ ui_region_label }}</label>
                        <select name="region" class="form-control">
                            <option value="서울시 마포구">서울시 마포구</option>
                            <option value="부산시 해운대구">부산시 해운대구</option>
                            <option value="인천시 부평구">인천시 부평구</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>{{ ui_nationality_label }}</label>
                        <select name="nationality" class="form-control">
                            <option value="Korea">Korea</option>
                            <option value="Vietnam">Vietnam</option>
                            <option value="China">China</option>
                            <option value="Philippines">Philippines</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>{{ ui_language_label }}</label>
                        <select name="language" class="form-control">
                            <option value="en">English</option>
                            <option value="ko">한국어</option>
                            <option value="vi">Tiếng Việt</option>
                            <option value="zh">中文</option>
                            <option value="ph">Filipino</option>
                        </select>
                    </div>
                    <button type="submit" class="btn-submit"><i class="fa-solid fa-heart"></i> {{ ui_register_button }}</button>
                </form>
                {% endif %}
            </div>

            <h3><i class="fa-solid fa-people-roof"></i> {{ ui_community_section }}</h3>
            <div class="app-card">
                <p style="font-size:13px; color:#64748B; margin-top:0;">Find nearby parents who use the same language and join cultural and childcare activities.</p>

                {% if child %}
                    <div style="margin-bottom: 12px; background: #EEECFB; padding: 10px; border-radius: 10px; font-size: 12px; color: var(--secondary); font-weight: bold;">
                        <i class="fa-solid fa-bullseye"></i> {{ child.region }} + {{ child.language }}
                    </div>

                    {% if matching_groups %}
                        {% for group in matching_groups %}
                        <div class="match-card">
                            <div class="match-header">
                                <span class="match-lang-tag"><i class="fa-solid fa-comments"></i> {{ group.target_language }}</span>
                                <span style="font-size:11px; color:var(--success); font-weight:700;"><i class="fa-solid fa-user-group"></i> {{ group.member_count }} members</span>
                            </div>
                            <div class="match-title">{{ group.event_name }}</div>
                            <div class="match-desc">{{ group.description }}</div>
                            <div class="match-footer">
                                <span>Host: {{ group.host_name }}</span>
                                <form action="/join-group/{{ group.id }}?ui_lang={{ ui_lang }}" method="POST" style="margin:0;">
                                    <button type="submit" class="btn-sm" style="background:var(--secondary);"><i class="fa-solid fa-door-open"></i> Join</button>
                                </form>
                            </div>
                        </div>
                        {% endfor %}
                    {% else %}
                        <p style="font-size:12px; color:#A0AEC0; text-align:center; padding:10px 0;">No matching group is available for your region and language.</p>
                    {% endif %}

                    <hr style="border:0; border-top:1px solid #E2E8F0; margin:16px 0;">
                    <form action="/create-group?ui_lang={{ ui_lang }}" method="POST" style="background:#F8FAFC; padding:12px; border-radius:14px;">
                        <div style="font-size:13px; font-weight:700; color:var(--dark); margin-bottom:8px;"><i class="fa-solid fa-plus"></i> Create a local cultural meetup</div>
                        <input type="text" name="event_name" class="form-control" placeholder="Event name" required style="padding:8px; font-size:12px; margin-bottom:8px;">
                        <input type="text" name="description" class="form-control" placeholder="Description" required style="padding:8px; font-size:12px; margin-bottom:8px;">
                        <button type="submit" class="btn-sm" style="background:var(--primary); width:100%; padding:8px;"><i class="fa-solid fa-users"></i> Create channel</button>
                    </form>
                {% else %}
                    <p style="font-size:12px; color:#A0AEC0; text-align:center; padding:15px 0;">Register a child profile to see matching community lists.</p>
                {% endif %}
            </div>

            <h3><i class="fa-solid fa-hourglass-half"></i> {{ ui_timeline_section }}</h3>
            <div class="app-card">
                {% if timeline_events %}
                <div class="timeline-stream">
                    {% for event in timeline_events %}
                    <div class="timeline-node {{ event.category|lower }}">
                        <div class="timeline-icon"></div>
                        <div class="timeline-body">
                            <span class="timeline-tag {{ event.category|lower }}">{{ event.category }}</span>
                            <div class="timeline-title">[{{ event.target_month }} months] {{ event.title }}</div>
                            <div class="timeline-text">{{ event.description }}</div>
                            <div class="timeline-source"><i class="fa-solid fa-square-poll-horizontal"></i> {{ event.source_asset }}</div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% else %}
                <p style="font-size:12px; color:#64748B; text-align:center; padding:15px 0;">Personalized timeline will appear after child registration.</p>
                {% endif %}
            </div>

            <h3><i class="fa-solid fa-wand-magic-sparkles"></i> {{ ui_idiom_section }}</h3>
            <div class="app-card">
                <form action="/translate?ui_lang={{ ui_lang }}" method="POST" style="display:flex; gap:8px;">
                    <input type="text" name="idiom" class="form-control" placeholder="등센서, 돌치레, 우쭈쭈" required style="margin:0;">
                    <button type="submit" class="btn-submit" style="width:auto; padding:0 20px; margin:0;"><i class="fa-solid fa-magnifying-glass"></i></button>
                </form>

                {% if dict_result %}
                <div class="dict-result-box">
                    <div class="dict-title"><i class="fa-solid fa-comment-dots"></i> {{ dict_result.idiom }}</div>
                    <div class="dict-trans"><i class="fa-solid fa-language"></i> {{ dict_result.translation }}</div>
                    <div class="dict-desc">{{ dict_result.explanation }}</div>
                    <div class="dict-tip"><i class="fa-solid fa-lightbulb"></i> Care Tip: {{ dict_result.cultural_tip }}</div>
                </div>
                {% endif %}
            </div>

            <h3><i class="fa-solid fa-map-location-dot"></i> {{ ui_support_section }}</h3>
            <div class="app-card">
                {% for center in support_centers %}
                <div style="padding:14px 0; border-bottom:1px solid #EDF2F7; display:flex; justify-content:space-between; align-items:center; font-size:13px;">
                    <div style="flex:1;">
                        <strong style="color:var(--dark);">{{ center.facility_name }}</strong>
                        <div style="font-size:11px; color:#A0AEC0; margin-top:2px;">{{ center.region }}</div>
                    </div>
                    <div style="text-align:right; display:flex; flex-direction:column; gap:6px;">
                        <div>
                            <span class="api-badge">Toys: {{ center.toy_inventory }}</span>
                            <span class="api-badge" style="background:#E6F9F5; color:#00B894;">{{ center.playroom_status }}</span>
                        </div>
                        <form action="/reserve-facility/{{ center.id }}?ui_lang={{ ui_lang }}" method="POST" style="margin:0;">
                            <button type="submit" class="btn-sm" style="background:var(--secondary); width:100%;">Reserve</button>
                        </form>
                    </div>
                </div>
                {% endfor %}
            </div>

            <h3><i class="fa-solid fa-file-signature"></i> {{ ui_document_section }}</h3>
            <div class="app-card">
                {% if child %}
                <div class="doc-preview">
                    [Multicultural Parenting Voucher Application]<br>
                    -------------------------------------<br>
                    Mother nationality: {{ child.nationality }}<br>
                    Preferred language: {{ child.language }}<br>
                    Region: {{ child.region }}<br>
                    Child name: {{ child.name }}<br>
                    Child age: {{ child.age_months }} months<br>
                    -------------------------------------<br>
                    Administrative draft ready
                </div>
                <div style="display:flex; gap:8px; margin-top:12px;">
                    <a href="/download-document?ui_lang={{ ui_lang }}" class="btn-submit" style="background:#64748B; text-align:center; text-decoration:none; font-size:14px; padding:12px; flex:1;">
                        <i class="fa-solid fa-file-arrow-down"></i> Download
                    </a>
                    <button class="btn-submit" style="background:var(--secondary); font-size:14px; padding:12px; flex:1;" onclick="alert('Submitted successfully.')">
                        <i class="fa-solid fa-paper-plane"></i> Submit
                    </button>
                </div>
                {% else %}
                <p style="font-size:12px; color:#A0AEC0; text-align:center; padding:10px 0;">Register a child profile to generate the document draft.</p>
                {% endif %}
            </div>

        </div>

        <nav class="bottom-nav">
            <a href="/?ui_lang={{ ui_lang }}" class="nav-item active"><i class="fa-solid fa-house"></i><span>Home</span></a>
            <a href="/?ui_lang={{ ui_lang }}#translate" class="nav-item"><i class="fa-solid fa-language"></i><span>Translate</span></a>
            <a href="/?ui_lang={{ ui_lang }}#support" class="nav-item"><i class="fa-solid fa-users"></i><span>Community</span></a>
            <a href="/?ui_lang={{ ui_lang }}#document" class="nav-item"><i class="fa-solid fa-file-shield"></i><span>Documents</span></a>
        </nav>
    </div>
</body>
</html>
"""

# ==========================================
# 5. 라우팅
# ==========================================
@app.route("/")
def main_dashboard():
    ui_lang = get_ui_lang()
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM children ORDER BY id DESC LIMIT 1")
    child_row = c.fetchone()

    child = None
    timeline_events = []
    matching_groups = []

    if child_row:
        current_months = calculate_months(child_row["birth_date"])
        child = {
            "name": child_row["name"],
            "birth_date": child_row["birth_date"],
            "nationality": child_row["nationality"],
            "language": child_row["language"],
            "region": child_row["region"],
            "age_months": current_months
        }

        c.execute("SELECT * FROM master_timeline WHERE target_month >= ? ORDER BY target_month ASC LIMIT 3", (current_months,))
        timeline_events = c.fetchall()

        c.execute("SELECT * FROM culture_groups WHERE region = ? AND target_language = ? ORDER BY id DESC", (child["region"], child["language"]))
        matching_groups = c.fetchall()

    c.execute("SELECT * FROM support_centers")
    centers = c.fetchall()

    dict_result = getattr(app, "latest_dict_result", None)
    conn.close()

    return render_template_string(
        HTML_LAYOUT,
        ui_lang=ui_lang,
        ui_title=TRANSLATIONS[ui_lang]["title"],
        ui_subtitle=TRANSLATIONS[ui_lang]["subtitle"],
        ui_child_section=TRANSLATIONS[ui_lang]["child_section"],
        ui_community_section=TRANSLATIONS[ui_lang]["community_section"],
        ui_timeline_section=TRANSLATIONS[ui_lang]["timeline_section"],
        ui_idiom_section=TRANSLATIONS[ui_lang]["idiom_section"],
        ui_support_section=TRANSLATIONS[ui_lang]["support_section"],
        ui_document_section=TRANSLATIONS[ui_lang]["document_section"],
        ui_register_button=TRANSLATIONS[ui_lang]["register_button"],
        ui_reset_button=TRANSLATIONS[ui_lang]["reset_button"],
        ui_language_label=TRANSLATIONS[ui_lang]["language_label"],
        ui_region_label=TRANSLATIONS[ui_lang]["region_label"],
        ui_nationality_label=TRANSLATIONS[ui_lang]["nationality_label"],
        ui_birth_label=TRANSLATIONS[ui_lang]["birth_label"],
        ui_name_label=TRANSLATIONS[ui_lang]["name_label"],
        child=child,
        timeline_events=timeline_events,
        support_centers=centers,
        dict_result=dict_result,
        matching_groups=matching_groups
    )

@app.route("/register", methods=["POST"])
def register_child():
    name = request.form.get("name", "").strip()
    birth_date = request.form.get("birth_date", "").strip()
    nationality = request.form.get("nationality", "").strip()
    language = request.form.get("language", "en").strip().lower()
    region = request.form.get("region", "").strip()

    if language not in LANGUAGES:
        language = DEFAULT_UI_LANG

    initial_months = calculate_months(birth_date)

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM children")
    c.execute(
        "INSERT INTO children (name, birth_date, nationality, language, region, age_months) VALUES (?, ?, ?, ?, ?, ?)",
        (name, birth_date, nationality, language, region, initial_months)
    )
    conn.commit()
    conn.close()

    if hasattr(app, "latest_dict_result"):
        delattr(app, "latest_dict_result")
    return redirect(url_for("main_dashboard", ui_lang=request.args.get("ui_lang", DEFAULT_UI_LANG)))

@app.route("/create-group", methods=["POST"])
def create_group():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT language, region, name FROM children ORDER BY id DESC LIMIT 1")
    child = c.fetchone()

    if child:
        event_name = request.form.get("event_name", "").strip()
        description = request.form.get("description", "").strip()
        c.execute(
            "INSERT INTO culture_groups (event_name, region, target_language, host_name, member_count, description) VALUES (?, ?, ?, ?, ?, ?)",
            (event_name, child["region"], child["language"], f"{child['name']} mom", 1, description)
        )
        conn.commit()

    conn.close()
    return redirect(url_for("main_dashboard", ui_lang=request.args.get("ui_lang", DEFAULT_UI_LANG)))

@app.route("/join-group/<int:group_id>", methods=["POST"])
def join_group(group_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE culture_groups SET member_count = member_count + 1 WHERE id = ?", (group_id,))
    conn.commit()
    conn.close()
    return f"<script>alert('Joined successfully!'); location.href='/?ui_lang={request.args.get('ui_lang', DEFAULT_UI_LANG)}';</script>"

@app.route("/translate", methods=["POST"])
def translate_idiom():
    idiom_keyword = request.form.get("idiom", "").strip()
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT language FROM children ORDER BY id DESC LIMIT 1")
    user_lang_row = c.fetchone()
    target_lang = user_lang_row["language"] if user_lang_row else DEFAULT_UI_LANG

    c.execute("SELECT * FROM cultural_dictionary WHERE idiom LIKE ? AND target_lang = ?", (f"%{idiom_keyword}%", target_lang))
    res = c.fetchone()
    conn.close()

    if res:
        app.latest_dict_result = {
            "idiom": res["idiom"],
            "translation": res["translation"],
            "explanation": res["explanation"],
            "cultural_tip": res["cultural_tip"]
        }
    else:
        app.latest_dict_result = {
            "idiom": idiom_keyword,
            "translation": "No matched translation found",
            "explanation": f"Analyzing the Korean idiom '{idiom_keyword}'.",
            "cultural_tip": "Ask a local mentor for more detailed context."
        }
    return redirect(url_for("main_dashboard", ui_lang=request.args.get("ui_lang", DEFAULT_UI_LANG)))

@app.route("/reserve-facility/<int:facility_id>", methods=["POST"])
def reserve_facility(facility_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT facility_name, toy_inventory FROM support_centers WHERE id = ?", (facility_id,))
    facility = c.fetchone()

    if not facility or facility[1] <= 0:
        conn.close()
        return "<script>alert('No available inventory.'); history.back();</script>"

    c.execute("SELECT name FROM children ORDER BY id DESC LIMIT 1")
    child = c.fetchone()
    child_name = child[0] if child else "Family"

    c.execute("UPDATE support_centers SET toy_inventory = toy_inventory - 1 WHERE id = ?", (facility_id,))
    c.execute(
        "INSERT INTO reservations (child_name, facility_name, reserved_at) VALUES (?, ?, ?)",
        (child_name, facility[0], datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    )
    conn.commit()
    conn.close()
    return f"<script>alert('Reservation complete: {facility[0]}'); location.href='/?ui_lang={request.args.get('ui_lang', DEFAULT_UI_LANG)}';</script>"

@app.route("/download-document", methods=["GET"])
def download_document():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM children ORDER BY id DESC LIMIT 1")
    child = c.fetchone()
    conn.close()

    if not child:
        return "<script>alert('No child profile found.'); history.back();</script>"

    current_months = calculate_months(child["birth_date"])
    doc_content = f"""==================================================
Multicultural Parenting Voucher Application
==================================================
Mother nationality: {child['nationality']}
Preferred language: {child['language']}
Region: {child['region']}
Child name: {child['name']}
Birth date: {child['birth_date']}
Age: {current_months} months
==================================================
Generated on: {datetime.date.today().strftime('%Y-%m-%d')}
"""

    buffer = io.BytesIO()
    buffer.write(doc_content.encode("utf-8"))
    buffer.seek(0)

    response = make_response(buffer.getvalue())
    filename = f"moa_voucher_{child['name']}.txt"
    response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{filename}"
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    return response

@app.route("/clear")
def clear_child():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM children")
    conn.commit()
    conn.close()
    if hasattr(app, "latest_dict_result"):
        delattr(app, "latest_dict_result")
    return redirect(url_for("main_dashboard", ui_lang=request.args.get("ui_lang", DEFAULT_UI_LANG)))

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
