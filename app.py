from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import dotenv
from PIL import Image, ImageOps
from instagrapi import Client
import threading


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


def login_instagram():
    global g_instagram_client
    client = Client()
    try:
        client.login(instagram_username, instagram_password)
        g_instagram_client = client
        print("Logged in to Instagram")
    except Exception as e:
        print(f"Login failed: {e}")


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


def uploader(book_info, content, image_path):
    processed_image = process_image(image_path)
    # 유저가 책 정보를 입력한 경우
    if book_info:
        caption = f"{content}\n\n{book_info}"
    else:
        caption = content
    processed_image_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                        f"processed_{os.path.basename(image_path)}")
    processed_image.save(processed_image_path)
    upload_instagram(caption, processed_image_path)


@app.route('/', methods=['GET'])
def index():
    # 페이지 로딩 시 비동기로 로그인 작업 수행
    global g_instagram_client
    if not g_instagram_client:
        thread = threading.Thread(target=login_instagram)
        thread.start()

    # 세션에 저장된 최근 3개의 book_info를 불러옴
    recent_book_infos = session.get('recent_book_infos', [])
    return render_template('upload.html', recent_book_infos=recent_book_infos)


@app.route('/', methods=['POST'])
def upload():
    global g_instagram_client
    if not g_instagram_client:
        flash("Login failed. Try again.", "error")
        return redirect(url_for('index'))

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
