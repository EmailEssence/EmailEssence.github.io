import { baseUrl } from "./emailParse";

export async function markEmailAsRead(emailId) {
  try {
    const response = await fetch(`${baseUrl}/${emailId}/read`, {
      method: "PUT",
    });
    if (!response.ok) {
      throw new Error(`Failed to mark email as read: ${response.statusText}`);
    }
    const updatedEmail = await response.json();
    return updatedEmail;
  } catch (error) {
    console.error(error);
  }
}
