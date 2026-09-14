# Calculator Service - Sprint 0

Командный учебный проект: веб-клиент отправляет арифметическое выражение в
сервис, сервис вычисляет результат, сообщает об ошибках и хранит историю
конкретного клиента в SQLite. Запуск локальный, Docker не используется.

## Что требуется реализовать

- GUI в браузере с вводом выражения и кнопками калькулятора.
- Вычисление только на backend, а не в React.
- Поддержка чисел, скобок, `+`, `-`, `*`, `/` и унарного минуса.
- Понятная ошибка для некорректного выражения и деления на ноль.
- Хранение всех успешных вычислений в SQLite.
- История только текущего клиента по cookie.
- Клик по записи истории возвращает выражение в поле ввода.
- Живое демо и резервная видеозапись.

## Технологии

| Часть | Технологии |
|---|---|
| Backend | Python 3.12, Flask, Flask-CORS |
| Вычислитель | собственный parser или безопасный allow-list Python AST |
| База | SQLite, Flask-SQLAlchemy |
| Frontend | React 19, Vite, Axios, CSS |
| Тесты | Pytest для backend; сборка frontend через Vite |
| Интеграция | GitHub Actions, pull requests |

Docker, MySQL и внешние облачные сервисы для Sprint 0 не нужны.

## Архитектура

```text
React :5173
    |
    | POST /api/v1/calculate
    | GET  /api/v1/history
    v
Flask :5000
    |-- calculator service
    |-- client cookie
    `-- history repository --> SQLite
```

Подробности находятся в [описании архитектуры](docs/architecture.md), а
согласованный формат запросов - в [контракте API](docs/api.md).

## Текущее состояние

В интеграционной ветке `dev` реализованы:

- Flask application factory и API `GET /health`, `POST /calculate`,
  `GET /history`;
- безопасный parser арифметических выражений без `eval`;
- проверка типа, пустого ввода, деления на ноль и лимита в 512 символов;
- SQLite-модель и repository для сохранения успешных вычислений;
- разделение истории клиентов по cookie `calculator_user_id`;
- React/Vite-интерфейс, подключённый к вычислению и истории;
- backend-набор из 127 проходящих тестов;
- GitHub Actions с запуском Pytest и сборкой frontend.

## Структура

```text
backend/
  app/
    api/             # HTTP endpoints
    models/          # SQLAlchemy models
    repositories/    # SQLite access
    services/        # expression parser and business logic
  run.py
frontend/
  src/
    api/             # Axios client
tests/               # Pytest tests
docs/                # architecture and API contract
.github/workflows/   # continuous integration
```

## Локальный запуск

### Backend - Windows PowerShell

Из корня проекта:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m backend.run
```

Проверка:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/v1/health
```

Ожидаемый ответ: `{"status":"ok"}`.

### Frontend

Во втором терминале:

```powershell
cd frontend
npm install
npm run dev
```

Открыть `http://127.0.0.1:5173`. Vite автоматически перенаправляет `/api` на
Flask. Локальный `.env` не нужен.

### Тесты

Из корня проекта, с активированным venv:
 
```powershell
python -m pytest
```
 
Форма `python -m pytest` обязательна: она добавляет корень проекта в
`sys.path`, и только так работает импорт `backend.app`. Команда `pytest` без
`python -m`, а также запуск из папки `tests`, завершатся ошибкой
`ModuleNotFoundError: No module named 'backend'`.
 
Состав набора:
 
| Файл | Что покрывает |
|---|---|
| `tests/test_health.py` | доступность `GET /api/v1/health` |
| `tests/test_calculator_service.py` | разбор выражений, унарные знаки, деление на ноль, отклонение Python-кода |
| `tests/test_calculate_api.py` | `POST /api/v1/calculate`: формат ответа, ошибки 400, лимит 512, cookie, устойчивость к мусорному вводу |
| `tests/test_history_api.py` | `GET /api/v1/history`: сортировка, разделение по клиентам, сохранность после перезапуска |
| `tests/test_repository.py` | модель `Calculation` и repository истории |
 
Тесты используют SQLite в памяти и не трогают рабочую базу в `instance/`.
Проверка сохранности истории между запусками создаёт временный файл базы,
который удаляется автоматически.

Полезные варианты запуска:
 
```powershell
python -m pytest -v # имя каждого теста отдельной строкой
python -m pytest tests/test_calculate_api.py # один файл
python -m pytest -k cookie # тесты, в имени которых есть cookie
python -m pytest -x # остановиться на первом падении
```

## Распределение работы

### Студент 1 - Backend: parser и calculate API

Ветка: `feature/calculator-engine`

Основные файлы:

- `backend/app/services/calculator.py`
- `backend/app/api/calculations.py`
- `docs/api.md`, если контракт уточняется

Задачи:

- реализовать вычислитель без сырого `eval`;
- проверить тип, пустую строку и лимит 512 символов;
- поддержать числа, скобки, `+`, `-`, `*`, `/`, унарные знаки;
- реализовать `POST /api/v1/calculate`;
- вернуть единый JSON для syntax error и division by zero;
- после объединения SQLite сохранять успешный результат через repository.

Готово, когда пример из задания считается, а мусорный ввод быстро возвращает
HTTP 400 и не роняет сервер.

Рекомендуемые коммиты:

```text
feat(calculator): implement safe expression parser
feat(api): implement calculate endpoint
fix(api): validate expression input
```

### Студент 2 - Data и local run: SQLite/history

Ветка: `feature/sqlite-history`

Основные файлы:

- `backend/app/models/`
- `backend/app/repositories/`
- `backend/app/api/history.py`
- `backend/app/__init__.py`
- `.gitignore` и раздел запуска README при необходимости

Задачи:

- создать модель `Calculation` по таблице из `docs/architecture.md`;
- создавать таблицы при старте приложения;
- реализовать repository: добавить вычисление и получить историю пользователя;
- создать безопасный случайный `calculator_user_id` cookie;
- реализовать `GET /api/v1/history` с сортировкой от новых к старым;
- проверить сохранение истории после перезапуска;
- передать Студенту 1 функцию repository для записи результата.

Готово, когда два браузерных клиента видят разные истории, а база появляется
автоматически в `instance/` и не попадает в Git.

Рекомендуемые коммиты:

```text
feat(database): add calculation model and SQLite setup
feat(history): add calculation repository
feat(api): implement client history endpoint
```

### Студент 3 - Frontend

Ветка: `feature/calculator-ui`

Основные файлы: `frontend/src/`.

Задачи:

- заменить стартовую страницу интерфейсом калькулятора;
- добавить текстовый ввод и кнопки цифр/операторов;
- отправлять строку в `POST /api/v1/calculate`;
- показывать результат, loading и сообщения об ошибках;
- получать `GET /api/v1/history`;
- сделать записи истории кликабельными;
- обеспечить удобное отображение длинного выражения.

Готово, когда пользователь выполняет весь сценарий задания только через GUI.

Рекомендуемые коммиты:

```text
feat(frontend): build calculator interface
feat(frontend): connect calculation API
feat(frontend): add clickable history
```

### Студент 4 - QA, CI и демонстрация

Ветка: `test/sprint-zero`

Основные файлы:

- `tests/`
- `.github/workflows/ci.yml`
- финальный раздел README

Задачи:

- покрыть parser, API, SQLite и разделение истории тестами;
- проверить пустой JSON, неверные скобки, `1/0`, текст и строку >512;
- обновлять тесты после объединения feature-веток;
- проверить CI, выполнить финальный smoke-test;
- подготовить сценарий живого демо и резервное видео.

Готово, когда CI зелёный и весь демонстрационный сценарий повторяется на чистой
машине по README.

Рекомендуемые коммиты:

```text
test(calculator): cover valid and invalid expressions
test(history): verify client isolation and persistence
ci: verify backend tests and frontend build
docs: add demonstration checklist
```

## Порядок интеграции

1. Участники выполняют свою часть в отдельных feature-ветках.
2. Pull request направляется в интеграционную ветку `dev`.
3. Все части проверяются совместно по контракту `docs/api.md`.
4. Перед финальным слиянием выполняются `python -m pytest` и
   `npm run build`.
5. После успешного CI ветка `dev` сливается в `main`.
6. Каждый pull request проверяет хотя бы один другой участник.

Не следует одновременно редактировать чужую основную папку без согласования.

## Definition of Done

- `python -m pytest` проходит;
- `npm run build` проходит;
- пример из задания возвращает результат;
- некорректные скобки и деление на ноль возвращают HTTP 400;
- сервер не падает на длинном или текстовом вводе;
- история сохраняется в SQLite и разделяется по клиентам;
- запись истории кликабельна во frontend;
- проект запускается по README без Docker;
- подготовлены живое демо и резервная видеозапись.
