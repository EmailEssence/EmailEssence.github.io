import { useEffect, useState } from "react";
import { baseUrl } from "../../../emails/emailHandler";
import "./settings.css";

export function Settings({
  isChecked,
  handleToggleSummariesInInbox,
  emailFetchInterval,
  handleSetEmailFetchInterval,
  theme,
  handleSetTheme,
}) {
  const handleLogout = () => {
    localStorage.removeItem("auth_token");
    window.location.href = "/login";
  };

  const handleDeleteAccount = async() => {
    //confirm if the user wants to delete their account
    if (!window.confirm("Are you sure you want to delete your account? This action is permanent and cannot be undone.")) return;
    try{
      const profile = await fetchUserProfile();
      const userId = profile.google_id
      await deleteUserById(userId);

      localStorage.removeItem("auth_token");
      window.location.href = "/login";
    } catch (error) {
      console.error("Failed to delete account:", error);
      alert("Failed to delete account. Please try again later.");
    };
  }

  const isDarkTheme = useSystemTheme();
  // useEffect that sets the dark mode class when the theme is set to system
  useEffect(() => {
    if (theme === "system") {
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
      <Theme theme={theme} onSetTheme={handleSetTheme} />
      <div className="settings-account-actions">
        <Logout onLogout={handleLogout} />
        <DeleteAccount onDelete={handleDeleteAccount} />
      </div>
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
export function EmailFetchInterval({
  emailFetchInterval,
  onSetEmailFetchInterval,
}) {
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
      const isDarkTheme = window.matchMedia(
        "(prefers-color-scheme: dark)"
      ).matches;
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
        {themes.map(
          (
            t //renders the theme buttons
          ) => (
            <button
              key={t}
              className={`theme-toggle-item ${theme === t ? "selected" : ""}`}
              onClick={() => handleThemeChange(t)}
            >
              {t.charAt(0).toUpperCase() + t.slice(1)}
            </button>
          )
        )}
      </div>
    </div>
  );
}

export function Logout({ onLogout }) {
  return (
    <button className="logout" onClick={onLogout}>
      <span className="logout-text">Logout</span>
    </button>
  );
}

export function DeleteAccount({ onDelete }) {
  return (
    <button className="delete-account" onClick={onDelete}>
      <span className="delete-account-text">Delete Account</span>
    </button>
  );
}

const useSystemTheme = () => {
  const getCurrentTheme = () =>
    window.matchMedia("(prefers-color-scheme: dark)").matches;
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

//  @router.get("/me"), gets current users profile, Retrieves the authenticated user's profile
export const fetchUserProfile = async () => {
  const token = localStorage.getItem("auth_token");
  const response = await fetch(`${baseUrl}/user/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch users profile ${response.status}`);
  }
  return response.json();
};

// @router.get("/preferences"), gets the user preferences, Retrieves the authenticated user's preferences settings
export const fetchUserPreferences = async () => {
  const token = localStorage.getItem("auth_token");
  const response = await fetch(`${baseUrl}/user/preferences`, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch user preferences ${response.status}`);
  }
  return response.json();
};

// @router.put("/preferences"), updates the user preferences, Updates the authenticated user's preferences settings
export const updateUserPreferences = async () => {
  const token = localStorage.getItem("auth_token");
  const response = await fetch(`${baseUrl}/user/preferences`, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });
  if (!response.ok) {
    throw new Error(`Failed to update user preferences ${response.status}`);
  }
  return response.json();
};

// @router.get ("/user_id"). gets user by ID, retrieves user information by user ID
export const fetchUserById = async () => {
  const token = localStorage.getItem("auth_token");
  const response = await fetch(`${baseUrl}/user/${user_id}`, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch user by ID ${response.status}`);
  }
  return response.json();
};

// @router.put("/user_id"), updates user, updates user information by user ID
export const updateUserById = async (user_id) => {
  const token = localStorage.getItem("auth_token");
  const response = await fetch(`${baseUrl}/user/${user_id}`, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });
  if (!response.ok) {
    throw new Error(`Failed to update user by ID ${response.status}`);
  }
  return response.json();
};

// @router.delete( "/user_id"), deletes user, deletes user account by user ID
export const deleteUserById = async (user_id) => {
  const token = localStorage.getItem("auth_token");
  
  const response = await fetch(`${baseUrl}/user/${user_id}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });
  if (!response.ok) {
    throw new Error(`Failed to delete user by ID ${response.status}`);
  }
  return response.json();
};

// function saves the user preferences to the backend
export const saveUserPreferences = async (user_id, userPreferences) => {
  const token = localStorage.getItem("auth_token");
  const response = await fetch(
    `${baseUrl}/user/${user_id}/preferences`,
    {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify(userPreferences),
    }
  );
  if (!response.ok) {
    throw new Error(`Failed to fetch ${response.status}`);
  }
  return response.json();
};
