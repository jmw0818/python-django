# PosturePro

운동 영상을 업로드하면 AI가 관절 좌표를 분석하여 자세 점수와 피드백을 제공하는 웹 애플리케이션입니다.

## 지원 운동 종목

- Lunge (런지)
- Pull Up (풀업)
- Squat (스쿼트)
- Flank (플랭크)

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
