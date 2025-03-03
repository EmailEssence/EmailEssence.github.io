// import emails from "./retrieve_emails_response.json";
// import summaries from "./summarize_email_response.json";
const isDevMode = false;
export const baseUrl = isDevMode
  ? "http://localhost:19000"
  : "https://ee-backend-w86t.onrender.com";

async function getAllEmails() {
  try {
    const response = await fetch(`${baseUrl}/emails/`);
    if (!response.ok) {
      throw new Error(`Failed to retrieve emails: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Email fetch error:", error);
    return []; // Return empty array on error for graceful degradation
  }
}

async function getAllSummaries() {
  try {
    const response = await fetch(`${baseUrl}/summaries/`);
    if (!response.ok) {
      throw new Error(`Failed to retrieve summaries: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Summary fetch error:", error);
    return []; // Return empty array on error for graceful degradation
  }
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

export default async function fetchAll() {
  try {
    // Fetch both emails and summaries concurrently
    const [emails, summaries] = await Promise.all([
      getAllEmails(),
      getAllSummaries(),
    ]);

    // Validate array responses
    if (!Array.isArray(emails)) {
      console.error("Invalid emails response:", emails);
      return [];
    }

    // Handle case where summaries length doesn't match emails
    const processedEmails = emails.map((email, index) => {
      const summary = summaries[index] || { summary_text: "", keywords: [] };

      return {
        ...email,
        summary_text: summary.summary_text || "",
        keywords: summary.keywords || [],
        received_at: parseDate(email.received_at),
      };
    });

    return processedEmails;
  } catch (error) {
    console.error("Email processing error:", error);
    return []; // Return empty array for graceful degradation
  }
}

export function getTop5(emails) {
  return emails.length > 5 ? emails.slice(0, 5) : emails;
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
