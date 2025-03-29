import { render, screen } from "@testing-library/react";
import { describe, it, expect, beforeEach } from "vitest";
import Page from "../page";

describe("Page Component Not Logged In", () => {
  it("renders logged out state", () => {
    render(<Page />);
    expect(screen.getByText("Login with Google")).toBeInTheDocument();
  });
});

describe("Page Component Logged In", () => {
  beforeEach(() => {
    localStorage.clear();
    localStorage.setItem("auth_token", "mock_token");
  });
});
