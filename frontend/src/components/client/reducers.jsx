import { saveUserPreferences } from "./settings/settings";

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
        isChecked: action.emailFetchInterval,
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
