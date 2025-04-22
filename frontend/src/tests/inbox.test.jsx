import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import Inbox from "../components/client/inbox/inbox";
import EmailDisplay from "../components/client/inbox/emailDisplay";

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
  {
    email_id: "2",
    sender: "sender2@example.com",
    received_at: [2025, 2, 17],
    subject: "Subject 2",
    summary_text: "Summary 2",
    body: "Body 2",
    recipients: "recipient2@example.com",
    is_read: true,
  },
];

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

  it("renders ReaderView", () => {
    render(<EmailDisplay curEmail={mockEmailList[0]} />);
    const svgElement = screen.getByText(
      (content, element) => element.tagName.toLowerCase() === "svg"
    ); // Get Element Role Name "svg"
    expect(svgElement).toBeInTheDocument();
  });

  it("renders ReaderView PopUp", () => {
    // Create a mock portal in the test DOM
    const portal = document.createElement("div");
    portal.setAttribute("id", "portal");
    document.body.appendChild(portal);

    render(<EmailDisplay curEmail={mockEmailList[0]} />);

    const button = screen.getByTestId("reader-view-button");
    fireEvent.click(button);

    expect(screen.getByText("Click To Close")).toBeInTheDocument();

    // Clean up the portal after the test
    document.body.removeChild(portal);
  });
});
