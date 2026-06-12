import sqlite3
import requests
import json
import uuid
from datetime import datetime
from flask import Flask, request, render_template_string, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = "mcst_culture_data_mother_all_investment_secret_key"

DB_NAME = "mother_all_investment.db"
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
LM_STUDIO_MODELS_URL = "http://localhost:1234/v1/models"

# ==========================================
# 1. 데이터베이스 초기화 (마스터 데이터 아키텍처)
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
# 2. UI/UX 템플릿 (인베스트먼트 뷰어 & 저장/복사 액션 포함)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>K-컬처 육아 통합 내비게이션 [모아] 투자 유치형 마스터 빌더</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        body { background-color: #f1f5f9; font-family: 'Pretendard', sans-serif; }
        .sidebar { background: #0f172a; color: #f8fafc; min-height: 100vh; border-right: 1px solid #334155; }
        .sidebar .form-label { color: #cbd5e1; font-weight: 500; font-size: 0.85rem; }
        .main-content { min-height: 100vh; background-color: #f8fafc; }
        .report-view { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 45px; box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.05); position: relative; }
        .badge-investment { background-color: #db2777; color: white; font-size: 0.85rem; padding: 6px 14px; border-radius: 30px; font-weight: 600; }
        .list-group-item { background: #1e293b; border: 1px solid #334155; color: #cbd5e1; cursor: pointer; transition: all 0.2s; }
        .list-group-item:hover { background: #334155; color: #ffffff; }
        .list-group-item.active { background: #db2777; border-color: #db2777; color: white; }
        
        .report-view table { width: 100%; margin: 25px 0; border-collapse: collapse; font-size: 0.9rem; }
        .report-view th { background-color: #fdf2f8; color: #9d174d; padding: 14px; border: 1px solid #fbcfe8; text-align: center; font-weight: 700; }
        .report-view td { padding: 14px; border: 1px solid #e2e8f0; vertical-align: middle; }
        
        .loading-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15, 23, 42, 0.96); z-index: 9999; justify-content: center; align-items: center; color: white; }
        .log-code { max-height: 280px; background-color: #1e1e1e; color: #e2e8f0; font-family: 'Consolas', monospace; font-size: 0.85rem; padding: 15px; border-radius: 8px; overflow-y: auto; border: 1px solid #475569; }
        
        .action-bar { border-bottom: 2px solid #f1f5f9; padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: flex-end; gap: 12px; }
        .btn-action-copy { background-color: #ffffff; color: #475569; border: 1px solid #cbd5e1; font-weight: 600; }
        .btn-action-copy:hover { background-color: #f8fafc; color: #1e293b; border-color: #94a3b8; }
        .btn-action-save { background-color: #db2777; color: #ffffff; border: none; font-weight: 600; }
        .btn-action-save:hover { background-color: #be185d; color: #ffffff; }
    </style>
</head>
<body>

<div id="loadingOverlay" class="loading-overlay flex-column">
    <div class="spinner-border text-pink mb-4" style="width: 3.5rem; height: 3.5rem; color: #db2777;" role="status"></div>
    <h4 id="statusTitle" class="fw-bold text-light">투자 유치형 마스터 파이프라인 연산 중...</h4>
    <p id="statusDesc" class="text-muted text-center px-4" style="max-width: 550px;">
        국립민속박물관 일생의례 사료, 전국 지자체 육아종합지원센터 API 융합 설계 모델 및 Flask 이식용 다국어 맥락 필터링 시스템 프롬프트를 통합 엔지니어링 중입니다.
    </p>
    
    <div class="container mt-3" style="max-width: 650px;">
        <div class="progress" style="height: 25px; border-radius: 8px;">
            <div id="progressBar" class="progress-bar progress-bar-striped progress-bar-animated bg-danger" role="progressbar" style="width: 0%; background-color: #db2777 !important;">0%</div>
        </div>
        <div id="stageList" class="mt-4 text-start bg-dark p-3 rounded border border-secondary small">
            <div id="stage1" class="text-white-50 mb-2"><i class="bi bi-circle"></i> 1단계: 다문화 가구 독박육아/문화고립 페인포인트 및 시장성 검증</div>
            <div id="stage2" class="text-white-50 mb-2"><i class="bi bi-circle"></i> 2단계: 문체부 전통문화 에셋 X 지자체 실시간 API 매시업 아키텍처 설계</div>
            <div id="stage3" class="text-white-50 mb-2"><i class="bi bi-circle"></i> 3단계: 단편적 단순 번역기 및 주입식 교재 대조군 대비 탁월성 행렬 도출</div>
            <div id="stage4" class="text-white-50 mb-2"><i class="bi bi-circle"></i> 4단계: B2G SaaS 라이선스 및 B2B 타겟 커머스/데이터 파이프라인 지속 가능 BM 수립</div>
            <div id="stage5" class="text-white-50 mb-2"><i class="bi bi-circle"></i> 5단계: Flask/SQLite 환경 탑재용 문화 맥락 의역 다국어 LLM 시스템 프롬프트 코드 구현</div>
        </div>
    </div>
</div>

<div class="container-fluid">
    <div class="row">
        <div class="col-md-4 p-4 sidebar">
            <h4 class="mb-3 text-light d-flex align-items-center fw-bold">
                <i class="bi bi-shield-check text-danger me-2" style="color: #db2777 !important;"></i> 모아 (Mother-All) 빌더
            </h4>
            <p class="small text-muted mb-4">최고의 투자 컨설턴트 시각에서 문체부 경진대회 대상(대통령상)을 저격할 수 있도록 공공데이터의 기술적 융합과 초우량 비즈니스 스케일업 전략을 모델링합니다.</p>

            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    {% for message in messages %}
                        <div class="alert alert-pink alert-dismissible fade show bg-dark text-white border-secondary" role="alert">
                            {{ message }}
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="alert" aria-label="Close"></button>
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}

            <div class="bg-dark p-3 rounded mb-4 border border-secondary">
                <div class="mb-3">
                    <label class="form-label">산업 도메인 및 타겟 마켓</label>
                    <input type="text" id="industry" class="form-control bg-secondary text-white" value="공공 문화 데이터 X 다국어 AI 에듀테크 X 지자체 육아 행정">
                </div>
                <div class="mb-3">
                    <label class="form-label">혁신 플랫폼 프로젝트명</label>
                    <input type="text" id="topic" class="form-control bg-secondary text-white" value="K-컬처 육아 통합 내비게이션 '모아(Mother-All)'">
                </div>
                <div class="mb-3">
                    <label class="form-label">대조군 서비스 모델</label>
                    <input type="text" id="competitor" class="form-control bg-secondary text-white" value="일반 단편적인 번역 전용 애플리케이션 및 지자체별 파편화된 웹사이트 사이일">
                </div>
                <div class="mb-3">
                    <label class="form-label">마스터 기획안 공식 타이틀</label>
                    <input type="text" id="title" class="form-control bg-secondary text-white" value="다문화 가정을 위한 한국 전통 문화 기반 맞춤형 AI 육아 크루즈: 모아(Mother-All)">
                </div>
                
                <button type="button" onclick="startDeepSearch()" class="btn btn-danger w-100 fw-bold shadow-lg" style="background-color: #db2777; border:none;">
                    <i class="bi bi-graph-up-arrow"></i> 마스터 기획 및 백엔드 프롬프트 빌드
                </button>
            </div>

            <h5 class="text-muted pt-2 mb-3" style="font-size: 0.9rem;">작성 완료된 기획안 아카이브 ({{ reports|length }})</h5>
            <div class="list-group overflow-auto" style="max-height: 250px;">
                {% for r in reports %}
                    <div class="list-group-item d-flex justify-content-between align-items-start p-2 {% if current_report and current_report[0] == r[0] %}active{% endif %}">
                        <div class="ms-2 me-auto text-truncate" onclick="location.href='{{ url_for('index', report_id=r[0]) }}'" style="max-width:85%;">
                            <div class="fw-bold text-truncate" style="font-size:0.85rem;">{{ r[1] }}</div>
                            <small class="text-muted" style="font-size:0.75rem;">{{ r[6] }}</small>
                        </div>
                        <form action="{{ url_for('delete_competition', report_id=r[0]) }}" method="POST">
                            <button type="submit" class="btn btn-link text-danger p-0 border-0"><i class="bi bi-trash3-fill"></i></button>
                        </form>
                    </div>
                {% endfor %}
            </div>
        </div>

        <div class="col-md-8 p-5 main-content">
            {% if current_report %}
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <span class="badge badge-investment shadow-sm"><i class="bi bi-gem"></i> Investment Grade: GRADE A+</span>
                    <small class="text-muted"><i class="bi bi-database-check"></i> 타임스탬프: {{ current_report[6] }}</small>
                </div>
                <h2 class="fw-bold text-dark mb-4" id="reportTitle">{{ current_report[1] }}</h2>
                
                <div class="action-bar">
                    <button class="btn btn-action-copy btn-sm" onclick="copyMarkupToClipboard()">
                        <i class="bi bi-clipboard2-code-fill text-primary"></i> HTML 소스 코드 복사
                    </button>
                    <button class="btn btn-action-save btn-sm" onclick="downloadHtmlDocument()">
                        <i class="bi bi-cloud-arrow-down-fill"></i> 정적 웹 문서 다운로드
                    </button>
                </div>

                <div id="copyAlert" class="alert alert-primary p-2 small mb-3 text-center d-none fw-bold shadow-sm" role="alert">
                    <i class="bi bi-patch-check-fill"></i> 마크업 원본 데이터가 성공적으로 복사되었습니다! 개발 소스나 보고서 서식에 즉시 복사하여 사용하세요.
                </div>

                <div class="report-view shadow-sm mb-5" id="reportRawContainer">
                    {{ current_report[5]|safe }}
                </div>

                <div class="card border-secondary shadow-sm mt-5">
                    <div class="card-header bg-dark text-white fw-bold d-flex justify-content-between align-items-center">
                        <span class="text-pink" style="color: #f472b6;"><i class="bi bi-cpu"></i> 링킹 디버거: 실시간 컨텍스트 데이터 추적기</span>
                        <span class="badge bg-secondary">V3 마스터 에이전트</span>
                    </div>
                    <div class="card-body bg-light">
                        <p class="text-muted small">각 다단계 파이프라인에서 추출된 시스템 구조 가이드와 심사위원을 매료시킨 실제 백엔드 소스 전용 Few-Shot 텍스트 자산을 파악할 수 있습니다.</p>
                        
                        <div class="accordion" id="accordionLogs">
                            {% for log in logs %}
                            <div class="accordion-item">
                                <h2 class="accordion-header" id="heading{{ log[0] }}">
                                    <button class="accordion-button collapsed fw-bold" type="button" data-bs-toggle="collapse" data-bs-target="#collapse{{ log[0] }}" aria-expanded="false" aria-controls="collapse{{ log[0] }}">
                                        <strong>[{{ log[3] }}단계 매퍼] {{ log[4] }}</strong>
                                    </button>
                                </h2>
                                <div id="collapse{{ log[0] }}" class="accordion-collapse collapse" aria-labelledby="heading{{ log[0] }}" data-bs-parent="#accordionLogs">
                                    <div class="accordion-body bg-dark">
                                        <div class="mb-3">
                                            <h6 class="text-info fw-bold" style="font-size:0.85rem;"><i class="bi bi-arrow-right-circle"></i> 투자 컨설턴트 지시 프롬프트 오케스트레이션</h6>
                                            <pre class="log-code">{{ log[5] }}</pre>
                                        </div>
                                        <div class="mb-3">
                                            <h6 class="text-success fw-bold" style="font-size:0.85rem;"><i class="bi bi-arrow-right-circle"></i> 컴파일된 마크업 결과 데이터 (Pure HTML)</h6>
                                            <pre class="log-code text-light">{{ log[6] }}</pre>
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
                    <i class="bi bi-safe2 text-secondary" style="font-size: 5.5rem; color: #cbd5e1 !important;"></i>
                    <h4 class="mt-4 fw-bold text-dark">활성화된 마스터 투자 기획서가 없습니다.</h4>
                    <p>좌측 도메인 세그먼트를 튜닝하고 통합 연산 버튼을 작동시켜 주십시오.</p>
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
                alert("기획 파이프라인 빌딩 프로세스 내부 에러: " + result.error);
                closeOverlay();
                return;
            }
            
            combinedContent += result.content + "<hr class='my-5' style='border-top: 2px dashed #db2777;'>";
            updateStageUI(stage, 'success');
            
            let progressPercentage = stage * 20;
            document.getElementById('progressBar').style.width = progressPercentage + '%';
            document.getElementById('progressBar').innerText = progressPercentage + '%';
        } catch (err) {
            alert("LLM 로컬 컴파일러 오프라인 상태 점검 요망: " + err);
            closeOverlay();
            return;
        }
    }

    document.getElementById('statusTitle').innerText = "기획서 데이터베이스 인덱싱 및 무결성 영속화 중...";
    const saveResponse = await fetch('/save_final', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...data, full_content: combinedContent })
    });
    
    const saveResult = await saveResponse.json();
    if(saveResult.success) {
        location.href = `/${saveResult.new_id}`;
    } else {
        alert("기획 데이터 정형 스토리지 커밋 실패.");
        closeOverlay();
    }
}

function updateStageUI(stage, status) {
    const stageEl = document.getElementById(`stage${stage}`);
    if (status === 'processing') {
        document.getElementById('statusTitle').innerText = `${stage}단계 투자 유치 핵심 데이터 합성 중...`;
        stageEl.className = "text-warning fw-bold mb-2";
        stageEl.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span> [연산중] 비즈니스 프레임워크 밸런싱 및 아키텍처 토큰 연산 중...`;
    } else if (status === 'success') {
        stageEl.className = "text-success mb-2";
        stageEl.innerHTML = `<i class="bi bi-check-circle-fill me-2" style="color:#22c55e;"></i> [빌드완료] 심사 지표 매핑 세그먼트 적재 완료`;
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

function copyMarkupToClipboard() {
    const container = document.getElementById('reportRawContainer');
    if (!container) return;
    
    const rawHtmlContent = container.innerHTML.trim();
    
    navigator.clipboard.writeText(rawHtmlContent).then(() => {
        const alertBox = document.getElementById('copyAlert');
        alertBox.classList.remove('d-none');
        setTimeout(() => {
            alertBox.classList.add('d-none');
        }, 4000);
    }).catch(err => {
        alert('클립보드 접근 권한 에러: ' + err);
    });
}

function downloadHtmlDocument() {
    const title = document.getElementById('reportTitle').innerText.trim() || 'Mother_All_Investment_Plan';
    const container = document.getElementById('reportRawContainer');
    if (!container) return;
    
    const content = container.innerHTML;
    
    const fullHtmlTemplate = `<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>\${title}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { padding: 60px; background-color: #f1f5f9; font-family: system-ui, -apple-system, sans-serif; color: #1e293b; }
        .master-box { background: #ffffff; padding: 50px; border: 1px solid #e2e8f0; border-radius: 16px; max-width: 1100px; margin: 0 auto; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); }
        table { width: 100%; margin: 25px 0; border-collapse: collapse; }
        th { background-color: #fdf2f8; color: #9d174d; padding: 14px; border: 1px solid #fbcfe8; text-align: center; font-weight: bold; }
        td { padding: 14px; border: 1px solid #e2e8f0; vertical-align: middle; }
        pre { background: #1e1e1e; color: #e2e8f0; padding: 18px; border-radius: 8px; overflow-x: auto; border: 1px solid #334155; }
        h4 { color: #db2777; font-weight: 700; margin-top: 30px; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="master-box">
        <h1 style="font-weight: 800; margin-bottom: 35px; border-bottom: 3px solid #db2777; padding-bottom: 20px; color:#0f172a;">\${title}</h1>
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
# 3. 백엔드 컨트롤러 (투자 마스터 파이프라인 아키텍처)
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
        1: "Executive Summary & 유저 페인포인트 다각도 정밀 분석",
        2: "문체부 공공데이터 자산 링킹 매시업 아키텍처 매트릭스 도출",
        3: "기존 단편 번역앱/파편화 사이트 대조군 대비 핵심 우위 차별성 행렬",
        4: "B2G 행정 SaaS 및 B2B 커머스/비식별 데이터 API 지속 가능 수익 모델",
        5: "Flask/SQLite 연동용 다국어 문화 맥락 의역 처리 코어 시스템 프롬프트"
    }
    stage_title = stage_titles.get(stage, "미정의 단계")

    system_prompt = (
        "너는 문체부 공공데이터 활용 경진대회에서 대통령상(대상) 수상을 확정 짓고, 벤처캐피탈(VC) 심사역들의 투자 확약을 받아내는 "
        "국내 최고 역량의 컴퍼니 빌더이자 테크니컬 소프트웨어 아키텍트야. "
        "모든 문서 결과물은 정부 지원금 심사기준(공익성, 데이터 융합성)과 투자사 심사기준(시장성, 스케일업 파괴력)을 동시 관통해야 해. "
        "마크다운 문법(예: ```html, ```, #, **)은 절대 출력에 섞지 말고, "
        "바로 HTML 렌더링에 사용할 수 있는 순수 웹 컴포넌트 마크업(<h4>, <p>, <table>, <pre>, <code> 등)만 가공하여 출력하라."
    )

    if stage == 1:
        prompt = (
            f"주제인 [{topic}] 플랫폼의 '1. Executive Summary 및 고도화된 Pain-Point 분석' 장을 작성해줘. "
            f"초저출산 정국 속에서 지속 증가하는 다문화 가구의 '독박 육아'와 '문화 고립'을 해결하는 거시적 환경 가치를 명시하고, "
            f"전래동화, 백일/돌잔치 등 한국인에겐 상식이나 이주 여성에겐 장벽인 전통 육아 문화 비대칭 요소를 정밀하게 짚어줘. "
            f"소제목은 <h4> 태그, 본문은 고품격 컨설팅 어조의 <p> 태그를 사용해줘."
        )
    elif stage == 2:
        prompt = (
            f"[{topic}]의 '2. 데이터 아키텍처 및 공공 데이터 자산 융합 스택' 장을 빌드해줘. "
            f"반드시 다음 5가지 원천 데이터를 명확히 매핑해줘: "
            f"① 국립민속박물관/국립국악원의 일생의례(백일, 돌, 명절) 및 전래동화/자장가 음원 데이터, "
            f"② 문화포털의 전국 지자체 문화행사 영유아 동선 API, "
            f"③ 육아정책연구소/보건복지부의 월령별 발달 표준 및 필수 예방접종 가이드, "
            f"④ 전국 지자체 육아종합지원센터의 장난감 도서관 잔여 수량 및 놀이체험실 실시간 예약 연동 API, "
            f"⑤ 여성가족부 가족센터의 다문화 멘토링 프로그램 데이터. "
            f"이들이 융합되어 어떻게 초개인화 육아 타임라인 푸시와 서류 작성 도우미로 진화하는지 명세서를 작성해줘."
        )
    elif stage == 3:
        prompt = (
            f"[{topic}]가 기존 대조군 솔루션인 [{competitor}] 대비 가진 압도적 경쟁력을 증명하는 '3. 서비스 독창성 및 대조군 비교 행렬' 장을 기술해줘. "
            f"반드시 <table class='table table-bordered table-striped text-center'>"
            f"<thead><tr><th>평가 차원</th><th>단편적 번역 애플리케이션</th><th>파편화된 지자체 사이트</th><th>모아 (Mother-All) (본 사업)</th></tr></thead>"
            f"형태의 표를 완전하게 구현해줘. 비교 차원은 '문화적 맥락 의역 수준', '실시간 지자체 API 결합도', '자녀 생애주기별 푸시 자동화', "
            f"'행정 서류 원클릭 자동 작성', 'B2G 확장성'의 5가지를 명확하게 크로스 체크하여 작성해줘."
        )
    elif stage == 4:
        prompt = (
            f"[{topic}]의 '4. 지속 가능한 비즈니스 모델(BM) 및 스케일업 로드맵' 장을 작성해줘. "
            f"B2G 영역에서 여성가족부 및 전국 지자체 대상 '다문화 가구 관리 및 알림 소통 효율화 SaaS 플랫폼' 라이선스 공급 모델(행정비용 60% 절감)과 "
            f"바우처 연동 수수료 구조를 기술해줘. B2B 영역에서는 국내 대형 유아용품 제조사 대상 비식별 육아 패턴 데이터 API 매매 및 "
            f"K-푸드/K-육아용품 커머스 중개 수수료 확보 방안을 구조화해줘. "
            f"향후 전 세계 한인 디아스포라 대상 역방향 서비스 확장 로드맵까지 포함해줘."
        )
    elif stage == 5:
        prompt = (
            f"[{topic}] 플랫폼을 실제 Python Flask 백엔드 환경에서 SQLite와 연동하여 구동할 때, "
            f"단순 직역을 넘어 한국의 육아 은어/관용구('우쭈쭈', '등센서', '돌치레' 등)를 이주여성의 문화 배경에 맞추어 "
            f"완벽하게 의역해 내는 '5. 서비스 코어 탑재용 AI 시스템 프롬프트(Few-Shot Engineering) 명세서' 장을 빌드해줘. "
            f"개발자가 코드에 바로 적용할 수 있도록 `SYSTEM_PROMPT` 정의와 `USER_INPUT_STRUCTURE` 가변 파라미터 "
            f"[spouse_nationality, language, child_age_months, localized_idiom] 구조를 포함해줘. "
            f"또한, 베트남 국적의 초보 엄마 유저에게 '등센서 작동' 및 '백일 떡 돌리기' 문화 맥락을 매끄럽게 번역 및 자동 안내 큐레이션을 지시하는 "
            f"실제 프롬프트 에셋 예시를 <pre><code class='text-danger bg-dark p-3 d-block rounded'> 태그 내부에 누락 없이 명시해줘."
        )
    else:
        return jsonify({"success": False, "error": "인덱스 범위 초과"})

    active_model_name = get_active_model()

    payload = {
        "model": active_model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.25
    }

    try:
        response = requests.post(LM_STUDIO_URL, json=payload, timeout=590)
        response.raise_for_status()
        ai_output = response.json()["choices"][0]["message"]["content"]
        
        # 가끔 마크다운 코드 블록 태그 유출 방어 링 필터
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
    flash("선택하신 모아(Mother-All) 투자 기획 데이터 및 디버깅 로그가 초기화되었습니다.")
    return redirect(url_for("index"))


if __name__ == "__main__":
    # 포트 충돌 방지를 위해 고유 포트 50012 번으로 배포
    app.run(host="0.0.0.0", port=50008, debug=True)