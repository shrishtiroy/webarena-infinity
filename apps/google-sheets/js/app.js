const App = (function() {
    let openMenu = null;
    let contextMenuEl = null;
    let formulaViewMode = false;
    let showGridlines = true;

    function init() {
        AppState.init();
        renderLayout();
        Grid.init();
        Charts.initChartDrag();
        attachGlobalEvents();
        AppState.setupSSE();
        AppState.onChange(() => {
            renderSheetTabs();
            renderChartsOverlay();
        });
        renderChartsOverlay();
    }

    function renderLayout() {
        const app = document.getElementById('app');
        app.innerHTML = '';
        app.innerHTML += Components.renderMenuBar();
        app.innerHTML += Components.renderToolbar();
        app.innerHTML += Components.renderFormulaBar();
        app.innerHTML += '<div class="grid-wrapper"><div class="grid-container" id="grid-container"></div><div class="charts-overlay" id="charts-overlay"></div></div>';
        app.innerHTML += Components.renderSheetTabs();
        app.innerHTML += renderModals();
    }

    function renderSheetTabs() {
        const tabsEl = document.getElementById('sheet-tabs');
        if (tabsEl) {
            const state = AppState.getState();
            let html = '';
            state.sheets.forEach((sheet, i) => {
                const active = i === state.activeSheet ? ' active' : '';
                html += `<div class="sheet-tab${active}" data-sheet-index="${i}" data-testid="sheet-tab-${i}">`;
                html += `<span class="sheet-tab-name">${Components.escapeHtml(sheet.name)}</span>`;
                html += `</div>`;
            });
            html += '<div class="sheet-tab add-sheet" data-action="add-sheet" data-testid="add-sheet-btn">+</div>';
            tabsEl.innerHTML = html;
        }
    }

    function renderChartsOverlay() {
        const overlay = document.getElementById('charts-overlay');
        if (!overlay) return;
        const si = AppState.getState().activeSheet;
        overlay.innerHTML = Charts.renderCharts(si);
        setTimeout(() => Charts.drawAllCharts(si), 10);
    }

    function render() {
        Grid.render();
        renderSheetTabs();
        renderChartsOverlay();
    }

    function renderModals() {
        let html = '';

        // Find and Replace
        html += Components.renderModal('find-replace-modal', 'Find and Replace',
            `<div class="form-group">
                <label>Find:</label>
                <input type="text" id="find-input" class="modal-input" />
            </div>
            <div class="form-group">
                <label>Replace:</label>
                <input type="text" id="replace-input" class="modal-input" />
            </div>
            <div class="form-group">
                <label><input type="checkbox" id="find-match-case" /> Match case</label>
                <label><input type="checkbox" id="find-match-entire" /> Match entire cell</label>
                <label><input type="checkbox" id="find-all-sheets" /> Search all sheets</label>
            </div>`,
            `<button class="modal-btn" id="find-next-btn">Find Next</button>
            <button class="modal-btn" id="replace-one-btn">Replace</button>
            <button class="modal-btn primary" id="replace-all-btn">Replace All</button>`
        );

        // Paste Special
        html += Components.renderModal('paste-special-modal', 'Paste Special',
            `<div class="form-group">
                <label><input type="radio" name="paste-type" value="values" checked /> Paste values only</label>
                <label><input type="radio" name="paste-type" value="formulas" /> Paste formulas only</label>
                <label><input type="radio" name="paste-type" value="formatting" /> Paste formatting only</label>
            </div>`,
            `<button class="modal-btn" data-close-modal="paste-special-modal">Cancel</button>
            <button class="modal-btn primary" id="paste-special-ok">OK</button>`
        );

        // Conditional Formatting
        html += Components.renderModal('conditional-format-modal', 'Conditional Formatting',
            `<div class="form-group">
                <label>Range:</label>
                <input type="text" id="cf-range" class="modal-input" />
            </div>
            <div class="form-group">
                <label>Rule type:</label>
                <div class="custom-dropdown" id="cf-rule-type-dropdown">
                    <div class="dropdown-trigger" data-value="greater_than">Greater than</div>
                    <div class="dropdown-menu">
                        <div class="dropdown-item" data-value="greater_than">Greater than</div>
                        <div class="dropdown-item" data-value="less_than">Less than</div>
                        <div class="dropdown-item" data-value="equal_to">Equal to</div>
                        <div class="dropdown-item" data-value="between">Between</div>
                        <div class="dropdown-item" data-value="text_contains">Text contains</div>
                        <div class="dropdown-item" data-value="is_empty">Is empty</div>
                        <div class="dropdown-item" data-value="is_not_empty">Is not empty</div>
                    </div>
                </div>
            </div>
            <div class="form-group">
                <label>Value:</label>
                <input type="text" id="cf-value" class="modal-input" />
                <input type="text" id="cf-value2" class="modal-input" placeholder="Value 2 (for between)" style="display:none;" />
            </div>
            <div class="form-group">
                <label>Background color:</label>
                <input type="text" id="cf-bg-color" class="modal-input" value="#ffcccc" />
            </div>
            <div class="form-group">
                <label>Text color:</label>
                <input type="text" id="cf-text-color" class="modal-input" value="" placeholder="Optional" />
            </div>
            <div id="cf-existing-rules"></div>`,
            `<button class="modal-btn" data-close-modal="conditional-format-modal">Cancel</button>
            <button class="modal-btn primary" id="cf-add-btn">Add Rule</button>`
        );

        // Named Range
        html += Components.renderModal('named-range-modal', 'Named Ranges',
            `<div class="form-group">
                <label>Name:</label>
                <input type="text" id="nr-name" class="modal-input" />
            </div>
            <div class="form-group">
                <label>Reference:</label>
                <input type="text" id="nr-reference" class="modal-input" />
            </div>
            <div id="nr-existing-list"></div>`,
            `<button class="modal-btn" data-close-modal="named-range-modal">Cancel</button>
            <button class="modal-btn primary" id="nr-add-btn">Add</button>`
        );

        // Chart Editor
        html += Components.renderModal('chart-editor-modal', 'Chart Editor',
            `<div class="form-group">
                <label>Chart type:</label>
                <div class="chart-type-selector" id="chart-type-selector">
                    <div class="chart-type-option selected" data-chart-type="bar" title="Bar chart">&#9638; Bar</div>
                    <div class="chart-type-option" data-chart-type="horizontal_bar" title="Horizontal bar">&#9644; H-Bar</div>
                    <div class="chart-type-option" data-chart-type="line" title="Line chart">&#10138; Line</div>
                    <div class="chart-type-option" data-chart-type="pie" title="Pie chart">&#9673; Pie</div>
                    <div class="chart-type-option" data-chart-type="scatter" title="Scatter">&#8226; Scatter</div>
                </div>
            </div>
            <div class="form-group">
                <label>Data range:</label>
                <input type="text" id="chart-data-range" class="modal-input" />
            </div>
            <div class="form-group">
                <label>Chart title:</label>
                <input type="text" id="chart-title-input" class="modal-input" />
            </div>
            <div class="form-group">
                <label>X-axis label:</label>
                <input type="text" id="chart-x-label" class="modal-input" />
            </div>
            <div class="form-group">
                <label>Y-axis label:</label>
                <input type="text" id="chart-y-label" class="modal-input" />
            </div>
            <div class="form-group">
                <label><input type="checkbox" id="chart-show-legend" checked /> Show legend</label>
                <div class="custom-dropdown" id="chart-legend-pos-dropdown">
                    <div class="dropdown-trigger" data-value="top">Top</div>
                    <div class="dropdown-menu">
                        <div class="dropdown-item" data-value="top">Top</div>
                        <div class="dropdown-item" data-value="bottom">Bottom</div>
                        <div class="dropdown-item" data-value="left">Left</div>
                        <div class="dropdown-item" data-value="right">Right</div>
                    </div>
                </div>
            </div>`,
            `<button class="modal-btn" data-close-modal="chart-editor-modal">Cancel</button>
            <button class="modal-btn primary" id="chart-save-btn">Save</button>`
        );

        // Sort dialog
        html += Components.renderModal('sort-modal', 'Multi-column Sort',
            `<div id="sort-keys">
                <div class="sort-key-row">
                    <label>Sort by:</label>
                    <input type="text" class="modal-input sort-col" placeholder="Column (e.g. A)" />
                    <div class="custom-dropdown sort-order-dropdown">
                        <div class="dropdown-trigger" data-value="asc">A to Z</div>
                        <div class="dropdown-menu">
                            <div class="dropdown-item" data-value="asc">A to Z</div>
                            <div class="dropdown-item" data-value="desc">Z to A</div>
                        </div>
                    </div>
                </div>
            </div>
            <button class="modal-btn" id="sort-add-key">+ Add sort key</button>`,
            `<button class="modal-btn" data-close-modal="sort-modal">Cancel</button>
            <button class="modal-btn primary" id="sort-apply-btn">Sort</button>`
        );

        // Data Validation
        html += Components.renderModal('data-validation-modal', 'Data Validation',
            `<div class="form-group">
                <label>Validation type:</label>
                <div class="custom-dropdown" id="dv-type-dropdown">
                    <div class="dropdown-trigger" data-value="list">Dropdown list</div>
                    <div class="dropdown-menu">
                        <div class="dropdown-item" data-value="list">Dropdown list</div>
                        <div class="dropdown-item" data-value="number">Number range</div>
                        <div class="dropdown-item" data-value="text_length">Text length</div>
                    </div>
                </div>
            </div>
            <div class="form-group">
                <label>Values (comma-separated or range):</label>
                <input type="text" id="dv-values" class="modal-input" />
            </div>`,
            `<button class="modal-btn" data-close-modal="data-validation-modal">Cancel</button>
            <button class="modal-btn primary" id="dv-apply-btn">Apply</button>`
        );

        // Number Format
        html += Components.renderModal('number-format-modal', 'Number Format',
            `<div class="form-group">
                <label><input type="radio" name="nf-type" value="general" checked /> General</label>
                <label><input type="radio" name="nf-type" value="number" /> Number</label>
                <label><input type="radio" name="nf-type" value="currency" /> Currency ($)</label>
                <label><input type="radio" name="nf-type" value="percentage" /> Percentage (%)</label>
                <label><input type="radio" name="nf-type" value="date" /> Date (MM/DD/YYYY)</label>
                <label><input type="radio" name="nf-type" value="text" /> Plain text</label>
            </div>
            <div class="form-group">
                <label>Decimal places:</label>
                <input type="number" id="nf-decimals" class="modal-input" value="2" min="0" max="10" />
            </div>`,
            `<button class="modal-btn" data-close-modal="number-format-modal">Cancel</button>
            <button class="modal-btn primary" id="nf-apply-btn">Apply</button>`
        );

        // Filter dialog
        html += Components.renderModal('filter-modal', 'Filter',
            `<div id="filter-content"></div>`,
            `<button class="modal-btn" id="filter-clear-btn">Clear Filter</button>
            <button class="modal-btn" data-close-modal="filter-modal">Cancel</button>
            <button class="modal-btn primary" id="filter-apply-btn">Apply</button>`
        );

        // Borders
        html += Components.renderModal('borders-modal', 'Cell Borders',
            `<div class="form-group">
                <label>Border type:</label>
                <div class="border-options">
                    <button class="border-opt" data-border="top">Top</button>
                    <button class="border-opt" data-border="bottom">Bottom</button>
                    <button class="border-opt" data-border="left">Left</button>
                    <button class="border-opt" data-border="right">Right</button>
                    <button class="border-opt" data-border="all">All Borders</button>
                    <button class="border-opt" data-border="outer">Outer Borders</button>
                    <button class="border-opt" data-border="none">No Borders</button>
                </div>
            </div>
            <div class="form-group">
                <label>Style:</label>
                <div class="custom-dropdown" id="border-style-dropdown">
                    <div class="dropdown-trigger" data-value="solid">Solid</div>
                    <div class="dropdown-menu">
                        <div class="dropdown-item" data-value="solid">Solid</div>
                        <div class="dropdown-item" data-value="dashed">Dashed</div>
                        <div class="dropdown-item" data-value="dotted">Dotted</div>
                    </div>
                </div>
            </div>
            <div class="form-group">
                <label>Color:</label>
                <input type="text" id="border-color-input" class="modal-input" value="#000000" />
            </div>`,
            `<button class="modal-btn" data-close-modal="borders-modal">Cancel</button>
            <button class="modal-btn primary" id="borders-apply-btn">Apply</button>`
        );

        // Merge cells
        html += Components.renderModal('merge-modal', 'Merge Cells',
            `<div class="form-group">
                <button class="modal-btn" id="merge-center-btn">Merge & Center</button>
                <button class="modal-btn" id="merge-across-btn">Merge Across</button>
                <button class="modal-btn" id="unmerge-btn">Unmerge</button>
            </div>`,
            `<button class="modal-btn" data-close-modal="merge-modal">Close</button>`
        );

        // Delete confirm
        html += Components.renderModal('delete-sheet-modal', 'Delete Sheet',
            `<p>Are you sure you want to delete this sheet? This action cannot be undone.</p>`,
            `<button class="modal-btn" data-close-modal="delete-sheet-modal">Cancel</button>
            <button class="modal-btn danger" id="delete-sheet-confirm-btn">Delete</button>`
        );

        // Context menu placeholder
        html += '<div class="context-menu" id="context-menu"></div>';

        // Color palette overlays
        html += '<div class="color-palette-overlay" id="font-color-palette-overlay"></div>';
        html += '<div class="color-palette-overlay" id="fill-color-palette-overlay"></div>';

        return html;
    }

    function attachGlobalEvents() {
        // Menu bar
        document.getElementById('menu-bar').addEventListener('click', (e) => {
            const menuItem = e.target.closest('.menu-item');
            if (!menuItem) return;
            const menuName = menuItem.dataset.menu;
            if (openMenu === menuName) {
                closeMenu();
                return;
            }
            openMenu = menuName;
            const items = Components.getMenuItems(menuName);
            const rect = menuItem.getBoundingClientRect();
            showDropdownMenu(items, rect.left, rect.bottom);
        });

        // Toolbar
        document.getElementById('toolbar').addEventListener('click', (e) => {
            const btn = e.target.closest('.toolbar-btn');
            if (!btn) return;
            const action = btn.dataset.action;
            handleAction(action);
        });

        // Sheet tabs
        document.getElementById('sheet-tabs').addEventListener('click', (e) => {
            const tab = e.target.closest('.sheet-tab');
            if (!tab) return;
            if (tab.dataset.action === 'add-sheet') {
                AppState.addSheet();
                render();
                return;
            }
            const index = parseInt(tab.dataset.sheetIndex);
            if (!isNaN(index)) {
                AppState.setActiveSheet(index);
                render();
            }
        });

        // Sheet tab context menu
        document.getElementById('sheet-tabs').addEventListener('contextmenu', (e) => {
            e.preventDefault();
            const tab = e.target.closest('.sheet-tab');
            if (!tab || tab.dataset.action === 'add-sheet') return;
            const index = parseInt(tab.dataset.sheetIndex);
            showContextMenu(e.clientX, e.clientY, [
                { label: 'Rename', action: () => renameSheetPrompt(index) },
                { label: 'Duplicate', action: () => { AppState.duplicateSheet(index); render(); } },
                { label: 'Delete', action: () => deleteSheetPrompt(index) },
                { label: 'Move left', action: () => { if (index > 0) { AppState.moveSheet(index, index - 1); render(); } } },
                { label: 'Move right', action: () => { const s = AppState.getState(); if (index < s.sheets.length - 1) { AppState.moveSheet(index, index + 1); render(); } } }
            ]);
        });

        // Chart actions
        document.addEventListener('click', (e) => {
            const btn = e.target.closest('.chart-action-btn');
            if (!btn) return;
            const action = btn.dataset.chartAction;
            const chartId = btn.dataset.chartId;
            const si = AppState.getState().activeSheet;

            if (action === 'delete') {
                AppState.deleteChart(si, chartId);
                renderChartsOverlay();
            } else if (action === 'edit') {
                openChartEditor(chartId);
            } else if (action === 'duplicate') {
                const chart = AppState.getActiveSheet().charts.find(c => c.id === chartId);
                if (chart) {
                    const copy = JSON.parse(JSON.stringify(chart));
                    copy.position = { x: (copy.position?.x || 200) + 30, y: (copy.position?.y || 100) + 30 };
                    delete copy.id;
                    AppState.addChart(si, copy);
                    renderChartsOverlay();
                }
            }
        });

        // Custom dropdowns
        document.addEventListener('click', (e) => {
            const trigger = e.target.closest('.dropdown-trigger');
            if (trigger) {
                const dropdown = trigger.closest('.custom-dropdown');
                if (dropdown) {
                    const menu = dropdown.querySelector('.dropdown-menu');
                    if (menu) menu.classList.toggle('visible');
                    e.stopPropagation();
                    return;
                }
            }
            const item = e.target.closest('.custom-dropdown .dropdown-item');
            if (item) {
                const dropdown = item.closest('.custom-dropdown');
                const trigger = dropdown.querySelector('.dropdown-trigger');
                trigger.textContent = item.textContent;
                trigger.dataset.value = item.dataset.value;
                dropdown.querySelector('.dropdown-menu').classList.remove('visible');

                // Special handlers
                if (dropdown.id === 'cf-rule-type-dropdown') {
                    const v2 = document.getElementById('cf-value2');
                    if (v2) v2.style.display = item.dataset.value === 'between' ? '' : 'none';
                }
                return;
            }
        });

        // Modal close buttons
        document.addEventListener('click', (e) => {
            if (e.target.dataset.closeModal) {
                Components.hideModal(e.target.dataset.closeModal);
            }
        });

        // Close menu/context on outside click
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.menu-item') && !e.target.closest('.dropdown-menu')) {
                closeMenu();
            }
            if (!e.target.closest('.context-menu')) {
                hideContextMenu();
            }
            // Close color palettes
            if (!e.target.closest('.toolbar-color-group')) {
                document.getElementById('font-color-palette-overlay').innerHTML = '';
                document.getElementById('fill-color-palette-overlay').innerHTML = '';
            }
        });

        // Modal button handlers
        attachModalHandlers();
    }

    function attachModalHandlers() {
        // Find and Replace
        document.getElementById('find-next-btn')?.addEventListener('click', findNext);
        document.getElementById('replace-one-btn')?.addEventListener('click', replaceOne);
        document.getElementById('replace-all-btn')?.addEventListener('click', replaceAll);

        // Paste Special
        document.getElementById('paste-special-ok')?.addEventListener('click', () => {
            const type = document.querySelector('input[name="paste-type"]:checked')?.value;
            if (type === 'values') Grid.pasteValuesOnly();
            else if (type === 'formulas') Grid.pasteFormulasOnly();
            else if (type === 'formatting') Grid.pasteFormattingOnly();
            Components.hideModal('paste-special-modal');
        });

        // Conditional Formatting
        document.getElementById('cf-add-btn')?.addEventListener('click', () => {
            const si = AppState.getState().activeSheet;
            const range = document.getElementById('cf-range').value;
            const ruleType = document.querySelector('#cf-rule-type-dropdown .dropdown-trigger').dataset.value;
            const value = document.getElementById('cf-value').value;
            const value2 = document.getElementById('cf-value2').value;
            const bgColor = document.getElementById('cf-bg-color').value;
            const textColor = document.getElementById('cf-text-color').value;

            const rule = { range, type: ruleType, value, value2, backgroundColor: bgColor };
            if (textColor) rule.fontColor = textColor;
            AppState.addConditionalFormat(si, rule);
            Components.hideModal('conditional-format-modal');
            render();
        });

        // Named Range
        document.getElementById('nr-add-btn')?.addEventListener('click', () => {
            const name = document.getElementById('nr-name').value.trim();
            const ref = document.getElementById('nr-reference').value.trim();
            if (name && ref) {
                AppState.setNamedRange(name, ref);
                Components.hideModal('named-range-modal');
            }
        });

        // Chart Editor
        document.getElementById('chart-save-btn')?.addEventListener('click', saveChart);

        // Chart type selector
        document.getElementById('chart-type-selector')?.addEventListener('click', (e) => {
            const opt = e.target.closest('.chart-type-option');
            if (!opt) return;
            document.querySelectorAll('.chart-type-option').forEach(o => o.classList.remove('selected'));
            opt.classList.add('selected');
        });

        // Sort
        document.getElementById('sort-add-key')?.addEventListener('click', () => {
            const container = document.getElementById('sort-keys');
            const div = document.createElement('div');
            div.className = 'sort-key-row';
            div.innerHTML = `
                <label>Then by:</label>
                <input type="text" class="modal-input sort-col" placeholder="Column (e.g. B)" />
                <div class="custom-dropdown sort-order-dropdown">
                    <div class="dropdown-trigger" data-value="asc">A to Z</div>
                    <div class="dropdown-menu">
                        <div class="dropdown-item" data-value="asc">A to Z</div>
                        <div class="dropdown-item" data-value="desc">Z to A</div>
                    </div>
                </div>`;
            container.appendChild(div);
        });

        document.getElementById('sort-apply-btn')?.addEventListener('click', () => {
            const rows = document.querySelectorAll('.sort-key-row');
            const keys = [];
            rows.forEach(row => {
                const col = row.querySelector('.sort-col').value.toUpperCase().trim();
                const order = row.querySelector('.dropdown-trigger').dataset.value;
                if (col) keys.push({ col, order });
            });
            if (keys.length > 0) multiColumnSort(keys);
            Components.hideModal('sort-modal');
        });

        // Number Format
        document.getElementById('nf-apply-btn')?.addEventListener('click', () => {
            const type = document.querySelector('input[name="nf-type"]:checked')?.value;
            const decimals = parseInt(document.getElementById('nf-decimals').value) || 2;
            const addrs = Grid.getSelectedAddresses();
            const si = AppState.getState().activeSheet;
            AppState.applyFormatToRange(si, addrs, 'numberFormat', type);
            if (type === 'number' || type === 'percentage') {
                AppState.applyFormatToRange(si, addrs, 'decimalPlaces', decimals);
            }
            Components.hideModal('number-format-modal');
            render();
        });

        // Filter
        document.getElementById('filter-apply-btn')?.addEventListener('click', applyFilter);
        document.getElementById('filter-clear-btn')?.addEventListener('click', () => {
            const col = document.getElementById('filter-modal').dataset.filterCol;
            if (col) {
                AppState.setFilter(AppState.getState().activeSheet, col, null);
                Components.hideModal('filter-modal');
                render();
            }
        });

        // Borders
        document.getElementById('borders-apply-btn')?.addEventListener('click', () => {
            const selected = document.querySelector('.border-opt.selected');
            const borderType = selected ? selected.dataset.border : 'all';
            const style = document.querySelector('#border-style-dropdown .dropdown-trigger').dataset.value || 'solid';
            const color = document.getElementById('border-color-input').value || '#000000';
            applyBorders(borderType, style, color);
            Components.hideModal('borders-modal');
        });

        document.querySelectorAll('.border-opt').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.border-opt').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
            });
        });

        // Merge
        document.getElementById('merge-center-btn')?.addEventListener('click', () => {
            const bounds = Grid.getSelectionBounds();
            if (bounds) {
                const range = bounds.startCol + bounds.startRow + ':' + bounds.endCol + bounds.endRow;
                const si = AppState.getState().activeSheet;
                AppState.mergeCells(si, range);
                // Center content
                AppState.setCellFormat(si, bounds.startCol + bounds.startRow, 'horizontalAlign', 'center');
                AppState.notify();
                Components.hideModal('merge-modal');
                render();
            }
        });

        document.getElementById('merge-across-btn')?.addEventListener('click', () => {
            const bounds = Grid.getSelectionBounds();
            if (bounds) {
                const si = AppState.getState().activeSheet;
                for (let r = bounds.startRow; r <= bounds.endRow; r++) {
                    const range = bounds.startCol + r + ':' + bounds.endCol + r;
                    AppState.mergeCells(si, range);
                }
                Components.hideModal('merge-modal');
                render();
            }
        });

        document.getElementById('unmerge-btn')?.addEventListener('click', () => {
            const si = AppState.getState().activeSheet;
            const sheet = AppState.getActiveSheet();
            const addr = Grid.getActiveCell().col + Grid.getActiveCell().row;
            const toRemove = sheet.mergedCells.filter(range => {
                const cells = expandRange(range, si);
                return cells.some(c => c.addr === addr);
            });
            toRemove.forEach(range => AppState.unmergeCells(si, range));
            Components.hideModal('merge-modal');
            render();
        });

        // Data Validation
        document.getElementById('dv-apply-btn')?.addEventListener('click', () => {
            const type = document.querySelector('#dv-type-dropdown .dropdown-trigger').dataset.value;
            const values = document.getElementById('dv-values').value;
            const si = AppState.getState().activeSheet;
            const addr = Grid.getActiveCell().col + Grid.getActiveCell().row;
            const validation = { type, values };
            AppState.setDataValidation(si, addr, validation);
            Components.hideModal('data-validation-modal');
            render();
        });

        // Delete sheet confirm
        document.getElementById('delete-sheet-confirm-btn')?.addEventListener('click', () => {
            const idx = parseInt(document.getElementById('delete-sheet-modal').dataset.sheetIndex);
            if (!isNaN(idx)) {
                AppState.deleteSheet(idx);
                Components.hideModal('delete-sheet-modal');
                render();
            }
        });
    }

    function showDropdownMenu(items, x, y) {
        // Remove existing
        const existing = document.querySelector('.dropdown-menu.floating');
        if (existing) existing.remove();

        let html = `<div class="dropdown-menu floating visible" style="left:${x}px;top:${y}px;">`;
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

        const div = document.createElement('div');
        div.innerHTML = html;
        const menu = div.firstElementChild;
        document.body.appendChild(menu);

        menu.addEventListener('click', (e) => {
            const item = e.target.closest('.dropdown-item');
            if (item && !item.classList.contains('disabled')) {
                handleAction(item.dataset.action);
                closeMenu();
            }
        });
    }

    function closeMenu() {
        openMenu = null;
        document.querySelectorAll('.dropdown-menu.floating').forEach(m => m.remove());
    }

    function showContextMenu(x, y, items) {
        const menu = document.getElementById('context-menu');
        let html = '';
        items.forEach(item => {
            html += `<div class="context-menu-item">${item.label}</div>`;
        });
        menu.innerHTML = html;
        menu.style.left = x + 'px';
        menu.style.top = y + 'px';
        menu.classList.add('visible');

        const menuItems = menu.querySelectorAll('.context-menu-item');
        menuItems.forEach((el, i) => {
            el.addEventListener('click', () => {
                items[i].action();
                hideContextMenu();
            });
        });
    }

    function hideContextMenu() {
        const menu = document.getElementById('context-menu');
        if (menu) menu.classList.remove('visible');
    }

    function handleAction(action) {
        const si = AppState.getState().activeSheet;
        const ac = Grid.getActiveCell();

        switch (action) {
            case 'edit-undo': AppState.undo(); render(); break;
            case 'edit-redo': AppState.redo(); render(); break;
            case 'edit-cut': Grid.doCut(); break;
            case 'edit-copy': Grid.doCopy(); break;
            case 'edit-paste': Grid.doPaste(); break;
            case 'edit-paste-special': Components.showModal('paste-special-modal'); break;
            case 'edit-find-replace': showFindReplace(); break;
            case 'edit-delete-row': AppState.deleteRow(si, ac.row); render(); break;
            case 'edit-delete-col': AppState.deleteColumn(si, ac.col); render(); break;
            case 'edit-insert-row': AppState.insertRow(si, ac.row - 1); render(); break;
            case 'edit-insert-col': AppState.insertColumn(si, indexToColLetter(colLetterToIndex(ac.col) - 1)); render(); break;

            case 'view-freeze-rows': AppState.setFrozenRows(si, ac.row); render(); break;
            case 'view-freeze-cols': AppState.setFrozenCols(si, colLetterToIndex(ac.col)); render(); break;
            case 'view-unfreeze': AppState.setFrozenRows(si, 0); AppState.setFrozenCols(si, 0); render(); break;
            case 'view-gridlines': showGridlines = !showGridlines; document.getElementById('grid-container')?.classList.toggle('no-gridlines'); break;
            case 'view-formula-view': formulaViewMode = !formulaViewMode; render(); break;

            case 'insert-row-above': AppState.insertRow(si, ac.row - 1); render(); break;
            case 'insert-row-below': AppState.insertRow(si, ac.row); render(); break;
            case 'insert-col-left': AppState.insertColumn(si, indexToColLetter(colLetterToIndex(ac.col) - 1)); render(); break;
            case 'insert-col-right': AppState.insertColumn(si, ac.col); render(); break;
            case 'insert-chart': showChartEditor(); break;
            case 'insert-named-range': showNamedRangeDialog(); break;

            case 'format-bold': toggleBold(); break;
            case 'format-italic': toggleItalic(); break;
            case 'format-underline': toggleUnderline(); break;
            case 'format-strikethrough': toggleStrikethrough(); break;
            case 'format-font-color': showFontColorPalette(); break;
            case 'format-fill-color': showFillColorPalette(); break;
            case 'format-align-left': applyAlignment('left'); break;
            case 'format-align-center': applyAlignment('center'); break;
            case 'format-align-right': applyAlignment('right'); break;
            case 'format-number': Components.showModal('number-format-modal'); break;
            case 'format-number-quick': Components.showModal('number-format-modal'); break;
            case 'format-currency': applyQuickFormat('currency'); break;
            case 'format-percent': applyQuickFormat('percentage'); break;
            case 'format-decimal-inc': changeDecimalPlaces(1); break;
            case 'format-decimal-dec': changeDecimalPlaces(-1); break;
            case 'format-borders-dropdown': Components.showModal('borders-modal'); break;
            case 'format-merge-dropdown': Components.showModal('merge-modal'); break;
            case 'format-alignment': applyAlignment('center'); break;
            case 'format-borders': Components.showModal('borders-modal'); break;
            case 'format-merge': Components.showModal('merge-modal'); break;
            case 'format-conditional': showConditionalFormatDialog(); break;

            case 'data-sort-asc': sortColumn(ac.col, 'asc'); break;
            case 'data-sort-desc': sortColumn(ac.col, 'desc'); break;
            case 'data-sort-multi': Components.showModal('sort-modal'); break;
            case 'data-filter-toggle': AppState.toggleFilterMode(si); render(); break;
            case 'data-validation': Components.showModal('data-validation-modal'); break;
            case 'data-named-ranges': showNamedRangeDialog(); break;

            case 'file-download-csv': downloadCSV(); break;
        }
    }

    // Formatting helpers
    function toggleBold() {
        const addrs = Grid.getSelectedAddresses();
        const si = AppState.getState().activeSheet;
        const sheet = AppState.getActiveSheet();
        const first = sheet.cells[addrs[0]];
        const isBold = first && first.format && first.format.bold;
        AppState.applyFormatToRange(si, addrs, 'bold', !isBold);
        render();
    }

    function toggleItalic() {
        const addrs = Grid.getSelectedAddresses();
        const si = AppState.getState().activeSheet;
        const sheet = AppState.getActiveSheet();
        const first = sheet.cells[addrs[0]];
        const isItalic = first && first.format && first.format.italic;
        AppState.applyFormatToRange(si, addrs, 'italic', !isItalic);
        render();
    }

    function toggleUnderline() {
        const addrs = Grid.getSelectedAddresses();
        const si = AppState.getState().activeSheet;
        const sheet = AppState.getActiveSheet();
        const first = sheet.cells[addrs[0]];
        const isUnderline = first && first.format && first.format.underline;
        AppState.applyFormatToRange(si, addrs, 'underline', !isUnderline);
        render();
    }

    function toggleStrikethrough() {
        const addrs = Grid.getSelectedAddresses();
        const si = AppState.getState().activeSheet;
        const sheet = AppState.getActiveSheet();
        const first = sheet.cells[addrs[0]];
        const isStrike = first && first.format && first.format.strikethrough;
        AppState.applyFormatToRange(si, addrs, 'strikethrough', !isStrike);
        render();
    }

    function applyAlignment(align) {
        const addrs = Grid.getSelectedAddresses();
        const si = AppState.getState().activeSheet;
        AppState.applyFormatToRange(si, addrs, 'horizontalAlign', align);
        render();
    }

    function applyQuickFormat(format) {
        const addrs = Grid.getSelectedAddresses();
        const si = AppState.getState().activeSheet;
        AppState.applyFormatToRange(si, addrs, 'numberFormat', format);
        render();
    }

    function changeDecimalPlaces(delta) {
        const addrs = Grid.getSelectedAddresses();
        const si = AppState.getState().activeSheet;
        const sheet = AppState.getActiveSheet();
        addrs.forEach(addr => {
            const c = sheet.cells[addr];
            const current = (c && c.format && c.format.decimalPlaces) || 2;
            const newVal = Math.max(0, Math.min(10, current + delta));
            AppState.setCellFormat(si, addr, 'decimalPlaces', newVal);
            if (!c?.format?.numberFormat) AppState.setCellFormat(si, addr, 'numberFormat', 'number');
        });
        AppState.notify();
        render();
    }

    function showFontColorPalette() {
        const overlay = document.getElementById('font-color-palette-overlay');
        overlay.innerHTML = Components.renderColorPalette('font-color-palette-popup', '#000000');
        overlay.style.display = 'block';
        const toolbar = document.getElementById('toolbar');
        overlay.style.top = toolbar.getBoundingClientRect().bottom + 'px';
        overlay.style.left = '200px';

        overlay.addEventListener('click', (e) => {
            const swatch = e.target.closest('.color-swatch');
            if (swatch) {
                const color = swatch.dataset.color;
                const addrs = Grid.getSelectedAddresses();
                const si = AppState.getState().activeSheet;
                AppState.applyFormatToRange(si, addrs, 'fontColor', color);
                overlay.innerHTML = '';
                overlay.style.display = 'none';
                const indicator = document.getElementById('font-color-indicator');
                if (indicator) indicator.style.background = color;
                render();
            }
        }, { once: true });
    }

    function showFillColorPalette() {
        const overlay = document.getElementById('fill-color-palette-overlay');
        overlay.innerHTML = Components.renderColorPalette('fill-color-palette-popup', '#ffffff');
        overlay.style.display = 'block';
        const toolbar = document.getElementById('toolbar');
        overlay.style.top = toolbar.getBoundingClientRect().bottom + 'px';
        overlay.style.left = '240px';

        overlay.addEventListener('click', (e) => {
            const swatch = e.target.closest('.color-swatch');
            if (swatch) {
                const color = swatch.dataset.color;
                const addrs = Grid.getSelectedAddresses();
                const si = AppState.getState().activeSheet;
                AppState.applyFormatToRange(si, addrs, 'backgroundColor', color);
                overlay.innerHTML = '';
                overlay.style.display = 'none';
                const indicator = document.getElementById('fill-color-indicator');
                if (indicator) indicator.style.background = color;
                render();
            }
        }, { once: true });
    }

    // Sort
    function sortColumn(col, order) {
        const si = AppState.getState().activeSheet;
        const sheet = AppState.getActiveSheet();
        AppState.saveUndoSnapshot();

        // Find data range (skip header row 1)
        let maxRow = 1;
        for (const addr in sheet.cells) {
            const p = parseAddress(addr);
            if (p && p.row > maxRow) maxRow = p.row;
        }
        let maxCol = 1;
        for (const addr in sheet.cells) {
            const p = parseAddress(addr);
            if (p) {
                const ci = colLetterToIndex(p.col);
                if (ci > maxCol) maxCol = ci;
            }
        }

        // Collect rows 2..maxRow
        const rows = [];
        for (let r = 2; r <= maxRow; r++) {
            const rowData = {};
            for (let c = 1; c <= maxCol; c++) {
                const addr = indexToColLetter(c) + r;
                if (sheet.cells[addr]) {
                    rowData[indexToColLetter(c)] = JSON.parse(JSON.stringify(sheet.cells[addr]));
                }
            }
            const sortVal = sheet.cells[col + r] ? sheet.cells[col + r].value : null;
            rows.push({ data: rowData, sortVal });
        }

        rows.sort((a, b) => {
            let av = a.sortVal, bv = b.sortVal;
            if (av == null) return 1;
            if (bv == null) return -1;
            if (typeof av === 'number' && typeof bv === 'number') {
                return order === 'asc' ? av - bv : bv - av;
            }
            av = String(av).toLowerCase();
            bv = String(bv).toLowerCase();
            return order === 'asc' ? av.localeCompare(bv) : bv.localeCompare(av);
        });

        // Clear old data rows
        for (let r = 2; r <= maxRow; r++) {
            for (let c = 1; c <= maxCol; c++) {
                delete sheet.cells[indexToColLetter(c) + r];
            }
        }

        // Write sorted rows
        rows.forEach((row, i) => {
            const r = i + 2;
            for (const col in row.data) {
                sheet.cells[col + r] = row.data[col];
            }
        });

        AppState.recalcAllFormulas();
        AppState.notify();
        render();
    }

    function multiColumnSort(keys) {
        const si = AppState.getState().activeSheet;
        const sheet = AppState.getActiveSheet();
        AppState.saveUndoSnapshot();

        let maxRow = 1, maxCol = 1;
        for (const addr in sheet.cells) {
            const p = parseAddress(addr);
            if (p) {
                if (p.row > maxRow) maxRow = p.row;
                const ci = colLetterToIndex(p.col);
                if (ci > maxCol) maxCol = ci;
            }
        }

        const rows = [];
        for (let r = 2; r <= maxRow; r++) {
            const rowData = {};
            const sortVals = {};
            for (let c = 1; c <= maxCol; c++) {
                const cl = indexToColLetter(c);
                const addr = cl + r;
                if (sheet.cells[addr]) {
                    rowData[cl] = JSON.parse(JSON.stringify(sheet.cells[addr]));
                    sortVals[cl] = sheet.cells[addr].value;
                }
            }
            rows.push({ data: rowData, sortVals });
        }

        rows.sort((a, b) => {
            for (const key of keys) {
                let av = a.sortVals[key.col], bv = b.sortVals[key.col];
                if (av == null && bv == null) continue;
                if (av == null) return 1;
                if (bv == null) return -1;
                let cmp;
                if (typeof av === 'number' && typeof bv === 'number') {
                    cmp = av - bv;
                } else {
                    cmp = String(av).toLowerCase().localeCompare(String(bv).toLowerCase());
                }
                if (cmp !== 0) return key.order === 'asc' ? cmp : -cmp;
            }
            return 0;
        });

        for (let r = 2; r <= maxRow; r++) {
            for (let c = 1; c <= maxCol; c++) {
                delete sheet.cells[indexToColLetter(c) + r];
            }
        }

        rows.forEach((row, i) => {
            const r = i + 2;
            for (const col in row.data) {
                sheet.cells[col + r] = row.data[col];
            }
        });

        AppState.recalcAllFormulas();
        AppState.notify();
        render();
    }

    // Find and Replace
    let findState = { lastAddr: null };

    function showFindReplace() {
        Components.showModal('find-replace-modal');
        setTimeout(() => document.getElementById('find-input')?.focus(), 100);
    }

    function findNext() {
        const searchText = document.getElementById('find-input').value;
        const matchCase = document.getElementById('find-match-case').checked;
        const matchEntire = document.getElementById('find-match-entire').checked;
        const allSheets = document.getElementById('find-all-sheets').checked;

        if (!searchText) return;
        const state = AppState.getState();
        const sheetsToSearch = allSheets ? state.sheets.map((_, i) => i) : [state.activeSheet];

        for (const si of sheetsToSearch) {
            const sheet = state.sheets[si];
            for (const addr in sheet.cells) {
                const c = sheet.cells[addr];
                if (!c || c.value == null) continue;
                const val = String(c.value);
                const search = matchCase ? searchText : searchText.toLowerCase();
                const target = matchCase ? val : val.toLowerCase();

                const matches = matchEntire ? (target === search) : target.includes(search);
                if (matches) {
                    if (findState.lastAddr && addr <= findState.lastAddr && si === state.activeSheet) continue;
                    findState.lastAddr = addr;
                    if (si !== state.activeSheet) AppState.setActiveSheet(si);
                    const p = parseAddress(addr);
                    if (p) {
                        Grid.setActiveCell(p.col, p.row);
                        Grid.scrollToCell(p.col, p.row);
                    }
                    return;
                }
            }
        }
        findState.lastAddr = null;
    }

    function replaceOne() {
        const ac = Grid.getActiveCell();
        const addr = ac.col + ac.row;
        const si = AppState.getState().activeSheet;
        const sheet = AppState.getActiveSheet();
        const c = sheet.cells[addr];
        if (!c) return;

        const searchText = document.getElementById('find-input').value;
        const replaceText = document.getElementById('replace-input').value;
        const matchCase = document.getElementById('find-match-case').checked;

        const val = String(c.value);
        if (matchCase) {
            AppState.setCellValue(si, addr, val.replace(searchText, replaceText));
        } else {
            AppState.setCellValue(si, addr, val.replace(new RegExp(searchText.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i'), replaceText));
        }
        render();
        findNext();
    }

    function replaceAll() {
        const searchText = document.getElementById('find-input').value;
        const replaceText = document.getElementById('replace-input').value;
        const matchCase = document.getElementById('find-match-case').checked;
        const allSheets = document.getElementById('find-all-sheets').checked;

        if (!searchText) return;
        AppState.saveUndoSnapshot();
        const state = AppState.getState();
        const sheetsToSearch = allSheets ? state.sheets : [state.sheets[state.activeSheet]];
        let count = 0;

        sheetsToSearch.forEach(sheet => {
            for (const addr in sheet.cells) {
                const c = sheet.cells[addr];
                if (!c || c.value == null || c.formula) continue;
                const val = String(c.value);
                const regex = new RegExp(searchText.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), matchCase ? 'g' : 'gi');
                if (regex.test(val)) {
                    c.value = val.replace(regex, replaceText);
                    count++;
                }
            }
        });

        AppState.notify();
        render();
    }

    // Filter
    function showFilterDialog(col) {
        const si = AppState.getState().activeSheet;
        const sheet = AppState.getActiveSheet();
        document.getElementById('filter-modal').dataset.filterCol = col;

        // Collect unique values
        const values = new Set();
        for (let r = 2; r <= Grid.TOTAL_ROWS; r++) {
            const addr = col + r;
            const c = sheet.cells[addr];
            if (c && c.value != null) values.add(String(c.value));
        }

        const currentFilter = sheet.filters && sheet.filters[col];
        const hiddenValues = currentFilter && currentFilter.hiddenValues ? currentFilter.hiddenValues : [];

        let html = '<div class="filter-values">';
        html += `<label class="filter-select-all"><input type="checkbox" id="filter-select-all" ${hiddenValues.length === 0 ? 'checked' : ''} /> (Select All)</label>`;
        Array.from(values).sort().forEach(v => {
            const checked = !hiddenValues.includes(v) ? 'checked' : '';
            html += `<label><input type="checkbox" class="filter-value-cb" value="${Components.escapeHtml(v)}" ${checked} /> ${Components.escapeHtml(v)}</label>`;
        });
        html += '</div>';

        document.getElementById('filter-content').innerHTML = html;

        // Select All toggle
        document.getElementById('filter-select-all')?.addEventListener('change', (e) => {
            document.querySelectorAll('.filter-value-cb').forEach(cb => cb.checked = e.target.checked);
        });

        Components.showModal('filter-modal');
    }

    function applyFilter() {
        const col = document.getElementById('filter-modal').dataset.filterCol;
        const checkboxes = document.querySelectorAll('.filter-value-cb');
        const hiddenValues = [];
        checkboxes.forEach(cb => {
            if (!cb.checked) hiddenValues.push(cb.value);
        });

        if (hiddenValues.length === 0) {
            AppState.setFilter(AppState.getState().activeSheet, col, null);
        } else {
            AppState.setFilter(AppState.getState().activeSheet, col, { type: 'values', hiddenValues });
        }
        Components.hideModal('filter-modal');
        render();
    }

    // Borders
    function applyBorders(type, style, color) {
        const addrs = Grid.getSelectedAddresses();
        const si = AppState.getState().activeSheet;
        const border = `1px ${style} ${color}`;
        AppState.saveUndoSnapshot();

        addrs.forEach(addr => {
            switch (type) {
                case 'all':
                    AppState.setCellFormat(si, addr, 'borderTop', border);
                    AppState.setCellFormat(si, addr, 'borderBottom', border);
                    AppState.setCellFormat(si, addr, 'borderLeft', border);
                    AppState.setCellFormat(si, addr, 'borderRight', border);
                    break;
                case 'top': AppState.setCellFormat(si, addr, 'borderTop', border); break;
                case 'bottom': AppState.setCellFormat(si, addr, 'borderBottom', border); break;
                case 'left': AppState.setCellFormat(si, addr, 'borderLeft', border); break;
                case 'right': AppState.setCellFormat(si, addr, 'borderRight', border); break;
                case 'outer':
                    // Apply outer borders only
                    AppState.setCellFormat(si, addr, 'borderTop', border);
                    AppState.setCellFormat(si, addr, 'borderBottom', border);
                    AppState.setCellFormat(si, addr, 'borderLeft', border);
                    AppState.setCellFormat(si, addr, 'borderRight', border);
                    break;
                case 'none':
                    AppState.setCellFormat(si, addr, 'borderTop', '');
                    AppState.setCellFormat(si, addr, 'borderBottom', '');
                    AppState.setCellFormat(si, addr, 'borderLeft', '');
                    AppState.setCellFormat(si, addr, 'borderRight', '');
                    break;
            }
        });
        AppState.notify();
        render();
    }

    // Conditional Formatting
    function showConditionalFormatDialog() {
        const ac = Grid.getActiveCell();
        const bounds = Grid.getSelectionBounds();
        let rangeStr = ac.col + ac.row;
        if (bounds) {
            rangeStr = bounds.startCol + bounds.startRow + ':' + bounds.endCol + bounds.endRow;
        }
        document.getElementById('cf-range').value = rangeStr;

        // Show existing rules
        const si = AppState.getState().activeSheet;
        const sheet = AppState.getActiveSheet();
        let rulesHtml = '<h4>Existing Rules</h4>';
        if (sheet.conditionalFormats && sheet.conditionalFormats.length > 0) {
            sheet.conditionalFormats.forEach((rule, i) => {
                rulesHtml += `<div class="cf-rule-item">
                    <span>${rule.range}: ${rule.type} ${rule.value || ''}</span>
                    <button class="modal-btn small" data-cf-delete="${i}">Delete</button>
                </div>`;
            });
        } else {
            rulesHtml += '<p>No rules defined.</p>';
        }
        document.getElementById('cf-existing-rules').innerHTML = rulesHtml;

        // Attach delete handlers
        document.querySelectorAll('[data-cf-delete]').forEach(btn => {
            btn.addEventListener('click', () => {
                AppState.removeConditionalFormat(si, parseInt(btn.dataset.cfDelete));
                showConditionalFormatDialog(); // Refresh
            });
        });

        Components.showModal('conditional-format-modal');
    }

    // Named Ranges
    function showNamedRangeDialog() {
        const state = AppState.getState();
        const ac = Grid.getActiveCell();
        document.getElementById('nr-reference').value = state.sheets[state.activeSheet].name + '!' + ac.col + ac.row;

        let html = '<h4>Existing Named Ranges</h4>';
        const nr = state.namedRanges;
        const names = Object.keys(nr);
        if (names.length > 0) {
            names.forEach(name => {
                html += `<div class="nr-item">
                    <span><b>${Components.escapeHtml(name)}</b>: ${Components.escapeHtml(nr[name])}</span>
                    <button class="modal-btn small" data-nr-delete="${name}">Delete</button>
                </div>`;
            });
        } else {
            html += '<p>No named ranges defined.</p>';
        }
        document.getElementById('nr-existing-list').innerHTML = html;

        document.querySelectorAll('[data-nr-delete]').forEach(btn => {
            btn.addEventListener('click', () => {
                AppState.deleteNamedRange(btn.dataset.nrDelete);
                showNamedRangeDialog();
            });
        });

        Components.showModal('named-range-modal');
    }

    // Chart Editor
    let editingChartId = null;

    function showChartEditor() {
        editingChartId = null;
        const bounds = Grid.getSelectionBounds();
        let rangeStr = '';
        if (bounds) {
            rangeStr = bounds.startCol + bounds.startRow + ':' + bounds.endCol + bounds.endRow;
        }
        document.getElementById('chart-data-range').value = rangeStr;
        document.getElementById('chart-title-input').value = '';
        document.getElementById('chart-x-label').value = '';
        document.getElementById('chart-y-label').value = '';
        document.getElementById('chart-show-legend').checked = true;

        document.querySelectorAll('.chart-type-option').forEach(o => o.classList.remove('selected'));
        document.querySelector('.chart-type-option[data-chart-type="bar"]')?.classList.add('selected');

        Components.showModal('chart-editor-modal');
    }

    function openChartEditor(chartId) {
        editingChartId = chartId;
        const si = AppState.getState().activeSheet;
        const chart = AppState.getActiveSheet().charts.find(c => c.id === chartId);
        if (!chart) return;

        document.getElementById('chart-data-range').value = chart.dataRange || '';
        document.getElementById('chart-title-input').value = chart.title || '';
        document.getElementById('chart-x-label').value = chart.xAxisLabel || '';
        document.getElementById('chart-y-label').value = chart.yAxisLabel || '';
        document.getElementById('chart-show-legend').checked = chart.showLegend !== false;

        document.querySelectorAll('.chart-type-option').forEach(o => {
            o.classList.toggle('selected', o.dataset.chartType === chart.type);
        });

        Components.showModal('chart-editor-modal');
    }

    function saveChart() {
        const type = document.querySelector('.chart-type-option.selected')?.dataset.chartType || 'bar';
        const dataRange = document.getElementById('chart-data-range').value;
        const title = document.getElementById('chart-title-input').value;
        const xAxisLabel = document.getElementById('chart-x-label').value;
        const yAxisLabel = document.getElementById('chart-y-label').value;
        const showLegend = document.getElementById('chart-show-legend').checked;
        const legendPosition = document.querySelector('#chart-legend-pos-dropdown .dropdown-trigger')?.dataset.value || 'top';

        const si = AppState.getState().activeSheet;

        if (editingChartId) {
            AppState.updateChart(si, editingChartId, {
                type, dataRange, title, xAxisLabel, yAxisLabel, showLegend, legendPosition
            });
        } else {
            AppState.addChart(si, {
                type, dataRange, title, xAxisLabel, yAxisLabel, showLegend, legendPosition,
                position: { x: 250, y: 50 },
                size: { width: 450, height: 300 }
            });
        }

        Components.hideModal('chart-editor-modal');
        renderChartsOverlay();
    }

    function renameSheetPrompt(index) {
        const sheet = AppState.getState().sheets[index];
        const tab = document.querySelector(`[data-sheet-index="${index}"] .sheet-tab-name`);
        if (!tab) return;
        const input = document.createElement('input');
        input.type = 'text';
        input.value = sheet.name;
        input.className = 'sheet-rename-input';
        tab.replaceWith(input);
        input.focus();
        input.select();

        const finish = () => {
            AppState.renameSheet(index, input.value);
            renderSheetTabs();
        };
        input.addEventListener('blur', finish);
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') { e.preventDefault(); finish(); }
            if (e.key === 'Escape') { renderSheetTabs(); }
        });
    }

    function deleteSheetPrompt(index) {
        const sheet = AppState.getState().sheets[index];
        const hasCells = Object.keys(sheet.cells).length > 0;
        if (hasCells) {
            document.getElementById('delete-sheet-modal').dataset.sheetIndex = index;
            Components.showModal('delete-sheet-modal');
        } else {
            AppState.deleteSheet(index);
            render();
        }
    }

    function downloadCSV() {
        const sheet = AppState.getActiveSheet();
        let maxRow = 0, maxCol = 0;
        for (const addr in sheet.cells) {
            const p = parseAddress(addr);
            if (p) {
                if (p.row > maxRow) maxRow = p.row;
                const ci = colLetterToIndex(p.col);
                if (ci > maxCol) maxCol = ci;
            }
        }

        let csv = '';
        for (let r = 1; r <= maxRow; r++) {
            const row = [];
            for (let c = 1; c <= maxCol; c++) {
                const addr = indexToColLetter(c) + r;
                const cell = sheet.cells[addr];
                const val = cell ? String(cell.value ?? '') : '';
                row.push('"' + val.replace(/"/g, '""') + '"');
            }
            csv += row.join(',') + '\n';
        }

        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = sheet.name + '.csv';
        a.click();
        URL.revokeObjectURL(url);
    }

    return {
        init, render, showContextMenu, showFilterDialog,
        sortColumn, toggleBold, toggleItalic, toggleUnderline,
        showFindReplace
    };
})();

document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
