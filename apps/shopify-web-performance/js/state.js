// ============================================================
// state.js — Centralized state management for Shopify Web Performance Dashboard
// ============================================================

const AppState = {
    // ---- Persistent State ----
    storeInfo: null,
    currentUser: null,
    themes: [],
    apps: [],
    tagManagerTags: [],
    pages: [],
    pageTypes: [],
    pagePerformance: {},
    pageTypePerformance: {},
    performanceEvents: [],
    sessionsByDevice: {},
    overallPerformance: {},
    recommendations: [],
    reports: [],
    settings: {},
    lcpOverTimeDesktop: [],
    lcpOverTimeMobile: [],
    inpOverTimeDesktop: [],
    inpOverTimeMobile: [],
    clsOverTimeDesktop: [],
    clsOverTimeMobile: [],

    // ---- UI State (not persisted) ----
    currentRoute: 'themes',
    currentReportId: null,
    sidebarCollapsed: false,
    modalOpen: null,
    modalData: null,
    toastMessage: null,
    toastType: null,
    reportSearchQuery: '',
    pageSearchQuery: '',
    sortColumn: null,
    sortDirection: 'asc',
    expandedSections: ['web-performance-summary'],
    selectedAppId: null,
    selectedRecommendationId: null,

    // ---- Listeners ----
    _listeners: [],

    subscribe(fn) {
        this._listeners.push(fn);
    },

    notify() {
        this._persist();
        this._pushStateToServer();
        for (const fn of this._listeners) {
            try { fn(); } catch (e) { console.error('Listener error:', e); }
        }
    },

    // ---- Initialization ----

    init() {
        const persisted = this._loadPersistedData();
        if (persisted) {
            this.storeInfo = persisted.storeInfo || {};
            this.currentUser = persisted.currentUser || {};
            this.themes = persisted.themes || [];
            this.apps = persisted.apps || [];
            this.tagManagerTags = persisted.tagManagerTags || [];
            this.pages = persisted.pages || [];
            this.pageTypes = persisted.pageTypes || [];
            this.pagePerformance = persisted.pagePerformance || {};
            this.pageTypePerformance = persisted.pageTypePerformance || {};
            this.performanceEvents = persisted.performanceEvents || [];
            this.sessionsByDevice = persisted.sessionsByDevice || {};
            this.overallPerformance = persisted.overallPerformance || {};
            this.recommendations = persisted.recommendations || [];
            this.reports = persisted.reports || [];
            this.settings = persisted.settings || {};
            this.lcpOverTimeDesktop = persisted.lcpOverTimeDesktop || [];
            this.lcpOverTimeMobile = persisted.lcpOverTimeMobile || [];
            this.inpOverTimeDesktop = persisted.inpOverTimeDesktop || [];
            this.inpOverTimeMobile = persisted.inpOverTimeMobile || [];
            this.clsOverTimeDesktop = persisted.clsOverTimeDesktop || [];
            this.clsOverTimeMobile = persisted.clsOverTimeMobile || [];
        } else {
            this._loadSeedData();
        }
    },

    _loadSeedData() {
        this.storeInfo = JSON.parse(JSON.stringify(STORE_INFO));
        this.currentUser = JSON.parse(JSON.stringify(CURRENT_USER));
        this.themes = JSON.parse(JSON.stringify(THEMES));
        this.apps = JSON.parse(JSON.stringify(APPS));
        this.tagManagerTags = JSON.parse(JSON.stringify(TAG_MANAGER_TAGS));
        this.pages = JSON.parse(JSON.stringify(PAGES));
        this.pageTypes = JSON.parse(JSON.stringify(PAGE_TYPES));
        this.pagePerformance = JSON.parse(JSON.stringify(PAGE_PERFORMANCE));
        this.pageTypePerformance = JSON.parse(JSON.stringify(PAGE_TYPE_PERFORMANCE));
        this.performanceEvents = JSON.parse(JSON.stringify(PERFORMANCE_EVENTS));
        this.sessionsByDevice = JSON.parse(JSON.stringify(SESSIONS_BY_DEVICE));
        this.overallPerformance = JSON.parse(JSON.stringify(OVERALL_PERFORMANCE));
        this.recommendations = JSON.parse(JSON.stringify(RECOMMENDATIONS));
        this.reports = JSON.parse(JSON.stringify(REPORTS));
        this.settings = JSON.parse(JSON.stringify(SETTINGS));
        this.lcpOverTimeDesktop = JSON.parse(JSON.stringify(LCP_OVER_TIME_DESKTOP));
        this.lcpOverTimeMobile = JSON.parse(JSON.stringify(LCP_OVER_TIME_MOBILE));
        this.inpOverTimeDesktop = JSON.parse(JSON.stringify(INP_OVER_TIME_DESKTOP));
        this.inpOverTimeMobile = JSON.parse(JSON.stringify(INP_OVER_TIME_MOBILE));
        this.clsOverTimeDesktop = JSON.parse(JSON.stringify(CLS_OVER_TIME_DESKTOP));
        this.clsOverTimeMobile = JSON.parse(JSON.stringify(CLS_OVER_TIME_MOBILE));
    },

    _loadPersistedData() {
        try {
            const saved = localStorage.getItem('shopifyWebPerfState');
            if (!saved) return null;
            const parsed = JSON.parse(saved);
            if (parsed._seedVersion !== SEED_DATA_VERSION) {
                localStorage.removeItem('shopifyWebPerfState');
                return null;
            }
            return parsed;
        } catch (e) {
            return null;
        }
    },

    // ---- Persistence ----

    _persist() {
        const state = this.getSerializableState();
        localStorage.setItem('shopifyWebPerfState', JSON.stringify(state));
    },

    _pushStateToServer() {
        const state = this.getSerializableState();
        fetch('/api/state', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(state)
        }).catch(() => {});
    },

    getSerializableState() {
        return {
            _seedVersion: SEED_DATA_VERSION,
            storeInfo: this.storeInfo,
            currentUser: this.currentUser,
            themes: this.themes,
            apps: this.apps,
            tagManagerTags: this.tagManagerTags,
            pages: this.pages,
            pageTypes: this.pageTypes,
            pagePerformance: this.pagePerformance,
            pageTypePerformance: this.pageTypePerformance,
            performanceEvents: this.performanceEvents,
            sessionsByDevice: this.sessionsByDevice,
            overallPerformance: this.overallPerformance,
            recommendations: this.recommendations,
            reports: this.reports,
            settings: this.settings,
            lcpOverTimeDesktop: this.lcpOverTimeDesktop,
            lcpOverTimeMobile: this.lcpOverTimeMobile,
            inpOverTimeDesktop: this.inpOverTimeDesktop,
            inpOverTimeMobile: this.inpOverTimeMobile,
            clsOverTimeDesktop: this.clsOverTimeDesktop,
            clsOverTimeMobile: this.clsOverTimeMobile,
        };
    },

    resetToSeedData() {
        localStorage.removeItem('shopifyWebPerfState');
        this._loadSeedData();
        this.currentRoute = 'themes';
        this.currentReportId = null;
        this.modalOpen = null;
        this.modalData = null;
        this.toastMessage = null;
        this.reportSearchQuery = '';
        this.pageSearchQuery = '';
        this.sortColumn = null;
        this.sortDirection = 'asc';
        this.notify();
    },

    // ---- Settings Mutations ----

    updateSetting(key, value) {
        if (key.includes('.')) {
            const parts = key.split('.');
            let obj = this.settings;
            for (let i = 0; i < parts.length - 1; i++) {
                if (!obj[parts[i]]) obj[parts[i]] = {};
                obj = obj[parts[i]];
            }
            obj[parts[parts.length - 1]] = value;
        } else {
            this.settings[key] = value;
        }
        this.notify();
    },

    // ---- App Mutations ----

    updateAppStatus(appId, status) {
        const app = this.apps.find(a => a.id === appId);
        if (!app) return;
        app.status = status;
        if (status === 'disabled') {
            app.loadsOnStorefront = false;
        } else if (status === 'active') {
            app.loadsOnStorefront = app.scriptsCount > 0;
        }
        this.notify();
    },

    removeApp(appId) {
        this.apps = this.apps.filter(a => a.id !== appId);
        this.notify();
    },

    // ---- Tag Manager Mutations ----

    updateTagStatus(tagId, status) {
        const tag = this.tagManagerTags.find(t => t.id === tagId);
        if (!tag) return;
        tag.status = status;
        this.notify();
    },

    removeTag(tagId) {
        this.tagManagerTags = this.tagManagerTags.filter(t => t.id !== tagId);
        this.notify();
    },

    // ---- Theme Mutations ----

    publishTheme(themeId) {
        for (const theme of this.themes) {
            if (theme.id === themeId) {
                theme.role = 'main';
                theme.status = 'published';
            } else if (theme.role === 'main') {
                theme.role = 'unpublished';
                theme.status = 'unpublished';
            }
        }
        this.settings.selectedThemeId = themeId;
        this.notify();
    },

    updateThemeSections(themeId, pageKey, count) {
        const theme = this.themes.find(t => t.id === themeId);
        if (!theme) return;
        theme.sectionsPerPage[pageKey] = count;
        this.notify();
    },

    toggleThemeAnimations(themeId) {
        const theme = this.themes.find(t => t.id === themeId);
        if (!theme) return;
        theme.hasAnimations = !theme.hasAnimations;
        this.notify();
    },

    toggleThemePageTransitions(themeId) {
        const theme = this.themes.find(t => t.id === themeId);
        if (!theme) return;
        theme.hasPageTransitions = !theme.hasPageTransitions;
        this.notify();
    },

    // ---- Recommendation Mutations ----

    updateRecommendationStatus(recId, status) {
        const rec = this.recommendations.find(r => r.id === recId);
        if (!rec) return;
        rec.status = status;
        this.notify();
    },

    // ---- Performance Alert Settings ----

    updatePerformanceAlert(key, value) {
        if (!this.settings.performanceAlerts) {
            this.settings.performanceAlerts = {};
        }
        this.settings.performanceAlerts[key] = value;
        this.notify();
    },

    // ---- Store Info Mutations ----

    updateStoreInfo(key, value) {
        this.storeInfo[key] = value;
        this.notify();
    },

    // ---- Query Helpers ----

    getActiveTheme() {
        return this.themes.find(t => t.role === 'main');
    },

    getActiveApps() {
        return this.apps.filter(a => a.status === 'active');
    },

    getStorefrontApps() {
        return this.apps.filter(a => a.status === 'active' && a.loadsOnStorefront);
    },

    getActiveTags() {
        return this.tagManagerTags.filter(t => t.status === 'active');
    },

    getReportById(id) {
        return this.reports.find(r => r.id === id);
    },

    getPageById(id) {
        return this.pages.find(p => p.id === id);
    },

    getRecommendationsByMetric(metric) {
        return this.recommendations.filter(r => r.metric === metric);
    },

    getOpenRecommendations() {
        return this.recommendations.filter(r => r.status === 'open');
    },

    getHighPriorityRecommendations() {
        return this.recommendations.filter(r => r.priority === 'high' && r.status === 'open');
    },

    searchReports(query) {
        if (!query) return this.reports;
        const q = query.toLowerCase().trim();
        return this.reports.filter(r =>
            r.name.toLowerCase().includes(q) ||
            r.metric.toLowerCase().includes(q) ||
            r.type.replace(/_/g, ' ').includes(q)
        );
    },

    searchPages(query) {
        if (!query) return this.pages;
        const q = query.toLowerCase().trim();
        return this.pages.filter(p =>
            p.url.toLowerCase().includes(q) ||
            p.title.toLowerCase().includes(q) ||
            p.pageType.toLowerCase().includes(q)
        );
    },

    // ---- Performance Metric Helpers ----

    getMetricRanking(metric, value) {
        if (metric === 'lcp') {
            if (value <= 2500) return 'good';
            if (value < 4000) return 'moderate';
            return 'poor';
        }
        if (metric === 'inp') {
            if (value <= 200) return 'good';
            if (value < 500) return 'moderate';
            return 'poor';
        }
        if (metric === 'cls') {
            if (value <= 0.1) return 'good';
            if (value < 0.25) return 'moderate';
            return 'poor';
        }
        return 'unknown';
    },

    getCurrentMetricSummary() {
        const dateRange = this.settings.dateRange;
        const device = this.settings.deviceFilter;

        // Get the latest LCP/INP/CLS values based on filters
        const lcpData = device === 'mobile' ? this.lcpOverTimeMobile :
                        device === 'desktop' ? this.lcpOverTimeDesktop :
                        this.lcpOverTimeDesktop; // 'all' uses desktop as primary
        const inpData = device === 'mobile' ? this.inpOverTimeMobile :
                        device === 'desktop' ? this.inpOverTimeDesktop :
                        this.inpOverTimeDesktop;
        const clsData = device === 'mobile' ? this.clsOverTimeMobile :
                        device === 'desktop' ? this.clsOverTimeDesktop :
                        this.clsOverTimeDesktop;

        let days = 7;
        if (dateRange === 'today') days = 1;
        else if (dateRange === 'last_30_days') days = 30;

        const lcpSlice = lcpData.slice(-days);
        const inpSlice = inpData.slice(-days);
        const clsSlice = clsData.slice(-days);

        const avgLcp = lcpSlice.length > 0 ? Math.round(lcpSlice.reduce((s, d) => s + d.value, 0) / lcpSlice.length) : 0;
        const avgInp = inpSlice.length > 0 ? Math.round(inpSlice.reduce((s, d) => s + d.value, 0) / inpSlice.length) : 0;
        const avgCls = clsSlice.length > 0 ? parseFloat((clsSlice.reduce((s, d) => s + d.value, 0) / clsSlice.length).toFixed(2)) : 0;

        return {
            lcp: { value: avgLcp, ranking: this.getMetricRanking('lcp', avgLcp), unit: 'ms' },
            inp: { value: avgInp, ranking: this.getMetricRanking('inp', avgInp), unit: 'ms' },
            cls: { value: avgCls, ranking: this.getMetricRanking('cls', avgCls), unit: '' }
        };
    },

    getTimeSeriesForReport(reportId) {
        const report = this.getReportById(reportId);
        if (!report) return [];
        const device = this.settings.deviceFilter;

        if (report.metric === 'lcp') {
            if (device === 'mobile') return this.lcpOverTimeMobile;
            return this.lcpOverTimeDesktop;
        }
        if (report.metric === 'inp') {
            if (device === 'mobile') return this.inpOverTimeMobile;
            return this.inpOverTimeDesktop;
        }
        if (report.metric === 'cls') {
            if (device === 'mobile') return this.clsOverTimeMobile;
            return this.clsOverTimeDesktop;
        }
        return [];
    },

    getFilteredTimeSeriesForReport(reportId) {
        const data = this.getTimeSeriesForReport(reportId);
        const dateRange = this.settings.dateRange;
        let days = 7;
        if (dateRange === 'today') days = 1;
        else if (dateRange === 'last_30_days') days = 30;
        return data.slice(-days);
    },

    getPageDataForReport(reportId) {
        const report = this.getReportById(reportId);
        if (!report) return [];
        const device = this.settings.deviceFilter === 'mobile' ? 'mobile' : 'desktop';
        const metric = report.metric;

        return this.pages.map(page => {
            const perf = this.pagePerformance[page.id];
            if (!perf) return null;
            const devicePerf = perf[device];
            const metricData = devicePerf[metric];
            return {
                ...page,
                p75: metricData.p75,
                distribution: metricData.distribution,
                ranking: this.getMetricRanking(metric, metricData.p75)
            };
        }).filter(Boolean).sort((a, b) => b.p75 - a.p75);
    },

    getPageTypeDataForReport(reportId) {
        const report = this.getReportById(reportId);
        if (!report) return [];
        const device = this.settings.deviceFilter === 'mobile' ? 'mobile' : 'desktop';
        const metric = report.metric;

        return this.pageTypes.map(pt => {
            const perf = this.pageTypePerformance[pt.id];
            if (!perf) return null;
            const devicePerf = perf[device];
            const metricData = devicePerf[metric];
            return {
                ...pt,
                p75: metricData.p75,
                distribution: metricData.distribution,
                ranking: this.getMetricRanking(metric, metricData.p75)
            };
        }).filter(Boolean).sort((a, b) => b.p75 - a.p75);
    },

    getSessionsForDateRange() {
        const dateRange = this.settings.dateRange;
        if (dateRange === 'today') return this.sessionsByDevice.today;
        if (dateRange === 'last_30_days') return this.sessionsByDevice.last30d;
        return this.sessionsByDevice.last7d;
    },

    getEventsForDateRange() {
        const dateRange = this.settings.dateRange;
        const now = new Date('2026-03-02');
        let cutoff = new Date(now);
        if (dateRange === 'today') cutoff.setDate(cutoff.getDate() - 1);
        else if (dateRange === 'last_7_days') cutoff.setDate(cutoff.getDate() - 7);
        else cutoff.setDate(cutoff.getDate() - 30);
        const cutoffStr = cutoff.toISOString().split('T')[0];
        return this.performanceEvents.filter(e => e.date >= cutoffStr);
    },

    getTotalEstimatedImpact() {
        const storefrontApps = this.getStorefrontApps();
        return {
            lcp: storefrontApps.reduce((s, a) => s + (a.estimatedLcpImpact || 0), 0),
            inp: storefrontApps.reduce((s, a) => s + (a.estimatedInpImpact || 0), 0)
        };
    }
};
