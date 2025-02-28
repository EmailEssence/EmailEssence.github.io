export function placeholderReducer(tasks, action) {
  switch (action.type) {
    case 'logoClick': {
      return null;
    }
    case 'pageChange': {
      return null;
    }
    case 'setCurEmail': {
      return null;
    }
  }
}



export function userPreferencesReducer(tasks, action){
    switch(action.type){
        case "isChecked":{
            return null;
        }
        case "emailFetchInterval":{
            return null;
        }
        case "theme":{
            return null;
        }
    }
}