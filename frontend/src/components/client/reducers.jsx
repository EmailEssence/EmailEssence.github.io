import { saveUserPreferences } from "./settings/settings";

/**
 * Reducer for client state (sidebar, current page, current email).
 * @param {Object} client - Current client state.
 * @param {Object} action - Action to perform.
 * @param {string} action.type - Type of action ("logoClick", "pageChange", "emailChange").
 * @param {boolean} [action.state] - Sidebar expansion state (for "logoClick").
 * @param {string} [action.page] - Page name (for "pageChange").
 * @param {Object} [action.email] - Email object (for "emailChange").
 * @returns {Object} New client state.
 */
export function clientReducer(client, action) {
  switch (action.type) {
    case "logoClick": {
      return {
        ...client,
        expandedSideBar: !action.state,
      };
    }
    case "pageChange": {
      return {
        ...client,
        curPage: action.page,
      };
    }
    case "emailChange": {
      return {
        ...client,
        curEmail: action.email,
      };
    }
  }
}

/**
 * Reducer for user preferences state.
 * Updates and saves user preferences based on the action type.
 * @param {Object} userPreferences - Current user preferences state.
 * @param {Object} action - Action to perform.
 * @param {string} action.type - Type of action ("isChecked", "emailFetchInterval", "theme").
 * @param {boolean} [action.isChecked] - Toggle summaries in inbox (for "isChecked").
 * @param {number} [action.emailFetchInterval] - Email fetch interval (for "emailFetchInterval").
 * @param {string} [action.theme] - Theme name (for "theme").
 * @returns {Object} New user preferences state.
 */
export function userPreferencesReducer(userPreferences, action) {
  // Call to get user preferences to the update preferences base on the reducer action
  switch (action.type) {
    case "isChecked": {
      // if the action type is isChecked then the user preferences will be updated with the new isChecked value and saved to the local storage
      saveUserPreferences({
        ...userPreferences,
        isChecked: !action.isChecked,
      });
      return {
        // returns the updated state of the user preferences
        ...userPreferences,
        isChecked: !action.isChecked,
      };
    }
    case "emailFetchInterval": {
      saveUserPreferences({
        ...userPreferences,
        emailFetchInterval: action.emailFetchInterval,
      });
      return {
        ...userPreferences,
        emailFetchInterval: action.emailFetchInterval,
      };
    }
    case "theme": {
      saveUserPreferences({
        ...userPreferences,
        theme: action.theme,
      });
      return {
        ...userPreferences,
        theme: action.theme,
      };
    }
  }
}
