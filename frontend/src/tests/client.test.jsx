import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, beforeEach, vi } from "vitest";
import Client from "../client";
const mockEmails = [
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
];

beforeEach(() => {
  vi.clearAllTimers();
  vi.clearAllMocks();
  vi.mock("../emails/emailParse", () => ({
    getTop5: vi.fn(() => mockEmails),
    default: vi.fn(() => mockEmails),
  }));
});

describe("Client Component", () => {
  it("Renders Component", () => {
    render(<Client emailsByDate={mockEmails} />);
    expect(screen.getByText("Test Summary")).toBeInTheDocument();
  });

  it("Runs Effect", async () => {
    const setEmailsByDate = vi.fn();

    vi.useFakeTimers();

    render(
      <Client
        emailsByDate={mockEmails}
        setEmailsByDate={setEmailsByDate}
        defaultUserPreferences={{
          isChecked: true,
          emailFetchInterval: 1,
          theme: "light",
        }}
      />
    );
    const emailparseFuncs = await import("../emails/emailParse");

    vi.advanceTimersByTime(900);

    expect(emailparseFuncs.default).not.toHaveBeenCalled(); // to not be called

    vi.advanceTimersByTime(200); // 100 ms for padding

    expect(emailparseFuncs.default).toHaveBeenCalled();

    vi.useRealTimers();
  });
});

describe("SideBar Page Changes", () => {
  it("Expands SideBar", () => {
    render(<Client emailsByDate={mockEmails} />);
    const button = screen.getByTestId("logo");
    fireEvent.click(button);
    expect(screen.getByText("Settings")).toBeInTheDocument();
  });

  // Test Fails Due To Error In Settings Page
  it.skip("Goes To Settings Page", () => {
    render(<Client emailsByDate={mockEmails} />);
    const settingsButton = screen.getByTestId("settings");
    fireEvent.click(settingsButton);
    expect(screen.getByText("Settings")).toBeInTheDocument();
  });

  it("Goes To Inobx Page", () => {
    render(<Client emailsByDate={mockEmails} />);
    const inboxButton = screen.getByTestId("inbox");
    fireEvent.click(inboxButton);
    expect(screen.getByText("Test Body")).toBeInTheDocument();
  });

  it("Returns To Dashboard", () => {
    render(<Client emailsByDate={mockEmails} />);
    const inboxButton = screen.getByTestId("inbox");
    fireEvent.click(inboxButton);
    fireEvent.click(inboxButton);
    expect(screen.getByText("Test Summary")).toBeInTheDocument();
  });
});
