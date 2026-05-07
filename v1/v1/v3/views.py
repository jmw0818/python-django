from django.shortcuts import render,HttpResponse
from .models import Video
import pandas as pd
from django.conf import settings
from django.http import JsonResponse
import csv
from .models import UserRank
from . import models
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import cv2
import math
import csv
import pandas as pd
import ast
import shutil
# Create your views here.

import os
import pandas as pd
from django.shortcuts import render
from .models import UserModel, UserRank, Video,RankHistory
import time
import json
from django.http import JsonResponse
import json
from django.shortcuts import render, redirect
from django.utils import timezone

import json  # json 모듈 임포트 추가

def main(request):
    # 세션에서 로그인한 사용자 정보 가져오기
    username = request.session.get('username')
    rank_history = RankHistory.objects.filter(user=username) if username else []
    
    # 사용자 정보 가져오기
    rank_values = [history.rank_value for history in rank_history]
    timestamps = [history.timestamp.strftime("%Y-%m-%d") for history in rank_history]  # 원하는 형식으로 변환
    postures = [history.posture for history in rank_history]  # 각 기록의 posture 추가
    # timestamps와 postures를 결합해 labels 생성
    labels = [f"{timestamp} \n {posture}" for timestamp, posture in zip(timestamps, postures)]  # '시간 (자세)' 형식으로 변환

    chart_data = {
        'rank_values': rank_values,
        'labels': labels,
    }

    context = {
        'rank_history': rank_history,
        'username': username,
        'chart_data': json.dumps(chart_data),  # JSON으로 변환하여 템플릿에 전달
    }

    return render(request, 'v2/main.html', context)


def login(request):
    # POST 요청이 들어오면 로그인 처리 해줌
    if request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        
        try:
            # 사용자가 존재하는지 확인
            me = UserModel.objects.get(username=username)
            
            # 비밀번호가 일치하는지 확인
            if me.password == password:
                # 로그인 성공 시 세션에 사용자 이름 저장
                request.session['username'] = me.username
                return redirect('v3:main')  # 로그인 성공 후 main 뷰로 리디렉션
            else:
                # 비밀번호 불일치 시 에러 메시지
                return render(request, 'v2/login.html', {'error': '비밀번호가 틀렸습니다.'})
        except UserModel.DoesNotExist:
            # 사용자명이 없을 때 에러 메시지
            return render(request, 'v2/login.html', {'error': '계정이 존재하지 않습니다.'})
    
    # GET 요청이 들어오면 login form을 담고있는 html을 열어줌
    elif request.method == 'GET':
        return render(request, 'v2/login.html')


def password(request):
    return render(request, 'v2/password.html')

def register(request):
    if request.method == "POST":
        username = request.POST.get('username',None)
        password = request.POST.get('password',None)
        password2 = request.POST.get('password2',None)
        if password != password2:
            return render(request, ' v2/register.html')
        else:
            new_user = UserModel()
            new_user.username = username
            new_user.password = password
            new_user.save()
        return render(request, 'v2/login.html')
    elif request.method =='GET':
        return render(request, 'v2/register.html')
def check_username(request):
    if request.method == "GET":
        username = request.GET.get('username', None)
        exists = UserModel.objects.filter(username=username).exists()
        return JsonResponse({'exists': exists})


def lunge(request):
    return render(request, 'v2/lunge.html')
def flank(request):
    return render(request, 'v2/flank.html')
def squat(request):
    return render(request, 'v2/squat.html')
def pullup(request):
    return render(request, 'v2/pullup.html')
def events(request):
    return render(request, 'v2/events.html')
def video_list(request):
    return render(request, 'v2/video_list.html')

def import_csv_to_model(csv_file_path):
    try:
        # CSV 파일을 DataFrame으로 읽기
        df = pd.read_csv(csv_file_path, encoding='euc-kr')
        
        # 'rank' 컬럼에서 '올바른 자세'인 행의 개수 구하기
        count_correct_postures = len(df[df['Posture'] == '올바른 자세'])
        count_incorrect_postures = len(df[df['Posture'] == '올바르지 못한 자세'])
        
        # rank_value 계산
        rank_value = count_correct_postures / (count_correct_postures + count_incorrect_postures) * 100
        
        # rank_value를 문자열로 변환하여 모델에 저장
        UserRank.objects.create(rank=str(rank_value))
        
        return rank_value
    except Exception as e:
        # 예외 처리
        print(f"Error in import_csv_to_model: {e}")
        return None

def result(request):
    username = request.session.get('username')
    style = request.session.get('style', 'default_style')  # 세션에서 'style' 값을 가져옴, 기본값은 'default_style'

    # 사용자 정보 가져오기
    user = UserModel.objects.get(username=username)

    # 사용자 기록이나 추가 정보를 전달할 수도 있음
    context = {
        'user': user,
        'username': username,
        # username을 템플릿으로 전달
    }
    
    # CSV 파일 경로 설정
    if style == 'lunge':
        csv_file_path = os.path.join("frame_point/lunge/lunge_co/all_points.csv")
        if os.path.exists(csv_file_path):
            try:
                # CSV 파일을 모델에 import하고 rank_value를 받음
                rank_value = import_csv_to_model(csv_file_path)
            
                # RankHistory 모델에 rank_value 저장
                RankHistory.objects.create(user=user, rank_value=rank_value, posture=style)  # posture 변수 저장
            
                # CSV 파일을 DataFrame으로 읽기
                df = pd.read_csv(csv_file_path, encoding='euc-kr')
            
                # '올바른 자세'인 행의 posture 컬럼 값 리스트로 가져오기
                correct_postures = df[df['Posture'] == '올바른 자세']['Posture'].tolist()
            
                # '올바르지 않은 자세'인 행의 첫 번째 프레임 가져오기
                incorrect_postures = df[df['Posture'] == '올바르지 못한 자세'].iloc[0]
            
                # 'front' 열 데이터 가져오기
                front = incorrect_postures['front']
                if front == 'right':
                    knee_angle_right_values = incorrect_postures['knee_angle_right']
                    if knee_angle_right_values - 80 > 0:
                        csv_text = '오른쪽 무릎의 각도가 충분하지 않습니다. 허벅지와 종아리 근육을 사용해 조금 더 깊게 굽혀 안정된 자세를 유지해 주세요.'
                    else:
                        csv_text = '전체적으로 오른쪽 무릎이 과도하게 굽혀졌습니다.\n 무릎 관절에 무리가 갈 수 있으니, 다리를 약간 덜 굽혀 체중을 고르게 분산해 주세요.'
                elif front == 'left':
                    knee_angle_left_values = incorrect_postures['knee_angle_left']
                    if knee_angle_left_values - 80 > 0:
                        csv_text = '왼쪽 무릎의 각도가 충분하지 않습니다. 무릎과 허벅지를 더 많이 사용하여 균형을 잡고, 적절한 깊이로 내려가 주세요.'
                    else:
                        csv_text = '왼쪽 무릎이 과도하게 굽혀졌습니다. 관절 손상을 예방하기 위해 무릎을 약간 덜 굽히고 체중을 고르게 분산시켜주세요.'
                else:
                    csv_text = "올바르지 않은 자세가 감지되었습니다. 선택하신 자세가 맞으십니까?"
            except Exception as e:
                # 예외 처리
                print(f"rror in result view: {e}")
                csv_text = "데이터 처리 중 오류가 발생했습니다."
        else:
            csv_text = "CSV 파일을 찾을 수 없습니다."
    elif style == 'pullup':
        csv_file_path = os.path.join("frame_point/pullup/pullco/all_points.csv")
        if os.path.exists(csv_file_path):
            try:
                # CSV 파일을 모델에 import하고 rank_value를 받음
                rank_value = import_csv_to_model(csv_file_path)
            
                # RankHistory 모델에 rank_value 저장
                RankHistory.objects.create(user=user, rank_value=rank_value, posture=style)  # posture 변수 저장
            
                # CSV 파일을 DataFrame으로 읽기
                df = pd.read_csv(csv_file_path, encoding='euc-kr')
            
                # '올바른 자세'인 행의 posture 컬럼 값 리스트로 가져오기
                correct_postures = df[df['Posture'] == '올바른 자세']['Posture'].tolist()
            
                # '올바르지 않은 자세'인 행의 첫 번째 프레임 가져오기
                incorrect_postures = df[df['Posture'] == '올바르지 못한 자세'].iloc[0]
                if style == 'pullup':
                    print("pullup.")
            except Exception as e:
                # 예외 처리
                print(f"Error in result view: {e}")
                csv_text = "데이터 처리 중 오류가 발생했습니다."
        else:
            csv_text = "CSV 파일을 찾을 수 없습니다."
    elif style == 'squat':
        csv_file_path = os.path.join("frame_point/squat/squatco/all_points.csv")
        if os.path.exists(csv_file_path):
            try:
                # CSV 파일을 모델에 import하고 rank_value를 받음
                rank_value = import_csv_to_model(csv_file_path)
            
                # RankHistory 모델에 rank_value 저장
                RankHistory.objects.create(user=user, rank_value=rank_value, posture=style)  # posture 변수 저장
            
                # CSV 파일을 DataFrame으로 읽기
                df = pd.read_csv(csv_file_path, encoding='euc-kr')
            
                # '올바른 자세'인 행의 posture 컬럼 값 리스트로 가져오기
                correct_postures = df[df['Posture'] == '올바른 자세']['Posture'].tolist()
            
                # '올바르지 않은 자세'인 행의 첫 번째 프레임 가져오기
                incorrect_postures = df[df['Posture'] == '올바르지 못한 자세'].iloc[0]
                if style == 'squat':
                    print("squat.")
            except Exception as e:
                # 예외 처리
                print(f"Error in result view: {e}")
                csv_text = "데이터 처리 중 오류가 발생했습니다."
        else:
            csv_text = "CSV 파일을 찾을 수 없습니다."
    elif style == 'flank':
        csv_file_path = os.path.join("frame_point/flank/flank_co/all_points.csv")
        if os.path.exists(csv_file_path):
            try:
                # CSV 파일을 모델에 import하고 rank_value를 받음
                rank_value = import_csv_to_model(csv_file_path)
            
                # RankHistory 모델에 rank_value 저장
                RankHistory.objects.create(user=user, rank_value=rank_value, posture=style)  # posture 변수 저장
            
                # CSV 파일을 DataFrame으로 읽기
                df = pd.read_csv(csv_file_path, encoding='euc-kr')
            
                # '올바른 자세'인 행의 posture 컬럼 값 리스트로 가져오기
                correct_postures = df[df['Posture'] == '올바른 자세']['Posture'].tolist()
            
                # '올바르지 않은 자세'인 행의 첫 번째 프레임 가져오기
                incorrect_postures = df[df['Posture'] == '올바르지 못한 자세'].iloc[0]
                if style == 'flank':
                    print("flank.")
            except Exception as e:
                # 예외 처리
                print(f"Error in result view: {e}")
                csv_text = "데이터 처리 중 오류가 발생했습니다."
        else:
            csv_text = "CSV 파일을 찾을 수 없습니다."
        

    # 비디오 리스트 가져오기
    videos = Video.objects.all()
    
    # 템플릿 렌더링
    return render(request, 'v2/result.html', {'videos': videos, 'csv_text': csv_text, 'rank_value': rank_value, 'context': context})

def flank_video(request):
    if request.method == "POST":
        if 'document' in request.FILES:
            document = request.FILES["document"]

            # 변경할 파일 이름 설정
            new_file_name = "flank_test"

            existing_file_path = os.path.join(settings.MEDIA_ROOT, new_file_name + ".mp4")
            if os.path.exists(existing_file_path):
                os.remove(existing_file_path)

            # 기존 데이터베이스 레코드 삭제
            Video.objects.all().delete()

            # 업로드된 파일의 확장자 가져오기
            file_extension = os.path.splitext(document.name)[1]

            # 새 파일 이름과 확장자 결합
            new_file_name_with_extension = f"{new_file_name}{file_extension}"

            # 새로운 파일 저장
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            filename = fs.save(new_file_name_with_extension, document)

            # 데이터베이스에 정보 저장
            document = Video(title=new_file_name_with_extension, document=filename)
            document.save()

            # 'lunge' 변수 저장
            request.session['style'] = 'flank'  # 세션에 'style' 변수 저장

    # 가장 최근의 비디오 가져오기 (하나만 존재할 것이므로)
    latest_video = Video.objects.latest('upload_date') if Video.objects.exists() else None
    flank_tool(request) 
    return render(request, "v2/events.html", context={"video": latest_video})
def squat_video(request):
    if request.method == "POST":
        if 'document' in request.FILES:
            document = request.FILES["document"]

            # 변경할 파일 이름 설정
            new_file_name = "squat_test"

            existing_file_path = os.path.join(settings.MEDIA_ROOT, new_file_name + ".mp4")
            if os.path.exists(existing_file_path):
                os.remove(existing_file_path)

            # 기존 데이터베이스 레코드 삭제
            Video.objects.all().delete()

            # 업로드된 파일의 확장자 가져오기
            file_extension = os.path.splitext(document.name)[1]

            # 새 파일 이름과 확장자 결합
            new_file_name_with_extension = f"{new_file_name}{file_extension}"

            # 새로운 파일 저장
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            filename = fs.save(new_file_name_with_extension, document)

            # 데이터베이스에 정보 저장
            document = Video(title=new_file_name_with_extension, document=filename)
            document.save()

            # 'lunge' 변수 저장
            request.session['style'] = 'flank'  # 세션에 'style' 변수 저장

    # 가장 최근의 비디오 가져오기 (하나만 존재할 것이므로)
    latest_video = Video.objects.latest('upload_date') if Video.objects.exists() else None
    squat_tool(request) 
    return render(request, "v2/events.html", context={"video": latest_video})

from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
# lunge_video 함수
def lunge_video(request):
    if request.method == "POST":
        if 'document' in request.FILES:
            document = request.FILES["document"]

            # 변경할 파일 이름 설정
            new_file_name = "lunge_test"

            existing_file_path = os.path.join(settings.MEDIA_ROOT, new_file_name + ".mp4")
            if os.path.exists(existing_file_path):
                os.remove(existing_file_path)

            # 기존 데이터베이스 레코드 삭제
            Video.objects.all().delete()

            # 업로드된 파일의 확장자 가져오기
            file_extension = os.path.splitext(document.name)[1]

            # 새 파일 이름과 확장자 결합
            new_file_name_with_extension = f"{new_file_name}{file_extension}"

            # 새로운 파일 저장
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            filename = fs.save(new_file_name_with_extension, document)

            # 데이터베이스에 정보 저장
            document = Video(title=new_file_name_with_extension, document=filename)
            document.save()

    # 가장 최근의 비디오 가져오기 (하나만 존재할 것이므로)
    latest_video = Video.objects.latest('upload_date') if Video.objects.exists() else None
    lunge_tool(request) 
    return render(request, "v2/events.html", context={"video": latest_video})

# pullup_video 함수
def pullup_video(request):
    if request.method == "POST":
        if 'document' in request.FILES:
            document = request.FILES["document"]

            # 변경할 파일 이름 설정
            new_file_name = "pullup_test"

            existing_file_path = os.path.join(settings.MEDIA_ROOT, new_file_name + ".mp4")
            if os.path.exists(existing_file_path):
                os.remove(existing_file_path)

            # 기존 데이터베이스 레코드 삭제
            Video.objects.all().delete()

            # 업로드된 파일의 확장자 가져오기
            file_extension = os.path.splitext(document.name)[1]

            # 새 파일 이름과 확장자 결합
            new_file_name_with_extension = f"{new_file_name}{file_extension}"

            # 새로운 파일 저장
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            filename = fs.save(new_file_name_with_extension, document)

            # 데이터베이스에 정보 저장
            document = Video(title=new_file_name_with_extension, document=filename)
            document.save()

    # 가장 최근의 비디오 가져오기 (하나만 존재할 것이므로)
    latest_video = Video.objects.latest('upload_date') if Video.objects.exists() else None
    pullup_tool(request) 
    return render(request, "v2/events.html", context={"video": latest_video})




# calculate_angle 함수 정의
def lunge_calculate_angle(point_a, point_b, point_c):
    # 세 관절 사이의 각도 계산
    vector_ab = (point_b[0] - point_a[0], point_b[1] - point_a[1])
    vector_bc = (point_c[0] - point_b[0], point_c[1] - point_b[1])

    # 벡터의 길이 계산
    magnitude_ab = math.sqrt(vector_ab[0]**2 + vector_ab[1]**2)
    magnitude_bc = math.sqrt(vector_bc[0]**2 + vector_bc[1]**2)

    # 벡터의 내적 계산
    dot_product = vector_ab[0] * vector_bc[0] + vector_ab[1] * vector_bc[1]

    # 코사인 값 계산
    cosine_theta = dot_product / (magnitude_ab * magnitude_bc)
    
    # 각도 계산
    angle_rad = math.acos(cosine_theta)
    angle_deg = math.degrees(angle_rad)
    return 180 - angle_deg

# 왼쪽 엉덩이와 오른쪽 엉덩이의 y 좌표 비교하여 다리 판별
def detect_front_leg(Lhip_point, Rhip_point):
    if Lhip_point[1] < Rhip_point[1]:
        return "left"  # 왼쪽 다리가 앞으로 나옴
    else:
        return "right"  # 오른쪽 다리가 앞으로 나옴

# 데이터프레임의 한 열에서 y값을 출력하는 함수 정의
def lunge_get_y_value(coord_str):
    # 문자열을 파싱하여 튜플로 변환
    if pd.isna(coord_str) or coord_str == "None":
        return math.nan
    coord_tuple = ast.literal_eval(coord_str)
    # 튜플의 두 번째 요소인 y값을 반환
    return coord_tuple[1]

def lunge_find_max_y_frames(df, column_name, num):
    y_values = []
    frame_names = []

    # 데이터프레임의 한 열에서 y값을 추출하여 y_values 및 frame_names 리스트에 추가
    for index, row in df.iterrows():
        y_value = lunge_get_y_value(row[column_name])
        if not math.isnan(y_value):  # NaN이 아닐 경우에만 추가
            y_values.append(y_value)
            frame_names.append(df.iloc[index]['Frame Name'])

    # 상위 n개 y 값 추출
    top_n_y_frames = []
    for _ in range(num):
        if y_values:  # y_values가 비어 있지 않으면
            max_y_value = max(y_values)
            max_index = y_values.index(max_y_value)
            top_n_y_frames.append(frame_names[max_index])
            # 선택한 값을 제거하여 다음 최대값을 찾음
            y_values.pop(max_index)
            frame_names.pop(max_index)

    return top_n_y_frames

def video_div(style,folder_path,output_folder):
    # 동영상 파일 형식
    video_formats = ('.mp4', '.avi', '.mov')  # 필요에 따라 확장자 추가
    # 폴더 내의 모든 파일 가져오기
    file_list = os.listdir(folder_path)
    # 동영상 파일 필터링 및 동영상 경로 리스트 만들기
    video_paths = [os.path.join(folder_path, file) for file in file_list if file.lower().endswith(video_formats)]
    # 특정 단어가 포함된 동영상 파일만 선택하기
    video_paths_with_keyword = [path for path in video_paths if style in path.lower()]
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)  # 기존 폴더 삭제
    # 이미지 저장을 위한 폴더 생성
    os.makedirs(output_folder, exist_ok=True)

    # 각 동영상 파일별로 처리
    for video_path in video_paths_with_keyword:
        # 동영상 파일 열기
        cap = cv2.VideoCapture(video_path)
        # 동영상의 초당 프레임 수 가져오기
        fps = cap.get(cv2.CAP_PROP_FPS)
        # 0.5초마다 이미지 저장할 시간 간격
        interval = int(fps * 0.5)
        # 프레임 인덱스 초기화
        frame_index = 0
        # 이미지 저장 시간 초기화
        save_time = 0
        # 프레임 단위로 동영상을 읽어와 이미지로 저장
        while True:
            # 동영상 파일로부터 프레임 읽기
            ret, frame = cap.read()
            # 프레임을 모두 읽었거나 동영상 파일이 종료되면 반복문 탈출
            if not ret:
                break
            # 0.5초마다 이미지 저장
            if frame_index >= save_time:
                # 프레임 이미지 저장
                image_path = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(video_path))[0]}_frame_{frame_index}.jpg")
                cv2.imwrite(image_path, frame)
                # 이미지 저장 시간 업데이트
                save_time += interval
            # 다음 프레임 인덱스로 이동
            frame_index += 1
        # 동영상 파일 닫기
        cap.release()

import time
import json
import os

def save_progress(progress_value):
    progress_data = {"progress": progress_value}
    json_path = os.path.join(settings.MEDIA_ROOT, "progress.json")
    with open(json_path, "w") as f:
        json.dump(progress_data, f)

# 런지 Body25
def lunge_tool(request):
    save_progress(0)
    # 동영상 파일 경로
    folder_path = "media"
    style = 'lunge'
    request.session['style'] = style
    # 저장할 이미지 폴더 경로
    output_folder = "frame_split/lunge/lunge_co"
    image_output_folder = "frame_split/lunge/lungeimage"
    output_csv_file_folder = "frame_split/lunge/lunge_co"
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder, exist_ok=True)
    if os.path.exists(image_output_folder):
        shutil.rmtree(image_output_folder)
    os.makedirs(image_output_folder, exist_ok=True)
    if os.path.exists(output_csv_file_folder):
        shutil.rmtree(output_csv_file_folder)
    os.makedirs(output_csv_file_folder, exist_ok=True)
    video_div(style,folder_path,output_folder)
    
    BODY_PARTS_BODY_25 = {0: "Nose", 1: "Neck", 2: "RShoulder", 3: "RElbow", 4: "RWrist",
                      5: "LShoulder", 6: "LElbow", 7: "LWrist", 8: "MidHip", 9: "RHip",
                      10: "RKnee", 11: "RAnkle", 12: "LHip", 13: "LKnee", 14: "LAnkle",
                      15: "REye", 16: "LEye", 17: "REar", 18: "LEar", 19: "LBigToe",
                      20: "LSmallToe", 21: "LHeel", 22: "RBigToe", 23: "RSmallToe", 24: "RHeel", 25: "Background"}

    POSE_PAIRS_BODY_25 = [[0, 1], [0, 15], [0, 16], [1, 2], [1, 5], [1, 8], [8, 9], [8, 12], [9, 10], [12, 13], [2, 3],
                      [3, 4], [5, 6], [6, 7], [10, 11], [13, 14], [15, 17], [16, 18], [14, 21], [19, 21], [20, 21],
                      [11, 24], [22, 24], [23, 24]]

    protoFile_body_25 = "pose_deploy.prototxt"
    weightsFile_body_25 = "pose_iter_584000.caffemodel"
    net = cv2.dnn.readNetFromCaffe(protoFile_body_25, weightsFile_body_25)

    # 결과를 저장할 CSV 파일 경로
    output_csv_folder = "frame_point/lunge/lunge_co"
    output_csv_file = "frame_point/lunge/lunge_co/all_points.csv"

    # 이미지 파일 필터링 및 이미지 경로 리스트 만들기
    folder_path = "frame_split/lunge/lunge_co"
    file_list = os.listdir(folder_path)
    image_paths = [os.path.join(folder_path, file) for file in file_list if file.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if os.path.exists(output_csv_file):
        os.remove(output_csv_file)

    # 텍스트 파일 열기 (추가 모드)
    with open(output_csv_file, "w", newline='') as csvfile:
        # CSV writer 생성
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([
            "Frame Name", "Point 0", "Point 1", "Point 2", "Point 3", "Point 4", "Point 5", "Point 6", "Point 7", "Point 8",
            "Point 9", "Point 10", "Point 11", "Point 12", "Point 13", "Point 14", "Point 15", "Point 16", "Point 17",
            "Point 18", "Point 19", "Point 20", "Point 21", "Point 22", "Point 23", "Point 24","Point 25","knee_angle_left","knee_angle_right"
        ])

        # 이미지 경로마다 반복하여 처리
        for idx, image_path in enumerate(image_paths):
            points = []
            # 프레임 이름 추출
            frame_name = os.path.basename(image_path)
            # 이미지 읽어오기
            image = cv2.imread(image_path)
            # 입력 이미지의 사이즈 정의
            image_height, image_width, _ = image.shape

            # 네트워크에 넣기 위한 전처리
            input_blob = cv2.dnn.blobFromImage(image, 1.0 / 255, (image_width, image_height), (0, 0, 0), swapRB=False, crop=False)

            # 전처리된 blob 네트워크에 입력
            net.setInput(input_blob)

            # 결과 받아오기
            output = net.forward()

            for i in range(len(BODY_PARTS_BODY_25)):
                # 신체 부위의 confidence map
                prob_map = output[0, i, :, :]

                # 최소값, 최대값, 최소값 위치, 최대값 위치
                min_val, prob, min_loc, point = cv2.minMaxLoc(prob_map)

                # 원본 이미지에 맞게 포인트 위치 조정
                x = (image_width * point[0]) / output.shape[3]
                y = (image_height * point[1]) / output.shape[2]
                                                                                                
                if prob > 0.2 :  # [pointed]
                    points.append((int(x), int(y)))
                
                else:  # [not pointed]
                    points.append(None)

            # 무릎, 발목, 엉덩이 포인트 추출
            Rknee_point = points[10]
            Lknee_point = points[13]
            Rankle_point = points[11]
            Lankle_point = points[14]
            Rhip_point = points[9]
            Lhip_point = points[12]

            if Rknee_point and Lknee_point and Rankle_point and Lankle_point and Rhip_point and Lhip_point:
                # 좌측 다리 각도 계산
                knee_angle_left = lunge_calculate_angle(Lankle_point, Lknee_point, Lhip_point)
                knee_angle_right = lunge_calculate_angle(Rankle_point, Rknee_point, Rhip_point)

                # 각 프레임의 데이터를 CSV 파일에 추가
                csvwriter.writerow([frame_name] + points + [knee_angle_left, knee_angle_right])

            for pair in POSE_PAIRS_BODY_25:
                part_a = pair[0]
                part_b = pair[1]
                if points[part_a] and points[part_b]:
                    cv2.line(image, points[part_a], points[part_b], (0, 255, 0), 2)
            file_name_with_suffix = os.path.splitext(frame_name)[0] + '_image.jpg'  # 파일명 뒤에 _image 추가
            save_path = os.path.join(image_output_folder, file_name_with_suffix)
            # 진행률 업데이트
            progress_percentage = 10 + (idx / len(image_paths)) * 40
            save_progress(progress_percentage)
            # 수정된 이미지 저장
            cv2.imwrite(save_path, image)
    save_progress(99)  # 이미지 분석 완료 후 99% 진행
            

    df = pd.read_csv(output_csv_file, encoding='CP949')

    max_y_result = lunge_find_max_y_frames(df, 'Point 8', 5)
    
    for frame_name in max_y_result:
        # 주어진 프레임에 해당하는 데이터프레임 추출
        frame_df = df[df['Frame Name'] == frame_name]
        # 프레임의 관절 포인트 추출
        points = frame_df.iloc[0][1:16]  # 프레임의 관절 포인트는 데이터프레임의 두 번째부터 열에 저장되어 있다고 가정
        
        # 관절 포인트 문자열을 튜플로 변환
        points = [ast.literal_eval(p) if pd.notna(p) and p != "None" else None for p in points]
        
        # 무릎, 발목, 엉덩이 포인트 추출
        Rknee_point = points[10]
        Lknee_point = points[13]
        Rankle_point = points[11]
        Lankle_point = points[14]
        Rhip_point = points[9]
        Lhip_point = points[12]
        
        posture = ""
        
        if Rknee_point and Lknee_point and Rankle_point and Lankle_point and Rhip_point and Lhip_point:
            # 좌측 다리 각도 계산
            knee_angle_left = lunge_calculate_angle(Lankle_point, Lknee_point, Lhip_point)
            knee_angle_right = lunge_calculate_angle(Rankle_point, Rknee_point, Rhip_point)
            
            if (detect_front_leg(Lhip_point, Rhip_point) == "left"):
                if(80 <= knee_angle_left <= 100):
                    posture="올바른 자세"
                else:
                    posture="올바르지 못한 자세"
            else:
                if (80 <= knee_angle_right <= 100):
                    posture="올바른 자세"
                else:
                    posture="올바르지 못한 자세"
        else:
            posture="올바르지 못한 자세"

        # 결과를 데이터프레임에 추가
        df.loc[df['Frame Name'] == frame_name, 'front'] = detect_front_leg(Lhip_point, Rhip_point)
        df.loc[df['Frame Name'] == frame_name, 'Posture'] = posture
            
            #src_image_path = os.path.join(folder_path, frame_name)
            #dst_image_path = os.path.join(result_image_folder, frame_name)
            #shutil.copyfile(src_image_path, dst_image_path)
    save_progress(100)  # 모든 작업 완료
    # 업데이트된 데이터프레임 저장
    df.to_csv(output_csv_file, index=False, encoding='cp949')
    return style
# ----------------------------------------------------------------------#



# pullup 실행 코드
def pullup_calculate_angle(a, b, c):
    try:
        rad1 = math.atan((a[1]-b[1]) / (a[0]-b[0]))
    except ZeroDivisionError:
        rad1 = 0
    try:
        rad2 = math.atan((a[1]-c[1]) / (a[0]-c[0]))
    except ZeroDivisionError:
        rad2 = 0    
    angle = abs((rad1-rad2) * 180/math.pi)
    return angle

def calculate_distance(point_a, point_b):
    x1, y1 = point_a
    x2, y2 = point_b
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance

def pullup_get_y_value(coord_str):
    if pd.isna(coord_str) or coord_str == "None":
        return math.nan
    # 문자열을 파싱하여 튜플로 변환
    coord_tuple = ast.literal_eval(coord_str)
    # 튜플의 두 번째 요소인 y값을 반환
    return coord_tuple[1]

def pullup_find_min_y_frames(df, column_name, num):
    y_values = []
    frame_names = []

    # 데이터프레임의 한 열에서 y값을 추출하여 y_values 및 frame_names 리스트에 추가
    for index, row in df.iterrows():
        y_value = pullup_get_y_value(row[column_name])
        if not math.isnan(y_value):  # NaN이 아닐 경우에만 추가
            y_values.append(y_value)
            frame_names.append(df.iloc[index]['Frame Name'])

    # 하위 n개 y 값 추출
    bottom_n_y_frames = []
    for _ in range(num):
        if y_values:  # y_values가 비어 있지 않으면
            min_y_value = min(y_values)
            min_index = y_values.index(min_y_value)
            bottom_n_y_frames.append(frame_names[min_index])
            # 선택한 값을 제거하여 다음 최소값을 찾음
            y_values.pop(min_index)
            frame_names.pop(min_index)

    return bottom_n_y_frames

def pullup_tool(request):
    save_progress(10)
    # 동영상 파일 경로
    folder_path = "media"
    style = 'pullup'
    request.session['style'] = style
    # 저장할 이미지 폴더 경로
    output_folder = "frame_split/pullup/pullco"
    image_output_folder = "frame_split/pullup/pullimage"
    output_csv_file_folder = "frame_split/pullup/pullco"
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder, exist_ok=True)
    if os.path.exists(image_output_folder):
        shutil.rmtree(image_output_folder)
    os.makedirs(image_output_folder, exist_ok=True)
    if os.path.exists(output_csv_file_folder):
        shutil.rmtree(output_csv_file_folder)
    os.makedirs(output_csv_file_folder, exist_ok=True)
    save_progress(10)  # 10% 진행
    video_div(style,folder_path,output_folder)

    # MPII에서 각 파트 번호, 선으로 연결될 POSE_PAIRS
    BODY_PARTS = { "Head": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
                    "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
                    "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "Chest": 14,
                    "Background": 15 }

    POSE_PAIRS = [ ["Head", "Neck"], ["Neck", "RShoulder"], ["RShoulder", "RElbow"],
                    ["RElbow", "RWrist"], ["Neck", "LShoulder"], ["LShoulder", "LElbow"],
                    ["LElbow", "LWrist"], ["Neck", "Chest"], ["Chest", "RHip"], ["RHip", "RKnee"],
                    ["RKnee", "RAnkle"], ["Chest", "LHip"], ["LHip", "LKnee"], ["LKnee", "LAnkle"] ]
    
    protoFile = "pose_deploy_linevec_faster_4_stages.prototxt"
    weightsFile = "pose_iter_160000.caffemodel"
    net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)
    
    # 결과를 저장할 CSV 파일 경로
    output_csv_folder = "frame_point/pullup/pullco"
    output_csv_file = "frame_point/pullup/pullco/all_points.csv"
    # 초록선이 추가된 이미지를 저장할 경로

    # 이미지 파일 필터링 및 이미지 경로 리스트 만들기
    folder_path = "frame_split/pullup/pullco"
    file_list = os.listdir(folder_path)
    image_paths = [os.path.join(folder_path, file) for file in file_list if file.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if os.path.exists(output_csv_file):
        os.remove(output_csv_file)

    # CSV 파일 열기 (append 모드로)
    with open(output_csv_file, 'w', newline='') as csvfile:
        # CSV writer 생성
        csvwriter = csv.writer(csvfile)
        # 헤더 작성
        csvwriter.writerow(["Frame Name", "Point 0", "Point 1", "Point 2", "Point 3", "Point 4", "Point 5", 
                            "Point 6", "Point 7", "Point 8", "Point 9", "Point 10", "Point 11", "Point 12", 
                            "Point 13", "Point 14", "arm_angle_right","arm_angle_left", "shoulder_length","wrist_length", "Posture"])
        # 이미지 경로마다 반복하여 처리
        for idx,image_path in enumerate(image_paths):
            points = []
            # 프레임 이름 추출
            frame_name = os.path.basename(image_path)
            # 이미지 읽어오기
            image = cv2.imread(image_path)
            # frame.shape = 불러온 이미지에서 height, width, color 받아옴
            imageHeight, imageWidth, _ = image.shape
            # network에 넣기위해 전처리
            inpBlob = cv2.dnn.blobFromImage(image, 1.0 / 255, (imageWidth, imageHeight), (0, 0, 0), swapRB=False, crop=False)
            # network에 넣어주기
            net.setInput(inpBlob)
            # 결과 받아오기
            output = net.forward()
            # 키포인트 검출시 이미지에 그려줌
            for i in range(0, 15):
                # 해당 신체부위 신뢰도 얻음.
                probMap = output[0, i, :, :]
                # global 최대값 찾기
                minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)
                # 원래 이미지에 맞게 점 위치 변경
                x = (imageWidth * point[0]) / output.shape[3]
                y = (imageHeight * point[1]) / output.shape[2]
                # 키포인트 검출한 결과가 0.3보다 크면(검출한곳이 위 BODY_PARTS랑 맞는 부위면) points에 추가, 검출했는데 부위가 없으면 None으로
                if prob > 0.2 :    
                    points.append((int(x), int(y)))
                else :
                    points.append(None)
            
            chest_point = points[BODY_PARTS["Chest"]]
            shoulder_left = points[BODY_PARTS["LShoulder"]]
            shoulder_right = points[BODY_PARTS["RShoulder"]]
            elbow_left = points[BODY_PARTS["LElbow"]]
            elbow_right = points[BODY_PARTS["RElbow"]]
            wrist_left = points[BODY_PARTS["LWrist"]]
            wrist_right = points[BODY_PARTS["RWrist"]]
            knee_left = points[BODY_PARTS["LKnee"]]

            # 진행률 업데이트
            progress_percentage = 10 + (idx / len(image_paths)) * 80
            save_progress(progress_percentage)

            if chest_point and shoulder_left and shoulder_right and elbow_right and elbow_left and wrist_left and wrist_right and knee_left:
                # 무릎 각도 계산 (다리 사이의 각도)
                arm_angle_right = pullup_calculate_angle(chest_point, shoulder_right, elbow_right)
                arm_angle_left = pullup_calculate_angle(chest_point, shoulder_left, elbow_left)
                shoulder_length = calculate_distance(shoulder_right, shoulder_left)
                wrist_length = calculate_distance(wrist_right, wrist_left)

                # 각 프레임의 데이터를 CSV 파일에 추가
                csvwriter.writerow([frame_name] + points + [arm_angle_right,arm_angle_left, shoulder_length,wrist_length])
            
            for pair in POSE_PAIRS:
                    partA = pair[0]
                    partB = pair[1]
                    if points[BODY_PARTS[partA]] and points[BODY_PARTS[partB]]:
                        cv2.line(image, points[BODY_PARTS[partA]], points[BODY_PARTS[partB]], (0, 255, 0), 2)

            file_name_with_suffix = os.path.splitext(frame_name)[0] + '_image.jpg'  # 파일명 뒤에 _image 추가
            save_path = os.path.join(image_output_folder, file_name_with_suffix)

            # 수정된 이미지 저장
            cv2.imwrite(save_path, image)

    save_progress(99)  # 이미지 분석 완료 후 99% 진행 
    df = pd.read_csv(output_csv_file, encoding='CP949')
    min_y_result = pullup_find_min_y_frames(df, 'Point 14', 10)

    for frame_name in min_y_result:
        # 주어진 프레임에 해당하는 데이터프레임 추출
        frame_df = df[df['Frame Name'] == frame_name]
        
        # 프레임의 관절 포인트 추출
        points = frame_df.iloc[0][1:16]  # 프레임의 관절 포인트는 데이터프레임의 두 번째부터 열에 저장되어 있다고 가정
        
        # 관절 포인트 문자열을 튜플로 변환
        points = [ast.literal_eval(p) if pd.notna(p) and p != "None" else None for p in points]
        
        chest_point = points[BODY_PARTS["Chest"]]
        shoulder_left = points[BODY_PARTS["LShoulder"]]
        shoulder_right = points[BODY_PARTS["RShoulder"]]
        elbow_left = points[BODY_PARTS["LElbow"]]
        elbow_right = points[BODY_PARTS["RElbow"]]
        wrist_left = points[BODY_PARTS["LWrist"]]
        wrist_right = points[BODY_PARTS["RWrist"]]
        
        posture = ""
        if chest_point and shoulder_left and shoulder_right and elbow_right and elbow_left and wrist_left and wrist_right:
            arm_angle_right = pullup_calculate_angle(chest_point, shoulder_right, elbow_right)
            arm_angle_left = pullup_calculate_angle(chest_point, shoulder_left, elbow_left)
            shoulder_length = calculate_distance(shoulder_right, shoulder_left)
            wrist_length = calculate_distance(wrist_right, wrist_left)

            if ((shoulder_length * 2.3) >= wrist_length and wrist_length >= (shoulder_length * 1.5)):
                if ((55 >= arm_angle_right >= 35) & (55 >= arm_angle_left >= 35)):
                    posture = "올바른 자세"
                else:
                    posture = "올바르지 못한 자세"
            else:
                posture = "올바르지 못한 자세"
        else:
            posture = "올바르지 못한 자세"

        # 결과를 데이터프레임에 추가
        df.loc[df['Frame Name'] == frame_name, 'Posture'] = posture
    
    # 업데이트된 데이터프레임 저장
    save_progress(100)  # 모든 작업 완료  
    # 업데이트된 데이터프레임 저장
    df.to_csv(output_csv_file, index=False, encoding='CP949')
    return style

# squat 실행 코드
def squat_calculate_angle(a, b, c):
    try:
        rad1 = math.atan((a[1]-b[1]) / (a[0]-b[0]))
    except ZeroDivisionError:
        rad1 = 0
    try:
        rad2 = math.atan((a[1]-c[1]) / (a[0]-c[0]))
    except ZeroDivisionError:
        rad2 = 0

    angle = abs((rad1-rad2) * 180/math.pi)
    return angle

def squat_get_y_value(coord_str):
    # 문자열을 파싱하여 튜플로 변환
    coord_tuple = ast.literal_eval(coord_str)
    # 튜플의 두 번째 요소인 y값을 반환
    return coord_tuple[1]

def squat_find_max_y_frames(df, column_name, num):
    y_values = []
    frame_names = []

    # 데이터프레임의 한 열에서 y값을 추출하여 y_values 및 frame_names 리스트에 추가
    for index, row in df.iterrows():
        y_value = squat_get_y_value(row[column_name])
        if not math.isnan(y_value):  # NaN이 아닐 경우에만 추가
            y_values.append(y_value)
            frame_names.append(df.iloc[index]['Frame Name'])

    # 상위 n개 y 값 추출
    top_n_y_frames = []
    for _ in range(num):
        if y_values:  # y_values가 비어 있지 않으면
            max_y_value = max(y_values)
            max_index = y_values.index(max_y_value)
            top_n_y_frames.append(frame_names[max_index])
            # 선택한 값을 제거하여 다음 최대값을 찾음
            y_values.pop(max_index)
            frame_names.pop(max_index)

    return top_n_y_frames

def squat_tool(request):
    save_progress(10)
    # 동영상 파일 경로
    folder_path = "media"
    style = 'squat'
    request.session['style'] = style
    # 저장할 이미지 폴더 경로
    output_folder = "frame_split/squat/squatco"
    image_output_folder = "frame_split/squat/squatimage"
    output_csv_file_folder = "frame_point/squat/squatco"
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder, exist_ok=True)
    if os.path.exists(image_output_folder):
        shutil.rmtree(image_output_folder)
    os.makedirs(image_output_folder, exist_ok=True)
    if os.path.exists(output_csv_file_folder):
        shutil.rmtree(output_csv_file_folder)
    os.makedirs(output_csv_file_folder, exist_ok=True)
    save_progress(10)  # 10% 진행
    video_div(style,folder_path,output_folder)

    # MPII에서 각 파트 번호, 선으로 연결될 POSE_PAIRS
    BODY_PARTS = { "Head": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
                    "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
                    "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "Chest": 14,
                    "Background": 15 }

    POSE_PAIRS = [ ["Head", "Neck"], ["Neck", "RShoulder"], ["RShoulder", "RElbow"],
                    ["RElbow", "RWrist"], ["Neck", "LShoulder"], ["LShoulder", "LElbow"],
                    ["LElbow", "LWrist"], ["Neck", "Chest"], ["Chest", "RHip"], ["RHip", "RKnee"],
                    ["RKnee", "RAnkle"], ["Chest", "LHip"], ["LHip", "LKnee"], ["LKnee", "LAnkle"] ]
    
    protoFile = "pose_deploy_linevec_faster_4_stages.prototxt"
    weightsFile = "pose_iter_160000.caffemodel"
    net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)
    
    # 결과를 저장할 CSV 파일 경로
    output_csv_folder = "frame_point/squat/squatco"
    output_csv_file = "frame_point/squat/squatco/all_points.csv"

    # 이미지 파일 필터링 및 이미지 경로 리스트 만들기
    folder_path = "frame_split/squat/squatco"
    file_list = os.listdir(folder_path)
    image_paths = [os.path.join(folder_path, file) for file in file_list if file.lower().endswith(('.png', '.jpg', '.jpeg'))]
    # CSV 파일 열기 (append 모드로)
    
    # CSV 파일 열기 (append 모드로)
    with open(output_csv_file, 'w', newline='') as csvfile:
        # CSV writer 생성
        csvwriter = csv.writer(csvfile)
        # 헤더 작성
        csvwriter.writerow(["Frame Name", "Point 0", "Point 1", "Point 2", "Point 3", "Point 4", "Point 5", 
                            "Point 6", "Point 7", "Point 8", "Point 9", "Point 10", "Point 11", "Point 12", 
                            "Point 13", "Point 14", "knee_angle_left", "knee_angle_right", "Posture"])
        # 이미지 경로마다 반복하여 처리
        for idx,image_path in enumerate(image_paths):
            points = []
            # 프레임 이름 추출
            frame_name = os.path.basename(image_path)
            # 이미지 읽어오기
            image = cv2.imread(image_path)
            # frame.shape = 불러온 이미지에서 height, width, color 받아옴
            imageHeight = 368
            imageWidth = 368
            image = cv2.resize(image, (imageWidth, imageHeight))

            # network에 넣기위해 전처리
            inpBlob = cv2.dnn.blobFromImage(image, 1.0 / 255, (imageWidth, imageHeight), (0, 0, 0), swapRB=False, crop=False)
            # network에 넣어주기
            net.setInput(inpBlob)
            # 결과 받아오기
            output = net.forward()
            # 키포인트 검출시 이미지에 그려줌
            for i in range(0, 15):
                # 해당 신체부위 신뢰도 얻음.
                probMap = output[0, i, :, :]
                # global 최대값 찾기
                minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)
                # 원래 이미지에 맞게 점 위치 변경
                x = (imageWidth * point[0]) / output.shape[3]
                y = (imageHeight * point[1]) / output.shape[2]
                # 키포인트 검출한 결과가 0.3보다 크면(검출한곳이 위 BODY_PARTS랑 맞는 부위면) points에 추가, 검출했는데 부위가 없으면 None으로
                if prob > 0.1 :    
                    points.append((int(x), int(y)))
                else :
                    points.append(None)
            
            hip_left = points[BODY_PARTS["LHip"]]
            hip_right = points[BODY_PARTS["RHip"]]
            knee_left = points[BODY_PARTS["LKnee"]]
            knee_right = points[BODY_PARTS["RKnee"]]
            ankle_left = points[BODY_PARTS["LAnkle"]]
            ankle_right = points[BODY_PARTS["RAnkle"]]

            # 진행률 업데이트
            progress_percentage = 10 + (idx / len(image_paths)) * 80
            save_progress(progress_percentage)

            if hip_left and hip_right and knee_left and knee_right and ankle_left and ankle_right:
                # 무릎 각도 계산 (다리 사이의 각도)
                knee_angle_right = squat_calculate_angle(knee_right, hip_right, ankle_right)
                knee_angle_left = squat_calculate_angle(knee_left, hip_left, ankle_left)

                # 각 프레임의 데이터를 CSV 파일에 추가
                csvwriter.writerow([frame_name] + points + [knee_angle_left, knee_angle_right])

            # 초록 선 그리기
            for pair in POSE_PAIRS:
                partA = pair[0]
                partB = pair[1]
                if points[BODY_PARTS[partA]] and points[BODY_PARTS[partB]]:
                    cv2.line(image, points[BODY_PARTS[partA]], points[BODY_PARTS[partB]], (0, 255, 0), 3)

            file_name_with_suffix = os.path.splitext(frame_name)[0] + '_image.jpg'  # 파일명 뒤에 _image 추가
            save_path = os.path.join(image_output_folder, file_name_with_suffix)

            # 수정된 이미지 저장
            cv2.imwrite(save_path, image)
    
    save_progress(99)  # 이미지 분석 완료 후 99% 진행
    df = pd.read_csv(output_csv_file, encoding='CP949')
    max_y_result = squat_find_max_y_frames(df,'Point 8', 10)

    for frame_name in max_y_result:
        # 주어진 프레임에 해당하는 데이터프레임 추출
        frame_df = df[df['Frame Name'] == frame_name]
        
        # 프레임의 관절 포인트 추출
        points = frame_df.iloc[0][1:16]  # 프레임의 관절 포인트는 데이터프레임의 두 번째부터 열에 저장되어 있다고 가정
        
        # 관절 포인트 문자열을 튜플로 변환
        points = [ast.literal_eval(p) if pd.notna(p) and p != "None" else None for p in points]
        
        hip_left = points[BODY_PARTS["LHip"]]
        hip_right = points[BODY_PARTS["RHip"]]
        knee_left = points[BODY_PARTS["LKnee"]]
        knee_right = points[BODY_PARTS["RKnee"]]
        ankle_left = points[BODY_PARTS["LAnkle"]]
        ankle_right = points[BODY_PARTS["RAnkle"]]
        
        posture = ""
        if hip_left and hip_right and knee_left and knee_right and ankle_left and ankle_right:
            # 무릎 각도 계산 (다리 사이의 각도)
            knee_angle_right = squat_calculate_angle(knee_right, hip_right, ankle_right)
            knee_angle_left = squat_calculate_angle(knee_left, hip_left, ankle_left)
            
            # 자세 판단
            if (((knee_angle_left >= 50) & (knee_angle_left <= 90)) & ((knee_angle_right <= 90) & (knee_angle_right >= 50))):
                posture = "올바른 자세"
            else:
                posture = "올바르지 못한 자세"
        else:
            posture = "올바르지 못한 자세"
            
        # 결과를 데이터프레임에 추가
        df.loc[df['Frame Name'] == frame_name, 'Posture'] = posture
            #src_image_path = os.path.join(folder_path, frame_name)
            #dst_image_path = os.path.join(result_folder, frame_name)
            #shutil.copyfile(src_image_path, dst_image_path)
    
    save_progress(100)  # 모든 작업 완료 
    # 업데이트된 데이터프레임 저장
    df.to_csv(output_csv_file, index=False, encoding='CP949')
    return style

# flank 실행 코드
def flank_calculate_angle(point_a, point_b, point_c):
    # 세 관절 사이의 각도 계산
    vector_ab = (point_b[0] - point_a[0], point_b[1] - point_a[1])
    vector_bc = (point_c[0] - point_b[0], point_c[1] - point_b[1])
    
    # 벡터의 길이 계산
    magnitude_ab = math.sqrt(vector_ab[0]**2 + vector_ab[1]**2)
    magnitude_bc = math.sqrt(vector_bc[0]**2 + vector_bc[1]**2)
    
    # 벡터의 내적 계산
    dot_product = vector_ab[0] * vector_bc[0] + vector_ab[1] * vector_bc[1]
    
    # 코사인 값 계산
    cosine_theta = dot_product / (magnitude_ab * magnitude_bc)
    
    # 각도 계산
    angle_rad = math.acos(cosine_theta)
    angle_deg = math.degrees(angle_rad)
    
    return angle_deg

def flank_tool(request):
    save_progress(10)
    # 동영상 파일 경로
    folder_path = "media"
    style = 'flank'
    request.session['style'] = style
    # 저장할 이미지 폴더 경로
    output_folder = "frame_split/flank/flank_co"
    image_output_folder = "frame_split/flank/flankimage"
    output_csv_file_folder = "frame_point/flank/flank_co"
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder, exist_ok=True)
    if os.path.exists(image_output_folder):
        shutil.rmtree(image_output_folder)
    os.makedirs(image_output_folder, exist_ok=True)
    if os.path.exists(output_csv_file_folder):
        shutil.rmtree(output_csv_file_folder)
    os.makedirs(output_csv_file_folder, exist_ok=True)
    save_progress(10)  # 10% 진행
    video_div(style,folder_path,output_folder)
    
    BODY_PARTS_BODY_25 = {0: "Nose", 1: "Neck", 2: "RShoulder", 3: "RElbow", 4: "RWrist",
                      5: "LShoulder", 6: "LElbow", 7: "LWrist", 8: "MidHip", 9: "RHip",
                      10: "RKnee", 11: "RAnkle", 12: "LHip", 13: "LKnee", 14: "LAnkle",
                      15: "REye", 16: "LEye", 17: "REar", 18: "LEar", 19: "LBigToe",
                      20: "LSmallToe", 21: "LHeel", 22: "RBigToe", 23: "RSmallToe", 24: "RHeel", 25: "Background"}

    POSE_PAIRS_BODY_25 = [[0, 1], [0, 15], [0, 16], [1, 2], [1, 5], [1, 8], [8, 9], [8, 12], [9, 10], [12, 13], [2, 3],
                      [3, 4], [5, 6], [6, 7], [10, 11], [13, 14], [15, 17], [16, 18], [14, 21], [19, 21], [20, 21],
                      [11, 24], [22, 24], [23, 24]]

    protoFile_body_25 = "pose_deploy.prototxt"
    weightsFile_body_25 = "pose_iter_584000.caffemodel"
    net = cv2.dnn.readNetFromCaffe(protoFile_body_25, weightsFile_body_25)

    # 결과를 저장할 CSV 파일 경로
    output_csv_file = "frame_point/flank/flank_co/all_points.csv"

    # 이미지 파일 필터링 및 이미지 경로 리스트 만들기
    folder_path = "frame_split/flank/flank_co"
    file_list = os.listdir(folder_path)
    image_paths = [os.path.join(folder_path, file) for file in file_list if file.lower().endswith(('.png', '.jpg', '.jpeg'))]

    # 텍스트 파일 열기 (추가 모드)
    with open(output_csv_file, "w", newline='') as csvfile:
        # CSV writer 생성
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([
            "Frame Name", "Point 0", "Point 1", "Point 2", "Point 3", "Point 4", "Point 5", "Point 6", "Point 7", "Point 8",
            "Point 9", "Point 10", "Point 11", "Point 12", "Point 13", "Point 14", "Point 15", "Point 16", "Point 17",
            "Point 18", "Point 19", "Point 20", "Point 21", "Point 22", "Point 23", "Point 24","Point 25","knee_angle_left","Posture"
        ])

        # 이미지 경로마다 반복하여 처리
        for idx,image_path in enumerate(image_paths):
            points = []
            # 프레임 이름 추출
            frame_name = os.path.basename(image_path)
            # 이미지 읽어오기
            image = cv2.imread(image_path)
            # frame.shape = 불러온 이미지에서 height, width, color 받아옴
            imageHeight = 368
            imageWidth = 368
            image = cv2.resize(image, (imageWidth, imageHeight))
            # network에 넣기위해 전처리
            inpBlob = cv2.dnn.blobFromImage(image, 1.0 / 255, (imageWidth, imageHeight), (0, 0, 0), swapRB=False, crop=False)
            # network에 넣어주기
            net.setInput(inpBlob)
            # 결과 받아오기
            output = net.forward()
            # 키포인트 검출시 이미지에 그려줌
            for i in range(len(BODY_PARTS_BODY_25)):
                # 해당 신체부위 신뢰도 얻음.
                probMap = output[0, i, :, :]
                # global 최대값 찾기
                minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)
                # 원래 이미지에 맞게 점 위치 변경
                x = (imageWidth * point[0]) / output.shape[3]
                y = (imageHeight * point[1]) / output.shape[2]
                # 키포인트 검출한 결과가 0.3보다 크면(검출한곳이 위 BODY_PARTS랑 맞는 부위면) points에 추가, 검출했는데 부위가 없으면 None으로
                if prob > 0.1 :    
                    points.append((int(x), int(y)))
                else :
                    points.append(None)

            for pair in POSE_PAIRS_BODY_25:
                    partA = pair[0]
                    partB = pair[1]
                    if points[partA] and points[partB]:
                        cv2.line(image, points[partA], points[partB], (0, 255, 0), 2)

            file_name_with_suffix = os.path.splitext(frame_name)[0] + '_image.jpg'  # 파일명 뒤에 _image 추가
            save_path = os.path.join(image_output_folder, file_name_with_suffix)

            # 수정된 이미지 저장
            cv2.imwrite(save_path, image)
                    
            posture = ""

            # 무릎, 발목, 엉덩이 포인트 추출
            #Rknee_point = points[10]
            Lknee_point = points[13]
            #Rshoulder_point = points[2]
            Lshoulder_point = points[5]
            #Rhip_point = points[9]
            Lhip_point = points[12]
            #bg_point = points[25]

            # 진행률 업데이트
            progress_percentage = 10 + (idx / len(image_paths)) * 80
            save_progress(progress_percentage)

            if Lknee_point and Lhip_point and Lshoulder_point:
                y_shoulder = Lshoulder_point[1]
                y_hip = Lhip_point[1]
                y_knee = Lknee_point[1]
                # 좌측 다리 각도 계산
                knee_angle_left = flank_calculate_angle(Lshoulder_point, Lknee_point, Lhip_point)
                if (y_shoulder <= y_hip <= y_knee and 160 <= knee_angle_left <= 180):
                    posture = "올바른 자세"
                else:
                    posture = "올바르지 못한 자세"
                
                # 각 프레임의 데이터를 CSV 파일에 추가
                csvwriter.writerow([frame_name] + points + [knee_angle_left, posture])
    
    save_progress(100)  # 이미지 분석 완료 후 99% 진행
    df = pd.read_csv(output_csv_file, encoding='CP949')
    return style
