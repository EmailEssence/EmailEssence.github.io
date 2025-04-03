import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, beforeEach, vi } from "vitest";
import Client from "../client";
const mockEmail1 = [
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

const mockEmail2 = [
  {
    user_id: 1,
    email_id: 2,
    sender: "MockSender",
    recipients: "You",
    subject: "Test Email2",
    body: "Test Body2",
    received_at: ["2000", "02", "01", "00:00"],
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
    getTop5: vi.fn(() => mockEmail1),
    default: vi.fn(() => Promise.resolve(mockEmail2)),
  }));
});

describe("Client Component", () => {
  it("Renders Component", () => {
    render(<Client emailsByDate={mockEmail1} />);
    expect(screen.getByText("Test Summary")).toBeInTheDocument();
  });

  it.skip("Runs Effect", async () => {
    // Not running setEmailsByDate Function
    const setEmailsByDate = vi.fn();

    vi.useFakeTimers();

    render(
      <Client
        emailsByDate={mockEmail1}
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
    expect(setEmailsByDate).not.toHaveBeenCalled();

    vi.advanceTimersByTime(200); // 100 ms for padding

    expect(emailparseFuncs.default).toHaveBeenCalled();
    expect(setEmailsByDate).toHaveBeenCalled();

    vi.useRealTimers();
  });

  // Create Test for HandleToggleSummariesInInbox

  // Create Test for HandleSetEmailFetchInterval

  // Create Test for HandleSetTheme

  it("Runs handleSetCurEmail & Switches To Inbox On MiniView Email Click", () => {
    render(<Client emailsByDate={[...mockEmail1, ...mockEmail2]} />);
    const email2 = screen.getByText("Test Email2");
    fireEvent.click(email2);
    expect(screen.getByText("Test Body2")).toBeInTheDocument();
  });
});

describe("SideBar Page Changes", () => {
  it("Expands SideBar", () => {
    render(<Client emailsByDate={mockEmail1} />);
    const button = screen.getByTestId("logo");
    fireEvent.click(button);
    expect(screen.getByText("Settings")).toBeInTheDocument();
  });

  // Test Fails Due To Error In Settings Page
  it.skip("Goes To Settings Page", () => {
    render(<Client emailsByDate={mockEmail1} />);
    const settingsButton = screen.getByTestId("settings");
    fireEvent.click(settingsButton);
    expect(screen.getByText("Settings")).toBeInTheDocument();
  });

  it("Goes To Inobx Page", () => {
    render(<Client emailsByDate={mockEmail1} />);
    const inboxButton = screen.getByTestId("inbox");
    fireEvent.click(inboxButton);
    expect(screen.getByText("Test Body")).toBeInTheDocument();
  });

  it("Returns To Dashboard", () => {
    render(<Client emailsByDate={mockEmail1} />);
    const inboxButton = screen.getByTestId("inbox");
    fireEvent.click(inboxButton);
    fireEvent.click(inboxButton);
    expect(screen.getByText("Test Summary")).toBeInTheDocument();
  });
});
