import datetime
import io
import json
import sqlite3
from flask import Flask, jsonify, redirect, render_template_string, request, url_for, make_response

app = Flask(__name__)
DB_FILE = "mother_all.db"

# ==========================================
# 1. 데이터베이스 초기화 및 확장 아키텍처 구축
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # [가족 데이터] 아이 및 부모 정보 테이블 (지역 정보 'region' 추가)
    c.execute('''CREATE TABLE IF NOT EXISTS children (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    birth_date TEXT NOT NULL,
                    nationality TEXT NOT NULL,
                    language TEXT NOT NULL,
                    region TEXT NOT NULL,
                    age_months INTEGER DEFAULT 0
                 )''')

    # [문화/건강/지원 데이터] 초개인화 타임라인 마스터 데이터
    c.execute('''CREATE TABLE IF NOT EXISTS master_timeline (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_month INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT NOT NULL,
                    source_asset TEXT NOT NULL
                 )''')

    # [문화 콘텐츠] AI 의역 사전 데이터
    c.execute('''CREATE TABLE IF NOT EXISTS cultural_dictionary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    idiom TEXT NOT NULL,
                    target_lang TEXT NOT NULL,
                    translation TEXT NOT NULL,
                    explanation TEXT NOT NULL,
                    cultural_tip TEXT NOT NULL
                 )''')

    # [육아 지원 정보] 지자체 육아종합지원센터 데이터
    c.execute('''CREATE TABLE IF NOT EXISTS support_centers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    region TEXT NOT NULL,
                    facility_name TEXT NOT NULL,
                    toy_inventory INTEGER NOT NULL,
                    playroom_status TEXT NOT NULL
                 )''')

    # [신규 추가: 커뮤니티] 문화 체험 중심 동일 언어 사용자 매칭 및 모임 테이블
    c.execute('''CREATE TABLE IF NOT EXISTS culture_groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_name TEXT NOT NULL,
                    region TEXT NOT NULL,
                    target_language TEXT NOT NULL,
                    host_name TEXT NOT NULL,
                    member_count INTEGER DEFAULT 1,
                    description TEXT NOT NULL
                 )''')

    # [신규 추가: 예약] 지자체 인프라 예약 내역 테이블
    c.execute('''CREATE TABLE IF NOT EXISTS reservations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    child_name TEXT NOT NULL,
                    facility_name TEXT NOT NULL,
                    reserved_at TEXT NOT NULL
                 )''')

    # 마스터 데이터 초기 삽입 (최초 1회 실행)
    c.execute("SELECT count(*) FROM master_timeline")
    if c.fetchone()[0] == 0:
        # ① 생애주기별 타임라인 데이터
        timeline_data = [
            (0, "BCG(피내용) 예방접종 안내", "Health", "생후 4주 이내에 접종해야 하는 필수 백신입니다. 보건소 정보를 확인하세요.", "보건복지부 가이드라인 v1.2"),
            (3, "우리 아이 삼칠일(21일)과 백일 의례", "Culture", "한국에서는 백일날 백설기를 이웃과 나누며 아이의 장수와 건강을 기원합니다.", "국립민속박물관 일생의례 데이터집"),
            (6, "B형간염 3차 필수 예방접종 및 영유아 검진", "Health", "생후 6개월은 면역력이 떨어지는 시기입니다. 발달 표준 검진을 잊지 마세요.", "육아정책연구소 발달 표준 가이드"),
            (6, "가족센터 다문화 멘토링 프로그램 신청", "Support", "선배 이주여성 멘토와 연계하여 한국 육아 문화 적응 및 정서적 안정을 지원합니다.", "여성가족부 가족센터 지원 데이터"),
            (12, "전통 돌잔치와 돌잡이 문화 체험", "Culture", "첫 번째 생일인 '돌'에는 돌잡이를 통해 아이의 미래를 축복하고 점쳐봅니다.", "국립민속박물관 풍속 아카이브")
        ]
        c.executemany("INSERT INTO master_timeline (target_month, title, category, description, source_asset) VALUES (?, ?, ?, ?, ?)", timeline_data)

        # ⑤ AI 문화 맥락 의역 데이터
        dict_data = [
            ("등센서", "vi", "Cảm biến lưng (Nhạy cảm khi đặt nằm)", "Từ lóng mô tả việc em bé khóc ngay lập tức khi vừa được đặt lưng xuống giường.", "Mẹo K-Caring: Người Hàn thường dùng gối ôm hình chữ U để tạo cảm giác an toàn như đang được bế."),
            ("돌치레", "vi", "Sốt mọc răng / Sốt đầu đời (Thôi nôi)", "Tình trạng trẻ nhỏ đột ngột bị sốt hoặc ốm nhẹ vào khoảng thời gian sinh nhật đầu tiên (1 tuổi).", "Mẹo K-Caring: Đây là hiện tượng sinh lý bình thường khi kháng thể từ mẹ giảm đi, đừng quá lo lắng."),
            ("우쭈쭈", "vi", "Âu yếm / Cưng nựng hành vi", "Âm thanh dỗ dành hoặc thể hiện tình yêu thương vô bờ bến với trẻ nhỏ.", "Mẹo K-Caring: Tương đương với cách nói cưng nựng trẻ em tại Việt Nam.")
        ]
        c.executemany("INSERT INTO cultural_dictionary (idiom, target_lang, translation, explanation, cultural_tip) VALUES (?, ?, ?, ?, ?)", dict_data)

        # ④ 전국 지자체 API 연동 가상 데이터
        center_data = [
            ("서울시 마포구", "마포 영유아 장난감 도서관", 14, "예약 가능"),
            ("부산시 해운대구", "해운대 놀이체험실", 3, "마감 임박"),
            ("인천시 부평구", "부평 육아종합지원센터", 25, "예약 가능")
        ]
        c.executemany("INSERT INTO support_centers (region, facility_name, toy_inventory, playroom_status) VALUES (?, ?, ?, ?)", center_data)

        # [신규 데이터] 문화포털 영유아 동선 기반 가상 멘토링/문화 체험 모임
        group_data = [
            ("국립민속박물관 다문화 백일 문화 체험", "서울시 마포구", "vi", "흐엉 (베트남)", 3, "같은 베트남 엄마들끼리 모여서 한국 백일 떡 만들기 체험 같이 가요!"),
            ("해운대 육아종합지원센터 유아 놀이방 모임", "부산시 해운대구", "vi", "마이티 (베트남)", 2, "6개월 전후 아기 데리고 같이 수다 떨며 정보 공유해요.")
        ]
        c.executemany("INSERT INTO culture_groups (event_name, region, target_language, host_name, member_count, description) VALUES (?, ?, ?, ?, ?, ?)", group_data)

    conn.commit()
    conn.close()

# ==========================================
# 2. 헬퍼 함수: 실시간 월령 연산
# ==========================================
def calculate_months(birth_date_str):
    try:
        birth_date = datetime.datetime.strptime(birth_date_str, "%Y-%m-%d").date()
        today = datetime.date.today()
        return (today.year - birth_date.year) * 12 + today.month - birth_date.month - (1 if today.day < birth_date.day else 0)
    except Exception:
        return 0

# ==========================================
# 3. 템플릿 엔지니어링 (현대적 모바일 라이브 앱 디자인 UI)
# ==========================================
HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>모아 (Mother-All) - K-컬처 육아 내비게이션</title>
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
        
        .app-frame {
            width: 100%; max-width: 430px; background-color: var(--gray-bg);
            min-height: 100vh; position: relative; padding-bottom: 90px;
            box-shadow: 0 0 30px rgba(0,0,0,0.15); display: flex; flex-direction: column;
        }
        
        header {
            background: linear-gradient(135deg, var(--secondary), var(--primary));
            padding: 35px 24px 25px; border-radius: 0 0 32px 32px; color: white;
        }
        header .brand-zone { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
        header .brand-zone h2 { margin: 0; font-size: 20px; font-weight: 800; letter-spacing: -0.5px; }
        header .brand-zone .badge { background: rgba(255,255,255,0.2); padding: 4px 10px; border-radius: 12px; font-size: 11px; }
        header h1 { margin: 0; font-size: 24px; font-weight: 700; line-height: 1.3; }
        
        .container { padding: 20px; flex: 1; }
        h3 { font-size: 18px; color: var(--dark); margin: 24px 0 14px; display: flex; align-items: center; gap: 8px; }
        
        .app-card {
            background: white; border-radius: 24px; padding: 20px;
            margin-bottom: 20px; box-shadow: 0 8px 16px rgba(0,0,0,0.02);
            border: 1px solid rgba(0,0,0,0.03);
        }
        
        .form-group { margin-bottom: 16px; }
        .form-group label { display: block; font-size: 13px; font-weight: 600; color: #64748B; margin-bottom: 6px; }
        .form-control {
            width: 100%; padding: 14px; border-radius: 14px; border: 1.5px solid #E2E8F0;
            font-size: 15px; background: #F8FAFC; transition: 0.2s;
        }
        .form-control:focus { outline: none; border-color: var(--primary); background: white; }
        
        .btn-submit {
            width: 100%; background: var(--dark); color: white; border: none; padding: 15px;
            border-radius: 14px; font-size: 16px; font-weight: 700; cursor: pointer; transition: 0.2s;
        }
        .btn-submit:hover { background: var(--primary); }
        .btn-sm { padding: 6px 12px; border-radius: 8px; font-size: 11px; font-weight: 700; border: none; cursor: pointer; color: white; }
        
        .baby-profile {
            display: flex; align-items: center; gap: 16px; background: white;
            padding: 16px; border-radius: 20px; border-left: 5px solid var(--primary);
        }
        .baby-avatar { width: 50px; height: 50px; background: var(--primary-light); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: var(--primary); font-size: 22px; }
        .baby-info h4 { margin: 0; font-size: 16px; color: var(--dark); }
        .baby-info p { margin: 4px 0 0; font-size: 13px; color: #64748B; }
        
        /* 초개인화 타임라인 */
        .timeline-stream { position: relative; padding-left: 20px; border-left: 2px dashed #E2E8F0; margin-left: 10px; }
        .timeline-node { position: relative; margin-bottom: 24px; }
        .timeline-icon {
            position: absolute; left: -31px; top: 2px; width: 20px; height: 20px;
            border-radius: 50%; background: white; border: 3px solid var(--primary);
        }
        .timeline-node.health .timeline-icon { border-color: var(--secondary); }
        .timeline-node.support .timeline-icon { border-color: var(--success); }
        .timeline-body { background: white; padding: 16px; border-radius: 18px; }
        .timeline-tag { font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 8px; display: inline-block; margin-bottom: 8px; }
        .timeline-tag.culture { background: var(--primary-light); color: var(--primary); }
        .timeline-tag.health { background: var(--secondary-light); color: var(--secondary); }
        .timeline-tag.support { background: #E6F9F5; color: var(--success); }
        .timeline-title { font-size: 15px; font-weight: 700; color: var(--dark); margin: 0 0 6px; }
        .timeline-text { font-size: 13px; color: #4A5568; margin: 0 0 8px; line-height: 1.4; }
        
        /* 동일 언어 매칭 커뮤니티 디자인 스택 */
        .match-card { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 16px; padding: 14px; margin-bottom: 12px; }
        .match-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
        .match-lang-tag { background: #E2E8F0; color: var(--dark); font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 6px; }
        .match-title { font-size: 14px; font-weight: 700; color: var(--dark); margin-bottom: 4px; }
        .match-desc { font-size: 12px; color: #4A5568; line-height: 1.4; margin-bottom: 10px; }
        .match-footer { display: flex; justify-content: space-between; align-items: center; font-size: 11px; color: #94A3B8; }
        
        /* AI 의역 및 서류 도우미 */
        .dict-result-box { background: #F1F2F6; border-radius: 16px; padding: 16px; margin-top: 14px; border-left: 4px solid var(--secondary); }
        .dict-title { font-size: 15px; font-weight: 700; color: var(--secondary); margin-bottom: 4px; }
        .dict-trans { font-size: 13px; font-weight: 600; color: var(--dark); margin-bottom: 6px; }
        .dict-desc { font-size: 12px; color: #4E5968; margin-bottom: 8px; line-height: 1.4; }
        .dict-tip { font-size: 11px; color: #FF7A94; font-weight: 600; background: white; padding: 8px; border-radius: 8px; }
        .api-badge { font-size: 11px; background: #EDF2F7; color: #4A5568; padding: 4px 8px; border-radius: 6px; }
        .doc-preview { background: #FAF9F6; border: 1px dashed #D3D3D3; border-radius: 12px; padding: 16px; font-family: monospace; font-size: 11px; line-height: 1.4; }
        
        .bottom-nav {
            position: fixed; bottom: 0; width: 100%; max-width: 430px; height: 74px;
            background: rgba(255, 255, 255, 0.94); backdrop-filter: blur(12px);
            display: flex; justify-content: space-around; align-items: center;
            border-top: 1px solid rgba(0,0,0,0.06); border-radius: 24px 24px 0 0; z-index: 100;
        }
        .nav-item { text-decoration: none; color: #94A3B8; display: flex; flex-direction: column; align-items: center; gap: 4px; font-size: 11px; font-weight: 600; }
        .nav-item.active { color: var(--primary); }
        .nav-item i { font-size: 20px; }
    </style>
</head>
<body>

    <div class="app-frame">
        <header>
            <div class="brand-zone">
                <h2>MOA (모아)</h2>
                <div class="badge"><i class="fa-solid fa-earth-asia"></i> Live Network v1.2</div>
            </div>
            <h1>K-컬처 육아<br>통합 내비게이션</h1>
        </header>

        <div class="container">
            
            <h3><i class="fa-solid fa-baby"></i> 자녀 정보 및 AI 맞춤화 설정</h3>
            <div class="app-card">
                {% if child %}
                <div class="baby-profile">
                    <div class="baby-avatar"><i class="fa-solid fa-child-reaching"></i></div>
                    <div class="baby-info">
                        <h4>{{ child.name }} 아기 ({{ child.nationality }})</h4>
                        <p>지역: <strong>{{ child.region }}</strong> | <strong>{{ child.age_months }}개월차</strong></p>
                        <p style="font-size:11px; margin-top:2px;">설정 언어팩: <span style="color:var(--secondary); font-weight:700;">{{ child.language }}</span></p>
                    </div>
                </div>
                <div style="margin-top:12px; text-align:right;">
                    <a href="{{ url_for('clear_child') }}" style="font-size:12px; color:#94A3B8; text-decoration:none;"><i class="fa-solid fa-rotate-left"></i> 재설정하기</a>
                </div>
                {% else %}
                <form action="/register" method="POST">
                    <div class="form-group">
                        <label>아이 이름 (또는 태명)</label>
                        <input type="text" name="name" class="form-control" placeholder="예: 사랑이" required>
                    </div>
                    <div class="form-group">
                        <label>출생일</label>
                        <input type="date" name="birth_date" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label>거주 지역 (지자체 API 동선 연동)</label>
                        <select name="region" class="form-control">
                            <option value="서울시 마포구">서울시 마포구</option>
                            <option value="부산시 해운대구">부산시 해운대구</option>
                            <option value="인천시 부평구">인천시 부평구</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>어머니 국적 배경</label>
                        <select name="nationality" class="form-control">
                            <option value="Vietnam">베트남 (Vietnam)</option>
                            <option value="China">중국 (China)</option>
                            <option value="Philippines">필리핀 (Philippines)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>사용 언어 선택</label>
                        <select name="language" class="form-control">
                            <option value="vi">Tiếng Việt (베트남어)</option>
                            <option value="zh">中文 (중국어)</option>
                            <option value="ko">한국어 (Korean)</option>
                        </select>
                    </div>
                    <button type="submit" class="btn-submit"><i class="fa-solid fa-heart"></i> 맞춤형 육아 에코시스템 가동</button>
                </form>
                {% endif %}
            </div>

            <h3><i class="fa-solid fa-people-roof"></i> 주변 동일 언어 맘 소통 네트워크</h3>
            <div class="app-card">
                <p style="font-size:13px; color:#64748B; margin-top:0;">거주 지역 내에서 동일한 모국어를 사용하며 한국 문화 체험 및 육아 인프라를 이용하는 이웃과 연결해 드립니다.</p>
                
                {% if child %}
                    <div style="margin-bottom: 12px; background: #EEECFB; padding: 10px; border-radius: 10px; font-size: 12px; color: var(--secondary); font-weight: bold;">
                        <i class="fa-solid fa-bullseye"></i> 추천 타겟 매칭 팩트: [{{ child.region }}] + [언어: {{ child.language }}]
                    </div>
                    
                    {% if matching_groups %}
                        {% for group in matching_groups %}
                        <div class="match-card">
                            <div class="match-header">
                                <span class="match-lang-tag"><i class="fa-solid fa-comments"></i> {{ group.target_language }} 전용방</span>
                                <span style="font-size:11px; color:var(--success); font-weight:700;"><i class="fa-solid fa-user-group"></i> {{ group.member_count }}명 참여 중</span>
                            </div>
                            <div class="match-title">{{ group.event_name }}</div>
                            <div class="match-desc">{{ group.description }}</div>
                            <div class="match-footer">
                                <span>방장: {{ group.host_name }} 님</span>
                                <form action="/join-group/{{ group.id }}" method="POST" style="margin:0;">
                                    <button type="submit" class="btn-sm" style="background:var(--secondary);"><i class="fa-solid fa-door-open"></i> 단톡방 참여하기</button>
                                </form>
                            </div>
                        </div>
                        {% endfor %}
                    {% else %}
                        <p style="font-size:12px; color:#A0AEC0; text-align:center; padding:10px 0;">현재 해당 지역 및 언어에 개설된 매칭방이 없습니다. 아래에서 방을 직접 개설해 보세요!</p>
                    {% endif %}
                    
                    <hr style="border:0; border-top:1px solid #E2E8F0; margin:16px 0;">
                    <form action="/create-group" method="POST" style="background:#F8FAFC; padding:12px; border-radius:14px;">
                        <div style="font-size:13px; font-weight:700; color:var(--dark); margin-bottom:8px;"><i class="fa-solid fa-plus"></i> 문화 체험 같이 갈 멤버 모집하기</div>
                        <input type="text" name="event_name" class="form-control" placeholder="체험 테마 (예: 마포 문화센터 돌상 체험)" required style="padding:8px; font-size:12px; margin-bottom:8px;">
                        <input type="text" name="description" class="form-control" placeholder="소개글을 적어주세요." required style="padding:8px; font-size:12px; margin-bottom:8px;">
                        <button type="submit" class="btn-sm" style="background:var(--primary); width:100%; padding:8px;"><i class="fa-solid fa-users"></i> 매칭 채널 개설하기</button>
                    </form>
                {% else %}
                    <p style="font-size:12px; color:#A0AEC0; text-align:center; padding:15px 0;">자녀 정보를 입력하시면 소통 가능한 매칭 리스트가 필터링됩니다.</p>
                {% endif %}
            </div>

            <h3><i class="fa-solid fa-hourglass-half"></i> 월령별 맞춤형 융합 타임라인</h3>
            <div class="app-card">
                {% if timeline_events %}
                <div class="timeline-stream">
                    {% for event in timeline_events %}
                    <div class="timeline-node {{ event.category|lower }}">
                        <div class="timeline-icon"></div>
                        <div class="timeline-body">
                            <span class="timeline-tag {{ event.category|lower }}">
                                {% if event.category == 'Culture' %}한국 전통 의례 (국립민속박물관)
                                {% elif event.category == 'Health' %}보건복지부 필수 정보
                                {% else %}여가부 다문화 케어{% endif %}
                            </span>
                            <div class="timeline-title">[{{ event.target_month }}개월] {{ event.title }}</div>
                            <div class="timeline-text">{{ event.description }}</div>
                            <div class="timeline-source"><i class="fa-solid fa-square-poll-horizontal"></i> 출처 자산: {{ event.source_asset }}</div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% else %}
                <p style="font-size:12px; color:#64748B; text-align:center; padding:15px 0;">자녀 정보 연동 시 초개인화 타임라인 빌드가 시작됩니다.</p>
                {% endif %}
            </div>

            <h3><i class="fa-solid fa-wand-magic-sparkles"></i> AI K-육아 관용구 의역기</h3>
            <div class="app-card">
                <form action="/translate" method="POST" style="display:flex; gap:8px;">
                    <input type="text" name="idiom" class="form-control" placeholder="예: 등센서, 돌치레, 우쭈쭈" required style="margin:0;">
                    <button type="submit" class="btn-submit" style="width:auto; padding:0 20px; margin:0;"><i class="fa-solid fa-magnifying-glass"></i></button>
                </form>

                {% if dict_result %}
                <div class="dict-result-box">
                    <div class="dict-title"><i class="fa-solid fa-comment-dots"></i> 한국 표현: {{ dict_result.idiom }}</div>
                    <div class="dict-trans"><i class="fa-solid fa-language"></i> 모국어 의역: {{ dict_result.translation }}</div>
                    <div class="dict-desc">{{ dict_result.explanation }}</div>
                    <div class="dict-tip"><i class="fa-solid fa-lightbulb"></i> Care Tip: {{ dict_result.cultural_tip }}</div>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; background:#FFF9E6; border:1px solid #FFEAA7; border-radius:14px; padding:12px 16px; margin-top:10px;">
                    <span style="font-size:12px; color:#B33771; font-weight:700;"><i class="fa-solid fa-cart-shopping"></i> '{{ dict_result.idiom }}' 추천 육아 필수 템</span>
                    <button class="btn-sm" style="background:#F1C40F;" onclick="alert('커머스 중개 수수료 확보 파트너십 몰로 연결됩니다.')">구매하기</button>
                </div>
                {% endif %}
            </div>

            <h3><i class="fa-solid fa-map-location-dot"></i> 전국 지자체 실시간 인프라 현황</h3>
            <div class="app-card">
                {% for center in support_centers %}
                <div style="padding:14px 0; border-bottom:1px solid #EDF2F7; display:flex; justify-content:space-between; align-items:center; font-size:13px;">
                    <div style="flex:1;">
                        <strong style="color:var(--dark);">{{ center.facility_name }}</strong>
                        <div style="font-size:11px; color:#A0AEC0; margin-top:2px;">위치: {{ center.region }}</div>
                    </div>
                    <div style="text-align:right; display:flex; flex-direction:column; gap:6px;">
                        <div>
                            <span class="api-badge">장난감: {{ center.toy_inventory }}개</span>
                            <span class="api-badge" style="background:#E6F9F5; color:#00B894;">{{ center.playroom_status }}</span>
                        </div>
                        <form action="/reserve-facility/{{ center.id }}" method="POST" style="margin:0;">
                            <button type="submit" class="btn-sm" style="background:var(--secondary); width:100%;">원클릭 예약</button>
                        </form>
                    </div>
                </div>
                {% endfor %}
            </div>

            <h3><i class="fa-solid fa-file-signature"></i> 원클릭 행정 서류 자동 도우미</h3>
            <div class="app-card">
                {% if child %}
                <div class="doc-preview">
                    [가족센터 다문화 육아 지원 바우처 신청서]<br>
                    -------------------------------------<br>
                    ■ 신청인(모): {{ child.name }}의 모친 (국적: {{ child.nationality }})<br>
                    ■ 대상자녀: {{ child.name }} (거주지: {{ child.region }})<br>
                    ■ 아기 연령: 생후 {{ child.age_months }}개월 (만 {{ child.age_months // 12 }}세)<br>
                    -------------------------------------<br>
                    [여성가족부 행정 양식 연동 완료]
                </div>
                <div style="display:flex; gap:8px; margin-top:12px;">
                    <a href="/download-document" class="btn-submit" style="background:#64748B; text-align:center; text-decoration:none; font-size:14px; padding:12px; flex:1;">
                        <i class="fa-solid fa-file-arrow-down"></i> 서류 다운로드 (.txt)
                    </a>
                    <button class="btn-submit" style="background:var(--secondary); font-size:14px; padding:12px; flex:1;" onclick="alert('행정 시스템(B2G)망으로 원클릭 전자 접수되었습니다.')">
                        <i class="fa-solid fa-paper-plane"></i> 즉시 전산제출
                    </button>
                </div>
                {% else %}
                <p style="font-size:12px; color:#A0AEC0; text-align:center; padding:10px 0;">자녀 정보를 입력하시면 서류 초안이 연동 빌드됩니다.</p>
                {% endif %}
            </div>

        </div>

        <nav class="bottom-nav">
            <a href="/" class="nav-item active"><i class="fa-solid fa-house"></i><span>홈</span></a>
            <a href="/#translate" class="nav-item"><i class="fa-solid fa-language"></i><span>의역기</span></a>
            <a href="/#support" class="nav-item"><i class="fa-solid fa-users"></i><span>소통 커뮤니티</span></a>
            <a href="/#document" class="nav-item"><i class="fa-solid fa-file-shield"></i><span>서류센터</span></a>
        </nav>
    </div>

</body>
</html>
"""

# ==========================================
# 4. 비즈니스 컨트롤러 및 라우팅 로직
# ==========================================
@app.route("/")
def main_dashboard():
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

        # 초개인화 데이터 융합 타임라인 연산
        c.execute("SELECT * FROM master_timeline WHERE target_month >= ? ORDER BY target_month ASC LIMIT 3", (current_months,))
        timeline_events = c.fetchall()

        # [핵심 확장 핵심 기능] 동일 지역 및 동일 소통 언어를 사용하는 모임 필터링 바인딩
        c.execute("SELECT * FROM culture_groups WHERE region = ? AND target_language = ? ORDER BY id DESC", (child["region"], child["language"]))
        matching_groups = c.fetchall()

    c.execute("SELECT * FROM support_centers")
    centers = c.fetchall()

    dict_result = getattr(app, 'latest_dict_result', None)
    conn.close()

    return render_template_string(HTML_LAYOUT, child=child, timeline_events=timeline_events, support_centers=centers, dict_result=dict_result, matching_groups=matching_groups)

@app.route("/register", methods=["POST"])
def register_child():
    name = request.form.get("name")
    birth_date = request.form.get("birth_date")
    nationality = request.form.get("nationality")
    language = request.form.get("language")
    region = request.form.get("region")

    initial_months = calculate_months(birth_date)

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM children")
    c.execute("INSERT INTO children (name, birth_date, nationality, language, region, age_months) VALUES (?, ?, ?, ?, ?, ?)",
              (name, birth_date, nationality, language, region, initial_months))
    conn.commit()
    conn.close()

    if hasattr(app, 'latest_dict_result'): delattr(app, 'latest_dict_result')
    return redirect(url_for("main_dashboard"))

# [신규 라우터] 사용자가 직접 동네 문화체험 커뮤니티 모임을 개설하는 기능
@app.route("/create-group", methods=["POST"])
def create_group():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("SELECT language, region, name FROM children ORDER BY id DESC LIMIT 1")
    child = c.fetchone()
    
    if child:
        event_name = request.form.get("event_name")
        description = request.form.get("description")
        
        c.execute("INSERT INTO culture_groups (event_name, region, target_language, host_name, member_count, description) VALUES (?, ?, ?, ?, 1, ?)",
                  (event_name, child["region"], child["language"], f"{child['name']} 맘", description))
        conn.commit()
    conn.close()
    return redirect(url_for("main_dashboard"))

# [신규 라우터] 소통 그룹 참여 액션 처리
@app.route("/join-group/<int:group_id>", methods=["POST"])
def join_group(group_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE culture_groups SET member_count = member_count + 1 WHERE id = ?", (group_id,))
    conn.commit()
    conn.close()
    return "<script>alert('참여가 완료되었습니다! 소통 타운 라운지로 입장합니다.'); location.href='/';</script>"

@app.route("/translate", methods=["POST"])
def translate_idiom():
    idiom_keyword = request.form.get("idiom", "").strip()
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT language FROM children ORDER BY id DESC LIMIT 1")
    user_lang_row = c.fetchone()
    target_lang = user_lang_row["language"] if user_lang_row else "vi"

    c.execute("SELECT * FROM cultural_dictionary WHERE idiom LIKE ? AND target_lang = ?", (f"%{idiom_keyword}%", target_lang))
    res = c.fetchone()
    conn.close()

    if res:
        app.latest_dict_result = {"idiom": res["idiom"], "translation": res["translation"], "explanation": res["explanation"], "cultural_tip": res["cultural_tip"]}
    else:
        app.latest_dict_result = {
            "idiom": idiom_keyword,
            "translation": "언어팩 조율 중 (In-Context 빌드 대상)",
            "explanation": f"한국식 특수 관용구 '{idiom_keyword}'를 분석하고 있습니다.",
            "cultural_tip": "매칭된 동네 커뮤니티 전용 선배 멘토 라인에 물어보시면 더욱 상세히 답변받으실 수 있습니다."
        }
    return redirect(url_for("main_dashboard"))

@app.route("/reserve-facility/<int:facility_id>", methods=["POST"])
def reserve_facility(facility_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT facility_name, toy_inventory FROM support_centers WHERE id = ?", (facility_id,))
    facility = c.fetchone()

    if not facility or facility[1] <= 0:
        conn.close()
        return "<script>alert('예약 가능한 재고가 존재하지 않습니다.'); history.back();</script>"

    c.execute("SELECT name FROM children ORDER BY id DESC LIMIT 1")
    child = c.fetchone()
    child_name = child[0] if child else "다문화 가구"

    c.execute("UPDATE support_centers SET toy_inventory = toy_inventory - 1 WHERE id = ?", (facility_id,))
    c.execute("INSERT INTO reservations (child_name, facility_name, reserved_at) VALUES (?, ?, ?)",
              (child_name, facility[0], datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()
    return f"<script>alert('[{facility[0]}] 인프라 연동 예약 완료!'); location.href='/';</script>"

@app.route("/download-document", methods=["GET"])
def download_document():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM children ORDER BY id DESC LIMIT 1")
    child = c.fetchone()
    conn.close()

    if not child: return "<script>alert('매핑 데이터가 없습니다.'); history.back();</script>"
    current_months = calculate_months(child["birth_date"])

    doc_content = f"""==================================================
[여성가족부 소관 다문화 지원망] 육아 서비스 통합 바우처 신청서
==================================================
1. 가구 기본 정보
 - 대상 모친 국적: {child['nationality']}
 - 소통 선호 언어: {child['language']}
 - 거주 자치 지자체: {child['region']}

2. 영유아 대상자
 - 아동 성명/태명: {child['name']}
 - 생년월일: {child['birth_date']} (생후 {current_months}개월 차 진입)

3. 플랫폼 융합 연계 원클릭 확인 사항
 - 지역 문화행사 연계 멘토링 매칭 신청 포함
 - 지자체 인프라(장난감 및 돌상 체험) 우선권 동시 확보 요구됨

--------------------------------------------------
접수 일시: {datetime.date.today().strftime('%Y년 %m월 %d일')}
여성가족부 가족센터 및 지역 자치 민원 행정망 전산 연동용
==================================================
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
    if hasattr(app, 'latest_dict_result'): delattr(app, 'latest_dict_result')
    return redirect(url_for("main_dashboard"))

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
