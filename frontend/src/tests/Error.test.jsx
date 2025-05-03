import { render, screen } from "@testing-library/react";
import { test } from "vitest";
import Error from "../components/login/Error";

describe("Error Component", () => {
    beforeEach(() => {
        localStorage.clear();
    });

    test("renders the Error component with default error message", () => {
        render(<Error />);
        expect(screen.getByText("Authentication Error")).toBeInTheDocument(); // Checks for the title
        expect(screen.getByText("Error: Unknown error")).toBeInTheDocument(); // Checks for the default error message
        expect(screen.getByRole("button", { name: "Retry Login" })).toBeInTheDocument(); // Checks for the button
    });

    test("renders the Error component with a custom error message from localStorage",() => {
        localStorage.setItem("error_message", "Custom error message");
        render(<Error />);
        expect(screen.getByText("Error: Custom error message")).toBeInTheDocument();
        expect(screen.getByRole("button", { name: "Retry Login" })).toBeInTheDocument(); 
    });

    test("renders the Error icon", () =>{
        render(<Error />);
        const errorIcon = screen.getByTestId("error-logo");
        expect(errorIcon).toBeInTheDocument();
    });

    test("navigates to the login page when the button is clicked", () => {
        delete window.location;
        window.location = { href: "" }; // Mock window.location.href
        render(<Error />);
        const retryButton = screen.getByRole("button", { name: "Retry Login" });
        retryButton.click();

        expect(window.location.href).toBe("/login");
    });

});
