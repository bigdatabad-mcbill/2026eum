from datetime import date, datetime
import requests
from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# --------------------------------------------------
# Flask Config
# --------------------------------------------------
app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///motherall.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# --------------------------------------------------
# Models
# --------------------------------------------------
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    nationality = db.Column(db.String(50))
    language = db.Column(db.String(20))
    baby_name = db.Column(db.String(100))
    baby_birth = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class CulturalStory(db.Model):
    __tablename__ = "cultural_stories"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    category = db.Column(db.String(100))
    age_group = db.Column(db.String(50))
    description = db.Column(db.Text)
    image_url = db.Column(db.Text)


class Lullaby(db.Model):
    __tablename__ = "lullabies"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    audio_url = db.Column(db.Text)
    age_group = db.Column(db.String(50))


# [신규 추가] 일정 관리를 위한 모델
class Schedule(db.Model):
    __tablename__ = "schedules"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)


# --------------------------------------------------
# Utility Functions
# --------------------------------------------------
def calculate_month_age(birth_date):
    if not birth_date:
        return 0

    today = date.today()
    months = (today.year - birth_date.year) * 12 + today.month - birth_date.month

    return max(months, 0)


def recommend_story(age):
    if age <= 6:
        return "까치와 호랑이"
    elif age <= 12:
        return "흥부와 놀부"
    elif age <= 24:
        return "해님달님"
    else:
        return "선녀와 나무꾼"


def get_cultural_milestone(age):
    events = []
    events.append(
        {
            "event": "백일",
            "description": "아기의 건강한 성장을 기원하는 한국 전통 문화",
            "active": True if age >= 3 else False,
        }
    )
    events.append(
        {
            "event": "돌잔치",
            "description": "아기의 첫 생일을 축하하는 전통 행사",
            "active": True if age >= 12 else False,
        }
    )
    return events


# --------------------------------------------------
# UI Front-end (Instagram Style Mobile View)
# --------------------------------------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Mother-All</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        .hide-scrollbar::-webkit-scrollbar { display: none; }
        .hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
    </style>
</head>
<body class="bg-gray-50 flex justify-center items-center min-h-screen">

    <div class="w-full max-w-md h-[844px] bg-white shadow-2xl relative flex flex-col overflow-hidden border border-gray-200">
        
        <header class="flex justify-between items-center px-4 py-3 border-b border-gray-100 bg-white sticky top-0 z-50">
            <h1 class="text-xl font-bold tracking-tight text-gray-900 font-serif italic">Mother-All</h1>
            <div class="flex gap-4 text-xl text-gray-700">
                <i class="fa-regular fa-heart cursor-pointer hover:text-red-500"></i>
                <i class="fa-regular fa-paper-plane cursor-pointer"></i>
            </div>
        </header>

        <main class="flex-1 overflow-y-auto pb-20 hide-scrollbar bg-white">
            
            <section id="page-home" class="page-view">
                <div class="flex gap-4 p-4 border-b border-gray-100 overflow-x-auto hide-scrollbar bg-white">
                    <div class="flex flex-col items-center flex-shrink-0">
                        <div class="w-16 h-16 rounded-full p-[2px] bg-gradient-to-tr from-yellow-400 to-fuchsia-600 flex items-center justify-center">
                            <div class="w-full h-full bg-white rounded-full flex items-center justify-center border-2 border-white">
                                <span class="text-xs font-bold text-gray-700">내아기</span>
                            </div>
                        </div>
                        <span class="text-xs text-gray-500 mt-1" id="baby-name-label">아가</span>
                    </div>
                    <div id="milestone-stories" class="flex gap-4"></div>
                </div>

                <div id="home-feed" class="space-y-4 pt-2"></div>
            </section>

            <section id="page-story" class="page-view hidden p-4">
                <h2 class="text-lg font-bold mb-4 text-gray-800">오늘의 추천 전래동화</h2>
                <div id="story-card" class="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm"></div>
            </section>

            <section id="page-lullaby" class="page-view hidden p-4">
                <h2 class="text-lg font-bold mb-4 text-gray-800">힐링 자장가 플레이어</h2>
                <div id="lullaby-card" class="bg-white border border-gray-200 rounded-xl p-6 shadow-sm text-center"></div>
            </section>

            <section id="page-schedule" class="page-view hidden p-4">
                <h2 class="text-lg font-bold mb-3 text-gray-800">아이 일정 관리</h2>
                
                <form id="schedule-form" class="bg-gray-50 p-4 rounded-xl border border-gray-100 mb-6 space-y-3">
                    <div>
                        <label class="text-xs font-semibold text-gray-500 block mb-1">일정명</label>
                        <input type="text" id="sched-title" required class="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 bg-white focus:outline-none focus:border-gray-400" placeholder="예: 예방접종, 문화센터 가는 날">
                    </div>
                    <div class="grid grid-cols-2 gap-2">
                        <div>
                            <label class="text-xs font-semibold text-gray-500 block mb-1">날짜</label>
                            <input type="date" id="sched-date" required class="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 bg-white focus:outline-none focus:border-gray-400">
                        </div>
                        <div>
                            <label class="text-xs font-semibold text-gray-500 block mb-1">메모</label>
                            <input type="text" id="sched-desc" class="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 bg-white focus:outline-none focus:border-gray-400" placeholder="간단한 메모">
                        </div>
                    </div>
                    <button type="submit" class="w-full bg-blue-500 hover:bg-blue-600 text-white font-medium text-sm py-2 rounded-lg transition">새 일정 등록하기</button>
                </form>

                <div class="space-y-3">
                    <h3 class="text-sm font-bold text-gray-600">다가오는 일정</h3>
                    <div id="schedule-list" class="space-y-2"></div>
                </div>
            </section>

        </main>

        <nav class="absolute bottom-0 left-0 right-0 h-16 bg-white border-t border-gray-200 flex justify-around items-center z-50">
            <button onclick="switchPage('home')" class="nav-btn text-gray-900 flex flex-col items-center gap-0.5">
                <i class="fa-solid fa-house text-xl"></i>
                <span class="text-[10px] font-medium">홈</span>
            </button>
            <button onclick="switchPage('story')" class="nav-btn text-gray-400 flex flex-col items-center gap-0.5">
                <i class="fa-solid fa-book-open text-xl"></i>
                <span class="text-[10px] font-medium">동화</span>
            </button>
            <button onclick="switchPage('lullaby')" class="nav-btn text-gray-400 flex flex-col items-center gap-0.5">
                <i class="fa-solid fa-music text-xl"></i>
                <span class="text-[10px] font-medium">자장가</span>
            </button>
            <button onclick="switchPage('schedule')" class="nav-btn text-gray-400 flex flex-col items-center gap-0.5">
                <i class="fa-regular fa-calendar-check text-xl"></i>
                <span class="text-[10px] font-medium">일정</span>
            </button>
        </nav>
    </div>

    <script>
        const USER_ID = 1; // 기본 연동 유저 ID 예시

        document.addEventListener("DOMContentLoaded", () => {
            loadInitialData();
            setupScheduleForm();
        });

        // 페이지 네비게이션 스위칭 함수
        function switchPage(pageId) {
            document.querySelectorAll('.page-view').forEach(el => el.classList.add('hidden'));
            document.getElementById(`page-${pageId}`).classList.remove('hidden');
            
            // 네비게이션 아이콘 강조 조절
            document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.replace('text-gray-900', 'text-gray-400'));
            event.currentTarget.classList.replace('text-gray-400', 'text-gray-900');
        }

        async function loadInitialData() {
            try {
                // 1. 타임라인 및 마일스톤 데이터 연동
                const tlRes = await fetch(`/api/timeline/${USER_ID}`);
                const tlData = await tlRes.json();
                
                if(tlData.success) {
                    // 상단 스토리 마일스톤 빌드
                    const milestoneBox = document.getElementById('milestone-stories');
                    milestoneBox.innerHTML = tlData.timeline.map(item => `
                        <div class="flex flex-col items-center flex-shrink-0 cursor-pointer" onclick="alert('${item.description}')">
                            <div class="w-16 h-16 rounded-full p-[2px] ${item.active ? 'bg-gradient-to-tr from-amber-500 to-pink-500' : 'bg-gray-300'} flex items-center justify-center">
                                <div class="w-full h-full bg-white rounded-full flex items-center justify-center border-2 border-white">
                                    <span class="text-xs font-semibold ${item.active ? 'text-gray-900' : 'text-gray-400'}">${item.event}</span>
                                </div>
                            </div>
                            <span class="text-[11px] text-gray-500 mt-1">${item.active ? '달성 완료' : '진행 예정'}</span>
                        </div>
                    `).join('');
                }

                // 2. 피드 및 문화 이벤트 연동
                const evRes = await fetch('/api/events');
                const evData = await evRes.json();
                
                const feedBox = document.getElementById('home-feed');
                feedBox.innerHTML = evData.events.map(ev => `
                    <div class="border-b border-gray-100 pb-4 bg-white">
                        <div class="flex items-center px-4 py-3 gap-3">
                            <div class="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-xs font-bold text-indigo-600">M</div>
                            <div>
                                <p class="text-xs font-bold text-gray-800">Mother-All Official</p>
                                <p class="text-[10px] text-gray-400">${ev.location} • 추천 이벤트</p>
                            </div>
                        </div>
                        <div class="w-full h-64 bg-slate-100 flex flex-col justify-center items-center p-6 text-center border-y border-gray-50">
                            <i class="fa-solid fa-map-location-dot text-4xl text-gray-400 mb-3"></i>
                            <h3 class="font-bold text-lg text-gray-800">${ev.title}</h3>
                            <p class="text-xs text-gray-500 mt-1">개최일: ${ev.date}</p>
                        </div>
                        <div class="p-4">
                            <div class="flex gap-4 text-xl text-gray-700 mb-2">
                                <i class="fa-regular fa-heart cursor-pointer hover:text-red-500"></i>
                                <i class="fa-regular fa-comment"></i>
                            </div>
                            <p class="text-xs text-gray-700"><span class="font-bold mr-2">Mother-All</span>아기들과 함께 참여하기 좋은 전통 문화 행사 정보를 공유합니다.</p>
                        </div>
                    </div>
                `).join('');

                // 3. 추천 동화 데이터 가져오기
                const storyRes = await fetch(`/api/story/${USER_ID}`);
                const storyData = await storyRes.json();
                document.getElementById('story-card').innerHTML = `
                    <div class="p-6 bg-amber-50/50 text-center border-b border-gray-100">
                        <i class="fa-solid fa-book text-4xl text-amber-600 mb-2"></i>
                        <h3 class="text-xl font-bold text-amber-900">${storyData.title}</h3>
                        <span class="text-xs bg-amber-200 text-amber-800 px-2 py-0.5 rounded-full font-semibold inline-block mt-2">${storyData.category || '전래동화'}</span>
                    </div>
                    <div class="p-4">
                        <p class="text-sm text-gray-600 leading-relaxed">${storyData.description}</p>
                    </div>
                `;

                // 4. 자장가 가져오기
                const lullRes = await fetch(`/api/lullaby/${USER_ID}`);
                const lullData = await lullRes.json();
                document.getElementById('lullaby-card').innerHTML = `
                    <i class="fa-solid fa-moon text-5xl text-violet-500 mb-4 animate-pulse"></i>
                    <h3 class="text-lg font-bold text-gray-800">${lullData.title}</h3>
                    <p class="text-xs text-gray-400 mt-1 mb-4">${lullData.description}</p>
                    <audio controls class="w-full mt-2">
                        <source src="${lullData.audio_url}" type="audio/mpeg">
                        브라우저가 오디오를 지원하지 않습니다.
                    </audio>
                `;

                // 5. 일정 리스트 가져오기
                loadSchedules();

            } catch (err) {
                console.error("데이터 로드 실패:", err);
            }
        }

        // 스케줄 리스트 전용 로드기 함수
        async function loadSchedules() {
            const res = await fetch(`/api/schedules/${USER_ID}`);
            const data = await res.json();
            const listContainer = document.getElementById('schedule-list');
            
            if(data.schedules.length === 0) {
                listContainer.innerHTML = '<p class="text-xs text-gray-400 text-center py-4">등록된 일정이 없습니다.</p>';
                return;
            }

            listContainer.innerHTML = data.schedules.map(item => `
                <div class="flex justify-between items-center bg-white p-3 border border-gray-200 rounded-xl shadow-sm">
                    <div>
                        <p class="text-xs font-bold text-gray-400">${item.date}</p>
                        <h4 class="text-sm font-semibold text-gray-800">${item.title}</h4>
                        ${item.description ? `<p class="text-xs text-gray-500 mt-0.5">${item.description}</p>` : ''}
                    </div>
                    <button onclick="deleteSchedule(${item.id})" class="text-xs text-red-400 hover:text-red-600 p-2">
                        <i class="fa-regular fa-trash-can"></i>
                    </button>
                </div>
            `).join('');
        }

        // 스케줄 폼 이벤트 바인딩
        function setupScheduleForm() {
            document.getElementById('schedule-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                const title = document.getElementById('sched-title').value;
                const date = document.getElementById('sched-date').value;
                const description = document.getElementById('sched-desc').value;

                const res = await fetch(`/api/schedules/${USER_ID}`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ title, date, description })
                });

                if(res.ok) {
                    document.getElementById('schedule-form').reset();
                    loadSchedules();
                }
            });
        }

        // 스케줄 삭제
        async function deleteSchedule(id) {
            if(confirm("이 일정을 삭제하시겠습니까?")) {
                const res = await fetch(`/api/schedules/${id}`, { method: 'DELETE' });
                if(res.ok) loadSchedules();
            }
        }
    </script>
</body>
</html>
"""


# --------------------------------------------------
# UI Route
# --------------------------------------------------
@app.route("/")
def index():
    # 모바일 웹 앱 인터페이스 출력
    return render_template_string(HTML_TEMPLATE)


# --------------------------------------------------
# API Endpoints
# --------------------------------------------------
@app.route("/api/status")
def status():
    return jsonify({"service": "Mother-All", "version": "1.0", "status": "running"})


@app.route("/api/users", methods=["POST"])
def create_user():
    data = request.json
    try:
        birth_date = datetime.strptime(data["baby_birth"], "%Y-%m-%d").date()
        user = User(
            name=data["name"],
            nationality=data["nationality"],
            language=data["language"],
            baby_name=data["baby_name"],
            baby_birth=birth_date,
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({"success": True, "user_id": user.id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/timeline/<int:user_id>")
def timeline(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    age = calculate_month_age(user.baby_birth)
    return jsonify(
        {
            "success": True,
            "baby_age_month": age,
            "timeline": get_cultural_milestone(age),
        }
    )


@app.route("/api/story/<int:user_id>")
def story_recommendation(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"success": False}), 404

    age = calculate_month_age(user.baby_birth)
    story_title = recommend_story(age)
    story = CulturalStory.query.filter_by(title=story_title).first()

    if story:
        return jsonify(
            {
                "title": story.title,
                "description": story.description,
                "category": story.category,
            }
        )
    return jsonify({"title": story_title, "description": "추천 전래동화"})


@app.route("/api/lullaby/<int:user_id>")
def lullaby_recommendation(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"success": False}), 404

    lullaby = Lullaby.query.first()
    if lullaby:
        return jsonify(
            {
                "title": lullaby.title,
                "description": lullaby.description,
                "audio_url": lullaby.audio_url,
            }
        )
    return jsonify({"title": "섬집아기", "description": "한국 전통 자장가"})


@app.route("/api/events")
def cultural_events():
    return jsonify(
        {
            "events": [
                {"title": "전통놀이 체험", "location": "서울", "date": "2026-07-01"},
                {"title": "어린이 국악 공연", "location": "부산", "date": "2026-07-10"},
            ]
        }
    )


@app.route("/api/culture-guide")
def culture_guide():
    topic = request.args.get("topic")
    guides = {
        "백일": "백일은 아기의 건강과 장수를 기원하는 한국 전통 문화입니다.",
        "돌잔치": "돌잔치는 첫 생일을 기념하는 대표적인 한국 문화입니다.",
        "추석": "추석은 가족이 모여 조상을 기리고 음식을 나누는 명절입니다.",
    }
    return jsonify(
        {"topic": topic, "guide": guides.get(topic, "문화 정보를 준비 중입니다.")}
    )


# --------------------------------------------------
# [신규 API] Schedule Management API
# --------------------------------------------------
@app.route("/api/schedules/<int:user_id>", methods=["GET", "POST"])
def manage_schedules(user_id):
    if request.method == "POST":
        data = request.json
        try:
            sched_date = datetime.strptime(data["date"], "%Y-%m-%d").date()
            new_sched = Schedule(
                user_id=user_id,
                title=data["title"],
                date=sched_date,
                description=data.get("description", ""),
            )
            db.session.add(new_sched)
            db.session.commit()
            return jsonify({"success": True, "schedule_id": new_sched.id}), 21
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400

    else:  # GET 요청
        schedules = (
            Schedule.query.filter_by(user_id=user_id).order_by(Schedule.date).all()
        )
        return jsonify(
            {
                "schedules": (
                    {
                        "id": s.id,
                        "title": s.title,
                        "date": s.date.strftime("%Y-%m-%d"),
                        "description": s.description,
                    }
                )
                for s in schedules
            }
        )


@app.route("/api/schedules/<int:schedule_id>", methods=["DELETE"])
def delete_schedule(schedule_id):
    sched = db.session.get(Schedule, schedule_id)
    if not sched:
        return jsonify({"success": False, "message": "일정을 찾을 수 없습니다."}), 404

    db.session.delete(sched)
    db.session.commit()
    return jsonify({"success": True, "message": "일정이 삭제되었습니다."})


# --------------------------------------------------
# Seed Data
# --------------------------------------------------
def seed_data():
    # 데모 유저 한 명 생성 (기본 연동용)
    if User.query.count() == 0:
        demo_user = User(
            name="홍길동",
            nationality="Korea",
            language="ko",
            baby_name="정우",
            baby_birth=datetime.strptime("2026-01-15", "%Y-%m-%d").date(),
        )
        db.session.add(demo_user)

    if CulturalStory.query.count() == 0:
        stories = [
            CulturalStory(
                title="까치와 호랑이",
                category="전래동화",
                age_group="0-6",
                description="용기와 지혜를 알려주는 이야기",
            ),
            CulturalStory(
                title="흥부와 놀부",
                category="전래동화",
                age_group="6-12",
                description="나눔과 형제애를 배우는 이야기",
            ),
            CulturalStory(
                title="해님달님",
                category="전래동화",
                age_group="12-24",
                description="가족애를 배우는 이야기",
            ),
            CulturalStory(
                title="선녀와 나무꾼",
                category="전래동화",
                age_group="24-36",
                description="상상력을 키워주는 이야기",
            ),
        ]
        db.session.add_all(stories)

    if Lullaby.query.count() == 0:
        db.session.add(
            Lullaby(
                title="섬집아기",
                description="한국 대표 자장가",
                audio_url="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",  # 실제 재생 가능한 샘플 주소로 교체
                age_group="0-36",
            )
        )
    db.session.commit()


# --------------------------------------------------
# Main Entry Point
# --------------------------------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_data()

    print(" -> 브라우저에서 http://127.0.0.1:5000 접속 시 모바일 전용 UI가 노출됩니다.")
    app.run(host="0.0.0.0", port=5000, debug=True)
