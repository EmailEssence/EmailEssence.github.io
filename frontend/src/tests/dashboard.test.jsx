import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import Dashboard from "../components/dashboard/dashboard";

const mockEmailList = [
  {
    email_id: "1",
    sender: "sender1@example.com",
    received_at: [2025, 2, 17],
    subject: "Subject 1",
    summary_text: "Summary 1",
  },
  {
    email_id: "2",
    sender: "sender2@example.com",
    received_at: [2025, 2, 17],
    subject: "Subject 2",
    summary_text: "Summary 2",
  },
  {
    email_id: "3",
    sender: "sender3@example.com",
    received_at: [2025, 2, 17],
    subject: "Subject 3",
    summary_text: "Summary 3",
  },
  {
    email_id: "4",
    sender: "sender4@example.com",
    received_at: [2025, 2, 17],
    subject: "Subject 4",
    summary_text: "Summary 4",
  },
  {
    email_id: "5",
    sender: "sender5@example.com",
    received_at: [2025, 2, 17],
    subject: "Subject 5",
    summary_text: "Summary 5",
  },
];

const mockHandlePageChange = vi.fn();
const mockSetCurEmail = vi.fn();

describe("Dashboard Component", () => {
  it("renders Dashboard component", () => {
    render(
      <Dashboard
        emailList={mockEmailList}
        handlePageChange={mockHandlePageChange}
        setCurEmail={mockSetCurEmail}
      />
    );
    expect(screen.getByText("Inbox")).toBeInTheDocument();
  });

  it("renders WeightedEmailList component", () => {
    render(
      <Dashboard
        emailList={mockEmailList}
        handlePageChange={mockHandlePageChange}
        setCurEmail={mockSetCurEmail}
      />
    );
    expect(screen.getByText("Summary 1")).toBeInTheDocument();
    expect(screen.getByText("Summary 2")).toBeInTheDocument();
  });

  it("renders MiniViewPanel component", () => {
    render(
      <Dashboard
        emailList={mockEmailList}
        handlePageChange={mockHandlePageChange}
        setCurEmail={mockSetCurEmail}
      />
    );
    expect(screen.getByText("Inbox")).toBeInTheDocument();
  });

  it("calls handlePageChange when MiniViewHead expand button is clicked", () => {
    render(
      <Dashboard
        emailList={mockEmailList}
        handlePageChange={mockHandlePageChange}
        setCurEmail={mockSetCurEmail}
      />
    );
    fireEvent.click(screen.getByRole("button"));
    expect(mockHandlePageChange).toHaveBeenCalledWith("inbox");
  });

  it("calls setCurEmail and handlePageChange when MiniViewEmail is clicked", () => {
    render(
      <Dashboard
        emailList={mockEmailList}
        handlePageChange={mockHandlePageChange}
        setCurEmail={mockSetCurEmail}
      />
    );
    fireEvent.click(screen.getByText("Subject 1"));
    expect(mockSetCurEmail).toHaveBeenCalledWith(mockEmailList[0]);
    expect(mockHandlePageChange).toHaveBeenCalledWith("inbox");
  });
});
