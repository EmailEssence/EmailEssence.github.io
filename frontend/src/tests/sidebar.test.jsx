import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { MemoryRouter } from "react-router";
import Sidebar from "../components/client/sidebar/sidebar";

describe("Sidebar Component", () => {
  it("Renders Component", () => {
    render(
      <MemoryRouter>
        <Sidebar />
      </MemoryRouter>
    );
    expect(screen.getByTestId("sidebar")).toBeInTheDocument();
  });
  // Sidebar Expanding Test In Client
});
