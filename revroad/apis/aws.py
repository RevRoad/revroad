import hashlib
import io
import logging
import mimetypes
import requests
import tempfile

from boto3 import Session
from django.conf import settings
from django.utils import timezone
from PIL import Image, ExifTags


bucket = settings.S3_BUCKET
logger = logging.getLogger(__name__)

try:
    session = Session(profile_name=settings.AWS_PROFILE_NAME)
    s3 = session.client('s3')
except:
    logger.error('Error instantiating AWS services. AWS credentials might not be configured correctly. '
                 'http://docs.aws.amazon.com/general/latest/gr/aws-access-keys-best-practices.html')


def transfer_image_url_to_s3(url, make_jpeg=False, max_size=None, thumbnail_size=None, **kwargs):
    if url.startswith('{}/{}/{}'.format(s3.meta.endpoint_url, bucket, kwargs.get('path', ''))):
        # already in s3
        print('url already in s3', url)
        return url
    print('requesting', url)
    request = requests.get(url, headers={'User-Agent': settings.USER_AGENT}, timeout=15)
    content_type = request.headers['Content-Type']
    if 'image/' not in content_type:
        raise Exception('Not an image')
    image = io.BytesIO(request.content)
    if make_jpeg:
        image = convert_to_jpg(image, content_type)
        content_type = 'image/jpeg'
    if max_size:
        image = make_thumbnail(image, content_type, size=max_size)
    image_url, image_file_name = upload_file(image, content_type, **kwargs)
    image.seek(0)
    image_thumbnail = make_thumbnail(image, content_type, size=thumbnail_size)
    upload_file(image_thumbnail, content_type, file_name='{}-t'.format(image_file_name), **kwargs)
    return image_url


def upload_file(file_obj, content_type=None, path=None, file_name=None, existing_keys=None):
    if not content_type:
        content_type = file_obj.content_type
    if content_type.startswith('image/'):
        file_obj = rotate_img(file_obj, content_type)
    if not path:
        path = 'images/'
    file_obj.seek(0)
    file_data = file_obj.read()
    if not file_name:
        sha = hashlib.sha1()
        sha.update(file_data)
        file_name = sha.hexdigest()
    key = '{}{}'.format(path, file_name)
    if not existing_keys or key not in existing_keys:
        # print('uploading to s3', key)
        s3.put_object(Bucket=bucket, Body=file_data, Key=key, ACL='public-read', ContentType=content_type)
    return '{}/{}/{}'.format(s3.meta.endpoint_url, bucket, key), file_name


def convert_to_jpg(image_file, content_type):
    if content_type == 'image/png':
        pillow_image = Image.open(image_file)
        pillow_image = pillow_image.convert('RGB')
        image_file = io.BytesIO()
        pillow_image.save(image_file, 'JPEG')
    return image_file


def rotate_img(image_file, content_type):
    try:
        pillow_image = Image.open(image_file)
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = dict(pillow_image._getexif().items())
        if exif[orientation] in (3, 6, 8):
            if exif[orientation] == 3:
                pillow_image = pillow_image.rotate(180, expand=True)
            elif exif[orientation] == 6:
                pillow_image = pillow_image.rotate(270, expand=True)
            elif exif[orientation] == 8:
                pillow_image = pillow_image.rotate(90, expand=True)
            image_file_io = io.BytesIO()
            pillow_image.save(image_file_io, _get_format(content_type))
            pillow_image.close()
            return image_file_io
        else:
            return image_file
    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        return image_file


def _get_format(content_type):
    fmt = mimetypes.guess_extension(content_type, strict=False).replace('.', '').upper()
    return {
        'JPG': 'JPEG',
        'JPE': 'JPEG',
    }.get(fmt, fmt)


def make_thumbnail(image_file, content_type, size=None):
    if not size:
        size = (700, 500)
    pillow_image = Image.open(image_file)
    pillow_image.thumbnail(size)
    if content_type == 'image/jpeg':
        pillow_image = pillow_image.convert('RGB')
    image_file = io.BytesIO()
    # print('contnet_type', content_type, _get_format(content_type))
    pillow_image.save(image_file, _get_format(content_type))
    return image_file


def list_objects(prefix=''):
    try:
        return s3.list_objects(Bucket=bucket, Prefix=prefix).get('Contents', [])
    except:
        return []
