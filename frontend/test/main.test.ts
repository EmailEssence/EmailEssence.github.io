import {Stack} from "../src/main";

describe("My Stack", () => {
  let stack: Stack;

  beforeEach(() => {
    stack = new Stack();
  });

  it("is created empty", () => {
    expect(stack.top).toBe(-1);
    expect(stack.items).toEqual([]);
  });

  it("can push to the top", () => {
    stack.push("hello");
    expect(stack.top).toBe(0);
    expect(stack.peek).toBe("hello");
  });

  it("can pop off", () => {
    stack.push("hello");
    stack.push("bye");
    expect(stack.pop).toBe("bye");
    expect(stack.peek).toBe("hello");
  });
});
