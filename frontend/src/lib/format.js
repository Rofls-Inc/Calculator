const DISPLAY_DECIMALS = 4;


/** Round the backend's exact string result for the large display. */
export function formatResult(raw) {
  const value = Number(raw);

  if (!Number.isFinite(value)) {
    return { display: String(raw), exact: String(raw), rounded: false };
  }

  const display = Number.isInteger(value)
    ? String(value)
    : String(Number(value.toFixed(DISPLAY_DECIMALS)));

  return { display, exact: String(raw), rounded: display !== String(raw) };
}


export function formatTime(isoString) {
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" });
}


function startOfDay(date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate()).getTime();
}


/** Human label for the day a history item belongs to. */
export function dayLabel(isoString, now = new Date()) {
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) return "ранее";

  const diffDays = Math.round((startOfDay(now) - startOfDay(date)) / 86_400_000);

  if (diffDays === 0) return "сегодня";
  if (diffDays === 1) return "вчера";
  return date.toLocaleDateString("ru-RU", { day: "2-digit", month: "2-digit" });
}


export function groupByDay(items, now = new Date()) {
  const groups = [];
  const index = new Map();

  for (const item of items) {
    const label = dayLabel(item.created_at, now);
    let group = index.get(label);
    if (!group) {
      group = { label, items: [] };
      index.set(label, group);
      groups.push(group);
    }
    group.items.push(item);
  }

  return groups;
}


const ERROR_MESSAGES = {
  INVALID_EXPRESSION: "Некорректное выражение",
  DIVISION_BY_ZERO: "Деление на ноль",
  EXPRESSION_TOO_LONG: "Выражение длиннее 512 символов",
  EMPTY_EXPRESSION: "Пустое выражение",
  UNSUPPORTED_OP: "Операция не поддерживается",
};


export function describeApiError(error, brackets) {
  if (brackets && !brackets.balanced) {
    return brackets.errorKind === "extra-close"
      ? "Лишняя закрывающая скобка"
      : "Не хватает «)»";
  }
  return ERROR_MESSAGES[error?.code] || error?.message || "Ошибка вычисления";
}
