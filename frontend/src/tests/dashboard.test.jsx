import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import Dashboard from "../components/client/dashboard/dashboard";

const mockEmailList = [];

for (let i = 1; i < 50; i++) {
  mockEmailList.push({
    email_id: `${i}`,
    sender: "sender1@example.com",
    received_at: [2025, 2, 17],
    subject: `Subject ${i}`,
    summary_text: i == 3 ? "" : `Summary ${i}`,
    body: `Body ${i}`,
    recipients: `recipient${i}@example.com`,
    is_read: false,
  });
}

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
    expect(mockHandlePageChange).not.toHaveBeenCalledWith("/client/inbox");
    fireEvent.click(screen.getByRole("button"));
    expect(mockHandlePageChange).toHaveBeenCalledWith("/client/inbox");
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
    expect(mockHandlePageChange).toHaveBeenCalledWith("/client/inbox");
  });

  it("calls setCurEmail and handlePageChange when WE List Icon is clicked", () => {
    render(
      <Dashboard
        emailList={mockEmailList}
        handlePageChange={mockHandlePageChange}
        setCurEmail={mockSetCurEmail}
      />
    );
    fireEvent.click(screen.getByTestId("WEListEmail1"));
    expect(mockSetCurEmail).toHaveBeenCalledWith(mockEmailList[0]);
    expect(mockHandlePageChange).toHaveBeenCalledWith("/client/inbox");
  });
});
