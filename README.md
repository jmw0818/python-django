# PosturePro

> **본 저장소는 졸업 프로젝트 제출본 원본입니다.**
> 포트폴리오 목적의 리팩토링 버전은 별도 저장소에서 진행 예정입니다.

운동 영상을 업로드하면 AI가 관절 좌표를 분석하여 자세 점수와 피드백을 제공하는 웹 애플리케이션입니다.

## 구현 기능

| 기능 | 상태 |
|------|------|
| 회원가입 / 로그인 | 완료 |
| 런지 (Lunge) 자세 분석 | 완료 |
| 풀업 (Pull Up) 자세 분석 | 완료 |
| 스쿼트 (Squat) 자세 분석 | 완료 |
| 플랭크 (Flank) 자세 분석 | 완료 |
| 운동 기록 저장 및 차트 시각화 | 완료 |
| 자세 피드백 텍스트 | 런지만 구현 |

## 프로젝트 구조에 대한 참고사항

개발 과정에서 파일 이동 실수로 인해 Django 설정 파일(`settings.py`, `urls.py` 등)이 올바른 패키지 경로(`v1/`)와 루트(`v1/v1/`) 두 곳에 중복 존재하는 상태입니다. 경로 설정이 꼬여 있어 수정 시 충돌이 발생하여 졸업 제출 시점에는 그대로 유지하였습니다. 이 부분은 리팩토링 버전에서 구조를 새로 잡아 개선할 예정입니다.

## 기술 스택

- Python 3.x / Django 5.0
- OpenPose (Caffe)
- OpenCV, Pandas
- Bootstrap 5, ApexCharts

---

## 설치 및 실행 방법

### 1. 레포지토리 클론

```bash
git clone https://github.com/<your-username>/PosturePro.git
cd PosturePro
```

### 2. 가상환경 생성 및 패키지 설치

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install django pandas opencv-python django-sass-processor
```

### 3. OpenPose 모델 파일 다운로드 (필수)

모델 파일은 용량 문제로 저장소에 포함되지 않습니다. 아래 링크에서 직접 다운받아 프로젝트 루트(`manage.py`와 같은 위치)에 넣어주세요.

| 파일명 | 용도 | 다운로드 |
|--------|------|----------|
| `pose_iter_584000.caffemodel` | Lunge / Flank 분석 (Body25) | [Google Drive - CMU OpenPose](https://drive.google.com/file/d/1nB5c19yAHBFMoqU0S2xQUDk9xIECMGOW/view?usp=sharing) |
| `pose_deploy.prototxt` | Body25 모델 설정 | 이 저장소에 포함됨 |
| `pose_iter_160000.caffemodel` | Squat / Pull Up 분석 (MPII) | [Google Drive - CMU OpenPose](https://drive.google.com/file/d/1c9SXQZ3KGMgKmyq-sNsn8x7TuXHe-9xT/view?usp=sharing) |
| `pose_deploy_linevec_faster_4_stages.prototxt` | MPII 모델 설정 | 이 저장소에 포함됨 |

> 공식 출처: [CMU OpenPose GitHub](https://github.com/CMU-Perceptual-Computing-Lab/openpose)

### 4. 데이터베이스 마이그레이션

```bash
python manage.py migrate
```

### 5. 서버 실행

```bash
python manage.py runserver
```

브라우저에서 `http://127.0.0.1:8000/` 접속

---

## 폴더 구조

```
v1/v1/
├── manage.py
├── v1/                  Django 프로젝트 설정
├── v3/                  메인 앱 (뷰, 모델, URL)
├── templates/v2/        HTML 템플릿
├── static/              정적 파일
└── *.prototxt           OpenPose 모델 설정 파일
```
