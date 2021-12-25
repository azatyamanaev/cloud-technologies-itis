import configparser
import boto3
import base64
import requests as req
from PIL import Image
import io

def get_storage(cfg):
    cfg.read('/function/code/cfg/config')
    region = cfg['default']['region']

    cfg.read('/function/code/cfg/keys.ini')
    key_id = cfg['aws']['api_id']
    secret_key = cfg['aws']['api_key']

    session = boto3.session.Session()

    s3resource = session.resource(
        service_name='s3',
        endpoint_url='https://storage.yandexcloud.net',
        aws_access_key_id = key_id,
        aws_secret_access_key = secret_key,
        region_name=region
    )

    return s3resource

def get_faces(b64, cfg):
    s1 = '{"analyzeSpecs": [{"features": [{"type": "FACE_DETECTION"}],"content":"' + b64.decode('utf-8') + '"}]}'


    url = 'https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze'
    cfg.read('/function/code/cfg/keys.ini')
    secret_key = cfg['yacloud']['api_key']

    headers = {
            'Content-Type': "application/json", 
            'Authorization': "Api-Key {}".format(secret_key)
    }

    r = req.post(url, headers = headers, data = s1)
    detected = r.json()['results'][0]['results'][0]['faceDetection'] != {}
    if detected:
        faces = r.json()['results'][0]['results'][0]['faceDetection']['faces']
        return faces
    else:
        return []

def crop_faces(faces, data):
    stream = io.BytesIO(data)

    im = Image.open(stream)
    boxes = []

    for i in range(len(faces)):
        face = faces[i]
        ps = face['boundingBox']['vertices']
        box = (int(ps[0]['x']), int(ps[0]['y']), int(ps[2]['x']), int(ps[2]['y']))
        boxes.append(box)

    imgs = []    
    for i in range(len(boxes)):
        img = im.crop(boxes[i])
        imgs.append(img)
    return imgs

def upload_images(imgs, bucket, key):
    ind = key.rfind('_group-photo.jpg')
    names = []
    for i in range(len(imgs)):
        img = imgs[i]
        img.save('/tmp/img.jpg')
        name = '{pr_img}_group-photo/face{num}{ext}'.format(pr_img=key[:ind], num=i+1, ext='.jpg')
        names.append(name)
        with open('/tmp/img.jpg', 'rb') as img_file:
            bucket.upload_fileobj(img_file, name)
    return names

def get_mq(cfg):
    cfg.read('/function/code/cfg/config')
    region = cfg['default']['region']

    cfg.read('/function/code/cfg/keys.ini')
    key_id = cfg['aws']['api_id']
    secret_key = cfg['aws']['api_key']

    session = boto3.session.Session()

    sqs = session.resource(
        service_name='sqs',
        endpoint_url='https://message-queue.api.cloud.yandex.net',
        aws_access_key_id = key_id,
        aws_secret_access_key = secret_key,
        region_name=region
    )
    
    return sqs

def send_names_to_queue(sqs, names, key):
    q = sqs.get_queue_by_name(QueueName = 'faces-queue')
    
    q.send_message(MessageBody = 'Faces from {}'.format(key),
              MessageAttributes={
        'string': {
            'StringValue': str(names),
            'DataType': 'string'
        }
    })


def handler(event, context):    
    bucket_name = event['messages'][0]['details']['bucket_id']
    object_name = event['messages'][0]['details']['object_id']
    cfg = configparser.ConfigParser()
    res = get_storage(cfg)
    obj = res.ObjectSummary(bucket_name, object_name)
    data = obj.get()['Body'].read()
    

    faces = get_faces(base64.b64encode(data), cfg)
    if faces == []:
        print('faces not found')
    else:
        print('faces found')
        bucket = res.Bucket(bucket_name)
        imgs = crop_faces(faces, data)
        names = upload_images(imgs, bucket, object_name)
        send_names_to_queue(get_mq(cfg), names, object_name)



    return {
        'statusCode': 200,
        'body': 'Hello World!',
    }
