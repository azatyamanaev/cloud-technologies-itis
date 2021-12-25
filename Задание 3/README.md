# cloud-technologies-itis

## Настройка
1) Настройка функций описана в папках функций
2) Нужно создать телеграм бота

## Тестирование
1) Посылать в очередь сообщения типа:
q.send_message(MessageBody = 'some text',
                MessageAttributes={
      'string': {
            'StringValue': str(names),
            'DataType': 'string'
        }})
, где names - массив ключей обьектов(лиц людей). Пример - ["'test/2_group-photo/face1.jpg'", "'test/2_group-photo/face2.jpg'", "'test/2_group-photo/face3.jpg'", "'test/2_group-photo/face4.jpg'", "'test/2_group-photo/face5.jpg'", "'test/2_group-photo/face6.jpg'"], str(names) - массив, переведенный в строку

Один элемент массива - ключ обьекта

Примечание: каждый ключ обьекта дополнительно заключен в одинарные кавычки

2) Использовать приложение cloudphoto из репозитория (https://github.com/azatyamanaev/yandex-cloud-photo) и функцию cut-faces-from-image cloud function из репозитория (https://github.com/azatyamanaev/cloud-technologies-itis/tree/main/cut-faces-from-image)
