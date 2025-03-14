export function clientReducer(client, action) {
  switch (action.type) {
    case 'logoClick': {
      return {
        ...client,
        expandedSideBar: !action.state
      };
    };
    case 'pageChange': {
      return {
        ...client,
        curPage: action.page
      };
    };
    case 'emailChange': {
      return {
        ...client,
        curEmail: action.email
      };
    };
  };
};



export function userPreferencesReducer(userPreferences, action){
    // Call to get user preferences the the update preferences base on the reducer action
    switch(action.type){
        case "isChecked":{
            return {
                ...userPreferences, 
                isChecked: !action.isChecked
            };
        }
        case "emailFetchInterval":{
            return {
                ...userPreferences, 
                emailFetchInterval: action.emailFetchInterval
            };
        }
        case "theme":{
            return {
                ...userPreferences, 
                theme: action.theme
            };
        }
    }
}
