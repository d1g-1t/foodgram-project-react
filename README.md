Проект **"Продуктовый помощник"** - приложение для гурманов с обширной базой кулинарных рецептов. Позволяет пользователям создавать и публиковать свои рецепты, сохранять любимые рецепты, подписываться на других пользователей, а также формировать и скачивать списки покупок для приготовления рецептов.

**Деплой на удаленный сервер.**

**1. Клонируем проект.**
```
git clone git@github.com:d1g-1t/foodgram-project-react.git
```

**2. Заходим на удаленный сервер.**
```
ssh user@server_ip
```

**3. Устанавливаем Docker.**
Обновляем apt.
```
sudo apt-get update
```

**Устанавливаем пакеты для работы с HTTPS.**
```
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
```

**Добавляем ключ GPG Docker.**
```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
```

**Устанавливаем репозиторий Docker.**
```
echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

**Обновляем список пакетов.**
```
sudo apt-get update
```

**Устанавливаем Docker.**
```
sudo apt-get install docker-ce docker-ce-cli containerd.io
```

**Cоздаем и переходим в папку проекта.**
```
mkdir foodgram && cd foodgram/
```
В папке foodgram располагаем файлы docker-compose.yml, nginx.conf и .env.

**Запускаем проект.**
```
docker-compose.production.yml.
```

**Для корректной работы после запуска контейнеров необходимо провести миграции, импортировать базу данных ингредиентов, собрать статику и создать суперпользователя.**
```
docker exec -it <имя_контейнера_бекенда> python manage.py migrate

docker exec -it <имя_контейнера_бекенда> python manage.py db_import

docker exec -it <имя_контейнера_бекенда> python manage.py collectstatic --no-input

docker exec -it <имя_контейнера_бекенда> python manage.py createsuperuser
```

**API проекта будет доступно по локальному адресу: http://localhost/api/**

**Документация проекта будет доступен по локальному адресу: http://localhost/api/docs/redoc.html**

**Проект доступен для теста по адресу: https://foodgram-project.bounceme.net**

**Документация к API (примеры запросов, ответов и тд.) доступна по адресу: https://foodgram-project.bounceme.net/api/docs/redoc.html**
