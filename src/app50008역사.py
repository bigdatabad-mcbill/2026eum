import sqlite3
import requests
import json
import uuid
from datetime import datetime
from flask import Flask, request, render_template_string, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = "mcst_culture_data_history_education_v3_secret_key"

DB_NAME = "competitions_history_edu.db"#"competitions_ieum.db"#"competitions_history_edu.db"
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
# 2. UI/UX 템플릿 (복사 및 다운로드 액션 엔진 추가)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>문체부 문화데이터 경진대회 플랫폼 - 한누리(Hannuri) v3</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        body { background-color: #f3f4f7; font-family: 'Pretendard', sans-serif; }
        .sidebar { background: #0f172a; color: #f8fafc; min-height: 100vh; border-right: 1px solid #1e293b; }
        .sidebar .form-label { color: #94a3b8; font-weight: 500; font-size: 0.85rem; }
        .main-content { min-height: 100vh; background-color: #f8fafc; }
        .report-view { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 40px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); position: relative; }
        .badge-industry { background-color: #0284c7; color: white; font-size: 0.85rem; padding: 6px 12px; }
        .list-group-item { background: #1e293b; border: 1px solid #334155; color: #cbd5e1; cursor: pointer; }
        .list-group-item:hover { background: #334155; color: #ffffff; }
        .list-group-item.active { background: #0284c7; border-color: #0284c7; color: white; }
        
        .report-view table { width: 100%; margin: 20px 0; border-collapse: collapse; }
        .report-view th { background-color: #f0f9ff; color: #0369a1; padding: 12px; border: 1px solid #bae6fd; text-align: center; }
        .report-view td { padding: 12px; border: 1px solid #e2e8f0; }
        
        .loading-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15, 23, 42, 0.95); z-index: 9999; justify-content: center; align-items: center; color: white; }
        .log-code { max-height: 250px; background-color: #1e1e1e; color: #d4d4d4; font-family: 'Consolas', monospace; font-size: 0.85rem; padding: 12px; border-radius: 6px; overflow-y: auto; }
        
        .action-bar { border-bottom: 1px solid #e2e8f0; padding-bottom: 15px; margin-bottom: 25px; display: flex; justify-content: flex-end; gap: 10px; }
    </style>
</head>
<body>

<div id="loadingOverlay" class="loading-overlay flex-column">
    <div class="spinner-border text-info mb-4" style="width: 3rem; height: 3rem;" role="status"></div>
    <h4 id="statusTitle" class="fw-bold text-light">다문화 역사 교육 플랫폼 기획 및 프롬프트 생성 중...</h4>
    <p id="statusDesc" class="text-muted text-center px-4" style="max-width: 500px;">
        국립중앙박물관 역사 유물 데이터와 사료 데이터베이스를 컴파일하여 실제 이식이 가능한 백엔드용 시스템 프롬프트 에셋을 추출 중입니다.
    </p>
    
    <div class="container mt-3" style="max-width: 600px;">
        <div class="progress" style="height: 25px;">
            <div id="progressBar" class="progress-bar progress-bar-striped progress-bar-animated bg-info" role="progressbar" style="width: 0%;">0%</div>
        </div>
        <div id="stageList" class="mt-4 text-start bg-dark p-3 rounded border border-secondary small">
            <div id="stage1" class="text-white-50 mb-2"><i class="bi bi-circle"></i> 1단계: 외국인 배우자 역사 소외 및 자녀 교육 단절 페인포인트 분석</div>
            <div id="stage2" class="text-white-50 mb-2"><i class="bi bi-circle"></i> 2단계: 역사 문화 공공데이터 매핑 및 맞춤형 스토리텔링 아키텍처 설계</div>
            <div id="stage3" class="text-white-50 mb-2"><i class="bi bi-circle"></i> 3단계: 단편적 교재 및 딱딱한 주입식 인강 대조군 대비 차별성 행렬 분석</div>
            <div id="stage4" class="text-white-50 mb-2"><i class="bi bi-circle"></i> 4단계: 지자체/가족센터 확산 모델 및 사회통합 정량적 기대효과 산출</div>
            <div id="stage5" class="text-white-50 mb-2"><i class="bi bi-circle"></i> 5단계: Flask/SQLite 연동용 개인화 역사 스토리텔링 LLM 시스템 프롬프트 코드 구현</div>
        </div>
    </div>
</div>

<div class="container-fluid">
    <div class="row">
        <div class="col-md-4 p-4 sidebar">
            <h4 class="mb-3 text-light d-flex align-items-center fw-bold">
                <i class="bi bi-book-half text-info me-2"></i> 한누리(Hannuri) 빌더 v3
            </h4>
            <p class="small text-muted mb-4">문체부 공공데이터를 융합하여 외국인 배우자가 한국의 역사를 학습하고 자녀에게 직접 스토리텔링할 수 있는 차세대 플랫폼 설계기입니다.</p>

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
                    <input type="text" id="industry" class="form-control bg-secondary text-white" value="문화 데이터 X 다문화가족 역사 문화 교육">
                </div>
                <div class="mb-3">
                    <label class="form-label">분석 플랫폼 핵심 주제</label>
                    <input type="text" id="topic" class="form-control bg-secondary text-white" value="AI 기반 다문화 가정을 위한 맞춤형 한국 역사-문화 스토리텔링 가이드 '한누리'">
                </div>
                <div class="mb-3">
                    <label class="form-label">대조군 서비스</label>
                    <input type="text" id="competitor" class="form-control bg-secondary text-white" value="단순 귀화 시험용 주입식 역사 교재 및 비개인화 한국사 인터넷 강의">
                </div>
                <div class="mb-3">
                    <label class="form-label">공식 기획서 타이틀</label>
                    <input type="text" id="title" class="form-control bg-secondary text-white" value="문화 공공데이터 기반 AI 다문화 가정 맞춤형 한국 역사 스토리텔링 플랫폼: 한누리(Hannuri)">
                </div>
                
                <button type="button" onclick="startDeepSearch()" class="btn btn-info w-100 fw-bold text-white shadow">
                    <i class="bi bi-cpu-fill"></i> 기획 및 역사 교육 프롬프트 산출
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
                    <span class="badge badge-industry shadow-sm"><i class="bi bi-journal-bookmark-fill"></i> {{ current_report[2] }}</span>
                    <small class="text-muted"><i class="bi bi-clock-history"></i> 역사 데이터 싱크 마스터: {{ current_report[6] }}</small>
                </div>
                <h2 class="fw-bold text-dark mb-4" id="reportTitle">{{ current_report[1] }}</h2>
                
                <div class="action-bar">
                    <button class="btn btn-outline-primary btn-sm fw-bold" onclick="copyMarkupToClipboard()">
                        <i class="bi bi-clipboard-plus"></i> HTML 마크업 복사
                    </button>
                    <button class="btn btn-success btn-sm fw-bold text-white" onclick="downloadHtmlDocument()">
                        <i class="bi bi-file-earmark-arrow-down-fill"></i> HTML 파일로 저장
                    </button>
                </div>

                <div id="copyAlert" class="alert alert-success p-2 small mb-3 text-center d-none fw-bold" role="alert">
                    <i class="bi bi-check2-circle"></i> 마크업 소스코드가 클립보드에 성공적으로 복사되었습니다! 그대로 활용하세요.
                </div>

                <div class="report-view shadow-sm mb-5" id="reportRawContainer">
                    {{ current_report[5]|safe }}
                </div>

                <div class="card border-info shadow-sm mt-5">
                    <div class="card-header bg-dark text-info fw-bold d-flex justify-content-between align-items-center">
                        <span><i class="bi bi-code-slash"></i> 🔍 데이터 파이프라인 실시간 컨텍스트 및 교육용 프롬프트 디버거</span>
                        <span class="badge bg-info text-dark">v3.0 역사 RAG</span>
                    </div>
                    <div class="card-body">
                        <p class="text-muted small">각 빌드 단계별 시스템 수집 프롬프트와 백엔드 소스에 적용 가능한 역사 맞춤형 에이전트 프롬프트 원본을 검증할 수 있습니다.</p>
                        
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
                                            <h6 class="text-primary fw-bold" style="font-size:0.85rem;"><i class="bi bi-chevron-right"></i> 시스템 오케스트레이션 및 프롬프트 명령 구조</h6>
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
                    <i class="bi bi-mortarboard text-secondary" style="font-size: 5rem;"></i>
                    <h4 class="mt-4 fw-bold">활성화된 역사 교육 기획서가 없습니다.</h4>
                    <p>좌측의 테마 변수를 확인하고 기획 및 프롬프트 산출 버튼을 클릭해 주세요.</p>
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
            
            combinedContent += result.content + "<hr class='my-5 border-info'>";
            updateStageUI(stage, 'success');
            
            let progressPercentage = stage * 20;
            document.getElementById('progressBar').style.width = progressPercentage + '%';
            document.getElementById('progressBar').innerText = progressPercentage + '%';
        } catch (err) {
            alert("백엔드 엔진 연결 실패: " + err);
            closeOverlay();
            return;
        }
    }

    document.getElementById('statusTitle').innerText = "최종 역사 교육 보고서 마스터 데이터 바인딩 중...";
    const saveResponse = await fetch('/save_final', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...data, full_content: combinedContent })
    });
    
    const saveResult = await saveResponse.json();
    if(saveResult.success) {
        location.href = `/${saveResult.new_id}`;
    } else {
        alert("기획서 저장에 실패했습니다.");
        closeOverlay();
    }
}

function updateStageUI(stage, status) {
    const stageEl = document.getElementById(`stage${stage}`);
    if (status === 'processing') {
        document.getElementById('statusTitle').innerText = `${stage}단계 컨텍스트 연산 및 교육 모델 설계 중...`;
        stageEl.className = "text-warning fw-bold mb-2";
        stageEl.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span> [구동 중] 사료 데이터 세그먼트 파싱 및 링킹 중...`;
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

/* 신규 이식: 마크업 코드 클립보드 복사 액션 스크립트 */
function copyMarkupToClipboard() {
    const container = document.getElementById('reportRawContainer');
    if (!container) return;
    
    // 이너 HTML 코드를 수집하여 클립보드에 이식
    const rawHtmlContent = container.innerHTML.trim();
    
    navigator.clipboard.writeText(rawHtmlContent).then(() => {
        const alertBox = document.getElementById('copyAlert');
        alertBox.classList.remove('d-none');
        setTimeout(() => {
            alertBox.classList.add('d-none');
        }, 3500);
    }).catch(err => {
        alert('클립보드 복사 중 실패가 발생했습니다: ' + err);
    });
}

/* 신규 이식: HTML 단독 정적 문서 클라이언트 다운로드 액션 스크립트 */
function downloadHtmlDocument() {
    const title = document.getElementById('reportTitle').innerText.trim() || 'Hannuri_Report';
    const container = document.getElementById('reportRawContainer');
    if (!container) return;
    
    const content = container.innerHTML;
    
    // 독립형 정적 뷰가 가능하도록 Bootstrap CDN을 포함한 고품질 웹 문서로 가공
    const fullHtmlTemplate = `<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>\${title}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { padding: 50px; background-color: #f8fafc; font-family: sans-serif; }
        .container-box { background: white; padding: 40px; border: 1px solid #e2e8f0; border-radius: 12px; max-width: 1000px; margin: 0 auto; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
        table { width: 100%; margin: 20px 0; border-collapse: collapse; }
        th { background-color: #f0f9ff; color: #0369a1; padding: 12px; border: 1px solid #bae6fd; text-align: center; }
        td { padding: 12px; border: 1px solid #e2e8f0; }
        pre { background: #1e1e1e; color: #d4d4d4; padding: 15px; border-radius: 6px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container-box">
        <h1 style="font-weight: bold; margin-bottom: 30px; border-bottom: 2px solid #0284c7; padding-bottom: 15px;">\${title}</h1>
        \${content}
    </div>
</body>
</html>`;

    const blob = new Blob([fullHtmlTemplate], { type: 'text/html;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement("a");
    link.href = url;
    link.download = `\${title.replace(/[\/:*?"<>|]/g, "_")}.html`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}
</script>
</body>
</html>
"""

# ==========================================
# 3. 백엔드 컨트롤러 (역사 교육 테마 커스텀 프롬프트 파이프라인)
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
        1: "제안 배경, 다문화 가구 내 한국사 소외 및 자녀 교육 연계 필요성",
        2: "역사/문화 공공데이터 활용 설계 및 초개인화 스토리텔링 아키텍처",
        3: "기존 단편적 역사 교재 대조군 대비 차별화 비교 행렬 및 독창성 분석",
        4: "B2G 확산 로드맵 및 사회 통합 기여도 정량적 기대효과 지표 산출",
        5: "Flask/SQLite 환경 배포 서비스 탑재용 백엔드 LLM 역사 교육 시스템 프롬프트"
    }
    stage_title = stage_titles.get(stage, "미정의 단계")

    system_prompt = (
        "너는 문화체육관광부 공공데이터 분석 경진대회에서 대상(대통령상)을 목표로 에듀테크 및 다문화 복지 정책 기획서를 작성하는 "
        "국내 최고 수준의 AI 역사 문화 교육 융합 전문가야. "
        "모든 문서 구조는 심사위원과 개발자 집단을 동시에 설득할 수 있도록 명확한 비즈니스 프레임워크와 에듀테크 파라미터를 동반해야 해. "
        "마크다운 문법(예: ```html, ```, #, **)은 절대 출력에 섞지 말고, "
        "바로 HTML 렌더링에 사용할 수 있는 순수 웹 컴포넌트 마크업(<h1>, <h4>, <p>, <table>, <pre>, <code> 등)만 가공하여 출력하라."
    )

    if stage == 1:
        prompt = (
            f"주제인 [{topic}] 플랫폼의 '1. 제안 배경 및 필요성(Pain Point)' 영역을 작성해줘. "
            f"국내 다문화 가정이 겪는 커다란 소외 장벽 중 하나인 '한국의 역사와 문화 지식 부족'을 다루어야 해. "
            f"외국인 배우자가 한국사 지식이 부족해 성장하는 자녀의 질문에 답하지 못해 소외감을 느끼는 페인포인트를 짚어줘. "
            f"기존의 단순 국적 취득용 암기식 한국사가 아닌, 정서적 유대감을 높이고 자녀 양육의 주체로 우뚝 설 수 있게 돕는 "
            f"역사 중심 문화 융합 교육의 국가적 시급성과 공익성을 논리적으로 서술해줘. 소제목은 <h4>, 본문은 <p> 태그를 사용해줘."
        )
    elif stage == 2:
        prompt = (
            f"[{topic}]의 '2. 역사 문화 공공데이터 활용 및 AI 아키텍처 설계' 장을 구성해줘. "
            f"활용할 핵심 데이터 소스인 "
            f"① 국립중앙박물관 유물 및 소장품 데이터 API, ② 국사편찬위원회 한국사데이터베이스 사료 정보, "
            f"③ 한국학중앙연구원 향토문화전자대전 인물/지리 정보, ④ 국립국어원 다국어 대역사전 데이터를 명확히 기재해줘. "
            f"이 공공데이터들을 활용해 LLM 기반 AI가 외국인 배우자의 출신 국가(예: 베트남, 필리핀 등) 역사 속 유사 사건이나 인물과 매핑하여 "
            f"한국 역사를 직관적으로 이해시키는 '초개인화 상호주의 역사 스토리텔링' 생성 파이프라인을 보여줘."
        )
    elif stage == 3:
        prompt = (
            f"[{topic}]가 기존 대조군 솔루션인 [{competitor}] 대비 가진 탁월성을 입증하는 '3. 서비스 독창성 및 우위성' 장을 작성해줘. "
            f"반드시 <table class='table table-bordered table-striped text-center'>"
            f"<thead><tr><th>구분</th><th>귀화 시험용 역사 교재</th><th>일반 한국사 인강</th><th>한누리(Hannuri) (본 기획)</th></tr></thead>"
            f"형태의 표를 빌드해줘. 데이터 신뢰도(공공 사료 연계), 외국인 모국 역사와의 비교 분석 기능 유무, 자녀 교육/양육 활용성, "
            f"학습 난이도 조정(다국어 번역 및 한글 숙련도 매칭), 에듀테크 공익성의 5가지 차원 비교를 완벽히 채우고 독창성을 설명해줘."
        )
    elif stage == 4:
        prompt = (
            f"[{topic}]의 '4. 기대효과 및 향후 비즈니스/확산 방안'을 도출해줘. "
            f"정량적 효과(다문화 가구의 한국 사회 정착 만족도 증가율, 자녀 역사 교육 공백 해소율, 다문화 센터 보급률 등)와 "
            f"정성적 효과(다문화 가정 내 정서적 고립 완화, 진정한 의미의 다문화 사회 통합)를 구조화해줘. "
            f"더불어 B2G 확산 방안으로 전국 가족센터(다문화가족지원센터) 표준 교육 패키지 채택 및 "
            f"박물관/유적지 연계 역사 탐방 다문화 패밀리 O2O 바우처 모델을 깔끔한 HTML 구조로 출력해줘."
        )
    elif stage == 5:
        prompt = (
            f"[{topic}] 플랫폼을 실제 Python Flask와 SQLite 환경에서 개발할 때, 역사 콘텐츠 생성을 전담하는 "
            f"'5. 서비스 코어 이식용 AI 시스템 프롬프트(Few-Shot Engineering) 명세서' 장을 빌드해줘. "
            f"Flask 백엔드 내부에서 인공지능 모델을 호출할 때 사용할 구체적인 `SYSTEM_PROMPT`와 `USER_INPUT_STRUCTURE`를 설계해줘. "
            f"프롬프트 내부에는 반드시 [사용자 입력 가변값: spouse_nationality, korean_level, child_age, target_era(시대)] 파라미터가 매핑되어야 하며, "
            f"예시로 '베트남 출신/한국어 초급/7세 자녀를 둔 배우자에게 세종대왕의 한글 창제 역사를 베트남의 쯔놈(Chữ Nôm) 문자 역사와 비교하며 "
            f"어린이 눈높이로 풀어주도록 지시하는 Few-Shot 규칙 가이드라인'을 "
            f"<pre><code class='text-info bg-dark p-3 d-block rounded'> 태그 내부에 소스코드 형태로 담아내어 개발 가능성을 증명해줘."
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
    flash("역사 교육 기획서 및 파이프라인 로그가 초기화되었습니다.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    # 포트 충돌 방지를 위해 고유 포트 50012 번으로 배포
    app.run(host="0.0.0.0", port=50008, debug=True)