# Figma Slides — App Description

## Summary

Figma Slides is a presentation editor application that allows users to create, edit, and present slide decks collaboratively. The app features a three-panel editor layout (slide filmstrip, canvas, properties panel), a full presenter mode, template gallery, slide transitions and element animations, speaker notes, collaborative comments, and export/share settings. The currently loaded presentation is "Q1 2026 Product Strategy" with 16 slides.

## Main Sections / Views

### 1. Editor View (default)
The main editing interface with three panels:
- **Left Panel (Slide Filmstrip):** Thumbnails of all slides with numbering, drag-to-reorder, comment count badges. Click to select a slide. "+" button to add new blank slides.
- **Center Panel (Canvas):** Displays the currently selected slide at actual resolution (1920x1080) with zoom. Elements can be clicked to select, dragged to reposition, and resized via corner handles. Optional grid and ruler overlays.
- **Right Panel (Properties):** Context-dependent properties panel with three tabs: Properties, Transitions, Animations.

### 2. Presenter Mode
Full presentation view activated via the "Present" button. Shows:
- Current slide displayed large on the left
- Right sidebar with: next slide preview, speaker notes, and navigation controls (Previous/Next buttons, slide counter)
- Keyboard navigation: Arrow keys, Space, Escape to exit

### 3. Templates Gallery
Grid of slide templates that can be applied to the current slide. Includes 10 built-in templates plus any custom templates saved by the user. Applying a template replaces the current slide's elements.

### 4. Export & Share View
Settings organized in cards:
- Export: format selection (PDF, PNG, SVG, PowerPoint)
- Share: share link, permission level, embed toggle
- Presentation settings: slide numbers, loop, auto-advance
- Theme selection: 10 built-in themes
- Collaborators: add/remove collaborators

### 5. Presentation Settings
Form to edit: title, slide dimensions (width/height), default transition type and duration.

## Implemented Features & UI Interactions

### Slide Management
- Add new blank slide (after current slide)
- Duplicate slide
- Delete slide (with confirmation; minimum 1 slide required)
- Reorder slides via drag-and-drop in the filmstrip
- Select slide by clicking thumbnail

### Element Editing
- **Add text element** via toolbar "T" button (creates text at center of slide)
- **Add shape element** via toolbar rectangle button (creates rectangle at center)
- **Select element** by clicking on canvas or elements list in right panel
- **Move element** by dragging on canvas (position updates X/Y in properties)
- **Resize element** by dragging corner handles (NW, NE, SW, SE)
- **Delete element** via properties panel delete button or Delete/Backspace key
- **Lock/unlock element** (locked elements cannot be moved/resized)
- **Show/hide element** (hidden elements not rendered on canvas or in presenter)
- **Reorder layers** via Bring to Front / Forward / Backward / Send to Back buttons
- **Deselect** by clicking canvas background or pressing Escape

### Text Element Properties
- **Font family**: dropdown with 15 options (Inter, Roboto, Open Sans, Montserrat, Playfair Display, Lato, Poppins, Source Sans Pro, Raleway, Nunito, Merriweather, PT Sans, Ubuntu, Oswald, Fira Sans)
- **Font size**: dropdown with 17 size options (10, 12, 14, 16, 18, 20, 24, 28, 32, 36, 40, 48, 56, 64, 72, 80, 96)
- **Font weight**: dropdown (Regular/normal, Bold, Thin/100, Light/300, Medium/500, Semibold/600, Extra Bold/800)
- **Italic toggle**: on/off
- **Underline toggle**: on/off
- **Text alignment**: Left, Center, Right
- **Text color**: hex input + 25 color swatches
- **Content**: textarea for editing text content (supports multiline)

### Shape Element Properties
- **Shape type**: dropdown (rectangle, circle, line, arrow, triangle, diamond, star, rounded-rectangle, pentagon, hexagon)
- **Fill color**: hex input + 25 color swatches
- **Stroke color**: hex text input
- **Stroke width**: number input (0-20)
- **Corner radius**: number input
- **Opacity**: number input (0-1, step 0.1)

### Position & Size (all elements)
- **X**: number input (left position in pixels)
- **Y**: number input (top position in pixels)
- **W**: number input (width in pixels)
- **H**: number input (height in pixels)

### Slide Properties (when no element selected)
- **Background color**: hex input + 25 color swatches
- **Template info**: displays current template type with "Change Template" button
- **Elements list**: shows all elements with type icon, name preview, hidden/locked badges; click to select
- **Slide actions**: Duplicate Slide, Save as Template, Delete Slide

### Slide Transitions (Transitions tab)
- **Transition type for current slide**: dropdown with 10 types (none, fade, slide-left, slide-right, slide-up, slide-down, dissolve, push, zoom-in, zoom-out)
- **Duration (ms)**: number input (0-5000, step 100)
- **Default transition type**: dropdown (same options, applies to presentation default)
- **Default duration**: number input
- **Apply Default to This Slide**: button to copy default transition to current slide

### Element Animations (Animations tab)
When element selected:
- **Animation type**: dropdown with 12 types (none, appear, fade-in, fade-out, move-in-left, move-in-right, move-in-top, move-in-bottom, zoom-in, zoom-out, bounce, spin)
- **Duration (ms)**: number input (0-5000, step 100)
- **Delay (ms)**: number input (0-10000, step 100)
- **Order**: number input (0-99, determines animation sequence)

When no element selected: shows animation order summary listing all animated elements sorted by order.

### Speaker Notes
- Collapsible panel below the canvas
- Textarea for editing notes per slide
- Notes display in presenter mode
- Toggle visibility with minimize button

### Comments (Comments tab in right panel)
- **Filter**: All / Open / Resolved filter buttons
- **Add comment**: textarea + Post button (creates comment on current slide)
- **Comment display**: author avatar, name, time ago, slide badge (clickable to navigate), comment text
- **Resolve/Reopen comment**: toggle button per comment
- **Delete comment**: with confirmation dialog
- **Replies**: displayed nested under parent comment
- **Add reply**: input field under each comment (press Enter to submit)
- **Delete reply**: button per reply
- **Navigate to comment's slide**: click slide badge

### Templates
- **10 built-in templates**: Title Slide, Title + Content, Two Column, Section Header, Blank, Image Focused, Comparison, Quote, Three Column, Statistics
- **Apply template**: click template card, confirm dialog (replaces slide content)
- **Save as Template**: saves current slide as custom template (with name input via modal)
- **Delete custom template**: only custom templates can be deleted

### Presentation Settings
- **Title**: text input (editable via toolbar click or settings view)
- **Slide dimensions**: width (640-3840) and height (480-2160) number inputs
- **Default transition**: type dropdown + duration input
- **Theme**: 10 themes selectable via theme cards (Modern Dark, Clean Light, Warm Earth, Ocean Breeze, Forest Green, Sunset Gradient, Minimal Gray, Bold Purple, Coral Pop, Midnight Blue)
- **Show slide numbers**: toggle
- **Loop presentation**: toggle
- **Auto-advance slides**: toggle
- **Auto-advance interval**: number input (1000-60000ms)
- **Export format**: dropdown (PDF, PNG, SVG, PowerPoint)
- **Share link**: read-only text input with Copy button
- **Share permission**: dropdown (Can View, Can Comment, Can Edit)
- **Enable embed link**: toggle
- **Collaborators**: list of users with Add/Remove buttons

### Toolbar
- **Logo**: Figma-style colored squares
- **Title**: clickable to edit presentation title
- **Add Text / Add Shape**: element creation buttons (editor only)
- **Toggle Grid / Toggle Rulers**: canvas display toggles
- **Zoom In/Out**: zoom control with percentage display (25%-200%)
- **Comments button**: opens/closes comments panel; shows unresolved count badge
- **Templates button**: opens templates view
- **Settings button**: opens settings view
- **Present button**: enters presenter mode
- **Export & Share button**: opens export view
- **Back to Editor**: returns from non-editor views

### Canvas
- **Grid overlay**: toggleable 40px grid lines
- **Ruler**: toggleable horizontal ruler with position marks
- **Zoom**: 25% to 200% in 10% steps
- **Element selection**: blue border + corner resize handles
- **Double-click text**: focuses content textarea in properties

## Data Model

### Presentation
- id, title, createdAt, updatedAt, owner (user ID), collaborators (user ID array)
- themeId, slideWidth, slideHeight, defaultTransition { type, duration }
- shareLink, sharePermission, embedEnabled, exportFormat
- showSlideNumbers, loopPresentation, autoAdvance, autoAdvanceInterval

### Slide
- id, position (0-based), templateType, backgroundColor
- transition { type, duration }
- speakerNotes (string)
- elements[] (array of Element objects)

### Element
- id, type ('text' | 'shape'), x, y, width, height, content
- style: (varies by type)
  - Text: { fontFamily, fontSize, fontWeight, color, textAlign, italic, underline }
  - Shape: { fill, stroke, strokeWidth, cornerRadius, opacity }
- shapeType (for shapes): rectangle, circle, line, arrow, triangle, diamond, star, rounded-rectangle, pentagon, hexagon
- animation { type, duration, delay, order }
- locked (boolean), visible (boolean)

### Template
- id, name, type, description, elements[] (element templates without id/animation/locked/visible)

### Comment
- id, slideId, elementId (nullable), author (user ID), text, createdAt
- resolved (boolean)
- replies[]: { id, author, text, createdAt }

### User
- id, name, email, avatarColor, role ('owner' | 'editor' | 'viewer' | 'commenter')

### Theme
- id, name, bgColor, textColor, accentColor, secondaryBg

## Navigation Structure

| View | How to Reach | Key Actions |
|------|-------------|-------------|
| Editor | Default view / "Back to Editor" button | Edit slides, elements, notes |
| Presenter | "Present" button in toolbar | Navigate slides, view notes |
| Templates | Templates button in toolbar | Apply/manage templates |
| Export & Share | Export button in toolbar | Export, share, theme, settings |
| Settings | Settings (gear) button in toolbar | Title, dimensions, transitions |

### Right Panel Tabs (Editor view only)
| Tab | Content |
|-----|---------|
| Properties | Element or slide properties |
| Transitions | Slide transition settings |
| Animations | Element animation settings |
| Comments | Comment list with filtering (accessed via Comments button) |

## Seed Data Summary

### Presentation
- Title: "Q1 2026 Product Strategy"
- Owner: Sarah Chen (usr_1)
- Theme: Modern Dark
- 4 collaborators: Alex Rivera, Jordan Kim, Casey Patel, Avery Johnson

### Slides (16 total)
1. Title Slide — "Q1 2026 Product Strategy"
2. Agenda — 5 agenda items
3. Section Header — "Company Vision"
4. Our Vision — Core pillars and 2026 focus areas
5. Section Header — "Market Overview"
6. Market Landscape — TAM, trends, opportunities, threats
7. Competitive Analysis — Acme vs Competitor A vs Competitor B
8. Section Header — "Key Metrics"
9. Q1 Performance — ARR ($4.2M), DAU (52.4K), NPS (71), Uptime (99.97%), detailed metrics
10. Section Header — "Product Roadmap"
11. AI Assistant v2 — Capabilities and timeline
12. Mobile Redesign — Key improvements and research
13. Quote — Maya Rodriguez, VP of Engineering
14. Team & Budget — 82 people, Q2 hiring plan, $6.2M budget
15. Next Steps — Action items (immediate, 30-day, 90-day)
16. Thank You — Contact info and links

### Elements (89 total across all slides)
- Mix of text blocks (titles, body text, bullet lists) and shapes (rectangles, rounded-rectangles, divider lines)
- Various font sizes (16-72px), colors, and styles
- Some elements are locked (e.g., decorative dividers)
- Many have animations configured (fade-in, zoom-in, move-in, appear)

### Templates (10 built-in)
Title Slide, Title + Content, Two Column, Section Header, Blank, Image Focused, Comparison, Quote, Three Column, Statistics

### Comments (18 comments, 13 replies)
- 5 resolved, 13 unresolved
- Spread across slides 1, 2, 4, 6, 7, 9, 11, 12, 13, 14, 15, 16
- Authors: multiple team members discussing strategy, data accuracy, timelines, and formatting

### Users (8)
| Name | Role | ID |
|------|------|----|
| Sarah Chen | Owner | usr_1 |
| Alex Rivera | Editor | usr_2 |
| Jordan Kim | Editor | usr_3 |
| Morgan Taylor | Viewer | usr_4 |
| Casey Patel | Editor | usr_5 |
| Riley Zhang | Viewer | usr_6 |
| Quinn Nakamura | Commenter | usr_7 |
| Avery Johnson | Editor | usr_8 |

### Themes (10)
Modern Dark, Clean Light, Warm Earth, Ocean Breeze, Forest Green, Sunset Gradient, Minimal Gray, Bold Purple, Coral Pop, Midnight Blue

### Available Colors (25 swatches)
#6366f1, #ec4899, #14b8a6, #f59e0b, #ef4444, #8b5cf6, #06b6d4, #84cc16, #3b82f6, #f97316, #10b981, #e11d48, #0ea5e9, #a855f7, #22c55e, #ffffff, #000000, #374151, #9ca3af, #d1d5db, #fbbf24, #34d399, #60a5fa, #fb7185, #c084fc

### Transition Types (10)
none, fade, slide-left, slide-right, slide-up, slide-down, dissolve, push, zoom-in, zoom-out

### Animation Types (12)
none, appear, fade-in, fade-out, move-in-left, move-in-right, move-in-top, move-in-bottom, zoom-in, zoom-out, bounce, spin

### Shape Types (10)
rectangle, circle, line, arrow, triangle, diamond, star, rounded-rectangle, pentagon, hexagon
