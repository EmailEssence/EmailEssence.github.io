import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import Inbox from "../components/inbox/inbox";

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

const mockSetCurEmail = vi.fn();

describe("Inbox Component", () => {
  it("renders Inbox component", () => {
    render(
      <Inbox
        emailList={mockEmailList}
        setCurEmail={mockSetCurEmail}
        curEmail={mockEmailList[0]}
      />
    );
    expect(screen.getByText("Inbox")).toBeInTheDocument();
  });

  it("renders EmailEntry components", () => {
    render(
      <Inbox
        emailList={mockEmailList}
        setCurEmail={mockSetCurEmail}
        curEmail={mockEmailList[0]}
      />
    );
    const subjects = screen.getAllByText("Subject 1");
    expect(subjects.length).toBeGreaterThan(0);
    expect(screen.getByText("Subject 2")).toBeInTheDocument();
  });

  it("calls setCurEmail when an EmailEntry is clicked", () => {
    render(
      <Inbox
        emailList={mockEmailList}
        setCurEmail={mockSetCurEmail}
        curEmail={mockEmailList[0]}
      />
    );
    fireEvent.click(screen.getByText("Subject 2"));
    expect(mockSetCurEmail).toHaveBeenCalledWith(mockEmailList[1]);
  });

  it("renders EmailDisplay component", () => {
    render(
      <Inbox
        emailList={mockEmailList}
        setCurEmail={mockSetCurEmail}
        curEmail={mockEmailList[0]}
      />
    );
    expect(screen.getByText("Body 1")).toBeInTheDocument();
  });

  it("renders ReaderView component", () => {
    render(
      <Inbox
        emailList={mockEmailList}
        setCurEmail={mockSetCurEmail}
        curEmail={mockEmailList[0]}
      />
    );
    expect(screen.getByText("Body 1")).toBeInTheDocument();
  });
});
