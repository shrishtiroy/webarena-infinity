// ============================================================
// components.js — Reusable UI components for Shopify Web Performance
// ============================================================

const Components = {

    // ---- Custom Dropdown ----
    dropdown(id, options, selectedValue, label, attrs = '') {
        const selected = options.find(o => o.value === selectedValue);
        const displayText = selected ? selected.label : 'Select...';
        return `
            <div class="custom-dropdown" id="${id}" data-testid="${id}" ${attrs}>
                <label class="dropdown-label">${label}</label>
                <div class="dropdown-trigger" data-dropdown-id="${id}" tabindex="0">
                    <span class="dropdown-value">${displayText}</span>
                    <span class="dropdown-arrow">
                        <svg width="12" height="12" viewBox="0 0 12 12"><path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" stroke-width="1.5" fill="none"/></svg>
                    </span>
                </div>
                <div class="dropdown-menu" id="${id}-menu">
                    ${options.map(o => `
                        <div class="dropdown-item ${o.value === selectedValue ? 'selected' : ''}"
                             data-dropdown-id="${id}" data-value="${o.value}" tabindex="0">
                            ${o.label}
                            ${o.value === selectedValue ? '<svg width="14" height="14" viewBox="0 0 14 14"><path d="M3 7L6 10L11 4" stroke="#008060" stroke-width="2" fill="none"/></svg>' : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    },

    // ---- Toggle Switch ----
    toggle(id, isChecked, label, attrs = '') {
        return `
            <div class="toggle-row" ${attrs}>
                <span class="toggle-label">${label}</span>
                <button class="toggle-switch ${isChecked ? 'active' : ''}"
                        id="${id}" data-testid="${id}"
                        data-toggle-id="${id}"
                        role="switch" aria-checked="${isChecked}">
                    <span class="toggle-knob"></span>
                </button>
            </div>
        `;
    },

    // ---- Metric Card ----
    metricCard(metric, label, value, unit, ranking, clickAction) {
        const rankClass = ranking === 'good' ? 'ranking-good' :
                         ranking === 'moderate' ? 'ranking-moderate' : 'ranking-poor';
        const rankLabel = ranking.charAt(0).toUpperCase() + ranking.slice(1);
        const displayValue = metric === 'cls' ? value.toFixed(2) : value;
        return `
            <div class="metric-card ${rankClass}" data-action="${clickAction}" data-metric="${metric}" data-testid="metric-card-${metric}" tabindex="0">
                <div class="metric-card-header">
                    <span class="metric-card-label">${label}</span>
                    <span class="metric-card-badge ${rankClass}">${rankLabel}</span>
                </div>
                <div class="metric-card-value">
                    <span class="metric-value-number">${displayValue}</span>
                    ${unit ? `<span class="metric-value-unit">${unit}</span>` : ''}
                </div>
                <div class="metric-card-sublabel">P75 value</div>
            </div>
        `;
    },

    // ---- Session Device Card ----
    sessionDeviceCard(sessions) {
        const total = (sessions.desktop || 0) + (sessions.mobile || 0) + (sessions.tablet || 0);
        const desktopPct = total > 0 ? ((sessions.desktop / total) * 100).toFixed(1) : 0;
        const mobilePct = total > 0 ? ((sessions.mobile / total) * 100).toFixed(1) : 0;
        const tabletPct = total > 0 ? ((sessions.tablet / total) * 100).toFixed(1) : 0;
        return `
            <div class="metric-card session-card" data-action="navigate-sessions-report" data-testid="sessions-device-card" tabindex="0">
                <div class="metric-card-header">
                    <span class="metric-card-label">Sessions by Device Type</span>
                </div>
                <div class="session-bars">
                    <div class="session-bar-row">
                        <span class="session-device-label">
                            <svg width="16" height="16" viewBox="0 0 16 16"><rect x="2" y="2" width="12" height="9" rx="1" stroke="currentColor" fill="none" stroke-width="1.2"/><line x1="5" y1="13" x2="11" y2="13" stroke="currentColor" stroke-width="1.2"/><line x1="8" y1="11" x2="8" y2="13" stroke="currentColor" stroke-width="1.2"/></svg>
                            Desktop
                        </span>
                        <div class="session-bar-track">
                            <div class="session-bar-fill desktop" style="width: ${desktopPct}%"></div>
                        </div>
                        <span class="session-count">${Components.formatNumber(sessions.desktop)} (${desktopPct}%)</span>
                    </div>
                    <div class="session-bar-row">
                        <span class="session-device-label">
                            <svg width="16" height="16" viewBox="0 0 16 16"><rect x="4" y="1" width="8" height="14" rx="1.5" stroke="currentColor" fill="none" stroke-width="1.2"/><line x1="6" y1="12" x2="10" y2="12" stroke="currentColor" stroke-width="1.2"/></svg>
                            Mobile
                        </span>
                        <div class="session-bar-track">
                            <div class="session-bar-fill mobile" style="width: ${mobilePct}%"></div>
                        </div>
                        <span class="session-count">${Components.formatNumber(sessions.mobile)} (${mobilePct}%)</span>
                    </div>
                    <div class="session-bar-row">
                        <span class="session-device-label">
                            <svg width="16" height="16" viewBox="0 0 16 16"><rect x="2" y="2" width="12" height="12" rx="1.5" stroke="currentColor" fill="none" stroke-width="1.2"/><line x1="5" y1="13" x2="11" y2="13" stroke="currentColor" stroke-width="0.8"/></svg>
                            Tablet
                        </span>
                        <div class="session-bar-track">
                            <div class="session-bar-fill tablet" style="width: ${tabletPct}%"></div>
                        </div>
                        <span class="session-count">${Components.formatNumber(sessions.tablet)} (${tabletPct}%)</span>
                    </div>
                </div>
                <div class="session-total">Total: ${Components.formatNumber(total)} sessions</div>
            </div>
        `;
    },

    // ---- Distribution Bar ----
    distributionBar(distribution) {
        const good = distribution.good || 0;
        const moderate = distribution.moderate || 0;
        const poor = distribution.poor || 0;
        return `
            <div class="distribution-bar" data-testid="distribution-bar">
                <div class="distribution-segment good" style="width: ${good}%" title="Good: ${good}%"></div>
                <div class="distribution-segment moderate" style="width: ${moderate}%" title="Moderate: ${moderate}%"></div>
                <div class="distribution-segment poor" style="width: ${poor}%" title="Poor: ${poor}%"></div>
            </div>
            <div class="distribution-labels">
                <span class="dist-label good">${good}% Good</span>
                <span class="dist-label moderate">${moderate}% Moderate</span>
                <span class="dist-label poor">${poor}% Poor</span>
            </div>
        `;
    },

    // ---- Line Chart (SVG) ----
    lineChart(data, options = {}) {
        const { width = 800, height = 250, metric = 'lcp', showThresholds = true, events = [] } = options;
        if (!data || data.length === 0) return '<div class="empty-chart">No data available</div>';

        const padding = { top: 20, right: 40, bottom: 40, left: 60 };
        const chartW = width - padding.left - padding.right;
        const chartH = height - padding.top - padding.bottom;

        const values = data.map(d => d.value);
        const minVal = Math.min(...values) * 0.8;
        const maxVal = Math.max(...values) * 1.15;

        const xScale = (i) => padding.left + (i / (data.length - 1)) * chartW;
        const yScale = (v) => padding.top + chartH - ((v - minVal) / (maxVal - minVal)) * chartH;

        // Build path
        const pathParts = data.map((d, i) => `${i === 0 ? 'M' : 'L'} ${xScale(i).toFixed(1)} ${yScale(d.value).toFixed(1)}`);
        const linePath = pathParts.join(' ');

        // Threshold lines
        let thresholdLines = '';
        if (showThresholds) {
            const thresholds = metric === 'lcp' ? [{ v: 2500, l: 'Good' }, { v: 4000, l: 'Poor' }] :
                              metric === 'inp' ? [{ v: 200, l: 'Good' }, { v: 500, l: 'Poor' }] :
                              [{ v: 0.1, l: 'Good' }, { v: 0.25, l: 'Poor' }];
            for (const t of thresholds) {
                if (t.v >= minVal && t.v <= maxVal) {
                    const y = yScale(t.v);
                    thresholdLines += `<line x1="${padding.left}" y1="${y.toFixed(1)}" x2="${width - padding.right}" y2="${y.toFixed(1)}" stroke="#ddd" stroke-dasharray="4,4" stroke-width="1"/>`;
                    thresholdLines += `<text x="${width - padding.right + 4}" y="${(y + 4).toFixed(1)}" class="chart-threshold-label">${t.l}</text>`;
                }
            }
        }

        // Event annotations
        let eventMarkers = '';
        if (events.length > 0) {
            const dateMap = {};
            data.forEach((d, i) => { dateMap[d.date] = i; });
            events.forEach((evt, idx) => {
                if (dateMap[evt.date] !== undefined) {
                    const x = xScale(dateMap[evt.date]);
                    const color = evt.impact === 'positive' ? '#008060' : evt.impact === 'negative' ? '#D72C0D' : '#5C5F62';
                    eventMarkers += `<line x1="${x.toFixed(1)}" y1="${padding.top}" x2="${x.toFixed(1)}" y2="${(padding.top + chartH).toFixed(1)}" stroke="${color}" stroke-width="1" stroke-dasharray="3,3" opacity="0.6"/>`;
                    eventMarkers += `<circle cx="${x.toFixed(1)}" cy="${padding.top - 6}" r="8" fill="${color}" class="event-marker" data-event-id="${evt.id}"/>`;
                    eventMarkers += `<text x="${x.toFixed(1)}" y="${padding.top - 2}" text-anchor="middle" fill="white" font-size="9" font-weight="bold" class="event-marker-text" data-event-id="${evt.id}">${idx + 1}</text>`;
                }
            });
        }

        // Y-axis labels
        const yTicks = 5;
        let yAxisLabels = '';
        for (let i = 0; i <= yTicks; i++) {
            const val = minVal + (maxVal - minVal) * (i / yTicks);
            const y = yScale(val);
            const label = metric === 'cls' ? val.toFixed(2) : Math.round(val);
            yAxisLabels += `<text x="${padding.left - 8}" y="${(y + 4).toFixed(1)}" text-anchor="end" class="chart-axis-label">${label}</text>`;
            yAxisLabels += `<line x1="${padding.left}" y1="${y.toFixed(1)}" x2="${width - padding.right}" y2="${y.toFixed(1)}" stroke="#f1f1f1" stroke-width="0.5"/>`;
        }

        // X-axis labels (show every Nth label)
        const xLabelInterval = Math.max(1, Math.floor(data.length / 7));
        let xAxisLabels = '';
        data.forEach((d, i) => {
            if (i % xLabelInterval === 0 || i === data.length - 1) {
                const x = xScale(i);
                const dateParts = d.date.split('-');
                const label = `${dateParts[1]}/${dateParts[2]}`;
                xAxisLabels += `<text x="${x.toFixed(1)}" y="${(padding.top + chartH + 20).toFixed(1)}" text-anchor="middle" class="chart-axis-label">${label}</text>`;
            }
        });

        // Data points
        let dataPoints = '';
        data.forEach((d, i) => {
            const x = xScale(i);
            const y = yScale(d.value);
            const displayVal = metric === 'cls' ? d.value.toFixed(3) : d.value;
            dataPoints += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="3" fill="#5C6AC4" class="chart-point" data-date="${d.date}" data-value="${displayVal}"/>`;
        });

        return `
            <div class="chart-container" data-testid="line-chart">
                <svg viewBox="0 0 ${width} ${height}" class="line-chart-svg">
                    ${yAxisLabels}
                    ${xAxisLabels}
                    ${thresholdLines}
                    ${eventMarkers}
                    <path d="${linePath}" fill="none" stroke="#5C6AC4" stroke-width="2" class="chart-line"/>
                    ${dataPoints}
                </svg>
                <div class="chart-tooltip" id="chart-tooltip" style="display:none"></div>
            </div>
        `;
    },

    // ---- Data Table ----
    dataTable(columns, rows, options = {}) {
        const { sortable = true, id = 'data-table' } = options;
        return `
            <div class="data-table-wrapper" id="${id}" data-testid="${id}">
                <table class="data-table">
                    <thead>
                        <tr>
                            ${columns.map(col => `
                                <th class="${sortable ? 'sortable' : ''} ${col.align || ''}"
                                    data-sort-key="${col.key}"
                                    ${sortable ? 'tabindex="0"' : ''}>
                                    ${col.label}
                                    ${sortable ? '<span class="sort-indicator"></span>' : ''}
                                </th>
                            `).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        ${rows.map(row => `
                            <tr>
                                ${columns.map(col => `
                                    <td class="${col.align || ''}">${row[col.key] !== undefined ? row[col.key] : ''}</td>
                                `).join('')}
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    },

    // ---- Event Annotation List ----
    eventAnnotationList(events) {
        if (!events || events.length === 0) return '';
        return `
            <div class="event-annotations" data-testid="event-annotations">
                <h4 class="annotations-title">Store Changes</h4>
                <div class="annotations-list">
                    ${events.map((evt, idx) => {
                        const impactClass = evt.impact === 'positive' ? 'impact-positive' : evt.impact === 'negative' ? 'impact-negative' : 'impact-neutral';
                        const typeIcon = evt.type === 'app_install' ? '&#128230;' :
                                        evt.type === 'app_uninstall' ? '&#128465;' :
                                        evt.type === 'theme_update' || evt.type === 'theme_change' ? '&#127912;' :
                                        evt.type === 'optimization' ? '&#9889;' :
                                        evt.type === 'code_change' ? '&#128187;' :
                                        evt.type === 'app_update' ? '&#128260;' : '&#128204;';
                        return `
                            <div class="annotation-item ${impactClass}" data-event-id="${evt.id}">
                                <span class="annotation-number">${idx + 1}</span>
                                <span class="annotation-icon">${typeIcon}</span>
                                <div class="annotation-content">
                                    <div class="annotation-title">${evt.title}</div>
                                    <div class="annotation-desc">${evt.description}</div>
                                    <div class="annotation-date">${Components.formatDate(evt.date)}</div>
                                </div>
                                <span class="annotation-impact ${impactClass}">
                                    ${evt.impact === 'positive' ? 'Improved' : evt.impact === 'negative' ? 'Degraded' : 'Neutral'}
                                </span>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    },

    // ---- App Card ----
    appCard(app) {
        const impactClass = app.performanceImpact === 'high' ? 'impact-high' :
                           app.performanceImpact === 'moderate' ? 'impact-moderate' :
                           app.performanceImpact === 'low' ? 'impact-low' : 'impact-none';
        return `
            <div class="app-card" data-app-id="${app.id}" data-testid="app-card-${app.id}">
                <div class="app-card-header">
                    <div class="app-card-info">
                        <div class="app-icon" style="background: ${app.status === 'active' ? '#E3F1DF' : '#F1F1F1'}">
                            ${app.name.charAt(0)}
                        </div>
                        <div>
                            <div class="app-name">${app.name}</div>
                            <div class="app-developer">by ${app.developer}</div>
                        </div>
                    </div>
                    <div class="app-status-badge ${app.status}">${app.status}</div>
                </div>
                <div class="app-card-body">
                    <div class="app-description">${app.description}</div>
                    <div class="app-metrics">
                        <span class="app-impact-badge ${impactClass}">
                            Impact: ${app.performanceImpact}
                        </span>
                        ${app.loadsOnStorefront ? `
                            <span class="app-detail">LCP +${app.estimatedLcpImpact}ms</span>
                            <span class="app-detail">INP +${app.estimatedInpImpact}ms</span>
                            <span class="app-detail">${app.scriptsCount} script${app.scriptsCount !== 1 ? 's' : ''}</span>
                        ` : '<span class="app-detail">No storefront scripts</span>'}
                    </div>
                </div>
                <div class="app-card-actions">
                    ${app.status === 'active' ? `
                        <button class="btn-secondary btn-sm" data-action="disable-app" data-app-id="${app.id}">Disable</button>
                    ` : app.status === 'disabled' ? `
                        <button class="btn-secondary btn-sm" data-action="enable-app" data-app-id="${app.id}">Enable</button>
                    ` : ''}
                    <button class="btn-danger btn-sm" data-action="remove-app" data-app-id="${app.id}">Remove</button>
                </div>
            </div>
        `;
    },

    // ---- Recommendation Card ----
    recommendationCard(rec) {
        const priorityClass = rec.priority === 'high' ? 'priority-high' :
                             rec.priority === 'medium' ? 'priority-medium' : 'priority-low';
        const metricLabel = rec.metric === 'lcp' ? 'LCP' : rec.metric === 'inp' ? 'INP' : 'CLS';
        return `
            <div class="recommendation-card ${rec.status === 'resolved' ? 'resolved' : ''}" data-rec-id="${rec.id}" data-testid="rec-${rec.id}">
                <div class="rec-header">
                    <span class="rec-priority-badge ${priorityClass}">${rec.priority}</span>
                    <span class="rec-metric-badge">${metricLabel}</span>
                    ${rec.status === 'resolved' ? '<span class="rec-resolved-badge">Resolved</span>' : ''}
                </div>
                <div class="rec-title">${rec.title}</div>
                <div class="rec-description">${rec.description}</div>
                <div class="rec-footer">
                    <span class="rec-improvement">${rec.estimatedImprovement}</span>
                    <span class="rec-affected">Affects: ${rec.affectedPages.join(', ')}</span>
                </div>
                <div class="rec-actions">
                    ${rec.status === 'open' ? `
                        <button class="btn-primary btn-sm" data-action="resolve-recommendation" data-rec-id="${rec.id}">Mark Resolved</button>
                        <button class="btn-secondary btn-sm" data-action="dismiss-recommendation" data-rec-id="${rec.id}">Dismiss</button>
                    ` : rec.status === 'resolved' ? `
                        <button class="btn-secondary btn-sm" data-action="reopen-recommendation" data-rec-id="${rec.id}">Reopen</button>
                    ` : ''}
                </div>
            </div>
        `;
    },

    // ---- Theme Card ----
    themeCard(theme) {
        const isPublished = theme.role === 'main';
        return `
            <div class="theme-card ${isPublished ? 'published' : ''}" data-theme-id="${theme.id}" data-testid="theme-card-${theme.id}">
                <div class="theme-card-header">
                    <div class="theme-card-info">
                        <div class="theme-name">${theme.name}</div>
                        <div class="theme-meta">
                            v${theme.version} by ${theme.developer}
                            ${isPublished ? ' &middot; <span class="theme-live-badge">Live</span>' : ''}
                        </div>
                    </div>
                    ${!isPublished ? `<button class="btn-primary btn-sm" data-action="publish-theme" data-theme-id="${theme.id}">Publish</button>` : ''}
                </div>
                <div class="theme-card-details">
                    <div class="theme-detail-row">
                        <span class="theme-detail-label">Family:</span>
                        <span class="theme-detail-value">${theme.family}</span>
                    </div>
                    <div class="theme-detail-row">
                        <span class="theme-detail-label">Online Store 2.0:</span>
                        <span class="theme-detail-value">${theme.isOnlineStore2 ? 'Yes' : 'No'}</span>
                    </div>
                    <div class="theme-detail-row">
                        <span class="theme-detail-label">Optimized:</span>
                        <span class="theme-detail-value">${theme.isOptimized ? 'Yes' : 'No'}</span>
                    </div>
                    <div class="theme-detail-row">
                        <span class="theme-detail-label">Animations:</span>
                        <span class="theme-detail-value">
                            ${theme.hasAnimations ? 'Enabled' : 'Disabled'}
                            <button class="btn-link btn-xs" data-action="toggle-animations" data-theme-id="${theme.id}">
                                ${theme.hasAnimations ? 'Disable' : 'Enable'}
                            </button>
                        </span>
                    </div>
                    <div class="theme-detail-row">
                        <span class="theme-detail-label">Page Transitions:</span>
                        <span class="theme-detail-value">
                            ${theme.hasPageTransitions ? 'Enabled' : 'Disabled'}
                            <button class="btn-link btn-xs" data-action="toggle-page-transitions" data-theme-id="${theme.id}">
                                ${theme.hasPageTransitions ? 'Disable' : 'Enable'}
                            </button>
                        </span>
                    </div>
                    <div class="theme-sections">
                        <span class="theme-detail-label">Sections per page:</span>
                        <div class="theme-sections-grid">
                            ${Object.entries(theme.sectionsPerPage).map(([page, count]) => `
                                <div class="section-count-item">
                                    <span class="section-page-label">${page}</span>
                                    <span class="section-count-value" data-testid="sections-${theme.id}-${page}">${count}</span>
                                    <div class="section-count-controls">
                                        <button class="btn-icon btn-xs" data-action="decrease-sections" data-theme-id="${theme.id}" data-page-key="${page}" ${count <= 1 ? 'disabled' : ''}>-</button>
                                        <button class="btn-icon btn-xs" data-action="increase-sections" data-theme-id="${theme.id}" data-page-key="${page}">+</button>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    // ---- Tag Manager Tag Row ----
    tagRow(tag) {
        return `
            <div class="tag-row" data-tag-id="${tag.id}" data-testid="tag-${tag.id}">
                <div class="tag-info">
                    <span class="tag-name">${tag.name}</span>
                    <span class="tag-category">${tag.category}</span>
                    <span class="tag-fire-rate">${tag.fireRate}</span>
                </div>
                <div class="tag-actions">
                    <span class="tag-status-badge ${tag.status}">${tag.status}</span>
                    ${tag.status === 'active' ? `
                        <button class="btn-secondary btn-xs" data-action="deactivate-tag" data-tag-id="${tag.id}">Deactivate</button>
                    ` : `
                        <button class="btn-secondary btn-xs" data-action="activate-tag" data-tag-id="${tag.id}">Activate</button>
                    `}
                    <button class="btn-danger btn-xs" data-action="remove-tag" data-tag-id="${tag.id}">Remove</button>
                </div>
            </div>
        `;
    },

    // ---- Modal ----
    modal(id, title, content, actions = '') {
        return `
            <div class="modal-overlay" id="${id}" data-testid="${id}">
                <div class="modal">
                    <div class="modal-header">
                        <h2 class="modal-title">${title}</h2>
                        <button class="modal-close" data-action="close-modal" aria-label="Close">&times;</button>
                    </div>
                    <div class="modal-body">${content}</div>
                    ${actions ? `<div class="modal-footer">${actions}</div>` : ''}
                </div>
            </div>
        `;
    },

    // ---- Toast Notification ----
    toast(message, type) {
        const icon = type === 'success' ? '<svg width="16" height="16" viewBox="0 0 16 16"><path d="M4 8L7 11L12 5" stroke="white" stroke-width="2" fill="none"/></svg>' :
                    type === 'error' ? '<svg width="16" height="16" viewBox="0 0 16 16"><path d="M4 4L12 12M12 4L4 12" stroke="white" stroke-width="2"/></svg>' :
                    '<svg width="16" height="16" viewBox="0 0 16 16"><circle cx="8" cy="8" r="6" stroke="white" fill="none" stroke-width="1.5"/><line x1="8" y1="5" x2="8" y2="9" stroke="white" stroke-width="1.5"/><circle cx="8" cy="11" r="0.8" fill="white"/></svg>';
        return `
            <div class="toast toast-${type}" data-testid="toast">
                <span class="toast-icon">${icon}</span>
                <span class="toast-message">${message}</span>
                <button class="toast-close" data-action="close-toast">&times;</button>
            </div>
        `;
    },

    // ---- Search Input ----
    searchInput(id, placeholder, value = '') {
        return `
            <div class="search-input-wrapper" data-testid="${id}">
                <svg class="search-icon" width="16" height="16" viewBox="0 0 16 16">
                    <circle cx="7" cy="7" r="4.5" stroke="currentColor" fill="none" stroke-width="1.5"/>
                    <line x1="10.5" y1="10.5" x2="14" y2="14" stroke="currentColor" stroke-width="1.5"/>
                </svg>
                <input type="text" class="search-input" id="${id}" placeholder="${placeholder}" value="${value}" data-search-id="${id}">
            </div>
        `;
    },

    // ---- Breadcrumb ----
    breadcrumb(items) {
        return `
            <nav class="breadcrumb" data-testid="breadcrumb">
                ${items.map((item, i) => {
                    const isLast = i === items.length - 1;
                    return isLast ?
                        `<span class="breadcrumb-current">${item.label}</span>` :
                        `<a class="breadcrumb-link" data-action="navigate" data-route="${item.route}" href="#">${item.label}</a>
                         <span class="breadcrumb-separator">/</span>`;
                }).join('')}
            </nav>
        `;
    },

    // ---- Empty State ----
    emptyState(title, description) {
        return `
            <div class="empty-state" data-testid="empty-state">
                <svg width="48" height="48" viewBox="0 0 48 48" class="empty-icon">
                    <circle cx="24" cy="24" r="22" stroke="#8C9196" fill="none" stroke-width="1.5"/>
                    <line x1="16" y1="20" x2="32" y2="20" stroke="#8C9196" stroke-width="1.5"/>
                    <line x1="16" y1="26" x2="28" y2="26" stroke="#8C9196" stroke-width="1.5"/>
                    <line x1="16" y1="32" x2="24" y2="32" stroke="#8C9196" stroke-width="1.5"/>
                </svg>
                <h3 class="empty-title">${title}</h3>
                <p class="empty-description">${description}</p>
            </div>
        `;
    },

    // ---- Number Input ----
    numberInput(id, value, min, max, label, unit = '') {
        return `
            <div class="number-input-group" data-testid="${id}">
                <label class="number-input-label">${label}</label>
                <div class="number-input-wrapper">
                    <input type="text" class="number-input" id="${id}" value="${value}"
                           data-min="${min}" data-max="${max}" data-number-id="${id}">
                    ${unit ? `<span class="number-input-unit">${unit}</span>` : ''}
                </div>
            </div>
        `;
    },

    // ---- Utility Functions ----

    formatNumber(n) {
        if (n === undefined || n === null) return '0';
        return n.toLocaleString();
    },

    formatDate(dateStr) {
        const d = new Date(dateStr + 'T00:00:00Z');
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        return `${months[d.getUTCMonth()]} ${d.getUTCDate()}, ${d.getUTCFullYear()}`;
    },

    formatDateTime(dateStr) {
        const d = new Date(dateStr);
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        return `${months[d.getUTCMonth()]} ${d.getUTCDate()}, ${d.getUTCFullYear()} ${d.getUTCHours()}:${String(d.getUTCMinutes()).padStart(2, '0')}`;
    }
};
