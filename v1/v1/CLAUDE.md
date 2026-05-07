# PosturePro — CLAUDE.md

## 실제 파일 구조 (현재 상태)

```
v1/v1/                              ← manage.py 위치 (작업 루트)
│
├── manage.py
│
├── [주의] 루트에 잘못 위치한 파일들  ← 원래 v1/ 안에 있어야 함
│   ├── settings.py                 ← v1/settings.py보다 최신 (frame_split 추가됨)
│   ├── urls.py                     ← 프로젝트 루트 URL conf
│   ├── wsgi.py
│   ├── asgi.py
│   └── __init__.py
│
├── squat_tool.py                   ← 개발 초기 테스트용 독립 스크립트 (Django 앱 아님, 하드코딩 경로 있음)
│
├── v1/                             ← Django 프로젝트 설정 패키지 (manage.py가 참조)
│   ├── settings.py                 ← 실제 사용되는 설정 파일 (루트 것보다 구버전)
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── v3/                             ← 메인 앱 (유일한 앱)
│   ├── views.py                    ← 모든 뷰 + 분석 로직 (약 1300줄)
│   ├── models.py
│   ├── urls.py
│   ├── forms.py
│   ├── admin.py
│   └── migrations/                 ← 0001 ~ 0031
│
├── templates/v2/                   ← HTML 템플릿
│   ├── main.html                   ← 대시보드 (ApexCharts 바 차트)
│   ├── result.html                 ← 결과 화면 (도넛 차트 + 피드백)
│   ├── events.html                 ← 분석 대기 로딩 화면 (6초 후 /result 리다이렉트)
│   ├── login.html
│   ├── register.html
│   ├── lunge.html / flank.html / squat.html / pullup.html
│   └── video_list.html 외 샘플 페이지들
│
├── media/                          ← 업로드된 영상 저장 (lunge_test.mp4, pullup_test.mp4)
├── frame_split/                    ← 영상에서 추출된 프레임 이미지 (무시 가능)
├── frame_point/                    ← 관절 좌표 CSV 파일 (무시 가능)
│
├── pose_deploy.prototxt            ← Body25 모델 설정
├── pose_deploy_linevec_faster_4_stages.prototxt  ← MPII 모델 설정
├── pose_iter_584000.caffemodel     ← Body25 가중치
├── pose_iter_160000.caffemodel     ← MPII 가중치
│
├── db.sqlite3
├── progress.json                   ← 분석 진행률 (0~100)
└── requirements.txt
```

## 가상환경 및 서버 실행

```powershell
# 가상환경 활성화 (ppenv 폴더 기준)
.\ppenv\Scripts\activate

# 서버 실행 (v1/v1/ 에서)
python manage.py runserver
```

## settings.py 주의사항

- Django가 실제로 읽는 파일 : `v1/settings.py` (manage.py의 DJANGO_SETTINGS_MODULE = 'v1.settings')
- 루트의 `settings.py`는 최신 수정본이나 **v1/ 안에 있어야 적용됨**
- 두 파일의 차이점: 루트 버전에 `STATICFILES_DIRS`에 `frame_split` 경로 추가됨

## URL 구조 (앱 네임스페이스: v3)

| URL | 뷰 | 설명 |
|-----|----|------|
| `/` | login | 로그인 (기본) |
| `/register` | register | 회원가입 |
| `/check_username/` | check_username | 아이디 중복 확인 (Ajax GET) |
| `/main` | main | 대시보드 |
| `/lunge` `/flank` `/squat` `/pullup` | 각 뷰 | 업로드 페이지 |
| `/lunge_video` `/pullup_video` `/flank_video` `/squat_video` | *_video | 영상 업로드 + 분석 실행 |
| `/events` | events | 분석 중 로딩 화면 |
| `/result` | result | 결과 화면 |

## 주요 모델 (models.py)

- `UserModel` — username(PK), password(평문), password2, rank_value, rank_time
- `RankHistory` — user(FK→UserModel), rank_value(0~100 정수), posture(종목명), timestamp
- `Video` — title, document(파일경로), upload_date
- `UserRank` — 레거시, 현재 거의 미사용
- `RankScore` — 레거시, 현재 거의 미사용

## 세션 키

- `request.session['username']` — 로그인한 사용자명
- `request.session['style']` — 현재 분석 종목 ('lunge' / 'pullup' / 'squat' / 'flank')

## 분석 흐름 (views.py)

1. `*_video()` — 영상 저장 → `*_tool()` 동기 호출 → events.html 렌더
2. `video_div()` — OpenCV로 0.5초마다 프레임 추출 → `frame_split/` 저장
3. `*_tool()` — OpenPose로 관절 좌표 추출 → CSV 저장 → 자세 판정 → `progress.json` 업데이트
4. `result()` — CSV 읽기 → 점수 계산 → RankHistory 저장 → 피드백 텍스트 → 렌더

## OpenPose 모델 사용 구분

- **Body25** (`pose_iter_584000.caffemodel`) — lunge, flank (25포인트)
- **MPII** (`pose_iter_160000.caffemodel`) — squat, pullup (15포인트)

## 자세 판정 기준

| 종목 | 기준 |
|------|------|
| lunge | 앞다리 무릎각 80~100° (좌우 자동 판별) |
| pullup | 팔꿈치각 35~55° AND 손목너비 = 어깨너비 × 1.5~2.3 |
| squat | 양 무릎각 50~90° |
| flank | 어깨-무릎-엉덩이 각도 160~180° AND y좌표 순서 (어깨 ≤ 엉덩이 ≤ 무릎) |

## 알려진 버그 (수정 예정)

- `squat_video()` 에서 `session['style'] = 'flank'` 로 잘못 저장됨 → `'squat'` 이어야 함 (views.py:354)
- `result()` 에서 pullup/squat/flank 분기에 `csv_text` 미할당 → 렌더 시 오류 가능 (views.py:286)
- `squat_get_y_value()` 에 NaN/None 체크 없음 → 런타임 에러 가능 (views.py:970)
- 비밀번호 평문 저장 및 비교 (views.py:71)
- `result()` 에 로그인 체크 없음 → 비로그인 접근 시 500 에러 (views.py:151)
- `RankHistory` 중복 저장 — result 페이지 새로고침 시 기록 중복
