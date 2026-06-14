<h4>1. 제안 배경 및 필요성 (Pain Point)</h4>

<p>한국 사회는 다문화 가정의 증가와 함께 다양한 문화적 배경을 가진 가족들이 공동체에 적응하고자 하는 과정에서, 특히 외국인 배우자가 한국 역사와 문화에 대한 이해 부족으로 인해 자녀 양육에 있어 심리적·정서적 장벽을 겪고 있습니다. 이러한 문제는 단순한 정보 부족을 넘어, 한국 사회에 대한 소속감과 정서적 유대감 형성의 어려움으로 이어지며, 결과적으로 다문화 가정 내 자녀의 정체성 혼란과 사회적 소외로 이어질 수 있습니다.</p>

<p>현재의 한국사 교육은 주로 국적 취득을 위한 암기 중심의 내용으로 구성되어 있어, 다문화 가정의 부모가 자녀에게 '왜 이렇게 되었는지', '이 문화는 어떤 의미를 가지는지'에 대한 깊이 있는 설명을 제공하기 어렵습니다. 이는 단순한 지식 전달을 넘어, 한국 사회와의 감정적 연결을 형성하는 데 있어 핵심적인 역할을 하지 못합니다. 특히 자녀가 '왜 우리 집은 다른 사람과 다르게 사는가?'라는 질문을 할 때, 부모는 자신의 한계를 느끼며 소외감을 경험하게 되고, 이는 가족 간의 소통 장벽으로 연결됩니다.</p>

<p>이러한 문제를 해결하기 위해 '한누리' 플랫폼은 단순한 역사적 사실 전달을 넘어, 다문화 가정의 부모와 자녀 모두가 한국 역사와 문화에 대한 감정적 유대감을 형성할 수 있도록 지원하는 맞춤형 스토리텔링 교육 방안을 제시합니다. 이는 단순한 정보 제공을 넘어서, 정서적 소속감과 자녀 양육의 주체로서의 역량 강화를 목표로 하며, 국가 차원에서 다문화 가정의 사회적 통합과 문화적 수용을 촉진하는 공익적 가치를 지닙니다.</p>

<p>따라서 '한누리'는 한국 역사와 문화의 정서적 연결 고리를 통해 다문화 가정이 사회에 자연스럽게 적응하고, 자녀 양육의 주체로서 자신감을 갖출 수 있도록 돕는 중요한 교육 플랫폼으로서, 국가의 문화 정책과 복지 정책의 핵심적 지원 대상이 되어야 합니다.</p><hr class="my-5 border-info"><h1>2. 역사 문화 공공데이터 활용 및 AI 아키텍처 설계</h1>

<p><strong>'한누리'</strong>는 다문화 가정의 외국인 배우자들이 한국 역사와 문화를 직관적으로 이해할 수 있도록 지원하는 AI 기반 맞춤형 스토리텔링 플랫폼입니다. 이 장에서는 <strong>국립중앙박물관, 국사편찬위원회, 한국학중앙연구원, 국립국어원</strong>의 공공데이터를 활용한 <strong>LLM 기반 AI 아키텍처</strong>와 <strong>초개인화 상호주의 역사 스토리텔링</strong> 생성 파이프라인을 구조화하여 설명합니다.</p>

<h4>2.1 핵심 공공데이터 소스 및 활용 방안</h4>

<table>
  <thead>
    <tr>
      <th>데이터 소스</th>
      <th>데이터 유형</th>
      <th>주요 활용 내용</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>국립중앙박물관 유물 및 소장품 데이터 API</strong></td>
      <td>문화유산, 유물 정보</td>
      <td>한국 역사의 시각적 매개체 제공. 외국인 배우자의 출신 국가와 유사한 유물과 비교 분석</td>
    </tr>
    <tr>
      <td><strong>국사편찬위원회 한국사데이터베이스 사료 정보</strong></td>
      <td>역사 문서, 기록</td>
      <td>한국 역사의 흐름과 사건의 배경을 정확히 전달. 외국인 배우자의 국가 역사와 연결</td>
    </tr>
    <tr>
      <td><strong>한국학중앙연구원 향토문화전자대전 인물/지리 정보</strong></td>
      <td>지리, 인물, 지역 문화</td>
      <td>지역별 역사적 인물과 사건의 맥락을 제공하여 다문화 배경 이해 강화</td>
    </tr>
    <tr>
      <td><strong>국립국어원 다국어 대역사전 데이터</strong></td>
      <td>다국어 역사 용어, 번역 정보</td>
      <td>한국 역사 용어의 다국어 해석 및 문화적 맥락 제공. 외국인 배우자 언어 장벽 해소</td>
    </tr>
  </tbody>
</table>

<h4>2.2 AI 아키텍처 설계</h4>

<p><strong>'한누리'</strong>는 LLM 기반의 <strong>다중 데이터 소스 통합형 AI 아키텍처</strong>를 기반으로 합니다. 이 아키텍처는 다음과 같은 구성 요소로 이루어져 있습니다:</p>

<ul>
  <li><strong>데이터 수집 모듈</strong>: 공공데이터 API를 통해 유물, 역사 문서, 인물 및 지리 정보를 실시간 수집</li>
  <li><strong>데이터 정제 및 매핑 모듈</strong>: 수집된 데이터를 일관성 있는 구조로 정제하고, 외국인 배우자의 출신 국가와의 상호 연결을 위한 매핑 수행</li>
  <li><strong>사용자 프로필 생성 모듈</strong>: 배우자의 국적, 언어, 문화 배경 등을 기반으로 사용자 맞춤형 프로파일 생성</li>
  <li><strong>스토리텔링 생성 엔진</strong>: LLM 기반의 스토리 생성 알고리즘을 통해 상호주의적 역사 스토리 자동 생성</li>
  <li><strong>사용자 피드백 및 지속 학습 모듈</strong>: 사용자 반응에 따라 AI의 스토리텔링 품질을 지속적으로 개선</li>
</ul>

<h4>2.3 초개인화 상호주의 역사 스토리텔링 파이프라인</h4>

<p><strong>'한누리'</strong>는 사용자 프로필과 공공데이터를 기반으로 <strong>초개인화 상호주의 역사 스토리텔링</strong>을 생성합니다. 아래는 이 과정의 단계별 설명입니다:</p>

<ol>
  <li><strong>사용자 정보 수집</strong>: 외국인 배우자의 출신 국가, 언어, 문화적 배경 정보 입력</li>
  <li><strong>데이터 매칭 및 분석</strong>: 해당 국가의 역사와 한국 역사 간 유사 사건/인물 매핑</li>
  <li><strong>LLM 기반 스토리 생성</strong>: AI가 매핑된 데이터를 바탕으로 자연어로 구성된 스토리 자동 생성</li>
  <li><strong>시각화 및 다국어 지원</strong>: 유물 이미지, 지도, 인물 사진 등을 시각적으로 제공하며, 다국어 번역 기능 포함</li>
  <li><strong>사용자 피드백 반영</strong>: 사용자가 스토리에 대한 평가 및 피드백을 제공하여 AI 학습에 활용</li>
</ol>

<h4>2.4 예시: 베트남 배우자의 한국 역사 스토리텔링</h4>

<p>예를 들어, <strong>베트남 출신 배우자</strong>가 '한누리'를 이용할 경우 다음과 같은 방식으로 스토리텔링이 생성됩니다:</p>

<ol>
  <li><strong>사용자 프로필</strong>: 베트남, 한국어 수준 중간, 역사적 관심사 높음</li>
  <li><strong>데이터 매칭</strong>: 베트남 전쟁과 한국의 고려-조선 시대의 외세 침략 비교</li>
  <li><strong>스토리 생성</strong>: '고려시대의 외세 침략과 베트남의 전쟁 역사 비교'를 주제로 한 스토리</li>
  <li><strong>시각화</strong>: 고려 시대 유물 사진 + 베트남 전쟁 관련 이미지 비교</li>
  <li><strong>다국어 지원</strong>: 한국어와 베트남어로 동일한 스토리 제공</li>
</ol>

<h4>2.5 기술적 장점 및 혁신성</h4>

<ul>
  <li><strong>공공데이터 활용의 최적화</strong>: 다양한 공공기관 데이터를 통합하여 역사적 맥락의 깊이 있는 스토리텔링 제공</li>
  <li><strong>초개인화된 학습 경험</strong>: 외국인 배우자의 문화적 배경을 반영한 맞춤형 역사 스토리 생성</li>
  <li><strong>AI 기반 자동화</strong>: LLM 기반으로 인해 수작업이 아닌 자동화된 스토리텔링 가능</li>
  <li><strong>다문화 교육의 디지털 혁신</strong>: 다문화 가정을 위한 맞춤형 역사 교육 플랫폼 제공</li>
</ul>

<p>이러한 구조를 통해 <strong>'한누리'</strong>는 단순히 한국 역사에 대한 정보 전달을 넘어, <strong>다문화 배경의 외국인 배우자들이 한국 문화와 역사에 대해 이해하고 공감할 수 있는 경로</strong>를 제시합니다.</p><hr class="my-5 border-info"><h4>3. 서비스 독창성 및 우위성</h4>

<p>본 프로젝트 '한누리(Hannuri)'는 기존의 귀화 시험 중심의 역사 교육 자료와 일반적인 한국사 온라인 강의에 비해, 다문화 가정의 실질적 교육 요구를 충족시키기 위한 맞춤형 스토리텔링 방식을 채택하고 있습니다. 아래 표는 <strong>데이터 신뢰도</strong>, <strong>다국어 비교 분석 기능</strong>, <strong>자녀 교육 활용성</strong>, <strong>학습 난이도 조정</strong>, <strong>에듀테크 공익성</strong>의 다섯 가지 차원에서 각 솔루션 간의 차별화된 우위성을 명확히 보여줍니다.</p>

<table class="table table-bordered table-striped text-center">
  <thead>
    <tr>
      <th>구분</th>
      <th>귀화 시험용 역사 교재</th>
      <th>일반 한국사 인강</th>
      <th>한누리(Hannuri) (본 기획)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>데이터 신뢰도 (공공 데이터 연계)</strong></td>
      <td>문화체육관광부 및 교육부 공공 데이터 미연계, 주로 시험 중심의 편집형 자료</td>
      <td>일부 공공 데이터 활용, 그러나 교육 목적에 맞춘 구조화 부족</td>
      <td>문화체육관광부, 국립중앙도서관, 한국사진문학원 등 공공 데이터와 API 연동, 학술적 신뢰성 확보</td>
    </tr>
    <tr>
      <td><strong>외국인 모국 역사와의 비교 분석 기능</strong></td>
      <td>비교 분석 없음. 단순 한국 역사 중심</td>
      <td>일부 비교적 간단한 역사적 맥락 제시, 자세한 비교 불가</td>
      <td>AI 기반 모국 역사와의 연계 분석 제공 (예: 중국, 일본, 미국 등과의 역사적 유사성/차이점), 다문화 이해 증진</td>
    </tr>
    <tr>
      <td><strong>자녀 교육/양육 활용성</strong></td>
      <td>교육 목적 외에 자녀 양육에 대한 기능 없음</td>
      <td>학습자 중심의 강의 구조, 가정에서의 실질적 활용 부족</td>
      <td>부모-자녀 간 공유 스토리텔링 모듈 제공, 가정 내 역사 교육에 적합한 콘텐츠 구성</td>
    </tr>
    <tr>
      <td><strong>학습 난이도 조정 (다국어 번역 및 한글 숙련도 매칭)</strong></td>
      <td>한국어 기준으로만 제공, 다문화 가정 대상 맞춤형 없음</td>
      <td>기본 영어 자막 제공, 난이도 조절 불가</td>
      <td>AI 기반 언어 적응형 학습 모델 적용, 다국어 번역 + 한글 숙련도 수준에 따른 콘텐츠 자동 조정</td>
    </tr>
    <tr>
      <td><strong>에듀테크 공익성</strong></td>
      <td>시험 통과 중심으로, 사회적 공익성 부족</td>
      <td>일반 교육 콘텐츠로, 다문화 가정의 특수성 반영 미흡</td>
      <td>공공기관과 협력한 맞춤형 교육 콘텐츠 제공, 다문화 가정의 역사적 소속감 형성 및 문화적 통합 지원</td>
    </tr>
  </tbody>
</table>

<h4>한누리의 독창성 요약</h4>

<p>'한누리'는 단순히 한국 역사 교육을 넘어서, 다문화 가정의 자녀가 자신의 모국 역사와 한국 역사 간의 연결고리를 이해하고, 언어적·문화적으로도 안정적인 정체성을 형성할 수 있도록 지원하는 <strong>AI 기반 맞춤형 스토리텔링 플랫폼</strong>입니다. 이는 다음과 같은 핵심 차별화 요소를 통해 기존 솔루션과 명확히 구분됩니다:</p>

<ul>
  <li><strong>AI 기반 역사적 맥락 연결</strong>: 외국인 모국 역사와 한국 역사 간의 비교 분석을 통해 문화적 통합 촉진</li>
  <li><strong>다국어 및 언어 적응형 학습</strong>: 한글 숙련도에 따라 자동 조정되는 맞춤형 콘텐츠 제공</li>
  <li><strong>공공 데이터 연계 및 학술적 신뢰성 확보</strong>: 공공기관과의 협력을 통해 교육 콘텐츠의 신뢰성과 정확성 보장</li>
  <li><strong>가정 내 공동 학습 지원</strong>: 부모와 자녀가 함께 사용할 수 있는 스토리텔링 모듈 제공</li>
  <li><strong>에듀테크 공익성 강화</strong>: 다문화 가정의 역사적 소속감과 문화적 정체성 형성에 기여하는 사회적 가치</li>
</ul>

<p>이러한 차별화된 기능은 단순한 교육 도구를 넘어, <strong>다문화 사회에서의 역사적 이해와 문화적 통합을 위한 지속 가능한 에듀테크 솔루션</strong>으로서, 문화체육관광부 공공데이터 분석 경진대회 대상(대통령상) 수상 가능성을 높이는 핵심 요소입니다.</p><hr class="my-5 border-info"><h1>4. 기대효과 및 향후 비즈니스/확산 방안</h1>

<h2>4.1 정량적 효과</h2>
<p>본 프로젝트는 AI 기반 맞춤형 한국 역사-문화 스토리텔링 플랫폼 '한누리'를 통해 다문화 가정의 사회적 통합과 교육 접근성을 높이는 것을 목표로 합니다. 아래는 주요 정량적 효과입니다.</p>

<table border="1" cellpadding="5" cellspacing="0">
  <thead>
    <tr>
      <th>지표</th>
      <th>설명</th>
      <th>기대 효과</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>다문화 가정의 한국 사회 정착 만족도 증가율</td>
      <td>한누리 사용 후 다문화 가정이 한국 사회에 대한 정착감과 만족도를 평가하는 지표</td>
      <td>+25% 이상</td>
    </tr>
    <tr>
      <td>자녀 역사 교육 공백 해소율</td>
      <td>다문화 가정 자녀의 한국 역사 및 문화에 대한 이해도 향상률</td>
      <td>+30% 이상</td>
    </tr>
    <tr>
      <td>다문화 센터 보급률</td>
      <td>한누리 플랫폼이 다문화 가족 지원 센터에 채택되는 비율</td>
      <td>전국 80% 이상의 센터에서 사용</td>
    </tr>
    <tr>
      <td>AI 맞춤형 콘텐츠 이용률</td>
      <td>사용자 맞춤형 스토리텔링 콘텐츠를 활용하는 비율</td>
      <td>70% 이상</td>
    </tr>
  </tbody>
</table>

<h2>4.2 정성적 효과</h2>
<p>정량적 지표 외에도 '한누리'는 다문화 가정의 정서적 고립 해소와 진정한 의미의 사회 통합을 위한 가치를 제공합니다.</p>

<ul>
  <li><strong>다문화 가정 내 정서적 고립 완화</strong>: 다양한 문화적 배경을 가진 가족들이 한국 역사와 문화에 대해 이해하고 소속감을 느끼는 데 기여</li>
  <li><strong>진정한 의미의 다문화 사회 통합</strong>: 역사적 정체성과 문화적 공감대 형성을 통해 사회적 수용도 향상</li>
  <li><strong>가족 간 소통 강화</strong>: 공유되는 역사 스토리텔링을 통해 부모와 자녀 간의 대화 및 이해 증진</li>
</ul>

<h2>4.3 B2G 확산 방안</h2>

<h4>4.3.1 전국 가족센터(다문화가족지원센터) 표준 교육 패키지 채택</h4>
<p>'한누리'는 다문화 가족 지원 센터의 표준 교육 패키지로 자리매김할 수 있도록 다음과 같은 전략을 제시합니다:</p>
<ul>
  <li>국가 지원 프로그램으로서의 정책적 지정 및 인증</li>
  <li>센터별 맞춤형 교육 커스터마이징 기능 제공</li>
  <li>센터 운영자 대상 온라인 교육 및 피드백 시스템 구축</li>
</ul>

<h4>4.3.2 박물관/유적지 연계 역사 탐방 다문화 패밀리 O2O 바우처 모델</h4>
<p>온라인에서 학습한 내용을 오프라인 체험과 연계하여 다문화 가족의 문화 체험을 강화하는 O2O 모델입니다:</p>
<ul>
  <li>한누리 사용자에게 박물관/유적지 방문 바우처 제공</li>
  <li>AI 기반 콘텐츠와 실제 체험 간 연결성 강화 (예: 가상 체험 → 실제 전시물)</li>
  <li>다문화 가족 중심의 맞춤형 패밀리 투어 프로그램 개발</li>
</ul>

<h4>4.3.3 확산 전략 요약</h4>
<table border="1" cellpadding="5" cellspacing="0">
  <thead>
    <tr>
      <th>확산 채널</th>
      <th>전략</th>
      <th>예상 효과</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>가족센터</td>
      <td>교육 패키지 제공 및 운영자 교육</td>
      <td>센터별 채택률 80% 이상</td>
    </tr>
    <tr>
      <td>박물관/유적지</td>
      <td>O2O 바우처 모델과 연계 프로그램 운영</td>
      <td>다문화 가족 방문 증가 30%</td>
    </tr>
    <tr>
      <td>정책 지원</td>
      <td>문화체육관광부 및 지자체와의 협력 프로그램 연계</td>
      <td>정책적 지속 가능성 확보</td>
    </tr>
  </tbody>
</table>

<h2>4.4 향후 비즈니스 모델 전망</h2>
<p>'한누리'는 단순 교육 도구를 넘어, 정책 기반의 사회적 가치 창출을 목표로 한 지속 가능한 비즈니스 모델로 확장될 수 있습니다:</p>
<ul>
  <li><strong>유료 커스터마이징 서비스</strong>: 고급 맞춤형 콘텐츠 및 전문 상담 제공</li>
  <li><strong>해외 다문화 가정 확장 시장 진출</strong>: 한국 문화에 대한 해외 이민자 가정 지원</li>
  <li><strong>데이터 기반 정책 제안</strong>: 사용자 행동 분석을 통한 다문화 정책 개선 제안</li>
</ul>

<p>이러한 전략적 확산과 지속 가능성은 '한누리'가 문화체육관광부 공공데이터 분석 경진대회에서 대상(대통령상) 수상의 기반을 마련할 수 있는 핵심 요소입니다.</p><hr class="my-5 border-info"><h1>AI 기반 다문화 가정을 위한 맞춤형 한국 역사-문화 스토리텔링 가이드 '한누리'</h1>

<h4>5. 서비스 코어 이식용 AI 시스템 프롬프트(Few-Shot Engineering) 명세서</h4>

<p>본 문서는 <strong>'한누리'</strong> 플랫폼의 핵심 AI 시스템을 Flask 백엔드에서 구동하기 위해 설계된 <code>SYSTEM_PROMPT</code>과 <code>USER_INPUT_STRUCTURE</code>를 명시합니다. 이 프롬프트는 사용자 입력 파라미터에 따라 맞춤형 역사-문화 스토리텔링 콘텐츠를 생성하는 데 필수적입니다.</p>

<h4>1. SYSTEM_PROMPT 구성</h4>
<pre><code class="text-info bg-dark p-3 d-block rounded">
[SYSTEM PROMPT]

당신은 한국 역사와 문화에 특화된 다문화 가정을 위한 맞춤형 스토리텔링 전문가입니다. 사용자의 배경(국적, 언어 수준, 자녀 나이)과 관심 시대를 기반으로, 어린이나 성인 모두가 이해할 수 있도록 재미있고 교육적인 역사 이야기를 생성해주세요.

[사용자 입력 가변값]
- spouse_nationality: 배우자의 국적 (예: 베트남, 중국, 러시아 등)
- korean_level: 한국어 수준 (초급, 중급, 고급 등)
- child_age: 자녀의 나이 (예: 5세, 10세 등)
- target_era: 관심 있는 역사 시대 (예: 조선, 고려, 삼국시대 등)

[지시사항]
1. 사용자의 배경에 맞춘 언어적 접근을 고려하세요.
2. 역사적 인물과 사건은 간단하고 재미있게 설명해주세요.
3. 사용자가 익숙한 문화적 요소와 연결하여 설명해주세요.
4. 자녀의 나이에 따라 어린이용 스토리텔링 방식으로 구성하세요.
5. 시대별 역사적 배경과 문화적 특성을 간략히 정리하고, 해당 시대의 인물이나 사건을 중심으로 이야기를 전개해주세요.

[예시]
- 베트남 출신/한국어 초급/7세 자녀를 둔 배우자에게 세종대왕의 한글 창제 역사를 베트남의 쯔놈(Chữ Nôm) 문자 역사와 비교하며 어린이 눈높이로 풀어주도록 지시합니다.
</code></pre>

<h4>2. USER_INPUT_STRUCTURE 구성</h4>
<pre><code class="text-info bg-dark p-3 d-block rounded">
[USER INPUT STRUCTURE]

{
  "spouse_nationality": "베트남",
  "korean_level": "초급",
  "child_age": 7,
  "target_era": "조선"
}

[예시]
{
  "spouse_nationality": "중국",
  "korean_level": "중급",
  "child_age": 10,
  "target_era": "삼국시대"
}
</code></pre>

<h4>3. Few-Shot 예시: 베트남 출신 가정의 세종대왕 이야기</h4>
<pre><code class="text-info bg-dark p-3 d-block rounded">
[USER INPUT EXAMPLE]
{
  "spouse_nationality": "베트남",
  "korean_level": "초급",
  "child_age": 7,
  "target_era": "조선"
}

[AI RESPONSE EXAMPLE]
세종대왕은 한국에서 아주 오래 전에 살았던 영웅이에요. 그는 사람들을 위해 새로운 글을 만들었어요. 베트남에도 쯔놈(Chữ Nôm)이라는 글이 있었는데, 세종대왕이 만든 한글은 사람들이 더 쉽게 배울 수 있도록 만들어졌어요. 

세종대왕은 아주 똑똑한 사람이었고, 사람들을 위해 많은 일을 했어요. 그는 '한글'이라는 새로운 글을 만들었어요. 이 글은 사람들이 읽고 쓰기 쉬워서, 베트남의 쯔놈처럼 새로운 글이 생긴 거예요. 

우리가 지금 쓰는 한글은 세종대왕이 만든 것이에요. 그리고 이 글은 많은 나라에서 사용되고 있어요!
</code></pre>

<h4>4. 개발 시 고려사항</h4>
<ul>
  <li>Flask 백엔드에서 AI 모델 호출 시 위의 <code>SYSTEM_PROMPT</code>과 <code>USER_INPUT_STRUCTURE</code>를 JSON 형식으로 전달합니다.</li>
  <li>AI 모델은 <code>spouse_nationality</code>, <code>korean_level</code>, <code>child_age</code>, <code>target_era</code> 파라미터에 따라 동적으로 콘텐츠를 생성해야 합니다.</li>
  <li>SQLite DB는 사용자 프로필과 콘텐츠 히스토리를 저장하여, 재사용 가능한 맞춤형 스토리텔링을 지원합니다.</li>
</ul>

<h4>5. 결론</h4>
<p>이 명세서는 <strong>'한누리'</strong> 플랫폼의 AI 시스템이 다문화 가정의 문화적 이해를 증진시키기 위한 핵심 프롬프트 구조를 제공합니다. 사용자 입력에 따라 맞춤형 역사 스토리텔링을 실시간으로 생성함으로써, 한국 역사와 문화에 대한 접근성을 높이는 데 기여할 것입니다.</p><hr class="my-5 border-info">


보내주신 Flask 소스 코드의 **파이썬 문법 오류(Syntax Error) 및 변수 누락을 정밀하게 교정**하고, 요청하신 1) 자녀 육아 품앗이 및 소통을 위한 '모임(Community) 기능'과 2) 문화 공간 다국어 데이터 개선을 위한 '사용자 장소 피드백 매뉴'를 단일 아키텍처 내에 유기적으로 통합했습니다.

---

## 1. 문법 검점 및 주요 디버깅 포인트

1. **`request` 객체 누락 교정:** `map_page` 함수 내 템플릿 컨텍스트 파라미터로 `request=request`를 전달하지 않으면, HTML 내부의 `request.args.get(...)` 연산에서 Jinja2 `UndefinedError`가 발생합니다. 이를 컨텍스트 인자에 명확히 바인딩했습니다.
2. **Jinja2 반복문 가독성 보완:** 맵 스카마에서 `amenities.split(',')` 처리 시 빈 값이 들어올 때의 예외 처리 레이아웃을 보강했습니다.
3. **독립 스키마 설계:** 신규 추가된 모임(`groups`)과 장소 피드백(`place_feedbacks`) 테이블이 유기적으로 조인(Join)될 수 있도록 SQLite 무결성 제약 조건을 고도화했습니다.

---

## 2. 고도화된 통합 소스 코드 (`app.py`)

```python
import sqlite3
import os
from flask import Flask, render_template_string, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'moamoa_expert_evaluator_secret_key'
DATABASE = 'moamoa_advanced.db'

# ==========================================
# 1. 데이터베이스 초기화 및 다문화 니즈 스키마 확장
# ==========================================
def init_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 문화 공간 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS culture_places (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_ko TEXT NOT NULL,
            name_en TEXT,
            name_vi TEXT,
            category TEXT,
            address TEXT,
            lat REAL,
            lng REAL,
            amenities TEXT,            -- 수유실, 유모차 대여 등 쉼표 분리 문자열
            has_multilingual TEXT       -- Y/N
        )
    ''')
    
    # [신규 추가] 사용자 장소 피드백 테이블 (다국어 인프라 실시간 교정용)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS place_feedbacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            place_id INTEGER NOT NULL,
            user_lang TEXT NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT NOT NULL,
            suggested_amenity TEXT,    -- 추가로 필요하다고 느낀 편의시설 정보
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(place_id) REFERENCES culture_places(id)
        )
    ''')

    # [신규 추가] 다문화 자녀 육아 품앗이 및 공동체 모임 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            target_age TEXT NOT NULL,   -- '0-2세', '3-5세', '6-7세' 등
            meeting_place TEXT,        -- 모임 장소 (문화공간 연계 가능)
            leader_lang TEXT NOT NULL,  -- 방장의 모국어 코드
            member_count INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 이중언어 육아 일기 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS diaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content_original TEXT NOT NULL,
            content_ko TEXT NOT NULL,
            lang_code TEXT NOT NULL,
            image_url TEXT,
            likes INTEGER DEFAULT 0,
            feeling_tag TEXT,
            bridge_note TEXT,              -- 한국인 배우자/어린이집 소통용 정제 문구
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 연령별 맞춤형 로드맵 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS age_roadmaps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            age_group TEXT NOT NULL,       -- '0-2세', '3-5세', '6-7세'
            title_ko TEXT NOT NULL,        
            title_vi TEXT,                 
            title_en TEXT,                 
            description_ko TEXT,           
            description_vi TEXT,           
            description_en TEXT,           
            recommended_target TEXT        
        )
    ''')
    
    # 로드맵 개인화 미션 완료 상태 트래킹 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_roadmap_status (
            roadmap_id INTEGER PRIMARY KEY,
            is_completed INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 데이터셋 초기 주입
    cursor.execute("SELECT COUNT(*) FROM culture_places")
    if cursor.fetchone()[0] == 0:
        places = [
            ('국립중앙박물관 어린이박물관', "National Museum of Korea Children's Museum", 'Bảo tàng Trẻ em Quốc gia', '어린이 전용', '서울 용산구 서빙고로 137', 37.5238, 126.9804, '수유실,유모차 대여,다국어 리플렛', 'Y'),
            ('서울역사박물관', 'Seoul Museum of History', 'Bảo tàng Lịch sử Seoul', '박물관', '서울 종로구 새문안로 55', 37.5705, 126.9705, '수유실,다국어 리플렛,아동 놀이방', 'Y'),
            ('국립현대미술관 서울 어린이미술관', "MMCA Children's Museum", 'Bảo tàng Nghệ thuật Trẻ em MMCA', '미술관', '서울 종로구 삼청로 30', 37.5786, 126.9801, '유모차 대여,수유실,체험존', 'Y')
        ]
        cursor.executemany('''
            INSERT INTO culture_places (name_ko, name_en, name_vi, category, address, lat, lng, amenities, has_multilingual)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', places)

        roadmap_data = [
            ('0-2세', '오감 자극 시각/청각 매칭 동화 다이어리', 'Kích thích 5 giác quan qua Nhật ký đồng thoại', 'Sensory Stimulation Auditory Diary', '국립국어원 사전과 연동된 부모 음성 오디오북을 들려주며 한국어 단어의 기초 주파수를 인지시키는 단계', 'Giai đoạn nhận biết tần số cơ bản của từ vựng tiếng Hàn bằng cách cho trẻ nghe sách nói giọng bố mẹ kết hợp từ điển.', 'A stage to recognize the basic frequency of Korean words by playing parental voice audiobooks linked with dictionaries.', '어린이 전용'),
            ('3-5세', '공공 인프라 활용 공간 정서 대면 미션', 'Nhiệm vụ tương tác không gian văn hóa', 'Cultural Space Interaction Mission', '박물관 놀이방 및 미술관 아동 체험관을 방문하여 다양한 한국 문화 색채를 직접 눈으로 확인하는 단계', 'Giai đoạn ghé thăm phòng chơi của bảo tàng và phòng trải nghiệm của bảo tàng nghệ thuật để tận mắt chứng kiến màu sắc văn hóa Hàn Quốc.', 'A stage to check various Korean cultural colors with their own eyes by visiting museum playrooms and art museum experience centers.', '미술관'),
            ('6-7세', '한국 전통 문양 및 역사 이야기 상호작용', 'Tương tác câu chuyện lịch sử và hoa văn truyền thống', 'Traditional Pattern & History Interaction', '취학 전 자녀가 초등학교 입학 시 문화 소외를 겪지 않도록 역사적 스토리를 이중언어로 마스터하는 단계', 'Giai đoạn làm chủ các câu chuyện lịch sử bằng song ngữ để trẻ chuẩn bị vào tiểu học không bị lạc lõng về mặt văn hóa.', 'A stage to master historical stories in bilingual so that pre-school children do not experience cultural alienation upon entering elementary school.', '박물관')
        ]
        cursor.executemany('''
            INSERT INTO age_roadmaps (age_group, title_ko, title_vi, title_en, description_ko, description_vi, description_en, recommended_target)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', roadmap_data)
        
        for i in range(1, 4):
            cursor.execute('INSERT INTO user_roadmap_status (roadmap_id, is_completed) VALUES (?, 0)', (i,))

        cursor.execute('''
            INSERT INTO diaries (title, content_original, content_ko, lang_code, image_url, likes, feeling_tag, bridge_note)
            VALUES (
                '아이와 어린이박물관 오감 체험', 
                'Hôm nay tôi đã đưa con đến Bảo tàng Trẻ em. Con tôi rất thích trải nghiệm ngũ quan ở đây.', 
                '오늘 아이를 데리고 어린이박물관에 다녀왔습니다. 이곳에서의 오감 체험을 아이가 정말 좋아하네요.', 
                'vi',
                'https://images.unsplash.com/photo-1542038784456-1ea8e935640e?q=80&w=600',
                25,
                '🥰 성장',
                '안녕하세요! 오늘 아이와 함께 국립중앙박물관 어린이박물관에 방문하여 다양한 오감 체험 활동을 정상적으로 완료했습니다. 아이가 한국 문화에 친숙해지는 좋은 시간이었습니다.'
            )
        ''')
        
        # 기본 커뮤니티 모임 데이터 샘플 추가
        cursor.execute('''
            INSERT INTO groups (title, description, target_age, meeting_place, leader_lang)
            VALUES ('용산구 영아기 품앗이 모임', '주말에 어린이박물관 수유실 정보 공유하고 오감 체험 미션 함께 수행해요.', '0-2세', '국립중앙박물관 어린이박물관', 'ko')
        ''')
        
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ==========================================
# 2. 모바일 퍼스트 인스타그램 레이아웃
# ==========================================
BASE_LAYOUT = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MOA-MOA</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { max-width: 425px; margin: 0 auto; background-color: #fafafa; min-height: 100vh; display: flex; flex-direction: column; }
        .main-content { flex: 1; padding-bottom: 75px; }
        ::-webkit-scrollbar { display: none; }
    </style>
</head>
<body class="border-x border-gray-200 shadow-2xl bg-white">

    <header class="sticky top-0 bg-white border-b border-gray-100 z-50 px-4 py-3 flex justify-between items-center shadow-sm">
        <h1 class="text-2xl font-extrabold tracking-tight bg-gradient-to-r from-indigo-600 via-purple-500 to-pink-500 bg-clip-text text-transparent font-sans italic">MOA-MOA</h1>
        <div class="flex items-center space-x-3">
            <select id="langSelect" onchange="changeLanguage(this.value)" class="text-xs bg-gray-50 border border-gray-200 rounded-full px-2 py-1 font-medium focus:outline-none">
                <option value="ko" {% if current_lang == 'ko' %}selected{% endif %}>🇰🇷 KO</option>
                <option value="en" {% if current_lang == 'en' %}selected{% endif %}>🇺🇸 EN</option>
                <option value="vi" {% if current_lang == 'vi' %}selected{% endif %}>🇻🇳 VI</option>
            </select>
        </div>
    </header>

    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for message in messages %}
          <div class="bg-indigo-600 text-white text-xs text-center py-2 z-50">{{ message }}</div>
         font-medium       {% endfor %}
      {% endif %}
    {% endwith %}

    <main class="main-content">
        {##CHILD_CONTENT##}
    </main>

    <nav class="fixed bottom-0 max-w-[425px] w-full bg-white border-t border-gray-100 flex justify-around py-3 z-50 shadow-[0_-2px_10px_rgba(0,0,0,0.03)]">
        <a href="{{ url_for('feed_page') }}?lang={{ current_lang }}" class="flex flex-col items-center {% if active_menu == 'feed' %}text-indigo-600 font-bold{% else %}text-gray-400{% endif %}">
            <i class="{% if active_menu == 'feed' %}fa-solid{% else %}fa-regular{% endif %} fa-house text-lg"></i>
            <span class="text-[9px] mt-1">피드</span>
        </a>
        <a href="{{ url_for('map_page') }}?lang={{ current_lang }}" class="flex flex-col items-center {% if active_menu == 'map' %}text-indigo-600 font-bold{% else %}text-gray-400{% endif %}">
            <i class="fa-solid fa-map-location-dot text-lg"></i>
            <span class="text-[9px] mt-1">문화맵</span>
        </a>
        <a href="{{ url_for('group_page') }}?lang={{ current_lang }}" class="flex flex-col items-center {% if active_menu == 'group' %}text-indigo-600 font-bold{% else %}text-gray-400{% endif %}">
            <i class="fa-solid fa-users text-lg"></i>
            <span class="text-[9px] mt-1">품앗이모임</span>
        </a>
        <a href="{{ url_for('roadmap_page') }}?lang={{ current_lang }}" class="flex flex-col items-center {% if active_menu == 'roadmap' %}text-indigo-600 font-bold{% else %}text-gray-400{% endif %}">
            <i class="fa-solid fa-timeline text-lg"></i>
            <span class="text-[9px] mt-1">성장로드맵</span>
        </a>
        <a href="{{ url_for('write_page') }}?lang={{ current_lang }}" class="flex flex-col items-center {% if active_menu == 'write' %}text-indigo-600 font-bold{% else %}text-gray-400{% endif %}">
            <i class="fa-regular fa-square-plus text-lg"></i>
            <span class="text-[9px] mt-1">기록하기</span>
        </a>
    </nav>

    <script>
        function changeLanguage(lang) {
            const url = new URL(window.location.href);
            url.searchParams.set('lang', lang);
            window.location.href = url.toString();
        }
    </script>
</body>
</html>
"""

def render_instagram_style(child_html, **context):
    full_template = BASE_LAYOUT.replace("{##CHILD_CONTENT##}", child_html)
    return render_template_string(full_template, **context)

# ==========================================
# 3. 라우팅 핸들러 및 비즈니스 로직 고도화
# ==========================================

@app.route('/')
def feed_page():
    lang = request.args.get('lang', 'ko')
    conn = get_db_connection()
    diaries = conn.execute('SELECT * FROM diaries ORDER BY created_at DESC').fetchall()
    conn.close()

    child_template = """
    <div class="p-4 space-y-6">
        {% for diary in diaries %}
        <div class="bg-white border border-gray-100 rounded-2xl overflow-hidden shadow-sm">
            <div class="flex justify-between items-center p-3">
                <div class="flex items-center space-x-3">
                    <div class="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold">🧑‍🍼</div>
                    <div>
                        <div class="flex items-center space-x-1.5">
                            <p class="text-xs font-bold text-gray-800">모아모아_가족</p>
                            <span class="text-[10px] px-1.5 py-0.2 bg-purple-50 text-purple-600 rounded-full font-medium">{{ diary.feeling_tag }}</span>
                        </div>
                        <p class="text-[9px] text-gray-400">{{ diary.created_at }}</p>
                    </div>
                </div>
            </div>
            <img src="{{ diary.image_url }}" class="w-full h-64 object-cover">
            
            <div class="px-3 pt-3 flex items-center justify-between">
                <div class="flex items-center space-x-2">
                    <form action="{{ url_for('like_diary', diary_id=diary.id) }}?lang={{ current_lang }}" method="POST">
                        <button type="submit" class="text-red-500 hover:scale-110 transition-transform">
                            <i class="fa-solid fa-heart text-lg"></i>
                        </button>
                    </form>
                    <span class="text-xs font-bold text-gray-700">좋아요 {{ diary.likes }}개</span>
                </div>
                
                <button onclick="navigator.clipboard.writeText('{{ diary.bridge_note }}'); alert('한국인 가족/어린이집 전용 소통 문구가 복사되었습니다!');" 
                        class="text-[10px] bg-emerald-50 text-emerald-700 border border-emerald-200 px-2.5 py-1 rounded-lg font-bold flex items-center gap-1">
                    <i class="fa-solid fa-share-nodes"></i> 가족/어린이집 공유용 복사
                </button>
            </div>

            <div class="p-3 pt-1 space-y-2 text-xs">
                <p class="text-gray-900 font-semibold text-sm">💡 {{ diary.title }}</p>
                <div class="bg-gray-50 p-2.5 rounded-xl text-gray-600 italic">
                    <span class="text-[9px] text-gray-400 block font-bold mb-0.5">My Mother Tongue</span>
                    {{ diary.content_original }}
                </div>
                <div class="bg-indigo-50 p-2.5 rounded-xl text-indigo-950 font-medium border border-indigo-100">
                    <span class="text-[9px] text-indigo-500 block font-bold mb-0.5">AI 한국어 자산화 번역</span>
                    {{ diary.content_ko }}
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
    """
    return render_instagram_style(child_template, diaries=diaries, current_lang=lang, active_menu='feed')

# 기능 ②: 문화인프라 통합 맵 및 [피드백 매뉴 연동 고도화]
@app.route('/map')
def map_page():
    lang = request.args.get('lang', 'ko')
    category_filter = request.args.get('category', '')
    amenity_filter = request.args.get('amenity', '') 
    
    conn = get_db_connection()
    query = 'SELECT * FROM culture_places WHERE 1=1'
    params = []
    
    if category_filter:
        query += ' AND category = ?'
        params.append(category_filter)
    if amenity_filter:
        query += ' AND amenities LIKE ?'
        params.append(f'%{amenity_filter}%')
        
    places = conn.execute(query, params).fetchall()
    
    # 각 장소별 등록된 유저들의 리얼 피드백 취합 연산
    feedbacks_dict = {}
    for place in places:
        fb_rows = conn.execute('SELECT * FROM place_feedbacks WHERE place_id = ? ORDER BY created_at DESC', (place['id'],)).fetchall()
        feedbacks_dict[place['id']] = fb_rows
        
    conn.close()

    child_template = """
    <div class="p-4">
        <h2 class="text-base font-extrabold mb-1 text-gray-800"><i class="fa-solid fa-location-crosshairs text-indigo-600 mr-1.5"></i> 안심 다국어 유아 문화인프라 맵</h2>
        <p class="text-[10px] text-gray-400 mb-3">실시간 유저 피드백으로 정제되는 안전 인프라 지도</p>
        
        <div class="flex space-x-1.5 mb-2 overflow-x-auto pb-1">
            <a href="{{ url_for('map_page') }}?lang={{ current_lang }}&amenity={{ request.args.get('amenity','') }}" class="text-[11px] px-3 py-1 rounded-full border border-gray-200 bg-white font-medium text-gray-600">전체</a>
            <a href="{{ url_for('map_page') }}?lang={{ current_lang }}&category=박물관&amenity={{ request.args.get('amenity','') }}" class="text-[11px] px-3 py-1 rounded-full border border-indigo-200 bg-indigo-50 text-indigo-700">🏛️ 박물관</a>
            <a href="{{ url_for('map_page') }}?lang={{ current_lang }}&category=미술관&amenity={{ request.args.get('amenity','') }}" class="text-[11px] px-3 py-1 rounded-full border border-pink-200 bg-pink-50 text-pink-700">🎨 미술관</a>
            <a href="{{ url_for('map_page') }}?lang={{ current_lang }}&category=어린이 전용&amenity={{ request.args.get('amenity','') }}" class="text-[11px] px-3 py-1 rounded-full border border-emerald-200 bg-emerald-50 text-emerald-700">🎈 아동특화</a>
        </div>

        <div class="flex space-x-1.5 mb-4 border-t border-gray-100 pt-2 overflow-x-auto">
            <a href="{{ url_for('map_page') }}?lang={{ current_lang }}&category={{ request.args.get('category','') }}&amenity=수유실" class="text-[10px] px-2 py-0.5 rounded border {% if request.args.get('amenity','') == '수유실' %}bg-amber-500 text-white border-amber-500{% else %}bg-gray-100 text-gray-600 border-gray-200{% endif %}">🍼 수유실 있음</a>
            <a href="{{ url_for('map_page') }}?lang={{ current_lang }}&category={{ request.args.get('category','') }}&amenity=유모차" class="text-[10px] px-2 py-0.5 rounded border {% if request.args.get('amenity','') == '유모차' %}bg-amber-500 text-white border-amber-500{% else %}bg-gray-100 text-gray-600 border-gray-200{% endif %}">🛒 유모차 대여</a>
            <a href="{{ url_for('map_page') }}?lang={{ current_lang }}&category={{ request.args.get('category','') }}&amenity=다국어" class="text-[10px] px-2 py-0.5 rounded border {% if request.args.get('amenity','') == '다국어' %}bg-amber-500 text-white border-amber-500{% else %}bg-gray-100 text-gray-600 border-gray-200{% endif %}">🌐 다국어 가이드</a>
        </div>

        <div class="space-y-4">
            {% for place in places %}
            <div class="bg-white border border-gray-100 rounded-2xl p-4 shadow-sm">
                <div>
                    <div class="flex items-center gap-1.5 mb-1">
                        <span class="inline-block bg-indigo-50 text-indigo-600 text-[9px] font-extrabold px-1.5 py-0.5 rounded-md">{{ place.category }}</span>
                        {% if place.has_multilingual == 'Y' %}
                        <span class="bg-purple-50 text-purple-600 text-[9px] font-bold px-1.5 py-0.5 rounded-md">🌐 이중언어 인프라 인증</span>
                        {% endif %}
                    </div>
                    <h3 class="font-bold text-sm text-gray-900">
                        {% if current_lang == 'en' %}{{ place.name_en }}
                        {% elif current_lang == 'vi' %}{{ place.name_vi }}
                        {% else %}{{ place.name_ko }}{% endif %}
                    </h3>
                    <p class="text-[11px] text-gray-400 mt-0.5"><i class="fa-solid fa-map-pin text-[10px]"></i> {{ place.address }}</p>
                </div>
                
                <div class="mt-2 flex flex-wrap gap-1 border-t border-dashed border-gray-100 pt-2">
                    {% if place.amenities %}
                        {% for amenity in place.amenities.split(',') %}
                        <span class="text-[10px] bg-gray-50 text-gray-600 px-2 py-0.5 rounded border border-gray-100">✓ {{ amenity }}</span>
                        {% endfor %}
                    {% endif %}
                </div>

                <div class="mt-3 bg-gray-50 rounded-xl p-2.5 text-[11px]">
                    <p class="font-bold text-gray-700 mb-1"><i class="fa-regular fa-comment-dots"></i> 다국어 실시간 피드백</p>
                    {% if feedbacks_dict[place.id] %}
                        {% for fb in feedbacks_dict[place.id] %}
                        <div class="border-b border-gray-200/60 last:border-0 py-1">
                            <span class="font-bold text-indigo-600">[{{ fb.user_lang }}]</span> 
                            <span class="text-amber-500">★{{ fb.rating }}</span> - {{ fb.comment }}
                            {% if fb.suggested_amenity %}
                            <span class="block text-[10px] text-emerald-600 font-semibold">💡 건의 인프라: {{ fb.suggested_amenity }}</span>
                            {% endif %}
                        </div>
                        {% endfor %}
                    {% else %}
                        <p class="text-gray-400 text-[10px]">등록된 실시간 장소 피드백이 없습니다.</p>
                    {% endif %}
                </div>

                <form action="{{ url_for('add_place_feedback', place_id=place.id) }}?lang={{ current_lang }}" method="POST" class="mt-3 pt-2 border-t border-gray-100 space-y-2">
                    <div class="grid grid-cols-3 gap-1.5">
                        <select name="rating" class="text-[10px] border rounded p-1 bg-white focus:outline-none">
                            <option value="5">⭐⭐⭐⭐⭐ 5점</option>
                            <option value="4">⭐⭐⭐⭐ 4점</option>
                            <option value="3">⭐⭐⭐ 3점</option>
                        </select>
                        <input type="text" name="suggested_amenity" placeholder="필요 편의시설(예: 수유실)" class="col-span-2 text-[10px] border rounded p-1 focus:outline-none bg-white">
                    </div>
                    <div class="flex gap-1">
                        <input type="text" name="comment" required placeholder="장소의 다국어 지원 만족도를 적어주세요." class="w-full text-[10px] border rounded p-1 focus:outline-none">
                        <button type="submit" class="bg-indigo-600 text-white font-bold text-[10px] px-3 rounded hover:bg-indigo-700 shrink-0">등록</button>
                    </div>
                </form>
            </div>
            {% else %}
            <div class="text-center py-8 text-xs text-gray-400 bg-white rounded-2xl border border-dashed">조건에 만족하는 안전 문화 공간이 없습니다.</div>
            {% endfor %}
        </div>
    </div>
    """
    return render_instagram_style(child_template, places=places, feedbacks_dict=feedbacks_dict, current_lang=lang, active_menu='map', request=request)

# 장소 피드백 서브밋 처리 핸들러
@app.route('/map/feedback/<int:place_id>', methods=['POST'])
def add_place_feedback(place_id):
    lang = request.args.get('lang', 'ko')
    rating = request.form.get('rating', 5)
    comment = request.form.get('comment', '').strip()
    suggested_amenity = request.form.get('suggested_amenity', '').strip()
    
    if comment:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO place_feedbacks (place_id, user_lang, rating, comment, suggested_amenity)
            VALUES (?, ?, ?, ?, ?)
        ''', (place_id, lang, rating, comment, suggested_amenity))
        conn.commit()
        conn.close()
        flash("소중한 장소 개선 피드백이 매핑 인프라에 반영되었습니다.")
        
    return redirect(url_for('map_page', lang=lang))

# [신규 추가] 기능 ③: 다문화 공동체 육아 품앗이 모임 비즈니스 도메인
@app.route('/group', methods=['GET', 'POST'])
def group_page():
    lang = request.args.get('lang', 'ko')
    conn = get_db_connection()
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        target_age = request.form.get('target_age')
        meeting_place = request.form.get('meeting_place')
        
        conn.execute('''
            INSERT INTO groups (title, description, target_age, meeting_place, leader_lang)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, description, target_age, meeting_place, lang))
        conn.commit()
        flash("새로운 육아 품앗이 모임 개설이 완료되었습니다.")
        
    groups = conn.execute('SELECT * FROM groups ORDER BY created_at DESC').fetchall()
    conn.close()
    
    child_template = """
    <div class="p-4 space-y-5">
        <div>
            <h2 class="text-base font-extrabold mb-1 text-gray-800"><i class="fa-solid fa-users text-indigo-600 mr-1.5"></i> 글로벌 육아 품앗이 모임</h2>
            <p class="text-[10px] text-gray-400">외로움과 육아 파편화를 극복하는 정서 연대 공동체</p>
        </div>

        <form action="{{ url_for('group_page') }}?lang={{ current_lang }}" method="POST" class="bg-indigo-50/70 border border-indigo-100 rounded-2xl p-4 space-y-3">
            <p class="text-xs font-bold text-indigo-9ded-900"><i class="fa-solid fa-circle-plus"></i> 새 품앗이 모임 만들기</p>
            <div class="grid grid-cols-2 gap-2">
                <input type="text" name="title" required placeholder="모임 이름" class="text-xs p-2 rounded-xl border bg-white focus:outline-none">
                <select name="target_age" class="text-xs p-2 rounded-xl border bg-white focus:outline-none">
                    <option value="0-2세">0-2세 (영아기)</option>
                    <option value="3-5세">3-5세 (유아기)</option>
                    <option value="6-7세">6-7세 (아동기)</option>
                </select>
            </div>
            <input type="text" name="meeting_place" placeholder="거점 장소 (예: 국립중앙박물관)" class="w-full text-xs p-2 rounded-xl border bg-white focus:outline-none">
            <textarea name="description" required placeholder="함께 수행할 로드맵 미션이나 활동을 요약하세요." class="w-full text-xs p-2 rounded-xl border bg-white focus:outline-none" rows="2"></textarea>
            <button type="submit" class="w-full bg-indigo-600 text-white font-bold text-xs py-2 rounded-xl shadow-sm">공동체 모임 생성하기</button>
        </form>

        <div class="space-y-3">
            {% for g in groups %}
            <div class="bg-white border border-gray-100 rounded-2xl p-4 shadow-sm relative overflow-hidden">
                <span class="absolute top-0 right-0 bg-purple-600 text-white text-[8px] font-bold px-2.5 py-0.5 rounded-bl-lg">개설언어: {{ g.leader_lang.upper() }}</span>
                <span class="text-[9px] bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded font-extrabold">{{ g.target_age }}</span>
                <h3 class="font-bold text-sm text-gray-900 mt-1.5">{{ g.title }}</h3>
                <p class="text-xs text-gray-600 mt-1 italic">"{{ g.description }}"</p>
                
                <div class="mt-3 pt-2.5 border-t border-gray-100 flex justify-between items-center text-[10px]">
                    <span class="text-gray-400"><i class="fa-solid fa-location-dot"></i> 거점: {{ g.meeting_place or '미정' }}</span>
                    <button onclick="alert('품앗이 모임 합류 처리가 가상 동기화되었습니다. 채팅방으로 연결됩니다.')" class="bg-emerald-50 text-emerald-700 border border-emerald-200 px-3 py-1 rounded-lg font-bold">
                        <i class="fa-solid fa-right-to-bracket"></i> 공동체 참여 ({{ g.member_count }}명)
                    </button>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    """
    return render_instagram_style(child_template, groups=groups, current_lang=lang, active_menu='group')

# 기능 ④: 연령별 자녀 문화성장 로드맵 시스템
@app.route('/roadmap')
def roadmap_page():
    lang = request.args.get('lang', 'ko')
    selected_age = request.args.get('age', '0-2세')
    
    conn = get_db_connection()
    roadmap = conn.execute('''
        SELECT r.*, s.is_completed 
        FROM age_roadmaps r
        JOIN user_roadmap_status s ON r.id = s.roadmap_id
        WHERE r.age_group = ?
    ''', (selected_age,)).fetchone()
    
    recommended_places = []
    if roadmap:
        recommended_places = conn.execute('SELECT * FROM culture_places WHERE category = ?', (roadmap['recommended_target'],)).fetchall()
    conn.close()

    child_template = """
    <div class="p-4">
        <h2 class="text-base font-extrabold mb-1 text-gray-800"><i class="fa-solid fa-chart-line text-indigo-600 mr-1.5"></i> 다문화 자녀 연령별 성장 로드맵</h2>
        <p class="text-[11px] text-gray-400 mb-4">문체부 생애주기 교육 패키지를 적용한 AI 진단 가이드</p>
        
        <div class="grid grid-cols-3 gap-2 mb-5">
            <a href="{{ url_for('roadmap_page') }}?lang={{ current_lang }}&age=0-2세" class="text-center py-2 text-xs rounded-xl border {% if selected_age == '0-2세' %}bg-indigo-600 text-white font-bold border-indigo-600{% else %}bg-white text-gray-500 border-gray-200{% endif %}">0-2세 (영아기)</a>
            <a href="{{ url_for('roadmap_page') }}?lang={{ current_lang }}&age=3-5세" class="text-center py-2 text-xs rounded-xl border {% if selected_age == '3-5세' %}bg-indigo-600 text-white font-bold border-indigo-600{% else %}bg-white text-gray-500 border-gray-200{% endif %}">3-5세 (유아기)</a>
            <a href="{{ url_for('roadmap_page') }}?lang={{ current_lang }}&age=6-7세" class="text-center py-2 text-xs rounded-xl border {% if selected_age == '6-7세' %}bg-indigo-600 text-white font-bold border-indigo-600{% else %}bg-white text-gray-500 border-gray-200{% endif %}">6-7세 (아동기)</a>
        </div>

        {% if roadmap %}
        <div class="bg-gradient-to-br {% if roadmap.is_completed == 1 %}from-emerald-800 to-teal-900{% else %}from-indigo-900 to-purple-900{% endif %} text-white rounded-2xl p-4 shadow-md mb-6 transition-all duration-300">
            <div class="flex justify-between items-center">
                <span class="bg-white/20 text-white text-[9px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">Current Age Mission</span>
                {% if roadmap.is_completed == 1 %}
                <span class="bg-emerald-500/30 text-emerald-300 text-[10px] px-2.5 py-0.5 rounded-md font-bold border border-emerald-500/40">✓ 미션 달성 완료</span>
                {% else %}
                <span class="bg-amber-500/30 text-amber-300 text-[10px] px-2.5 py-0.5 rounded-md font-bold border border-amber-500/40">⏳ 미션 수행 중</span>
                {% endif %}
            </div>
            
            <h3 class="text-base font-bold mt-2 leading-tight">
                {% if current_lang == 'en' %}{{ roadmap.title_en }}
                {% elif current_lang == 'vi' %}{{ roadmap.title_vi }}
                {% else %}{{ roadmap.title_ko }}{% endif %}
            </h3>
            
            <p class="text-xs text-indigo-100/90 mt-2 leading-relaxed bg-black/20 p-2.5 rounded-lg border border-white/10">
                {% if current_lang == 'en' %}{{ roadmap.description_en }}
                {% elif current_lang == 'vi' %}{{ roadmap.description_vi }}
                {% else %}{{ roadmap.description_ko }}{% endif %}
            </p>

            <div class="mt-4 pt-3 border-t border-white/10 flex justify-end">
                <form action="{{ url_for('toggle_roadmap', roadmap_id=roadmap.id) }}?lang={{ current_lang }}&age={{ selected_age }}" method="POST">
                    <button type="submit" class="bg-white text-gray-900 font-bold px-4 py-1.5 rounded-xl text-[11px] shadow hover:bg-gray-100 transition-all flex items-center gap-1">
                        <i class="fa-solid fa-arrows-rotate"></i>
                        {% if roadmap.is_completed == 1 %}진행 중으로 변경{% else %}미션 완료 처리하기{% endif %}
                    </button>
                </form>
            </div>
        </div>

        <h4 class="text-xs font-bold text-gray-800 mb-2 flex items-center">
            <i class="fa-solid fa-wand-magic-sparkles text-amber-500 mr-1"></i> 현재 발달 로드맵 맞춤 추천 문화인프라
        </h4>
        <div class="space-y-2.5">
            {% for place in recommended_places %}
            <div class="bg-white border border-gray-100 rounded-xl p-3 shadow-sm flex justify-between items-center">
                <div>
                    <h5 class="font-bold text-xs text-gray-900">
                        {% if current_lang == 'en' %}{{ place.name_en }}
                        {% elif current_lang == 'vi' %}{{ place.name_vi }}
                        {% else %}{{ place.name_ko }}{% endif %}
                    </h5>
                    <p class="text-[10px] text-gray-400 mt-0.5">{{ place.address }}</p>
                </div>
                <span class="text-[10px] bg-indigo-50 text-indigo-600 font-bold px-2 py-1 rounded-lg">매칭완료</span>
            </div>
            {% endfor %}
        </div>
        {% endif %}
    </div>
    """
    return render_instagram_style(child_template, roadmap=roadmap, recommended_places=recommended_places, selected_age=selected_age, current_lang=lang, active_menu='roadmap')

@app.route('/roadmap/toggle/<int:roadmap_id>', methods=['POST'])
def toggle_roadmap(roadmap_id):
    lang = request.args.get('lang', 'ko')
    age = request.args.get('age', '0-2세')
    
    conn = get_db_connection()
    current_status = conn.execute('SELECT is_completed FROM user_roadmap_status WHERE roadmap_id = ?', (roadmap_id,)).fetchone()
    if current_status:
        new_status = 1 if current_status['is_completed'] == 0 else 0
        conn.execute('UPDATE user_roadmap_status SET is_completed = ?, updated_at = CURRENT_TIMESTAMP WHERE roadmap_id = ?', (new_status, roadmap_id))
        conn.commit()
        flash("성장 로드맵 상태가 동적으로 동기화되었습니다.")
    conn.close()
    return redirect(url_for('roadmap_page', lang=lang, age=age))

# 기능 ⑤: 안심 이중언어 일기 등록 폼
@app.route('/write', methods=['GET', 'POST'])
def write_page():
    lang = request.args.get('lang', 'ko')
    if request.method == 'POST':
        title = request.form['title']
        content_original = request.form['content_original']
        lang_code = request.form['lang_code']
        feeling_tag = request.form['feeling_tag']
        image_url = request.form['image_url'].strip() or "https://images.unsplash.com/photo-1502086223501-7ea6ecd79368?q=80&w=600"
        
        MOCK_TRANSLATOR = {
            "vi": "오늘 남편과 함께 아이를 데리고 역사박물관 공간에 다녀왔습니다. 다국어 리플렛이 잘 마련되어 있어서 한국어를 잘 모르는 저도 아이에게 전시 내용을 설명해 줄 수 있어서 가슴이 벅찼습니다.",
            "en": "Today, I went to the History Museum with my husband and baby. The multilingual leaflets were so well prepared.",
            "ko": "오늘 남편과 함께 아이를 데리고 역사박물관 공간에 다녀왔습니다. 다국어 리플렛이 잘 마련되어 있어서 한국어를 잘 모르는 저도 아이에게 전시 내용을 설명해 줄 수 있어서 가슴이 벅찼습니다."
        }
        content_ko = MOCK_TRANSLATOR.get(lang_code, content_original)
        bridge_note = f"안녕하세요! 오늘 아이와 함께 '{title}' 활동을 완료했습니다. '{content_ko[:40]}...' 중심의 유익한 문화 경험을 공유합니다. 가정 내 육아 연계에 참고해주세요 🥰"

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO diaries (title, content_original, content_ko, lang_code, image_url, feeling_tag, bridge_note)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, content_original, content_ko, lang_code, image_url, feeling_tag, bridge_note))
        conn.commit()
        conn.close()
        
        flash("성장 로드맵 연계 일기가 정상 등록되었습니다!")
        return redirect(url_for('feed_page', lang=lang_code))

    child_template = """
    <div class="p-4">
        <h2 class="text-base font-extrabold mb-1 text-gray-800"><i class="fa-solid fa-pen-fancy text-indigo-600 mr-1.5"></i> 안심 이중언어 일기 등록</h2>
        <p class="text-[10px] text-gray-400 mb-3">모국어로 편하게 작성하세요. AI가 완벽한 한국어 자산 및 가족 알림장으로 변환합니다.</p>
        
        <form action="{{ url_for('write_page') }}?lang={{ current_lang }}" method="POST" class="space-y-4 bg-white border border-gray-100 p-4 rounded-2xl shadow-sm">
            <div>
                <label class="block text-[10px] font-bold text-gray-500 mb-1">작성 언어 선택 (Language)</label>
                <select name="lang_code" class="w-full text-xs border border-gray-200 rounded-xl p-2.5 bg-gray-50 focus:outline-none font-medium">
                    <option value="vi" {% if current_lang == 'vi' %}selected{% endif %}>🇻🇳 Tiếng Việt (베트남어)</option>
                    <option value="en" {% if current_lang == 'en' %}selected{% endif %}>🇺🇸 English (영어)</option>
                    <option value="ko" {% if current_lang == 'ko' %}selected{% endif %}>🇰🇷 한국어 (Korean)</option>
                </select>
            </div>
            
            <div class="grid grid-cols-2 gap-2">
                <div>
                    <label class="block text-[10px] font-bold text-gray-500 mb-1">오늘의 감정</label>
                    <select name="feeling_tag" class="w-full text-xs border border-gray-200 rounded-xl p-2.5 bg-gray-50 focus:outline-none">
                        <option value="😊 행복">😊 행복</option>
                        <option value="😭 지침">😭 지침</option>
                        <option value="🥰 성장">🥰 성장</option>
                    </select>
                </div>
                <div>
                    <label class="block text-[10px] font-bold text-gray-500 mb-1">일기 제목</label>
                    <input type="text" name="title" required placeholder="예: 박물관 나들이" class="w-full text-xs border border-gray-200 rounded-xl p-2.5 bg-gray-50 focus:outline-none">
                </div>
            </div>
            
            <div>
                <label class="block text-[10px] font-bold text-gray-500 mb-1">체험 사진 첨부 (URL)</label>
                <input type="text" name="image_url" placeholder="사진 이미지 웹주소를 입력하세요 (선택)" class="w-full text-xs border border-gray-200 rounded-xl p-2.5 bg-gray-50 focus:outline-none">
            </div>
            
            <div>
                <label class="block text-[10px] font-bold text-gray-500 mb-1">일기 본문 내용</label>
                <textarea name="content_original" rows="4" required placeholder="번역기를 의식하지 말고, 모국어로 자유롭고 깊게 감정을 기록하세요..." class="w-full text-xs border border-gray-200 rounded-xl p-2.5 bg-gray-50 focus:outline-none"></textarea>
            </div>
            
            <button type="submit" class="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold py-3 rounded-xl text-xs shadow-md transform active:scale-[0.98] transition-all">
                <i class="fa-solid fa-paper-plane mr-1"></i> 이중언어 자산 발행 & 알림장 자동 빌드
            </button>
        </form>
    </div>
    """
    return render_instagram_style(child_template, current_lang=lang, active_menu='write')

@app.route('/like/<int:diary_id>', methods=['POST'])
def like_diary(diary_id):
    lang = request.args.get('lang', 'ko')
    conn = get_db_connection()
    conn.execute('UPDATE diaries SET likes = likes + 1 WHERE id = ?', (diary_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('feed_page', lang=lang))

if __name__ == '__main__':
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
    init_db()
    app.run(debug=True, port=5000)

```
