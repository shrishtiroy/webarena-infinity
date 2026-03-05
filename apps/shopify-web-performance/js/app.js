// ============================================================
// app.js — Event handling and routing for Shopify Web Performance Dashboard
// ============================================================

const App = {
    init() {
        AppState.init();
        AppState.subscribe(() => this.renderApp());
        this.renderApp();
        AppState._pushStateToServer();
        this._setupSSE();
        this._setupGlobalListeners();
    },

    renderApp() {
        const appEl = document.getElementById('app');
        if (!appEl) return;
        appEl.innerHTML = Views.render();
        this._afterRender();
    },

    _afterRender() {
        // Close any open dropdowns that shouldn't be open
        // Scroll to top on route change
    },

    // ---- SSE ----
    _setupSSE() {
        const eventSource = new EventSource('/api/events');
        eventSource.onmessage = (e) => {
            if (e.data === 'reset') {
                AppState.resetToSeedData();
            }
        };
        eventSource.onerror = () => {
            // Silently reconnect
        };
    },

    // ---- Global Event Listeners ----
    _setupGlobalListeners() {
        document.addEventListener('click', (e) => this._handleClick(e));
        document.addEventListener('input', (e) => this._handleInput(e));
        document.addEventListener('change', (e) => this._handleChange(e));
        document.addEventListener('keydown', (e) => this._handleKeydown(e));
        document.addEventListener('mouseover', (e) => this._handleMouseover(e));
        document.addEventListener('mouseout', (e) => this._handleMouseout(e));
    },

    // ---- Click Handler ----
    _handleClick(e) {
        const target = e.target;

        // Close any open dropdowns when clicking outside
        if (!target.closest('.custom-dropdown')) {
            this._closeAllDropdowns();
        }

        // Close toast
        if (target.closest('[data-action="close-toast"]')) {
            AppState.toastMessage = null;
            this.renderApp();
            return;
        }

        // Dropdown trigger
        const dropdownTrigger = target.closest('.dropdown-trigger');
        if (dropdownTrigger) {
            e.preventDefault();
            const dropdownId = dropdownTrigger.dataset.dropdownId;
            this._toggleDropdown(dropdownId);
            return;
        }

        // Dropdown item selection
        const dropdownItem = target.closest('.dropdown-item');
        if (dropdownItem) {
            e.preventDefault();
            const dropdownId = dropdownItem.dataset.dropdownId;
            const value = dropdownItem.dataset.value;
            this._handleDropdownSelect(dropdownId, value);
            return;
        }

        // Toggle switch
        const toggleBtn = target.closest('.toggle-switch');
        if (toggleBtn) {
            e.preventDefault();
            const toggleId = toggleBtn.dataset.toggleId;
            this._handleToggle(toggleId);
            return;
        }

        // Data action buttons
        const actionEl = target.closest('[data-action]');
        if (actionEl) {
            e.preventDefault();
            this._handleAction(actionEl);
            return;
        }

        // Sort header click
        const sortHeader = target.closest('th.sortable');
        if (sortHeader) {
            const key = sortHeader.dataset.sortKey;
            this._handleSort(key);
            return;
        }

        // Chart point hover (click on mobile)
        const chartPoint = target.closest('.chart-point');
        if (chartPoint) {
            this._showChartTooltip(chartPoint);
            return;
        }
    },

    // ---- Input Handler ----
    _handleInput(e) {
        const target = e.target;

        // Search inputs
        if (target.id === 'report-search') {
            AppState.reportSearchQuery = target.value;
            this.renderApp();
            // Restore focus and cursor position
            const el = document.getElementById('report-search');
            if (el) { el.focus(); el.selectionStart = el.selectionEnd = target.selectionStart; }
            return;
        }
        if (target.id === 'page-search') {
            AppState.pageSearchQuery = target.value;
            this.renderApp();
            const el = document.getElementById('page-search');
            if (el) { el.focus(); el.selectionStart = el.selectionEnd = target.selectionStart; }
            return;
        }

        // Number inputs
        if (target.classList.contains('number-input')) {
            // Handled on blur/change
            return;
        }
    },

    // ---- Change Handler ----
    _handleChange(e) {
        const target = e.target;

        // Number inputs — apply on change/blur
        if (target.classList.contains('number-input')) {
            const id = target.dataset.numberId;
            const min = parseFloat(target.dataset.min);
            const max = parseFloat(target.dataset.max);
            let val = parseFloat(target.value);
            if (isNaN(val)) val = min;
            val = Math.max(min, Math.min(max, val));
            target.value = val;
            this._handleNumberInput(id, val);
            return;
        }
    },

    // ---- Keydown Handler ----
    _handleKeydown(e) {
        // Enter on dropdown trigger
        if (e.key === 'Enter') {
            const dropdownTrigger = e.target.closest('.dropdown-trigger');
            if (dropdownTrigger) {
                e.preventDefault();
                const dropdownId = dropdownTrigger.dataset.dropdownId;
                this._toggleDropdown(dropdownId);
                return;
            }
            const dropdownItem = e.target.closest('.dropdown-item');
            if (dropdownItem) {
                e.preventDefault();
                const dropdownId = dropdownItem.dataset.dropdownId;
                const value = dropdownItem.dataset.value;
                this._handleDropdownSelect(dropdownId, value);
                return;
            }
            // Enter on number input
            if (e.target.classList.contains('number-input')) {
                e.target.dispatchEvent(new Event('change'));
                return;
            }
        }

        // Escape closes modals and dropdowns
        if (e.key === 'Escape') {
            if (AppState.modalOpen) {
                AppState.modalOpen = null;
                AppState.modalData = null;
                this.renderApp();
                return;
            }
            this._closeAllDropdowns();
        }
    },

    // ---- Mouseover/Mouseout for chart tooltips ----
    _handleMouseover(e) {
        const point = e.target.closest('.chart-point');
        if (point) {
            this._showChartTooltip(point);
        }
        const eventMarker = e.target.closest('.event-marker, .event-marker-text');
        if (eventMarker) {
            this._showEventTooltip(eventMarker);
        }
    },

    _handleMouseout(e) {
        const tooltip = document.getElementById('chart-tooltip');
        if (tooltip) tooltip.style.display = 'none';
    },

    _showChartTooltip(point) {
        const tooltip = document.getElementById('chart-tooltip');
        if (!tooltip) return;
        const date = point.dataset.date;
        const value = point.dataset.value;
        tooltip.innerHTML = `<strong>${Components.formatDate(date)}</strong><br>Value: ${value}`;
        const rect = point.getBoundingClientRect();
        const container = point.closest('.chart-container').getBoundingClientRect();
        tooltip.style.left = (rect.left - container.left + 10) + 'px';
        tooltip.style.top = (rect.top - container.top - 40) + 'px';
        tooltip.style.display = 'block';
    },

    _showEventTooltip(marker) {
        const eventId = marker.dataset.eventId;
        const evt = AppState.performanceEvents.find(e => e.id === eventId);
        if (!evt) return;
        const tooltip = document.getElementById('chart-tooltip');
        if (!tooltip) return;
        tooltip.innerHTML = `<strong>${evt.title}</strong><br>${evt.description}<br><em>${Components.formatDate(evt.date)}</em>`;
        const rect = marker.getBoundingClientRect();
        const container = marker.closest('.chart-container').getBoundingClientRect();
        tooltip.style.left = (rect.left - container.left + 10) + 'px';
        tooltip.style.top = (rect.top - container.top - 60) + 'px';
        tooltip.style.display = 'block';
    },

    // ---- Dropdown Logic ----
    _toggleDropdown(dropdownId) {
        const dropdown = document.getElementById(dropdownId);
        if (!dropdown) return;
        const menu = dropdown.querySelector('.dropdown-menu');
        if (!menu) return;
        const isOpen = menu.classList.contains('open');
        this._closeAllDropdowns();
        if (!isOpen) {
            menu.classList.add('open');
        }
    },

    _closeAllDropdowns() {
        document.querySelectorAll('.dropdown-menu.open').forEach(m => m.classList.remove('open'));
    },

    _handleDropdownSelect(dropdownId, value) {
        this._closeAllDropdowns();

        switch (dropdownId) {
            case 'date-range-filter':
                AppState.updateSetting('dateRange', value);
                break;
            case 'device-filter':
                AppState.updateSetting('deviceFilter', value);
                break;
            case 'settings-date-grouping':
                AppState.updateSetting('dateGrouping', value);
                break;
            case 'settings-percentile':
                AppState.updateSetting('reportPercentile', value);
                break;
            default:
                break;
        }
    },

    // ---- Toggle Logic ----
    _handleToggle(toggleId) {
        switch (toggleId) {
            case 'show-annotations':
                AppState.updateSetting('showAnnotations', !AppState.settings.showAnnotations);
                break;
            case 'settings-annotations':
                AppState.updateSetting('showAnnotations', !AppState.settings.showAnnotations);
                break;
            case 'settings-comparison':
                AppState.updateSetting('comparisonEnabled', !AppState.settings.comparisonEnabled);
                break;
            case 'alert-on-poor':
                AppState.updatePerformanceAlert('alertOnPoor', !(AppState.settings.performanceAlerts?.alertOnPoor !== false));
                break;
            case 'alert-on-degradation':
                AppState.updatePerformanceAlert('alertOnDegradation', !(AppState.settings.performanceAlerts?.alertOnDegradation !== false));
                break;
            case 'alert-email':
                AppState.updatePerformanceAlert('emailAlerts', !(AppState.settings.performanceAlerts?.emailAlerts !== false));
                break;
            default:
                break;
        }
    },

    // ---- Number Input Logic ----
    _handleNumberInput(id, value) {
        switch (id) {
            case 'alert-lcp-threshold':
                AppState.updatePerformanceAlert('lcpThreshold', value);
                break;
            case 'alert-inp-threshold':
                AppState.updatePerformanceAlert('inpThreshold', value);
                break;
            case 'alert-cls-threshold':
                AppState.updatePerformanceAlert('clsThreshold', value);
                break;
            case 'alert-degradation-pct':
                AppState.updatePerformanceAlert('degradationPercent', value);
                break;
            default:
                break;
        }
    },

    // ---- Action Dispatcher ----
    _handleAction(el) {
        const action = el.dataset.action;

        switch (action) {
            // Navigation
            case 'navigate': {
                const route = el.dataset.route;
                AppState.currentRoute = route;
                AppState.currentReportId = null;
                AppState.pageSearchQuery = '';
                this.renderApp();
                window.scrollTo(0, 0);
                break;
            }

            // Open specific reports from metric cards
            case 'open-lcp-report':
                AppState.currentRoute = 'report-detail';
                AppState.currentReportId = 'report_lcp_time';
                this.renderApp();
                window.scrollTo(0, 0);
                break;
            case 'open-inp-report':
                AppState.currentRoute = 'report-detail';
                AppState.currentReportId = 'report_inp_time';
                this.renderApp();
                window.scrollTo(0, 0);
                break;
            case 'open-cls-report':
                AppState.currentRoute = 'report-detail';
                AppState.currentReportId = 'report_cls_time';
                this.renderApp();
                window.scrollTo(0, 0);
                break;
            case 'navigate-sessions-report':
                // Navigate to reports list
                AppState.currentRoute = 'reports';
                this.renderApp();
                window.scrollTo(0, 0);
                break;

            // Open report from list
            case 'open-report': {
                const reportId = el.dataset.reportId;
                AppState.currentRoute = 'report-detail';
                AppState.currentReportId = reportId;
                AppState.pageSearchQuery = '';
                this.renderApp();
                window.scrollTo(0, 0);
                break;
            }

            // App actions
            case 'disable-app': {
                const appId = el.dataset.appId;
                AppState.updateAppStatus(appId, 'disabled');
                this._showToast('App disabled', 'success');
                break;
            }
            case 'enable-app': {
                const appId = el.dataset.appId;
                AppState.updateAppStatus(appId, 'active');
                this._showToast('App enabled', 'success');
                break;
            }
            case 'remove-app': {
                const appId = el.dataset.appId;
                AppState.modalOpen = 'confirm-remove-app';
                AppState.modalData = { appId };
                this.renderApp();
                break;
            }
            case 'confirm-remove-app': {
                const appId = el.dataset.appId;
                AppState.removeApp(appId);
                AppState.modalOpen = null;
                AppState.modalData = null;
                this._showToast('App removed', 'success');
                break;
            }

            // Tag actions
            case 'activate-tag': {
                const tagId = el.dataset.tagId;
                AppState.updateTagStatus(tagId, 'active');
                this._showToast('Tag activated', 'success');
                break;
            }
            case 'deactivate-tag': {
                const tagId = el.dataset.tagId;
                AppState.updateTagStatus(tagId, 'inactive');
                this._showToast('Tag deactivated', 'success');
                break;
            }
            case 'remove-tag': {
                const tagId = el.dataset.tagId;
                AppState.modalOpen = 'confirm-remove-tag';
                AppState.modalData = { tagId };
                this.renderApp();
                break;
            }
            case 'confirm-remove-tag': {
                const tagId = el.dataset.tagId;
                AppState.removeTag(tagId);
                AppState.modalOpen = null;
                AppState.modalData = null;
                this._showToast('Tag removed', 'success');
                break;
            }

            // Theme actions
            case 'publish-theme': {
                const themeId = el.dataset.themeId;
                AppState.modalOpen = 'confirm-publish-theme';
                AppState.modalData = { themeId };
                this.renderApp();
                break;
            }
            case 'confirm-publish-theme': {
                const themeId = el.dataset.themeId;
                AppState.publishTheme(themeId);
                AppState.modalOpen = null;
                AppState.modalData = null;
                this._showToast('Theme published', 'success');
                break;
            }
            case 'toggle-animations': {
                const themeId = el.dataset.themeId;
                AppState.toggleThemeAnimations(themeId);
                const theme = AppState.themes.find(t => t.id === themeId);
                this._showToast(`Animations ${theme?.hasAnimations ? 'enabled' : 'disabled'}`, 'info');
                break;
            }
            case 'toggle-page-transitions': {
                const themeId = el.dataset.themeId;
                AppState.toggleThemePageTransitions(themeId);
                const theme = AppState.themes.find(t => t.id === themeId);
                this._showToast(`Page transitions ${theme?.hasPageTransitions ? 'enabled' : 'disabled'}`, 'info');
                break;
            }
            case 'increase-sections': {
                const themeId = el.dataset.themeId;
                const pageKey = el.dataset.pageKey;
                const theme = AppState.themes.find(t => t.id === themeId);
                if (theme) {
                    const current = theme.sectionsPerPage[pageKey] || 0;
                    AppState.updateThemeSections(themeId, pageKey, current + 1);
                }
                break;
            }
            case 'decrease-sections': {
                const themeId = el.dataset.themeId;
                const pageKey = el.dataset.pageKey;
                const theme = AppState.themes.find(t => t.id === themeId);
                if (theme) {
                    const current = theme.sectionsPerPage[pageKey] || 1;
                    if (current > 1) {
                        AppState.updateThemeSections(themeId, pageKey, current - 1);
                    }
                }
                break;
            }

            // Recommendation actions
            case 'resolve-recommendation': {
                const recId = el.dataset.recId;
                AppState.updateRecommendationStatus(recId, 'resolved');
                this._showToast('Recommendation marked as resolved', 'success');
                break;
            }
            case 'dismiss-recommendation': {
                const recId = el.dataset.recId;
                AppState.updateRecommendationStatus(recId, 'dismissed');
                this._showToast('Recommendation dismissed', 'info');
                break;
            }
            case 'reopen-recommendation': {
                const recId = el.dataset.recId;
                AppState.updateRecommendationStatus(recId, 'open');
                this._showToast('Recommendation reopened', 'info');
                break;
            }

            // Store settings
            case 'toggle-password-protection': {
                AppState.updateStoreInfo('passwordProtected', !AppState.storeInfo.passwordProtected);
                const status = AppState.storeInfo.passwordProtected ? 'enabled' : 'removed';
                this._showToast(`Password protection ${status}`, 'success');
                break;
            }

            // Modal
            case 'close-modal':
                AppState.modalOpen = null;
                AppState.modalData = null;
                this.renderApp();
                break;

            default:
                break;
        }
    },

    // ---- Sort ----
    _handleSort(key) {
        if (AppState.sortColumn === key) {
            AppState.sortDirection = AppState.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            AppState.sortColumn = key;
            AppState.sortDirection = 'asc';
        }
        this.renderApp();
    },

    // ---- Toast ----
    _showToast(message, type = 'info') {
        AppState.toastMessage = message;
        AppState.toastType = type;
        this.renderApp();
        setTimeout(() => {
            AppState.toastMessage = null;
            AppState.toastType = null;
            this.renderApp();
        }, 3000);
    }
};

// ---- Initialize on DOM ready ----
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
