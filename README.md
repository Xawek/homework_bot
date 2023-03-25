# homework_bot
python telegram bot

# Перед запуском бота \ Before runing bot
    1. Создать и активировать виртуальное окружение \ Create and activate virtual environment
        Создать \ Create

            'python -m venv venv' - для \ for - Windows
            'python3 -m venv venv' - для \ for - Linux

        Активировать \ Activate

            'source venv/Scripts/activate' - для \ for - Windows
            'source venv/Bin/activate' - для \ for - Linux

    2. Установить модули и пакеты для проекта из файла requirements.txt \ Install modules and packages for project from file requirements.txt
        Установка \ Installation

            'pip install requirements.txt' - для \ for - Windows
            'pip3 install requirements.txt' - для \ for - Linux

    3. В директории бота создать файл '.env' (homework_bot\.env) \ Create file '.env' in the bot directory (homework_bot\.env)
        Создать фаил \ Create file

            'touch .env'

    4. В файле .env записать токены и id чата \ In .env file, write tokens and chat id
        Пример \ Example

            PRACTICUM_TOKEN=123_qWerTY
            TELEGRAM_TOKEN=123:QweRTy
            TELEGRAM_CHAT_ID=12345

        Уточнение \ More detailed

            PRACTICUM_TOKEN=<Токен_Яндекса\Yandex_Token>
            TELEGRAM_TOKEN=<Токен_Бота_Телеграмма\Telegram_Bot_Token>
            TELEGRAM_CHAT_ID=<id_Чата_Телеграмма\Telegram_Chat_id>


    Пункт номер следующий написан не будет. Так как пишу и думаю о том что в лучшем случае это прочтёт человек 5 и 99% шанс того что они умеют читать по русски, ну и тем более они понимают что тут и как делается ^_^
