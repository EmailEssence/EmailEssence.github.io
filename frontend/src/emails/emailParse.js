import emails from "./retrieve_emails_response.json";
import summaries from "./summarize_email_response.json";

let arr1 = JSON.parse(JSON.stringify(emails));
const arr2 = JSON.parse(JSON.stringify(summaries));

arr1.map((element, index) => {
  const sumText = arr2[index].summary_text;
  const keywords = arr2[index].keywords;
  element.summary_text = sumText;
  element.keywords = keywords;
  return element;
});

export default arr1;
