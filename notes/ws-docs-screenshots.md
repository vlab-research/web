# Bails documentation — screenshot plan

Companion file to `docs/fly/reference/bails.md`. Save each image at the filename shown, into `docs/images/`; `eleventy.config.js` copies that directory as-is.

**These six are still missing, and so are three `fly-monitor-*` captures used by `docs/fly/reference/monitoring.md`.** They were missing on the Hugo site too — the migration did not break them, `scripts/check-links.py` simply made them visible. That checker reports exactly nine findings until the captures land, and zero afterwards.

## Required screenshots (6)

| # | Filename | What to capture |
|---|----------|-----------------|
| 1 | `bails-list.png` | `/bails` route. Full table with 3+ diverse rows: mix of `Conditions`/`User List`, mixed `Immediate`/`Scheduled`/`Absolute` tags, at least one row with a real `Last Execution` timestamp + "X matched, Y bailed" and at least one with `Never`. Show the four action icons (edit / duplicate / history / delete) on each row. Include the **+ New Bail System** button top-right. |
| 2 | `bails-create-form.png` | `/bails/create`. One tall scroll-friendly screenshot showing the cards in order: *Basic Information* (name + Enabled off) → *Bail Type* (Conditions radio selected) → *Conditions* (a single simple `form`-type condition so the card isn't empty) → *Execution Timing* (mode = **Immediate**, no extra fields) → *Action* (Destination Form + Metadata JSON). Crop the **Preview** card out — that gets its own screenshot. |
| 3 | `bails-compound.png` | `/bails/create`, Conditions card. A compound tree showing operator = **AND** (with the hint "(all conditions must match)"), with two child cards inside: a simple `state` condition plus a nested **OR** subgroup containing two `error_code` children. Per-child delete buttons visible, and the **Add Condition** / **Add Group** buttons under the OR group. |
| 4 | `bails-preview.png` | `/bails/create`, after clicking **Preview Matching Users**. The blue `Alert` saying "N users would be bailed" with up to 5 sample users, the **Show SQL** toggle expanded, the SQL `<pre>` block, and the parameter chips below (`$1 = "<value>"`). |
| 5 | `bails-user-list.png` | `/bails/create` after switching to **User List (CSV)** mode. The User List card mid-upload: drag/drop area at top, and a small table below with 3–4 parsed rows showing the `userid`/`pageid`/`shortcode` columns. |
| 6 | `bails-events.png` | `/bails/<id>/events`. The "Event History: <bail name>" card. Table with 5+ events, mix of green `execution` and red `error` tags, varied matched/bailed counts, at least one row with red error text. |

## Notes

- Crop to relevant UI — no whitespace, no browser chrome.
- Filenames follow the `bails-*.png` convention used elsewhere in `docs/images/` (e.g. `fly-*.png`, `typeform-*.png`).
- After dropping images in, run `npm run serve` and preview at `http://localhost:8080/docs/fly/reference/bails/`, then `python3 scripts/check-links.py` to confirm the count fell.
- `bails-create-form.png` is intentionally a tall image — capture as one continuous scroll of the form so all five cards appear in one shot.
