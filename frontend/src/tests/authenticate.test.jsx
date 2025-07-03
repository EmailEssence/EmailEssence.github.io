import {
  authenticate,
  checkAuthStatus,
  handleAuthenticate,
} from "../authentication/authenticate";
import {
  describe,
  it,
  expect,
  vi,
  beforeAll,
  afterAll,
  beforeEach,
} from "vitest";

// ToDo: Test handleOAuthCallback

beforeAll(() => {
  delete window.location;
  window.location = { href: "" };
});

afterAll(() => {
  window.location = originalLocation;
});
const originalLocation = window.location;
beforeEach(() => {
  vi.clearAllMocks();
  vi.mock("../emails/emailHandler", () => ({
    baseUrl: "https://example.com",
    retrieveUserData: vi.fn(),
  }));
});
describe("No Error", () => {
  it("redirects to correct login URL", async () => {
    const baseUrl = "https://example.com"; // Mock baseUrl
    const expectedRedirectUri = `${window.location.origin}/loading`;
    const expectedUrl = `${baseUrl}/auth/login?redirect_uri=${expectedRedirectUri}`;

    await authenticate();
    console.log(window.location.href);
    expect(window.location.href).toBe(expectedUrl);
  });

  it.skip("handles authentication", async () => {
    const token = "testToken";
    vi.mock("../authenticate/authenticate", () => ({
      retrieveUserData: vi.fn(),
    }));

    await handleAuthenticate(token);
    expect(localStorage.getItem("auth_token")).toBe(token);
  });

  it("returns true auth status on authenticated user", async () => {
    globalThis.fetch = vi.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve({ is_authenticated: true }),
      })
    );
    const token = "validToken";
    const result = await checkAuthStatus(token);
    expect(fetch).toHaveBeenCalledWith(expect.any(Request));
    expect(result).toBe(true);
  });
});

describe("With Error", () => {
  it.skip("handle authentication Error", async () => {
    const token = "testToken";
    vi.mocked(
      await import("../emails/emailHandler")
    ).retrieveUserData.mockImplementation(() => {
      throw new Error("Error");
    });

    await handleAuthenticate(token);
    expect(window.location.href).toBe("/error");
  });
  it("returns false when user is not authenticated", async () => {
    // Mock fetch to return a response with is_authenticated: false
    globalThis.fetch = vi.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve({ is_authenticated: false }),
      })
    );
    const token = "invalidToken";
    const result = await checkAuthStatus(token);
    expect(fetch).toHaveBeenCalledWith(expect.any(Request));
    expect(result).toBe(false);
  });
});
