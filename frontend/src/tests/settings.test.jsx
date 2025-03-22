import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, test, vi } from "vitest";
import {
  EmailFetchInterval,
  Settings,
  SummariesInInbox,
  Theme,
} from "../components/settings/settings";

// Mock window.matchMedia
Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false, // Default to light mode
    media: query,
    onchange: null,
    addListener: vi.fn(), // Deprecated
    removeListener: vi.fn(), // Deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

describe("Settings Components", () => {
  // Rendering Tests
  test("renders the Settings component", () => {
    render(<Settings />);
    expect(screen.getByText("Settings")).toBeInTheDocument();
  });

  test("renders the SummariesInInbox component", () => {
    render(<SummariesInInbox />);
    expect(screen.getByText("Summaries in Inbox")).toBeInTheDocument();
  });

  test("renders the EmailFetchInterval component", () => {
    render(<EmailFetchInterval />);
    expect(screen.getByText("Email Fetch Interval")).toBeInTheDocument();
  });

  test("renders the Theme component", () => {
    render(<Theme />);
    expect(screen.getByText("Theme")).toBeInTheDocument();
  });

  test("renders all theme buttons", () => {
    render(<Theme />);
    expect(screen.getByText("Light")).toBeInTheDocument();
    expect(screen.getByText("System")).toBeInTheDocument();
    expect(screen.getByText("Dark")).toBeInTheDocument();
  });

  // Event Handling Tests
  test("clicking a theme button updates the theme", () => {
    const mockSetTheme = vi.fn();
    const { rerender } = render(
      <Theme theme="light" onSetTheme={mockSetTheme} />
    );

    const lightButton = screen.getByText("Light");
    const systemButton = screen.getByText("System");
    const darkButton = screen.getByText("Dark");

    // Click the Light button
    fireEvent.click(lightButton);
    expect(mockSetTheme).toHaveBeenCalledWith("light");
    rerender(<Theme theme="light" onSetTheme={mockSetTheme} />);
    expect(lightButton).toHaveClass("selected");
    expect(systemButton).not.toHaveClass("selected");
    expect(darkButton).not.toHaveClass("selected");

    // Click the System button
    fireEvent.click(systemButton);
    expect(mockSetTheme).toHaveBeenCalledWith("system");
    rerender(<Theme theme="system" onSetTheme={mockSetTheme} />);
    expect(systemButton).toHaveClass("selected");
    expect(lightButton).not.toHaveClass("selected");
    expect(darkButton).not.toHaveClass("selected");

    // Click the Dark button
    fireEvent.click(darkButton);
    expect(mockSetTheme).toHaveBeenCalledWith("dark");
    rerender(<Theme theme="dark" onSetTheme={mockSetTheme} />);
    expect(darkButton).toHaveClass("selected");
    expect(lightButton).not.toHaveClass("selected");
    expect(systemButton).not.toHaveClass("selected");
  });
});