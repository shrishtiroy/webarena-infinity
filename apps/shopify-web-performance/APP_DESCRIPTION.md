# Shopify Web Performance Dashboard

## Summary

A faithful replica of Shopify's web performance dashboard, allowing store owners to monitor and optimize their online store's Core Web Vitals (Largest Contentful Paint, Interaction to Next Paint, and Cumulative Layout Shift). The app provides performance metric summaries, detailed reports (over time, by page URL, by page type), optimization recommendations, app/script management, and theme configuration — all tied to realistic e-commerce store data.

## Main Sections/Pages

### 1. Themes Page (default landing)
- **Web Performance metric summary**: Shows all 3 Core Web Vitals (LCP, INP, CLS) as cards with P75 values and Good/Moderate/Poor rankings
- **Sessions by Device Type**: Desktop, Mobile, Tablet session counts with bar chart
- **Theme Library**: Lists all installed themes with details, publish/unpublish actions, animation/transition toggles, and sections-per-page controls

### 2. Reports Page
- **Report list**: All 9 web performance reports searchable by keyword
- Reports are organized by metric (LCP, INP, CLS) and type (Over Time, Page URL, Page Type)

### 3. Report Detail Page
- **Over Time reports**: SVG line chart with threshold lines, event annotations, summary score, data table
- **By Page URL reports**: Table of all pages with P75 values, distribution bars (good/moderate/poor), ranking badges, page filter/search
- **By Page Type reports**: Table of page types (home, product, collection, cart, blog, page, search, account, checkout) with distribution bars and rankings

### 4. Optimization Page
- **Performance Impact Summary**: Count of active storefront apps, active tags, total estimated LCP/INP impact
- **Optimization Recommendations**: 10 recommendations with priority (high/medium/low), metric (LCP/INP/CLS), description, estimated improvement, affected pages, resolve/dismiss/reopen actions
- **Built-in Optimizations**: Lists 5 Shopify-included optimizations (CDN, caching, gzip, image optimization, minification)

### 5. Apps & Scripts Page
- **Installed Apps**: 15 apps with status, performance impact, LCP/INP impact estimates, scripts count, enable/disable/remove actions
- **Tag Manager Tags**: 10 tags with status, category, fire rate, activate/deactivate/remove actions

### 6. Settings Page
- **Display Preferences**: Date grouping dropdown, report percentile dropdown, show annotations toggle, comparison toggle
- **Performance Alerts**: Alert thresholds for LCP/INP/CLS, degradation percent, toggle for poor alerts, degradation alerts, email alerts
- **Store Information**: Store name, domain, plan, timezone, password protection toggle

## Implemented Features and UI Interactions

### Navigation
- Sidebar navigation with sections: Online Store (Themes), Analytics (Reports), Performance (Optimization, Apps, Settings)
- Breadcrumb navigation on all pages
- Route-based rendering (themes, reports, report-detail, improving, apps, settings)

### Filters (Top Bar, persistent across pages)
- **Date range dropdown**: Today, Last 7 days, Last 30 days
- **Device filter dropdown**: All devices, Desktop, Mobile

### Metric Summary Cards
- Click LCP card → opens LCP Over Time report
- Click INP card → opens INP Over Time report
- Click CLS card → opens CLS Over Time report
- Click Sessions card → navigates to Reports list

### Reports
- Search/filter reports by keyword
- Over Time reports show SVG line charts with:
  - Data points with hover tooltips
  - Threshold lines (Good/Poor boundaries)
  - Event annotation markers (numbered circles with colors)
  - Toggle to show/hide annotations
- By Page URL reports show filterable data table with search
- By Page Type reports show data table
- All tables show distribution bars (green/yellow/red segments)

### Theme Management
- View theme details (version, developer, family, OS2.0 status, optimization status)
- **Publish theme**: Confirmation modal, switches live theme
- **Toggle animations**: Enable/disable animations per theme
- **Toggle page transitions**: Enable/disable page transitions per theme
- **Sections per page**: Increase/decrease section counts per page type (home, product, collection, cart, blog) with +/- buttons

### App Management
- **Disable app**: Sets app to disabled, removes storefront loading
- **Enable app**: Sets app back to active
- **Remove app**: Confirmation modal with warning about residual code

### Tag Manager
- **Activate tag**: Sets tag to active
- **Deactivate tag**: Sets tag to inactive
- **Remove tag**: Confirmation modal, removes from list

### Recommendations
- **Mark Resolved**: Changes status to resolved (card dims)
- **Dismiss**: Changes status to dismissed
- **Reopen**: Reopens a resolved recommendation

### Settings
- All dropdowns and toggles update state and persist
- Number inputs for alert thresholds (LCP ms, INP ms, CLS score, degradation %)
- **Toggle password protection**: Toggles store password protection

### Modals
- Confirm remove app
- Confirm remove tag
- Confirm publish theme

### Toast Notifications
- Success/info/error toasts on actions (auto-dismiss after 3s)

### State Persistence
- All data persisted to localStorage on every mutation
- Seed data version stamp for invalidation
- State pushed to server on every mutation via PUT /api/state

## Data Model

### Store Info
- id, name, domain, customDomain, plan, currency, timezone, passwordProtected, createdAt

### Current User
- id, name, email, role, avatarColor

### Themes (3 entries)
- id, name, role (main/unpublished), version, developer, family, isOnlineStore2, isOptimized, installedAt, updatedAt, sectionsPerPage (object: home/product/collection/cart/blog → count), hasPageTransitions, hasAnimations, status

### Apps (15 entries)
- id, name, developer, category, installedAt, status (active/disabled), performanceImpact (none/low/moderate/high), estimatedLcpImpact (ms), estimatedInpImpact (ms), loadsOnStorefront, scriptsCount, description

### Tag Manager Tags (10 entries)
- id, name, status (active/inactive), category, fireRate, addedAt

### Pages (40 entries)
- id, url, title, pageType, visits30d, visits7d, visitsToday

### Page Types (9 types)
- id, name, urlPattern
- Types: home, product, collection, cart, blog, page, search, account, checkout

### Page Performance (per page)
- desktop/mobile → lcp/inp/cls → p75 value + distribution (good/moderate/poor percentages)

### Page Type Performance (per type)
- Same structure as page performance

### Time Series Data (30 days each)
- LCP over time (desktop + mobile): date → value (ms)
- INP over time (desktop + mobile): date → value (ms)
- CLS over time (desktop + mobile): date → value (score)

### Performance Events (12 entries)
- id, date, type (theme_update/app_install/app_uninstall/optimization/code_change/app_update/theme_change), title, description, impact (positive/negative/neutral)

### Sessions by Device
- Three time ranges (today, last7d, last30d) → desktop/mobile/tablet counts

### Overall Performance
- score, comparisonScore, comparisonLabel, percentile, trend

### Recommendations (10 entries)
- id, priority (high/medium/low), metric (lcp/inp/cls), title, description, category, estimatedImprovement, status (open/resolved/dismissed), affectedPages

### Reports (9 entries)
- id, name, metric (lcp/inp/cls), type (over_time/by_page_url/by_page_type), unit

### Settings
- dateRange, deviceFilter, reportPercentile, dateGrouping, showAnnotations, selectedThemeId, comparisonEnabled, notificationsEnabled
- performanceAlerts: lcpThreshold, inpThreshold, clsThreshold, alertOnPoor, alertOnDegradation, emailAlerts, degradationPercent

## Navigation Structure

```
Sidebar:
├── Online Store
│   └── Themes → themes page (metric summary + theme library)
├── Analytics
│   └── Reports → reports list → click report → report detail
└── Performance
    ├── Optimization → recommendations + built-in optimizations
    ├── Apps → installed apps + tag manager tags
    └── Settings → display prefs + alert settings + store info
```

## Available Form Controls

### Dropdowns
- **Date range**: Today, Last 7 days, Last 30 days
- **Device filter**: All devices, Desktop, Mobile
- **Date grouping** (settings): Daily, Weekly, Monthly
- **Report percentile** (settings): P50, P75, P90, P95

### Toggles
- Show event annotations on charts
- Compare with similar stores
- Alert when metrics reach Poor ranking
- Alert on significant performance degradation
- Send email alerts
- Theme animations (per theme)
- Theme page transitions (per theme)

### Number Inputs
- LCP alert threshold (1000–10000 ms)
- INP alert threshold (50–2000 ms)
- CLS alert threshold (0.01–1.0)
- Degradation threshold (5–50 %)

### Buttons
- Publish theme
- Enable/Disable theme animations
- Enable/Disable theme page transitions
- Increase/Decrease sections per page (+/- buttons)
- Enable/Disable app
- Remove app
- Activate/Deactivate tag
- Remove tag
- Mark recommendation Resolved/Dismiss/Reopen
- Toggle password protection

### Search Inputs
- Report search (reports page)
- Page URL filter (by page URL reports)

## Seed Data Summary

### Store
- **Evergreen Outdoor Co.** — Shopify Plus store selling outdoor/hiking gear
- Domain: www.evergreenoutdoor.com
- Owner: Jordan Mitchell

### Themes (3)
1. **Horizon - Outdoors** v14.2.0 (published, by Shopify, optimized)
2. **Dawn (backup)** v12.0.0 (unpublished, by Shopify, optimized)
3. **Prestige** v9.1.3 (unpublished, by Maestrooo, not optimized, has page transitions)

### Apps (15)
- Active apps with storefront impact: Klaviyo, Judge.me, GA4, Meta Pixel, Shopify Inbox, Recharge, Privy, Yotpo, Hotjar, Bold Product Options, TikTok, Back in Stock
- Active app without storefront impact: Shippo
- Disabled apps: SEO Manager, Infinite Options

### Tags (10)
- Active: GA4, Meta Pixel, Google Ads, TikTok, Hotjar, Microsoft Clarity, Affirm
- Inactive: Pinterest, Snapchat, Lucky Orange

### Pages (40)
- 15 product pages (hiking boots, jackets, tents, water bottles, etc.)
- 8 collection pages (hiking footwear, camping gear, winter essentials, etc.)
- 1 cart page, 3 blog pages, 5 static pages, 1 search page, 2 account pages

### Performance Events (12)
- Mix of theme updates, app installs/uninstalls, optimizations, code changes
- Dates spanning Feb 2–Mar 1, 2026

### Recommendations (10)
- 3 high priority, 4 medium priority, 3 low priority
- 9 open, 1 resolved
- Covering LCP, INP, and CLS improvements
