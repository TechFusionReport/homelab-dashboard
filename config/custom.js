/* Browser-local appearance preferences. No service data or credentials are read. */
(() => {
  const key = "homelab.color-theme";
  const themes = [
    { id: "night-circuit", label: "Night Circuit", swatch: "#a58bff" },
    { id: "afterglow", label: "Afterglow", swatch: "#ff9eae" },
    { id: "phosphor", label: "Phosphor", swatch: "#83d9ae" },
  ];
  let current = "night-circuit";
  try {
    const saved = localStorage.getItem(key);
    if (themes.some((theme) => theme.id === saved)) current = saved;
  } catch (_) { /* Appearance still works if browser storage is unavailable. */ }
  document.documentElement.dataset.homelabTheme = current;

  const mount = () => {
    if (document.getElementById("homelab-theme-switcher")) return;
    const group = document.createElement("div");
    group.id = "homelab-theme-switcher";
    group.className = "lab-theme-switcher";
    group.setAttribute("role", "group");
    group.setAttribute("aria-label", "Dashboard color theme");
    const label = document.createElement("span");
    label.className = "lab-theme-switcher-label";
    label.textContent = "Palette";
    group.append(label);
    themes.forEach((theme) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "lab-theme-button";
      button.setAttribute("aria-pressed", String(current === theme.id));
      button.setAttribute("aria-label", `${theme.label} color theme`);
      const swatch = document.createElement("span");
      swatch.className = "lab-theme-swatch";
      swatch.style.setProperty("--swatch", theme.swatch);
      swatch.setAttribute("aria-hidden", "true");
      button.append(swatch, document.createTextNode(theme.label));
      button.addEventListener("click", () => {
        document.documentElement.dataset.homelabTheme = theme.id;
        group.querySelectorAll("button").forEach((item) => item.setAttribute("aria-pressed", String(item === button)));
        try { localStorage.setItem(key, theme.id); } catch (_) { /* Session-only fallback. */ }
      });
      group.append(button);
    });
    document.body.append(group);
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mount, { once: true });
  else mount();
})();
