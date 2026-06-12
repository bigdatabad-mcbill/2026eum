

SYSTEM_PROMPT = '''
당신은 한국과 베트남 전래동화를 기반으로 한 상생형 문화 교육 플랫폼 '도란도란 스토리 브릿지'의 AI 코어입니다.

[가변 파라미터]
- target_child_age: [3세, 5세, 7세, 10세] 중 하나
- dual_story_pair: [한국 전래동화, 베트남 전래동화]의 이름 (예: "흥부와 놀부", "Tấm Cám")
- tracking_language: [Korean, Vietnamese]
- feedback_level: [Basic, Intermediate, Advanced]

[작업 지시사항]

1. 아이가 읽는 이야기를 분석하여:
   - 한국어 발음 정확도를 평가하고 피드백을 제공합니다.
   - 베트남어 성조 문화적 특성을 부모와 함께 연주하듯 매칭합니다.

2. 한국과 베트남 전래동화의 구조적 유사성을 추출하여:
   - 등장인물, 갈등, 결말의 유사성 및 차이점을 분석합니다.
   - 두 이야기의 '닮은꼴' 요소를 시각적으로 제시합니다.

3. 피드백 방식은 다음과 같습니다:
   - [Basic]: 단순한 발음/성조 피드백
   - [Intermediate]: 구조적 유사성 비교 및 설명
   - [Advanced]: 문화적 맥락과 교육적 요소를 포함한 상세 분석

[예시]
- 파라미터: target_child_age=5, dual_story_pair=["흥부와 놀부", "Tấm Cám"], tracking_language=Korean, feedback_level=Intermediate
- 출력:
  - "흥부와 놀부"의 발음 정확도: "흥부"는 '흥부'로 발음이 잘 되었어요! 
  - "Tấm Cám"과의 비교: 두 이야기 모두 '부모의 죽음 후 어려운 삶'이라는 공통된 시작점이 있어요.
  - 문화적 유사성: 두 이야기 모두 '희망과 복수'의 주제를 담고 있어요.

[결론]
- AI는 아이의 나이와 언어, 피드백 레벨에 따라 맞춤형으로 읽기 및 문화 교육을 제공합니다.
- 부모는 아이가 이야기를 읽을 때 함께 성조와 의미를 배우며, 한국과 베트남의 전통 문화를 상호 이해할 수 있는 기회를 얻습니다.
'''  위 프로젝트을 단계별 개발기획 매뉴별 구성, 디자인, 기능별 코드 개발 단계을 매뉴 수 만큼, 테스트을 3번씩 만들고 개선하고 수정하는 순서로 개발을 수행하는데 토큰이 작은 LLM에서 사용하도록 개발 요청을 단계별로 나누어서 수행하도록 다음 코드을 수정해줘  import sqlite3
import requests
import json
import uuid
from datetime import datetime
from flask import Flask, request, render_template_string, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = "mcst_culture_data_doran_story_bridge_secret_key"

DB_NAME = "doran_story_bridge.db"
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
# 2. UI/UX 템플릿 (도란도란 스토리 브릿지 커스텀 뷰 테마)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>도란도란 스토리 브릿지 [투자 유치형 마스터 빌더]</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        body { background-color: #f8fafc; font-family: 'Pretendard', sans-serif; }
        .sidebar { background: #1e1b4b; color: #f8fafc; min-height: 100vh; border-right: 1px solid #4338ca; }
        .sidebar .form-label { color: #c7d2fe; font-weight: 500; font-size: 0.85rem; }
        .main-content { min-height: 100vh; background-color: #f1f5f9; }
        .report-view { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 45px; box-shadow: 0 10px 25px -5px rgb(0 0 0 / 0.05); position: relative; }
        .badge-investment { background-color: #6366f1; color: white; font-size: 0.85rem; padding: 6px 14px; border-radius: 30px; font-weight: 600; }
        .list-group-item { background: #312e81; border: 1px solid #4338ca; color: #e0e7ff; cursor: pointer; transition: all 0.2s; }
        .list-group-item:hover { background: #4338ca; color: #ffffff; }
        .list-group-item.active { background: #4f46e5; border-color: #4f46e5; color: white; }
        
        .report-view table { width: 100%; margin: 25px 0; border-collapse: collapse; font-size: 0.9rem; }
        .report-view th { background-color: #e0e7ff; color: #312e81; padding: 14px; border: 1px solid #c7d2fe; text-align: center; font-weight: 700; }
        .report-view td { padding: 14px; border: 1px solid #e2e8f0; vertical-align: middle; }
        
        .loading-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(30, 27, 75, 0.97); z-index: 9999; justify-content: center; align-items: center; color: white; }
        .log-code { max-height: 280px; background-color: #1e1e1e; color: #e2e8f0; font-family: 'Consolas', monospace; font-size: 0.85rem; padding: 15px; border-radius: 8px; overflow-y: auto; border: 1px solid #4338ca; }
        
        .action-bar { border-bottom: 2px solid #e2e8f0; padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: flex-end; gap: 12px; }
        .btn-action-copy { background-color: #ffffff; color: #4f46e5; border: 1px solid #c7d2fe; font-weight: 600; }
        .btn-action-copy:hover { background-color: #f5f3ff; color: #3730a3; border-color: #818cf8; }
        .btn-action-save { background-color: #4f46e5; color: #ffffff; border: none; font-weight: 600; }
        .btn-action-save:hover { background-color: #3730a3; color: #ffffff; }
    </style>
</head>
<body>

<div id="loadingOverlay" class="loading-overlay flex-column">
    <div class="spinner-border text-indigo mb-4" style="width: 3.5rem; height: 3.5rem; color: #818cf8;" role="status"></div>
    <h4 id="statusTitle" class="fw-bold text-light">상생형 에듀테크 마스터 파이프라인 연산 중...</h4>
    <p id="statusDesc" class="text-muted text-center px-4" style="max-width: 550px;">
        국립국악원/KF 아세안문화원의 닮은꼴 전래동화 사료 매핑, 국립민속박물관 일생의례 데이터 기반 생활 문화 퀘스트 및 늘봄학교 B2G 비즈니스 모델을 조합하는 중입니다.
    </p>
    
    <div class="container mt-3" style="max-width: 650px;">
        <div class="progress" style="height: 25px; border-radius: 8px;">
            <div id="progressBar" class="progress-bar progress-bar-striped progress-bar-animated bg-indigo" role="progressbar" style="width: 0%; background-color: #4f46e5 !important;">0%</div>
        </div>
        <div id="stageList" class="mt-4 text-start bg-dark p-3 rounded border border-secondary small">
            <div id="stage1" class="text-white-50 mb-2"><i class="bi bi-circle"></i> 1단계: 7~10세 아동의 문화적 소외 해소 및 상호 문화 이해 시장성 분석</div>
            <div id="stage2" class="text-white-50 mb-2"><i class="bi bi-circle"></i> 2단계: 문체부 구비설화 X 아세안문화원 닮은꼴 동화 X 일생의례 데이터 아키텍처</div>
            <div id="stage3" class="text-white-50 mb-2"><i class="bi bi-circle"></i> 3단계: 딱딱한 주입식 한국어 교육 대조군 대비 독창성 및 우위성 행렬 도출</div>
            <div id="stage4" class="text-white-50 mb-2"><i class="bi bi-circle"></i> 4단계: 늘봄학교 커리큘럼 라이선스(B2G) 및 친환경 O2O 교구재(B2C) 수익 모델 수립</div>
            <div id="stage5" class="text-white-50 mb-2"><i class="bi bi-circle"></i> 5단계: Flask/SQLite 탑재용 한국-베트남 이중언어 분석 및 상호주의 시스템 프롬프트 구현</div>
        </div>
    </div>
</div>

<div class="container-fluid">
    <div class="row">
        <div class="col-md-4 p-4 sidebar">
            <h4 class="mb-3 text-light d-flex align-items-center fw-bold">
                <i class="bi bi-bookmark-star-fill text-warning me-2"></i> 스토리 브릿지 빌더
            </h4>
            <p class="small text-muted mb-4">다문화 아동에게는 자부심을, 한국 아동에게는 문화 다양성을 길러주는 '상생형 에듀테크 플랫폼'으로 대통령상(대상)과 시드 투자유치를 동시에 조준합니다.</p>

            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    {% for message in messages %}
                        <div class="alert alert-indigo alert-dismissible fade show bg-dark text-white border-secondary" role="alert">
                            {{ message }}
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="alert" aria-label="Close"></button>
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}

            <div class="bg-dark p-3 rounded mb-4 border border-secondary">
                <div class="mb-3">
                    <label class="form-label">산업 도메인 및 타겟 마켓</label>
                    <input type="text" id="industry" class="form-control bg-secondary text-white" value="공공 문화 사료 융합 X 상호주의 아동 에듀테크 X 늘봄학교 교구재">
                </div>
                <div class="mb-3">
                    <label class="form-label">혁신 플랫폼 프로젝트명</label>
                    <input type="text" id="topic" class="form-control bg-secondary text-white" value="글로벌 생활 문화 및 전래동화 융합 에듀테크 앱 '도란도란 스토리 브릿지(Doran Story Bridge)'">
                </div>
                <div class="mb-3">
                    <label class="form-label">대조군 서비스 모델</label>
                    <input type="text" id="competitor" class="form-control bg-secondary text-white" value="한국 문화 일방 주입식 다문화 앱 및 어휘 암기 위주의 딱딱한 한국어 학습 프로그램">
                </div>
                <div class="mb-3">
                    <label class="form-label">마스터 기획안 공식 타이틀</label>
                    <input type="text" id="title" class="form-control bg-secondary text-white" value="한국-아세안 닮은꼴 전래동화 기반 상생형 아동 생활문화 교육 플랫폼: 도란도란 스토리 브릿지">
                </div>
                
                <button type="button" onclick="startDeepSearch()" class="btn btn-primary w-100 fw-bold shadow-lg" style="background-color: #4f46e5; border:none;">
                    <i class="bi bi-lightning-charge-fill"></i> 마스터 기획안 및 에이전트 프롬프트 빌드
                </button>
            </div>

            <h5 class="text-muted pt-2 mb-3" style="font-size: 0.9rem;">산출된 기획안 아카이브 ({{ reports|length }})</h5>
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
                    <span class="badge badge-investment shadow-sm"><i class="bi bi-award-fill"></i> 대상(대통령상) 타겟 제안서</span>
                    <small class="text-muted"><i class="bi bi-calendar-check"></i> 생성 타임스탬프: {{ current_report[6] }}</small>
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
                    <i class="bi bi-patch-check-fill"></i> 마크업 원본 데이터가 클립보드에 복사되었습니다! 개발 소스나 경진대회 제출 서식에 붙여넣어 즉시 활용하세요.
                </div>

                <div class="report-view shadow-sm mb-5" id="reportRawContainer">
                    {{ current_report[5]|safe }}
                </div>

                <div class="card border-primary shadow-sm mt-5">
                    <div class="card-header bg-dark text-white fw-bold d-flex justify-content-between align-items-center">
                        <span class="text-indigo" style="color: #a5b4fc;"><i class="bi bi-cpu"></i> 파이프라인 디버거: 실시간 컨텍스트 및 프롬프트 추적기</span>
                        <span class="badge bg-primary">V4 스토리 RAG</span>
                    </div>
                    <div class="card-body bg-light">
                        <p class="text-muted small">각 단계별 엔진에서 컴파일된 시스템 구조 명령문과 심사위원을 매료시킨 실제 백엔드 소스용 Few-Shot 텍스트 코드를 디버깅할 수 있습니다.</p>
                        
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
                                            <h6 class="text-info fw-bold" style="font-size:0.85rem;"><i class="bi bi-arrow-right-circle"></i> 투자 컨설턴트 지시 프롬프트 구조</h6>
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
                    <i class="bi bi-bookmark-dash-fill text-secondary" style="font-size: 5.5rem; color: #cbd5e1 !important;"></i>
                    <h4 class="mt-4 fw-bold text-dark">활성화된 마스터 투자 기획서가 없습니다.</h4>
                    <p>좌측 도메인 세그먼트를 확인하고 통합 연산 버튼을 작동시켜 주십시오.</p>
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
                alert("기획 파이프라인 프로세스 내부 에러: " + result.error);
                closeOverlay();
                return;
            }
            
            combinedContent += result.content + "<hr class='my-5' style='border-top: 2px dashed #4f46e5;'>";
            updateStageUI(stage, 'success');
            
            let progressPercentage = stage * 20;
            document.getElementById('progressBar').style.width = progressPercentage + '%';
            document.getElementById('progressBar').innerText = progressPercentage + '%';
        } catch (err) {
            alert("LLM 로컬 엔진 검증 실패: " + err);
            closeOverlay();
            return;
        }
    }

    document.getElementById('statusTitle').innerText = "기획 데이터베이스 최종 인덱싱 및 스토리지 커밋 중...";
    const saveResponse = await fetch('/save_final', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...data, full_content: combinedContent })
    });
    
    const saveResult = await saveResponse.json();
    if(saveResult.success) {
        location.href = `/${saveResult.new_id}`;
    } else {
        alert("기획 데이터 영속화 디바이스 저장 실패.");
        closeOverlay();
    }
}

function updateStageUI(stage, status) {
    const stageEl = document.getElementById(`stage${stage}`);
    if (status === 'processing') {
        document.getElementById('statusTitle').innerText = `${stage}단계 투자 유치 및 심사 저격 지표 산출 중...`;
        stageEl.className = "text-warning fw-bold mb-2";
        stageEl.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span> [연산중] 상생형 듀얼 스토리 모델 매시업 엔진 컴파일 중...`;
    } else if (status === 'success') {
        stageEl.className = "text-success mb-2";
        stageEl.innerHTML = `<i class="bi bi-check-circle-fill me-2" style="color:#22c55e;"></i> [빌드완료] 세그먼트 적재 완료`;
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
        alert('클립보드 복사 중 예외 발생: ' + err);
    });
}

function downloadHtmlDocument() {
    const title = document.getElementById('reportTitle').innerText.trim() || 'Doran_Story_Bridge_Proposal';
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
        th { background-color: #e0e7ff; color: #312e81; padding: 14px; border: 1px solid #c7d2fe; text-align: center; font-weight: bold; }
        td { padding: 14px; border: 1px solid #e2e8f0; vertical-align: middle; }
        pre { background: #1e1e1e; color: #e2e8f0; padding: 18px; border-radius: 8px; overflow-x: auto; border: 1px solid #334155; }
        h4 { color: #4f46e5; font-weight: 700; margin-top: 30px; margin-bottom: 15px; border-left: 4px solid #4f46e5; padding-left: 10px; }
    </style>
</head>
<body>
    <div class="master-box">
        <h1 style="font-weight: 800; margin-bottom: 35px; border-bottom: 3px solid #4f46e5; padding-bottom: 20px; color:#1e1b4b;">\${title}</h1>
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
# 3. 백엔드 컨트롤러 (도란도란 스토리 브릿지 커스텀 로직)
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
        1: "Market Pain Points & Segment (다문화 및 일반 아동 타겟 시장 정밀 분석)",
        2: "Core Data Architecture (문체부, 국립민속박물관 및 KF 아세안문화원 공공데이터 연계 설계)",
        3: "Core Product Features (닮은꼴 동화극장, 생활문화 퀘스트, 이중언어 낭독방 핵심 우위성 행렬)",
        4: "Business Model & Sustainability (늘봄학교 SaaS 계약 및 친환경 O2O 굿즈 수익 다각화)",
        5: "Core Backend System Prompt (한국어-베트남어 상호 작용 및 발음 피드백용 LLM 프롬프트 명세)"
    }
    stage_title = stage_titles.get(stage, "미정의 단계")

    system_prompt = (
        "너는 문화체육관광부 공공데이터 경진대회에서 대통령상(대상) 수상을 확정 짓고, 임팩트 투자사들로부터 대규모 시드 투자를 유치하는 "
        "국내 최고의 에듀테크 컴퍼니 빌더이자 교육 정책 기획 전문가야. "
        "이번 기획안의 핵심은 일방적인 한국 문화 주입이 아닌, 한국과 베트남(아세안)의 전통 사료를 1:1로 매칭하는 '상생형 상호 문화 교육 모델'이야. "
        "마크다운 문법(예: ```html, ```, #, **)은 절대 출력에 섞지 말고, "
        "바로 HTML 렌더링에 사용할 수 있는 순수 웹 컴포넌트 마크업(<h4>, <p>, <table>, <pre>, <code> 등)만 가공하여 출력하라."
    )

    if stage == 1:
        prompt = (
            f"주제인 [{topic}] 플랫폼의 '1. Market Pain Points & Segment' 장을 빌드해줘. "
            f"타겟 유저인 7~10세의 한국 거주 다문화 가구 아동 및 일반 한국 아동층을 명시해줘. "
            f"기존 동화 교재들이 한국사/한국동화만 일방 주입하여 다문화 아동에게 '엄마 나라 문화는 이질적이다'라는 소외감을 유발하는 문제(Pain Point 1)와 "
            f"급식실 매너, 존댓말, 인사 예절 등 초등학교 현장에서 겪는 '실전 생활 예절 콘텐츠의 부재'(Pain Point 2)를 예리하게 지적해줘. "
            f"그리고 한-베 양국에서 발견되는 완벽한 구조의 '쌍둥이 동화'를 매칭하는 에듀테크 블루오션 기회를 투자 제안서 형태로 서술해줘."
        )
    elif stage == 2:
        prompt = (
            f"[{topic}]의 '2. Core Data Architecture (정부 기관 문화 데이터 연계)' 장을 구성해줘. "
            f"경진대회 심사위원들이 가장 중요하게 평가하는 공공데이터 융합 구도를 완벽히 설명해야 해: "
            f"① 한국국학진흥원 '스토리테마파크' 구비설화 및 국립중앙도서관 아동 전래동화 텍스트, "
            f"② KF 아세안문화원(ACH) 보유 베트남 전래동화 멀티미디어/번역 데이터, "
            f"③ 국립민속박물관 '한국일생의례사전' 및 '한국세시풍속사전'의 식사/주거/인사/명절 예절 데이터, "
            f"④ 국립국어원 '한국어-베트남어 학습 사전' 및 초등 교과서 어휘 데이터 파이프라인. "
            f"이 정보 자산들이 시스템 내부에서 어떻게 유기적으로 결합하는지 아키텍처를 증명해줘."
        )
    elif stage == 3:
        prompt = (
            f"[{topic}]의 핵심 강점을 증명하는 '3. Core Product Features 및 경쟁력 비교 행렬' 장을 작성해줘. "
            f"3대 핵심 기능인 [① 닮은꼴 동화 극장: 콩쥐팥쥐 X 떰똠(Tấm Cám), 견우와직녀 X 응우랑뜩느 및 박물관 3D 유물 팝업], "
            f"[② 생활 문화 퀘스트: 흥부와 함께 배우는 급식실 수저 예절 vs 베트남 밥그릇 문화, 심청이와 배우는 존댓말/인사 퍼즐], "
            f"[③ 부모님과 함께하는 이중언어 오디오 낭독방]의 세부 시나리오를 매끄럽게 녹여내야 해. "
            f"그리고 반드시 <table class='table table-bordered table-striped text-center'>"
            f"<thead><tr><th>차별화 차원</th><th>{competitor}</th><th>도란도란 스토리 브릿지 (본 서비스)</th></tr></thead>"
            f"형태의 표를 만들어 상호 문화주의적 관점, 실전 초등 생활 매너 연계, 이중언어 음성 분석 AI 유무를 완벽하게 대조하여 기술해줘."
        )
    elif stage == 4:
        prompt = (
            f"[{topic}]의 '4. Business Model & Sustainability (수익 모델 및 사업성)' 장을 도출해줘. "
            f"2026년 전국적으로 전면 도입 및 활성화된 '늘봄학교' 및 초등 방과후 커리큘럼의 상호문화 이해 교육 교재 도입 채널과 "
            f"국공립 유치원, 다문화가족지원센터 대상 고정 구독 매출 모델(B2G SaaS)을 논리적으로 제시해줘. "
            f"또한 B2C 확장 전략으로서 융합 캐릭터 자산을 활용한 양국 전통 가옥(한옥-수상 가옥) 구현 'O2O 친환경 입체 팝업북 및 문화 체험 키트' "
            f"제조/판매 매출 파이프라인을 체계적으로 구조화해줘."
        )
    elif stage == 5:
        prompt = (
            f"[{topic}] 플랫폼을 실제 Python Flask 백엔드 환경에서 SQLite 스토리지와 연동할 때 사용할 "
            f"'5. 서비스 코어 탑재용 AI 시스템 프롬프트(Few-Shot Engineering) 명세서' 장을 빌드해줘. "
            f"이 프롬프트는 아이가 전래동화를 읽을 때 한국어 발음 정확도를 피드백하고, 베트남어 성조의 문화적 특성을 부모와 함께 연주하듯 매칭하며, "
            f"한국-베트남의 닮은꼴 구조를 추출하도록 지시해야 해. "
            f"가변 파라미터 [target_child_age, dual_story_pair, tracking_language, feedback_level]를 반드시 포함하고, "
            f"실제 이식이 가능한 `SYSTEM_PROMPT` 코드 에셋을 "
            f"<pre><code class='text-danger bg-dark p-3 d-block rounded'> 태그 내부에 심사위원 저격 총평 멘트와 함께 온전하게 담아내어 가시화해줘."
        )
    else:
        return jsonify({"success": False, "error": "인덱스 매핑 실패"})

    active_model_name = get_active_model()

    payload = {
        "model": active_model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
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
    flash("도란도란 스토리 브릿지 마스터 기획 데이터가 정상적으로 소멸되었습니다.")
    return redirect(url_for("index"))


if __name__ == "__main__":
    # 포트 충돌 방지를 위해 고유 포트 50012 번으로 배포
    app.run(host="0.0.0.0", port=50008, debug=True)
