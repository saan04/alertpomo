from django.shortcuts import render

# Create your views here.
#import requests
from django.http import JsonResponse
import mediapipe as mp
import cv2
import numpy as np
from django.views.decorators.csrf import csrf_exempt
from scipy.spatial import distance as dis
from django.http import StreamingHttpResponse, HttpResponseServerError
from django.views.decorators import gzip
#from dd import perform_drowsiness_detection
from django.shortcuts import render

# def pomodoro_timer(request):
#     return render(request, 'pomodoro.html')
#

from django.http import HttpResponse

@gzip.gzip_page
@csrf_exempt
def detect_drowsiness(request):
    if request.method == 'POST':
        video_frames = request.FILES.getlist('frames')

        print(f"Number of frames received: {len(video_frames)}")

        # Iterate over the frames and print each frame
        for frame in video_frames:
            print(f"Frame content: {frame.read()}")

        frame_count = 0
        min_frame = 6
        min_tolerance = 5.0
        results = []

        face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=2,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5
        )

        LEFT_EYE_TOP_BOTTOM = [386, 374]
        LEFT_EYE_LEFT_RIGHT = [263, 362]
        RIGHT_EYE_TOP_BOTTOM = [159, 145]
        RIGHT_EYE_LEFT_RIGHT = [133, 33]
        UPPER_LOWER_LIPS = [13, 14]
        LEFT_RIGHT_LIPS = [78, 308]

        for frame in video_frames:
            nparr = np.frombuffer(frame.read(), np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            outputs = face_mesh.process(image_rgb)

            if outputs.multi_face_landmarks:
                face_landmarks = outputs.multi_face_landmarks[0].landmark

                top = face_landmarks[LEFT_EYE_TOP_BOTTOM[0]]
                bottom = face_landmarks[LEFT_EYE_TOP_BOTTOM[1]]
                left = face_landmarks[LEFT_EYE_LEFT_RIGHT[0]]
                right = face_landmarks[LEFT_EYE_LEFT_RIGHT[1]]

                left_eye_top_bottom_dis = euclidean_distance(image, top, bottom)
                left_eye_left_right_dis = euclidean_distance(image, left, right)
                left_eye_ratio = left_eye_left_right_dis / left_eye_top_bottom_dis

                top = face_landmarks[RIGHT_EYE_TOP_BOTTOM[0]]
                bottom = face_landmarks[RIGHT_EYE_TOP_BOTTOM[1]]
                left = face_landmarks[RIGHT_EYE_LEFT_RIGHT[0]]
                right = face_landmarks[RIGHT_EYE_LEFT_RIGHT[1]]

                right_eye_top_bottom_dis = euclidean_distance(image, top, bottom)
                right_eye_left_right_dis = euclidean_distance(image, left, right)
                right_eye_ratio = right_eye_left_right_dis / right_eye_top_bottom_dis

                eye_ratio = (left_eye_ratio + right_eye_ratio) / 2.0

                if eye_ratio > min_tolerance:
                    frame_count += 1
                else:
                    frame_count = 0

                if frame_count > min_frame:
                    alert = 'Drowsiness Alert: It seems you are sleepy.. Wake up!'
                else:
                    alert = ''

                top = face_landmarks[UPPER_LOWER_LIPS[0]]
                bottom = face_landmarks[UPPER_LOWER_LIPS[1]]
                left = face_landmarks[LEFT_RIGHT_LIPS[0]]
                right = face_landmarks[LEFT_RIGHT_LIPS[1]]

                upper_lower_lips_dis = euclidean_distance(image, top, bottom)
                left_right_lips_dis = euclidean_distance(image, left, right)
                lips_ratio = left_right_lips_dis / upper_lower_lips_dis

                if lips_ratio < 1.8:
                    warning = 'Drowsiness Warning: You look tired.. Please take rest'
                else:
                    warning = ''

                results.append({
                    'frame_number': frame_count,
                    'drowsy': frame_count > min_frame,
                    'alert': alert,
                    'warning': warning
                })

            frame_count += 1

        return JsonResponse(results, safe=False)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def draw_text(image, text, position, color):
    cv2.putText(image, text, position, cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)

def euclidean_distance(image, top, bottom):
    height, width = image.shape[0:2]
    point1 = int(top.x * width), int(top.y * height)
    point2 = int(bottom.x * width), int(bottom.y * height)
    distance = dis.euclidean(point1, point2)
    return distance