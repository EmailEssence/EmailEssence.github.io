import { fireEvent, render, screen } from '@testing-library/react';
import React from 'react';
import { describe, expect, test, vi } from 'vitest';
import { EmailFetchInterval, Settings, SummariesInInbox, Theme } from '../components/settings/settings';

// Unit Tests: Test individual functions, components, and utilities.
// Integration Tests: Test component interactions(e.g., props, state changes).
// End - to - End Tests: Ensure the app works as expected across user flows.
describe('Settings Components', () => {

    // Rendering Tests
    test('renders the Settings component', () => {
        render(<Settings />);
        expect(screen.getByText('Settings')).toBeInTheDocument();
    });

    test('renders the SummariesInInbox component', () => {
        render(<SummariesInInbox />);
        expect(screen.getByText('Summaries in Inbox')).toBeInTheDocument();
    });

    test('renders the EmailFetchInterval component', () => {
        render(<EmailFetchInterval />);
        expect(screen.getByText('Email Fetch Interval')).toBeInTheDocument();
    });

    test('renders the Theme component', () => {
        render(<Theme />);
        expect(screen.getByText('Theme')).toBeInTheDocument();
    });

    // test('renders all theme buttons', () => {
    //     render(<Theme />);
    //     expect(screen.getByText('light')).toBeInTheDocument();
    //     expect(screen.getByText('system')).toBeInTheDocument();
    //     expect(screen.getByText('dark')).toBeInTheDocument();
    // });

    // Event Handling Tests
    test("Summaries in Inbox Toggle Switch", () => {
        const handleToggle = vi.fn();
        render(<SummariesInInbox onClicked={handleToggle} />);
        fireEvent.click(screen.getByRole('checkbox'));
        expect(handleToggle).toHaveBeenCalledTimes(1);
    });

    test("Email Fetch Interval Slider", () => {  // Test the slider input event for value at 300
        render(<EmailFetchInterval />);
        const slider = screen.getByRole('slider');
        fireEvent.input(slider, { target: { value: 300 } });
        expect(screen.getByText('300')).toBeInTheDocument();
    });

    test("Email Fetch Interval Slider", () => {  // Test the slider input event for value at 0
        render(<EmailFetchInterval />);
        const slider = screen.getByRole('slider');
        fireEvent.input(slider, { target: { value: 0 } });
        expect(screen.getByText('0')).toBeInTheDocument();
    });

    test('clicking a theme button updates the theme', () => {
        render(<Theme />);
        const lightButton = screen.getByText('Light');
        const systemButton = screen.getByText('System');
        const darkButton = screen.getByText('Dark');

        // Click the Light button
        fireEvent.click(lightButton);
        expect(lightButton).toHaveClass('selected');
        expect(systemButton).not.toHaveClass('selected');
        expect(darkButton).not.toHaveClass('selected');

        // Click the System button
        fireEvent.click(systemButton);
        expect(systemButton).toHaveClass('selected');
        expect(lightButton).not.toHaveClass('selected');
        expect(darkButton).not.toHaveClass('selected');

        // Click the Dark button
        fireEvent.click(darkButton);
        expect(darkButton).toHaveClass('selected');
        expect(lightButton).not.toHaveClass('selected');
        expect(systemButton).not.toHaveClass('selected');
    });
});

