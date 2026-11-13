import { h } from "./dom";

/** Trash outline, drawn as SVG so it takes the theme colour (emoji render multicolour). */
function trashIcon(): SVGSVGElement {
  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg");
  svg.setAttribute("viewBox", "0 0 24 24");
  svg.setAttribute("width", "26");
  svg.setAttribute("height", "26");
  svg.setAttribute("fill", "none");
  svg.setAttribute("stroke", "currentColor");
  svg.setAttribute("stroke-width", "1.7");
  svg.setAttribute("stroke-linecap", "round");
  svg.setAttribute("stroke-linejoin", "round");
  svg.setAttribute("aria-hidden", "true");
  for (const d of [
    "M4 7h16",
    "M9.5 7V5.5A1.5 1.5 0 0 1 11 4h2a1.5 1.5 0 0 1 1.5 1.5V7",
    "M6.5 7l.8 11.2A2 2 0 0 0 9.3 20h5.4a2 2 0 0 0 2-1.8L17.5 7",
    "M10.5 11v5",
    "M13.5 11v5",
  ]) {
    const path = document.createElementNS(ns, "path");
    path.setAttribute("d", d);
    svg.append(path);
  }
  return svg;
}

export interface ConfirmOptions {
  title: string;
  text: string;
  confirmLabel: string;
  cancelLabel?: string;
}

/**
 * In-app confirmation sheet, replacing window.confirm().
 * Resolves true when the destructive action is chosen, false otherwise
 * (Cancel, Escape, backdrop tap, or the browser's back gesture closing it).
 */
export function confirmAction(opts: ConfirmOptions): Promise<boolean> {
  return new Promise((resolve) => {
    const previouslyFocused = document.activeElement as HTMLElement | null;
    let settled = false;

    const titleId = `sheetTitle-${Date.now()}`;
    const textId = `sheetText-${Date.now()}`;

    const cancel = h("button", {
      class: "action-btn action-btn-ghost",
      type: "button",
      text: opts.cancelLabel ?? "Keep them",
    });
    const confirm = h("button", {
      class: "action-btn action-btn-danger",
      type: "button",
      text: opts.confirmLabel,
    });

    const sheet = h(
      "div",
      { class: "action-sheet", role: "alertdialog", "aria-modal": "true", "aria-labelledby": titleId, "aria-describedby": textId },
      h("div", { class: "action-sheet-grip", "aria-hidden": "true" }),
      h("div", { class: "action-sheet-icon", "aria-hidden": "true" }, trashIcon()),
      h("h2", { class: "action-sheet-title", id: titleId, text: opts.title }),
      h("p", { class: "action-sheet-text", id: textId, text: opts.text }),
      h("div", { class: "action-sheet-actions" }, cancel, confirm),
      h("p", { class: "action-sheet-hint", text: "Esc or tap outside to go back" }),
    );

    const backdrop = h("div", { class: "action-sheet-backdrop" }, sheet);
    document.body.append(backdrop);
    document.body.classList.add("sheet-open");

    const finish = (result: boolean): void => {
      if (settled) return;
      settled = true;
      backdrop.classList.remove("open");
      document.removeEventListener("keydown", onKey, true);
      window.setTimeout(() => {
        backdrop.remove();
        document.body.classList.remove("sheet-open");
        if (previouslyFocused && document.contains(previouslyFocused)) previouslyFocused.focus();
        resolve(result);
      }, 180);
    };

    function onKey(e: KeyboardEvent): void {
      if (e.key === "Escape") {
        e.preventDefault();
        finish(false);
      } else if (e.key === "Tab") {
        // Keep focus inside the sheet while it is open.
        const target = e.shiftKey ? cancel : confirm;
        if (document.activeElement === (e.shiftKey ? confirm : cancel)) {
          e.preventDefault();
          target.focus();
        }
      }
    }

    cancel.onclick = () => finish(false);
    confirm.onclick = () => finish(true);
    backdrop.onclick = (e: MouseEvent) => {
      if (e.target === backdrop) finish(false);
    };
    document.addEventListener("keydown", onKey, true);

    // Next frame so the entry animation plays.
    window.requestAnimationFrame(() => {
      backdrop.classList.add("open");
      cancel.focus();
    });
  });
}
