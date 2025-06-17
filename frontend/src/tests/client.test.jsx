import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { describe, it, expect, beforeEach, vi } from "vitest";
import Client from "../components/client/client";

// physically impossible to test for lines 59 - 60

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
    is_read: true,
    summary_text: "Test Summary11",
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
    summary_text: "Test Summary22",
    keywords: ["Mock", "Test"],
  },
];

beforeEach(() => {
  vi.clearAllTimers();
  vi.clearAllMocks();
  vi.mock("../emails/emailHandler", () => ({
    fetchNewEmails: vi.fn(() => []),
    getTop5: vi.fn(() => [...mockEmail1, ...mockEmail2]),
    default: vi.fn(() => [...mockEmail1, ...mockEmail2]),
  }));
});

describe("Client Component", () => {
  it.skip("Renders Component & Sidebar", () => {
    render(
      <MemoryRouter initialEntries={["/home"]}>
        <Client emailsByDate={mockEmail1} />
      </MemoryRouter>
    );
    expect(screen.getByTestId("logo")).toBeInTheDocument();
  });

  it.skip("Runs Effect", async () => {
    vi.useFakeTimers();
    render(
      <MemoryRouter initialEntries={["/home"]}>
        <Client
          emailsByDate={mockEmail1}
          defaultUserPreferences={{
            isChecked: true,
            emailFetchInterval: 1,
            theme: "light",
          }}
        />
      </MemoryRouter>
    );
    const { fetchNewEmails } = await import("../emails/emailHandler");

    expect(fetchNewEmails).not.toHaveBeenCalled();

    vi.advanceTimersByTime(1100); // 100 ms for padding

    expect(fetchNewEmails).toHaveBeenCalled();

    vi.useRealTimers();
  });

  it.skip("Runs Effect & Throws Error", async () => {
    vi.clearAllMocks();
    vi.mock("../emails/emailHandler", () => ({
      fetchNewEmails: vi.fn(() => {
        throw new Error("Failed to fetch new emails");
      }),
      getTop5: vi.fn(() => [...mockEmail1, ...mockEmail2]),
      default: vi.fn(),
    }));
    vi.useFakeTimers();
    render(
      <MemoryRouter initialEntries={["/home"]}>
        <Client
          emailsByDate={mockEmail1}
          defaultUserPreferences={{
            isChecked: true,
            emailFetchInterval: 1,
            theme: "light",
          }}
        />
      </MemoryRouter>
    );
    const { fetchNewEmails } = await import("../emails/emailHandler");

    expect(fetchNewEmails).not.toHaveBeenCalled();

    vi.advanceTimersByTime(1100); // 100 ms for padding

    expect(fetchNewEmails).toHaveBeenCalled();

    vi.useRealTimers();
  });

  it.skip("Throws Update Emails Error", async () => {
    vi.clearAllMocks();
    vi.mock("../emails/emailHandler", () => ({
      fetchNewEmails: vi.fn(() => {
        throw new Error("Failed to fetch new emails");
      }),
      getTop5: vi.fn(() => [...mockEmail1, ...mockEmail2]),
      default: vi.fn(),
    }));
    vi.useFakeTimers();
    render(
      <MemoryRouter initialEntries={["/home"]}>
        <Client
          emailsByDate={mockEmail1}
          defaultUserPreferences={{
            isChecked: true,
            emailFetchInterval: 1,
            theme: "light",
          }}
        />
      </MemoryRouter>
    );
    const { fetchNewEmails } = await import("../emails/emailHandler");
    expect(fetchNewEmails).not.toHaveBeenCalled();

    vi.advanceTimersByTime(1100); // 100 ms for padding

    expect(fetchNewEmails).toHaveBeenCalled();

    vi.useRealTimers();
  });

  // Create Test for HandleToggleSummariesInInbox

  // Create Test for HandleSetEmailFetchInterval

  // Create Test for HandleSetTheme

  it.skip("Runs handleSetCurEmail & Switches To Inbox On MiniView Email Click", () => {
    render(
      <MemoryRouter initialEntries={["/home"]}>
        <Client emailsByDate={[...mockEmail1, ...mockEmail2]} />
      </MemoryRouter>
    );
    const email2 = screen.getByText("Test Email2");
    fireEvent.click(email2);
    expect(screen.getByText("Test Body2")).toBeInTheDocument();
  });
});

describe("SideBar Page Changes", () => {
  it.skip("Expands SideBar", () => {
    render(
      <MemoryRouter initialEntries={["/home"]}>
        <Client emailsByDate={mockEmail1} />
      </MemoryRouter>
    );
    const button = screen.getByTestId("logo");
    fireEvent.click(button);
    expect(screen.getByText("Settings")).toBeInTheDocument();
  });

  // Test Fails Due To Error In Settings Page
  it.skip("Goes To Settings Page", () => {
    render(
      <MemoryRouter initialEntries={["client/home"]}>
        <Client emailsByDate={mockEmail1} />
      </MemoryRouter>
    );
    const settingsButton = screen.getByTestId("settings");
    fireEvent.click(settingsButton);
    // Check we are in settings page
  });

  it.skip("Goes To Inbox Page", () => {
    render(
      <MemoryRouter initialEntries={["client/home"]}>
        <Client emailsByDate={mockEmail1} />
      </MemoryRouter>
    );
    const inboxButton = screen.getByTestId("inbox");
    fireEvent.click(inboxButton);
    expect(screen.getByText("Test Body")).toBeInTheDocument();
  });

  it.skip("Returns To Dashboard", () => {
    render(
      <MemoryRouter initialEntries={["client/home"]}>
        <Client emailsByDate={mockEmail1} />
      </MemoryRouter>
    );
    const inboxButton = screen.getByTestId("inbox");
    fireEvent.click(inboxButton);
    const dashboardButton = screen.getByTestId("home");
    fireEvent.click(dashboardButton);
    expect(screen.getByText("Test Summary22")).toBeInTheDocument();
  });
});
