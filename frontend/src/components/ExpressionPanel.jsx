import { useState } from "react";

import { describeApiError, formatResult } from "../lib/format.js";


const EXAMPLES = ["2*(3+4)", "144/12+7", "(12+22*7)/33"];


function HighlightedExpression({ tokens, errorPos }) {
  return (
    <>
      {tokens.map((token) => {
        const isError = errorPos !== null && token.start + 1 === errorPos;
        const className = `tok tok--${token.type}${isError ? " tok--error" : ""}`;
        return (
          <span key={token.start} className={className}>
            {token.value}
          </span>
        );
      })}
      {/* keeps the overlay one line tall even when the field is empty */}
      <span className="tok tok--space">{"\u200B"}</span>
    </>
  );
}


function CopyButton({ value }) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // Clipboard may be blocked outside secure contexts; ignore silently.
    }
  };

  return (
    <button type="button" className="chip chip--button" onClick={copy}>
      {copied ? "скопировано" : "копировать"}
    </button>
  );
}


function ExpressionPanel({
  expression,
  status,
  result,
  error,
  tokens,
  brackets,
  inputRef,
  onChange,
  onKeyDown,
  onPickExample,
}) {
  const isEmpty = expression.length === 0;
  const isError = status === "error";
  const showBracketError = isError && !brackets.balanced;
  const errorPos = showBracketError && brackets.errorKind === "extra-close" ? brackets.errorPos : null;

  const cardClass = [
    "expr-card",
    isEmpty && "expr-card--empty",
    isError && "expr-card--error",
    status === "loading" && "expr-card--loading",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <section className={cardClass} aria-label="Выражение">
      <header className="expr-card__header">
        <span className="section-label">Выражение</span>
        {!brackets.balanced && !isEmpty && (
          <span className="expr-card__note">
            скобки {brackets.close}/{brackets.open}
          </span>
        )}
      </header>

      <div className="expr-input">
        <span className="expr-input__prompt" aria-hidden="true">›</span>
        <div className="expr-input__field">
          <pre className="expr-input__overlay" aria-hidden="true">
            <HighlightedExpression tokens={tokens} errorPos={errorPos} />
          </pre>
          <textarea
            ref={inputRef}
            className="expr-input__textarea"
            value={expression}
            onChange={(event) => onChange(event.target.value)}
            onKeyDown={onKeyDown}
            placeholder="введите выражение"
            aria-label="Арифметическое выражение"
            rows={1}
            spellCheck={false}
            autoComplete="off"
            autoCapitalize="off"
            autoCorrect="off"
            disabled={status === "loading"}
            maxLength={512}
          />
        </div>
      </div>

      {showBracketError && brackets.errorPos !== null && (
        <div className="expr-position">▲ позиция {brackets.errorPos}</div>
      )}

      <div className="expr-card__divider" aria-hidden="true" />

      {isEmpty && (
        <div className="expr-footer expr-examples">
          <span>примеры:</span>
          {EXAMPLES.map((example) => (
            <button
              key={example}
              type="button"
              className="chip chip--example"
              onClick={() => onPickExample(example)}
            >
              {example}
            </button>
          ))}
        </div>
      )}

      {status === "editing" && (
        <div className="expr-footer expr-hint">Enter — посчитать · Esc — очистить</div>
      )}

      {status === "loading" && (
        <div className="expr-loading">
          <span className="expr-loading__url">POST /api/v1/calculate</span>
          <span className="expr-loading__progress">
            <span className="progress" aria-hidden="true">
              <span className="progress__bar" />
            </span>
            считаем…
          </span>
        </div>
      )}

      {status === "success" && result && <ResultBlock result={result} />}

      {status === "error" && error && (
        <div className="expr-error" role="alert">
          <span className="expr-error__message">{describeApiError(error, brackets)}</span>
          <span className="chip chip--code">
            {error.status ?? 400} · {error.code}
          </span>
        </div>
      )}

      {status === "offline" && error && (
        <div className="expr-error expr-error--offline" role="alert">
          <div>
            <div className="expr-error__message">
              {error.code === "NOT_IMPLEMENTED" ? "Ещё не реализовано" : "Сервис недоступен"}
            </div>
            <div className="expr-error__detail">
              {error.code === "NOT_IMPLEMENTED"
                ? "Backend отвечает, но POST /api/v1/calculate пока возвращает 501 — вычислитель ещё не готов."
                : `${error.message}. Проверьте, что backend запущен, и нажмите Enter ещё раз.`}
            </div>
          </div>
          <span className="chip chip--code">{error.status ?? "—"} · {error.code}</span>
        </div>
      )}
    </section>
  );
}


function ResultBlock({ result }) {
  const formatted = formatResult(result.value);

  return (
    <div className="expr-result">
      <div className="expr-result__meta">
        <span className="section-label">Результат</span>
        {formatted.rounded && (
          <span className="expr-result__exact">точно: {formatted.exact}</span>
        )}
      </div>
      <output className="expr-result__value" aria-live="polite">
        {formatted.display}
      </output>
      <CopyButton value={formatted.exact} />
    </div>
  );
}


export default ExpressionPanel;
