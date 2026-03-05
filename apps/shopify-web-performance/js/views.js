// ============================================================
// views.js — View rendering for Shopify Web Performance Dashboard
// ============================================================

const Views = {

    // ---- Sidebar ----
    renderSidebar() {
        const route = AppState.currentRoute;
        return `
            <div class="sidebar ${AppState.sidebarCollapsed ? 'collapsed' : ''}" id="sidebar" data-testid="sidebar">
                <div class="sidebar-header">
                    <div class="sidebar-logo">
                        <svg width="24" height="24" viewBox="0 0 24 24" class="shopify-logo">
                            <path d="M15.34 3.61a.42.42 0 00-.37-.07 .42.42 0 00-.27.25l-.67 1.62-.82-1.62a.42.42 0 00-.57-.18l-2.04 1.11.82 5.48a.21.21 0 01-.18.24h-1.82a.42.42 0 00-.42.42v9.1a.42.42 0 00.42.42h7.56a.42.42 0 00.42-.42V5.86a2.1 2.1 0 00-2.06-2.25z" fill="#95BF47"/>
                            <path d="M15.34 3.61s-.09-.02-.15-.02a2.1 2.1 0 00-1.91 2.27v14.1h4.28a.42.42 0 00.42-.42V5.86a2.1 2.1 0 00-2.06-2.25.42.42 0 00-.58 0z" fill="#5E8E3E"/>
                        </svg>
                        <span class="sidebar-title">Shopify</span>
                    </div>
                </div>
                <nav class="sidebar-nav">
                    <div class="nav-section">
                        <div class="nav-section-title">Online Store</div>
                        <a class="nav-item ${route === 'themes' ? 'active' : ''}"
                           data-action="navigate" data-route="themes" href="#" data-testid="nav-themes">
                            <svg width="18" height="18" viewBox="0 0 18 18"><rect x="2" y="2" width="14" height="14" rx="2" stroke="currentColor" fill="none" stroke-width="1.3"/><line x1="2" y1="6" x2="16" y2="6" stroke="currentColor" stroke-width="1.3"/><line x1="7" y1="6" x2="7" y2="16" stroke="currentColor" stroke-width="1.3"/></svg>
                            <span>Themes</span>
                        </a>
                    </div>
                    <div class="nav-section">
                        <div class="nav-section-title">Analytics</div>
                        <a class="nav-item ${route === 'reports' || route === 'report-detail' ? 'active' : ''}"
                           data-action="navigate" data-route="reports" href="#" data-testid="nav-reports">
                            <svg width="18" height="18" viewBox="0 0 18 18"><rect x="3" y="9" width="3" height="7" rx="0.5" fill="currentColor"/><rect x="7.5" y="5" width="3" height="11" rx="0.5" fill="currentColor"/><rect x="12" y="2" width="3" height="14" rx="0.5" fill="currentColor"/></svg>
                            <span>Reports</span>
                        </a>
                    </div>
                    <div class="nav-section">
                        <div class="nav-section-title">Performance</div>
                        <a class="nav-item ${route === 'improving' ? 'active' : ''}"
                           data-action="navigate" data-route="improving" href="#" data-testid="nav-improving">
                            <svg width="18" height="18" viewBox="0 0 18 18"><path d="M3 14L7 8L11 10L15 3" stroke="currentColor" fill="none" stroke-width="1.5"/><polygon points="14,2 16,2 16,4" fill="currentColor"/></svg>
                            <span>Optimization</span>
                        </a>
                        <a class="nav-item ${route === 'apps' ? 'active' : ''}"
                           data-action="navigate" data-route="apps" href="#" data-testid="nav-apps">
                            <svg width="18" height="18" viewBox="0 0 18 18"><rect x="2" y="2" width="6" height="6" rx="1" stroke="currentColor" fill="none" stroke-width="1.3"/><rect x="10" y="2" width="6" height="6" rx="1" stroke="currentColor" fill="none" stroke-width="1.3"/><rect x="2" y="10" width="6" height="6" rx="1" stroke="currentColor" fill="none" stroke-width="1.3"/><rect x="10" y="10" width="6" height="6" rx="1" stroke="currentColor" fill="none" stroke-width="1.3"/></svg>
                            <span>Apps</span>
                        </a>
                        <a class="nav-item ${route === 'settings' ? 'active' : ''}"
                           data-action="navigate" data-route="settings" href="#" data-testid="nav-settings">
                            <svg width="18" height="18" viewBox="0 0 18 18"><circle cx="9" cy="9" r="2.5" stroke="currentColor" fill="none" stroke-width="1.3"/><path d="M9 2v2M9 14v2M2 9h2M14 9h2M4.2 4.2l1.4 1.4M12.4 12.4l1.4 1.4M4.2 13.8l1.4-1.4M12.4 5.6l1.4-1.4" stroke="currentColor" stroke-width="1.3"/></svg>
                            <span>Settings</span>
                        </a>
                    </div>
                </nav>
                <div class="sidebar-footer">
                    <div class="store-info-mini">
                        <div class="store-avatar">${AppState.storeInfo.name.charAt(0)}</div>
                        <div class="store-details">
                            <div class="store-name-small">${AppState.storeInfo.name}</div>
                            <div class="store-plan">${AppState.storeInfo.plan}</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    // ---- Top Bar ----
    renderTopBar() {
        const route = AppState.currentRoute;
        const pageTitle = route === 'themes' ? 'Themes' :
                         route === 'reports' ? 'Reports' :
                         route === 'report-detail' ? (AppState.getReportById(AppState.currentReportId)?.name || 'Report') :
                         route === 'improving' ? 'Improving Web Performance' :
                         route === 'apps' ? 'Apps & Scripts' :
                         route === 'settings' ? 'Performance Settings' : 'Dashboard';
        return `
            <div class="top-bar" id="top-bar" data-testid="top-bar">
                <div class="top-bar-left">
                    <h1 class="page-title">${pageTitle}</h1>
                </div>
                <div class="top-bar-right">
                    <div class="top-bar-filters">
                        ${Components.dropdown('date-range-filter', [
                            { value: 'today', label: 'Today' },
                            { value: 'last_7_days', label: 'Last 7 days' },
                            { value: 'last_30_days', label: 'Last 30 days' }
                        ], AppState.settings.dateRange, 'Date range')}
                        ${Components.dropdown('device-filter', [
                            { value: 'all', label: 'All devices' },
                            { value: 'desktop', label: 'Desktop' },
                            { value: 'mobile', label: 'Mobile' }
                        ], AppState.settings.deviceFilter, 'Device')}
                    </div>
                </div>
            </div>
        `;
    },

    // ---- Themes Page (with Performance Metric Summary) ----
    renderThemesPage() {
        const activeTheme = AppState.getActiveTheme();
        const metrics = AppState.getCurrentMetricSummary();
        const sessions = AppState.getSessionsForDateRange();

        return `
            <div class="page-content themes-page" data-testid="themes-page">
                ${Components.breadcrumb([
                    { label: 'Online Store', route: 'themes' },
                    { label: 'Themes', route: 'themes' }
                ])}

                <section class="card performance-summary-section" data-testid="performance-summary">
                    <div class="card-header">
                        <h2 class="card-title">Web Performance</h2>
                        <span class="card-subtitle">Core Web Vitals summary</span>
                    </div>
                    <div class="metric-cards-grid">
                        ${Components.metricCard('lcp', 'LCP P75 (ms)', metrics.lcp.value, 'ms', metrics.lcp.ranking, 'open-lcp-report')}
                        ${Components.metricCard('inp', 'INP P75 (ms)', metrics.inp.value, 'ms', metrics.inp.ranking, 'open-inp-report')}
                        ${Components.metricCard('cls', 'Cumulative Layout Shift', metrics.cls.value, '', metrics.cls.ranking, 'open-cls-report')}
                        ${Components.sessionDeviceCard(sessions)}
                    </div>
                </section>

                <section class="card themes-section" data-testid="themes-section">
                    <div class="card-header">
                        <h2 class="card-title">Theme library</h2>
                    </div>
                    <div class="themes-list">
                        ${AppState.themes.map(t => Components.themeCard(t)).join('')}
                    </div>
                </section>
            </div>
        `;
    },

    // ---- Reports List Page ----
    renderReportsPage() {
        const filteredReports = AppState.searchReports(AppState.reportSearchQuery);
        return `
            <div class="page-content reports-page" data-testid="reports-page">
                ${Components.breadcrumb([
                    { label: 'Analytics', route: 'reports' },
                    { label: 'Reports', route: 'reports' }
                ])}

                <div class="reports-search-bar">
                    ${Components.searchInput('report-search', 'Search reports...', AppState.reportSearchQuery)}
                </div>

                <section class="card">
                    <div class="card-header">
                        <h2 class="card-title">Web Performance Reports</h2>
                        <span class="card-subtitle">${filteredReports.length} reports</span>
                    </div>
                    <div class="reports-list">
                        ${filteredReports.map(report => {
                            const typeLabel = report.type === 'over_time' ? 'Over Time' :
                                             report.type === 'by_page_url' ? 'By Page URL' : 'By Page Type';
                            const metricLabel = report.metric === 'lcp' ? 'Largest Contentful Paint' :
                                               report.metric === 'inp' ? 'Interaction to Next Paint' : 'Cumulative Layout Shift';
                            return `
                                <a class="report-list-item" data-action="open-report" data-report-id="${report.id}" href="#" data-testid="report-item-${report.id}">
                                    <div class="report-list-icon">
                                        <svg width="20" height="20" viewBox="0 0 20 20">
                                            ${report.type === 'over_time' ?
                                                '<path d="M3 15L8 8L12 11L17 4" stroke="#5C6AC4" fill="none" stroke-width="1.5"/>' :
                                            report.type === 'by_page_url' ?
                                                '<rect x="3" y="4" width="14" height="12" rx="1" stroke="#5C6AC4" fill="none" stroke-width="1.3"/><line x1="3" y1="8" x2="17" y2="8" stroke="#5C6AC4" stroke-width="1"/>' :
                                                '<rect x="4" y="10" width="3" height="6" fill="#5C6AC4"/><rect x="8.5" y="6" width="3" height="10" fill="#5C6AC4"/><rect x="13" y="3" width="3" height="13" fill="#5C6AC4"/>'
                                            }
                                        </svg>
                                    </div>
                                    <div class="report-list-content">
                                        <div class="report-list-name">${report.name}</div>
                                        <div class="report-list-meta">${metricLabel} &middot; ${typeLabel}</div>
                                    </div>
                                    <svg width="16" height="16" viewBox="0 0 16 16" class="report-list-arrow">
                                        <path d="M6 4L10 8L6 12" stroke="currentColor" fill="none" stroke-width="1.5"/>
                                    </svg>
                                </a>
                            `;
                        }).join('')}
                        ${filteredReports.length === 0 ? Components.emptyState('No reports found', 'Try a different search term.') : ''}
                    </div>
                </section>
            </div>
        `;
    },

    // ---- Report Detail Page ----
    renderReportDetailPage() {
        const report = AppState.getReportById(AppState.currentReportId);
        if (!report) return Components.emptyState('Report not found', 'The report could not be loaded.');

        const metricLabel = report.metric === 'lcp' ? 'Largest Contentful Paint' :
                           report.metric === 'inp' ? 'Interaction to Next Paint' : 'Cumulative Layout Shift';
        const typeLabel = report.type === 'over_time' ? 'Over Time' :
                         report.type === 'by_page_url' ? 'By Page URL' : 'By Page Type';

        let content = '';
        if (report.type === 'over_time') {
            content = this._renderOverTimeReport(report);
        } else if (report.type === 'by_page_url') {
            content = this._renderByPageUrlReport(report);
        } else {
            content = this._renderByPageTypeReport(report);
        }

        return `
            <div class="page-content report-detail-page" data-testid="report-detail-page">
                ${Components.breadcrumb([
                    { label: 'Analytics', route: 'reports' },
                    { label: 'Reports', route: 'reports' },
                    { label: report.name, route: 'report-detail' }
                ])}

                <div class="report-header">
                    <div class="report-header-info">
                        <h2 class="report-title">${report.name}</h2>
                        <div class="report-meta">${metricLabel} &middot; ${typeLabel}</div>
                    </div>
                </div>

                ${content}
            </div>
        `;
    },

    _renderOverTimeReport(report) {
        const data = AppState.getFilteredTimeSeriesForReport(report.id);
        const events = AppState.settings.showAnnotations ? AppState.getEventsForDateRange() : [];

        // Calculate summary
        const values = data.map(d => d.value);
        const avg = values.length > 0 ? (values.reduce((s, v) => s + v, 0) / values.length) : 0;
        const displayAvg = report.metric === 'cls' ? avg.toFixed(2) : Math.round(avg);
        const ranking = AppState.getMetricRanking(report.metric, avg);
        const unit = report.unit === 'ms' ? 'ms' : '';

        return `
            <section class="card report-summary-card">
                <div class="report-summary-row">
                    <div class="report-summary-metric">
                        <span class="report-summary-label">Summary (${AppState.settings.dateRange.replace(/_/g, ' ')})</span>
                        <span class="report-summary-value">${displayAvg}${unit}</span>
                        <span class="report-summary-ranking ranking-${ranking}">${ranking}</span>
                    </div>
                    <div class="report-summary-controls">
                        ${Components.toggle('show-annotations', AppState.settings.showAnnotations, 'Show annotations')}
                    </div>
                </div>
            </section>

            <section class="card chart-card">
                <div class="card-header">
                    <h3 class="card-title">${report.metric.toUpperCase()} over time</h3>
                </div>
                ${Components.lineChart(data, { metric: report.metric, showThresholds: true, events })}
            </section>

            ${events.length > 0 ? `
                <section class="card">
                    ${Components.eventAnnotationList(events)}
                </section>
            ` : ''}

            <section class="card">
                <div class="card-header">
                    <h3 class="card-title">Data Table</h3>
                </div>
                ${this._renderOverTimeDataTable(data, report)}
            </section>
        `;
    },

    _renderOverTimeDataTable(data, report) {
        const columns = [
            { key: 'date', label: 'Date' },
            { key: 'value', label: `P75 (${report.unit})`, align: 'right' },
            { key: 'ranking', label: 'Ranking' }
        ];
        const rows = data.map(d => ({
            date: Components.formatDate(d.date),
            value: report.metric === 'cls' ? d.value.toFixed(3) : d.value,
            ranking: `<span class="ranking-badge ranking-${AppState.getMetricRanking(report.metric, d.value)}">${AppState.getMetricRanking(report.metric, d.value)}</span>`
        }));
        return Components.dataTable(columns, rows, { id: 'over-time-table' });
    },

    _renderByPageUrlReport(report) {
        const pageData = AppState.getPageDataForReport(report.id);
        const searchQuery = AppState.pageSearchQuery;
        const filtered = searchQuery ?
            pageData.filter(p => p.url.toLowerCase().includes(searchQuery.toLowerCase()) || p.title.toLowerCase().includes(searchQuery.toLowerCase())) :
            pageData;
        const unit = report.unit === 'ms' ? 'ms' : '';

        const columns = [
            { key: 'url', label: 'Page Path' },
            { key: 'title', label: 'Page Title' },
            { key: 'value', label: `P75 (${report.unit})`, align: 'right' },
            { key: 'distribution', label: 'Distribution' },
            { key: 'ranking', label: 'Ranking' }
        ];
        const rows = filtered.map(p => ({
            url: p.url,
            title: p.title,
            value: report.metric === 'cls' ? p.p75.toFixed(3) : p.p75,
            distribution: Components.distributionBar(p.distribution),
            ranking: `<span class="ranking-badge ranking-${p.ranking}">${p.ranking}</span>`
        }));

        return `
            <section class="card">
                <div class="card-header">
                    <h3 class="card-title">Performance by Page URL</h3>
                </div>
                <div class="page-url-search">
                    ${Components.searchInput('page-search', 'Filter pages...', searchQuery)}
                </div>
                ${Components.dataTable(columns, rows, { id: 'page-url-table' })}
                ${filtered.length === 0 ? Components.emptyState('No pages match', 'Try a different filter.') : ''}
            </section>
        `;
    },

    _renderByPageTypeReport(report) {
        const typeData = AppState.getPageTypeDataForReport(report.id);
        const unit = report.unit === 'ms' ? 'ms' : '';

        const columns = [
            { key: 'name', label: 'Page Type' },
            { key: 'urlPattern', label: 'URL Pattern' },
            { key: 'value', label: `P75 (${report.unit})`, align: 'right' },
            { key: 'distribution', label: 'Distribution' },
            { key: 'ranking', label: 'Ranking' }
        ];
        const rows = typeData.map(pt => ({
            name: pt.name,
            urlPattern: `<code>${pt.urlPattern}</code>`,
            value: report.metric === 'cls' ? pt.p75.toFixed(3) : pt.p75,
            distribution: Components.distributionBar(pt.distribution),
            ranking: `<span class="ranking-badge ranking-${pt.ranking}">${pt.ranking}</span>`
        }));

        return `
            <section class="card">
                <div class="card-header">
                    <h3 class="card-title">Performance by Page Type</h3>
                </div>
                ${Components.dataTable(columns, rows, { id: 'page-type-table' })}
            </section>
        `;
    },

    // ---- Improving Performance Page ----
    renderImprovingPage() {
        const openRecs = AppState.getOpenRecommendations();
        const highPriority = AppState.getHighPriorityRecommendations();
        const allRecs = AppState.recommendations;
        const impact = AppState.getTotalEstimatedImpact();

        return `
            <div class="page-content improving-page" data-testid="improving-page">
                ${Components.breadcrumb([
                    { label: 'Performance', route: 'improving' },
                    { label: 'Optimization', route: 'improving' }
                ])}

                <section class="card impact-summary-card">
                    <div class="card-header">
                        <h2 class="card-title">Performance Impact Summary</h2>
                    </div>
                    <div class="impact-summary-grid">
                        <div class="impact-stat">
                            <div class="impact-stat-value">${AppState.getStorefrontApps().length}</div>
                            <div class="impact-stat-label">Active storefront apps</div>
                        </div>
                        <div class="impact-stat">
                            <div class="impact-stat-value">${AppState.getActiveTags().length}</div>
                            <div class="impact-stat-label">Active tracking tags</div>
                        </div>
                        <div class="impact-stat warning">
                            <div class="impact-stat-value">+${impact.lcp}ms</div>
                            <div class="impact-stat-label">Estimated LCP impact</div>
                        </div>
                        <div class="impact-stat warning">
                            <div class="impact-stat-value">+${impact.inp}ms</div>
                            <div class="impact-stat-label">Estimated INP impact</div>
                        </div>
                    </div>
                </section>

                <section class="card">
                    <div class="card-header">
                        <h2 class="card-title">Optimization Recommendations</h2>
                        <span class="card-subtitle">${openRecs.length} open &middot; ${highPriority.length} high priority</span>
                    </div>
                    <div class="recommendations-list">
                        ${allRecs.map(r => Components.recommendationCard(r)).join('')}
                    </div>
                </section>

                <section class="card">
                    <div class="card-header">
                        <h2 class="card-title">Built-in Optimizations</h2>
                        <span class="card-subtitle">Already included in your Shopify store</span>
                    </div>
                    <div class="built-in-optimizations">
                        <div class="optimization-item">
                            <span class="opt-check">&#10003;</span>
                            <div>
                                <div class="opt-title">Content Delivery Network (CDN)</div>
                                <div class="opt-desc">Shopify provides a world-class CDN via Cloudflare at no additional charge.</div>
                            </div>
                        </div>
                        <div class="optimization-item">
                            <span class="opt-check">&#10003;</span>
                            <div>
                                <div class="opt-title">Browser Caching</div>
                                <div class="opt-desc">Cacheable resources are set to 1 year, the maximum possible duration.</div>
                            </div>
                        </div>
                        <div class="optimization-item">
                            <span class="opt-check">&#10003;</span>
                            <div>
                                <div class="opt-title">Gzip Compression</div>
                                <div class="opt-desc">CSS, JavaScript, documents and pages are compressed to reduce bandwidth.</div>
                            </div>
                        </div>
                        <div class="optimization-item">
                            <span class="opt-check">&#10003;</span>
                            <div>
                                <div class="opt-title">Image Optimization</div>
                                <div class="opt-desc">JPG images are automatically compressed. Images served in WebP format when supported.</div>
                            </div>
                        </div>
                        <div class="optimization-item">
                            <span class="opt-check">&#10003;</span>
                            <div>
                                <div class="opt-title">File Minification</div>
                                <div class="opt-desc">CSS and JavaScript files are automatically minified when served to your storefront.</div>
                            </div>
                        </div>
                    </div>
                </section>
            </div>
        `;
    },

    // ---- Apps & Scripts Page ----
    renderAppsPage() {
        const sortedApps = [...AppState.apps].sort((a, b) => {
            if (a.status === 'active' && b.status !== 'active') return -1;
            if (a.status !== 'active' && b.status === 'active') return 1;
            const impactOrder = { high: 3, moderate: 2, low: 1, none: 0 };
            return (impactOrder[b.performanceImpact] || 0) - (impactOrder[a.performanceImpact] || 0);
        });

        return `
            <div class="page-content apps-page" data-testid="apps-page">
                ${Components.breadcrumb([
                    { label: 'Performance', route: 'apps' },
                    { label: 'Apps & Scripts', route: 'apps' }
                ])}

                <section class="card">
                    <div class="card-header">
                        <h2 class="card-title">Installed Apps</h2>
                        <span class="card-subtitle">${AppState.apps.length} apps &middot; ${AppState.getActiveApps().length} active</span>
                    </div>
                    <div class="apps-grid">
                        ${sortedApps.map(app => Components.appCard(app)).join('')}
                    </div>
                </section>

                <section class="card">
                    <div class="card-header">
                        <h2 class="card-title">Tag Manager Tags</h2>
                        <span class="card-subtitle">${AppState.tagManagerTags.length} tags &middot; ${AppState.getActiveTags().length} active</span>
                    </div>
                    <div class="tags-list">
                        ${AppState.tagManagerTags.map(tag => Components.tagRow(tag)).join('')}
                    </div>
                </section>
            </div>
        `;
    },

    // ---- Settings Page ----
    renderSettingsPage() {
        const alerts = AppState.settings.performanceAlerts || {};
        return `
            <div class="page-content settings-page" data-testid="settings-page">
                ${Components.breadcrumb([
                    { label: 'Performance', route: 'settings' },
                    { label: 'Settings', route: 'settings' }
                ])}

                <section class="card">
                    <div class="card-header">
                        <h2 class="card-title">Display Preferences</h2>
                    </div>
                    <div class="settings-group">
                        ${Components.dropdown('settings-date-grouping', [
                            { value: 'daily', label: 'Daily' },
                            { value: 'weekly', label: 'Weekly' },
                            { value: 'monthly', label: 'Monthly' }
                        ], AppState.settings.dateGrouping, 'Default date grouping')}
                        ${Components.dropdown('settings-percentile', [
                            { value: 'p50', label: '50th percentile (P50)' },
                            { value: 'p75', label: '75th percentile (P75)' },
                            { value: 'p90', label: '90th percentile (P90)' },
                            { value: 'p95', label: '95th percentile (P95)' }
                        ], AppState.settings.reportPercentile, 'Report percentile')}
                        ${Components.toggle('settings-annotations', AppState.settings.showAnnotations, 'Show event annotations on charts')}
                        ${Components.toggle('settings-comparison', AppState.settings.comparisonEnabled, 'Compare with similar stores')}
                    </div>
                </section>

                <section class="card">
                    <div class="card-header">
                        <h2 class="card-title">Performance Alerts</h2>
                    </div>
                    <div class="settings-group">
                        ${Components.toggle('alert-on-poor', alerts.alertOnPoor !== false, 'Alert when metrics reach Poor ranking')}
                        ${Components.toggle('alert-on-degradation', alerts.alertOnDegradation !== false, 'Alert on significant performance degradation')}
                        ${Components.toggle('alert-email', alerts.emailAlerts !== false, 'Send email alerts')}
                        ${Components.numberInput('alert-lcp-threshold', alerts.lcpThreshold || 2500, 1000, 10000, 'LCP alert threshold', 'ms')}
                        ${Components.numberInput('alert-inp-threshold', alerts.inpThreshold || 200, 50, 2000, 'INP alert threshold', 'ms')}
                        ${Components.numberInput('alert-cls-threshold', alerts.clsThreshold || 0.1, 0.01, 1.0, 'CLS alert threshold', '')}
                        ${Components.numberInput('alert-degradation-pct', alerts.degradationPercent || 15, 5, 50, 'Degradation threshold', '%')}
                    </div>
                </section>

                <section class="card">
                    <div class="card-header">
                        <h2 class="card-title">Store Information</h2>
                    </div>
                    <div class="settings-group store-info-display">
                        <div class="info-row">
                            <span class="info-label">Store name</span>
                            <span class="info-value">${AppState.storeInfo.name}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Domain</span>
                            <span class="info-value">${AppState.storeInfo.customDomain}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Plan</span>
                            <span class="info-value">${AppState.storeInfo.plan}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Timezone</span>
                            <span class="info-value">${AppState.storeInfo.timezone}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Password protected</span>
                            <span class="info-value">${AppState.storeInfo.passwordProtected ? 'Yes' : 'No'}
                                <button class="btn-link btn-xs" data-action="toggle-password-protection">
                                    ${AppState.storeInfo.passwordProtected ? 'Remove' : 'Enable'}
                                </button>
                            </span>
                        </div>
                    </div>
                </section>
            </div>
        `;
    },

    // ---- Main Render ----
    render() {
        const route = AppState.currentRoute;
        let mainContent = '';

        switch (route) {
            case 'themes':
                mainContent = this.renderThemesPage();
                break;
            case 'reports':
                mainContent = this.renderReportsPage();
                break;
            case 'report-detail':
                mainContent = this.renderReportDetailPage();
                break;
            case 'improving':
                mainContent = this.renderImprovingPage();
                break;
            case 'apps':
                mainContent = this.renderAppsPage();
                break;
            case 'settings':
                mainContent = this.renderSettingsPage();
                break;
            default:
                mainContent = this.renderThemesPage();
        }

        return `
            ${this.renderSidebar()}
            <div class="main-area">
                ${this.renderTopBar()}
                <div class="main-content" id="main-content">
                    ${mainContent}
                </div>
            </div>
            ${AppState.toastMessage ? Components.toast(AppState.toastMessage, AppState.toastType) : ''}
            ${AppState.modalOpen ? this._renderActiveModal() : ''}
        `;
    },

    _renderActiveModal() {
        if (AppState.modalOpen === 'confirm-remove-app') {
            const app = AppState.apps.find(a => a.id === AppState.modalData?.appId);
            return Components.modal('confirm-modal', 'Remove App',
                `<p>Are you sure you want to remove <strong>${app ? app.name : 'this app'}</strong>?</p>
                 <p class="modal-warning">Uninstalling an app doesn't automatically remove its code from your theme. You might need to contact the app developer for complete removal.</p>`,
                `<button class="btn-secondary" data-action="close-modal">Cancel</button>
                 <button class="btn-danger" data-action="confirm-remove-app" data-app-id="${AppState.modalData?.appId}">Remove</button>`
            );
        }
        if (AppState.modalOpen === 'confirm-remove-tag') {
            const tag = AppState.tagManagerTags.find(t => t.id === AppState.modalData?.tagId);
            return Components.modal('confirm-modal', 'Remove Tag',
                `<p>Are you sure you want to remove the <strong>${tag ? tag.name : 'this tag'}</strong> from your tag manager?</p>`,
                `<button class="btn-secondary" data-action="close-modal">Cancel</button>
                 <button class="btn-danger" data-action="confirm-remove-tag" data-tag-id="${AppState.modalData?.tagId}">Remove</button>`
            );
        }
        if (AppState.modalOpen === 'confirm-publish-theme') {
            const theme = AppState.themes.find(t => t.id === AppState.modalData?.themeId);
            return Components.modal('confirm-modal', 'Publish Theme',
                `<p>Are you sure you want to publish <strong>${theme ? theme.name : 'this theme'}</strong>?</p>
                 <p>This will replace your current live theme. Publishing a different theme may impact your web performance scores.</p>`,
                `<button class="btn-secondary" data-action="close-modal">Cancel</button>
                 <button class="btn-primary" data-action="confirm-publish-theme" data-theme-id="${AppState.modalData?.themeId}">Publish</button>`
            );
        }
        return '';
    }
};
