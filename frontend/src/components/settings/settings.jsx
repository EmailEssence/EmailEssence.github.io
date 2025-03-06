import "./settings.css";

export function Settings ({
  isChecked,
  handleToggleSummariesInInbox,
  emailFetchInterval,
  handleSetEmailFetchInterval,
  theme,
  handleSetTheme,
}) {
  return (
    <div className="settings">
      <h1>Settings</h1>
      <SummariesInInbox
        isChecked={isChecked}
        onToggle={handleToggleSummariesInInbox}
      />
      <EmailFetchInterval
        emailFetchInterval={emailFetchInterval}
        onSetEmailFetchInterval={handleSetEmailFetchInterval}
      />
      <Theme
        theme={theme}
        onSetTheme={handleSetTheme}
      />
    </div>
  );
}

// component that renders the summary toggle switch for enabling/disabling summaries in the inbox
export function SummariesInInbox({ isChecked, onToggle }) {
  return (
    <div className="settings-block">
      <h2>Summaries in Inbox</h2>
      <label className="switch">
        <input type="checkbox" checked={isChecked} onChange={onToggle} /> 
        <span className="toggle"></span>
      </label>
    </div>
  );
}

// component that renders the email fetch interval slider
export function EmailFetchInterval({ emailFetchInterval, onSetEmailFetchInterval }) {
  return (
    <div className="settings-block email-fetch-interval">
      <div className="header-container">
        <h2 className="header">Email Fetch Interval</h2>
        <p className="metric">(seconds)</p>
      </div>
      <input
        className="slider"
        type="range"
        min="0"
        max="600"
        step="5"
        value={emailFetchInterval}
        onChange={(e) => onSetEmailFetchInterval(e.target.value)}
      />
      <p className="count-display">{emailFetchInterval}</p>
    </div>
  );
}

// component that renders the buttons to switch between different themes
export function Theme({ theme, onSetTheme }) {
  const themes = ["light", "system", "dark"]; //array of themes

  //function to handle theme change
  const handleThemeChange = (newTheme) => {
    onSetTheme(newTheme);
    if (newTheme === "dark") {
      document.body.classList.add("dark-mode");
    } else {
      document.body.classList.remove("dark-mode");
    }
  };

  return (
    <div className="settings-block">
      <h2>Theme</h2>
      <div className="theme-toggle-group">
        {themes.map((t) => ( //renders the theme buttons
          <button
            key={t}
            className={`theme-toggle-item ${theme === t ? "selected" : ""}`}
            onClick={() => handleThemeChange(t)}
          >
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>
    </div>
  );
}
