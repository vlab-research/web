/* Documentation search.
 * ---------------------------------------------------------------------------
 * This is the first client-side JavaScript on the property, and D-030 records
 * what that is allowed to mean: it is loaded on /docs/ pages only, it makes one
 * request to one same-origin file, it sets no cookie and no storage, and it
 * reports nothing anywhere. D-009 (analytics) stays open and untouched by it.
 *
 * No library. At 47 pages a hand-written scorer is smaller than the loader for
 * one would be, and D-006's "no asset pipeline" holds: this file is copied to
 * the output verbatim, and what you read here is what the browser runs.
 *
 * The index is fetched on the FIRST FOCUS of the search box, never on page
 * load. A reader who does not search pays nothing for search.
 */
(function () {
  "use strict";

  var root = document.querySelector("[data-search]");
  if (!root) return;

  var input = root.querySelector("input");
  var panel = root.querySelector(".doc-results");

  // Progressive enhancement: the markup ships hidden, because an input that
  // accepts text and does nothing is worse than no input at all.
  root.hidden = false;

  var index = null;      // loaded pages, lower-cased fields cached
  var loading = false;
  var rows = [];         // currently rendered results
  var sel = -1;          // active option, -1 for none
  var timer = null;

  function load() {
    if (index || loading) return;
    loading = true;
    fetch("/docs/search-index.json", { credentials: "omit" })
      .then(function (r) {
        if (!r.ok) throw new Error(r.status);
        return r.json();
      })
      .then(function (data) {
        index = data.map(function (p) {
          return {
            u: p.u, t: p.t, s: p.s, h: p.h,
            lt: p.t.toLowerCase(),
            ls: (p.s || "").toLowerCase(),
            lh: p.h.map(function (h) { return h.t.toLowerCase(); }),
            lx: p.x.toLowerCase()
          };
        });
        loading = false;
        if (input.value.trim()) run();
      })
      .catch(function () {
        loading = false;
        // A failed index is a search box that cannot work. Say so rather than
        // sitting silent and looking broken.
        index = [];
        render([], true);
      });
  }

  // Count occurrences of a needle, capped -- a word repeated forty times in one
  // page does not make that page forty times the answer.
  function hits(hay, needle, cap) {
    var n = 0, i = hay.indexOf(needle);
    while (i !== -1 && n < cap) { n++; i = hay.indexOf(needle, i + needle.length); }
    return n;
  }

  function score(page, tokens) {
    var total = 0;
    // How many of the query's tokens each heading matches. The deep link goes to
    // the BEST-matching heading, not the first one to match anything: on the
    // hidden-fields page, "interpolation transforms" must land on
    // "Interpolation Transforms" and not on the "Interpolation" above it.
    var hcount = [];
    for (var h = 0; h < page.lh.length; h++) hcount.push(0);

    for (var i = 0; i < tokens.length; i++) {
      var tk = tokens[i], s = 0, hitHeading = false;
      if (page.lt.indexOf(tk) !== -1) s += 12;
      if (page.ls.indexOf(tk) !== -1) s += 3;
      for (var j = 0; j < page.lh.length; j++) {
        if (page.lh[j].indexOf(tk) !== -1) { hcount[j]++; hitHeading = true; }
      }
      if (hitHeading) s += 6;
      s += hits(page.lx, tk, 5);
      // Every token must appear somewhere. Two words that each match different
      // pages should return neither.
      if (s === 0) return null;
      total += s;
    }

    var heading = null, best = 0;
    for (var k = 0; k < hcount.length; k++) {
      // Strictly greater, so a tie keeps the earliest heading -- which is the one
      // higher up the page, and the safer place to land.
      if (hcount[k] > best) { best = hcount[k]; heading = page.h[k]; }
    }

    // An exact title match outranks anything a body-text pile-up can reach.
    if (page.lt === tokens.join(" ")) total += 40;
    return { page: page, score: total, heading: heading };
  }

  function run() {
    var q = input.value.trim().toLowerCase();
    if (q.length < 2) return close();
    if (!index) return load();

    var tokens = q.split(/\s+/).filter(Boolean);
    var out = [];
    for (var i = 0; i < index.length; i++) {
      var r = score(index[i], tokens);
      if (r) out.push(r);
    }
    out.sort(function (a, b) { return b.score - a.score; });
    render(out.slice(0, 8), false);
  }

  function render(results, failed) {
    panel.textContent = "";
    rows = results;
    sel = -1;

    if (failed || !results.length) {
      var p = document.createElement("p");
      p.className = "r-none";
      p.textContent = failed
        ? "Search is unavailable right now."
        : "Nothing matches “" + input.value.trim() + "”.";
      panel.appendChild(p);
    } else {
      results.forEach(function (r, i) {
        var a = document.createElement("a");
        a.href = r.page.u + (r.heading ? "#" + r.heading.i : "");
        a.id = "doc-r" + i;
        a.setAttribute("role", "option");
        a.setAttribute("aria-selected", "false");

        var t = document.createElement("span");
        t.className = "r-t";
        t.textContent = r.page.t;
        a.appendChild(t);

        // The sub-line says WHERE this is, and which section matched.
        var bits = [];
        if (r.page.s) bits.push(r.page.s);
        if (r.heading) bits.push(r.heading.t);
        if (bits.length) {
          var s = document.createElement("span");
          s.className = "r-s";
          s.textContent = bits.join(" · ");
          a.appendChild(s);
        }
        panel.appendChild(a);
      });
    }

    panel.hidden = false;
    input.setAttribute("aria-expanded", "true");
  }

  function close() {
    panel.hidden = true;
    panel.textContent = "";
    rows = [];
    sel = -1;
    input.setAttribute("aria-expanded", "false");
    input.removeAttribute("aria-activedescendant");
  }

  function move(step) {
    var opts = panel.querySelectorAll('[role="option"]');
    if (!opts.length) return;
    if (sel > -1) opts[sel].setAttribute("aria-selected", "false");
    sel = (sel + step + opts.length + 1) % (opts.length + 1) - 1;
    if (sel < 0) {
      input.removeAttribute("aria-activedescendant");
      return;
    }
    opts[sel].setAttribute("aria-selected", "true");
    input.setAttribute("aria-activedescendant", opts[sel].id);
    opts[sel].scrollIntoView({ block: "nearest" });
  }

  input.addEventListener("focus", load, { once: true });

  input.addEventListener("input", function () {
    clearTimeout(timer);
    timer = setTimeout(run, 90);
  });

  input.addEventListener("keydown", function (e) {
    if (e.key === "ArrowDown") { e.preventDefault(); move(1); }
    else if (e.key === "ArrowUp") { e.preventDefault(); move(-1); }
    else if (e.key === "Enter") {
      var opts = panel.querySelectorAll('[role="option"]');
      if (sel > -1 && opts[sel]) { e.preventDefault(); window.location = opts[sel].href; }
    }
    else if (e.key === "Escape") { close(); input.blur(); }
  });

  document.addEventListener("click", function (e) {
    if (!root.contains(e.target)) close();
  });

  // "/" focuses the search box, which is the convention on every docs site a
  // reader of this one has already used. Never while they are typing somewhere.
  document.addEventListener("keydown", function (e) {
    if (e.key !== "/" || e.metaKey || e.ctrlKey || e.altKey) return;
    var el = document.activeElement;
    if (el && (el.tagName === "INPUT" || el.tagName === "TEXTAREA" || el.isContentEditable)) return;
    e.preventDefault();
    input.focus();
    input.select();
  });
})();
