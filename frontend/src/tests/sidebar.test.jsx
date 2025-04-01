import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import Sidebar from "../components/sidebar/sidebar";

describe("Sidebar Component", () => {
  it("Renders Component", () => {
    render(<Sidebar />);
    expect(screen.getByTestId("sidebar")).toBeInTheDocument();
  });
});
