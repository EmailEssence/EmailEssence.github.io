import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, test, vi } from "vitest";
import {
  EmailFetchInterval,
  Settings,
  SummariesInInbox,
  Theme,
} from "../components/client/settings/settings";

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

// ------------------------ Settings Component Tests ------------------------
describe("Settings Component", () => {
  let mockToggleSummaries, mockSetEmailFetchInterval, mockSetTheme;

  beforeEach(() => {
    mockToggleSummaries = vi.fn();
    mockSetEmailFetchInterval = vi.fn();
    mockSetTheme = vi.fn();
  });

  test("renders the Settings component", () => {
    render(
      <Settings
        isChecked={true}
        handleToggleSummariesInInbox={mockToggleSummaries}
        emailFetchInterval={30}
        handleSetEmailFetchInterval={mockSetEmailFetchInterval}
        theme="light"
        handleSetTheme={mockSetTheme}
      />
    );

    expect(screen.getByText("Settings")).toBeInTheDocument();
    expect(screen.getByText("Summaries in Inbox")).toBeInTheDocument();
    expect(screen.getByText("Email Fetch Interval")).toBeInTheDocument();
    expect(screen.getByText("Theme")).toBeInTheDocument();
  });

  test("test the toggle and slider interactions", () => {
    render(
      <Settings
        isChecked={false}
        handleToggleSummariesInInbox={mockToggleSummaries}
        emailFetchInterval={30}
        handleSetEmailFetchInterval={mockSetEmailFetchInterval}
        theme="light"
        handleSetTheme={mockSetTheme}
      />
    );

    const checkbox = screen.getByRole("checkbox");
    fireEvent.click(checkbox);
    expect(mockToggleSummaries).toHaveBeenCalled();

    const slider = screen.getByRole("slider");
    fireEvent.change(slider, { target: { value: "60" } });
    expect(mockSetEmailFetchInterval).toHaveBeenCalledWith("60");
  });
});

// ------------------------ SummariesInInbox Component Tests ------------------------
describe("SummariesInInbox Component", () => {
  test("renders the SummariesInInbox toggle component", () => {
    render(<SummariesInInbox isChecked={false} onToggle={vi.fn()} />);
    expect(screen.getByText("Summaries in Inbox")).toBeInTheDocument();
  });

  test("toggles the SummariesInInbox when clicked", () => {
    const mockToggle = vi.fn();
    render(<SummariesInInbox isChecked={false} onToggle={mockToggle} />);

    const checkbox = screen.getByRole("checkbox");
    expect(checkbox).not.toBeChecked();

    fireEvent.click(checkbox);
    expect(mockToggle).toHaveBeenCalled();
  });
});

// ------------------------ EmailFetchInterval Component Tests ------------------------
describe("EmailFetchInterval Component", () => {
  test("tests slider renders with correct values", () => {
    render(
      <EmailFetchInterval
        emailFetchInterval={60}
        onSetEmailFetchInterval={vi.fn()}
      />
    );

    const slider = screen.getByRole("slider");
    expect(slider).toHaveValue("60");
  });

  test("test EmailFetchInterval renders with correct min and max values", () => {
    render(
      <EmailFetchInterval
        emailFetchInterval={60}
        onSetEmailFetchInterval={vi.fn()}
      />
    );

    const slider = screen.getByRole("slider");
    expect(slider).toHaveAttribute("min", "5");
    expect(slider).toHaveAttribute("max", "600");
  });

  test("test EmailFetchInterval slider changes its value", () => {
    const mockSetEmailFetchInterval = vi.fn();
    render(
      <EmailFetchInterval
        emailFetchInterval={60}
        onSetEmailFetchInterval={mockSetEmailFetchInterval}
      />
    );

    const slider = screen.getByRole("slider");
    fireEvent.change(slider, { target: { value: "120" } });
    expect(mockSetEmailFetchInterval).toHaveBeenCalledWith("120");
  });
});

// ------------------------ Theme Component Tests ------------------------
describe("Theme Component", () => {
  let mockSetTheme;

  beforeEach(() => {
    mockSetTheme = vi.fn();
    Object.defineProperty(window, "matchMedia", {
      writable: true,
      value: vi.fn().mockImplementation((query) => ({
        matches: query === "(prefers-color-scheme: dark)",
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    });
  });

  test("renders all the Theme component buttons", () => {
    render(<Theme theme="light" onSetTheme={mockSetTheme} />);

    expect(screen.getByText("Light")).toBeInTheDocument();
    expect(screen.getByText("System")).toBeInTheDocument();
    expect(screen.getByText("Dark")).toBeInTheDocument();
  });

  test("handles theme change to light mode", () => {
    render(<Theme theme="light" onSetTheme={mockSetTheme} />);

    const lightButton = screen.getByText("Light");
    fireEvent.click(lightButton);

    expect(mockSetTheme).toHaveBeenCalledWith("light");
    expect(document.body.classList.contains("dark-mode")).toBe(false);
  });

  test("handles theme change to dark mode", () => {
    render(<Theme theme="dark" onSetTheme={mockSetTheme} />);

    const darkButton = screen.getByText("Dark");
    fireEvent.click(darkButton);

    expect(mockSetTheme).toHaveBeenCalledWith("dark");
    expect(document.body.classList.contains("dark-mode")).toBe(true);
  });

  test("handles theme change to system mode when system is dark", () => {
    render(<Theme theme="system" onSetTheme={mockSetTheme} />);

    const systemButton = screen.getByText("System");
    fireEvent.click(systemButton);

    expect(mockSetTheme).toHaveBeenCalledWith("system");
    expect(document.body.classList.contains("dark-mode")).toBe(true);
  });

  test("handles theme change to system mode when system is light", () => {
    window.matchMedia = vi.fn().mockImplementation((query) => ({
      matches: query === "(prefers-color-scheme: light)",
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }));

    render(<Theme theme="system" onSetTheme={mockSetTheme} />);

    const systemButton = screen.getByText("System");
    fireEvent.click(systemButton);

    expect(mockSetTheme).toHaveBeenCalledWith("system");
    expect(document.body.classList.contains("dark-mode")).toBe(false);
  });

  test("checks the buttons are marked as selected based on the current theme", () => {
    const { rerender } = render(<Theme theme="light" onSetTheme={mockSetTheme} />);

    const lightButton = screen.getByText("Light");
    const systemButton = screen.getByText("System");
    const darkButton = screen.getByText("Dark");

    expect(lightButton).toHaveClass("selected");
    expect(systemButton).not.toHaveClass("selected");
    expect(darkButton).not.toHaveClass("selected");

    rerender(<Theme theme="system" onSetTheme={mockSetTheme} />);
    expect(systemButton).toHaveClass("selected");
    expect(lightButton).not.toHaveClass("selected");
    expect(darkButton).not.toHaveClass("selected");

    rerender(<Theme theme="dark" onSetTheme={mockSetTheme} />);
    expect(darkButton).toHaveClass("selected");
    expect(lightButton).not.toHaveClass("selected");
    expect(systemButton).not.toHaveClass("selected");
  });

  test("dark mode for when system theme is dark", () => {
    render(
      <Settings
        isChecked={true}
        handleToggleSummariesInInbox={vi.fn()}
        emailFetchInterval={30}
        handleSetEmailFetchInterval={vi.fn()}
        theme="system"
        handleSetTheme={vi.fn()}
      />
    );

    expect(document.body.classList.contains("dark-mode")).toBe(true);
  });

  test("removes dark mode class for when system theme is light", () => {
    window.matchMedia = vi.fn().mockImplementation((query) => ({
      matches: query === "(prefers-color-scheme: light)",
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }));

    render(
      <Settings
        isChecked={true}
        handleToggleSummariesInInbox={vi.fn()}
        emailFetchInterval={30}
        handleSetEmailFetchInterval={vi.fn()}
        theme="system"
        handleSetTheme={vi.fn()}
      />
    );

    expect(document.body.classList.contains("dark-mode")).toBe(false);
  });


});

