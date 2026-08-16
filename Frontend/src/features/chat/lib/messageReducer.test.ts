import { describe, expect, it } from "vitest";

import { applyDelta, type ChatEvent, type Message } from "./messageReducer";

/**
 * The streaming rules for one assistant turn.
 *
 * These exist because the same bug reached a user three times: a superseded draft left on
 * screen with the real answer appended to it, reading as the same paragraph twice. Each time
 * the server was correct and the client was not, and there was no test here to say so — the
 * project had no frontend test runner at all, so "verified" only ever meant verified on the
 * server.
 */

const delta = (over: Partial<ChatEvent & { type: "delta" }> = {}) =>
  ({
    type: "delta",
    turnId: "turn-1",
    conversationId: "conversation-1",
    text: "",
    ...over,
  }) as Extract<ChatEvent, { type: "delta" }>;

const bubble = (content: string): Message[] => [
  { id: "turn-1", role: "assistant", content, streaming: true },
];

describe("applyDelta", () => {
  it("appends streamed tokens", () => {
    let messages: Message[] = [];
    messages = applyDelta(messages, delta({ text: "Hello ", stage: "token" }));
    messages = applyDelta(messages, delta({ text: "world.", stage: "token" }));
    expect(messages).toHaveLength(1);
    expect(messages[0].content).toBe("Hello world.");
  });

  it("empties the bubble on restart instead of appending the rewrite", () => {
    let messages = bubble("First attempt, uncited.");
    messages = applyDelta(messages, delta({ stage: "restart" }));
    expect(messages[0].content).toBe("");
    messages = applyDelta(messages, delta({ text: "Second attempt [Doc 1].", stage: "token" }));
    expect(messages[0].content).toBe("Second attempt [Doc 1].");
    expect(messages[0].content).not.toContain("First attempt");
  });

  it("keeps the turn in place on restart rather than removing it", () => {
    // Removing and re-adding would move the message to the end of the list, so the answer
    // would jump past anything that arrived while it was being rewritten.
    const messages = applyDelta(
      [
        { id: "turn-1", role: "assistant", content: "draft" },
        { id: "turn-2", role: "user", content: "later message" },
      ],
      delta({ stage: "restart" }),
    );
    expect(messages.map((m) => m.id)).toEqual(["turn-1", "turn-2"]);
  });

  it("ignores a restart for a turn it has never seen", () => {
    expect(applyDelta([], delta({ stage: "restart" }))).toHaveLength(0);
  });

  it("replaces the bubble with the final answer", () => {
    // The safety net. Even if the restart above were dropped in transit, the terminal event
    // carries the whole answer, so what is left on screen is what the server persisted.
    let messages = bubble("First attempt, uncited.Second attempt [Doc 1].");
    messages = applyDelta(
      messages,
      delta({ text: "Second attempt [Doc 1].", stage: "reply", replace: true }),
    );
    expect(messages[0].content).toBe("Second attempt [Doc 1].");
  });

  it("does not treat an ordinary token as a replacement", () => {
    const messages = applyDelta(bubble("Hello "), delta({ text: "world.", stage: "token" }));
    expect(messages[0].content).toBe("Hello world.");
  });

  it("marks the message streaming only while tokens arrive", () => {
    expect(applyDelta(bubble("x"), delta({ text: "y", stage: "token" }))[0].streaming).toBe(true);
    expect(
      applyDelta(bubble("x"), delta({ text: "x", stage: "reply", replace: true }))[0].streaming,
    ).toBe(false);
  });

  it("leaves the transcript alone for tool status", () => {
    const before = bubble("partial answer");
    expect(applyDelta(before, delta({ text: "searching…", stage: "tool_status" }))).toBe(before);
  });
});
