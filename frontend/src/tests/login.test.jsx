import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, expect, test } from 'vitest';
import { Login } from '../components/login/login';

// Unit Tests: Test individual functions, components, and utilities.
// Integration Tests: Test component interactions(e.g., props, state changes).
// End - to - End Tests: Ensure the app works as expected across user flows.

describe('Login Components', () => {
    // Rendering Tests
    test('renders the login components', () => {
        render(<Login />);
        expect(screen.getByText('Welcome Back')).toBeInTheDocument();
        expect(screen.getByText("Login with Google")).toBeInTheDocument();
    });

    test('renders the svg image', () => {
        render(<Login />);
        expect(screen.getByAltText('Login Icon')).toBeInTheDocument();
    });

    test('renders the page', () => {
        render(<Login />);
        expect(screen.getByTestId('page')).toBeInTheDocument();
    });

    test('renders the formBox', () => {
        render(<Login />);
        expect(screen.getByTestId('formBox')).toBeInTheDocument();
    });

    test('renders the LoginDiv', () => {
        render(<Login />);
        expect(screen.getByTestId('loginDiv')).toBeInTheDocument();
    });

    test('renders the loginIcon', () => {
        render(<Login />);
        expect(screen.getByTestId('loginIcon')).toBeInTheDocument();
    });

    test('renders the loginPhoto', () => {
        render(<Login />);
        expect(screen.getByAltText('Login Icon')).toBeInTheDocument();
    });

});