import configparser
import requests as req
import json


def send_photo(photo_url):
    cfg = configparser.ConfigParser()

    cfg.read('/function/code/cfg/keys.ini')
    token = cfg['telegram']['token']
    tg_url = 'https://api.telegram.org/bot{token}/{method}'

    chat_id = cfg['telegram']['chat_id']
    entities = [{'type': 'text_link', 'offset':0, 'length':4, 'url':photo_url}]

    r_send = req.post(tg_url.format(token = token, method = 'sendPhoto'), 
    json = {'chat_id': chat_id, 'photo': photo_url, 'caption': 'Link\nКто это?', 'caption_entities':entities})


def handler(event, context):

    body = event['messages'][0]['details']['message']['body']
    print(body)

    names = event['messages'][0]['details']['message']['message_attributes']['string']['string_value']
    names = names[1:-1].split(', ')
    print(names)

    cfg = configparser.ConfigParser()
    cfg.read('/function/code/cfg/keys.ini')
    bucket = cfg['aws']['bucket_name']

    for name in names:
        photo_url = 'https://storage.yandexcloud.net/{bucket}/{key}'.format(bucket=bucket, key=name[1:-1])
        send_photo(photo_url)

    return {
        'statusCode': 200,
        'body': 'Hello World!',
    }
