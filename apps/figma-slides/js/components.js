const Components = (function() {
    let _confirmCallback = null;

    function escapeHtml(str) {
        if (!str) return '';
        return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
    }

    function escapeAttr(str) {
        return escapeHtml(str);
    }

    function timeAgo(dateStr) {
        if (!dateStr) return '';
        const now = new Date();
        const date = new Date(dateStr);
        const seconds = Math.floor((now - date) / 1000);
        if (seconds < 60) return 'just now';
        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) return minutes + 'm ago';
        const hours = Math.floor(minutes / 60);
        if (hours < 24) return hours + 'h ago';
        const days = Math.floor(hours / 24);
        if (days < 30) return days + 'd ago';
        const months = Math.floor(days / 30);
        if (months < 12) return months + 'mo ago';
        return Math.floor(months / 12) + 'y ago';
    }

    function formatDate(dateStr) {
        if (!dateStr) return '';
        const d = new Date(dateStr);
        return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    }

    function avatar(user, size) {
        size = size || 28;
        if (!user) return '';
        const initials = user.name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
        return '<span class="avatar" style="width:' + size + 'px;height:' + size + 'px;background:' + escapeAttr(user.avatarColor) + ';font-size:' + Math.floor(size * 0.4) + 'px" title="' + escapeAttr(user.name) + '">' + escapeHtml(initials) + '</span>';
    }

    function dropdown(id, options, selectedValue, placeholder, extraClass) {
        const selected = options.find(o => o.value === selectedValue);
        const label = selected ? selected.label : (placeholder || 'Select...');
        let html = '<div class="custom-dropdown ' + (extraClass || '') + '" id="' + escapeAttr(id) + '">';
        html += '<div class="dropdown-trigger" data-dropdown-trigger="' + escapeAttr(id) + '">';
        html += '<span class="dropdown-label">' + escapeHtml(label) + '</span>';
        html += '<span class="dropdown-arrow">&#9662;</span></div>';
        html += '<div class="dropdown-menu" id="' + escapeAttr(id) + '-menu">';
        options.forEach(function(opt) {
            const selectedClass = opt.value === selectedValue ? ' selected' : '';
            html += '<div class="dropdown-item' + selectedClass + '" data-dropdown-item="' + escapeAttr(id) + '" data-value="' + escapeAttr(opt.value) + '">' + escapeHtml(opt.label) + '</div>';
        });
        html += '</div></div>';
        return html;
    }

    function colorSwatch(color, selected, size) {
        size = size || 24;
        const cls = selected ? 'color-swatch selected' : 'color-swatch';
        return '<button class="' + cls + '" data-color="' + escapeAttr(color) + '" style="width:' + size + 'px;height:' + size + 'px;background:' + escapeAttr(color) + '" title="' + escapeAttr(color) + '"></button>';
    }

    function numberInput(id, value, label, min, max, step) {
        let html = '';
        if (label) html += '<label class="input-label" for="' + escapeAttr(id) + '">' + escapeHtml(label) + '</label>';
        html += '<input type="number" class="number-input" id="' + escapeAttr(id) + '" value="' + (value || 0) + '"';
        if (min !== undefined) html += ' min="' + min + '"';
        if (max !== undefined) html += ' max="' + max + '"';
        if (step !== undefined) html += ' step="' + step + '"';
        html += '>';
        return html;
    }

    function textInput(id, value, placeholder, label) {
        let html = '';
        if (label) html += '<label class="input-label" for="' + escapeAttr(id) + '">' + escapeHtml(label) + '</label>';
        html += '<input type="text" class="text-input" id="' + escapeAttr(id) + '" value="' + escapeAttr(value || '') + '" placeholder="' + escapeAttr(placeholder || '') + '">';
        return html;
    }

    function textarea(id, value, placeholder, label, rows) {
        let html = '';
        if (label) html += '<label class="input-label" for="' + escapeAttr(id) + '">' + escapeHtml(label) + '</label>';
        html += '<textarea class="textarea-input" id="' + escapeAttr(id) + '" rows="' + (rows || 3) + '" placeholder="' + escapeAttr(placeholder || '') + '">' + escapeHtml(value || '') + '</textarea>';
        return html;
    }

    function toggle(id, checked, label) {
        let html = '<label class="toggle-container">';
        html += '<span class="toggle-switch">';
        html += '<input type="checkbox" id="' + escapeAttr(id) + '" ' + (checked ? 'checked' : '') + '>';
        html += '<span class="toggle-slider"></span></span>';
        if (label) html += '<span class="toggle-label">' + escapeHtml(label) + '</span>';
        html += '</label>';
        return html;
    }

    function showModal(title, bodyHtml, footerHtml) {
        const overlay = document.getElementById('modalOverlay');
        if (!overlay) return;
        document.getElementById('modalTitle').textContent = title;
        document.getElementById('modalBody').innerHTML = bodyHtml;
        document.getElementById('modalFooter').innerHTML = footerHtml || '';
        overlay.classList.add('active');
    }

    function closeModal() {
        const overlay = document.getElementById('modalOverlay');
        if (overlay) overlay.classList.remove('active');
        _confirmCallback = null;
    }

    function confirm(message, onConfirm) {
        _confirmCallback = onConfirm;
        showModal('Confirm', '<p>' + escapeHtml(message) + '</p>',
            '<button class="btn btn-secondary" data-action="close-modal">Cancel</button> ' +
            '<button class="btn btn-primary" data-action="confirm-modal">Confirm</button>');
    }

    function confirmDanger(message, onConfirm) {
        _confirmCallback = onConfirm;
        showModal('Confirm', '<p>' + escapeHtml(message) + '</p>',
            '<button class="btn btn-secondary" data-action="close-modal">Cancel</button> ' +
            '<button class="btn btn-danger" data-action="confirm-modal">Delete</button>');
    }

    function executeConfirm() {
        if (_confirmCallback) {
            _confirmCallback();
            _confirmCallback = null;
        }
        closeModal();
    }

    function showToast(message, duration) {
        duration = duration || 3000;
        const container = document.getElementById('toastContainer');
        if (!container) return;
        const toast = document.createElement('div');
        toast.className = 'toast toast-enter';
        toast.innerHTML = '<span>' + escapeHtml(message) + '</span><button class="toast-close" onclick="this.parentElement.remove()">&times;</button>';
        container.appendChild(toast);
        setTimeout(function() { toast.classList.remove('toast-enter'); }, 50);
        setTimeout(function() {
            toast.classList.add('toast-exit');
            setTimeout(function() { toast.remove(); }, 300);
        }, duration);
    }

    function slideThumbnail(slide, isActive, index) {
        const theme = AppState.getCurrentTheme() || { bgColor: '#1a1a2e' };
        const bg = slide.backgroundColor || theme.bgColor;
        let html = '<div class="slide-thumbnail' + (isActive ? ' active' : '') + '" data-slide-id="' + escapeAttr(slide.id) + '" draggable="true">';
        html += '<div class="slide-thumb-number">' + (index + 1) + '</div>';
        html += '<div class="slide-thumb-preview" style="background:' + escapeAttr(bg) + '">';
        // Mini preview of elements
        (slide.elements || []).forEach(function(el) {
            if (!el.visible) return;
            const scale = 0.1;
            const sx = el.x * scale;
            const sy = el.y * scale;
            const sw = el.width * scale;
            const sh = el.height * scale;
            if (el.type === 'text') {
                const fontSize = Math.max(3, (el.style.fontSize || 16) * scale);
                html += '<div class="thumb-element thumb-text" style="left:' + sx + 'px;top:' + sy + 'px;width:' + sw + 'px;height:' + sh + 'px;font-size:' + fontSize + 'px;color:' + escapeAttr(el.style.color || '#fff') + ';font-weight:' + (el.style.fontWeight || 'normal') + ';text-align:' + (el.style.textAlign || 'left') + '">' + escapeHtml((el.content || '').substring(0, 30)) + '</div>';
            } else if (el.type === 'shape') {
                const fill = el.style.fill || '#6366f1';
                const radius = (el.shapeType === 'circle') ? '50%' : ((el.style.cornerRadius || 0) * scale) + 'px';
                html += '<div class="thumb-element thumb-shape" style="left:' + sx + 'px;top:' + sy + 'px;width:' + sw + 'px;height:' + sh + 'px;background:' + escapeAttr(fill) + ';border-radius:' + radius + '"></div>';
            }
        });
        html += '</div>';
        // Comment indicator
        const comments = AppState.getCommentsForSlide(slide.id);
        const unresolvedCount = comments.filter(c => !c.resolved).length;
        if (unresolvedCount > 0) {
            html += '<span class="slide-thumb-badge" title="' + unresolvedCount + ' comment(s)">' + unresolvedCount + '</span>';
        }
        html += '</div>';
        return html;
    }

    return {
        escapeHtml, escapeAttr, timeAgo, formatDate, avatar,
        dropdown, colorSwatch, numberInput, textInput, textarea, toggle,
        showModal, closeModal, confirm, confirmDanger, executeConfirm,
        showToast, slideThumbnail
    };
})();
