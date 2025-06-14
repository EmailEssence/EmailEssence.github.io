import { useEffect, useState } from "react";
import { baseUrl } from "../../../emails/emailHandler";
import "./settings.css";

/**
 * Settings component for managing user preferences
 * @param {Object} param0 - Component props
 * @param {boolean} param0.isChecked - Indicates whether summaries are enabled
 * @param {function} param0.handleToggleSummariesInInbox - Callback to toggle summaries
 * @param {number} param0.emailFetchInterval - Current email fetch interval
 * @param {function} param0.handleSetEmailFetchInterval - Callback to set email fetch interval
 * @param {string} param0.theme - Current theme
 * @param {function} param0.handleSetTheme - Callback to set theme
 * @returns {JSX.Element}
 */
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

  /**
   * Deletes the user account after confirmation, removes all user info from the database,
   * and redirects to the login page.
   * @async
   * @returns {Promise<void>}
   */
  const handleDeleteAccount = async () => {
    if (!window.confirm("Are you sure you want to delete your EmailEssence Account? \nThis will remove all information associated with your gmail account from our server and lead to longer loading times when you log back in next time.")) return;
    try {
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


  /**
   * Custom hook to detect system theme preference
   * This hook listens for changes in the user's system theme preference
   * and updates the state accordingly.
   * @returns {boolean} isDarkTheme - true if the system theme is dark, false otherwise
   */
  const isDarkTheme = useSystemTheme();
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

/* Component that renders the summary toggle switch for enabling/disabling summaries in the inbox */
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

/* Component that renders the email fetch interval slider */
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

/**
 * Component that renders the theme switcher buttons
 * @param {string} theme - The current theme
 * @param {function} onSetTheme - Callback function to handle theme changes
 * @returns {JSX.Element}
 */
export function Theme({ theme, onSetTheme }) {
  const themes = ["light", "system", "dark"];
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
        {themes.map( //renders the theme buttons
          (
            t
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

/* Component that renders the logout button */
export function Logout({ onLogout }) {
  return (
    <button className="logout" onClick={onLogout}>
      <span className="logout-text">Logout</span>
    </button>
  );
}

/* Component that renders the delete account button */
export function DeleteAccount({ onDelete }) {
  return (
    <button className="delete-account" onClick={onDelete}>
      <span className="delete-account-text">Delete Account</span>
    </button>
  );
}

/**
 * Custom hook to detect system theme preference
 * This hook listens for changes in the user's system theme preference
 * @returns {boolean} isDarkTheme - true if the system theme is dark, false otherwise
 */
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

/**
 * Fetches the current user's profile information
 * @returns {Promise<Object>} - The user's profile data
 */
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


/**
 * Fetches the current user's preferences
 * @returns {Promise<Object>} - The user's preferences data
 */
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

/**
 * Fetches the user's preferences and updates them
 * @returns {Promise<Object>} - The updated user's preferences data
 */
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

/**
 * Fetches a user by ID
 * @returns {Promise<Object>} - The user's data
 */
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

/**
 * Updates a user by ID
 * @param {string} user_id - The ID of the user to update
  * @returns {Promise<Object>} - The updated user's data
 */
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

/**
 * Deletes a user by ID
 * @param {string} user_id - The ID of the user to delete
 * @returns {Promise<Object>} - The deleted user's data
 */
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

/**
 * Saves the user preferences to the backend
 * @param {string} user_id - The ID of the user
 * @param {Object} userPreferences - The user's preferences data
 * @returns {Promise<Object>} - The updated user's preferences data
 */
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
