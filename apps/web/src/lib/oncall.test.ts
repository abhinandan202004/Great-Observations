import { expect, it } from "vitest";
import { move } from "./oncall";

it("moves one item and leaves the others in order", () => {
  const order = ["asha", "ben", "chen"];

  expect(move(order, 2, 1)).toEqual(["asha", "chen", "ben"]);
  expect(move(order, 0, 1)).toEqual(["ben", "asha", "chen"]);
  expect(order).toEqual(["asha", "ben", "chen"]);
});
