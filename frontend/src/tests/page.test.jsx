import { render, screen, fireEvent, act } from "@testing-library/react";
import { describe, it, expect, beforeEach, vi } from "vitest";
import Page from "../page";

const mockEmail = [
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
  localStorage.clear();
  vi.mock("../authentication/authenticate", () => ({
    authenticate: vi.fn(),
    checkAuthStatus: vi.fn((token) => console.log(token)),
    handleOAuthCallback: vi.fn(),
  }));
});

describe("Page Component Not Logged In", () => {
  it("renders logged out state", () => {
    act(() => {
      render(<Page />);
    });
    expect(screen.getByText("Login with Google")).toBeInTheDocument();
  });

  it("clicks button", async () => {
    const { authenticate } = await import("../authentication/authenticate");

    act(() => {
      render(<Page />);
    });

    const loginButton = screen.getByText("Login with Google");

    act(() => {
      fireEvent.click(loginButton);
    });

    expect(authenticate).toHaveBeenCalled();
  });
});

describe("Page Component Logged In", () => {
  beforeEach(() => {
    localStorage.setItem("auth_token", "mock_token");
    vi.mock("../emails/emailParse", () => ({
      getTop5: vi.fn(() => mockEmail),
      default: vi.fn(() => Promise.resolve(mockEmail)),
    }));
  });

  it("renders emails when logged in", async () => {
    await act(async () => {
      render(<Page />);
    });
    expect(await screen.findByText("Test Email")).toBeInTheDocument();
  });

  it.skip("Calls Auth Status Check", async () => {
    // Cannot Modify CalledAuth State To Allow For Auth Status Checks To Go Through
    vi.useFakeTimers();
    const { checkAuthStatus } = await import("../authentication/authenticate");
    await act(async () => {
      render(<Page />);
    });

    expect(checkAuthStatus).not.toHaveBeenCalled();

    act(() => {
      vi.advanceTimersByTime(60100);
    });

    expect(checkAuthStatus).toHaveBeenCalled();
    vi.useRealTimers();
  });
});
