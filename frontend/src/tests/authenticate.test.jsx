import {
  authenticate,
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

beforeAll(() => {
  delete window.location;
  window.location = { href: "" };
});

afterAll(() => {
  window.location = originalLocation;
});
const originalLocation = window.location;
describe("No Error", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mock("../emails/emailHandler", () => ({
      baseUrl: "https://example.com",
      retrieveUserData: vi.fn(),
    }));
  });

  it("redirects to correct login URL", async () => {
    const baseUrl = "https://example.com"; // Mock baseUrl
    const expectedRedirectUri = `${window.location.origin}/loading`;
    const expectedUrl = `${baseUrl}/auth/login?redirect_uri=${expectedRedirectUri}`;

    await authenticate();
    console.log(window.location.href);
    expect(window.location.href).toBe(expectedUrl);
  });

  it("handles authentication", async () => {
    const token = "testToken";
    vi.mock("../authenticate/authenticate", () => ({
      retrieveUserData: vi.fn(),
    }));

    await handleAuthenticate(token);
    expect(localStorage.getItem("auth_token")).toBe(token);
  });
});

describe("With Error", () => {
  it("handle authentication Error", async () => {
    const token = "testToken";
    vi.mocked(
      await import("../emails/emailHandler")
    ).retrieveUserData.mockImplementation(() => {
      throw new Error("Error");
    });

    await handleAuthenticate(token);
    expect(window.location.href).toBe("/error");
  });
});
