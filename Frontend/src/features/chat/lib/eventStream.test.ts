import { describe, expect, it } from "vitest";
import { parseEvent } from "./eventStream";

describe("parseEvent", () => {
  it("parses a delta", () => {
    expect(parseEvent('{"type":"delta","turn_id":"t1","text":"hi","conversation_id":"c1"}')).toEqual({
      type: "delta",
      turnId: "t1",
      text: "hi",
      conversationId: "c1",
    });
  });

  it("parses a delta carrying a stage", () => {
    expect(
      parseEvent('{"type":"delta","turn_id":"t1","text":"ok?","conversation_id":"c1","stage":"confirm"}'),
    ).toEqual({ type: "delta", turnId: "t1", text: "ok?", conversationId: "c1", stage: "confirm" });
  });

  it("parses a notification", () => {
    expect(parseEvent('{"type":"notification","id":"n1","title":"Created","body":"KAN-1"}')).toEqual({
      type: "notification",
      id: "n1",
      title: "Created",
      body: "KAN-1",
      jiraKey: undefined,
    });
  });

  it("returns null on garbage", () => {
    expect(parseEvent("not json")).toBeNull();
  });
});
