React Unit Testing Checklist (Vitest)

1. General Component Tests 
Rendering
- Component renders without crashing.
- Component renders correctly with default props.
- Component renders correctly with different props. 

Props Handling
- Component updates correctly when props change.
- Conditional rendering works as expected.

Event Handling
- Button clicks trigger the correct function.
- Input fields update state on change.
- Forms submit correctly.
- Keyboard/mouse events behave as expected.

State Management
- Local state updates correctly (useState).
- Derived values update when state changes.
- Side effects trigger correctly (useEffect).

Error Handling
- Component handles missing/invalid props.
- Error boundaries catch component failures.


2. API Calls & Async Behavior
Mocking API Requests
- API calls execute correctly.
- Loading states are displayed while fetching.
- Errors are handled gracefully (e.g., network failures).
- Data renders correctly after a successful fetch.

React Query / SWR (if used)
- Query calls execute properly.
- Cached data updates correctly.

3. Custom Hook Testing
- Hook initializes with correct state.
- Hook updates state properly.
- Hook cleans up side effects correctly.

4. Context & Global State Testing
Context Providers
- Provider renders children correctly.
- Context updates when actions are dispatched.

Redux / Zustand / Jotai (if used)
- Store initializes correctly.
- Actions update the store properly.
- Selectors return correct values.

5. UI/Styling & Accessibility
CSS / Tailwind Classes
- Conditional styles apply correctly.
- Dark mode / theme switching works.

Accessibility (a11y)
- Component has proper aria attributes.
- Keyboard navigation works.
- Screen reader text is accessible.

6. Other Considerations
Routing (if using React Router)
- Navigation works correctly.
- Route params are passed correctly.
- Redirects function as expected.

Component Unmounting
- useEffect cleanups trigger correctly.
- Event listeners are removed.

7. Next Steps
Run tests automatically using vitest --watch
Check test coverage with vitest --coverage
Integrate tests into CI/CD (GitHub Actions, GitLab CI)