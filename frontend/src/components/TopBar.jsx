const STATUS_TEXT = {
  checking: "проверяем сервис…",
  online: "сервис доступен",
  offline: "сервис недоступен",
};


function TopBar({ backend }) {
  const { status } = backend;

  return (
    <header className="topbar">
      <div className="topbar__brand">
        <span className="topbar__logo">CALC</span>
      </div>

      <div className={`service service--${status}`} role="status" aria-live="polite">
        <span className="service__dot" aria-hidden="true" />
        <span>{STATUS_TEXT[status]}</span>
      </div>
    </header>
  );
}


export default TopBar;
