import datetime
import json
import sqlite3
from flask import Flask, jsonify, redirect, render_template_string, request, url_for

app = Flask(__name__)
DB_FILE = "mother_all.db"


# ==========================================
# 1. 데이터베이스 초기화 및 아키텍처 구축
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # [가족 데이터] 아이 정보 테이블
    c.execute(
        """CREATE TABLE IF NOT EXISTS children (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    birth_date TEXT NOT NULL,
                    nationality TEXT NOT NULL,
                    language TEXT NOT NULL,
                    age_months INTEGER DEFAULT 0
                 )"""
    )

    # [문화/건강/지원 데이터] 초개인화 타임라인 마스터 데이터
    c.execute(
        """CREATE TABLE IF NOT EXISTS master_timeline (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_month INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT NOT NULL,
                    source_asset TEXT NOT NULL
                 )"""
    )

    # [문화 콘텐츠] AI 의역 사전 데이터
    c.execute(
        """CREATE TABLE IF NOT EXISTS cultural_dictionary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    idiom TEXT NOT NULL,
                    target_lang TEXT NOT NULL,
                    translation TEXT NOT NULL,
                    explanation TEXT NOT NULL,
                    cultural_tip TEXT NOT NULL
                 )"""
    )

    # [육아 지원 정보] 지자체 육아종합지원센터 시뮬레이션 데이터
    c.execute(
        """CREATE TABLE IF NOT EXISTS support_centers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    region TEXT NOT NULL,
                    facility_name TEXT NOT NULL,
                    toy_inventory INTEGER NOT NULL,
                    playroom_status TEXT NOT NULL
                 )"""
    )

    # 마스터 데이터 초기 삽입 (최초 1회 실행)
    c.execute("SELECT count(*) FROM master_timeline")
    if c.fetchone()[0] == 0:
        # ① 국립민속박물관/보건복지부 기반 생애주기별 타임라인 스택
        timeline_data = [
            (
                0,
                "BCG(피내용) 예방접종 안내",
                "Health",
                "생후 4주 이내에 접종해야 하는 필수 백신입니다. 보건소 정보를 확인하세요.",
                "보건복지부 가이드라인 v1.2",
            ),
            (
                3,
                "우리 아이 삼칠일(21일)과 백일 의례",
                "Culture",
                "한국에서는 삼칠일에는 수수경단을, 백일에는 백설기를 이웃과 나누며 아이의 장수와 건강을 기원합니다.",
                "국립민속박물관 일생의례 데이터집",
            ),
            (
                6,
                "B형간염 3차 필수 예방접종 및 영유아 검진",
                "Health",
                "생후 6개월은 면역력이 떨어지는 시기입니다. 3차 접종과 발달 표준 검진을 잊지 마세요.",
                "육아정책연구소 발달 표준 가이드",
            ),
            (
                6,
                "가족센터 다문화 멘토링 프로그램 신청",
                "Support",
                "선배 이주여성 멘토와 연계하여 한국 육아 문화 적응 및 정서적 안정을 지원합니다.",
                "여성가족부 가족센터 지원 데이터",
            ),
            (
                12,
                "전통 돌잔치와 돌잡이 문화 체험",
                "Culture",
                "첫 번째 생일인 '돌'에는 청진기, 실, 붓 등을 상 위에 올리고 아이가 잡는 물건으로 미래를 점쳐봅니다.",
                "국립민속박물관 풍속 아카이브",
            ),
        ]
        c.executemany(
            "INSERT INTO master_timeline (target_month, title, category, description, source_asset) VALUES (?, ?, ?, ?, ?)",
            timeline_data,
        )

        # ⑤ AI 문화 맥락 의역 사전 데이터 에셋
        dict_data = [
            (
                "등센서",
                "vi",
                "Cảm biến lưng (Nhạy cảm khi đặt nằm)",
                "Đây là từ lóng của Hàn Quốc mô tả việc em bé khóc ngay lập tức khi vừa được đặt lưng xuống giường.",
                "Mẹo K-Caring: Người Hàn thường dùng gối ôm hình chữ U hoặc quấn tã chặt để tạo cảm giác như đang được bế.",
            ),
            (
                "돌치레",
                "vi",
                "Sốt mọc răng / Sốt đầu đời (Thôi nôi)",
                "Cụm từ chỉ tình trạng trẻ nhỏ đột ngột bị sốt hoặc ốm nhẹ vào khoảng thời gian đón sinh nhật đầu tiên (1 tuổi).",
                "Mẹo K-Caring: Đây là hiện tượng sinh lý bình thường khi kháng thể từ mẹ giảm đi, đừng quá lo lắng.",
            ),
            (
                "우쭈쭈",
                "vi",
                "Âu yếm / Cưng nựng hành vi",
                "Âm thanh vô nghĩa dùng để dỗ dành, làm trò vui hoặc thể hiện tình yêu thương vô bờ bến với trẻ nhỏ.",
                "Mẹo K-Caring: Tương đương với cách nói cưng nựng trẻ em tại Việt Nam.",
            ),
        ]
        c.executemany(
            "INSERT INTO cultural_dictionary (idiom, target_lang, translation, explanation, cultural_tip) VALUES (?, ?, ?, ?, ?)",
            dict_data,
        )

        # ④ 지자체 육아종합지원센터 장난감/놀이체험실 실시간 데이터
        center_data = [
            ("서울시 마포구", "마포 영유아 장난감 도서관", 14, "예약 가능"),
            ("부산시 해운대구", "해운대 놀이체험실", 3, "마감 임박"),
            ("인천시 부평구", "부평 육아종합지원센터", 25, "예약 가능"),
        ]
        c.executemany(
            "INSERT INTO support_centers (region, facility_name, toy_inventory, playroom_status) VALUES (?, ?, ?, ?)",
            center_data,
        )

    conn.commit()
    conn.close()


# ==========================================
# 2. 헬퍼 함수: 개월 수 계산 로직
# ==========================================
def calculate_months(birth_date_str):
    try:
        birth_date = datetime.datetime.strptime(birth_date_str, "%Y-%m-%d").date()
        today = datetime.date.today()
        # 2026년 기준 실시간 개월수 연산 적용
        return (
            (today.year - birth_date.year) * 12
            + today.month
            - birth_date.month
            - (1 if today.day < birth_date.day else 0)
        )
    except Exception:
        return 0


# ==========================================
# 3. 템플릿 엔지니어링 (현대적 모바일 UI 앱 디자인)
# ==========================================
HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>모아 (Mother-All) - K-컬처 육아 플랫폼</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #FF7A94;
            --primary-light: #FFEBF0;
            --secondary: #6C5CE7;
            --secondary-light: #EEECFB;
            --dark: #2D3436;
            --gray-bg: #F8F9FD;
            --card-shadow: 0 12px 24px rgba(255, 122, 148, 0.12);
        }
        * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { margin: 0; padding: 0; background-color: #E9ECEF; display: flex; justify-content: center; min-height: 100vh; }
        
        /* 모바일 디바이스 프레임 구현 */
        .app-frame {
            width: 100%; max-width: 430px; background-color: var(--gray-bg);
            min-height: 100vh; position: relative; padding-bottom: 90px;
            box-shadow: 0 0 30px rgba(0,0,0,0.15); display: flex; flex-direction: column;
        }
        
        /* 상단 모던 헤더 */
        header {
            background: linear-gradient(135deg, var(--secondary), var(--primary));
            padding: 35px 24px 25px; border-radius: 0 0 32px 32px; color: white;
        }
        header .brand-zone { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
        header .brand-zone h2 { margin: 0; font-size: 20px; font-weight: 800; letter-spacing: -0.5px; }
        header .brand-zone .badge { background: rgba(255,255,255,0.2); padding: 4px 10px; border-radius: 12px; font-size: 11px; }
        header h1 { margin: 0; font-size: 24px; font-weight: 700; line-height: 1.3; }
        
        /* 메인 컨텐츠 컨테이너 */
        .container { padding: 20px; flex: 1; }
        h3 { font-size: 18px; color: var(--dark); margin: 24px 0 14px; display: flex; align-items: center; gap: 8px; }
        
        /* 모던 디자인 카드 스타일 */
        .app-card {
            background: white; border-radius: 24px; padding: 20px;
            margin-bottom: 20px; box-shadow: 0 8px 16px rgba(0,0,0,0.02);
            border: 1px solid rgba(0,0,0,0.03);
        }
        
        /* 폼 요소 스타일 */
        .form-group { margin-bottom: 16px; }
        .form-group label { display: block; font-size: 13px; font-weight: 600; color: #64748B; margin-bottom: 6px; }
        .form-control {
            width: 100%; padding: 14px; border-radius: 14px; border: 1.5px solid #E2E8F0;
            font-size: 15px; transition: 0.2s; background: #F8FAFC;
        }
        .form-control:focus { outline: none; border-color: var(--primary); background: white; }
        .btn-submit {
            width: 100%; background: var(--dark); color: white; border: none; padding: 15px;
            border-radius: 14px; font-size: 16px; font-weight: 700; cursor: pointer; transition: 0.2s;
        }
        .btn-submit:hover { background: var(--primary); }
        
        /* 아기 정보 요약 프로필 바 */
        .baby-profile {
            display: flex; align-items: center; gap: 16px; background: white;
            padding: 16px; border-radius: 20px; border-left: 5px solid var(--primary);
        }
        .baby-avatar { width: 50px; height: 50px; background: var(--primary-light); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: var(--primary); font-size: 22px; }
        .baby-info h4 { margin: 0; font-size: 16px; color: var(--dark); }
        .baby-info p { margin: 4px 0 0; font-size: 13px; color: #64748B; }
        
        /* 초개인화 타임라인 디자인 (핵심 기능 ①) */
        .timeline-stream { position: relative; padding-left: 20px; border-left: 2px dashed #E2E8F0; margin-left: 10px; }
        .timeline-node { position: relative; margin-bottom: 24px; }
        .timeline-icon {
            position: absolute; left: -31px; top: 2px; width: 20px; height: 20px;
            border-radius: 50%; background: white; border: 3px solid var(--primary);
            display: flex; align-items: center; justify-content: center;
        }
        .timeline-node.health .timeline-icon { border-color: var(--secondary); }
        .timeline-node.support .timeline-icon { border-color: #00B894; }
        .timeline-body { background: white; padding: 16px; border-radius: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.01); }
        .timeline-tag { font-size: 11px; font-weight: 700; text-transform: uppercase; padding: 3px 8px; border-radius: 8px; display: inline-block; margin-bottom: 8px; }
        .timeline-tag.culture { background: var(--primary-light); color: var(--primary); }
        .timeline-tag.health { background: var(--secondary-light); color: var(--secondary); }
        .timeline-tag.support { background: #E6F9F5; color: #00B894; }
        .timeline-title { font-size: 15px; font-weight: 700; color: var(--dark); margin: 0 0 6px; }
        .timeline-text { font-size: 13px; color: #4A5568; line-height: 1.4; margin: 0 0 8px; }
        .timeline-source { font-size: 11px; color: #A0AEC0; }
        
        /* AI 의역 엔진 결과 출력 공간 (핵심 기능 ⑤) */
        .dict-result-box { background: #F1F2F6; border-radius: 16px; padding: 16px; margin-top: 14px; display: block; border-left: 4px solid var(--secondary); }
        .dict-title { font-size: 16px; font-weight: 700; color: var(--secondary); margin-bottom: 4px; }
        .dict-trans { font-size: 14px; font-weight: 600; color: var(--dark); margin-bottom: 8px; }
        .dict-desc { font-size: 13px; color: #4E5968; margin-bottom: 8px; line-height: 1.4; }
        .dict-tip { font-size: 12px; color: #FF7A94; font-weight: 600; background: white; padding: 8px; border-radius: 8px; }
        
        /* 하단 모던 고정 네비게이션 바 */
        .bottom-nav {
            position: fixed; bottom: 0; width: 100%; max-width: 430px; height: 74px;
            background: rgba(255, 255, 255, 0.94); backdrop-filter: blur(12px);
            display: flex; justify-content: space-around; align-items: center;
            border-top: 1px solid rgba(0,0,0,0.06); border-radius: 24px 24px 0 0; z-index: 100;
        }
        .nav-item { text-decoration: none; color: #94A3B8; display: flex; flex-direction: column; align-items: center; gap: 4px; font-size: 11px; font-weight: 600; cursor: pointer; }
        .nav-item.active { color: var(--primary); }
        .nav-item i { font-size: 20px; }
        
        /* 알림 배너 및 리스트 스타일 */
        .api-badge-list { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
        .api-badge { font-size: 11px; background: #EDF2F7; color: #4A5568; padding: 4px 8px; border-radius: 6px; }
        
        /* 행정 서류 미리보기 구역 (핵심 기능 2번) */
        .doc-preview { background: #FAF9F6; border: 1px dashed #D3D3D3; border-radius: 12px; padding: 16px; font-family: 'Courier New', monospace; font-size: 12px; }
        
        /* B2B 커머스 연계 컴포넌트 */
        .commerce-widget { display: flex; justify-content: space-between; align-items: center; background: #FFF9E6; border: 1px solid #FFEAA7; border-radius: 14px; padding: 12px 16px; margin-top: 10px; }
        .commerce-text { font-size: 12px; color: #D6A2E8; font-weight: 700; }
        .commerce-btn { background: #F1C40F; color: white; border: none; padding: 6px 12px; border-radius: 8px; font-size: 11px; font-weight: 700; cursor: pointer; }
    </style>
</head>
<body>

    <div class="app-frame">
        <header>
            <div class="brand-zone">
                <h2>MOA (모아)</h2>
                <div class="badge"><i class="fa-solid fa-earth-asia"></i> Multilingual AI v1.0</div>
            </div>
            <h1>K-컬처 육아<br>통합 내비게이션</h1>
        </header>

        <div class="container">
            
            <!-- 1. 아기 정보 입력 및 연동 컴포넌트 -->
            <h3><i class="fa-solid fa-baby"></i> 자녀 정보 관리 및 AI 초개인화</h3>
            <div class="app-card">
                {% if child %}
                <div class="baby-profile">
                    <div class="baby-avatar"><i class="fa-solid fa-child-reaching"></i></div>
                    <div class="baby-info">
                        <h4>{{ child.name }} 아기 ({{ child.nationality }})</h4>
                        <p>생년월일: <strong>{{ child.birth_date }}</strong> | 현재 <strong>{{ child.age_months }}개월차</strong></p>
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
                        <label>어머니 국적 (배우자 배경)</label>
                        <select name="nationality" class="form-control">
                            <option value="Vietnam">베트남 (Vietnam)</option>
                            <option value="China">중국 (China)</option>
                            <option value="Philippines">필리핀 (Philippines)</option>
                            <option value="Japan">일본 (Japan)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>기본 소통 언어</label>
                        <select name="language" class="form-control">
                            <option value="vi">Tiếng Việt (베트남어)</option>
                            <option value="zh">中文 (중국어)</option>
                            <option value="en">English (영어)</option>
                            <option value="ko">한국어 (Korean)</option>
                        </select>
                    </div>
                    <button type="submit" class="btn-submit"><i class="fa-solid fa-heart"></i> 초개인화 맞춤형 타임라인 생성</button>
                </form>
                {% endif %}
            </div>

            <!-- 2. 초개인화 육아 타임라인 푸시 스트림 (핵심 서비스 ①) -->
            <h3><i class="fa-solid fa-hourglass-half"></i> 월령별 맞춤 융합 타임라인</h3>
            <div class="app-card">
                {% if timeline_events %}
                <div class="timeline-stream">
                    {% for event in timeline_events %}
                    <div class="timeline-node {{ event.category|lower }}">
                        <div class="timeline-icon"></div>
                        <div class="timeline-body">
                            <span class="timeline-tag {{ event.category|lower }}">
                                {% if event.category == 'Culture' %}한국 전통 의례 (국립민속박물관)
                                {% elif event.category == 'Health' %}보건복지부 발달가이드
                                {% else %}여성가족부 다문화지원{% endif %}
                            </span>
                            <div class="timeline-title">[{{ event.target_month }}개월] {{ event.title }}</div>
                            <div class="timeline-text">{{ event.description }}</div>
                            <div class="timeline-source"><i class="fa-solid fa-link"></i> 연계자산: {{ event.source_asset }}</div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% else %}
                <p style="font-size:13px; color:#64748B; text-align:center; padding:20px 0;">아이 정보를 입력하시면 정부 데이터 융합 엔진 기반의 초개인화 타임라인이 빌드됩니다.</p>
                {% endif %}
            </div>

            <!-- 3. AI 기반 한국 육아 문화 의역 엔진 (핵심 서비스 ⑤) -->
            <h3><i class="fa-solid fa-wand-magic-sparkles"></i> AI K-육아 관용구 의역기</h3>
            <div class="app-card">
                <p style="font-size:13px; color:#64748B; margin-top:0;">'등센서', '돌치레' 등 낯선 한국식 육아 표현을 문화적 배경에 맞춰 친숙하게 번역해 드립니다.</p>
                <form action="/translate" method="POST" style="display:flex; gap:8px;">
                    <input type="text" name="idiom" class="form-control" placeholder="예: 등센서, 돌치레, 우쭈쭈" required style="margin:0;">
                    <button type="submit" class="btn-submit" style="width:auto; padding:0 20px; margin:0;"><i class="fa-solid fa-magnifying-glass"></i></button>
                </form>

                {% if dict_result %}
                <div class="dict-result-box">
                    <div class="dict-title"><i class="fa-solid fa-comment-dots"></i> 입력 표현: {{ dict_result.idiom }}</div>
                    <div class="dict-trans"><i class="fa-solid fa-language"></i> 의역 명칭: {{ dict_result.translation }}</div>
                    <div class="dict-desc">{{ dict_result.explanation }}</div>
                    <div class="dict-tip"><i class="fa-solid fa-lightbulb"></i> 문화적 Care Tip: {{ dict_result.cultural_tip }}</div>
                </div>
                <!-- B2B 커머스 중개 수수료 확보 모델 가동 시뮬레이션 -->
                <div class="commerce-widget">
                    <div class="commerce-text"><i class="fa-solid fa-cart-shopping"></i> '{{ dict_result.idiom }}' 극복 추천 육아 에센셜 템</div>
                    <button class="commerce-btn" onclick="alert('B2B 커머스 중개 파트너 몰로 연결됩니다. (수수료 확보)')">구매하기</button>
                </div>
                {% endif %}
            </div>

            <!-- 4. 실시간 지자체 API 결합 서비스 공유 (핵심 서비스 ④) -->
            <h3><i class="fa-solid fa-map-location-dot"></i> 전국 지자체 실시간 인프라 현황</h3>
            <div class="app-card">
                <div style="font-size:12px; color:#4A5568; font-weight:700; margin-bottom:10px;"><i class="fa-solid fa-signal"></i> 전국 180개 이상 지자체 연동 API 가동 중</div>
                {% for center in support_centers %}
                <div style="padding:10px 0; border-bottom:1px solid #EDF2F7; display:flex; justify-content:between; align-items:center; font-size:13px;">
                    <div style="flex:1;">
                        <strong style="color:var(--dark);">{{ center.facility_name }}</strong>
                        <div style="font-size:11px; color:#A0AEC0;">위치: {{ center.region }}</div>
                    </div>
                    <div style="text-align:right;">
                        <span class="api-badge">장난감 잔여: {{ center.toy_inventory }}개</span>
                        <span class="api-badge" style="background:#E6F9F5; color:#00B894;">{{ center.playroom_status }}</span>
                    </div>
                </div>
                {% endfor %}
            </div>

            <!-- 5. 행정 서류 원클릭 자동 작성 기능 (핵심 서비스 ②) -->
            <h3><i class="fa-solid fa-file-signature"></i> 원클릭 행정 서류 자동 도우미</h3>
            <div class="app-card">
                <p style="font-size:13px; color:#64748B; margin-top:0;">등록된 자녀 정보와 보건복지부 일정을 반영하여 다문화 가정용 바우처/멘토링 지원 신청서가 자동 모델링됩니다.</p>
                {% if child %}
                <div class="doc-preview">
                    [가족센터 다문화 육아 지원 바우처 신청서]<br>
                    -------------------------------------<br>
                    ■ 신청인(모): {{ child.name }}의 모친 (국적: {{ child.nationality }})<br>
                    ■ 대상자녀: {{ child.name }} (생년월일: {{ child.birth_date }})<br>
                    ■ 아기 연령: 만 0세 (현재 {{ child.age_months }}개월)<br>
                    ■ 맞춤 가이드라인: 지원 조건(만 3세 미만 영유아) 충족 확인 완료.<br>
                    -------------------------------------<br>
                    [여성가족부 표준 양식 연동 - 전산 자동 접수 준비 완료]
                </div>
                <button class="btn-submit" style="background:var(--secondary); margin-top:12px;" onclick="alert('행정 서류가 해당 지자체 민원시스템으로 안전하게 원클릭 접수되었습니다.')"><i class="fa-solid fa-paper-plane"></i> 지자체 민원 시스템 원클릭 제출</button>
                {% else %}
                <p style="font-size:12px; color:#A0AEC0; text-align:center; padding:10px 0;">자녀 정보를 먼저 입력하시면 서류 초안이 렌더링됩니다.</p>
                {% endif %}
            </div>

        </div>

        <!-- 하단 고정형 모바일 내비게이션 바 -->
        <nav class="bottom-nav">
            <a href="/" class="nav-item active"><i class="fa-solid fa-house"></i><span>홈</span></a>
            <a href="/#translate" class="nav-item"><i class="fa-solid fa-language"></i><span>의역기</span></a>
            <a href="/#support" class="nav-item"><i class="fa-solid fa-building-user"></i><span>지자체</span></a>
            <a href="/#document" class="nav-item"><i class="fa-solid fa-file-shield"></i><span>서류도우미</span></a>
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

    # 활성화된 아기 프로필 로드
    c.execute("SELECT * FROM children ORDER BY id DESC LIMIT 1")
    child_row = c.fetchone()

    child = None
    timeline_events = []

    if child_row:
        # 실시간 월령 변동 로직 반영
        current_months = calculate_months(child_row["birth_date"])
        child = {
            "name": child_row["name"],
            "birth_date": child_row["birth_date"],
            "nationality": child_row["nationality"],
            "language": child_row["language"],
            "age_months": current_months,
        }

        # 초개인화 데이터 융합 엔진 알고리즘 가동
        # 아기의 실제 개월수 이하 및 직후 다가올 일정을 필터링 추출
        c.execute(
            "SELECT * FROM master_timeline WHERE target_month >= ? ORDER BY target_month ASC LIMIT 3",
            (current_months,),
        )
        timeline_events = c.fetchall()

    # 전국 지자체 육아종합지원센터 API 실시간 연동 데이터 바인딩
    c.execute("SELECT * FROM support_centers")
    centers = c.fetchall()

    # 세션 딕셔너리 값 유무 체크
    dict_result = getattr(app, "latest_dict_result", None)

    conn.close()

    return render_template_string(
        HTML_LAYOUT,
        child=child,
        timeline_events=timeline_events,
        support_centers=centers,
        dict_result=dict_result,
    )


@app.route("/register", methods=["POST"])
def register_child():
    name = request.form.get("name")
    birth_date = request.form.get("birth_date")
    nationality = request.form.get("nationality")
    language = request.form.get("language")

    # 가변 파라미터 연산 데이터 가공
    initial_months = calculate_months(birth_date)

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # 기존 데이터 청소 후 단일 유저 세션 관리 시뮬레이션
    c.execute("DELETE FROM children")
    c.execute(
        "INSERT INTO children (name, birth_date, nationality, language, age_months) VALUES (?, ?, ?, ?, ?)",
        (name, birth_date, nationality, language, initial_months),
    )
    conn.commit()
    conn.close()

    # 등록 시 이전 의역 히스토리 초기화
    if hasattr(app, "latest_dict_result"):
        delattr(app, "latest_dict_result")

    return redirect(url_for("main_dashboard"))


@app.route("/translate", methods=["POST"])
def translate_idiom():
    idiom_keyword = request.form.get("idiom", "").strip()

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 사용자의 배경 언어 파악을 위한 아이 프로필 확인
    c.execute("SELECT language FROM children ORDER BY id DESC LIMIT 1")
    user_lang_row = c.fetchone()
    target_lang = user_lang_row["language"] if user_lang_row else "vi"

    # 문화적 의역 매칭 쿼리 가동
    c.execute(
        "SELECT * FROM cultural_dictionary WHERE idiom LIKE ? AND target_lang = ?",
        (f"%{idiom_keyword}%", target_lang),
    )
    res = c.fetchone()
    conn.close()

    if res:
        app.latest_dict_result = {
            "idiom": res["idiom"],
            "translation": res["translation"],
            "explanation": res["explanation"],
            "cultural_tip": res["cultural_tip"],
        }
    else:
        # 데이터가 없을 시 실시간 생성형 번역 엔진 대체 가이드 제공
        app.latest_dict_result = {
            "idiom": idiom_keyword,
            "translation": "정의된 언어팩 준비 중 (In-Context 빌드 가능)",
            "explanation": f"한국의 특별한 육아 표현 '{idiom_keyword}'에 대한 맞춤형 번역을 조율 중입니다.",
            "cultural_tip": "다문화 센터 또는 플랫폼 멘토 전담 라인에 질문하시면 5분 내 매칭 피드가 전송됩니다.",
        }

    return redirect(url_for("main_dashboard"))


@app.route("/clear")
def clear_child():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM children")
    conn.commit()
    conn.close()

    if hasattr(app, "latest_dict_result"):
        delattr(app, "latest_dict_result")

    return redirect(url_for("main_dashboard"))



# ==========================================
# 5. 애플리케이션 엔트리 포인트
# ==========================================
if __name__ == "__main__":
    init_db()
    # 개발 및 배포 환경 최적화를 위한 샌드박스 가동
    app.run(host="0.0.0.0", port=5000, debug=True)
