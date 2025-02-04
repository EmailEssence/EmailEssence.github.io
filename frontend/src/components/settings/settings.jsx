import {useState} from "react";
import "./settings.css";

export default function Settings() {
  return (
    <div className="settings">
      <h1>Settings</h1>
      <SummariesInInbox />
      <EmailFetchInterval />
      <Theme />
    </div>
  );
}

function SummariesInInbox() {
  //globalize
  const [isChecked, setIsChecked] = useState(false);
  const handleToggle = () => setIsChecked(!isChecked);

  return (
    <div className="settings-block">
      <h2>Summaries in Inbox</h2>
      <label className="switch">
        <input type="checkbox" checked={isChecked} onChange={handleToggle} />
        <span className="toggle"></span>
      </label>
    </div>
  );
}

function EmailFetchInterval() {
  return (
    <div className="settings-block email-fetch-interval">
      <h2>Email Fetch Interval</h2>
      <input
        className="slider"
        type="range"
        min="5"
        max="600"
        step="1"
        onInput={inputEvent =>
          (inputEvent.target.nextSibling.textContent = `${inputEvent.target.value} seconds`)
        }
      />
      <p>5 seconds</p>
    </div>
  );
}

function Theme() {
  const [theme, setTheme] = useState("system");
  const themes = ["light", "system", "dark"];

  return (
    <div className="settings-block">
      <h2>Theme</h2>
      <div className="theme-toggle-group">
        {themes.map(t => (
          <button
            key={t}
            className={`theme-toggle-item ${theme === t ? "selected" : ""}`}
            onClick={() => setTheme(t)}
          >
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>
    </div>
  );
}
