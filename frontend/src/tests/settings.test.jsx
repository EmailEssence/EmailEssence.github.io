import { render, screen } from '@testing-library/react';
import { describe, expect, test } from 'vitest';
import { EmailFetchInterval, Settings, SummariesInInbox, Theme } from '../components/settings/settings';
// Unit Tests: Test individual functions, components, and utilities.
// Integration Tests: Test component interactions(e.g., props, state changes).
// End - to - End Tests: Ensure the app works as expected across user flows.
describe('Settings Components', () => {

    // Rendering the components 
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

    //
});

