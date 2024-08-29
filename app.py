from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import os
import dotenv
from PIL import Image, ImageOps
from instagrapi import Client
import threading
import time
from datetime import datetime, timedelta

app = Flask(__name__)

dotenv.load_dotenv()

app.secret_key = os.getenv('FLASK_SECRET_KEY')
instagram_username = os.getenv('INSTAGRAM_USERNAME')
instagram_password = os.getenv('INSTAGRAM_PASSWORD')

app.config['UPLOAD_FOLDER'] = 'upload/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}


if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# 전역 변수로 로그인 상태 관리
g_instagram_client = None
g_last_login_time = None


def login_instagram():
    global g_instagram_client, g_last_login_time
    client = Client()
    try:
        client.login(instagram_username, instagram_password)
        g_instagram_client = client
        g_last_login_time = datetime.now()
        print("Logged in to Instagram")
    except Exception as e:
        print(f"Login failed: {e}")
        g_instagram_client = None
        g_last_login_time = None


def check_login_status():
    global g_instagram_client, g_last_login_time
    while True:
        current_time = datetime.now()
        # 24시간 간격으로 로그인 상태 확인
        if g_last_login_time is None or (current_time - g_last_login_time) > timedelta(days=1):
            print("Checking login status...")
            if g_instagram_client is None or not g_instagram_client.account_info():
                print("Login expired. Attempting to re-login...")
                login_instagram()
            else:
                g_last_login_time = current_time
                print("Login is still valid.")
        time.sleep(3600 * 10)  # 10시간 간격으로 함수 실행


# 비동기로 로그인 작업 수행 및 주기적 체크 시작
threading.Thread(target=login_instagram, daemon=True).start()
threading.Thread(target=check_login_status, daemon=True).start()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def process_image(image_path):
    image = Image.open(image_path)

    if image.size[0] != image.size[1]:
        image = ImageOps.pad(
            image, (max(image.size), max(image.size)), color='black')
    return image


def upload_instagram(client, caption, image_path):
    client.photo_upload(image_path, caption)


def uploader(client, book_info, content, image_path):
    processed_image = process_image(image_path)
    # 유저가 책 정보를 입력한 경우
    if book_info:
        caption = f"{content}\n\n{book_info}"
    else:
        caption = content
    processed_image_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                        f"processed_{os.path.basename(image_path)}")
    processed_image.save(processed_image_path)
    upload_instagram(client, caption, processed_image_path)


@app.route('/login_status', methods=['GET'])
def login_status():
    global g_instagram_client, g_last_login_time
    if g_instagram_client and g_last_login_time:
        return jsonify({
            'status': 'logged_in',
            'last_login': g_last_login_time.isoformat()
        })
    else:
        return jsonify({'status': 'logged_out'})


@app.route('/', methods=['GET'])
def index():
    # 세션에 저장된 최근 3개의 book_info를 불러옴
    recent_book_infos = session.get('recent_book_infos', [])
    return render_template('upload.html', recent_book_infos=recent_book_infos)


@app.route('/', methods=['POST'])
def upload():
    global g_instagram_client
    if not g_instagram_client:
        return jsonify({'status': 'error', 'message': "Not logged in to Instagram"}), 403
        # flash("Login failed. Try again.", "error")
        # return redirect(url_for('index'))

    book_info = request.form['book_info']
    content = request.form['content']
    image = request.files['image']

    # 필수 정보를 입력하지 않은 경우
    if not content:
        flash("Content is required.", "error")
        return redirect(url_for('index'))

    if not image or not allowed_file(image.filename):
        flash("Image is required.", "error")
        return redirect(url_for('index'))

    # 세션에 book_info를 저장 (최대 3개만 유지)
    recent_book_infos = session.get('recent_book_infos', [])
    if book_info not in recent_book_infos:
        recent_book_infos.insert(0, book_info)
        if len(recent_book_infos) > 3:
            recent_book_infos.pop()
        session['recent_book_infos'] = recent_book_infos

    if image and allowed_file(image.filename):
        filename = image.filename
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)

        uploader(g_instagram_client, book_info, content, image_path)

        flash("Upload success!", "success")
        return redirect(url_for('index'))

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
