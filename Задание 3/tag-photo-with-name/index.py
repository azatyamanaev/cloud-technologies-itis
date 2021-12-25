import json
import configparser
import boto3
from botocore.exceptions import ClientError
import requests as req

def get_storage(cfg):
    region = cfg['default']['region']

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

def get_obj_url(msg):
    if 'reply_to_message' in msg.keys():
        reply_to_msg = msg['reply_to_message']
        keys = reply_to_msg.keys()
        if 'photo' in keys and 'caption_entities' in keys:
            caps = reply_to_msg['caption_entities']
            if len(caps) == 1 and caps[0]['type'] == 'text_link':
                url = caps[0]['url']
                return url
    return None

def change_obj_name(url, name, cfg):
    ar = url.split('/')
    bucket_name = ar[3]
    obj_name = '/'.join(ar[4:])

    res = get_storage(cfg)
    copy_source = {'Bucket': bucket_name, 'Key': obj_name}
    
    new_key = obj_name[:obj_name.rfind('/')+1] + name + '.jpg'

    bucket = res.Bucket(bucket_name)
    new_obj = bucket.Object(new_key)
    try:
        new_obj.copy(copy_source)
    
        old_obj = bucket.Object(obj_name)
        old_obj.delete()
        return True
    except ClientError as e:
        print(e)
        return False

def get_requested_name(msg):
    if 'reply_to_message' not in msg.keys():
        if 'entities' in msg.keys():
            entities = msg['entities']
            if len(entities) == 1 and entities[0]['type'] == 'bot_command' and msg['text'][:5] == '/find':
                name = msg['text'][6:]
                print('requested name - {}'.format(name))
                return name
    return None

def get_group_photos(r_name, cfg):
    res = get_storage(cfg)

    b_name = cfg['default']['bucket']
    bucket = res.Bucket(b_name)
    obs = bucket.objects.all()
    obs_filtered = list(filter(lambda x: '/{}.jpg'.format(r_name) in x.key, obs))
    group_photos = list(map(lambda x: x.key.split('/')[:2], obs_filtered))

    return group_photos

def send_reply_photo(photo_url, name, msg_id, album, cfg):
    token = cfg['telegram']['token']
    tg_url = 'https://api.telegram.org/bot{token}/{method}'

    chat_id = cfg['telegram']['chat_id']

    r_send = req.post(tg_url.format(token = token, method = 'sendPhoto'), 
    json = {'chat_id': chat_id, 'photo': photo_url, 
            'caption': 'Групповое фото из альбома {} на котором есть {}'.format(album, name),
            'reply_to_message_id': msg_id})

def send_not_found_response(r_name, msg_id, cfg):
    token = cfg['telegram']['token']
    tg_url = 'https://api.telegram.org/bot{token}/{method}'

    chat_id = cfg['telegram']['chat_id']

    r_send = req.post(tg_url.format(token = token, method = 'sendMessage'),
    json = {'chat_id': chat_id, 'text': 'Не найдено групповых фотографий на которых есть {}'.format(r_name), 
            'reply_to_message_id': msg_id})
     

def handler(event, context):
    st = event['body']

    body = json.loads(st)
    msg = body['message']
    print(msg)
    url = get_obj_url(msg)
    bucket_name = None
    obj_name = None

    r_name = get_requested_name(msg)
    cfg = configparser.ConfigParser()
    cfg.read('/function/code/cfg/config')

    if url:
        name = msg['text']
        status = change_obj_name(url, name, cfg)
        if status:
            print('successfully changed tagged photo with name {}'.format(name))
        else:
            print('failed to change object name - object not found')
    elif r_name:
        group_photos = get_group_photos(r_name, cfg)
        if len(group_photos) == 0:
            send_not_found_response(r_name, msg['message_id'], cfg)
        else:
            for photo in group_photos:
                photo_key = '/'.join(photo) + '.jpg'
                photo_url = 'https://storage.yandexcloud.net/{bucket}/{key}'.format(bucket=cfg['default']['bucket'], key=photo_key)
                send_reply_photo(photo_url, r_name, msg['message_id'], photo[0], cfg)
    else:
        print('no command was executed: wrong type of message')
    
    return {
        'statusCode': 200,
        'body': 'Hello World!',
    }
