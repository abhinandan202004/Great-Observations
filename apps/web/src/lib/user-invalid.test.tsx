import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { useRef } from "react";
import { afterEach, expect, it, vi } from "vitest";
import { useUserInvalid } from "./user-invalid";

afterEach(cleanup);

function Form() {
  const form = useRef<HTMLFormElement>(null);
  useUserInvalid(form);
  return (
    <form ref={form}>
      <label htmlFor="title">Title</label>
      <input id="title" name="title" required data-error="title-error" aria-describedby="hint" />
      <p id="hint">Short</p>
      <p id="title-error">Title is required.</p>
    </form>
  );
}

it("starts every field valid for assistive technology, keeping its hint", () => {
  render(<Form />);
  const field = screen.getByLabelText("Title");

  expect(field.getAttribute("aria-invalid")).toBe("false");
  expect(field.getAttribute("aria-describedby")).toBe("hint");
});

it("flags the field and links its error once :user-invalid matches, then clears it", () => {
  render(<Form />);
  const field = screen.getByLabelText("Title") as HTMLInputElement;
  // jsdom never matches :user-invalid, so stand in for the browser's own timing.
  const matches = vi.spyOn(field, "matches");
  matches.mockImplementation((selector) => selector === ":user-invalid" || selector.includes("input"));

  fireEvent.blur(field);
  expect(field.getAttribute("aria-invalid")).toBe("true");
  expect(field.getAttribute("aria-describedby")).toBe("hint title-error");

  matches.mockImplementation((selector) => selector.includes("input"));
  fireEvent.input(field, { target: { value: "Fixed" } });
  expect(field.getAttribute("aria-invalid")).toBe("false");
  expect(field.getAttribute("aria-describedby")).toBe("hint");
});
