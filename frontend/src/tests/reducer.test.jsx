import { beforeEach, describe, expect, test, vi } from "vitest";
import { clientReducer, userPreferencesReducer } from "../components/client/reducers";
import { saveUserPreferences } from "../components/client/settings/settings";

// Mock saveUserPreferences only
vi.mock("../components/client/settings/settings", () => ({
    saveUserPreferences: vi.fn(),
}));

describe("Reducer Component", () => {
    beforeEach(() => {
        vi.clearAllMocks(); // Clear mock calls before each test
    });

    describe("clientReducer", () => {
        test("checks logoClick for expandedSidebar", () => {
            const initialState = { expandedSideBar: false };
            const action = { type: "logoClick", state: false };
            const expectedState = clientReducer(initialState, action);

            expect(expectedState).toEqual({ ...initialState, expandedSideBar: true });
        });

        test("checks update pageChange for curPage", () => {
            const initialState = { curPage: "home" };
            const action = { type: "pageChange", page: "settings" };
            const expectedState = clientReducer(initialState, action);

            expect(expectedState).toEqual({ ...initialState, curPage: "settings" });
        });

        test("checks update emailChange for curEmail", () => {
            const initialState = { curEmail: null };
            const action = { type: "emailChange", email: "test@gmail.com" };
            const expectedState = clientReducer(initialState, action);

            expect(expectedState).toEqual({ curEmail: "test@gmail.com" });
        });
    });

    describe("userPreferencesReducer", () => {
        test("toggles isChecked and saves preferences", () => {
            const initialState = { isChecked: false };
            const action = { type: "isChecked", isChecked: false };
            const expectedState = userPreferencesReducer(initialState, action);

            expect(expectedState).toEqual({ isChecked: true });
            expect(saveUserPreferences).toHaveBeenCalledWith({ isChecked: true });
        });

        test("updates emailFetchInterval and saves preferences", () => {
            const initialState = { emailFetchInterval: 20 };
            const action = { type: "emailFetchInterval", emailFetchInterval: 40 };
            const expectedState = userPreferencesReducer(initialState, action);

            expect(expectedState).toEqual({ emailFetchInterval: 40 });
            expect(saveUserPreferences).toHaveBeenCalledWith({ emailFetchInterval: 40 });
        });

        test("updates theme and saves preferences", () => {
            const initialState = { theme: "light" };
            const action = { type: "theme", theme: "dark" };
            const expectedState = userPreferencesReducer(initialState, action);

            expect(expectedState).toEqual({ theme: "dark" });
            expect(saveUserPreferences).toHaveBeenCalledWith({ theme: "dark" });
        });
    });
});
