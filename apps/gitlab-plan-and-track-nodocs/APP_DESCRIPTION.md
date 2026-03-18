# GitLab Plan and Track — App Description

## Summary

A faithful replica of GitLab's project planning and issue tracking features. The app covers the full "Plan and Track" workflow including issues, kanban boards, milestones, iterations (sprints), epics, roadmaps, labels, time tracking, quick actions (slash commands), and notifications. The app is scoped to a single project ("AcmeCorp / platform") with 12 team members.

## Main Sections / Pages

The app is a single-page application with sidebar navigation. Sections are:

1. **Issues** (list, detail, create views)
2. **Boards** (kanban view)
3. **Milestones** (list, detail views)
4. **Iterations** (list, detail views)
5. **Epics** (list, detail views)
6. **Roadmap** (timeline/Gantt view)
7. **Labels** (management page)
8. **Notifications** (feed and settings)

## Navigation Structure

- **Sidebar** (always visible, dark theme, left side):
  - **Plan** section: Issues, Boards, Milestones, Iterations, Epics, Roadmap
  - **Manage** section: Labels
  - **User** section: Notifications (with unread badge count)
- **Top bar**: GitLab logo, project breadcrumb ("AcmeCorp / platform"), user avatar
- **Breadcrumbs** within content area for navigation context
- Click sidebar link to navigate between sections
- Click issue/milestone/iteration/epic titles to view detail pages
- "Back" navigation via breadcrumb links

## Implemented Features and UI Interactions

### Issues List
- Table view with columns: checkbox, title (with labels, priority, type badges), assignee avatars, milestone, updated date
- **Status tabs**: Open (count) / Closed (count) / All (count) — filters by issue state
- **Search**: Text search by title, description, or issue number (IID)
- **Filter bar**: Author dropdown, Assignee dropdown, Labels multi-select, Milestone dropdown, Type dropdown
- **Sort dropdown**: Created date, Updated date, Due date, Priority, Popularity, Weight (asc/desc)
- **Pagination**: 20 issues per page, showing "X–Y of Z" with page buttons
- **Bulk selection**: Checkbox per row + select-all; bulk actions bar appears with: Close, Reopen, Assign, Label, Milestone
- **Issue row displays**: Priority indicator, confidential icon, title link, IID, label chips (max 4 + overflow count), type badge, age, author, weight, due date (red if overdue), upvotes, time tracked

### Issue Detail View
- **Title**: Inline-editable (`contenteditable`), save button appears on edit
- **Description**: Markdown-rendered content with edit button; editor is a textarea with save/cancel
- **Sidebar metadata** (right column):
  - **Assignees**: Multi-select searchable dropdown, shows avatar + name list
  - **Labels**: Multi-select searchable dropdown with color swatches
  - **Milestone**: Single-select dropdown (active milestones only)
  - **Iteration**: Single-select dropdown (non-closed iterations)
  - **Epic**: Single-select searchable dropdown (open epics)
  - **Weight**: Numeric input (0–99)
  - **Due date**: Text input (YYYY-MM-DD format)
  - **Confidential**: Toggle switch
  - **Notifications**: Toggle switch (subscribed/unsubscribed)
- **Close / Reopen button** at bottom of sidebar
- **Related Issues section**: Shows blocking/blocked-by/related-to links with issue titles; add/remove related issues via modal
- **Time Tracking section**: Progress bar (spent vs estimated), "Set estimate" and "Log time" buttons open modals for hours/minutes input
- **Activity Feed**: Chronological list of comments and events (status changes, label additions, assignments, time logs); comments shown in card style with markdown rendering
- **Comment Box**: Textarea with slash command hints; supports quick actions

### Issue Creation Form
- **Type dropdown**: Issue, Incident, Task
- **Template dropdown**: Bug Report, Feature Request, Task (pre-fills description)
- **Title**: Required text input
- **Description**: Textarea with markdown support
- **Assignees**: Multi-select searchable dropdown
- **Labels**: Multi-select searchable dropdown
- **Milestone**: Single-select dropdown
- **Iteration**: Single-select dropdown
- **Epic**: Single-select searchable dropdown
- **Weight**: Numeric input
- **Due date**: Text input (YYYY-MM-DD)
- **Confidential**: Checkbox
- **Create / Cancel buttons**; validation requires title

### Boards (Kanban)
- **Board selector**: Dropdown to switch between boards (Development Board, Bug Triage Board)
- **Columns**: Each board has ordered lists (backlog/Open, label-based lists, closed/Done)
- **Issue cards**: Show title, IID, label chips, assignee avatars, weight
- **Drag and drop**: Cards can be dragged between columns; moving updates issue labels and state
- **Add list**: Button to add a new label-based list (via modal with label selector)
- **Remove list**: X button on label-based list headers
- **Create issue from board**: "+ New issue" button at bottom of each column

### Milestones
- **List view**: Active/Closed tabs with counts; each milestone shows title, dates, description, progress bar (% based on closed/open issues)
- **Actions**: Edit (modal), Close/Reopen, Delete (confirmation modal)
- **Create milestone**: Modal with title (required), description, start date, due date
- **Detail view**: Full description, progress bar with stats, tabs for Open/Closed issues within milestone

### Iterations
- **Grouped by cadence**: "Sprint Cycle" (2-week) and "Monthly Planning" (4-week)
- **Each iteration shows**: Title, state badge (current/upcoming/closed), date range, issue count, weight, progress bar
- **Create iteration**: Modal with cadence selector, title, start/end dates
- **Detail view**: Stats row (total issues, completed, remaining, total weight, % complete), progress bar, burndown chart (SVG), Open/Closed issue tabs

### Epics
- **List view**: Open/Closed tabs; epics displayed with hierarchy (child epics indented)
- **Each epic shows**: Title, state badge, label chips, date range, issue count, child epics count, progress bar
- **Create epic**: Modal with title, description, labels multi-select, parent epic dropdown, start/due dates, confidential checkbox
- **Close/Reopen** epic from detail view
- **Detail view**: Description (markdown), progress section, timeline bar (visual progress of start-to-due date), child epics list, issues list, sidebar with labels/dates/confidentiality

### Roadmap
- **Timeline view**: Horizontal bars showing epic and milestone durations
- **Month headers**: Auto-generated across the time range
- **Today marker**: Red vertical line
- **Two sections**: Epics (with progress fill) and Milestones (green bars with progress)
- **Bar labels**: Show completion percentage
- **Clickable**: Bar labels link to epic/milestone detail views
- Only epics/milestones with both start and due dates appear

### Labels Management
- **Scoped labels**: Grouped by scope prefix (priority::, status::, workflow::)
- **Unscoped labels**: Listed separately
- **Each label shows**: Color chip, name, description, issue count
- **Create label**: Modal with name input (supports scoped format "scope::name"), description, color picker (grid of 32 colors + hex input)
- **Edit label**: Modal pre-populated with current values
- **Delete label**: Confirmation modal (removes from all issues)

### Time Tracking
- Available on issue detail view
- **Set estimate**: Modal with hours + minutes inputs
- **Log time**: Modal with hours + minutes inputs; adds time to cumulative spent
- **Display**: Progress bar showing spent vs estimated; over-budget shown in red
- **Via slash commands**: `/estimate Nh` and `/spend NhMm` in comment box

### Quick Actions (Slash Commands)
- Processed in the comment box when submitting a comment
- Supported commands:
  - `/assign @username` — adds assignee
  - `/label ~"label name"` — adds label
  - `/milestone %"milestone title"` — sets milestone
  - `/close` — closes the issue
  - `/reopen` — reopens the issue
  - `/weight N` — sets weight
  - `/due YYYY-MM-DD` — sets due date
  - `/estimate Nh` or `/estimate NhMm` — sets time estimate
  - `/spend Nh` or `/spend NhMm` — logs time spent
- Slash commands are removed from the comment text; remaining text becomes a comment
- Activity entries are created for each action

### Notifications
- **Feed tab**: List of notifications (assigned, mentioned, status changes, label changes, comments, milestone changes)
- **Unread indicator**: Sidebar badge shows unread count; unread items highlighted in feed
- **Mark read**: Individual or "Mark all as read" button
- **Settings tab**:
  - Notification level dropdown: Global, Watch, On mention/participating, Disabled
  - Email notification toggles: New issues, Reassigned, Closed, New comments, Mentioned, Milestone changes

## Data Model

### Users (12 entities)
- Fields: id, username, name, email, avatar, role (Owner/Maintainer/Developer/Reporter), state (active/blocked)
- Current user: Sarah Chen (id: 1, Owner)

### Labels (24 entities)
- Fields: id, name, description, color, textColor, scoped (boolean)
- 10 unscoped labels: bug, feature, enhancement, documentation, security, performance, infrastructure, needs-triage, ready-for-dev, tech-debt, UX, regression, breaking-change
- 11 scoped labels across 3 scopes: priority:: (critical/high/medium/low), status:: (in-progress/review/blocked/done), workflow:: (design/backend/frontend)

### Milestones (6 entities)
- Fields: id, title, description, startDate, dueDate, state (active/closed), createdAt
- States: v4.0 Release (closed), v4.1 Patch (closed), v4.2 Release (active, current), v4.3 Release (active), v5.0 Major Release (active), Backlog (active, no dates)

### Iteration Cadences (2 entities)
- Fields: id, title, description, durationWeeks, autoSchedule, createdAt
- Cadences: Sprint Cycle (2-week), Monthly Planning (4-week)

### Iterations (8 entities)
- Fields: id, cadenceId, title, startDate, endDate, state (closed/current/upcoming), createdAt
- Sprint Cycle: Sprint 22–27 (22–25 closed, 26 current, 27 upcoming)
- Monthly Planning: March 2026 (current), April 2026 (upcoming)

### Epics (12 entities)
- Fields: id, title, description, state (opened/closed), authorId, labels (array of label IDs), confidential, startDate, dueDate, parentEpicId, createdAt, updatedAt
- Hierarchy: "API v3 - Breaking Changes" is child of "API v3 Migration"
- States: 10 open, 2 closed (Performance Optimization Q1, Data Export/Import)
- Key epics: User Authentication Overhaul, API v3 Migration, Mobile Responsive Redesign, CI/CD Pipeline Improvements, Security Audit Remediation, Dark Mode Implementation

### Issues (100 entities)
- Fields: id, iid, title, description, state (opened/closed), type (issue/incident/task), authorId, assignees (array), labels (array), milestoneId, iterationId, epicId, weight, dueDate, confidential, timeEstimate (seconds), timeSpent (seconds), createdAt, updatedAt, closedAt, closedBy, upvotes, downvotes, subscribed, relatedIssues (array of {issueId, linkType}), activities (array)
- 30 hand-crafted issues with full descriptions and activities
- 70 generated issues with realistic titles and varied attributes
- Distribution: ~67 open, ~33 closed
- Types: issue, incident, task
- Related issues use link types: blocks, is_blocked_by, relates_to
- Activities: comments, status_change, label_add, assignment, milestone_change, time_spent

### Boards (2 entities)
- Fields: id, name, createdAt, lists (array of {id, type, labelId, title, position})
- Development Board: Open, To Do (ready-for-dev), In Progress (status::in-progress), Review (status::review), Done
- Bug Triage Board: Open, Critical, High, Medium, Low, Closed

### Issue Templates (3 entities)
- Fields: id, name, content (markdown template)
- Templates: Bug Report, Feature Request, Task

### Notification Settings
- Fields: level (global/watch/participating/disabled), email (object with boolean flags for each event type)

### Notification Feed (10 entities)
- Fields: id, type (assigned/mentioned/status_change/label_change/new_comment/milestone_change), issueId, actorId, message, read, createdAt

## Available Form Controls

### Dropdowns (Custom HTML, no native <select>)
- Single-select dropdowns with optional search
- Multi-select dropdowns with checkmarks and search
- Used for: Author, Assignee, Labels, Milestone, Iteration, Epic, Board selector, Sort, Type, Notification level, Issue template

### Toggles
- Custom toggle switches for: Confidential, Subscribed, Email notification settings

### Text Inputs
- Standard text inputs for: Issue title, Label name, Milestone title, Iteration title, Epic title, Weight (number), Due date (YYYY-MM-DD pattern)
- Textareas for: Issue description, Comment box, Milestone description, Epic description

### Color Picker
- Grid of 32 preset color swatches + hex text input with live preview
- Used in label create/edit modals

### Checkboxes
- Custom styled checkboxes for: Issue selection, Select all, Confidential toggle in create forms

### Date Inputs
- Text-based date inputs (not native date pickers) with YYYY-MM-DD format
- Used for: Due date, Start date, End date (milestones, iterations, epics)

## Seed Data Summary

- **12 users**: Sarah Chen (Owner, current), Marcus Johnson (Maintainer), Priya Patel (Developer), Alex Kim (Developer), Jordan Williams (Developer), Elena Rodriguez (Maintainer), David Thompson (Developer), Lisa Wang (Reporter), Omar Hassan (Developer), Rachel Green (Reporter), Kai Nakamura (Maintainer), Sophie Martin (Developer, blocked)
- **24 labels**: 13 unscoped + 11 scoped across priority/status/workflow scopes
- **6 milestones**: 2 closed (v4.0, v4.1), 3 active with dates (v4.2, v4.3, v5.0), 1 backlog without dates
- **8 iterations**: 6 in Sprint Cycle (4 closed, 1 current, 1 upcoming), 2 in Monthly Planning (1 current, 1 upcoming)
- **12 epics**: 10 open, 2 closed; 1 parent-child relationship; varied date ranges across 2025-2026
- **100 issues**: ~67 open, ~33 closed; varied types (issue/incident/task), weights (1-8), priorities, milestones, iterations, epics; 30 with detailed descriptions and activities
- **2 boards**: Development Board (5 lists), Bug Triage Board (6 lists)
- **3 issue templates**: Bug Report, Feature Request, Task
- **10 notification feed entries**: Mix of assigned, mentioned, status changes, label changes, comments
