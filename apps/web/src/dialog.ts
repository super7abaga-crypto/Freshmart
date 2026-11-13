import { h } from "./dom";

export interface ConfirmOptions {
  title: string;
  text: string;
  confirmLabel: string;
  cancelLabel?: string;
  icon?: string;
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
      h("div", { class: "action-sheet-icon", "aria-hidden": "true", text: opts.icon ?? "🗑" }),
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
