import { render, screen } from "@testing-library/react";
import { describe, it, expect, beforeEach, vi } from "vitest";
import Page from "../page";

describe("Page Component Not Logged In", () => {
  it("renders logged out state", () => {
    render(<Page />);
    expect(screen.getByText("Login with Google")).toBeInTheDocument();
  });

  it("clicks button", async () => {
    vi.mock("../authentication/authenticate", () => ({
      authenticate: vi.fn(),
    }));

    const { authenticate } = await import("../authentication/authenticate");

    render(<Page />);

    const loginButton = screen.getByText("Login with Google");
    loginButton.click();

    expect(authenticate).toHaveBeenCalled();
  });
});

describe("Page Component Logged In", () => {
  beforeEach(() => {
    localStorage.clear();
    localStorage.setItem("auth_token", "mock_token");
  });

  it("renders loading dashboard state", () => {
    render(<Page />);
    expect(screen.getByText("Initializing dashboard...")).toBeInTheDocument();
  });

  it("renders emails when logged in", async () => {
    // Mock fetchEmails to return sample emails
    vi.mock("../emails/emailParse", () => ({
      getTop5: vi.fn(() => [
        {
          user_id: 1,
          email_id: 1,
          sender: "MockSender",
          recipients: "You",
          subject: "Test Email",
          body: "Test Body",
          received_at: ["2000", "01", "01", "00:00"],
          category: "MockCategory",
          is_read: false,
          summary_text: "Test Summary",
          keywords: ["Mock", "Test"],
        },
      ]),
      default: vi.fn(() =>
        Promise.resolve([
          {
            user_id: 1,
            email_id: 1,
            sender: "MockSender",
            recipients: "You",
            subject: "Test Email",
            body: "Test Body",
            received_at: ["2000", "01", "01", "00:00"],
            category: "MockCategory",
            is_read: false,
            summary_text: "Test Summary",
            keywords: ["Mock", "Test"],
          },
        ])
      ),
    }));

    render(<Page />);
    expect(await screen.findByText("Test Email")).toBeInTheDocument();
  });
});
