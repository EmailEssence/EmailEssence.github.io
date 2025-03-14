import React, { useEffect, useState } from 'react';
import "./settings.css";

export function Settings ({
  isChecked,
  handleToggleSummariesInInbox,
  emailFetchInterval,
  handleSetEmailFetchInterval,
  theme,
  handleSetTheme,
}) {
  const isDarkTheme = useSystemTheme();

  useEffect(() => {
    if (theme === 'system') {
      if (isDarkTheme) {
        document.body.classList.add("dark-mode");
      } else {
        document.body.classList.remove("dark-mode");
      }
    }
  }, [isDarkTheme, theme]);

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
        min="5"
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

  //function to handle theme change between light and dark through the buttons
  const handleThemeChange = (setTheme) => {
    onSetTheme(setTheme);
    if (setTheme === "dark") {
      document.body.classList.add("dark-mode");
    } else if (setTheme === "light") {
      document.body.classList.remove("dark-mode");
    } else if (setTheme === "system") {
      const isDarkTheme = window.matchMedia("(prefers-color-scheme: dark)").matches;
      if (isDarkTheme) {
        document.body.classList.add("dark-mode");
      } else {
        document.body.classList.remove("dark-mode");
      }
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

const useSystemTheme = () => {
  const getCurrentTheme = () => window.matchMedia("(prefers-color-scheme: dark)").matches;
  const [isDarkTheme, setIsDarkTheme] = useState(getCurrentTheme());

  const mqListener = (e) => {
    setIsDarkTheme(e.matches);
  };

  useEffect(() => {
    const darkThemeMq = window.matchMedia("(prefers-color-scheme: dark)");
    darkThemeMq.addListener(mqListener);
    return () => darkThemeMq.removeListener(mqListener);
  }, []);

  return isDarkTheme;
};

// need to test these
// my attempt at a function that gets the user preferences from the backend
const getUserPreferences = async (user_id) => {
  const response = await fetch(`http://localhost:8000/user/${user_id}/preferences`);
  if (!response.ok) {
    throw new Error(` failed to fetch ${response.status}`);
  }
  return response.json();
} 

// my attempt at a function saves the user preferences to the backend
const saveUserPreferences = async (userPreferences) => {
  const response = await fetch(`http://localhost:8000/user/${user_id}/preferences`, {
    method: 'PUT',
    headers: {'Content-Type':'application/json',},
    body: JSON.stringify(userPreferences),
  });
  if (!response.ok) {
    throw new Error(`failed to fetch ${response.status}`);
  }
  return response.json();
};


