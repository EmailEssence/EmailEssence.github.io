import DOMPurify from "dompurify";
import { fetchUserPreferences } from "../components/client/settings/settings";
// TODO : env variable for baseUrl
// export const baseUrl = "http://127.0.0.1:8000";
export const baseUrl = "https://ee-backend-w86t.onrender.com";

/**
 * Filters out emails that already exist in the list.
 * @param {Array<Email>} allEmails - The list of all emails.
 * @param {Array<Email>} requestedEmails - The list of requested emails.
 * @returns {Array<Email>} The list of new emails.
 */
function getNewEmails(allEmails, requestedEmails) {
  return requestedEmails.filter((reqEmail) => {
    let exists = false;
    for (const email of allEmails) {
      if (email.email_id === reqEmail.email_id) exists = true;
    }
    return !exists;
  });
}

/**
 * Handles the new emails by filtering out emails that already exist in the list.
 * @param {Array<Email>} allEmails - The list of all emails.
 * @param {Array<Email>} requestedEmails - The list of requested emails.
 * @returns {Array<Email>} The list of new emails.
 */
export const handleNewEmails = (allEmails, requestedEmails) => {
  if (requestedEmails.length > 0) {
    const newEmails = getNewEmails(allEmails, requestedEmails);
    if (newEmails.length > 0) {
      return newEmails;
    }
  }
  return [];
};
/**
 * Fetches user preferences based on the user ID.
 * @async
 * @param {string} user_id - The ID of the user whose preferences are to be fetched.
 * @returns {Promise<void>}
 * @throws {Error} If there is an error during the fetch operation.
 */
export const getUserPreferences = async (user_id) => {
  try {
    const preferences = await fetchUserPreferences(user_id);
    return preferences;
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
async function getEmails(number, ...args) {
  let refresh = "false";
  let curEmail = "0";
  if (args.length > 0) {
    if (typeof args[0] === "number") {
      curEmail = parseInt(args[0], 10);
    } else if (args[0]) {
      refresh = "true";
    }
  }
  const option = {
    method: "GET",
    headers: {
      Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
      "Content-Type": "application/json",
    },
  };
  try {
    const req = new Request(
      `${baseUrl}/emails/?skip=${curEmail}&limit=${number}&unread_only=false&sort_by=received_at&sort_order=desc&refresh=${refresh}`,
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
  return email.reader_content;
}

/**
 * Fetches the summary for a specific email.
 * @param {string} emailId - The ID of the email to fetch the summary for.
 * @returns {Promise<Object>} The summary of the email.
 */
async function getSummary(emailIds) {
  const params = new URLSearchParams();
  emailIds.forEach((id) => params.append("ids", id));
  params.append("batch_size", emailIds.length);
  const option = {
    method: "GET",
    headers: {
      Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
      "Content-Type": "application/json",
      Accept: "application/json",
    },
  };
  try {
    const req = new Request(
      `${baseUrl}/summaries/batch?${params.toString()}`,
      option
    );
    const response = await fetch(req);
    if (!response.ok) {
      throw new Error(`Failed to retrieve summaries: ${response.statusText}`);
    }
    let summary = await response.json();
    summary.valid = true;
    return summary;
  } catch (error) {
    console.error("Summary fetch error:", error);
    return { valid: false };
  }
}

/**
 * Parses the date of an email.
 * @param {string} date - The date of the email.
 * @returns {Array<string>} The parsed date.
 */
export async function setSummary(ids, allEmails) {
  const result = await getSummary(ids);
  const toReturn = allEmails.map((email) => {
    let eml = email;
    for (const summary of result) {
      if (summary.email_id === eml.email_id) {
        eml.summary_text = summary.summary_text;
        eml.keywords = summary.keywords;
      }
    }
    return eml;
  });
  return toReturn;
}

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
 * Fetches the emails from the server.
 * @param {number} pageSize - The number of emails to fetch.
 * @param {...any} args - The arguments to fetch the emails.
 * @returns {Promise<Array<Email>>} The list of emails.
 */
export default async function fetchEmails(pageSize, ...args) {
  try {
    // Fetch both emails and summaries concurrently
    const newEmails = await getEmails(pageSize, ...args);
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

/**
 * Trims the list of emails by keyword.
 * @param {Array<Email>} emails - The list of emails to trim.
 * @param {string} keyword - The keyword to trim the list by.
 * @returns {Array<Email>} The trimmed list of emails.
 */
export function trimList(emails, keyword) {
  const toReturn = emails.filter((email) => {
    if (email.subject.includes(keyword) || email.sender.includes(keyword))
      return true;
    for (const kWord in email.keywords) {
      if (kWord.includes(keyword)) return true;
    }
    return false;
  });
  return toReturn;
}

/**
 * Gets the top 5 emails.
 * @param {Array<Email>} emails - The list of emails to get the top 5 from.
 * @returns {Array<Email>} The top 5 emails.
 */
export function getTop5(emails) {
  return emails.length > 5 ? emails.slice(0, 5) : emails;
}

/**
 * Marks an email as read.
 * @param {string} emailId - The ID of the email to mark as read.
 * @returns {Promise<void>}
 */
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
