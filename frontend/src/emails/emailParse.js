import emails from "./retrieve_emails_response.json";
import summaries from "./summarize_email_response.json";

const arr1 = emails;
const arr2 = summaries;

export function emailsByDate () {
  return arr1.map((element, index) => {
    const sumText = arr2[index].summary_text;
    const keywords = arr2[index].keywords;
    element.summary_text = sumText;
    element.keywords = keywords;

    
  });
}

// --------------------------------------------------------------------

// const fs = require("fs");

// // Read the JSON file
// fs.readFile("retrieve_emails_response.json", "utf8", (err, data) => {
//   if (err) {
//     console.error("Error reading file:", err);
//     return;
//   }

//   try {
//     // Parse the JSON data
//     const emails = JSON.parse(data);
//     const summaries = JSON.parse(data);

//     // Process the emails
//     emails.forEach((email) => {
//       console.log(`Email ID: ${email.email_id}`);
//       console.log(`Sender: ${email.sender}`);
//       console.log(`Subject: ${email.subject}`);
//       console.log(`Received At: ${email.received_at}`);
//       console.log("---");
//     });
//   } catch (err) {
//     console.error("Error parsing JSON:", err);
//   }
// });