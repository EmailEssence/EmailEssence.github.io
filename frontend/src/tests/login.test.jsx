import { /*fireEvent,*/ render, screen } from "@testing-library/react";
import { describe, expect, test } from "vitest";
import { Login } from "../components/login/login";

// Unit Tests: Test individual functions, components, and utilities.
// Integration Tests: Test component interactions(e.g., props, state changes).
// End - to - End Tests: Ensure the app works as expected across user flows.

describe("Login Components", () => {
  // Rendering Tests
  test("renders the text", () => {
    render(<Login />);
    expect(screen.getByText("Welcome Back")).toBeInTheDocument();
    expect(screen.getByText("Login with Google")).toBeInTheDocument();
  });

  test("renders the page", () => {
    render(<Login />);
    expect(
      screen.getByRole("button", { name: "Login with Google" })
    ).toBeInTheDocument();
  });
});
