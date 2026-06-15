import os
import sqlite3
import datetime
import streamlit as st

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
        "overview": "Overview",
        "roadmap_hint": "You can add or remove roadmap cards.",
        "spots_hint": "Cultural spots and AR guide preview.",
        "cast_hint": "Create a mini audio session with QR flow.",
        "gov_hint": "Matched government support results.",
        "simulate_quiz": "Simulate mileage quiz success",
        "create_session": "Create cast session",
        "translate_text": "Translate sample text",
        "sample_text": "Welcome to Mamam Linker",
        "session_created": "Cast session created",
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
        "overview": "개요",
        "roadmap_hint": "로드맵 카드를 추가하거나 제거할 수 있습니다.",
        "spots_hint": "문화 스팟과 AR 안내 미리보기입니다.",
        "cast_hint": "QR 흐름이 포함된 미니 오디오 세션을 생성합니다.",
        "gov_hint": "매칭된 정부지원 결과를 확인합니다.",
        "simulate_quiz": "마일리지 퀴즈 성공 처리",
        "create_session": "발표장 세션 생성",
        "translate_text": "샘플 문장 번역",
        "sample_text": "마맘링커에 오신 것을 환영합니다.",
        "session_created": "발표장 세션 생성 완료",
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
        "overview": "Tổng quan",
        "roadmap_hint": "Bạn có thể thêm hoặc xóa thẻ lộ trình.",
        "spots_hint": "Xem trước điểm văn hóa và hướng dẫn AR.",
        "cast_hint": "Tạo phiên âm thanh mini với luồng QR.",
        "gov_hint": "Kết quả hỗ trợ chính phủ phù hợp.",
        "simulate_quiz": "Giả lập thành công câu đố mileage",
        "create_session": "Tạo phiên phát biểu",
        "translate_text": "Dịch câu mẫu",
        "sample_text": "Chào mừng bạn đến với Mamam Linker",
        "session_created": "Đã tạo phiên phát biểu",
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
        "overview": "概览",
        "roadmap_hint": "您可以添加或删除路线图卡片。",
        "spots_hint": "文化地点和 AR 指南预览。",
        "cast_hint": "创建带 QR 流程的迷你音频会话。",
        "gov_hint": "查看匹配的政府支持结果。",
        "simulate_quiz": "模拟里程答题成功",
        "create_session": "创建讲台会话",
        "translate_text": "翻译示例句",
        "sample_text": "欢迎来到 Mamam Linker",
        "session_created": "讲台会话已创建",
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
        "overview": "Overview",
        "roadmap_hint": "Maaari kang magdagdag o mag-alis ng roadmap cards.",
        "spots_hint": "Preview ng cultural spots at AR guide.",
        "cast_hint": "Gumawa ng mini audio session na may QR flow.",
        "gov_hint": "Mga tugmang government support results.",
        "simulate_quiz": "I-simulate ang mileage quiz success",
        "create_session": "Gumawa ng cast session",
        "translate_text": "I-translate ang sample text",
        "sample_text": "Maligayang pagdating sa Mamam Linker",
        "session_created": "Nagawa ang cast session",
    }
}

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.executescript("""
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
    """)

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
    return st.session_state.get("ui_lang", DEFAULT_LANG)

def set_lang_from_sidebar():
    st.session_state.ui_lang = st.sidebar.selectbox(
        "Language",
        list(SUPPORTED_LANGUAGES.keys()),
        format_func=lambda x: SUPPORTED_LANGUAGES[x],
        index=list(SUPPORTED_LANGUAGES.keys()).index(st.session_state.get("ui_lang", DEFAULT_LANG))
        if st.session_state.get("ui_lang", DEFAULT_LANG) in SUPPORTED_LANGUAGES else 0
    )

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

def load_child():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM children ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    child = dict(row)
    child["age_months"] = calculate_months(child["birth_date"])
    return child

def load_all(table, order="id ASC"):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table} ORDER BY {order}")
    rows = cur.fetchall()
    conn.close()
    return rows

def save_child(name, birth_date, nationality, language, region):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM children")
    cur.execute(
        "INSERT INTO children (name, birth_date, nationality, language, region, age_months) VALUES (?,?,?,?,?,?)",
        (name, birth_date, nationality, language, region, calculate_months(birth_date)),
    )
    conn.commit()
    conn.close()

def clear_child():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM children")
    conn.commit()
    conn.close()

def update_roadmap_active(item_id, active):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("UPDATE roadmap_cards SET active=? WHERE id=?", (active, item_id))
    conn.commit()
    conn.close()

def create_cast_session(host_name, profile_lang):
    code = datetime.datetime.now().strftime("CS%Y%m%d%H%M%S")
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO cast_sessions (session_code, host_name, profile_lang, status, attendee_count, created_at) VALUES (?,?,?,?,?,?)",
        (code, host_name, profile_lang, "live", 1, datetime.datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()
    return code

def set_translation_demo(lang):
    sample = UI_TEXT[lang]["sample_text"]
    translated = translate_google("Welcome to Mamam Linker", lang)
    if translated is None:
        translated = sample
    st.session_state.latest_translation = {
        "source": "Welcome to Mamam Linker",
        "translation": translated,
        "note": "Google Cloud Translation API will be used when credentials are configured."
    }

def get_labels(lang):
    return UI_TEXT[lang]

def main():
    st.set_page_config(page_title=APP_NAME, page_icon="👩‍👧", layout="centered")
    init_db()

    if "ui_lang" not in st.session_state:
        st.session_state.ui_lang = DEFAULT_LANG
    if "latest_translation" not in st.session_state:
        st.session_state.latest_translation = None
    if "latest_notice" not in st.session_state:
        st.session_state.latest_notice = None

    st.sidebar.title("Mamam Linker")
    set_lang_from_sidebar()
    lang = get_lang()
    labels = get_labels(lang)

    st.title(labels["title"])
    st.caption(labels["subtitle"])
    st.sidebar.info(labels["default_badge"])

    child = load_child()
    roadmap = load_all("roadmap_cards", "month ASC, id ASC")
    spots = load_all("cultural_spots", "id ASC")
    govs = load_all("gov_supports", "max_amount DESC, id ASC")
    cast_session = load_all("cast_sessions", "id DESC")
    cast_session = cast_session[0] if cast_session else None

    if st.session_state.latest_notice:
        st.success(st.session_state.latest_notice)

    tab1, tab2, tab3, tab4 = st.tabs([
        labels["profile"],
        labels["roadmap"],
        labels["spots"],
        labels["gov"],
    ])

    with tab1:
        st.subheader(labels["profile"])
        if child:
            cols = st.columns([1, 4, 1])
            with cols[0]:
                st.markdown(
                    f"""
                    <div style="width:64px;height:64px;border-radius:18px;
                    background:linear-gradient(135deg,#7c6cff,#35d2ff);
                    display:flex;align-items:center;justify-content:center;
                    color:#07111f;font-size:24px;font-weight:800;">{child['name'][:1].upper()}</div>
                    """,
                    unsafe_allow_html=True,
                )
            with cols[1]:
                st.markdown(f"**{child['name']} · {child['age_months']}m**")
                st.write(f"{child['region']} · {child['language']} · {child['nationality']}")
            with cols[2]:
                if st.button(labels["reset"], use_container_width=True):
                    clear_child()
                    st.session_state.latest_translation = None
                    st.session_state.latest_notice = None
                    st.rerun()
        else:
            with st.form("register_form"):
                c1, c2 = st.columns(2)
                with c1:
                    name = st.text_input(labels["child_name"])
                    birth_date = st.date_input(labels["birth_date"])
                with c2:
                    region = st.selectbox(labels["region"], ["Seoul", "Busan", "Incheon", "Gyeonggi"])
                    nationality = st.text_input(labels["nationality"], value="Korea")
                language = st.selectbox(
                    labels["language"],
                    list(SUPPORTED_LANGUAGES.keys()),
                    format_func=lambda x: SUPPORTED_LANGUAGES[x],
                    index=0,
                )
                submit = st.form_submit_button(labels["register"])
                if submit:
                    save_child(name, str(birth_date), nationality, language, region)
                    st.session_state.ui_lang = lang
                    st.session_state.latest_notice = None
                    st.rerun()

        st.write(labels["no_child"] if not child else "")

    with tab2:
        st.subheader(labels["roadmap"])
        st.caption(labels["roadmap_hint"])
        for item in roadmap:
            with st.container(border=True):
                st.markdown(f"**[{item['month']}m] {item['title']}**")
                st.write(item["description"])
                c1, c2 = st.columns(2)
                with c1:
                    if item["active"]:
                        if st.button(f"− {labels['remove']}", key=f"remove_{item['id']}", use_container_width=True):
                            update_roadmap_active(item["id"], 0)
                            st.rerun()
                    else:
                        if st.button(f"+ {labels['add']}", key=f"add_{item['id']}", use_container_width=True):
                            update_roadmap_active(item["id"], 1)
                            st.rerun()
                with c2:
                    st.write(item["category"])

        if st.button("Google Translate Demo", use_container_width=True):
            set_translation_demo(lang)
            st.rerun()

        if st.session_state.latest_translation:
            st.info(f"{labels['translation']}: {st.session_state.latest_translation['translation']}")

    with tab3:
        st.subheader(labels["spots"])
        st.caption(labels["spots_hint"])
        for s in spots:
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(f"**{s['name']}**")
                    st.write(f"{s['region']} · radius {s['radius_m']}m")
                    st.caption(s["audio_script"])
                with c2:
                    if st.button("AR", key=f"spot_{s['id']}", use_container_width=True):
                        st.session_state.latest_notice = f"{s['name']} quiz answer: {s['quiz_answer']} (+{s['mileage']} mileage)"
                        st.rerun()

    with tab4:
        st.subheader(labels["gov"])
        st.caption(labels["gov_hint"])
        if child:
            for g in govs:
                with st.container(border=True):
                    st.markdown(f"**{g['title']}**")
                    st.write(g["description"])
                    st.write(f"**Documents:** {g['documents']}")
                    st.write(f"**Max amount:** {g['max_amount']} KRW")
                    st.write(f"**Hotline:** {g['hotline']}")
        else:
            st.write(labels["no_gov"])

    st.divider()
    st.subheader(labels["cast"])
    st.caption(labels["cast_hint"])

    c1, c2 = st.columns([3, 2])
    with c1:
        host_name = st.text_input("Guide name", key="guide_name")
    with c2:
        profile_lang = st.selectbox(
            labels["language"],
            list(SUPPORTED_LANGUAGES.keys()),
            format_func=lambda x: SUPPORTED_LANGUAGES[x],
            key="cast_lang"
        )

    if st.button(labels["create_session"], use_container_width=True):
        if host_name.strip():
            code = create_cast_session(host_name, profile_lang)
            st.session_state.latest_notice = f"{labels['session_created']}: {code}"
            st.rerun()

    if cast_session:
        st.success(f"Session {cast_session['session_code']} · {cast_session['attendee_count']} attendees")

    st.divider()
    st.subheader(labels["translation_demo"])
    if st.button(labels["translate_text"], use_container_width=True):
        set_translation_demo(lang)
        st.rerun()

    if st.session_state.latest_translation:
        st.markdown(
            f"""
            **{st.session_state.latest_translation['source']}**
            
            {st.session_state.latest_translation['translation']}
            
            _{st.session_state.latest_translation['note']}_
            """
        )

    st.divider()
    st.caption(f"{APP_NAME} · {('Google Translate available' if GOOGLE_TRANSLATE_AVAILABLE else 'Google Translate unavailable')}")

if __name__ == "__main__":
    main()
