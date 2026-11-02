// The homepage's desktop windows, by id. Saved positions and minimized states are restored by an
// inline script before the first paint, so the windows never jump into place.

export const DESKTOP_WINDOWS = {
  about: "About Christopher Kearl",
  note: "Note Pad",
} as const;

export type DesktopWindowId = keyof typeof DESKTOP_WINDOWS;

export const MINIMIZED_KEY = "desktop-minimized";
export const POSITIONS_KEY = "desktop-positions";

export const restoreScript = `(function () {
  try {
    var root = document.documentElement;
    var positions = JSON.parse(localStorage.getItem("${POSITIONS_KEY}") || "{}");
    var minimized = JSON.parse(localStorage.getItem("${MINIMIZED_KEY}") || "[]");
    for (var id in positions) root.style.setProperty("--window-" + id, positions[id].x + "px " + positions[id].y + "px");
    root.dataset.minimized = minimized.join(" ");
  } catch (error) {}
})();`;
