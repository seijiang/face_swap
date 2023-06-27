import cv2
import face_recognition

def resize(input_image):
    height, width = input_image.shape[0], input_image.shape[1]
    size=450
    scale = height/size
    width_size = int(width/scale)
    input_image=cv2.resize(input_image,(width_size,size))
    return input_image
    
def faceswap_video(video,original_image,swap_image):
    #先得到换脸的照片中的脸
    # video=session['original_video']
    # original_image=session['original_face']
    # swap_image=session['swap_face']
    swap_face=face_recognition.load_image_file(swap_image)
    face_locations = face_recognition.face_locations(swap_face)
    top_swap, right_swap, bottom_swap, left_swap = face_locations[0]
    #将脸提取出来,需要将RGB(face_recognition)改成BGR(opencv)
    swap=swap_face[top_swap:bottom_swap, left_swap:right_swap,::-1]

    # Open the input movie file
    input_movie = cv2.VideoCapture(video)
    length = int(input_movie.get(7))
    video_width = int(input_movie.get(3))
    video_height = int(input_movie.get(4))
    video_fps = int(input_movie.get(5))
    # Create an output movie file (make sure resolution/frame rate matches input video!)
    fourcc = cv2.VideoWriter_fourcc(*'FMP4')
    output_movie = cv2.VideoWriter('output.avi', fourcc, video_fps, (video_width, video_height))
    if original_image == '':
        known_faces = []
    else :
        original = face_recognition.load_image_file(original_image)
        original_face_encoding = face_recognition.face_encodings(original)
        known_faces = original_face_encoding
    # Initialize some variables
    face_locations = []
    face_encodings = []
    frame_number = 0
    while True:
        # Grab a single frame of video
        ret, frame = input_movie.read()
        frame_number += 1

        # Quit when the input video file ends
        if not ret:
            break

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        for face_num in range(len(face_encodings)):
            # 如果已知脸不为空,判断是否是需要被换的人脸,否则全部替换
            if known_faces:
                match = True in (face_recognition.compare_faces(known_faces, face_encodings[face_num], tolerance=0.50))
            else:
                match= 1
            if(match):
                (top, right, bottom, left) = face_locations[face_num]
                frame_face=cv2.resize(swap,(right-left,bottom-top))
                frame[top:bottom, left:right]=frame_face
        # Write the resulting image to the output video file
        print("Writing frame {} / {}".format(frame_number, length))
        output_movie.write(frame)
        frame=resize(frame)
        imgencode=cv2.imencode('.jpg',frame)[1]
        stringData=imgencode.tostring()
        yield (b'--frame\r\n'
            b'Content-Type: text/plain\r\n\r\n'+stringData+b'\r\n')

    input_movie.release()
    cv2.destroyAllWindows()
    complete_image=face_recognition.load_image_file('static/complete.jpg')
    complete_image=resize(complete_image)
    #转换成opencv中的BGR格式
    complete_image=complete_image[:, :,::-1]
    imgencode=cv2.imencode('.jpg',complete_image)[1]
    stringData=imgencode.tostring()
    yield (b'--frame\r\n'
            b'Content-Type: text/plain\r\n\r\n'+stringData+b'\r\n')

def faceswap_picture(original_image,be_swapped_image,swap_image):
    swap_face=face_recognition.load_image_file(swap_image)
    swap_face_locations = face_recognition.face_locations(swap_face)[0]
    top_swap, right_swap, bottom_swap, left_swap = swap_face_locations
    swap=swap_face[top_swap:bottom_swap, left_swap:right_swap]

    if be_swapped_image == '':
        known_faces = []
    else :
        be_swapped_face = face_recognition.load_image_file(be_swapped_image)
        be_swapped_face_encodings = face_recognition.face_encodings(be_swapped_face)
        known_faces = be_swapped_face_encodings

    original_face=face_recognition.load_image_file(original_image)
    original_face_locations=face_recognition.face_locations(original_face)
    original_face_encodings=face_recognition.face_encodings(original_face)

    for face_num in range(len(original_face_encodings)):
        if(known_faces):
            match = True in (face_recognition.compare_faces(known_faces, original_face_encodings[face_num], tolerance=0.50))
        else:
            match = 1
        if(match):
            top, right, bottom, left = original_face_locations[face_num]
            original_face[top:bottom, left:right]=cv2.resize(swap,(right-left,bottom-top))
    #需要将RGB(face_recognition)改成BGR(opencv),这样才能在最后opencv写入图片时正常显示
    original_face = original_face[:,:,::-1]
    cv2.imwrite("output.jpg",original_face)
    
    original_face=resize(original_face)
    imgencode=cv2.imencode('.jpg',original_face)[1]
    stringData=imgencode.tostring()
    return (b'--frame\r\n'
            b'Content-Type: text/plain\r\n\r\n'+stringData+b'\r\n')