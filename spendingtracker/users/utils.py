import io
import os
import secrets

from PIL import Image
from botocore.exceptions import ClientError
from flask import url_for, current_app
from flask_mail import Message

from spendingtracker import s3_client


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pic', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    # i.save(picture_path)

    # https: // jdhao.github.io / 2019 / 07 / 06 / python_opencv_pil_image_to_bytes /
    buf = io.BytesIO()
    i.save(buf, format=f_ext.strip('.'))
    byte_img = buf.getvalue()

    try:
        s3_client.put_object(Body=byte_img,
                             Bucket=os.environ.get('S3_BUCKET_NAME'),
                             Key="flaskstatic/" + picture_fn,
                             ContentType=form_picture.mimetype)

    except ClientError as e:
        print(e)
        raise e

    return picture_fn


def show_image(avatar_name):
    img_url = None
    try:
        img_url = s3_client.generate_presigned_url('get_object',
                                                   Params={'Bucket': os.environ.get('S3_BUCKET_NAME'),
                                                           'Key': 'flaskstatic/' + avatar_name},
                                                   ExpiresIn=100)
    except Exception as e:
        print(e)
    return img_url


def send_reset_email(user):
    pass


#     token = user.get_reset_token()
#     msg = Message('Password Reset Request',
#                   sender='noreply@demo.com',
#                   recipients=[user.email])
#     msg.body = f'''To reset your password, visit the following link:
# {url_for('users.reset_token', token=token, _external=True)}
# If you did not make this request then simply ignore this email and no changes will be made.
# '''
#     mail.send(msg)

def allowed_file_ext(filename =None):
    if filename:
        filename = os.path.splitext(filename)[1]
        return filename in current_app.config['UPLOAD_EXTENSIONS']
