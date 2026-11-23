import { type RefObject, useEffect } from "react";

/**
 * Keep screen-reader state in step with the CSS :user-invalid state of a form's fields.
 *
 * :user-invalid only matches after the user leaves a field or tries to submit, but it does not
 * set aria-invalid. For each field whose data-error names its error message's id, this sets
 * aria-invalid, lists the message in aria-describedby only while it shows, and announces a new
 * error once through one polite live region for the page. Fields start at aria-invalid="false".
 */
export function useUserInvalid(form: RefObject<HTMLFormElement | null>) {
  useEffect(() => {
    const root = form.current;
    if (!root) return;
    const announcer = pageAnnouncer();
    const flagged = new WeakSet<Element>();
    const announced = new WeakSet<Element>();
    let announcedField: Element | null = null;
    let timer: ReturnType<typeof setTimeout> | undefined;

    const announce = (field: HTMLInputElement) => {
      const error = field.dataset.error && document.getElementById(field.dataset.error);
      if (!error) return;
      const label = field.labels?.[0] ? `${spoken(field.labels[0])}: ` : "";
      clearTimeout(timer);
      announcer.textContent = "";
      announcedField = field;
      // Wait until the screen reader has announced the field that receives focus next.
      timer = setTimeout(() => (announcer.textContent = label + spoken(error)), 500);
    };

    const sync = (target: EventTarget | null, withAnnouncement = false) => {
      if (!(target instanceof Element) || !target.matches("input, select, textarea")) return;
      const field = target as HTMLInputElement;
      if (field.matches(":user-invalid")) {
        if (withAnnouncement && !announced.has(field)) {
          announce(field);
          announced.add(field);
        }
        field.setAttribute("aria-invalid", "true");
        linkError(field, true);
        flagged.add(field);
      } else if (flagged.has(field) || field.getAttribute("aria-invalid") !== "true") {
        field.setAttribute("aria-invalid", "false");
        linkError(field, false);
        flagged.delete(field);
        announced.delete(field);
        if (announcedField === field) {
          clearTimeout(timer);
          announcer.textContent = "";
        }
      }
    };

    for (const field of root.elements) sync(field);
    const onBlur = (event: Event) => sync(event.target, true);
    const onInput = (event: Event) => {
      if (event.target instanceof Element && event.target.hasAttribute("aria-invalid")) {
        sync(event.target);
      }
    };
    // A failed submit fires 'invalid' on each failing field; focus moving to the first one
    // reads its error, so these are not announced again.
    const onInvalid = (event: Event) => {
      if (event.target instanceof Element) announced.add(event.target);
      sync(event.target);
    };
    const onReset = () => setTimeout(() => [...root.elements].forEach((field) => sync(field)));
    root.addEventListener("blur", onBlur, true);
    root.addEventListener("input", onInput);
    root.addEventListener("change", onBlur, true);
    root.addEventListener("invalid", onInvalid, true);
    root.addEventListener("reset", onReset, true);
    return () => {
      clearTimeout(timer);
      root.removeEventListener("blur", onBlur, true);
      root.removeEventListener("input", onInput);
      root.removeEventListener("change", onBlur, true);
      root.removeEventListener("invalid", onInvalid, true);
      root.removeEventListener("reset", onReset, true);
    };
  }, [form]);
}

// List the error message in aria-describedby only while it shows: text that aria-describedby
// references is announced even when it is hidden.
function linkError(field: HTMLElement, shown: boolean) {
  const errorId = field.dataset.error;
  if (!errorId) return;
  const ids = (field.getAttribute("aria-describedby") ?? "")
    .split(/\s+/)
    .filter((id) => id && id !== errorId);
  if (shown) ids.push(errorId);
  if (ids.length) field.setAttribute("aria-describedby", ids.join(" "));
  else field.removeAttribute("aria-describedby");
}

/** Text as a screen reader reads it: icons' text alternatives in, aria-hidden text out. */
function spoken(node: Element): string {
  const copy = node.cloneNode(true) as Element;
  copy.querySelectorAll('[aria-hidden="true"]').forEach((n) => n.remove());
  copy
    .querySelectorAll('[role="img"][aria-label]')
    .forEach((n) => n.replaceWith(`${n.getAttribute("aria-label")}: `));
  return (copy.textContent ?? "").replace(/\s+/g, " ").trim();
}

function pageAnnouncer(): HTMLElement {
  let region = document.getElementById("form-announcer");
  if (!region) {
    region = document.createElement("div");
    region.id = "form-announcer";
    region.setAttribute("aria-live", "polite");
    region.className = "visually-hidden";
    document.body.append(region);
  }
  return region;
}
