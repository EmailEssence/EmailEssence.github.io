import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { EmailFetchInterval, Settings, SummariesInInbox, Theme } from '../components/settings/settings';

describe('Settings Components', () => {
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
});

