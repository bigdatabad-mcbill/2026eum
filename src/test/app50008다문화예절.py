import sqlite3
import requests
import json
import uuid
from datetime import datetime
from flask import Flask, request, render_template_string, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = "mcst_culture_data_ieum_v2_secret_key"

DB_NAME = "competitions_ieum_v2.db"
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
LM_STUDIO_MODELS_URL = "http://localhost:1234/v1/models"

# ==========================================
# 1. 데이터베이스 초기화
# ==========================================
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS competitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                industry TEXT NOT NULL,
                topic TEXT NOT NULL,
                competitor TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS generation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id INTEGER, 
                session_id TEXT NOT NULL, 
                stage_num INTEGER NOT NULL, 
                stage_title TEXT NOT NULL, 
                prompt_sent TEXT NOT NULL, 
                response_received TEXT NOT NULL, 
                cumulative_context TEXT, 
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

init_db()

def get_active_model():
    try:
        response = requests.get(LM_STUDIO_MODELS_URL, timeout=5)
        if response.status_code == 200:
            models_data = response.json()
            if "data" in models_data and len(models_data["data"]) > 0:
                return models_data["data"][0]["id"]
    except Exception:
        pass
    return "local-model"

# ==========================================
# 2. UI/UX 템플릿 (5단계 개발 프롬프트 추적 엔진 포함)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>문체부 문화데이터 경진대회 플랫폼 - 이음(IEUM) v2</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        body { background-color: #f3f4f7; font-family: 'Pretendard', sans-serif; }
        .sidebar { background: #1e1b4b; color: #f8fafc; min-height: 100vh; border-right: 1px solid #312e81; }
        .sidebar .form-label { color: #c7d2fe; font-weight: 500; font-size: 0.85rem; }
        .main-content { min-height: 100vh; background-color: #f8fafc; }
        .report-view { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 40px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }
        .badge-industry { background-color: #4f46e5; color: white; font-size: 0.85rem; padding: 6px 12px; }
        .list-group-item { background: #312e81; border: 1px solid #4338ca; color: #e0e7ff; cursor: pointer; }
        .list-group-item:hover { background: #4338ca; color: #ffffff; }
        .list-group-item.active { background: #4f46e5; border-color: #4f46e5; color: white; }
        
        .report-view table { width: 100%; margin: 20px 0; border-collapse: collapse; }
        .report-view th { background-color: #eef2ff; color: #1e1b4b; padding: 12px; border: 1px solid #c7d2fe; text-align: center; }
        .report-view td { padding: 12px; border: 1px solid #e2e8f0; }
        
        .loading-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(30, 27, 75, 0.95); z-index: 9999; justify-content: center; align-items: center; color: white; }
        .log-code { max-height: 250px; background-color: #1e1e1e; color: #d4d4d4; font-family: 'Consolas', monospace; font-size: 0.85rem; padding: 12px; border-radius: 6px; overflow-y: auto; }
    </style>
</head>
<body>

<div id="loadingOverlay" class="loading-overlay flex-column">
    <div class="spinner-border text-primary mb-4" style="width: 3rem; height: 3rem;" role="status"></div>
    <h4 id="statusTitle" class="fw-bold text-light">다문화 의례 이음 기획/개발 가이드 추론 중...</h4>
    <p id="statusDesc" class="text-muted text-center px-4" style="max-width: 500px;">
        기획서 초안 빌드부터 실제 서비스 이식이 가능한 Flask/Sqlite 아키텍처 연동형 프로덕션 프롬프트 엔지니어링 에셋을 통합 수집합니다.
    </p>
    
    <div class="container mt-3" style="max-width: 600px;">
        <div class="progress" style="height: 25px;">
            <div id="progressBar" class="progress-bar progress-bar-striped progress-bar-animated bg-primary" role="progressbar" style="width: 0%;">0%</div>
        </div>
        <div id="stageList" class="mt-4 text-start bg-dark p-3 rounded border border-secondary small">
            <div id="stage1" class="text-white-50 mb-2"><i class="bi bi-circle"></i> 1단계: 다문화 가구 내 의례 갈등 페인포인트 및 사회적 공익성 배경 도출</div>
            <div id="stage2" class="text-white-50 mb-2"><i class="bi bi-circle"></i> 2단계: 공공 문화데이터 수집/매핑 및 AI 맞춤형 의례 절충 시나리오 설계</div>
            <div id="stage3" class="text-white-50 mb-2"><i class="bi bi-circle"></i> 3단계: 기존 단순 번역/정보 나열 서비스 대조군 대비 차별성 행렬 분석</div>
            <div id="stage4" class="text-white-50 mb-2"><i class="bi bi-circle"></i> 4단계: B2G 연계 방안 및 가구 정착/갈등 해소 정량적 성과 지표 산출</div>
            <div id="stage5" class="text-white-50 mb-2"><i class="bi bi-circle"></i> 5단계: 서비스 소스 코드 이식용 LLM 백엔드 개발 시스템 프롬프트(Few-Shot) 구현</div>
        </div>
    </div>
</div>

<div class="container-fluid">
    <div class="row">
        <div class="col-md-4 p-4 sidebar">
            <h4 class="mb-3 text-light d-flex align-items-center fw-bold">
                <i class="bi bi-code-square text-primary me-2"></i> 이음(IEUM) 개발 빌더
            </h4>
            <p class="small text-muted mb-4">문화체육관광부 공공데이터 결합 기획서 작성은 물론, Flask, SQLite 기반 시스템에서 실제 플래너를 생성해낼 수 있는 '프롬프트 코드'까지 자동 엔지니어링합니다.</p>

            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    {% for message in messages %}
                        <div class="alert alert-info alert-dismissible fade show" role="alert">
                            {{ message }}
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}

            <div class="bg-dark p-3 rounded mb-4 border border-secondary">
                <div class="mb-3">
                    <label class="form-label">산업 도메인 및 타겟</label>
                    <input type="text" id="industry" class="form-control bg-secondary text-white" value="공공 문화데이터 X 다문화가족 복지 교육">
                </div>
                <div class="mb-3">
                    <label class="form-label">분석 플랫폼 핵심 주제</label>
                    <input type="text" id="topic" class="form-control bg-secondary text-white" value="AI 기반 다문화 가정을 위한 생애주기별 맞춤형 K-전통 의례 가이드 '이음'">
                </div>
                <div class="mb-3">
                    <label class="form-label">대조군 서비스</label>
                    <input type="text" id="competitor" class="form-control bg-secondary text-white" value="포털 사이트의 단편적인 블로그 정보 및 단순 일반 다국어 번역 앱">
                </div>
                <div class="mb-3">
                    <label class="form-label">공식 기획서 타이틀</label>
                    <input type="text" id="title" class="form-control bg-secondary text-white" value="문화 공공데이터 기반 AI 다문화 가정 맞춤형 생애주기 K-전통 의례 플래너: 이음(IEUM)">
                </div>
                
                <button type="button" onclick="startDeepSearch()" class="btn btn-primary w-100 fw-bold shadow">
                    <i class="bi bi-lightning-charge"></i> 기획 및 개발 프롬프트 통합 추론
                </button>
            </div>

            <h5 class="text-muted pt-2 mb-3" style="font-size: 0.9rem;">산출된 기획서 히스토리 ({{ reports|length }})</h5>
            <div class="list-group overflow-auto" style="max-height: 250px;">
                {% for r in reports %}
                    <div class="list-group-item d-flex justify-content-between align-items-start p-2 {% if current_report and current_report[0] == r[0] %}active{% endif %}">
                        <div class="ms-2 me-auto text-truncate" onclick="location.href='{{ url_for('index', report_id=r[0]) }}'" style="max-width:85%;">
                            <div class="fw-bold text-truncate" style="font-size:0.85rem;">{{ r[1] }}</div>
                            <small class="text-muted" style="font-size:0.75rem;">{{ r[6] }}</small>
                        </div>
                        <form action="{{ url_for('delete_competition', report_id=r[0]) }}" method="POST">
                            <button type="submit" class="btn btn-link text-danger p-0 border-0"><i class="bi bi-trash-fill"></i></button>
                        </form>
                    </div>
                {% endfor %}
            </div>
        </div>

        <div class="col-md-8 p-5 main-content">
            {% if current_report %}
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <span class="badge badge-industry shadow-sm"><i class="bi bi-check2-all"></i> {{ current_report[2] }}</span>
                    <small class="text-muted"><i class="bi bi-clock-history"></i> 파이프라인 컴파일 마스터: {{ current_report[6] }}</small>
                </div>
                <h2 class="fw-bold text-dark mb-4">{{ current_report[1] }}</h2>
                
                <div class="report-view shadow-sm mb-5">
                    {{ current_report[5]|safe }}
                </div>

                <div class="card border-primary shadow-sm mt-5">
                    <div class="card-header bg-dark text-primary fw-bold d-flex justify-content-between align-items-center">
                        <span><i class="bi bi-terminal-box"></i> 🔍 데이터 파이프라인 실시간 컨텍스트 및 생성 로그 검증기</span>
                        <span class="badge bg-primary">v2 RAG 파라미터</span>
                    </div>
                    <div class="card-body">
                        <p class="text-muted small">각 다단계 추론 빌드 과정에서 입력된 시스템 오케스트레이션 및 데이터 매핑 추적 코드를 실시간 분석할 수 있습니다.</p>
                        
                        <div class="accordion" id="accordionLogs">
                            {% for log in logs %}
                            <div class="accordion-item">
                                <h2 class="accordion-header" id="heading{{ log[0] }}">
                                    <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse{{ log[0] }}" aria-expanded="false" aria-controls="collapse{{ log[0] }}">
                                        <strong>[{{ log[3] }}단계 분석] {{ log[4] }}</strong> &nbsp;&nbsp;<span class="text-muted" style="font-size:0.8rem;">({{ log[8] }})</span>
                                    </button>
                                </h2>
                                <div id="collapse{{ log[0] }}" class="accordion-collapse collapse" aria-labelledby="heading{{ log[0] }}" data-bs-parent="#accordionLogs">
                                    <div class="accordion-body">
                                        <div class="mb-3">
                                            <h6 class="text-primary fw-bold" style="font-size:0.85rem;"><i class="bi bi-chevron-right"></i> 시스템 오케스트레이션 프롬프트 및 수집 명령 구조</h6>
                                            <pre class="log-code bg-dark text-white p-2 small">{{ log[5] }}</pre>
                                        </div>
                                        <div class="mb-3">
                                            <h6 class="text-success fw-bold" style="font-size:0.85rem;"><i class="bi bi-chevron-right"></i> 생성된 구조 마크업 결과물 (Raw HTML)</h6>
                                            <pre class="log-code bg-dark text-light p-2 small">{{ log[6] }}</pre>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            {% else %}
                <div class="d-flex flex-column justify-content-center align-items-center h-100 text-muted">
                    <i class="bi bi-code-slash text-secondary" style="font-size: 5rem;"></i>
                    <h4 class="mt-4 fw-bold">활성화된 복합 기획 가이드가 없습니다.</h4>
                    <p>도메인 매퍼 및 가이드 구성을 확인하고 통합 추론 시작 버튼을 클릭해 주세요.</p>
                </div>
            {% endif %}
        </div>
    </div>
</div>

<script>
function generateUUID() {
    return 'session-' + 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

async function startDeepSearch() {
    const session_id = generateUUID();
    const data = {
        session_id: session_id,
        industry: document.getElementById('industry').value,
        topic: document.getElementById('topic').value,
        competitor: document.getElementById('competitor').value,
        title: document.getElementById('title').value
    };

    document.getElementById('loadingOverlay').style.display = 'flex';
    resetStageUI();

    let combinedContent = "";

    // 총 5개 단계 순차 추론 실행
    for (let stage = 1; stage <= 5; stage++) {
        updateStageUI(stage, 'processing');
        try {
            const response = await fetch(`/generate_step/${stage}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ...data, accumulated_context: combinedContent })
            });
            
            const result = await response.json();
            if (!result.success) {
                alert("기획서 및 프롬프트 생성 단계 오류: " + result.error);
                closeOverlay();
                return;
            }
            
            combinedContent += result.content + "<hr class='my-5 border-primary'>";
            updateStageUI(stage, 'success');
            
            let progressPercentage = stage * 20; // 5단계이므로 단계별 20%씩 가산
            document.getElementById('progressBar').style.width = progressPercentage + '%';
            document.getElementById('progressBar').innerText = progressPercentage + '%';
        } catch (err) {
            alert("백엔드 엔진 연결 실패: " + err);
            closeOverlay();
            return;
        }
    }

    document.getElementById('statusTitle').innerText = "최종 산출물 마스터 디스크 영속화 중...";
    const saveResponse = await fetch('/save_final', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...data, full_content: combinedContent })
    });
    
    const saveResult = await saveResponse.json();
    if(saveResult.success) {
        location.href = `/${saveResult.new_id}`;
    } else {
        alert("기획서 영속화 실패.");
        closeOverlay();
    }
}

function updateStageUI(stage, status) {
    const stageEl = document.getElementById(`stage${stage}`);
    if (status === 'processing') {
        document.getElementById('statusTitle').innerText = `${stage}단계 컨텍스트 연산 및 타겟 빌드 중...`;
        stageEl.className = "text-warning fw-bold mb-2";
        stageEl.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span> [구동 중] 데이터 아키텍처 추출 및 토큰 밸런싱 중...`;
    } else if (status === 'success') {
        stageEl.className = "text-success mb-2";
        stageEl.innerHTML = `<i class="bi bi-check-circle-fill me-2"></i> [완료] 해당 단계 가이드 컴파일 마크업 적재 완료`;
    }
}

function resetStageUI() {
    for (let i = 1; i <= 5; i++) {
        const stageEl = document.getElementById(`stage${i}`);
        stageEl.className = "text-white-50 mb-2";
        stageEl.innerHTML = `<i class="bi bi-circle"></i> ${i}단계 대기 중`;
    }
    document.getElementById('progressBar').style.width = '0%';
    document.getElementById('progressBar').innerText = '0%';
}

function closeOverlay() {
    document.getElementById('loadingOverlay').style.display = 'none';
}
</script>
</body>
</html>
"""

# ==========================================
# 3. 백엔드 컨트롤러 (5단계 확장 모델)
# ==========================================
@app.route("/")
@app.route("/<int:report_id>")
def index(report_id=None):
    reports = []
    current_report = None
    logs = []
    
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, industry, topic, competitor, content, datetime(created_at, 'localtime') FROM competitions ORDER BY id DESC")
        reports = cursor.fetchall()
        
        if report_id:
            cursor.execute("SELECT id, title, industry, topic, competitor, content, datetime(created_at, 'localtime') FROM competitions WHERE id = ?", (report_id,))
            current_report = cursor.fetchone()
            
            cursor.execute("""
                SELECT id, doc_id, session_id, stage_num, stage_title, prompt_sent, response_received, cumulative_context, datetime(created_at, 'localtime') 
                FROM generation_logs 
                WHERE doc_id = ? 
                ORDER BY stage_num ASC
            """, (report_id,))
            logs = cursor.fetchall()

    return render_template_string(HTML_TEMPLATE, reports=reports, current_report=current_report, logs=logs)


@app.route("/generate_step/<int:stage>", methods=["POST"])
def generate_step(stage):
    data = request.json
    session_id = data.get("session_id")
    industry = data.get("industry")
    topic = data.get("topic")
    competitor = data.get("competitor")
    accumulated_context = data.get("accumulated_context", "")

    stage_titles = {
        1: "제안 배경, 다문화 가구 내 의례 갈등 페인포인트 및 공익적 필요성",
        2: "공공 문화데이터 융합 설계 및 AI 절충 시나리오 아키텍처",
        3: "기존 정보 서비스 대조군 대비 차별화 비교 행렬 및 독창성 분석",
        4: "B2G 확산 로드맵 및 다문화 사회 안정화 정량적 기대효과 지표 산출",
        5: "실제 배포 서비스(Flask/SQLite) 탑재용 백엔드 LLM 개발자 시스템 프롬프트"
    }
    stage_title = stage_titles.get(stage, "미정의 단계")

    system_prompt = (
        "너는 문화체육관광부 공공데이터 분석 경진대회에서 대상(대통령상)을 목표로 기획서와 개발 명세서를 설계하는 "
        "국내 최고 수준의 AI 문화 융합 서비스 아키텍트이자 프롬프트 엔지니어링 전문가야. "
        "모든 문서 구조는 심사위원과 개발자 집단을 동시에 설득할 수 있도록 명확한 비즈니스 프레임워크와 테크니컬 파라미터를 동반해야 해. "
        "마크다운 문법(예: ```html, ```, #, **)은 절대 출력에 섞지 말고, "
        "바로 HTML 렌더링에 사용할 수 있는 순수 웹 컴포넌트 마크업(<h1>, <h4>, <p>, <table>, <pre>, <code> 등)만 가공하여 출력하라."
    )

    if stage == 1:
        prompt = (
            f"주제인 [{topic}] 플랫폼의 '1. 제안 배경 및 필요성(Pain Point)' 영역을 작성해줘. "
            f"다문화 가구원 수의 증가 추세 속에서 갈등의 핵심 요인으로 작용하는 "
            f"'한국의 제사, 차례, 돌잔치, 상례 등 독특한 전통 의례 문화에 대한 이해 부족 및 스트레스'를 정조준해줘. "
            f"이주민 배우자의 소외감과 한국 가족 간의 소통 단절 문제를 극복해야 하는 이유를 기술해줘. "
            f"소제목은 <h4> 태그, 본문은 <p> 태그를 쓰고 정량적 수치 지표는 강조해줘."
        )
    elif stage == 2:
        prompt = (
            f"[{topic}]의 '2. 공공 데이터 활용 및 AI 맞춤형 융합 아키텍처 설계' 장을 구성해줘. "
            f"제공된 핵심 데이터 소스인 "
            f"① 국립민속박물관 평생의례 사전 및 조사 데이터, ② 문화체육관광부/국학진흥원 한국 전통 가례/제례 데이터, "
            f"③ 보건복지부/교육부 영유아 발달 및 다문화가족 복지 공공데이터, ④ 국립국어원 다국어 대역 사전 데이터를 명시해줘. "
            f"이 데이터들을 LLM 기반 AI가 이주민 배우자의 국적과 종교를 고려해 개인화 가이드북을 자동 생성하는 아키텍처를 보여줘."
        )
    elif stage == 3:
        prompt = (
            f"[{topic}]가 기존 대조군 솔루션인 [{competitor}] 대비 가진 탁월성을 입증하는 '3. 서비스 독창성 및 우위성' 장을 작성해줘. "
            f"반드시 <table class='table table-bordered table-striped text-center'>"
            f"<thead><tr><th>구분</th><th>인터넷 포털 블로그</th><th>일반 다국어 번역 앱</th><th>이음(IEUM) (본 기획)</th></tr></thead>"
            f"형태의 표를 빌드해줘. 문화데이터의 신뢰성, 종교/국적별 개인화 수준, 양방향 이중언어 가이드 제공 여부, "
            f"스마트 체크리스트(D-Day) 유무, 공익적 가치의 5가지 차원 비교를 완벽히 채워주고 독창성을 설명해줘."
        )
    elif stage == 4:
        prompt = (
            f"[{topic}]의 '4. 기대효과 및 향후 비즈니스/확산 방안'을 도출해줘. "
            f"정량적 효과(의례 갈등으로 인한 다문화 이혼율 감소 기여도, 전국 다문화 가구 잠재 수혜율 등)와 "
            f"정성적 효과를 구조화해줘. 더불어 B2G 확산 방안으로서 여성가족부 산하 전국 다문화가족지원센터 연계 및 "
            f"O2O 의례 키트 커머스 확장 모델을 깔끔한 HTML 구조로 출력해줘."
        )
    elif stage == 5:
        prompt = (
            f"[{topic}]를 실제 Python Flask와 SQLite 환경에서 구동할 때, 가이드북 생성을 전담하는 "
            f"'5. 서비스 코어 이식용 AI 시스템 프롬프트(Few-Shot Engineering) 명세서' 장을 빌드해줘. "
            f"이 파트는 심사위원들에게 개발 구현 가능성(Feasibility)을 증명하는 핵심 구역이야. "
            f"Flask 백엔드 소스 내부에서 호출할 `SYSTEM_PROMPT`와 `USER_INPUT_STRUCTURE`를 명확히 설계해줘. "
            f"프롬프트 내부에는 반드시 [사용자 입력 가변값: spouse_nationality, religion, ritual_type] 프로필 구조가 매핑되어야 하며, "
            f"출력 형식을 JSON 구조나 좌우 대칭형 템플릿으로 강제하는 Few-Shot 규칙 예시(예: 이슬람 국적 배우자의 제사 가이드 대응법)를 "
            f"<pre><code class='text-warning bg-dark p-3 d-block rounded'> 태그 내부에 소스코드 형태로 보기 좋게 표현해줘."
        )
    else:
        return jsonify({"success": False, "error": "잘못된 단계 매핑"})

    active_model_name = get_active_model()

    payload = {
        "model": active_model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    try:
        response = requests.post(LM_STUDIO_URL, json=payload, timeout=590)
        response.raise_for_status()
        ai_output = response.json()["choices"][0]["message"]["content"]
        
        ai_output = ai_output.replace("```html", "").replace("```", "").strip()

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO generation_logs (doc_id, session_id, stage_num, stage_title, prompt_sent, response_received, cumulative_context)
                VALUES (NULL, ?, ?, ?, ?, ?, ?)
            """, (session_id, stage, stage_title, prompt, ai_output, accumulated_context))
            conn.commit()

        return jsonify({"success": True, "content": ai_output})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/save_final", methods=["POST"])
def save_final():
    data = request.json
    session_id = data.get("session_id")
    title = data.get("title")
    industry = data.get("industry")
    topic = data.get("topic")
    competitor = data.get("competitor")
    full_content = data.get("full_content")

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO competitions (title, industry, topic, competitor, content) VALUES (?, ?, ?, ?, ?)",
            (title, industry, topic, competitor, full_content)
        )
        new_doc_id = cursor.lastrowid
        
        cursor.execute(
            "UPDATE generation_logs SET doc_id = ? WHERE session_id = ?",
            (new_doc_id, session_id)
        )
        conn.commit()

    return jsonify({"success": True, "new_id": new_doc_id})


@app.route("/delete/<int:report_id>", methods=["POST"])
def delete_competition(report_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM competitions WHERE id = ?", (report_id,))
        cursor.execute("DELETE FROM generation_logs WHERE doc_id = ?", (report_id,))
        conn.commit()
    flash("기획서 및 개발 가이드 파이프라인 데이터가 초기화되었습니다.")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=50008, debug=True)
