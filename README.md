# nosql_template

После клонирования репозитория, перейти в папку репозитория, а затем

```shell
docker compose build --no-cache && docker compose up -d
```

После этого сайт будет доступен на `http://localhost:2026`

В проекте реализована полноценная регистрация и авторизация. Но для соответствия правилам при первом запуске автоматически создаются два отладочных аккаунта:

| Роль  | Логин   | Пароль    |
|-------|---------|-----------|
| user  | `user`  | `user1234`  |
| admin | `admin` | `admin1234` |

Администратор может редактировать и удалять любые публикации.

При смене email или восстановлении пароля, письма публикуются в логи. Т.е. посмотреть их можно с помощью команды `docker compose logs backend`

## Предварительная проверка заданий

<a href=" ./../../../actions/workflows/1_helloworld.yml" >![1. Согласована и сформулирована тема курсовой]( ./../../actions/workflows/1_helloworld.yml/badge.svg)</a>

<a href=" ./../../../actions/workflows/2_usecase.yml" >![2. Usecase]( ./../../actions/workflows/2_usecase.yml/badge.svg)</a>

<a href=" ./../../../actions/workflows/3_data_model.yml" >![3. Модель данных]( ./../../actions/workflows/3_data_model.yml/badge.svg)</a>

<a href=" ./../../../actions/workflows/4_prototype_store_and_view.yml" >![4. Прототип хранение и представление]( ./../../actions/workflows/4_prototype_store_and_view.yml/badge.svg)</a>

<a href=" ./../../../actions/workflows/5_prototype_analysis.yml" >![5. Прототип анализ]( ./../../actions/workflows/5_prototype_analysis.yml/badge.svg)</a>

<a href=" ./../../../actions/workflows/6_report.yml" >![6. Пояснительная записка]( ./../../actions/workflows/6_report.yml/badge.svg)</a>

<a href=" ./../../../actions/workflows/7_app_is_ready.yml" >![7. App is ready]( ./../../actions/workflows/7_app_is_ready.yml/badge.svg)</a>
