# send-photo-to-tg-chat cloud function

## Связь между фотографиями лиц и оригинальной фотографией

Допустим, в бакете есть фотография(лицо) с ключом test/2_group-photo/face3.jpg
Обьект test/2_group-photo/face3.jpg, где test - альбом, 2_group-photo - папка с лицами,вырезанными из групповой фотографии 2_group-photo. Причем, в папке альбома должна лежать групповая фотография с именем 2_group-photo.jpg, т. е. в самом бакете должен быть обьект test/2_group-photo.jpg.

Расширение лиц и групповых фотографий должно быть .jpg

## Настройка облачной функции

1) Создать функцию
2) Указать среду исполнения python 3.9
3) Зайти в редактор кода
4) Добавить файл index.py из этого репозитория
5) Добавить папку cfg с файлом keys.ini из этого репозитория
6) Заполнить файл keys.ini своими данными, где [aws][bucket-name] - имя бакета, в котором лежат фотографии, [telegram][token] - token телеграм бота, [telegram][chat_id] - id чата с телеграм ботом
7) У сервисного аккаунта должны быть права storage.admin, editor, serverless.functions.invoker
8) У хранилища должен быть публичный доступ на чтение обьектов и на доступ к списку обьектов
9) Создать очередь с названием faces-queue
10) Создать триггер на Message Queue, указать очередь, сервисный аккаунт, размер группы сообщений - 1, функцию, созданную ранее
11) Посылать в очередь сообщения типа:
q.send_message(MessageBody = 'some text',
              MessageAttributes={
        'string': {
            'StringValue': str(names),
            'DataType': 'string'
        }
    })
, где names - массив ключей обьектов(лиц людей). Пример - ["'test/2_group-photo/face1.jpg'", "'test/2_group-photo/face2.jpg'", "'test/2_group-photo/face3.jpg'", "'test/2_group-photo/face4.jpg'", "'test/2_group-photo/face5.jpg'", "'test/2_group-photo/face6.jpg'"]

Один элемент массива - ключ обьекта\n
Примечание: каждый ключ обьекта дополнительно заключен в одинарные кавычки

