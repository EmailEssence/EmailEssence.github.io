//import emails from "./retrieve_emails_response.json";
//import summaries from "./summarize_email_response.json";

export const baseUrl = "";

async function getAllEmails() {
  try {
    const response = await fetch(baseUrl);
    if (!response.ok) {
      throw new Error(`Failed to retrieve emails: ${response.statusText}`);
    }
    const emails = await response.json();
    return emails;
  } catch (error) {
    console.error(error);
  }
}

async function getAllSummaries() {
  try {
    const response = await fetch(baseUrl);
    if (!response.ok) {
      throw new Error(`Failed to retrieve summaries: ${response.statusText}`);
    }
    const summaries = await response.json();
    return summaries;
  } catch (error) {
    console.error(error);
  }
}

const emails = getAllEmails();
const summaries = getAllSummaries();

let arr1 = JSON.parse(JSON.stringify(emails));
const arr2 = JSON.parse(JSON.stringify(summaries));

arr1.map((element, index) => {
  const sumText = arr2[index].summary_text;
  const keywords = arr2[index].keywords;
  element.summary_text = sumText;
  element.keywords = keywords;
  const date = element.received_at;
  element.received_at = parseDate(date);
  return element;
});

function parseDate(date) {
  const dateArr = [];
  const time = date.slice(11, 16);
  const year = date.slice(0, 4);
  const month = date.slice(5, 7);
  const day = date.slice(8, 10);
  dateArr.push(year);
  dateArr.push(month);
  dateArr.push(day);
  dateArr.push(time);
  return dateArr;
}

export default arr1;

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
