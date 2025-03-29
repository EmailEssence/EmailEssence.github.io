import { render, screen } from "@testing-library/react";
import { describe, it, expect, beforeEach } from "vitest";
import Page from "../page";

describe("Page Component", () => {
  beforeEach(() => {});

  it("renders login with google button", () => {
    render(<Page />);
    expect(screen.getByText("Login with Google")).toBeInTheDocument();
  });
});
