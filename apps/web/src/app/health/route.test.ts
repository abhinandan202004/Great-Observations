// @vitest-environment node
import { describe, expect, it } from "vitest";
import packageJson from "../../../package.json";
import { GET } from "./route";

describe("GET /health", () => {
  it("reports ok", async () => {
    const response = GET();

    expect(response.status).toBe(200);
    expect(await response.json()).toEqual({
      status: "ok",
      service: "web",
      version: packageJson.version,
    });
  });
});
