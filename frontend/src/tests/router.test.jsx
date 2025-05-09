import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { beforeEach, describe, it, expect, vi } from "vitest";
import RouterComponent, { AppRouter } from "../components/router/Router";

beforeEach(() => {
  vi.clearAllMocks();
  vi.mock("../emails/emailHandler", async () => {
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
    const original = await vi.importActual("../emails/emailHandler");
    return {
      ...original,
      emails: [...mockEmail1, ...mockEmail2],
      getTop5: vi.fn(() => [...mockEmail1, ...mockEmail2]),
      default: vi.fn(),
    };
  });
});

describe("Router Component", () => {
  it("Renders Router Component", () => {
    render(<RouterComponent />);
    expect(
      screen.getByText(
        "Cut through email overload with our AI-powered solution that intelligently summarizes and categorizes messages, bringing clarity to your communications."
      )
    ).toBeInTheDocument();
  });

  it("Renders Loading Route", () => {
    render(
      <MemoryRouter initialEntries={["/loading"]}>
        <AppRouter />
      </MemoryRouter>
    );
    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("Renders Into Client", () => {
    render(
      <MemoryRouter initialEntries={["/client/dashboard"]}>
        <AppRouter />
      </MemoryRouter>
    );
    expect(screen.getByText("Test Summary22")).toBeInTheDocument();
  });
});
