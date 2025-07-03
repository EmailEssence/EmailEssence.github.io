import { render, screen } from "@testing-library/react";
import { vi, describe, beforeEach, test, expect } from "vitest";
import { handleOAuthCallback } from "../authentication/authenticate";
import Loading from "../components/login/Loading";

vi.mock("../authentication/authenticate", () => ({
  handleOAuthCallback: vi.fn(),
}));

const mockNavigate = vi.fn();
vi.mock("react-router", () => ({
  // mocking react-router
  ...vi.importActual("react-router"),
  useNavigate: () => mockNavigate,
}));

describe("Loading Component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test("renders the loading spinner and text", () => {
    render(<Loading />);
    expect(screen.getByText("Loading...")).toBeInTheDocument();
    expect(screen.getByRole("spinner")).toBeInTheDocument();
  });

  test.skip("navigates to dashboard when OAuth is successful", async () => {
    handleOAuthCallback.mockResolvedValueOnce();
    render(<Loading />);
    await vi.waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith("/client/home#newEmails");
    });
  });

  test("navigates to error page when OAuth fails", async () => {
    handleOAuthCallback.mockRejectedValueOnce(new Error("OAuth failed"));
    render(<Loading />);
    await vi.waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith("/error");
    });
  });
});
