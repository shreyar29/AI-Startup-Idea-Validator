# Frontend Documentation

## Tech Stack

| Technology | Role |
|-----------|------|
| React 19 (Vite) | Component framework |
| Tailwind CSS 3 | Utility-first styling |
| Framer Motion | Animations and transitions |
| Axios | Backend API communication |
| Lucide React | SVG icon set |
| React Router DOM v6 | Client-side routing |
| Google Fonts: Outfit + Inter | Typography |

---

## Routing

| Path | Component | Purpose |
|------|-----------|---------|
| `/` | `Home.jsx` | Landing page with feature overview |
| `/validate` | `ValidateStartup.jsx` | Main validation workflow |

The Contact page has been removed.

---

## Pages

### `pages/Home.jsx`
Landing page featuring:
- "Powered by Agentic AI" badge chip
- Large gradient headline
- 3 feature cards: Query Agent, Web Search Agent, Result Generation
- CTA button linking to `/validate`

### `pages/ValidateStartup.jsx`
Main validation page. All backend logic is triggered here.

**State:**
- `idea` — current textarea value
- `isProcessing` — disables input during API call
- `currentStage` — drives the animated pipeline indicator (0=Query, 1=Search, 2=Result)
- `results` — structured JSON from backend
- `error` — error message string

**Flow:**
1. User types idea into `<textarea>` (multi-line, `rows=4`, non-resizable)
2. User clicks "Validate" button
3. `handleValidate()` fires:
   - Sets `isProcessing = true`, clears previous results/errors
   - Starts a `setInterval` to advance `currentStage` every 1.5s (visual UX)
   - Awaits `validateStartup(idea)` from `services/api.js`
   - On success: clears interval, sets `results`, stops processing
   - On failure: clears interval, sets `error` message
4. Results rendered dynamically:
   - **Identified Context** card — LLM-detected product, industry, audience, technology
   - **Market Intelligence Report** — per-category 3-column grid of result cards

**Example chips:** 4 randomly selected sample ideas shown below the input when idle.

---

## Components

### `components/Navbar.jsx`
- Fixed top navigation bar with glassmorphism background
- Links: Home (Rocket icon), Validate (Activity icon)
- Active link indicated by animated underline using Framer Motion `layoutId`

### `components/Footer.jsx`
Standard footer component.

---

## Services

### `services/api.js`

```js
validateStartup(idea)  // POST /search → { idea }
```

- Base URL: `http://127.0.0.1:8001`
- Sends `POST /search` with JSON body
- On error: unwraps `error.response.data.detail` from FastAPI's structured error responses
- Throws with the human-readable message for the UI to display

---

## Design System

### Color Palette (tailwind.config.js)

| Token | Hex | Usage |
|-------|-----|-------|
| `background` | `#0B0F19` | Page background |
| `surface` | `#131B2D` | Cards and panels |
| `primary` | `#06b6d4` | Cyan — buttons, active states, icons |
| `primaryHover` | `#0891b2` | Darker cyan on hover |
| `accent` | `#D946EF` | Fuchsia — secondary accents |
| `textMain` | `#F3F4F6` | Primary text |
| `textMuted` | `#9CA3AF` | Captions, labels, placeholders |

### CSS Utilities (index.css)

| Class | Description |
|-------|-------------|
| `.glass-panel` | `bg-white/5 backdrop-blur-xl border border-white/10 shadow-2xl` |
| `.glass-panel-hover` | Hover: lightened background + blue glow border |
| `.text-gradient` | Animated cyan → fuchsia → indigo gradient text |
| `.animate-gradient-x` | 15s background-position keyframe animation |

### Typography
- **Headings (h1–h6):** Outfit font, `letter-spacing: -0.025em`
- **Body / UI:** Inter font
