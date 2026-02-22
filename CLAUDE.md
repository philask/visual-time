# Visual Time

Single-page website displaying the current time across 4 timezones as stacked sky-gradient rulers.

## Project structure

- `index.html` — the entire app (embedded CSS + vanilla JS, no build tools)

## What it does

- 4 rows: New York, London, Dubai, Singapore
- Each row: city label + live HH:MM clock on the left, 24-hour sky-gradient ruler on the right
- Left edge of each ruler = "now", right edge = 24 hours ahead
- Sky gradient interpolates 24 hand-crafted colours (midnight navy → sunrise gold → noon blue → sunset orange → dusk purple)
- Tick marks every hour (short) and every 3 hours (tall) using `mix-blend-mode: difference`
- Hour labels at 3-hour intervals in pill badges inside the ruler
- Midnight: full-height divider + date label above the ruler
- Clock text updates every second; rulers rebuild at each minute boundary

## Key implementation details

- Timezone extraction: `Intl.DateTimeFormat` with `hour12: false` + `formatToParts()`
- Gradient: one CSS colour stop per integer hour boundary in the 24-hour window
- No frameworks, no server required — open `index.html` directly in a browser
