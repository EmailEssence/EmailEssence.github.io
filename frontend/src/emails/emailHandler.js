import { fetchUserPreferences } from "../components/client/settings/settings";
import DOMPurify from "dompurify";
// TODO : env variable for baseUrl
// export const baseUrl = "http://127.0.0.1:8000";
export const baseUrl = "https://ee-backend-w86t.onrender.com";
export let userPreferences = {
  isChecked: true,
  emailFetchInterval: 120,
  theme: "light",
};

// export const fetchNewEmails = async () => {
//   try {
//     const requestedEmails = await fetchEmails(100);
//     if (requestedEmails.length > 0) {
//       const newEmails = getNewEmails(requestedEmails, emails); // O(n^2) operation
//       if (newEmails.length > 0) {
//         emails = [...emails, ...newEmails];
//         window.location.hash = "#newEmails";
//       }
//     }
//   } catch (error) {
//     console.error(`Error fetching new emails: ${error}`);
//   }
// };

// function getNewEmails(requestedEmails, allEmails) {
//   return requestedEmails.filter((reqEmail) => {
//     let exists = false;
//     for (const email of allEmails) {
//       if (email.email_id === reqEmail.email_id) exists = true;
//     }
//     return !exists;
//   });
// }

export const getUserPreferences = async (user_id) => {
  try {
    const preferences = await fetchUserPreferences(user_id);
    userPreferences = preferences;
  } catch (error) {
    console.error(error);
  }
};

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

// async function getSummaries(emailIds) {
//   const option = {
//     method: "GET",
//     headers: {
//       Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
//       "Content-Type": "application/json",
//     },
//   };
//   try {
//     const queryParams = new URLSearchParams();
//     emailIds.forEach((id) => queryParams.append("ids", id));
//     const req = new Request(
//       `${baseUrl}/summaries/batch?${queryParams}`,
//       option
//     );
//     const response = await fetch(req);
//     if (!response.ok) {
//       throw new Error(`Failed to retrieve summaries: ${response.statusText}`);
//     }
//     return await response.json();
//   } catch (error) {
//     console.error("Summary fetch error:", error);
//     return []; // Return empty array on error for graceful degradation
//   }
// }

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

export async function fetchMoreEmails(curEmailsLength) {}

export default async function fetchEmails(numRequested) {
  try {
    // Fetch both emails and summaries concurrently
    const newEmails = await getEmails(numRequested);
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
