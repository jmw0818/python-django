# PosturePro — 운동 자세 교정 웹 애플리케이션

## 프로젝트 개요

운동 영상을 업로드하면 AI가 관절 좌표를 분석하여 자세의 정확도를 점수화하고, 잘못된 자세에 대한 피드백을 제공하는 웹 애플리케이션입니다. 졸업작품으로 제작되었으며, 사용자가 혼자서도 운동 자세를 점검하고 개선할 수 있도록 돕는 것을 목표로 합니다.

---

## 기술 스택

| 분류 | 기술 |
|------|------|
| Backend | Python 3.x, Django 5.0 |
| Frontend | Bootstrap 5, ApexCharts, AOS (Animate On Scroll) |
| Computer Vision | OpenCV (cv2), OpenPose (Caffe 모델) |
| Database | SQLite3 |
| Data Processing | Pandas |
| Template Engine | Django Template Language |

---

## 시스템 아키텍처

```
[사용자]
   │
   ▼ 영상 업로드 (POST)
[Django View]
   │
   ├─ video_div()         영상 → 0.5초 간격 프레임 추출 (OpenCV)
   │
   ├─ *_tool()            프레임 → OpenPose 관절 좌표 추출 → CSV 저장
   │                      → 관절 각도 계산 → 자세 판정 → progress.json 업데이트
   │
   └─ result()            점수 계산 → DB 저장 → 피드백 텍스트 → 결과 화면
```

---

## 주요 기능

### 1. 회원 기능
- 회원가입 / 로그인 / 로그아웃
- 아이디 중복 확인 (Ajax 비동기 처리)
- 세션 기반 로그인 상태 유지

### 2. 운동 자세 분석 (4종목)

| 종목 | 사용 모델 | 핵심 측정 지표 | 정상 범위 |
|------|-----------|---------------|-----------|
| 런지 (Lunge) | OpenPose Body25 | 앞다리 무릎 굴곡각 | 80° ~ 100° |
| 풀업 (Pull Up) | OpenPose MPII | 팔꿈치 굴곡각 + 손목 너비 비율 | 35° ~ 55°, 어깨 너비의 1.5~2.3배 |
| 스쿼트 (Squat) | OpenPose MPII | 양쪽 무릎 굴곡각 | 50° ~ 90° |
| 플랭크 (Flank) | OpenPose Body25 | 어깨-엉덩이-무릎 직선 정렬각 | 160° ~ 180° |

### 3. 자세 점수화 및 기록
- 분석된 프레임 중 '올바른 자세' 비율을 0~100점으로 환산
- 종목별, 날짜별 운동 기록을 DB에 누적 저장
- 메인 대시보드에서 ApexCharts 바 차트로 운동 기록 시각화

### 4. 피드백 제공 (Lunge 기준)
- 잘못된 자세 감지 시 구체적인 교정 메시지 제공
  - 무릎이 덜 굽혀진 경우 / 과도하게 굽혀진 경우 구분
  - 왼쪽/오른쪽 다리를 각각 독립적으로 판별

### 5. 분석 대기 화면
- 영상 분석 중 로딩 스피너 표시
- `progress.json`을 통한 진행률 상태 관리
- 분석 완료 후 결과 페이지로 자동 이동

---

## 핵심 알고리즘

### 관절 각도 계산

세 관절 포인트 A, B, C가 주어졌을 때, 벡터의 내적을 이용해 각도를 계산합니다.

```
벡터 AB = B - A
벡터 BC = C - B

cos(θ) = (AB · BC) / (|AB| × |BC|)
각도 = arccos(cos(θ))
```

종목별로 계산 방식을 달리 적용합니다.
- **Lunge / Flank** : 코사인 법칙 기반 (정확한 내각 계산)
- **Squat / Pull Up** : `atan` 기반 (상대 기울기 각도 측정)

### 앞다리 판별 (Lunge)

엉덩이 관절의 y좌표를 비교하여 어느 쪽 다리가 앞에 나왔는지 자동 판별합니다.

```python
if Lhip_point[1] < Rhip_point[1]:
    return "left"   # 왼쪽 다리가 앞
else:
    return "right"  # 오른쪽 다리가 앞
```

### 핵심 프레임 추출

영상 전체가 아닌, 운동의 최저점/최고점에 해당하는 프레임만 선별하여 분석합니다.

- **Lunge / Squat** : MidHip 포인트의 y값이 가장 높은(가장 낮게 내려간) 상위 5~10프레임 추출
- **Pull Up** : Head 포인트의 y값이 가장 낮은(가장 높이 올라간) 하위 10프레임 추출
- **Flank** : 전 프레임 분석 (정적 자세)

---

## 데이터베이스 구조

```
UserModel (사용자)
  ├── username (PK, CharField)
  ├── password (CharField, 평문)
  ├── password2 (CharField)
  ├── rank_value (IntegerField, nullable)
  ├── rank_time (DateTimeField, auto)
  └── user_ranks → UserRank (M:N, 레거시)

RankHistory (운동 기록)
  ├── user → UserModel (FK)
  ├── rank_value (IntegerField, 0~100)
  ├── posture (CharField, 종목명)
  └── timestamp (DateTimeField)

Video (업로드 영상)
  ├── title (CharField)
  ├── document (FileField → media/videos/)
  └── upload_date (DateTimeField, auto)
```

---

## 화면 구성

| 화면 | 설명 |
|------|------|
| 로그인 | 아이디/비밀번호 입력, 오류 메시지 표시 |
| 회원가입 | 아이디 중복 확인(Ajax), 비밀번호 확인 |
| 메인 대시보드 | 운동 종목 선택 카드 4개, 운동 기록 바 차트 |
| 종목 페이지 | 각 종목 설명 및 영상 업로드 폼 |
| 분석 대기 | 로딩 스피너, 6초 후 결과 페이지 자동 이동 |
| 결과 | 업로드 영상 재생, 점수 도넛 차트, 피드백 텍스트 |

---

## 개발 과정 및 파일 구조

### 초기 개발 → 웹 통합 흐름
1. `squat_tool.py` — 독립 스크립트로 OpenPose + 각도 계산 로직 프로토타이핑
2. 검증된 로직을 Django `views.py`의 각 `*_tool()` 함수로 이식
3. 종목별로 최적 모델(Body25 / MPII)을 선택하여 적용

### 주요 파일

```
v1/v1/
├── manage.py
├── v1/                             Django 프로젝트 설정
│   ├── settings.py
│   └── urls.py
├── v3/                             메인 앱
│   ├── views.py                    뷰 및 분석 로직 전체
│   ├── models.py
│   └── urls.py
├── templates/v2/                   HTML 템플릿 (로그인/대시보드/결과 등)
├── media/                          업로드 영상 저장
├── frame_split/                    추출된 프레임 이미지 (임시)
├── frame_point/                    관절 좌표 CSV (임시)
└── pose_deploy*.prototxt           OpenPose 모델 파일
    pose_iter*.caffemodel
```

---

## 구현 중 해결한 기술적 과제

- **두 가지 OpenPose 모델 혼용** : 종목 특성에 따라 MPII(15포인트)와 Body25(25포인트) 모델을 선택적으로 적용하여 정확도 향상
- **핵심 프레임 선별** : 영상 전체 분석 대신 운동의 핵심 구간(최대 하강/상승 프레임)만 추출하여 불필요한 연산 절감
- **앞다리 자동 판별** : 런지에서 어느 다리가 앞에 나왔는지 관절 좌표 비교로 자동 감지, 별도 입력 없이 좌우 자세 분석
- **분석 진행률 전달** : `progress.json` 파일을 매개로 서버 분석 상태를 프론트엔드에 전달하는 방식 구현
- **프로토타입 → 웹 통합** : 독립 스크립트로 검증한 CV 로직을 Django 뷰로 이식하는 단계적 개발 진행
