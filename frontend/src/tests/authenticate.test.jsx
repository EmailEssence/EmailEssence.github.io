import { authenticate } from "../authentication/authenticate";
import {
  describe,
  it,
  expect,
  vi,
  beforeAll,
  afterAll,
  beforeEach,
} from "vitest";

const originalLocation = window.location;
describe("No Error", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mock("../emails/emailHandler", () => ({
      baseUrl: "https://example.com",
      retrieveUserData: vi.fn(),
    }));
  });

  beforeAll(() => {
    delete window.location;
    window.location = { href: "" };
  });

  afterAll(() => {
    window.location = originalLocation;
  });

  it("redirects to correct login URL", async () => {
    const baseUrl = "https://example.com"; // Mock baseUrl
    const expectedRedirectUri = `${window.location.origin}/loading`;
    const expectedUrl = `${baseUrl}/auth/login?redirect_uri=${expectedRedirectUri}`;

    await authenticate();
    console.log(window.location.href);
    expect(window.location.href).toBe(expectedUrl);
  });

  vi.mock("../authentication/authenticate", async () => {
    const originalModule = await vi.importActual(
      "../authentication/authenticate"
    );
    return {
      ...originalModule,
      checkAuthStatus: vi.fn(),
      handleAuthenticate: vi.fn(),
      handleAuthError: vi.fn(),
    };
  });
});

// describe("With Error", () => {});
