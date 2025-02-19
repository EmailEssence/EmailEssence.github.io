import { /*fireEvent,*/ render, screen } from '@testing-library/react';
import React from 'react';
import { describe, expect, test } from 'vitest';
import Login from '../components/login/login';

// Unit Tests: Test individual functions, components, and utilities.
// Integration Tests: Test component interactions(e.g., props, state changes).
// End - to - End Tests: Ensure the app works as expected across user flows.

describe('Login Components', () => {
    // Rendering Tests
    test('renders the login components ', () => {
        render(<Login />);
        expect(screen.getByText('Welcome Back')).toBeInTheDocument();
        expect(screen.getByText("Don't have an account yet?")).toBeInTheDocument();
        expect(screen.getByText('Sign up')).toBeInTheDocument();
        expect(screen.getByPlaceholderText('Email Address')).toBeInTheDocument();
        expect(screen.getByPlaceholderText('Password')).toBeInTheDocument();
        expect(screen.getByDisplayValue('Login')).toBeInTheDocument();
    });
});