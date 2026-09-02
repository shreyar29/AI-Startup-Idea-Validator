# Frontend Documentation

This document catalogs every functional file in the VentureLens React frontend.

## 1. App Configuration (`frontend/src/`)

### `App.jsx`
- **Purpose**: Main Application Router.
- **Responsibilities**: Defines lazy-loaded routes (`/`, `/dashboard`, `/report/:id`, `/report/:id/market`, etc.), applies standard layout wrappers, and handles error boundaries.

### `main.jsx`
- **Purpose**: React Bootstrap.
- **Responsibilities**: Renders `<App />` inside React StrictMode and attaches to `#root`.

## 2. Pages (`frontend/src/pages/`)

### `Home.jsx`
- **Purpose**: Landing Page.
- **Responsibilities**: Displays hero section, feature marketing, and entry point to sign up or log in.

### `Dashboard.jsx`
- **Purpose**: User Hub.
- **Responsibilities**: The main input form for submitting a new startup idea (`idea`, `target_audience`, `business_model`). Displays recent report history.

### `ReportView.jsx` (and subpages in `report/`)
- **Purpose**: Report Wrapper.
- **Responsibilities**: Fetches report data from `/api/history/{id}` and passes it to the `DashboardContext`.
- **Subpages**: `Market.jsx`, `Customer.jsx`, `Competitor.jsx`, `SWOT.jsx`, `MVP.jsx`, `GTM.jsx`, `Risk.jsx` - These act as route-specific wrappers that inject data into their respective components.

### `VeraWorkspace.jsx`
- **Purpose**: Vera AI Co-Founder Chat Interface.
- **Responsibilities**: Connects to the WebSocket endpoint, manages chat session history, and renders markdown streamed from the backend.

## 3. Core Components (`frontend/src/components/`)

### `MarketSection.jsx`
- **Purpose**: Displays TAM/SAM/SOM, growth drivers, market trends, and regulations.
- **Dependencies**: Recharts (for visual charting if applicable), Lucide React (icons).

### `CustomerSection.jsx`
- **Purpose**: Displays personas, pain points, and pricing willingness.
- **Dependencies**: Framer Motion for staggered entrance animations.

### `CompetitorSection.jsx`
- **Purpose**: Competitive Landscape.
- **Responsibilities**: Renders the Competitor Radar chart (moat analysis) and Price vs Value Scatter Plot.

### `SWOTSection.jsx`
- **Purpose**: Strategy Display.
- **Responsibilities**: Renders 2x2 SWOT grid and interactive TOWS Matrix tabs (S-O, W-O, S-T, W-T).

### `MVPSection.jsx` & `GTMSection.jsx`
- **Purpose**: Execution roadmaps.
- **Responsibilities**: Displays phased release plans and the 90-Day Action Plan timelines.

### `ComparisonSection.jsx` (Executive Summary)
- **Purpose**: Final Verdict.
- **Responsibilities**: Renders the "Validation Score", "Innovation Score", "Biggest Risk", and the "Final Recommendation".

### `ValidationPipeline.jsx`
- **Purpose**: Loading State.
- **Responsibilities**: Displays the animated multi-step loading screen while the backend Agent Mesh runs.

### `DashboardContext.jsx`
- **Purpose**: State Management.
- **Responsibilities**: Provides the heavily nested `data` object (the complete JSON report) to any component deep in the tree to prevent prop-drilling.

## 4. UI Utilities (`frontend/src/components/vera/`)

### `VeraVerdict.jsx`
- **Purpose**: Specialized chat message renderer.
- **Responsibilities**: Parses complex JSON/Markdown payloads emitted by the RAG pipeline into beautiful conversational UI blocks.

## 5. CSS & Styling

### `index.css`
- **Purpose**: Global Styles & Tailwind Directives.
- **Responsibilities**: Defines the premium dark-mode theme, CSS variables (`--color-surface`, `--color-primary`), and custom keyframe animations (like Vera's floating glow).
