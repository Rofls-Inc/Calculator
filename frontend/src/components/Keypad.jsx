const ROWS = [
  [
    { label: "C", action: "clear", variant: "danger", aria: "Очистить" },
    { label: "(", insert: "(" },
    { label: ")", insert: ")" },
    { label: "⌫", action: "backspace", aria: "Удалить символ" },
  ],
  [
    { label: "7", insert: "7" },
    { label: "8", insert: "8" },
    { label: "9", insert: "9" },
    { label: "÷", insert: "/", variant: "operator", aria: "Разделить" },
  ],
  [
    { label: "4", insert: "4" },
    { label: "5", insert: "5" },
    { label: "6", insert: "6" },
    { label: "×", insert: "*", variant: "operator", aria: "Умножить" },
  ],
  [
    { label: "1", insert: "1" },
    { label: "2", insert: "2" },
    { label: "3", insert: "3" },
    { label: "−", insert: "-", variant: "operator", aria: "Вычесть" },
  ],
  [
    { label: "0", insert: "0" },
    { label: ".", insert: "." },
    { label: "=", action: "submit", variant: "primary", aria: "Посчитать" },
    { label: "+", insert: "+", variant: "operator", aria: "Сложить" },
  ],
];


function Keypad({ disabled, loading, onInsert, onClear, onBackspace, onSubmit, onToggleSign }) {
  const handle = (key) => {
    if (key.insert) onInsert(key.insert);
    else if (key.action === "clear") onClear();
    else if (key.action === "backspace") onBackspace();
    else if (key.action === "submit") onSubmit();
  };

  // Keep focus in the expression field so typing continues to work after a click.
  const keepFocus = (event) => event.preventDefault();

  return (
    <div className="keypad">
      <div className="keypad__extras">
        <span className="section-label">доп.</span>
        <button
          type="button"
          className="key key--small"
          onMouseDown={keepFocus}
          onClick={onToggleSign}
          disabled={disabled}
          aria-label="Сменить знак"
        >
          ±
        </button>
      </div>

      <div className="keypad__grid">
        {ROWS.flat().map((key) => {
          const isSubmit = key.action === "submit";
          const className = `key${key.variant ? ` key--${key.variant}` : ""}${
            isSubmit && loading ? " key--busy" : ""
          }`;

          return (
            <button
              key={key.label}
              type="button"
              className={className}
              onMouseDown={keepFocus}
              onClick={() => handle(key)}
              disabled={disabled}
              aria-label={key.aria}
              aria-busy={isSubmit && loading ? true : undefined}
            >
              {isSubmit && loading ? <span className="spinner" aria-hidden="true" /> : key.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}


export default Keypad;
