import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import Inbox from "../components/client/inbox/inbox";
import EmailDisplay from "../components/client/inbox/emailDisplay";
// import { getReaderView } from "../emails/emailHandler";

// Need to implement scrolling test

const mockEmailList = [
  {
    email_id: "1",
    sender: "sender1@example.com",
    received_at: [2025, 2, 17],
    subject: "Subject 1",
    summary_text: "Summary 1",
    body: "Body 1",
    recipients: "recipient1@example.com",
    is_read: false,
  },
];
for (let i = 2; i < 50; i++) {
  mockEmailList.push({
    email_id: `${i}`,
    sender: "sender1@example.com",
    received_at: [2025, 2, 17],
    subject: `Subject ${i}`,
    summary_text: i == 3 ? "" : `Summary ${i}`,
    body: `Body ${i}`,
    recipients: "recipient1@example.com",
    is_read: false,
  });
}

const mockSetCurEmail = vi.fn(console.log("Hello words"));

describe("Inbox Component", () => {
  it("renders Inbox component", () => {
    render(
      <Inbox
        displaySummaries={true}
        emailList={mockEmailList}
        curEmail={mockEmailList[0]}
        setCurEmail={mockSetCurEmail}
      />
    );
    expect(screen.getByText("Inbox")).toBeInTheDocument();
  });

  it("renders EmailEntry components", () => {
    render(
      <Inbox
        displaySummaries={true}
        emailList={mockEmailList}
        curEmail={mockEmailList[0]}
        setCurEmail={mockSetCurEmail}
      />
    );
    const subjects = screen.getAllByText("Subject 1");
    expect(subjects.length).toBeGreaterThan(0);
    expect(screen.getByText("Subject 2")).toBeInTheDocument();
  });

  it("calls setCurEmail when an EmailEntry is clicked", () => {
    render(
      <Inbox
        displaySummaries={true}
        emailList={mockEmailList}
        curEmail={mockEmailList[0]}
        setCurEmail={mockSetCurEmail}
      />
    );
    fireEvent.click(screen.getByText("Subject 2"));
    expect(mockSetCurEmail).toHaveBeenCalledWith(mockEmailList[1]);
  });

  it("renders ReaderView component", () => {
    render(
      <Inbox
        displaySummaries={true}
        emailList={mockEmailList}
        curEmail={mockEmailList[0]}
        setCurEmail={mockSetCurEmail}
      />
    );
    expect(screen.getByText("Body 1")).toBeInTheDocument();
  });
});

describe("Email Display Component", () => {
  it("renders EmailDisplay component", () => {
    render(<EmailDisplay curEmail={mockEmailList[0]} />);
    expect(screen.getByText("Body 1")).toBeInTheDocument();
  });

  it("renders ReaderView Icon", () => {
    render(<EmailDisplay curEmail={mockEmailList[0]} />);
    const svgElement = screen.getByText(
      (content, element) => element.tagName.toLowerCase() === "svg"
    ); // Get Element Role Name "svg"
    expect(svgElement).toBeInTheDocument();
  });

  it("renders ReaderView PopUp", () => {
    vi.mock("../emails/emailHandler", async () => {
      const original = await vi.importActual("../emails/emailHandler");
      return {
        ...original,
        getReaderView: vi.fn(async () => "RVText"),
      };
    });
    vi.useFakeTimers();
    // Create a mock portal in the test DOM
    const portal = document.createElement("div");
    portal.setAttribute("id", "portal");
    document.body.appendChild(portal);

    render(<EmailDisplay curEmail={mockEmailList[0]} />);

    const button = screen.getByTestId("reader-view-button");
    fireEvent.click(button);

    vi.advanceTimersByTime(1000);

    expect(screen.getByTestId("loading")).toBeInTheDocument();

    // Clean up the portal after the test
    document.body.removeChild(portal);
    vi.useRealTimers();
    vi.clearAllMocks();
  });
});
