
from flask import Flask,session,render_template,request,redirect,url_for,Response
from capture import CameraSwap
import os,tempfile
import face_recognition
from faceswap import *

ALLOWED_pic_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_vid_EXTENSIONS = {'mp4','avi','wmv','mpg','mpeg','mov','rm','ram','swf','flv'}


app = Flask(__name__)
app.secret_key = "level5"
camera = None

def allowed_pic_file(filename):#判断filename是否是允许的图片文件格式
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_pic_EXTENSIONS

def allowed_vid_file(filename):#判断filename是否是允许的视频文件格式
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_vid_EXTENSIONS


@app.route('/',methods=['GET','POST'])
def menu():#主菜单
    if request.method == 'POST':
        if 'picture_change_face_btn' in request.form:
            return redirect(url_for('pcf'))
        elif 'video_change_face_btn' in request.form:
            return redirect(url_for('vcf'))
        elif 'camera_change_face_btn' in request.form:
            return redirect(url_for('ccf'))
    return render_template('menu.html')

@app.route('/vcf',methods=['GET','POST'])
def vcf():
    if request.method == 'POST':
        if 'enter_btn' in request.form:
            if 'original_video' not in request.files:
                return '<script>alert("原视频不可为空");location.href="/vcf";</script>'
            original_video = request.files['original_video']
            if original_video.filename=='':
                return '<script>alert("原视频不可为空");location.href="/vcf";</script>'
            if not(original_video and allowed_vid_file(original_video.filename)):
                return '<script>alert("上传的原视频文件格式不正确");location.href="/vcf";</script>'
            temp_path=tempfile.mkdtemp()
            video_path = os.path.join(temp_path,original_video.filename)
            original_video.save(video_path)

            original_face_path=''
            if 'original_face' not in  request.files:
                original_face = ''
            else:
                original_face = request.files['original_face']
                if original_face.filename=='':
                    original_face=''
                if original_face and allowed_pic_file(original_face.filename)==0:#不符合文件名格式
                    '<script>alert("上传被换的人脸图片文件格式不正确");location.href="/vcf";</script>'
            if(original_face and allowed_pic_file(original_face.filename)):
                original_face_path = os.path.join(temp_path,original_face.filename)
                original_face.save(original_face_path)
            if not (original_face=='' or 
                face_recognition.face_locations(face_recognition.load_image_file(original_face))):
                return '<script>alert("被换的人脸图片中没有检测到人脸,如果想将视频中人脸全部替换,无须上传该文件");location.href="/vcf";</script>'

            if 'swap_face' not in request.files:
                return '<script>alert("换入的人脸图片不可为空");location.href="/vcf";</script>'
            swap_face = request.files['swap_face']
            if swap_face.filename=='':
                return '<script>alert("换入的人脸图片不可为空");location.href="/vcf";</script>'
            if not(swap_face and allowed_pic_file(swap_face.filename)):
                return '<script>alert("上传换入的人脸图片文件格式不正确");location.href="/vcf";</script>'
            swap_face_path = os.path.join(temp_path,swap_face.filename)
            swap_face.save(swap_face_path)
            if not face_recognition.face_locations(face_recognition.load_image_file(swap_face)):
                return '<script>alert("换入的人脸图片中没有检测到人脸,请重新上传");location.href="/vcf";</script>'

            session['original_video']=video_path
            session['original_face']=original_face_path
            session['swap_face']=swap_face_path

            # swap_face=face_recognition.load_image_file(swap_face_path)
            # original_face=face_recognition.load_image_file(original_face_path)
            return render_template('faceswap_video.html')
        if 'back_btn' in request.form:
            return redirect(url_for('menu'))
    return render_template('vcf.html')

@app.route('/pcf',methods=['GET','POST'])
def pcf():
    global picture_index
    if request.method == 'POST':
        if 'enter_btn' in request.form:
            if 'original_face' not in request.files:
                return '<script>alert("原图片不可为空");location.href="/pcf";</script>'
            original_face = request.files['original_face']
            if original_face.filename=='':
                return '<script>alert("原图片不可为空");location.href="/pcf";</script>'
            if not(original_face and allowed_pic_file(original_face.filename)):
                return '<script>alert("上传的原图片文件格式不正确");location.href="/pcf";</script>'
            temp_path=tempfile.mkdtemp()
            original_face_path = os.path.join(temp_path,original_face.filename)
            original_face.save(original_face_path)
            if not face_recognition.face_locations(face_recognition.load_image_file(original_face)):
                return '<script>alert("原图片中没有检测到人脸");location.href="/pcf";</script>'

            be_swapped_face_path=''
            if 'be_swapped_face' not in  request.files:
                be_swapped_face = ''
            else:
                be_swapped_face = request.files['be_swapped_face']
                if be_swapped_face.filename=='':
                    be_swapped_face=''
                if be_swapped_face and allowed_pic_file(be_swapped_face.filename)==0:#不符合文件名格式
                    '<script>alert("上传被换的人脸图片文件格式不正确");location.href="/pcf";</script>'
            if(be_swapped_face and allowed_pic_file(be_swapped_face.filename)):
                be_swapped_face_path = os.path.join(temp_path,be_swapped_face.filename)
                be_swapped_face.save(be_swapped_face_path)
            if not (be_swapped_face=='' or 
                face_recognition.face_locations(face_recognition.load_image_file(be_swapped_face))):
                return '<script>alert("被换的人脸图片中没有检测到人脸,如果想将图片中人脸全部替换,无须上传该文件");location.href="/pcf";</script>'

            if 'swap_face' not in request.files:
                return '<script>alert("换入的人脸图片不可为空");location.href="/pcf";</script>'
            swap_face = request.files['swap_face']
            if swap_face.filename=='':
                return '<script>alert("换入的人脸图片不可为空");location.href="/pcf";</script>'
            if not(swap_face and allowed_pic_file(swap_face.filename)):
                return '<script>alert("上传换入的人脸图片文件格式不正确");location.href="/pcf";</script>'
            swap_face_path = os.path.join(temp_path,swap_face.filename)
            swap_face.save(swap_face_path)
            if not face_recognition.face_locations(face_recognition.load_image_file(swap_face)):
                return '<script>alert("换入的人脸图片中没有检测到人脸,请重新上传");location.href="/pcf";</script>'
            session['original_face']=original_face_path
            session['be_swapped_face']=be_swapped_face_path
            session['swap_face']=swap_face_path
            return render_template('faceswap_picture.html')
        if 'back_btn' in request.form:
            return redirect(url_for('menu'))
    return render_template('pcf.html')

@app.route('/ccf',methods=['GET','POST'])
def ccf():
    global camera
    if request.method=='POST':
        if 'enter_btn' in request.form:
            if camera == None:
                camera = CameraSwap()
            return render_template('camera_change_face.html')
        if 'back_btn' in request.form:
            if camera != None:
                camera.release()
                camera = None
            return redirect(url_for('menu'))
    return render_template("ccf.html")

@app.route('/camera_change_face',methods=['GET','POST'])
def camera_change_face():
    try:
        return Response(camera.one_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        return Response('static/404.png', mimetype='image/jpeg')

@app.route('/faceswap_video_response',methods=['GET','POST'])
def faceswap_video_response():
    try:
        return Response(faceswap_video(session['original_video'],session['original_face'],session['swap_face']), mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        return Response('static/404.png', mimetype='image/jpeg')

@app.route('/faceswap_picture_response',methods=['GET','POST'])
def faceswap_picture_response():
    try:
        return Response(faceswap_picture(session['original_face'],session['be_swapped_face'],session['swap_face']), mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        return Response('static/404.png', mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(host = "0.0.0.0", debug=True)