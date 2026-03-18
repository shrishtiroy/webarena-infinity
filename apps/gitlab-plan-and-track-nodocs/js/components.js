/* ============================================================
   GitLab Plan & Track — Reusable Components
   ============================================================ */

const Components = {

    // ── Escaping ───────────────────────────────────────────
    escapeHtml(str) {
        if (str == null) return '';
        return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
    },

    escapeAttr(str) {
        if (str == null) return '';
        return String(str).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
    },

    // ── Avatars ────────────────────────────────────────────
    avatar(user, size = 32) {
        if (!user) return `<span class="avatar" style="width:${size}px;height:${size}px;font-size:${size*0.4}px">?</span>`;
        const initials = user.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
        const colors = ['#e74c3c','#3498db','#2ecc71','#f39c12','#9b59b6','#1abc9c','#e67e22','#34495e','#e91e63','#00bcd4','#8bc34a','#ff5722'];
        const color = colors[user.id % colors.length];
        return `<span class="avatar" style="width:${size}px;height:${size}px;font-size:${size*0.4}px;background:${color}" title="${this.escapeAttr(user.name)}">${initials}</span>`;
    },

    // ── Badges ─────────────────────────────────────────────
    badge(text, type = 'default') {
        return `<span class="badge badge-${type}">${this.escapeHtml(text)}</span>`;
    },

    stateBadge(state) {
        if (state === 'opened') return '<span class="badge badge-open">Open</span>';
        if (state === 'closed') return '<span class="badge badge-closed">Closed</span>';
        return this.badge(state);
    },

    typeBadge(type) {
        const icons = { issue: '&#9679;', incident: '&#9888;', task: '&#9745;' };
        return `<span class="badge badge-type badge-type-${type}">${icons[type] || ''} ${this.escapeHtml(type)}</span>`;
    },

    labelChip(label) {
        if (!label) return '';
        return `<span class="label-chip" style="background:${label.color};color:${label.textColor}" title="${this.escapeAttr(label.description)}">${this.escapeHtml(label.name)}</span>`;
    },

    priorityIcon(labels) {
        const prioLabels = labels.filter(lid => [11,12,13,14].includes(lid));
        if (prioLabels.length === 0) return '';
        const map = { 11: { cls: 'critical', text: '!!' }, 12: { cls: 'high', text: '!' }, 13: { cls: 'medium', text: '-' }, 14: { cls: 'low', text: '...' } };
        const p = map[prioLabels[0]];
        return p ? `<span class="priority-indicator priority-${p.cls}" title="Priority: ${p.cls}">${p.text}</span>` : '';
    },

    // ── Custom Dropdown ────────────────────────────────────
    dropdown(id, options, selectedValue, opts = {}) {
        const { placeholder = 'Select...', searchable = false, multi = false, small = false } = opts;
        const selected = options.find(o => o.value === selectedValue);
        const displayText = selected ? selected.label : placeholder;
        const sizeClass = small ? 'dropdown-sm' : '';
        return `
            <div class="custom-dropdown ${sizeClass}" id="${id}" data-dropdown-id="${id}" data-value="${this.escapeAttr(selectedValue || '')}">
                <div class="dropdown-trigger" tabindex="0">
                    <span class="dropdown-display">${this.escapeHtml(displayText)}</span>
                    <span class="dropdown-arrow">&#9662;</span>
                </div>
                <div class="dropdown-menu" style="display:none">
                    ${searchable ? `<div class="dropdown-search-wrap"><input type="text" class="dropdown-search" placeholder="Search..." data-dropdown-search="${id}"></div>` : ''}
                    <div class="dropdown-items">
                        ${options.map(o => `
                            <div class="dropdown-item${o.value === selectedValue ? ' selected' : ''}" data-value="${this.escapeAttr(o.value)}" data-dropdown-for="${id}">
                                ${o.color ? `<span class="dropdown-item-color" style="background:${o.color}"></span>` : ''}
                                <span class="dropdown-item-label">${this.escapeHtml(o.label)}</span>
                                ${o.description ? `<span class="dropdown-item-desc">${this.escapeHtml(o.description)}</span>` : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>`;
    },

    multiSelectDropdown(id, options, selectedValues, opts = {}) {
        const { placeholder = 'Select...', searchable = true } = opts;
        const selectedLabels = options.filter(o => selectedValues.includes(o.value)).map(o => o.label);
        const displayText = selectedLabels.length > 0 ? selectedLabels.join(', ') : placeholder;
        return `
            <div class="custom-dropdown multi-dropdown" id="${id}" data-dropdown-id="${id}" data-multi="true">
                <div class="dropdown-trigger" tabindex="0">
                    <span class="dropdown-display">${this.escapeHtml(displayText)}</span>
                    <span class="dropdown-arrow">&#9662;</span>
                </div>
                <div class="dropdown-menu" style="display:none">
                    ${searchable ? `<div class="dropdown-search-wrap"><input type="text" class="dropdown-search" placeholder="Search..." data-dropdown-search="${id}"></div>` : ''}
                    <div class="dropdown-items">
                        ${options.map(o => `
                            <div class="dropdown-item${selectedValues.includes(o.value) ? ' selected' : ''}" data-value="${this.escapeAttr(o.value)}" data-dropdown-for="${id}" data-multi-item="true">
                                <span class="dropdown-check">${selectedValues.includes(o.value) ? '&#10003;' : ''}</span>
                                ${o.color ? `<span class="dropdown-item-color" style="background:${o.color}"></span>` : ''}
                                <span class="dropdown-item-label">${this.escapeHtml(o.label)}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>`;
    },

    // ── Modal ──────────────────────────────────────────────
    showModal(title, bodyHtml, footerHtml, opts = {}) {
        const overlay = document.getElementById('modalOverlay');
        const container = document.getElementById('modalContainer');
        if (!overlay || !container) return;
        const { width = '560px' } = opts;
        container.style.maxWidth = width;
        container.innerHTML = `
            <div class="modal-header">
                <h3>${this.escapeHtml(title)}</h3>
                <button class="modal-close" data-action="closeModal">&times;</button>
            </div>
            <div class="modal-body">${bodyHtml}</div>
            ${footerHtml ? `<div class="modal-footer">${footerHtml}</div>` : ''}
        `;
        overlay.classList.add('active');
    },

    closeModal() {
        const overlay = document.getElementById('modalOverlay');
        if (overlay) overlay.classList.remove('active');
        AppState.activeModal = null;
        AppState.modalData = null;
    },

    confirm(title, message, onConfirm, opts = {}) {
        const { confirmText = 'Confirm', confirmClass = 'btn-danger' } = opts;
        this.showModal(title,
            `<p>${message}</p>`,
            `<button class="btn btn-secondary" data-action="closeModal">Cancel</button>
             <button class="btn ${confirmClass}" data-action="confirmAction">${confirmText}</button>`
        );
        window._pendingConfirmAction = onConfirm;
    },

    // ── Toast ──────────────────────────────────────────────
    showToast(message, type = 'info', duration = 4000) {
        const container = document.getElementById('toastContainer');
        if (!container) return;
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `<span>${this.escapeHtml(message)}</span><button class="toast-close">&times;</button>`;
        container.appendChild(toast);
        toast.querySelector('.toast-close').onclick = () => toast.remove();
        setTimeout(() => { if (toast.parentNode) toast.remove(); }, duration);
    },

    // ── Tabs ───────────────────────────────────────────────
    tabs(id, items, activeTab) {
        return `<div class="tabs" id="${id}">
            ${items.map(t => `
                <button class="tab-btn${t.key === activeTab ? ' active' : ''}" data-tab="${t.key}" data-tab-group="${id}">
                    ${this.escapeHtml(t.label)}${t.count !== undefined ? ` <span class="tab-count">${t.count}</span>` : ''}
                </button>
            `).join('')}
        </div>`;
    },

    // ── Search ─────────────────────────────────────────────
    searchInput(id, value, placeholder = 'Search...') {
        return `<div class="search-input-wrap">
            <span class="search-icon">&#128269;</span>
            <input type="text" class="search-input" id="${id}" value="${this.escapeAttr(value || '')}" placeholder="${placeholder}" data-search-id="${id}">
        </div>`;
    },

    // ── Pagination ─────────────────────────────────────────
    pagination(currentPage, totalPages, total) {
        if (totalPages <= 1) return '';
        let pages = '';
        const maxVisible = 7;
        let start = Math.max(1, currentPage - 3);
        let end = Math.min(totalPages, start + maxVisible - 1);
        if (end - start < maxVisible - 1) start = Math.max(1, end - maxVisible + 1);

        pages += `<button class="page-btn${currentPage === 1 ? ' disabled' : ''}" data-page="${currentPage - 1}" ${currentPage === 1 ? 'disabled' : ''}>&laquo; Prev</button>`;
        if (start > 1) {
            pages += `<button class="page-btn" data-page="1">1</button>`;
            if (start > 2) pages += '<span class="page-ellipsis">...</span>';
        }
        for (let p = start; p <= end; p++) {
            pages += `<button class="page-btn${p === currentPage ? ' active' : ''}" data-page="${p}">${p}</button>`;
        }
        if (end < totalPages) {
            if (end < totalPages - 1) pages += '<span class="page-ellipsis">...</span>';
            pages += `<button class="page-btn" data-page="${totalPages}">${totalPages}</button>`;
        }
        pages += `<button class="page-btn${currentPage === totalPages ? ' disabled' : ''}" data-page="${currentPage + 1}" ${currentPage === totalPages ? 'disabled' : ''}>Next &raquo;</button>`;

        return `<div class="pagination">
            <span class="pagination-info">Showing ${(currentPage-1)*AppState.issuesPerPage + 1}–${Math.min(currentPage*AppState.issuesPerPage, total)} of ${total}</span>
            <div class="pagination-controls">${pages}</div>
        </div>`;
    },

    // ── Progress Bar ───────────────────────────────────────
    progressBar(percentage, opts = {}) {
        const { showLabel = true, size = 'normal', color = '#2ecc71' } = opts;
        return `<div class="progress-bar progress-bar-${size}">
            <div class="progress-fill" style="width:${percentage}%;background:${color}"></div>
            ${showLabel ? `<span class="progress-label">${percentage}%</span>` : ''}
        </div>`;
    },

    // ── Time tracking bar ──────────────────────────────────
    timeTrackingBar(estimate, spent) {
        if (!estimate && !spent) return '<span class="text-muted">No time tracked</span>';
        const estStr = estimate ? this.formatDuration(estimate) : 'None';
        const spentStr = spent ? this.formatDuration(spent) : '0h';
        const pct = estimate ? Math.min(100, Math.round((spent / estimate) * 100)) : 0;
        const overBudget = estimate && spent > estimate;
        return `<div class="time-tracking">
            <div class="time-tracking-bar">
                <div class="time-tracking-fill${overBudget ? ' over-budget' : ''}" style="width:${pct}%"></div>
            </div>
            <div class="time-tracking-labels">
                <span>Spent: ${spentStr}</span>
                <span>Est: ${estStr}</span>
            </div>
        </div>`;
    },

    // ── Form Components ────────────────────────────────────
    formField(id, label, inputHtml, opts = {}) {
        const { helpText, error, required } = opts;
        return `<div class="form-field${error ? ' has-error' : ''}" id="field-${id}">
            <label class="form-label" for="${id}">${this.escapeHtml(label)}${required ? ' <span class="required">*</span>' : ''}</label>
            ${inputHtml}
            ${helpText ? `<div class="form-help">${this.escapeHtml(helpText)}</div>` : ''}
            ${error ? `<div class="form-error">${this.escapeHtml(error)}</div>` : ''}
        </div>`;
    },

    textInput(id, value, opts = {}) {
        const { placeholder = '', type = 'text', disabled = false } = opts;
        return `<input type="${type}" class="form-input" id="${id}" name="${id}" value="${this.escapeAttr(value || '')}" placeholder="${this.escapeAttr(placeholder)}" ${disabled ? 'disabled' : ''}>`;
    },

    textarea(id, value, opts = {}) {
        const { placeholder = '', rows = 6 } = opts;
        return `<textarea class="form-textarea" id="${id}" name="${id}" rows="${rows}" placeholder="${this.escapeAttr(placeholder)}">${this.escapeHtml(value || '')}</textarea>`;
    },

    numberInput(id, value, opts = {}) {
        const { min, max, placeholder = '' } = opts;
        return `<input type="number" class="form-input form-input-sm" id="${id}" name="${id}" value="${value != null ? value : ''}" ${min != null ? `min="${min}"` : ''} ${max != null ? `max="${max}"` : ''} placeholder="${this.escapeAttr(placeholder)}">`;
    },

    checkbox(id, label, checked, opts = {}) {
        return `<label class="custom-checkbox" for="${id}">
            <input type="checkbox" id="${id}" ${checked ? 'checked' : ''}>
            <span class="checkbox-mark"></span>
            <span class="checkbox-label">${this.escapeHtml(label)}</span>
        </label>`;
    },

    toggle(id, checked) {
        return `<label class="toggle-switch" for="${id}">
            <input type="checkbox" id="${id}" ${checked ? 'checked' : ''}>
            <span class="toggle-slider"></span>
        </label>`;
    },

    // ── Color Picker (custom) ──────────────────────────────
    colorPicker(id, selectedColor) {
        const colors = [
            '#d9534f', '#e74c3c', '#c0392b', '#b71c1c',
            '#e91e63', '#9b59b6', '#8e44ad', '#673ab7',
            '#3f51b5', '#428bca', '#2980b9', '#3498db',
            '#00bcd4', '#1abc9c', '#009688', '#27ae60',
            '#2ecc71', '#5cb85c', '#8bc34a', '#cddc39',
            '#f0ad4e', '#f39c12', '#e67e22', '#ff9800',
            '#ff5722', '#795548', '#95a5a6', '#607d8b',
            '#2c3e50', '#34495e', '#333333', '#000000'
        ];
        return `<div class="color-picker" id="${id}">
            <div class="color-grid">
                ${colors.map(c => `<div class="color-swatch${c === selectedColor ? ' selected' : ''}" data-color="${c}" style="background:${c}" title="${c}"></div>`).join('')}
            </div>
            <div class="color-input-wrap">
                <input type="text" class="form-input form-input-sm color-hex-input" id="${id}-hex" value="${selectedColor || '#428bca'}" placeholder="#hex" maxlength="7">
                <div class="color-preview" style="background:${selectedColor || '#428bca'}"></div>
            </div>
        </div>`;
    },

    // ── Date Input (custom text) ───────────────────────────
    dateInput(id, value, opts = {}) {
        const { placeholder = 'YYYY-MM-DD' } = opts;
        return `<input type="text" class="form-input form-input-sm date-input" id="${id}" name="${id}" value="${this.escapeAttr(value || '')}" placeholder="${placeholder}" pattern="\\d{4}-\\d{2}-\\d{2}">`;
    },

    // ── Empty State ────────────────────────────────────────
    emptyState(title, description, actionHtml) {
        return `<div class="empty-state">
            <div class="empty-state-icon">&#128196;</div>
            <h3>${this.escapeHtml(title)}</h3>
            <p>${this.escapeHtml(description)}</p>
            ${actionHtml || ''}
        </div>`;
    },

    // ── Breadcrumb ─────────────────────────────────────────
    breadcrumb(items) {
        return `<nav class="breadcrumb" id="breadcrumb">
            ${items.map((item, i) => {
                if (i === items.length - 1) return `<span class="breadcrumb-current">${this.escapeHtml(item.label)}</span>`;
                return `<a class="breadcrumb-link" data-action="navigate" data-section="${item.section}" ${item.params ? `data-params='${JSON.stringify(item.params)}'` : ''}>${this.escapeHtml(item.label)}</a><span class="breadcrumb-sep">/</span>`;
            }).join('')}
        </nav>`;
    },

    // ── Info/Warning/Error Boxes ───────────────────────────
    infoBox(msg) { return `<div class="alert alert-info">${msg}</div>`; },
    warningBox(msg) { return `<div class="alert alert-warning">${msg}</div>`; },
    errorBox(msg) { return `<div class="alert alert-danger">${msg}</div>`; },
    successBox(msg) { return `<div class="alert alert-success">${msg}</div>`; },

    // ── Date/Time Formatting ───────────────────────────────
    formatDate(isoStr) {
        if (!isoStr) return '';
        const d = new Date(isoStr);
        return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    },

    formatDateTime(isoStr) {
        if (!isoStr) return '';
        const d = new Date(isoStr);
        return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    },

    timeAgo(isoStr) {
        if (!isoStr) return '';
        const now = new Date();
        const d = new Date(isoStr);
        const diffMs = now - d;
        const diffMins = Math.floor(diffMs / 60000);
        if (diffMins < 1) return 'just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        const diffHrs = Math.floor(diffMins / 60);
        if (diffHrs < 24) return `${diffHrs}h ago`;
        const diffDays = Math.floor(diffHrs / 24);
        if (diffDays < 30) return `${diffDays}d ago`;
        const diffMonths = Math.floor(diffDays / 30);
        if (diffMonths < 12) return `${diffMonths}mo ago`;
        return `${Math.floor(diffMonths / 12)}y ago`;
    },

    formatDuration(seconds) {
        if (!seconds || seconds <= 0) return '0h';
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        if (h > 0 && m > 0) return `${h}h ${m}m`;
        if (h > 0) return `${h}h`;
        return `${m}m`;
    },

    // ── Markdown-lite renderer ─────────────────────────────
    renderMarkdown(text) {
        if (!text) return '';
        let html = this.escapeHtml(text);
        // Code blocks
        html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        // Inline code
        html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
        // Bold
        html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        // Italic
        html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
        // Headers
        html = html.replace(/^## (.+)$/gm, '<h4>$1</h4>');
        html = html.replace(/^# (.+)$/gm, '<h3>$1</h3>');
        // Checklists
        html = html.replace(/^- \[x\] (.+)$/gm, '<div class="checklist-item checked"><span class="checklist-box">&#10003;</span> $1</div>');
        html = html.replace(/^- \[ \] (.+)$/gm, '<div class="checklist-item"><span class="checklist-box"></span> $1</div>');
        // Lists
        html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
        html = html.replace(/^(\d+)\. (.+)$/gm, '<li>$2</li>');
        // Mentions
        html = html.replace(/@(\w+)/g, '<span class="mention">@$1</span>');
        // Labels
        html = html.replace(/~"([^"]+)"/g, '<span class="mention-label">~$1</span>');
        // Line breaks
        html = html.replace(/\n/g, '<br>');
        return html;
    }
};

// ── Global dropdown behavior ───────────────────────────────
document.addEventListener('click', function(e) {
    // Toggle dropdown
    const trigger = e.target.closest('.dropdown-trigger');
    if (trigger) {
        const dd = trigger.closest('.custom-dropdown');
        const menu = dd.querySelector('.dropdown-menu');
        // Close others
        document.querySelectorAll('.dropdown-menu').forEach(m => {
            if (m !== menu) m.style.display = 'none';
        });
        menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
        const searchInput = menu.querySelector('.dropdown-search');
        if (searchInput) setTimeout(() => searchInput.focus(), 10);
        e.stopPropagation();
        return;
    }

    // Select dropdown item
    const item = e.target.closest('.dropdown-item');
    if (item) {
        const dd = item.closest('.custom-dropdown');
        const isMulti = dd.dataset.multi === 'true';

        if (isMulti) {
            item.classList.toggle('selected');
            const check = item.querySelector('.dropdown-check');
            check.innerHTML = item.classList.contains('selected') ? '&#10003;' : '';
            // Collect selected values
            const selectedValues = Array.from(dd.querySelectorAll('.dropdown-item.selected')).map(i => i.dataset.value);
            dd.dispatchEvent(new CustomEvent('dropdown-change', { detail: { values: selectedValues, id: dd.dataset.dropdownId }, bubbles: true }));
            // Update display
            const labels = Array.from(dd.querySelectorAll('.dropdown-item.selected .dropdown-item-label')).map(l => l.textContent);
            dd.querySelector('.dropdown-display').textContent = labels.length > 0 ? labels.join(', ') : 'Select...';
            e.stopPropagation();
            return;
        }

        // Single select
        dd.querySelectorAll('.dropdown-item').forEach(i => i.classList.remove('selected'));
        item.classList.add('selected');
        dd.dataset.value = item.dataset.value;
        dd.querySelector('.dropdown-display').textContent = item.querySelector('.dropdown-item-label').textContent;
        dd.querySelector('.dropdown-menu').style.display = 'none';
        dd.dispatchEvent(new CustomEvent('dropdown-change', { detail: { value: item.dataset.value, id: dd.dataset.dropdownId }, bubbles: true }));
        e.stopPropagation();
        return;
    }

    // Close all dropdowns when clicking elsewhere
    document.querySelectorAll('.dropdown-menu').forEach(m => m.style.display = 'none');
});

// Dropdown search filtering
document.addEventListener('input', function(e) {
    if (e.target.classList.contains('dropdown-search')) {
        const query = e.target.value.toLowerCase();
        const dd = e.target.closest('.custom-dropdown');
        dd.querySelectorAll('.dropdown-item').forEach(item => {
            const label = item.querySelector('.dropdown-item-label').textContent.toLowerCase();
            item.style.display = label.includes(query) ? '' : 'none';
        });
    }
});

// Color picker behavior
document.addEventListener('click', function(e) {
    const swatch = e.target.closest('.color-swatch');
    if (swatch) {
        const picker = swatch.closest('.color-picker');
        picker.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('selected'));
        swatch.classList.add('selected');
        const hexInput = picker.querySelector('.color-hex-input');
        const preview = picker.querySelector('.color-preview');
        if (hexInput) hexInput.value = swatch.dataset.color;
        if (preview) preview.style.background = swatch.dataset.color;
    }
});

document.addEventListener('input', function(e) {
    if (e.target.classList.contains('color-hex-input')) {
        const picker = e.target.closest('.color-picker');
        const preview = picker.querySelector('.color-preview');
        if (preview && /^#[0-9a-fA-F]{6}$/.test(e.target.value)) {
            preview.style.background = e.target.value;
        }
    }
});

// Modal close on overlay click and Escape
document.addEventListener('click', function(e) {
    if (e.target.id === 'modalOverlay') {
        Components.closeModal();
    }
});

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        const modal = document.getElementById('modalOverlay');
        if (modal && modal.classList.contains('active')) {
            Components.closeModal();
        }
        document.querySelectorAll('.dropdown-menu').forEach(m => m.style.display = 'none');
    }
});
