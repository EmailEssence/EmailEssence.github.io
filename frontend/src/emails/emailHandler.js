import DOMPurify from "dompurify";
import { fetchUserPreferences } from "../components/client/settings/settings";
// TODO : env variable for baseUrl
// export const baseUrl = "http://127.0.0.1:8000";
export const baseUrl = "https://ee-backend-w86t.onrender.com";
export let emails = [];
export let userPreferences = {
  isChecked: true,
  emailFetchInterval: 120,
  theme: "light",
};

/**
 * @typedef {Object} Email
 * @property {string} email_id
 * @property {string} sender
 * @property {string[]} recipients
 * @property {string} subject
 * @property {string} body
 * @property {[string, string, string, string]} received_at - [year, month, day, time]
 * @property {string} category
 * @property {boolean} is_read
 * @property {string} summary_text
 * @property {string[]} keywords
 * @property {boolean} hasInnerHTML
 */


/**
 * Fetches new emails and updates the global emails array.
 * If found, it appends new emails to the existing list and updates the URL hash.
 * @async
 * @returns {Promise<void>}
 * @throws {Error} If there is an error during the fetch operation.
 */
export const fetchNewEmails = async () => {
  try {
    const requestedEmails = await fetchEmails(100);
    if (requestedEmails.length > 0) {
      const newEmails = getNewEmails(requestedEmails, emails); // O(n^2) operation
      if (newEmails.length > 0) {
        emails = [...emails, ...newEmails];
        window.location.hash = "#newEmails";
      }
    }
  } catch (error) {
    console.error(`Error fetching new emails: ${error}`);
  }
};


/**
 * Filters out emails that already exist in the allEmails array.
 * @param {Array} requestedEmails the list of emails requested by the user
 * @param {Array} allEmails the list of all existing emails
 * @returns {Array} the list of new emails
 */
function getNewEmails(requestedEmails, allEmails) {
  return requestedEmails.filter((reqEmail) => {
    let exists = false;
    for (const email of allEmails) {
      if (email.email_id === reqEmail.email_id) exists = true;
    }
    return !exists;
  });
}

/**
 * Retrieves user data: emails and preferences.
 * @async
 * @returns {Promise<void>}
 * @throws {Error} If there is an error during the fetch operations.
 */
export const retrieveUserData = async () => {
  try {
    emails = await fetchEmails(100);
    const user_id = null; // Get user ID
    if (user_id) getUserPreferences(user_id);
  } catch (error) {
    console.error(error);
  }
};

/**
 * Fetches user preferences based on the user ID.
 * @async
 * @param {string} user_id - The ID of the user whose preferences are to be fetched.
 * @returns {Promise<void>}
 * @throws {Error} If there is an error during the fetch operation.
 */
const getUserPreferences = async (user_id) => {
  try {
    const preferences = await fetchUserPreferences(user_id);
    userPreferences = preferences;
  } catch (error) {
    console.error(error);
  }
};

/**
 * Fetches raw emails from the backend.
 * @param {number} extension - The number of emails to fetch.
 * @returns {Promise<array>} - A promise that resolves to an array of emails.
 * @throws {Error} If it fails to retrieve emails or response is not ok.
 */
async function getEmails(extension) {
  const option = {
    method: "GET",
    headers: {
      Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
      "Content-Type": "application/json",
    },
  };
  try {
    const req = new Request(
      `${baseUrl}/emails/?skip=0&limit=${extension}&unread_only=false&sort_by=received_at&sort_order=desc&refresh=true`,
      option
    );
    const response = await fetch(req);
    if (!response.ok) {
      throw new Error(`Failed to retrieve emails: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Email fetch error:", error);
    return []; // Return empty array on error for graceful degradation
  }
}

/**
 * Fetches the reader view content for a specific email.
 * @async
 * @param {string} emailId - The ID of the email to fetch the reader view for.
 * @returns {Promise<string>} - A promise that resolves to the reader view content of the email.
 * @throws {Error} Will throw if the fetch fails.
 */
export async function getReaderView(emailId) {
  const option = {
    method: "GET",
    headers: {
      Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
      "Content-Type": "application/json",
    },
  };
  const request = new Request(
    `${baseUrl}/emails/${emailId}/reader-view`,
    option
  );
  const response = await fetch(request);
  if (!response.ok) {
    throw new Error(`Failed to retrieve ReaderView: ${response.statusText}`);
  }
  const email = await response.json();
  // console.log(`Returning: \n ${email.reader_content}`);
  return email.reader_content;
}

/**
 * Fetches summaries for a batch of email IDs.
 * @async
 * @param {Array<string>} emailIds - Array of email IDs.
 * @returns {Promise<Array<Object>>} Array of summary objects.
 * @throws {Error} If the request fails.
 */
async function getSummaries(emailIds) {
  const option = {
    method: "GET",
    headers: {
      Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
      "Content-Type": "application/json",
    },
  };
  try {
    const queryParams = new URLSearchParams();
    emailIds.forEach((id) => queryParams.append("ids", id));
    const req = new Request(
      `${baseUrl}/summaries/batch?${queryParams}`,
      option
    );
    const response = await fetch(req);
    if (!response.ok) {
      throw new Error(`Failed to retrieve summaries: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Summary fetch error:", error);
    return []; // Return empty array on error for graceful degradation
  }
}

/**
 * Parses a date string into an array of [year, month, day, time].
 * @param {string} date - The date string to parse.
 * @returns {Array<string>} [year, month, day, time] or ["", "", "", ""] on error.
 * @throws {Error} If the date string is invalid or parsing fails.
 */
function parseDate(date) {
  if (!date) return ["", "", "", ""]; // Handle null/undefined dates
  try {
    return [
      date.slice(0, 4), // year
      date.slice(5, 7), // month
      date.slice(8, 10), // day
      date.slice(11, 16), // time
    ];
  } catch (error) {
    console.error("Date parsing error:", error);
    return ["", "", "", ""]; // Return empty date array on error
  }
}


/**
 * Fetches emails from the backend.
 * @async
 * @param {number} numRequested - The number of emails to fetch.
 * @returns {Promise<Array>} - Array of processed email objects.
 */
export default async function fetchEmails(numRequested) {
  try {
    // Fetch both emails and summaries concurrently
    const newEmails = await getEmails(numRequested);
    // remove and replace with per page summary loading
    // const summaries = await getSummaries(ids);
    // summaries.reverse(); // link summaries to respected email
    // Validate array responses
    if (!Array.isArray(newEmails.emails)) {
      console.error("Invalid emails response:", newEmails);
      return [];
    }
    // Handle case where summaries length doesn't match emails
    const processedEmails = newEmails.emails.map((email) => {
      const parser = new DOMParser();
      const doc = parser.parseFromString(email.body, "text/html");
      const hasInnerHTML = doc.body.children.length > 0;

      return {
        ...email,
        body: hasInnerHTML ? DOMPurify.sanitize(email.body) : email.body,
        hasInnerHTML: hasInnerHTML,
        summary_text: "",
        keywords: [],
        received_at: parseDate(email.received_at),
      };
    });

    return processedEmails;
  } catch (error) {
    console.error("Email processing error:", error);
    return []; // Return empty array for graceful degradation
  }
}

export function getPageSummaries(emailList) {
  const toGetSummaries = emailList.filter(
    (email) => email.summary_text.length === 0
  );
  if (toGetSummaries.length > 0) addSummaries(toGetSummaries);
}

export function getTop5(emailList) {
  let toGetSummaries = emailList.length > 5 ? emailList.slice(0, 5) : emailList;
  toGetSummaries = toGetSummaries.filter(
    (email) => email.summary_text.length === 0
  );
  if (toGetSummaries.length > 0) addSummaries(toGetSummaries);
  return emailList.length > 5 ? emailList.slice(0, 5) : emailList;
}

/**
 * Adds summaries and keywords to a list of emails by fetching them from the backend.
 * Updates the corresponding emails in the global emails array.
 * @async
 * @param {Array<Object>} emailList - List of email objects to update with summaries.
 * @returns {Promise<void>}
 * @throws {Error} If fetching or updating summaries fails.
 */
async function addSummaries(emailList) {
  const ids = emailList.map((emailList) => {
    return emailList.email_id;
  });
  try {
    const summaries = await getSummaries(ids);
    summaries.reverse(); // link summaries to respected email
    for (let i = 0; i < emailList.length; i++) {
      const index = emails.indexOf(emailList[i]);
      emails[index] = {
        ...emails[index],
        summary_text: summaries[i].summary_text || "",
        keywords: summaries[i].keywords || [],
      };
    }
    if (emailList.length > 0) window.location.hash = "#newEmails";
  } catch (error) {
    console.error("Summaries adding error:", error);
  }
}

export async function markEmailAsRead(emailId) {
  console.log(emailId);
  return;
  // try {
  //   const response = await fetch(`${baseUrl}/${emailId}/read`, {
  //     method: "PUT",
  //   });
  //   if (!response.ok) {
  //     throw new Error(`Failed to mark email as read: ${response.statusText}`);
  //   }
  //   const updatedEmail = await response.json();
  //   return updatedEmail;
  // } catch (error) {
  //   console.error(error);
  // }
}

// "user_id" ID of the user
// "email_id" ID of the email (unique to each email)
// "sender" email of the sender
// "recipients" emails of the users that have received this email
// "subject" title of the email
// "body" content of the email
// "received_at" [year, month, day, time]
// "category" category of email
// "is_read" has the email been read
// "summary_text" summary of the email
// "keywords": [] keywords used to describe email
// "hasInnerHTML" boolean saying wether to display email as HTML
