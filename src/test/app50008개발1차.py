import sqlite3
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
# 2. UI/UX 템플릿 (12단계 분할 파이프라인 최적화)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>도란도란 스토리 브릿지 [소형 LLM 최적화 마스터 빌더]</title>
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
        .stage-box { max-height: 320px; overflow-y: auto; padding-right: 5px; }
    </style>
</head>
<body>

<div id="loadingOverlay" class="loading-overlay flex-column">
    <div class="spinner-border text-indigo mb-4" style="width: 3.5rem; height: 3.5rem; color: #818cf8;" role="status"></div>
    <h4 id="statusTitle" class="fw-bold text-light">토큰 절약형 12단계 반복 루프 가동 중...</h4>
    <p id="statusDesc" class="text-muted text-center px-4" style="max-width: 550px;">
        기획-디자인-개발-테스트 과정을 각 3회씩 점진적으로 빌드하여 소형 LLM의 컨텍스트 한계를 극복하고 완성도를 극대화합니다.
    </p>
    
    <div class="container mt-3" style="max-width: 650px;">
        <div class="progress" style="height: 25px; border-radius: 8px;">
            <div id="progressBar" class="progress-bar progress-bar-striped progress-bar-animated bg-indigo" role="progressbar" style="width: 0%;">0%</div>
        </div>
        <div id="stageList" class="mt-4 text-start bg-dark p-3 rounded border border-secondary small stage-box">
            <div id="stage1" class="text-white-50 mb-1"><i class="bi bi-circle"></i> [개발기획-1차] 기본 요구사항 정의 및 Pain Point 분석</div>
            <div id="stage2" class="text-white-50 mb-1"><i class="bi bi-circle"></i> [개발기획-2차] 공공 데이터 아키텍처 연계 보완</div>
            <div id="stage3" class="text-white-50 mb-1"><i class="bi bi-circle"></i> [개발기획-3차] 기획 명세 검증 및 최종 확정</div>
            <div id="stage4" class="text-white-50 mb-1"><i class="bi bi-circle"></i> [디자인-1차] 상호문화 UI/UX 및 테마 와이어프레임 설계</div>
            <div id="stage5" class="text-white-50 mb-1"><i class="bi bi-circle"></i> [디자인-2차] 컴포넌트 단위 고도화 및 테이블 레이아웃 보완</div>
            <div id="stage6" class="text-white-50 mb-1"><i class="bi bi-circle"></i> [디자인-3차] 반응형 에셋 배치 및 인터랙션 마감</div>
            <div id="stage7" class="text-white-50 mb-1"><i class="bi bi-circle"></i> [코드개발-1차] Core AI 시스템 프롬프트(Few-Shot) 초안 구조화</div>
            <div id="stage8" class="text-white-50 mb-1"><i class="bi bi-circle"></i> [코드개발-2차] Flask/SQLite 연동 및 예외 처리 로직 삽입</div>
            <div id="stage9" class="text-white-50 mb-1"><i class="bi bi-circle"></i> [코드개발-3차] 토큰 세이빙 최적화 튜닝 및 코드 클린업</div>
            <div id="stage10" class="text-white-50 mb-1"><i class="bi bi-circle"></i> [테스트-1차] 다문화 아동 연령별 발음 피드백 가상 시나리오 검증</div>
            <div id="stage11" class="text-white-50 mb-1"><i class="bi bi-circle"></i> [테스트-2차] 한-베 이중언어 성조 매칭 에러 케이스 추적 디버깅</div>
            <div id="stage12" class="text-white-50 mb-1"><i class="bi bi-circle"></i> [테스트-3차] 통합 시스템 프롬프트 무결성 및 인덱싱 최종 패스</div>
        </div>
    </div>
</div>

<div class="container-fluid">
    <div class="row">
        <div class="col-md-4 p-4 sidebar">
            <h4 class="mb-3 text-light d-flex align-items-center fw-bold">
                <i class="bi bi-bookmark-star-fill text-warning me-2"></i> 스토리 브릿지 빌더 v2
            </h4>
            <p class="small text-muted mb-4">소형 모델(Low-Token LLM)의 컨텍스트 누수를 방지하기 위해 4대 개발 주기를 3회 반복 피드백 알고리즘으로 분할 제어합니다.</p>

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
                    <input type="text" id="title" class="form-control bg-secondary text-white" value="한국-아세안 닮은꼴 전래동화 기반 상생형 아동 생활문화 교육 플랫폼">
                </div>
                
                <button type="button" onclick="startSplitPipeline()" class="btn btn-primary w-100 fw-bold shadow-lg" style="background-color: #4f46e5; border:none;">
                    <i class="bi bi-lightning-charge-fill"></i> 12단계 순차 빌드 가동
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
                    <span class="badge badge-investment shadow-sm"><i class="bi bi-award-fill"></i> 12단계 순차 정밀 검증형 제안서</span>
                    <small class="text-muted"><i class="bi bi-calendar-check"></i> 완료일시: {{ current_report[6] }}</small>
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
                    <i class="bi bi-patch-check-fill"></i> 마크업 데이터가 클립보드에 복사되었습니다!
                </div>

                <div class="report-view shadow-sm mb-5" id="reportRawContainer">
                    {{ current_report[5]|safe }}
                </div>

                <div class="card border-primary shadow-sm mt-5">
                    <div class="card-header bg-dark text-white fw-bold d-flex justify-content-between align-items-center">
                        <span style="color: #a5b4fc;"><i class="bi bi-cpu"></i> 소형 모델 디버깅: 12단계 점진적 추적기</span>
                        <span class="badge bg-success">Loop 3 Count Passed</span>
                    </div>
                    <div class="card-body bg-light">
                        <div class="accordion" id="accordionLogs">
                            {% for log in logs %}
                            <div class="accordion-item">
                                <h2 class="accordion-header" id="heading{{ log[0] }}">
                                    <button class="accordion-button collapsed fw-bold" type="button" data-bs-toggle="collapse" data-bs-target="#collapse{{ log[0] }}">
                                        <strong>[단계 {{ log[3] }} / 12] {{ log[4] }}</strong>
                                    </button>
                                </h2>
                                <div id="collapse{{ log[0] }}" class="accordion-collapse collapse" data-bs-parent="#accordionLogs">
                                    <div class="accordion-body bg-dark">
                                        <div class="mb-2">
                                            <h6 class="text-info small fw-bold"><i class="bi bi-arrow-right-circle"></i> 주입 프롬프트</h6>
                                            <pre class="log-code">{{ log[5] }}</pre>
                                        </div>
                                        <div class="mb-2">
                                            <h6 class="text-success small fw-bold"><i class="bi bi-arrow-right-circle"></i> 산출 결과 스냅샷</h6>
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
                    <i class="bi bi-bookmark-dash-fill text-secondary" style="font-size: 5.5rem;"></i>
                    <h4 class="mt-4 fw-bold text-dark">로드된 기획 문서가 존재하지 않습니다.</h4>
                    <p>왼쪽 빌더 옵션을 확인하고 12단계 파이프라인 작동 버튼을 클릭하세요.</p>
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

async function startSplitPipeline() {
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

    let lastStageContent = ""; // 직전 단계 산출물만 전송하여 로컬 LLM 토큰 유지
    let finalCombinedHtml = ""; // 클라이언트에 최종 누적 정렬할 임베디드 스트링

    const TOTAL_STAGES = 12;

    for (let stage = 1; stage <= TOTAL_STAGES; stage++) {
        updateStageUI(stage, 'processing');
        try {
            const response = await fetch(`/generate_step/${stage}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ...data, accumulated_context: lastStageContent })
            });
            
            const result = await response.json();
            if (!result.success) {
                alert(`${stage}단계 파이프라인 연산 중 로컬 백엔드 오류: ` + result.error);
                closeOverlay();
                return;
            }
            
            lastStageContent = result.content; // 토큰 세이빙용 바인딩 수정
            
            // 실질 결과물이 업데이트되는 시점(최종 수정 주기)을 수집하거나 파트를 병합
            if (stage === 3 || stage === 6 || stage === 9 || stage === 12) {
                let sectionTitle = "";
                if(stage===3) sectionTitle = "<h3>[1] 시스템 개발 기획 검증 명세서</h3>";
                if(stage===6) sectionTitle = "<h3>[2] 상생형 구조적 인터페이스 및 디자인 체계</h3>";
                if(stage===9) sectionTitle = "<h3>[3] Core AI 엔지니어링 및 이식용 백엔드 코드</h3>";
                if(stage===12) sectionTitle = "<h3>[4] 시나리오 기반 무결성 테스트 보고서</h3>";
                
                finalCombinedHtml += sectionTitle + result.content + "<hr class='my-5' style='border-top: 2px dashed #4f46e5;'>";
            }
            
            updateStageUI(stage, 'success');
            
            let progressPercentage = Math.floor((stage / TOTAL_STAGES) * 100);
            document.getElementById('progressBar').style.width = progressPercentage + '%';
            document.getElementById('progressBar').innerText = progressPercentage + '%';
        } catch (err) {
            alert("LLM 컨텍스트 통신 실패: " + err);
            closeOverlay();
            return;
        }
    }

    document.getElementById('statusTitle').innerText = "기획 데이터베이스 영속성 레이어 원자적 저장 중...";
    const saveResponse = await fetch('/save_final', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...data, full_content: finalCombinedHtml })
    });
    
    const saveResult = await saveResponse.json();
    if(saveResult.success) {
        location.href = `/${saveResult.new_id}`;
    } else {
        alert("최종 결과 영속성 디스크 저장에 실패했습니다.");
        closeOverlay();
    }
}

function updateStageUI(stage, status) {
    const stageEl = document.getElementById(`stage${stage}`);
    if(!stageEl) return;
    if (status === 'processing') {
        document.getElementById('statusTitle').innerText = `${stage}/12 단계 알고리즘 연산 처리 중...`;
        stageEl.className = "text-warning fw-bold mb-1";
        stageEl.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span> [연산중] 로컬 프롬프트 최적화 분석 중...`;
    } else if (status === 'success') {
        stageEl.className = "text-success mb-1 small text-decoration-line-through";
        stageEl.innerHTML = `<i class="bi bi-check-circle-fill me-2" style="color:#22c55e;"></i> [완료] Iteration Loop 통과`;
    }
}

function resetStageUI() {
    const stageTitles = [
        "[개발기획-1차] 기본 요구사항 정의 및 Pain Point 분석",
        "[개발기획-2차] 공공 데이터 아키텍처 연계 보완",
        "[개발기획-3차] 기획 명세 검증 및 최종 확정",
        "[디자인-1차] 상호문화 UI/UX 및 테마 와이어프레임 설계",
        "[디자인-2차] 컴포넌트 단위 고도화 및 테이블 레이아웃 보완",
        "[디자인-3차] 반응형 에셋 배치 및 인터랙션 마감",
        "[코드개발-1차] Core AI 시스템 프롬프트(Few-Shot) 초안 구조화",
        "[코드개발-2차] Flask/SQLite 연동 및 예외 처리 로직 삽입",
        "[코드개발-3차] 토큰 세이빙 최적화 튜닝 및 코드 클린업",
        "[테스트-1차] 다문화 아동 연령별 발음 피드백 가상 시나리오 검증",
        "[테스트-2차] 한-베 이중언어 성조 매칭 에러 케이스 추적 디버깅",
        "[테스트-3차] 통합 시스템 프롬프트 무결성 및 인덱싱 최종 패스"
    ];
    for (let i = 1; i <= 12; i++) {
        const stageEl = document.getElementById(`stage${i}`);
        if(stageEl) {
            stageEl.className = "text-white-50 mb-1";
            stageEl.innerHTML = `<i class="bi bi-circle"></i> ${stageTitles[i-1]}`;
        }
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
        setTimeout(() => alertBox.classList.add('d-none'), 3000);
    }).catch(err => alert('복사 에러: ' + err));
}

function downloadHtmlDocument() {
    const title = document.getElementById('reportTitle').innerText.trim() || 'Doran_Story_Bridge_Iterative_Proposal';
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
        body { padding: 60px; background-color: #f1f5f9; font-family: system-ui, sans-serif; color: #1e293b; }
        .master-box { background: #ffffff; padding: 50px; border: 1px solid #e2e8f0; border-radius: 16px; max-width: 1100px; margin: 0 auto; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); }
        table { width: 100%; margin: 25px 0; border-collapse: collapse; }
        th { background-color: #e0e7ff; color: #312e81; padding: 14px; border: 1px solid #c7d2fe; text-align: center; font-weight: bold; }
        td { padding: 14px; border: 1px solid #e2e8f0; vertical-align: middle; }
        pre { background: #1e1e1e; color: #e2e8f0; padding: 18px; border-radius: 8px; overflow-x: auto; }
        h3 { color: #1e1b4b; border-bottom: 2px solid #4f46e5; padding-bottom: 8px; margin-top: 40px; }
        h4 { color: #4f46e5; font-weight: 700; margin-top: 20px; border-left: 4px solid #4f46e5; padding-left: 10px; }
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
# 3. 백엔드 컨트롤러 (12단계 분할 유도 로직)
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
    # 토큰 세이빙 기법: 전체 컨텍스트 누적을 받되, 소형 모델용 프롬프트 구성을 위해 인계받음
    prev_context = data.get("accumulated_context", "")

    stage_titles = {
        1: "[개발기획-초안] 핵심 요구사항 정의 및 비즈니스 고도화 대상 정의",
        2: "[개발기획-개선] 정부 기관 사료(국합진흥원/KF) 융합 설계 추가 보완",
        3: "[개발기획-수정] 다문화 Pain Point 1,2 해결 조건 최종 픽스 보고서화",
        
        4: "[디자인-초안] 상호주의 듀얼 전래동화 컴포넌트 인터페이스 와이어프레임 설계",
        5: "[디자인-개선] 대조군 앱 구조 대비 우위 차별성 UI 구조 테이블 레이아웃 구현",
        6: "[디자인-수정] 7~10세 다문화 가동 전용 반응형 접근성 디자인 사양 마감",
        
        7: "[코드개발-초안] AI 코어 전용 가변 파라미터 내장형 SYSTEM_PROMPT 아키텍처 코딩",
        8: "[코드개발-개선] Python Flask 및 SQLite 인프라와 결합 가능한 문자열 에셋화 고도화",
        9: "[코드개발-수정] 소형 모델 최적화용 Few-Shot 템플릿 임베딩 사양 최종 코드 산출",
        
        10: "[테스트-초안] 흥부놀부/떰똠 낭독 시나리오 가상 런타임 데이터 유효성 검증",
        11: "[테스트-개선] 한-베 이중언어 성조 번역 가상 예외 케이스 디버깅 로그 생성",
        12: "[테스트-수정] 통합 플랫폼 연동 무결성 최종 검과 테스트 검수 싸인오프 완료"
    }
    stage_title = stage_titles.get(stage, "알 수 없는 루프 단계")

    system_prompt = (
        "너는 다문화 상생 에듀테크 플랫폼 '도란도란 스토리 브릿지'의 핵심 테크니컬 아키텍트이자 파이프라인 마스터야. "
        "컨텍스트 윈도우가 작은 환경에서 동작하고 있으므로, 잡설이나 인사말은 생략하고 즉시 활용 가능한 순수 HTML 웹 컴포넌트 마크업(<h4>, <p>, <table>, <pre>, <code>)만 출력해라. "
        "마크다운 언어 지시자 (```html 등)는 결과에 절대 섞지 마라."
    )

    # 12개 하위 분할 프롬프트 구조화 (초안 -> 개선 -> 수정의 3-Iteration 루프 구조)
    if stage == 1:
        prompt = f"[{topic}]의 '개발기획 1차 초안'을 빌드해라. 7~10세 한국 거주 다문화 가정 아동이 마주하는 일방적 한국 문화 주입의 한계를 지적하고 개선 방향을 서술해라."
    elif stage == 2:
        prompt = f"다음 제시된 1차 초안의 한계를 보완하여 '개발기획 2차 개선안'을 작성해라. 한국국학진흥원 '스토리테마파크'와 KF 아세안문화원의 베트남 전래동화 사료 연계 방식을 테이블 구조로 구체화해라.\n[참고 데이터]:\n{prev_context}"
    elif stage == 3:
        prompt = f"다음 2차 개선안을 완벽하게 다듬어 심사위원 제출용 '개발기획 3차 최종안'을 가공하라. 대통령상 타겟 형태로 요약 멘트와 비즈니스 정당성을 <h4>와 <p> 태그 구조로 완결 지어라.\n[참고 데이터]:\n{prev_context}"
    
    elif stage == 4:
        prompt = f"[{topic}]의 '디자인 1차 초안'을 작성해라. 한국과 베트남의 듀얼 동화를 1:1로 배치하고, 입체 팝업북과 연동할 수 있는 UI/UX 와이어프레임 구조를 텍스트 디스크립션 형태로 기술해라."
    elif stage == 5:
        prompt = f"다음 디자인 초안을 보완하여 '디자인 2차 개선안'을 구성해라. {competitor} 모델과 당사 모델의 UI 관점 차별성을 극대화하는 <table class='table table-bordered table-striped text-center'> 마크업 표 구조를 완벽히 그려내라.\n[참고 디자인 구조]:\n{prev_context}"
    elif stage == 6:
        prompt = f"다음 2차 개선 사양을 마감하여 '디자인 3차 최종 승인안'을 출력하라. 다문화 아동 접근성 컬러(indigo, slate) 테마와 폰트 가독성 설정안을 구체화하여 명시하라.\n[참고 디자인 구조]:\n{prev_context}"
    
    elif stage == 7:
        prompt = f"[{topic}] 플랫폼의 '코드개발 1차 초안'을 작성해라. 가변 파라미터 [target_child_age, dual_story_pair, tracking_language, feedback_level]를 포함하는 한국어-베트남어 AI 피드백 엔진용 SYSTEM_PROMPT의 골격을 <pre><code> 구조 내에 코딩하라."
    elif stage == 8:
        prompt = f"다음 개발 초안을 확장하여 '코드개발 2차 개선안'을 작성해라. 소형 LLM에 맞추어 Few-Shot 낭독 예시('흥부와 놀부' 읽기 피드백 예문)를 구체적으로 주입하고 오류를 방지하는 예외 지시문을 시스템 프롬프트 코드 내부에 삽입해라.\n[기존 코드 구조]:\n{prev_context}"
    elif stage == 9:
        prompt = f"다음 2차 코드를 최종 고도화하여 실제 Flask 백엔드에서 바로 이식하여 사용할 수 있는 '코드개발 3차 최종 상용 에셋'을 완성하라. 순수 파이썬 문자열 형태 포맷으로 정돈하여 가시화하라.\n[기존 코드 구조]:\n{prev_context}"
    
    elif stage == 10:
        prompt = f"[{topic}]의 '테스트 1차 초안'을 빌드해라. 7~10세 아동이 '콩쥐팥쥐'와 베트남의 '떰똠'을 읽었을 때 AI 시스템이 발음 정확도를 정상 출력하는지 판정하는 가상 통합 테스트 케이스 명세서를 구성하라."
    elif stage == 11:
        prompt = f"다음 테스트 초안을 보완하여 '테스트 2차 개선 사양'을 정의해라. 부모와 함께 연주하듯 매칭하는 베트남어 성조 추적 기능 오작동 시의 예외 처리 로그 디버깅 가상 시나리오 데이터를 테이블로 추가하라.\n[기존 테스트 문서]:\n{prev_context}"
    elif stage == 12:
        prompt = f"전 단계 사양을 총망라하여 가상 인프라 무결성이 확보되었음을 증명하는 '테스트 3차 최종 검수 패스 보고서'를 완결하여 출력하라.\n[기존 테스트 문서]:\n{prev_context}"
    else:
        return jsonify({"success": False, "error": "파이프라인 인덱스 이탈"})

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
        
        # 마크다운 백틱 가드 레일 코드 제거 유지
        ai_output = ai_output.replace("```html", "").replace("```", "").strip()

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO generation_logs (doc_id, session_id, stage_num, stage_title, prompt_sent, response_received, cumulative_context)
                VALUES (NULL, ?, ?, ?, ?, ?, ?)
            """, (session_id, stage, stage_title, prompt, ai_output, prev_context[:500] + "...(중략)"))
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
    flash("정밀 분할 빌드된 마스터 기획서 및 중간 이터레이션 추적 로그가 정상 파기되었습니다.")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=50008, debug=True)
