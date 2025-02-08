import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { EmailFetchInterval, Settings, SummariesInInbox, Theme } from '../components/settings/settings';
// Unit Tests: Test individual functions, components, and utilities.
// Integration Tests: Test component interactions(e.g., props, state changes).
// End - to - End Tests: Ensure the app works as expected across user flows.
describe('Settings Components', () => {

    // Test the Settings components making sure they render
    it('renders the Settings component', () => {
        render(<Settings />);
        expect(screen.getByText('Settings')).toBeInTheDocument();
    });

    it('renders the SummariesInInbox component', () => {
        render(<SummariesInInbox />);
        expect(screen.getByText('Summaries in Inbox')).toBeInTheDocument();
    });

    it('renders the EmailFetchInterval component', () => {
        render(<EmailFetchInterval />);
        expect(screen.getByText('Email Fetch Interval')).toBeInTheDocument();
    });

    it('renders the Theme component', () => {
        render(<Theme />);
        expect(screen.getByText('Theme')).toBeInTheDocument();
    });

    //
});

