import { describe, expect, it } from "vitest";
import { applyDelta, type Message } from "./messageReducer";

describe("applyDelta", () => {
  it("creates an assistant message for a new turn", () => {
    const out = applyDelta([], { type: "delta", turnId: "t1", text: "Hello", conversationId: "c1" });
    expect(out).toEqual([{ id: "t1", role: "assistant", content: "Hello" }]);
  });

  it("appends streamed text to the same turn", () => {
    const start: Message[] = [{ id: "t1", role: "assistant", content: "Hel" }];
    const out = applyDelta(start, { type: "delta", turnId: "t1", text: "lo", conversationId: "c1" });
    expect(out[0].content).toBe("Hello");
  });

  it("carries the confirm stage onto the message", () => {
    const out = applyDelta([], {
      type: "delta",
      turnId: "t2",
      text: "Create it?",
      conversationId: "c1",
      stage: "confirm",
    });
    expect(out[0].stage).toBe("confirm");
  });
});
