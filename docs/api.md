# API contract

Base URL: `/api/v1`

## Health

`GET /health`

```json
{
  "status": "ok"
}
```

## Calculate

`POST /calculate`

Request:

```json
{
  "expression": "(12 + 22 * 7) / (33 + (12 * 3 - 8)) * 3"
}
```

Success, HTTP 200:

```json
{
  "result": "8.163934426229508"
}
```

Invalid input, HTTP 400:

```json
{
  "error": {
    "code": "INVALID_EXPRESSION",
    "message": "Expression contains a syntax error"
  }
}
```

The service supports decimal numbers, parentheses, unary plus/minus, and the
operators `+`, `-`, `*`, `/`. The maximum request expression length is 512.

## History

`GET /history`

Success, HTTP 200:

```json
{
  "items": [
    {
      "id": 1,
      "expression": "2 + 2",
      "result": "4",
      "created_at": "2026-09-13T18:30:00Z"
    }
  ]
}
```

The API identifies a browser by the `calculator_user_id` cookie. The frontend
must be able to click a history item and put its expression back into the input.
