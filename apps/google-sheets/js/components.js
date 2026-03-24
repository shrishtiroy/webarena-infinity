const Components = (function() {

    function renderMenuBar() {
        return `
        <div class="menu-bar" id="menu-bar">
            <div class="menu-item" data-menu="file">File</div>
            <div class="menu-item" data-menu="edit">Edit</div>
            <div class="menu-item" data-menu="view">View</div>
            <div class="menu-item" data-menu="insert">Insert</div>
            <div class="menu-item" data-menu="format">Format</div>
            <div class="menu-item" data-menu="data">Data</div>
            <div class="menu-item" data-menu="tools">Tools</div>
        </div>`;
    }

    function getMenuItems(menuName) {
        switch (menuName) {
            case 'file': return [
                { label: 'New', action: 'file-new', disabled: true },
                { label: 'Open', action: 'file-open', disabled: true },
                { type: 'separator' },
                { label: 'Download as CSV', action: 'file-download-csv' }
            ];
            case 'edit': return [
                { label: 'Undo', action: 'edit-undo', shortcut: 'Ctrl+Z' },
                { label: 'Redo', action: 'edit-redo', shortcut: 'Ctrl+Y' },
                { type: 'separator' },
                { label: 'Cut', action: 'edit-cut', shortcut: 'Ctrl+X' },
                { label: 'Copy', action: 'edit-copy', shortcut: 'Ctrl+C' },
                { label: 'Paste', action: 'edit-paste', shortcut: 'Ctrl+V' },
                { label: 'Paste Special...', action: 'edit-paste-special' },
                { type: 'separator' },
                { label: 'Find and Replace...', action: 'edit-find-replace', shortcut: 'Ctrl+H' },
                { type: 'separator' },
                { label: 'Delete row', action: 'edit-delete-row' },
                { label: 'Delete column', action: 'edit-delete-col' },
                { label: 'Insert row above', action: 'edit-insert-row' },
                { label: 'Insert column left', action: 'edit-insert-col' }
            ];
            case 'view': return [
                { label: 'Freeze up to current row', action: 'view-freeze-rows' },
                { label: 'Freeze up to current column', action: 'view-freeze-cols' },
                { label: 'Unfreeze', action: 'view-unfreeze' },
                { type: 'separator' },
                { label: 'Gridlines', action: 'view-gridlines', toggle: true },
                { label: 'Formula view', action: 'view-formula-view', toggle: true }
            ];
            case 'insert': return [
                { label: 'Row above', action: 'insert-row-above' },
                { label: 'Row below', action: 'insert-row-below' },
                { label: 'Column left', action: 'insert-col-left' },
                { label: 'Column right', action: 'insert-col-right' },
                { type: 'separator' },
                { label: 'Chart', action: 'insert-chart' },
                { label: 'Named range', action: 'insert-named-range' }
            ];
            case 'format': return [
                { label: 'Number format...', action: 'format-number' },
                { type: 'separator' },
                { label: 'Bold', action: 'format-bold', shortcut: 'Ctrl+B' },
                { label: 'Italic', action: 'format-italic', shortcut: 'Ctrl+I' },
                { label: 'Underline', action: 'format-underline', shortcut: 'Ctrl+U' },
                { type: 'separator' },
                { label: 'Text alignment...', action: 'format-alignment' },
                { label: 'Cell borders...', action: 'format-borders' },
                { label: 'Merge cells...', action: 'format-merge' },
                { type: 'separator' },
                { label: 'Conditional formatting...', action: 'format-conditional' }
            ];
            case 'data': return [
                { label: 'Sort ascending', action: 'data-sort-asc' },
                { label: 'Sort descending', action: 'data-sort-desc' },
                { label: 'Multi-column sort...', action: 'data-sort-multi' },
                { type: 'separator' },
                { label: 'Create filter', action: 'data-filter-toggle' },
                { label: 'Data validation...', action: 'data-validation' },
                { label: 'Named ranges...', action: 'data-named-ranges' }
            ];
            case 'tools': return [
                { label: 'Explore (no-op)', action: 'tools-explore', disabled: true }
            ];
            default: return [];
        }
    }

    function renderDropdownMenu(items, x, y) {
        let html = `<div class="dropdown-menu visible" style="left:${x}px;top:${y}px;">`;
        items.forEach(item => {
            if (item.type === 'separator') {
                html += '<div class="dropdown-separator"></div>';
            } else {
                const cls = item.disabled ? 'dropdown-item disabled' : 'dropdown-item';
                html += `<div class="${cls}" data-action="${item.action || ''}">`;
                html += `<span>${item.label}</span>`;
                if (item.shortcut) html += `<span class="shortcut">${item.shortcut}</span>`;
                html += `</div>`;
            }
        });
        html += '</div>';
        return html;
    }

    function renderToolbar() {
        return `
        <div class="toolbar" id="toolbar">
            <button class="toolbar-btn" data-action="edit-undo" title="Undo">&#8617;</button>
            <button class="toolbar-btn" data-action="edit-redo" title="Redo">&#8618;</button>
            <div class="toolbar-separator"></div>
            <button class="toolbar-btn" data-action="format-bold" title="Bold (Ctrl+B)"><b>B</b></button>
            <button class="toolbar-btn" data-action="format-italic" title="Italic (Ctrl+I)"><i>I</i></button>
            <button class="toolbar-btn" data-action="format-underline" title="Underline (Ctrl+U)"><u>U</u></button>
            <button class="toolbar-btn" data-action="format-strikethrough" title="Strikethrough"><s>S</s></button>
            <div class="toolbar-separator"></div>
            <div class="toolbar-color-group">
                <button class="toolbar-btn color-btn" data-action="format-font-color" title="Font color">
                    <span>A</span><div class="color-indicator" id="font-color-indicator" style="background:#000000;"></div>
                </button>
                <div class="color-palette-anchor" id="font-color-palette"></div>
            </div>
            <div class="toolbar-color-group">
                <button class="toolbar-btn color-btn" data-action="format-fill-color" title="Fill color">
                    <span>&#9608;</span><div class="color-indicator" id="fill-color-indicator" style="background:#ffffff;"></div>
                </button>
                <div class="color-palette-anchor" id="fill-color-palette"></div>
            </div>
            <div class="toolbar-separator"></div>
            <button class="toolbar-btn" data-action="format-align-left" title="Align left">&#8676;</button>
            <button class="toolbar-btn" data-action="format-align-center" title="Align center">&#8596;</button>
            <button class="toolbar-btn" data-action="format-align-right" title="Align right">&#8677;</button>
            <div class="toolbar-separator"></div>
            <div class="toolbar-dropdown-group">
                <button class="toolbar-btn" data-action="format-number-quick" title="Number format">123</button>
                <div class="number-format-anchor" id="number-format-dropdown"></div>
            </div>
            <button class="toolbar-btn" data-action="format-currency" title="Currency">$</button>
            <button class="toolbar-btn" data-action="format-percent" title="Percent">%</button>
            <button class="toolbar-btn" data-action="format-decimal-inc" title="Increase decimal">.0</button>
            <button class="toolbar-btn" data-action="format-decimal-dec" title="Decrease decimal">.00</button>
            <div class="toolbar-separator"></div>
            <div class="toolbar-dropdown-group">
                <button class="toolbar-btn" data-action="format-borders-dropdown" title="Borders">&#9633;</button>
            </div>
            <div class="toolbar-dropdown-group">
                <button class="toolbar-btn" data-action="format-merge-dropdown" title="Merge cells">&#8862;</button>
            </div>
            <div class="toolbar-separator"></div>
            <button class="toolbar-btn" data-action="insert-chart" title="Insert chart">&#9783;</button>
            <button class="toolbar-btn" data-action="data-filter-toggle" title="Filter">&#9782;</button>
        </div>`;
    }

    function renderFormulaBar() {
        return `
        <div class="formula-bar" id="formula-bar">
            <div class="formula-addr" id="formula-addr">A1</div>
            <div class="formula-fx">fx</div>
            <input type="text" class="formula-input" id="formula-input" />
        </div>`;
    }

    function renderSheetTabs() {
        const state = AppState.getState();
        let html = '<div class="sheet-tabs" id="sheet-tabs">';
        state.sheets.forEach((sheet, i) => {
            const active = i === state.activeSheet ? ' active' : '';
            html += `<div class="sheet-tab${active}" data-sheet-index="${i}" data-testid="sheet-tab-${i}">`;
            html += `<span class="sheet-tab-name">${escapeHtml(sheet.name)}</span>`;
            html += `</div>`;
        });
        html += '<div class="sheet-tab add-sheet" data-action="add-sheet" data-testid="add-sheet-btn">+</div>';
        html += '</div>';
        return html;
    }

    function renderColorPalette(id, currentColor) {
        const colors = [
            '#000000', '#434343', '#666666', '#999999', '#b7b7b7', '#cccccc', '#d9d9d9', '#efefef', '#f3f3f3', '#ffffff',
            '#980000', '#ff0000', '#ff9900', '#ffff00', '#00ff00', '#00ffff', '#4a86e8', '#0000ff', '#9900ff', '#ff00ff',
            '#e6b8af', '#f4cccc', '#fce5cd', '#fff2cc', '#d9ead3', '#d0e0e3', '#c9daf8', '#cfe2f3', '#d9d2e9', '#ead1dc',
            '#dd7e6b', '#ea9999', '#f9cb9c', '#ffe599', '#b6d7a8', '#a2c4c9', '#a4c2f4', '#9fc5e8', '#b4a7d6', '#d5a6bd',
            '#cc4125', '#e06666', '#f6b26b', '#ffd966', '#93c47d', '#76a5af', '#6d9eeb', '#6fa8dc', '#8e7cc3', '#c27ba0',
            '#a61c00', '#cc0000', '#e69138', '#f1c232', '#6aa84f', '#45818e', '#3c78d8', '#3d85c6', '#674ea7', '#a64d79',
            '#85200c', '#990000', '#b45f06', '#bf9000', '#38761d', '#134f5c', '#1155cc', '#0b5394', '#351c75', '#741b47'
        ];
        let html = `<div class="color-palette" id="${id}">`;
        html += '<div class="color-palette-grid">';
        colors.forEach(color => {
            const selected = color === currentColor ? ' selected' : '';
            html += `<div class="color-swatch${selected}" data-color="${color}" style="background-color:${color};"></div>`;
        });
        html += '</div></div>';
        return html;
    }

    function renderModal(id, title, bodyHtml, footerHtml) {
        return `
        <div class="modal-overlay" id="${id}">
            <div class="modal">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button class="modal-close" data-close-modal="${id}">&times;</button>
                </div>
                <div class="modal-body">${bodyHtml}</div>
                <div class="modal-footer">${footerHtml || ''}</div>
            </div>
        </div>`;
    }

    function showModal(id) {
        const el = document.getElementById(id);
        if (el) el.classList.add('visible');
    }

    function hideModal(id) {
        const el = document.getElementById(id);
        if (el) el.classList.remove('visible');
    }

    function escapeHtml(str) {
        return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    return {
        renderMenuBar, getMenuItems, renderDropdownMenu,
        renderToolbar, renderFormulaBar, renderSheetTabs,
        renderColorPalette, renderModal, showModal, hideModal,
        escapeHtml
    };
})();
