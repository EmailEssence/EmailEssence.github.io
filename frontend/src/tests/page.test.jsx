import { render, screen } from "@testing-library/react";
import { describe, it, expect, beforeEach, vi } from "vitest";
import Page from "../page";

describe("Page Component Not Logged In", () => {
  it("renders logged out state", () => {
    render(<Page />);
    expect(screen.getByText("Login with Google")).toBeInTheDocument();
  });
});

describe("Page Component Logged In", () => {
  beforeEach(() => {
    localStorage.clear();
    localStorage.setItem("auth_token", "mock_token");
  });

  it("renders loading state", () => {
    render(<Page />);
    expect(screen.getByText("Initializing dashboard...")).toBeInTheDocument();
  });

  // Test Fails because top5 accesses chache emails and test stores emails in state only.
  it("renders emails when logged in", async () => {
    // Mock fetchEmails to return sample emails
    vi.mock("../emails/emailParse", () => ({
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
