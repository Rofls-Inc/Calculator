import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { calculate, normalizeApiError } from "./api/client.js";
import ExpressionPanel from "./components/ExpressionPanel.jsx";
import HistoryPanel from "./components/HistoryPanel.jsx";
import Keypad from "./components/Keypad.jsx";
import TopBar from "./components/TopBar.jsx";
import { useBackendStatus } from "./hooks/useBackendStatus.js";
import { useHistory } from "./hooks/useHistory.js";
import { bracketStats, tokenize } from "./lib/tokenize.js";


const MAX_EXPRESSION_LENGTH = 512;


function App() {
  const [expression, setExpression] = useState("");
  const [status, setStatus] = useState("empty"); // empty | editing | loading | success | error | offline
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [activeKey, setActiveKey] = useState(null);
  const [query, setQuery] = useState("");

  const inputRef = useRef(null);
  const pendingCaret = useRef(null);
  const requestId = useRef(0);

  const backend = useBackendStatus();
  const history = useHistory();

  const tokens = useMemo(() => tokenize(expression), [expression]);
  const brackets = useMemo(() => bracketStats(tokens), [tokens]);

  // Restore the caret after programmatic edits (keypad, ±, history pick).
  useEffect(() => {
    if (pendingCaret.current === null || !inputRef.current) return;
    const position = pendingCaret.current;
    pendingCaret.current = null;
    inputRef.current.focus();
    inputRef.current.setSelectionRange(position, position);
  }, [expression]);

  const focusInput = () => inputRef.current?.focus();

  // The field is disabled while a request is in flight; give focus back once
  // it is enabled again so the keyboard keeps working after Enter.
  useEffect(() => {
    if (status !== "loading") focusInput();
  }, [status]);

  const updateExpression = useCallback((next, caret = null) => {
    const clean = next.replace(/[\r\n]+/g, "").slice(0, MAX_EXPRESSION_LENGTH);
    setExpression(clean);
    setStatus(clean.length === 0 ? "empty" : "editing");
    setResult(null);
    setError(null);
    pendingCaret.current = caret === null ? null : Math.min(caret, clean.length);
  }, []);

  const insert = (text) => {
    const field = inputRef.current;
    const start = field?.selectionStart ?? expression.length;
    const end = field?.selectionEnd ?? expression.length;
    updateExpression(expression.slice(0, start) + text + expression.slice(end), start + text.length);
  };

  const backspace = () => {
    const field = inputRef.current;
    const start = field?.selectionStart ?? expression.length;
    const end = field?.selectionEnd ?? expression.length;

    if (start !== end) {
      updateExpression(expression.slice(0, start) + expression.slice(end), start);
    } else if (start > 0) {
      updateExpression(expression.slice(0, start - 1) + expression.slice(start), start - 1);
    } else {
      focusInput();
    }
  };

  const clear = () => {
    requestId.current += 1; // drop any in-flight response
    updateExpression("", 0);
    setActiveKey(null);
  };

  const toggleSign = () => {
    const meaningful = tokens.filter((token) => token.type !== "space");
    const last = meaningful[meaningful.length - 1];

    // Nothing, or an operator / "(" at the end: start a negative number.
    if (!last || last.type === "op" || last.value === "(") {
      insert("-");
      return;
    }

    if (last.type !== "num") {
      focusInput();
      return;
    }

    const numberIndex = meaningful.indexOf(last);
    const previous = meaningful[numberIndex - 1];
    const beforePrevious = meaningful[numberIndex - 2];
    const previousIsUnaryMinus =
      previous?.value === "-" &&
      (!beforePrevious || beforePrevious.type === "op" || beforePrevious.value === "(");

    if (previousIsUnaryMinus) {
      const next = expression.slice(0, previous.start) + expression.slice(previous.start + 1);
      updateExpression(next, next.length);
    } else if (!previous || previous.type === "op" || previous.value === "(") {
      const next = expression.slice(0, last.start) + "-" + expression.slice(last.start);
      updateExpression(next, next.length);
    } else {
      // Binary context like "2 3" or ") 3": wrap so the minus stays unary.
      const end = last.start + last.value.length;
      const next = `${expression.slice(0, last.start)}(-${last.value})${expression.slice(end)}`;
      updateExpression(next, next.length);
    }
  };

  const submit = async () => {
    const trimmed = expression.trim();
    if (!trimmed || status === "loading") return;

    const id = ++requestId.current;
    setStatus("loading");
    setError(null);
    setResult(null);

    try {
      const data = await calculate(trimmed);
      if (id !== requestId.current) return;
      setResult({ value: String(data.result) });
      setStatus("success");
      setActiveKey(null);
      history.refresh();
    } catch (caught) {
      if (id !== requestId.current) return;
      const normalized = normalizeApiError(caught);
      setError(normalized);
      if (normalized.kind === "api") {
        setStatus("error");
        history.addLocalError(trimmed, normalized);
      } else {
        setStatus("offline");
        backend.refresh();
      }
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      submit();
    } else if (event.key === "Escape") {
      event.preventDefault();
      clear();
    }
  };

  // Typing anywhere on the page (except in another control) goes to the field.
  useEffect(() => {
    const onWindowKeyDown = (event) => {
      const target = event.target;
      const tag = target?.tagName;
      if (tag === "TEXTAREA" || tag === "INPUT" || tag === "BUTTON") return;
      if (event.metaKey || event.ctrlKey || event.altKey) return;

      if (event.key === "Enter") {
        event.preventDefault();
        submit();
      } else if (event.key === "Escape") {
        event.preventDefault();
        clear();
      } else if (event.key === "Backspace") {
        event.preventDefault();
        backspace();
      } else if (event.key.length === 1 && /[0-9+\-*/().\s]/.test(event.key)) {
        event.preventDefault();
        insert(event.key);
      }
    };

    window.addEventListener("keydown", onWindowKeyDown);
    return () => window.removeEventListener("keydown", onWindowKeyDown);
  });

  const pickHistory = (item, { useResult }) => {
    const value = useResult ? String(item.result) : item.expression;
    updateExpression(value, value.length);
    setActiveKey(item.key);
  };

  const pickExample = (example) => updateExpression(example, example.length);

  return (
    <div className="stage">
      <div className="backdrop" aria-hidden="true" />
      <main className="app">
        <TopBar backend={backend} />

        <div className="app__body">
          <div className="workspace">
            <ExpressionPanel
              expression={expression}
              status={status}
              result={result}
              error={error}
              tokens={tokens}
              brackets={brackets}
              inputRef={inputRef}
              onChange={(value) => updateExpression(value)}
              onKeyDown={handleKeyDown}
              onPickExample={pickExample}
            />

            <Keypad
              disabled={status === "loading"}
              loading={status === "loading"}
              onInsert={insert}
              onClear={clear}
              onBackspace={backspace}
              onSubmit={submit}
              onToggleSign={toggleSign}
            />
          </div>

          <HistoryPanel
            items={history.items}
            status={history.status}
            query={query}
            activeKey={activeKey}
            onQueryChange={setQuery}
            onPick={pickHistory}
          />
        </div>
      </main>
    </div>
  );
}


export default App;
