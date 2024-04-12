from django.shortcuts import render
from django.db import models
# Create your views here.
def four01(request):
    return render(request, 'v2/401.html')

def four04(request):
    return render(request, 'v2/404.html')

def five00(request):
    return render(request, 'v2/500.html')

def charts(request):
    return render(request, 'v2/charts.html')

def main(request):
    return render(request, 'v2/index.html')

def layout_sidenav_light(request):
    return render(request, 'v2/layout-sidenav-light.html')

def layout_static(request):
    return render(request, 'v2/layout-static.html')

def login(request):
    return render(request, 'v2/login.html')

def password(request):
    return render(request, 'v2/password.html')

def register(request):
    return render(request, 'v2/register.html')
def tables(request):
    return render(request, 'v2/tables.html')
def fileUp(request):
    return render(request, 'v2/fileUp.html')
from . import models
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import cv2
import math

def uploadFile(request):
    if request.method == "POST":
        fileTitle = request.POST["fileTitle"]
        uploadedFile = request.FILES["uploadedFile"]

        # Changing the file name to "squat_test.mp4"
        new_file_name = "squat_test.mp4"

        existing_file_path = os.path.join(settings.MEDIA_ROOT, new_file_name)
        if os.path.exists(existing_file_path):
            os.remove(existing_file_path)

        # Get the file extension of the uploaded file
        file_extension = os.path.splitext(uploadedFile.name)[1]

        # Combine the new file name with the original file extension
        new_file_name_with_extension = f"{new_file_name}{file_extension}"

        # Save the uploaded file with the new file name
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        filename = fs.save(new_file_name, uploadedFile)

        # Saving the information in the database
        document = models.Document(title=fileTitle, uploadedFile=filename)
        document.save()

        # 동영상 파일 프레임으로 쪼개는 코드


        # 동영상 파일 경로
        folder_path = "media"

        # 저장할 이미지 폴더 경로
        output_folder = "frame_split/squat/squat_co"

        # 동영상 파일 형식
        video_formats = ('.mp4', '.avi', '.mov')  # 필요에 따라 확장자 추가

        # 폴더 내의 모든 파일 가져오기
        file_list = os.listdir(folder_path)

        # 동영상 파일 필터링 및 동영상 경로 리스트 만들기
        video_paths = [os.path.join(folder_path, file) for file in file_list if file.lower().endswith(video_formats)]

        # 특정 단어가 포함된 동영상 파일만 선택하기
        video_paths_with_keyword = [path for path in video_paths if "squat" in path.lower()]

        # 이미지 저장을 위한 폴더 생성
        os.makedirs(output_folder, exist_ok=True)

        # 각 동영상 파일별로 처리
        for video_path in video_paths_with_keyword:
            # 동영상 파일 열기
            cap = cv2.VideoCapture(video_path)

            # 동영상 파일이 정상적으로 열렸는지 확인
            if not cap.isOpened():
                print("Error: Could not open video.")
                continue

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

        print("Images saved successfully in the 'frame_split/squat/squat_co' folder.")

        ####

        #### 가중치 파일 불러오고 mpii호출


        #스쿼트
        # MPII에서 각 파트 번호, 선으로 연결될 POSE_PAIRS
        BODY_PARTS = { "Head": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
                        "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
                        "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "Chest": 14,
                        "Background": 15 }

        POSE_PAIRS = [ ["Head", "Neck"], ["Neck", "RShoulder"], ["RShoulder", "RElbow"],
                        ["RElbow", "RWrist"], ["Neck", "LShoulder"], ["LShoulder", "LElbow"],
                        ["LElbow", "LWrist"], ["Neck", "Chest"], ["Chest", "RHip"], ["RHip", "RKnee"],
                        ["RKnee", "RAnkle"], ["Chest", "LHip"], ["LHip", "LKnee"], ["LKnee", "LAnkle"] ]

        # 각 파일 path
        protoFile = "pose_deploy_linevec_faster_4_stages.prototxt"
        weightsFile = "pose_iter_160000.caffemodel"

        # 위의 path에 있는 network 불러오기
        net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)

        #####



        ##### 프레임별로 포인트, 선 그리고 각도 계산
        # 이미지 파일이 있는 폴더 경로
        folder_path = "frame_split/squat/squat_co"

        # 폴더 내의 모든 파일 가져오기
        file_list = os.listdir(folder_path)

        # 이미지 파일 필터링 및 이미지 경로 리스트 만들기
        image_paths = [os.path.join(folder_path, file) for file in file_list if file.lower().endswith(('.png', '.jpg', '.jpeg'))]

        # 텍스트 파일 경로 설정
        output_text_path = "frame_point/squat/squat_co/all_points.txt"


        output_folder = "frame_point/squat/squat_co"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
    
        # 텍스트 파일 열기
        with open(output_text_path, 'w') as output_file:
            # 이미지 경로마다 반복하여 처리
            for image_path in image_paths:
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
                points = []
                for i in range(0, 15):
                    # 해당 신체부위 신뢰도 얻음.
                    probMap = output[0, i, :, :]

                    # global 최대값 찾기
                    minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)

                    # 원래 이미지에 맞게 점 위치 변경
                    x = (imageWidth * point[0]) / output.shape[3]
                    y = (imageHeight * point[1]) / output.shape[2]

                    # 키포인트 검출한 결과가 0.1보다 크면(검출한곳이 위 BODY_PARTS랑 맞는 부위면) points에 추가, 검출했는데 부위가 없으면 None으로
                    if prob > 0.1 :    
                        cv2.circle(image, (int(x), int(y)), 3, (0, 255, 255), thickness=-1, lineType=cv2.FILLED)
                        cv2.putText(image, "{}".format(i), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, lineType=cv2.LINE_AA)
                        points.append((int(x), int(y)))
                    else :
                        points.append(None)
                # 관절 포인트를 연결하여 선 그리기
                for pair in POSE_PAIRS:
                    partA = pair[0]
                    partB = pair[1]

                    if points[BODY_PARTS[partA]] and points[BODY_PARTS[partB]]:
                        cv2.line(image, points[BODY_PARTS[partA]], points[BODY_PARTS[partB]], (0, 255, 0), 3)


                output_image_path = os.path.join(output_folder, os.path.basename(image_path))
                cv2.imwrite(output_image_path, image)


        
                # 관절 포인트 값을 파일에 저장
                output_file.write(f"Image Path: {image_path}\n")
                for i, point in enumerate(points):
                    output_file.write(f'Point {i}: {point}\n')
            
                hip_left = points[BODY_PARTS["LHip"]]
                hip_right = points[BODY_PARTS["RHip"]]
                knee_left = points[BODY_PARTS["LKnee"]]
                knee_right = points[BODY_PARTS["RKnee"]]
                ankle_left = points[BODY_PARTS["LAnkle"]]
                ankle_right = points[BODY_PARTS["RAnkle"]]

                def calculate_angle(a, b, c):
            # 세 점 사이의 각도 계산
                    radians = math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0])
                    angle = math.degrees(radians)
                    #angle = angle + 360 if angle < 0 else angle
                    return angle
        
    
                if hip_left and hip_right and knee_left and knee_right and ankle_left and ankle_right:
                    # 무릎 각도 계산 (다리 사이의 각도)
                    knee_angle_left = calculate_angle(hip_left, knee_left, ankle_left)
                    knee_angle_right = calculate_angle(hip_right, knee_right, ankle_right)
                    output_file.write(f"Knee angle (Left): {knee_angle_left} degrees\n")
                    output_file.write(f"Knee angle (Right): {knee_angle_right} degrees\n")

                    # 허리 각도 계산 (허리와 다리 사이의 각도)
                    hip_center = ((hip_left[0] + hip_right[0]) // 2, (hip_left[1] + hip_right[1]) // 2)
                    neck = points[BODY_PARTS["Neck"]]
                    if neck:
                        waist_angle = calculate_angle(hip_center, neck, knee_left)  # 왼쪽 무릎을 기준으로 허리 각도 계산
                        output_file.write(f"Waist angle: {waist_angle} degrees\n")

        
                    if ((knee_angle_left <= 90) & (knee_angle_right <= 90)):
                        output_file.write("정확한 자세입니다.")
            
                    else:
                        output_file.write("올바르지 못한 자세입니다.")
            
                output_file.write("\n")
        
            
        print(f"All points saved successfully in the '{output_text_path}' file.")
        print(f"All images with keypoints saved successfully in the '{output_folder}' folder.")

        ####

    documents = models.Document.objects.all()

    return render(request, "v2/fileUp.html", context={"files": documents})
