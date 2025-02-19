import { /*fireEvent,*/ render, screen } from '@testing-library/react';
import React from 'react';
import { describe, expect, test } from 'vitest';
import Register from "../components/register/register";

describe("Register Components", () => {
  // Rendering Tests
  test("renders the register components ", () => {
    render(<Register />);
    expect(screen.getByText("Create an Account")).toBeInTheDocument();
    expect(screen.getByText("Already have an account?")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Email Address")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Password")).toBeInTheDocument();
    expect(screen.getByDisplayValue("Register")).toBeInTheDocument();
  });
});