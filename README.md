# SecDev Groups Activities

API менеджмента групп пользователей по активностям с session-based authN, authZ

## Контейнеры

- Контейнер c API - `studygroups-api`
- Контейнер с PgSQL - `studygroups-db`
- Контейнер с Nginx api GW - `studygroups-api-gateway`

Миграции накатываются вместе с `studygroups-api`, после доступности `studygroups-db` по health-check

```bash
docker compose up -d
```

## Endpoints

Посмотреть актуальную спецификацию и описание endpoint-ов можно в

**[Postman Workspace](https://www.postman.com/fluxconfig/hse-secdev-groupactivities)**


## Быстрый старт
```bash
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

## Ритуал перед PR
```bash
pytest tests/ -v
pre-commit run --all-files
```

## Тесты
```bash
pytest tests/ -v
```

## CI
В репозитории настроен workflow **CI** (GitHub Actions) — required check для `main`.
Badge добавится автоматически после загрузки шаблона в GitHub.
