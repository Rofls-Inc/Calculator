import { describeApiError, formatResult, formatTime, groupByDay } from "../lib/format.js";
import { bracketStats, tokenize } from "../lib/tokenize.js";


function HistoryPanel({ items, status, query, activeKey, onQueryChange, onPick }) {
  const normalizedQuery = query.trim().toLowerCase();
  const visible = normalizedQuery
    ? items.filter((item) => item.expression.toLowerCase().includes(normalizedQuery))
    : items;
  const groups = groupByDay(visible);

  return (
    <aside className="history" aria-label="История вычислений">
      <header className="history__header">
        <span className="section-label section-label--strong">
          История · {items.length}
        </span>
        {/* «очистить» is intentionally absent: the API contract has no DELETE /history. */}
      </header>

      <label className="history__search">
        <span aria-hidden="true">⌕</span>
        <input
          type="search"
          value={query}
          onChange={(event) => onQueryChange(event.target.value)}
          placeholder="поиск по выражению"
          aria-label="Поиск по выражению"
        />
      </label>

      <div className="history__list">
        {status === "unavailable" && items.length === 0 && (
          <p className="history__empty">
            история недоступна — backend не отвечает или эндпоинт ещё не реализован
          </p>
        )}

        {status !== "unavailable" && items.length === 0 && (
          <p className="history__empty">
            <span className="history__prompt">›</span> введите выражение — первая запись
            появится здесь
          </p>
        )}

        {items.length > 0 && visible.length === 0 && (
          <p className="history__empty">ничего не найдено</p>
        )}

        {groups.map((group) => (
          <section key={group.label} className="history__group">
            <h3 className="history__day">{group.label}</h3>
            {group.items.map((item) => (
              <HistoryItem
                key={item.key}
                item={item}
                active={item.key === activeKey}
                onPick={onPick}
              />
            ))}
          </section>
        ))}
      </div>

      <footer className="history__footer">
        <div>клик — подставить выражение</div>
        <div>⇧клик — подставить результат</div>
      </footer>
    </aside>
  );
}


function HistoryItem({ item, active, onPick }) {
  const isError = item.kind === "error";

  const handleClick = (event) => {
    onPick(item, { useResult: event.shiftKey && !isError });
  };

  return (
    <button
      type="button"
      className={`history-item${active ? " history-item--active" : ""}${
        isError ? " history-item--error" : ""
      }`}
      onClick={handleClick}
      title={isError ? "Клик — вернуть выражение для правки" : "Клик — выражение, ⇧клик — результат"}
    >
      <div className="history-item__top">
        <span className="history-item__expression">{item.expression}</span>
        <time className="history-item__time" dateTime={item.created_at}>
          {formatTime(item.created_at)}
        </time>
      </div>
      <div className="history-item__bottom">
        {isError
          ? describeApiError(item.error, bracketStats(tokenize(item.expression)))
          : `= ${formatResult(item.result).display}`}
      </div>
    </button>
  );
}


export default HistoryPanel;
