const Grid = (function() {
    const TOTAL_ROWS = 100;
    const TOTAL_COLS = 26;
    const DEFAULT_COL_WIDTH = 100;
    const DEFAULT_ROW_HEIGHT = 25;
    const HEADER_HEIGHT = 25;
    const ROW_HEADER_WIDTH = 50;
    const BUFFER_ROWS = 5;

    let activeCell = { col: 'A', row: 1 };
    let selectionStart = null;
    let selectionEnd = null;
    let multiSelections = [];
    let editingCell = null;
    let editValue = '';
    let scrollTop = 0;
    let scrollLeft = 0;
    let gridContainer = null;
    let resizingCol = null;
    let resizingRow = null;
    let resizeStartX = 0;
    let resizeStartY = 0;
    let resizeStartSize = 0;
    let clipboard = null;
    let clipboardMode = null; // 'copy' or 'cut'
    let autofillStart = null;
    let formulaViewMode = false;

    function init() {
        gridContainer = document.getElementById('grid-container');
        if (!gridContainer) return;
        render();
        attachEvents();
    }

    function getColWidth(col) {
        const sheet = AppState.getActiveSheet();
        return (sheet.columnWidths && sheet.columnWidths[col]) || DEFAULT_COL_WIDTH;
    }

    function getRowHeight(row) {
        const sheet = AppState.getActiveSheet();
        return (sheet.rowHeights && sheet.rowHeights[row]) || DEFAULT_ROW_HEIGHT;
    }

    function getTotalWidth() {
        let w = ROW_HEADER_WIDTH;
        for (let c = 1; c <= TOTAL_COLS; c++) {
            w += getColWidth(indexToColLetter(c));
        }
        return w;
    }

    function getColX(colIndex) {
        let x = ROW_HEADER_WIDTH;
        for (let c = 1; c < colIndex; c++) {
            x += getColWidth(indexToColLetter(c));
        }
        return x;
    }

    function getRowY(row) {
        let y = HEADER_HEIGHT;
        for (let r = 1; r < row; r++) {
            y += getRowHeight(r);
        }
        return y;
    }

    function render() {
        if (!gridContainer) return;
        const sheet = AppState.getActiveSheet();
        const scrollEl = gridContainer;
        scrollTop = scrollEl.scrollTop;
        scrollLeft = scrollEl.scrollLeft;

        const viewWidth = scrollEl.clientWidth;
        const viewHeight = scrollEl.clientHeight;

        // Find visible rows
        let firstVisibleRow = 1;
        let y = HEADER_HEIGHT;
        for (let r = 1; r <= TOTAL_ROWS; r++) {
            const rh = getRowHeight(r);
            if (y + rh > scrollTop) { firstVisibleRow = r; break; }
            y += rh;
        }
        firstVisibleRow = Math.max(1, firstVisibleRow - BUFFER_ROWS);

        let lastVisibleRow = firstVisibleRow;
        y = getRowY(firstVisibleRow);
        for (let r = firstVisibleRow; r <= TOTAL_ROWS; r++) {
            lastVisibleRow = r;
            y += getRowHeight(r);
            if (y > scrollTop + viewHeight + BUFFER_ROWS * DEFAULT_ROW_HEIGHT) break;
        }

        // Find visible cols
        let firstVisibleCol = 1;
        let x = ROW_HEADER_WIDTH;
        for (let c = 1; c <= TOTAL_COLS; c++) {
            const cw = getColWidth(indexToColLetter(c));
            if (x + cw > scrollLeft) { firstVisibleCol = c; break; }
            x += cw;
        }
        firstVisibleCol = Math.max(1, firstVisibleCol - 2);

        let lastVisibleCol = firstVisibleCol;
        x = getColX(firstVisibleCol);
        for (let c = firstVisibleCol; c <= TOTAL_COLS; c++) {
            lastVisibleCol = c;
            x += getColWidth(indexToColLetter(c));
            if (x > scrollLeft + viewWidth + 200) break;
        }

        const totalH = getRowY(TOTAL_ROWS + 1);
        const totalW = getTotalWidth();

        let html = '';
        html += `<div class="grid-inner" style="width:${totalW}px;height:${totalH}px;position:relative;">`;

        // Column headers
        html += `<div class="col-headers" style="position:sticky;top:0;z-index:3;height:${HEADER_HEIGHT}px;">`;
        html += `<div class="corner-header" style="position:sticky;left:0;z-index:4;width:${ROW_HEADER_WIDTH}px;height:${HEADER_HEIGHT}px;"></div>`;
        for (let c = firstVisibleCol; c <= lastVisibleCol; c++) {
            const col = indexToColLetter(c);
            const cx = getColX(c);
            const cw = getColWidth(col);
            const selected = isColSelected(c);
            html += `<div class="col-header${selected ? ' selected' : ''}" data-col="${col}" style="left:${cx}px;width:${cw}px;height:${HEADER_HEIGHT}px;">`;
            html += col;
            html += `<div class="col-resize-handle" data-col="${col}"></div>`;
            if (sheet.filterMode) {
                const hasFilter = sheet.filters && sheet.filters[col];
                html += `<div class="filter-arrow${hasFilter ? ' active' : ''}" data-filter-col="${col}">&#9660;</div>`;
            }
            html += `</div>`;
        }
        html += `</div>`;

        // Row headers
        for (let r = firstVisibleRow; r <= lastVisibleRow; r++) {
            const ry = getRowY(r);
            const rh = getRowHeight(r);
            const selected = isRowSelected(r);
            if (isRowHiddenByFilter(r, sheet)) continue;
            html += `<div class="row-header${selected ? ' selected' : ''}" data-row="${r}" style="top:${ry}px;height:${rh}px;width:${ROW_HEADER_WIDTH}px;">`;
            html += r;
            html += `<div class="row-resize-handle" data-row="${r}"></div>`;
            html += `</div>`;
        }

        // Cells
        for (let r = firstVisibleRow; r <= lastVisibleRow; r++) {
            if (isRowHiddenByFilter(r, sheet)) continue;
            const ry = getRowY(r);
            const rh = getRowHeight(r);
            for (let c = firstVisibleCol; c <= lastVisibleCol; c++) {
                const col = indexToColLetter(c);
                const addr = col + r;
                const cx = getColX(c);
                const cw = getColWidth(col);
                const cellData = sheet.cells[addr];
                const value = cellData ? cellData.value : '';
                const format = cellData ? (cellData.format || {}) : {};
                const isActive = activeCell.col === col && activeCell.row === r;
                const isSelected = isCellInSelection(col, r);
                const isEditing = editingCell && editingCell.col === col && editingCell.row === r;

                // Check if cell is part of a merged range
                const mergeInfo = getMergeInfo(addr, sheet);
                if (mergeInfo && mergeInfo.hidden) continue;

                let cellW = cw;
                let cellH = rh;
                if (mergeInfo && mergeInfo.master) {
                    cellW = mergeInfo.width;
                    cellH = mergeInfo.height;
                }

                let style = `left:${cx}px;top:${ry}px;width:${cellW}px;height:${cellH}px;`;
                if (format.bold) style += 'font-weight:bold;';
                if (format.italic) style += 'font-style:italic;';
                // Combine text-decoration values
                const textDecs = [];
                if (format.underline) textDecs.push('underline');
                if (format.strikethrough) textDecs.push('line-through');
                if (textDecs.length > 0) style += `text-decoration:${textDecs.join(' ')};`;
                if (format.fontColor) style += `color:${format.fontColor};`;
                if (format.backgroundColor) style += `background-color:${format.backgroundColor};`;
                if (format.horizontalAlign) style += `text-align:${format.horizontalAlign};`;
                if (format.verticalAlign) {
                    const va = format.verticalAlign === 'top' ? 'flex-start' : format.verticalAlign === 'bottom' ? 'flex-end' : 'center';
                    style += `align-items:${va};display:flex;`;
                }
                // Border CSS
                if (format.borderTop) style += `border-top:${format.borderTop};`;
                if (format.borderBottom) style += `border-bottom:${format.borderBottom};`;
                if (format.borderLeft) style += `border-left:${format.borderLeft};`;
                if (format.borderRight) style += `border-right:${format.borderRight};`;

                // Conditional formatting
                const cfStyle = getConditionalFormatStyle(addr, value, sheet);
                if (cfStyle.backgroundColor) style += `background-color:${cfStyle.backgroundColor};`;
                if (cfStyle.fontColor) style += `color:${cfStyle.fontColor};`;

                let classes = 'cell';
                if (isActive) classes += ' active';
                if (isSelected) classes += ' selected';

                const displayVal = isEditing ? '' : (formulaViewMode && cellData && cellData.formula ? cellData.formula : formatDisplayValue(value, format));

                html += `<div class="${classes}" data-addr="${addr}" data-col="${col}" data-row="${r}" style="${style}">`;
                if (isEditing) {
                    html += `<input class="cell-editor" id="cell-editor" value="${escapeHtml(editValue)}" autofocus />`;
                } else {
                    html += `<span class="cell-content">${escapeHtml(String(displayVal ?? ''))}</span>`;
                }
                html += `</div>`;

                // Autofill handle on active cell
                if (isActive && !isEditing) {
                    html += `<div class="autofill-handle" style="left:${cx + cellW - 4}px;top:${ry + cellH - 4}px;"></div>`;
                }
            }
        }

        // Selection border
        if (selectionStart && selectionEnd) {
            const s = getSelectionBounds();
            const sx = getColX(colLetterToIndex(s.startCol));
            const sy = getRowY(s.startRow);
            let sw = 0;
            for (let c = colLetterToIndex(s.startCol); c <= colLetterToIndex(s.endCol); c++) {
                sw += getColWidth(indexToColLetter(c));
            }
            let sh = 0;
            for (let r = s.startRow; r <= s.endRow; r++) {
                sh += getRowHeight(r);
            }
            html += `<div class="selection-border" style="left:${sx}px;top:${sy}px;width:${sw}px;height:${sh}px;"></div>`;
        }

        html += `</div>`;
        gridContainer.innerHTML = html;

        // Focus the cell editor if editing
        if (editingCell) {
            const editor = document.getElementById('cell-editor');
            if (editor) {
                editor.focus();
                editor.setSelectionRange(editor.value.length, editor.value.length);
            }
        }

        updateFormulaBar();
    }

    function getMergeInfo(addr, sheet) {
        if (!sheet.mergedCells || sheet.mergedCells.length === 0) return null;
        const parsed = parseAddress(addr);
        if (!parsed) return null;

        for (const range of sheet.mergedCells) {
            const [start, end] = range.split(':');
            const sp = parseAddress(start);
            const ep = parseAddress(end);
            if (!sp || !ep) continue;

            const sc = colLetterToIndex(sp.col), ec = colLetterToIndex(ep.col);
            const sr = sp.row, er = ep.row;
            const ac = colLetterToIndex(parsed.col);

            if (ac >= sc && ac <= ec && parsed.row >= sr && parsed.row <= er) {
                if (addr === start) {
                    let w = 0;
                    for (let c = sc; c <= ec; c++) w += getColWidth(indexToColLetter(c));
                    let h = 0;
                    for (let r = sr; r <= er; r++) h += getRowHeight(r);
                    return { master: true, width: w, height: h };
                }
                return { hidden: true };
            }
        }
        return null;
    }

    function isRowHiddenByFilter(row, sheet) {
        if (!sheet.filterMode || !sheet.filters || row === 1) return false;
        for (const col in sheet.filters) {
            const filter = sheet.filters[col];
            if (!filter) continue;
            const addr = col + row;
            const cellData = sheet.cells[addr];
            const value = cellData ? String(cellData.value ?? '') : '';

            if (filter.type === 'values' && filter.hiddenValues) {
                if (filter.hiddenValues.includes(value)) return true;
            }
            if (filter.type === 'condition') {
                if (!matchesFilterCondition(value, filter)) return true;
            }
        }
        return false;
    }

    function matchesFilterCondition(value, filter) {
        const cond = filter.condition;
        const target = filter.conditionValue || '';
        switch (cond) {
            case 'contains': return value.toLowerCase().includes(target.toLowerCase());
            case 'does_not_contain': return !value.toLowerCase().includes(target.toLowerCase());
            case 'starts_with': return value.toLowerCase().startsWith(target.toLowerCase());
            case 'ends_with': return value.toLowerCase().endsWith(target.toLowerCase());
            case 'greater_than': return Number(value) > Number(target);
            case 'less_than': return Number(value) < Number(target);
            case 'equal_to': return value == target;
            case 'between': return Number(value) >= Number(filter.conditionValue) && Number(value) <= Number(filter.conditionValue2);
            default: return true;
        }
    }

    function getConditionalFormatStyle(addr, value, sheet) {
        const result = {};
        if (!sheet.conditionalFormats) return result;
        const parsed = parseAddress(addr);
        if (!parsed) return result;

        for (const rule of sheet.conditionalFormats) {
            if (!isAddrInRange(addr, rule.range)) continue;
            if (evaluateCondition(value, rule)) {
                if (rule.backgroundColor) result.backgroundColor = rule.backgroundColor;
                if (rule.fontColor) result.fontColor = rule.fontColor;
            }
        }
        return result;
    }

    function isAddrInRange(addr, rangeStr) {
        if (!rangeStr) return false;
        const cells = expandRange(rangeStr, AppState.getState().activeSheet);
        return cells.some(c => c.addr === addr);
    }

    function evaluateCondition(value, rule) {
        const numVal = Number(value);
        switch (rule.type) {
            case 'greater_than': return !isNaN(numVal) && numVal > Number(rule.value);
            case 'less_than': return !isNaN(numVal) && numVal < Number(rule.value);
            case 'equal_to': return String(value) === String(rule.value);
            case 'between': return !isNaN(numVal) && numVal >= Number(rule.value) && numVal <= Number(rule.value2);
            case 'text_contains': return String(value).toLowerCase().includes(String(rule.value).toLowerCase());
            case 'is_empty': return value === null || value === undefined || value === '';
            case 'is_not_empty': return value !== null && value !== undefined && value !== '';
            default: return false;
        }
    }

    function formatDisplayValue(value, format) {
        if (value === null || value === undefined || value === '') return '';
        if (typeof value === 'string' && value.startsWith('#')) return value; // error values

        const nf = format.numberFormat;
        if (!nf || nf === 'general' || nf === 'text') return value;

        const num = Number(value);
        if (isNaN(num)) return value;

        switch (nf) {
            case 'number': return num.toFixed(format.decimalPlaces ?? 2);
            case 'currency': return '$' + num.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
            case 'percentage': return (num * 100).toFixed(format.decimalPlaces ?? 0) + '%';
            case 'date': return value;
            default: return value;
        }
    }

    function getSelectionBounds() {
        if (!selectionStart || !selectionEnd) return null;
        const sc = colLetterToIndex(selectionStart.col);
        const ec = colLetterToIndex(selectionEnd.col);
        const sr = selectionStart.row;
        const er = selectionEnd.row;
        return {
            startCol: indexToColLetter(Math.min(sc, ec)),
            endCol: indexToColLetter(Math.max(sc, ec)),
            startRow: Math.min(sr, er),
            endRow: Math.max(sr, er)
        };
    }

    function getSelectedAddresses() {
        const addrs = [];
        if (selectionStart && selectionEnd) {
            const bounds = getSelectionBounds();
            const sc = colLetterToIndex(bounds.startCol);
            const ec = colLetterToIndex(bounds.endCol);
            for (let r = bounds.startRow; r <= bounds.endRow; r++) {
                for (let c = sc; c <= ec; c++) {
                    addrs.push(indexToColLetter(c) + r);
                }
            }
        }
        if (addrs.length === 0) {
            addrs.push(activeCell.col + activeCell.row);
        }
        return addrs;
    }

    function isCellInSelection(col, row) {
        if (!selectionStart || !selectionEnd) return false;
        const bounds = getSelectionBounds();
        const ci = colLetterToIndex(col);
        const sci = colLetterToIndex(bounds.startCol);
        const eci = colLetterToIndex(bounds.endCol);
        return ci >= sci && ci <= eci && row >= bounds.startRow && row <= bounds.endRow;
    }

    function isColSelected(colIdx) {
        if (!selectionStart || !selectionEnd) {
            return colLetterToIndex(activeCell.col) === colIdx;
        }
        const bounds = getSelectionBounds();
        const sci = colLetterToIndex(bounds.startCol);
        const eci = colLetterToIndex(bounds.endCol);
        return colIdx >= sci && colIdx <= eci;
    }

    function isRowSelected(row) {
        if (!selectionStart || !selectionEnd) {
            return activeCell.row === row;
        }
        const bounds = getSelectionBounds();
        return row >= bounds.startRow && row <= bounds.endRow;
    }

    function setActiveCell(col, row) {
        activeCell = { col, row };
        selectionStart = null;
        selectionEnd = null;
        if (editingCell) commitEdit();
        render();
    }

    function startEditing(col, row, initialValue) {
        const sheet = AppState.getActiveSheet();
        const addr = col + row;
        const cellData = sheet.cells[addr];
        editingCell = { col, row };
        if (initialValue !== undefined) {
            editValue = initialValue;
        } else {
            editValue = cellData ? (cellData.formula || String(cellData.value ?? '')) : '';
        }
        render();
        updateFormulaBar();
    }

    function commitEdit() {
        if (!editingCell) return;
        const addr = editingCell.col + editingCell.row;
        const si = AppState.getState().activeSheet;
        AppState.setCellValue(si, addr, editValue);
        editingCell = null;
        editValue = '';
        render();
    }

    function cancelEdit() {
        editingCell = null;
        editValue = '';
        render();
    }

    function updateFormulaBar() {
        const addrLabel = document.getElementById('formula-addr');
        const formulaInput = document.getElementById('formula-input');
        if (addrLabel) addrLabel.textContent = activeCell.col + activeCell.row;
        if (formulaInput) {
            const sheet = AppState.getActiveSheet();
            const addr = activeCell.col + activeCell.row;
            const cellData = sheet.cells[addr];
            if (editingCell) {
                formulaInput.value = editValue;
            } else {
                formulaInput.value = cellData ? (cellData.formula || String(cellData.value ?? '')) : '';
            }
        }
    }

    function attachEvents() {
        gridContainer.addEventListener('mousedown', handleMouseDown);
        gridContainer.addEventListener('dblclick', handleDblClick);
        gridContainer.addEventListener('contextmenu', handleContextMenu);
        document.addEventListener('keydown', handleKeyDown);
        document.addEventListener('mouseup', handleMouseUp);
        document.addEventListener('mousemove', handleMouseMove);

        gridContainer.addEventListener('scroll', () => {
            render();
        });

        const formulaInput = document.getElementById('formula-input');
        if (formulaInput) {
            formulaInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    if (!editingCell) {
                        startEditing(activeCell.col, activeCell.row);
                    }
                    editValue = formulaInput.value;
                    commitEdit();
                    moveActive(0, 1);
                } else if (e.key === 'Escape') {
                    cancelEdit();
                } else {
                    if (!editingCell) {
                        startEditing(activeCell.col, activeCell.row);
                    }
                    setTimeout(() => { editValue = formulaInput.value; }, 0);
                }
            });
            formulaInput.addEventListener('input', () => {
                if (editingCell) {
                    editValue = formulaInput.value;
                    const editor = document.getElementById('cell-editor');
                    if (editor) editor.value = editValue;
                }
            });
        }

        const addrLabel = document.getElementById('formula-addr');
        if (addrLabel) {
            addrLabel.addEventListener('click', () => {
                // Replace the label with an editable input for cell navigation
                const currentText = addrLabel.textContent;
                const navInput = document.createElement('input');
                navInput.type = 'text';
                navInput.value = currentText;
                navInput.className = 'formula-addr-input';
                navInput.style.cssText = 'width:80px;height:100%;border:1px solid #1a73e8;outline:none;padding:0 4px;font-size:12px;text-align:center;';
                addrLabel.replaceWith(navInput);
                navInput.focus();
                navInput.select();

                const finishNav = () => {
                    const val = navInput.value.toUpperCase().trim();
                    const parsed = parseAddress(val);
                    // Restore the label
                    const newLabel = document.createElement('div');
                    newLabel.className = 'formula-addr';
                    newLabel.id = 'formula-addr';
                    newLabel.textContent = activeCell.col + activeCell.row;
                    navInput.replaceWith(newLabel);
                    // Re-attach click handler
                    attachAddrLabelHandler(newLabel);

                    if (parsed && parsed.row >= 1 && parsed.row <= TOTAL_ROWS) {
                        setActiveCell(parsed.col, parsed.row);
                        scrollToCell(parsed.col, parsed.row);
                    }
                };
                navInput.addEventListener('blur', finishNav);
                navInput.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') { e.preventDefault(); finishNav(); }
                    if (e.key === 'Escape') { navInput.value = currentText; finishNav(); }
                });
            });
        }

        function attachAddrLabelHandler(label) {
            label.addEventListener('click', () => {
                const currentText = label.textContent;
                const navInput = document.createElement('input');
                navInput.type = 'text';
                navInput.value = currentText;
                navInput.style.cssText = 'width:80px;height:100%;border:1px solid #1a73e8;outline:none;padding:0 4px;font-size:12px;text-align:center;';
                label.replaceWith(navInput);
                navInput.focus();
                navInput.select();

                const finishNav = () => {
                    const val = navInput.value.toUpperCase().trim();
                    const parsed = parseAddress(val);
                    const newLabel = document.createElement('div');
                    newLabel.className = 'formula-addr';
                    newLabel.id = 'formula-addr';
                    newLabel.textContent = activeCell.col + activeCell.row;
                    navInput.replaceWith(newLabel);
                    attachAddrLabelHandler(newLabel);
                    if (parsed && parsed.row >= 1 && parsed.row <= TOTAL_ROWS) {
                        setActiveCell(parsed.col, parsed.row);
                        scrollToCell(parsed.col, parsed.row);
                    }
                };
                navInput.addEventListener('blur', finishNav);
                navInput.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') { e.preventDefault(); finishNav(); }
                    if (e.key === 'Escape') { navInput.value = currentText; finishNav(); }
                });
            });
        }
    }

    function handleMouseDown(e) {
        const target = e.target;

        // Autofill handle
        if (target.classList.contains('autofill-handle')) {
            autofillStart = { col: activeCell.col, row: activeCell.row };
            e.preventDefault();
            return;
        }

        // Column resize
        if (target.classList.contains('col-resize-handle')) {
            resizingCol = target.dataset.col;
            resizeStartX = e.clientX;
            resizeStartSize = getColWidth(resizingCol);
            e.preventDefault();
            return;
        }

        // Row resize
        if (target.classList.contains('row-resize-handle')) {
            resizingRow = parseInt(target.dataset.row);
            resizeStartY = e.clientY;
            resizeStartSize = getRowHeight(resizingRow);
            e.preventDefault();
            return;
        }

        // Corner header - select all
        if (target.classList.contains('corner-header')) {
            selectionStart = { col: 'A', row: 1 };
            selectionEnd = { col: indexToColLetter(TOTAL_COLS), row: TOTAL_ROWS };
            render();
            return;
        }

        // Column header - select column
        if (target.classList.contains('col-header') || target.parentElement?.classList.contains('col-header')) {
            const colEl = target.classList.contains('col-header') ? target : target.parentElement;
            const col = colEl.dataset.col;
            if (col) {
                if (e.shiftKey && selectionStart) {
                    selectionEnd = { col, row: TOTAL_ROWS };
                } else {
                    selectionStart = { col, row: 1 };
                    selectionEnd = { col, row: TOTAL_ROWS };
                    activeCell = { col, row: 1 };
                }
                render();
            }
            return;
        }

        // Row header - select row
        if (target.classList.contains('row-header')) {
            const row = parseInt(target.dataset.row);
            if (row) {
                if (e.shiftKey && selectionStart) {
                    selectionEnd = { col: indexToColLetter(TOTAL_COLS), row };
                } else {
                    selectionStart = { col: 'A', row };
                    selectionEnd = { col: indexToColLetter(TOTAL_COLS), row };
                    activeCell = { col: 'A', row };
                }
                render();
            }
            return;
        }

        // Filter arrow
        if (target.classList.contains('filter-arrow')) {
            const col = target.dataset.filterCol;
            if (col) App.showFilterDialog(col);
            e.preventDefault();
            return;
        }

        // Cell click
        const cell = target.closest('.cell');
        if (cell) {
            const col = cell.dataset.col;
            const row = parseInt(cell.dataset.row);
            if (col && row) {
                if (editingCell) commitEdit();
                if (e.shiftKey) {
                    if (!selectionStart) selectionStart = { ...activeCell };
                    selectionEnd = { col, row };
                } else if (e.ctrlKey || e.metaKey) {
                    // Multi-select: save current selection and start new
                    if (selectionStart && selectionEnd) {
                        multiSelections.push({ start: selectionStart, end: selectionEnd });
                    }
                    activeCell = { col, row };
                    selectionStart = { col, row };
                    selectionEnd = { col, row };
                } else {
                    activeCell = { col, row };
                    selectionStart = { col, row };
                    selectionEnd = { col, row };
                    multiSelections = [];
                }
                render();
            }
        }
    }

    function handleDblClick(e) {
        // Double-click on column resize handle = auto-fit
        if (e.target.classList.contains('col-resize-handle')) {
            const col = e.target.dataset.col;
            autoFitColumn(col);
            return;
        }

        const cell = e.target.closest('.cell');
        if (cell) {
            const col = cell.dataset.col;
            const row = parseInt(cell.dataset.row);
            if (col && row) {
                startEditing(col, row);
            }
        }
    }

    function handleContextMenu(e) {
        e.preventDefault();
        const cell = e.target.closest('.cell');
        const colHeader = e.target.closest('.col-header');
        const rowHeader = e.target.closest('.row-header');

        if (colHeader) {
            const col = colHeader.dataset.col;
            App.showContextMenu(e.clientX, e.clientY, [
                { label: 'Sort A \u2192 Z', action: () => App.sortColumn(col, 'asc') },
                { label: 'Sort Z \u2192 A', action: () => App.sortColumn(col, 'desc') },
                { label: 'Insert column left', action: () => AppState.insertColumn(AppState.getState().activeSheet, indexToColLetter(colLetterToIndex(col) - 1)) },
                { label: 'Delete column', action: () => AppState.deleteColumn(AppState.getState().activeSheet, col) }
            ]);
        } else if (rowHeader) {
            const row = parseInt(rowHeader.dataset.row);
            App.showContextMenu(e.clientX, e.clientY, [
                { label: 'Insert row above', action: () => AppState.insertRow(AppState.getState().activeSheet, row - 1) },
                { label: 'Delete row', action: () => AppState.deleteRow(AppState.getState().activeSheet, row) }
            ]);
        } else if (cell) {
            App.showContextMenu(e.clientX, e.clientY, [
                { label: 'Cut', action: () => doCut() },
                { label: 'Copy', action: () => doCopy() },
                { label: 'Paste', action: () => doPaste() },
                { label: 'Insert row above', action: () => AppState.insertRow(AppState.getState().activeSheet, activeCell.row - 1) },
                { label: 'Insert column left', action: () => AppState.insertColumn(AppState.getState().activeSheet, indexToColLetter(colLetterToIndex(activeCell.col) - 1)) },
                { label: 'Delete row', action: () => AppState.deleteRow(AppState.getState().activeSheet, activeCell.row) },
                { label: 'Delete column', action: () => AppState.deleteColumn(AppState.getState().activeSheet, activeCell.col) }
            ]);
        }
    }

    function handleMouseUp(e) {
        if (resizingCol) {
            resizingCol = null;
            return;
        }
        if (resizingRow) {
            resizingRow = null;
            return;
        }
        if (autofillStart) {
            performAutofill(autofillStart, activeCell);
            autofillStart = null;
        }
    }

    function handleMouseMove(e) {
        if (resizingCol) {
            const delta = e.clientX - resizeStartX;
            const newW = Math.max(30, resizeStartSize + delta);
            AppState.setColumnWidth(AppState.getState().activeSheet, resizingCol, newW);
            render();
            return;
        }
        if (resizingRow) {
            const delta = e.clientY - resizeStartY;
            const newH = Math.max(15, resizeStartSize + delta);
            AppState.setRowHeight(AppState.getState().activeSheet, resizingRow, newH);
            render();
            return;
        }
        // Drag selection
        if (e.buttons === 1 && selectionStart && !autofillStart) {
            const cell = document.elementFromPoint(e.clientX, e.clientY);
            if (cell) {
                const cellEl = cell.closest('.cell');
                if (cellEl) {
                    const col = cellEl.dataset.col;
                    const row = parseInt(cellEl.dataset.row);
                    if (col && row) {
                        selectionEnd = { col, row };
                        render();
                    }
                }
            }
        }
    }

    function handleKeyDown(e) {
        // Don't handle keys when dialogs are open
        if (document.querySelector('.modal-overlay.visible')) return;
        if (document.activeElement && document.activeElement.tagName === 'INPUT' &&
            document.activeElement.id !== 'cell-editor' && document.activeElement.id !== 'formula-input') return;

        if (editingCell) {
            handleEditingKeyDown(e);
            return;
        }

        // Ctrl shortcuts
        if (e.ctrlKey || e.metaKey) {
            switch (e.key.toLowerCase()) {
                case 'z':
                    e.preventDefault();
                    if (e.shiftKey) { AppState.redo(); } else { AppState.undo(); }
                    render();
                    return;
                case 'y':
                    e.preventDefault();
                    AppState.redo();
                    render();
                    return;
                case 'c':
                    e.preventDefault();
                    doCopy();
                    return;
                case 'x':
                    e.preventDefault();
                    doCut();
                    return;
                case 'v':
                    e.preventDefault();
                    doPaste();
                    return;
                case 'b':
                    e.preventDefault();
                    App.toggleBold();
                    return;
                case 'i':
                    e.preventDefault();
                    App.toggleItalic();
                    return;
                case 'u':
                    e.preventDefault();
                    App.toggleUnderline();
                    return;
                case 'h':
                    e.preventDefault();
                    App.showFindReplace();
                    return;
            }
        }

        switch (e.key) {
            case 'ArrowUp': e.preventDefault(); moveActive(0, -1); break;
            case 'ArrowDown': e.preventDefault(); moveActive(0, 1); break;
            case 'ArrowLeft': e.preventDefault(); moveActive(-1, 0); break;
            case 'ArrowRight': e.preventDefault(); moveActive(1, 0); break;
            case 'Tab':
                e.preventDefault();
                moveActive(e.shiftKey ? -1 : 1, 0);
                break;
            case 'Enter':
                e.preventDefault();
                if (e.shiftKey) moveActive(0, -1);
                else startEditing(activeCell.col, activeCell.row);
                break;
            case 'Delete':
            case 'Backspace':
                e.preventDefault();
                clearSelection();
                break;
            case 'F2':
                e.preventDefault();
                startEditing(activeCell.col, activeCell.row);
                break;
            default:
                if (e.key.length === 1 && !e.ctrlKey && !e.metaKey && !e.altKey) {
                    startEditing(activeCell.col, activeCell.row, e.key);
                }
                break;
        }
    }

    function handleEditingKeyDown(e) {
        const editor = document.getElementById('cell-editor');

        if (e.key === 'Enter') {
            e.preventDefault();
            if (editor) editValue = editor.value;
            commitEdit();
            if (e.shiftKey) moveActive(0, -1); else moveActive(0, 1);
        } else if (e.key === 'Escape') {
            e.preventDefault();
            cancelEdit();
        } else if (e.key === 'Tab') {
            e.preventDefault();
            if (editor) editValue = editor.value;
            commitEdit();
            moveActive(e.shiftKey ? -1 : 1, 0);
        } else {
            // Sync editor value
            setTimeout(() => {
                if (editor) {
                    editValue = editor.value;
                    const formulaInput = document.getElementById('formula-input');
                    if (formulaInput) formulaInput.value = editValue;
                }
            }, 0);
        }
    }

    function moveActive(dc, dr) {
        const ci = colLetterToIndex(activeCell.col) + dc;
        const ri = activeCell.row + dr;
        if (ci >= 1 && ci <= TOTAL_COLS && ri >= 1 && ri <= TOTAL_ROWS) {
            setActiveCell(indexToColLetter(ci), ri);
        }
    }

    function clearSelection() {
        const si = AppState.getState().activeSheet;
        const addrs = getSelectedAddresses();
        AppState.saveUndoSnapshot();
        addrs.forEach(addr => {
            const sheet = AppState.getActiveSheet();
            if (sheet.cells[addr]) {
                sheet.cells[addr].value = null;
                sheet.cells[addr].formula = null;
            }
        });
        AppState.notify();
        render();
    }

    function doCopy() {
        const addrs = getSelectedAddresses();
        const si = AppState.getState().activeSheet;
        const sheet = AppState.getActiveSheet();
        clipboard = addrs.map(addr => ({
            addr,
            data: sheet.cells[addr] ? JSON.parse(JSON.stringify(sheet.cells[addr])) : null
        }));
        clipboardMode = 'copy';
    }

    function doCut() {
        doCopy();
        clipboardMode = 'cut';
    }

    function doPaste() {
        if (!clipboard || clipboard.length === 0) return;
        const si = AppState.getState().activeSheet;
        const sheet = AppState.getActiveSheet();
        AppState.saveUndoSnapshot();

        // Calculate offset from first clipboard cell to active cell
        const firstAddr = parseAddress(clipboard[0].addr);
        if (!firstAddr) return;
        const colOffset = colLetterToIndex(activeCell.col) - colLetterToIndex(firstAddr.col);
        const rowOffset = activeCell.row - firstAddr.row;

        clipboard.forEach(item => {
            const parsed = parseAddress(item.addr);
            if (!parsed) return;
            const newCol = colLetterToIndex(parsed.col) + colOffset;
            const newRow = parsed.row + rowOffset;
            if (newCol < 1 || newCol > TOTAL_COLS || newRow < 1 || newRow > TOTAL_ROWS) return;
            const newAddr = indexToColLetter(newCol) + newRow;

            if (item.data) {
                sheet.cells[newAddr] = JSON.parse(JSON.stringify(item.data));
                // Adjust formula references for copy
                if (item.data.formula && clipboardMode === 'copy') {
                    sheet.cells[newAddr].formula = adjustFormulaRefs(item.data.formula, colOffset, rowOffset);
                    sheet.cells[newAddr].value = FormulaEngine.evaluate(sheet.cells[newAddr].formula, si);
                }
            }
        });

        if (clipboardMode === 'cut') {
            clipboard.forEach(item => {
                delete sheet.cells[item.addr];
            });
            clipboard = null;
            clipboardMode = null;
        }

        AppState.notify();
        render();
    }

    function adjustFormulaRefs(formula, colOffset, rowOffset) {
        if (!formula) return formula;
        return formula.replace(/(\$?)([A-Z]+)(\$?)(\d+)/g, (match, absc, col, absr, row) => {
            let newCol = col;
            let newRow = parseInt(row);
            if (!absc) {
                const ci = colLetterToIndex(col) + colOffset;
                if (ci >= 1 && ci <= TOTAL_COLS) newCol = indexToColLetter(ci);
            }
            if (!absr) {
                newRow = newRow + rowOffset;
            }
            return (absc || '') + newCol + (absr || '') + newRow;
        });
    }

    function performAutofill(start, end) {
        // Simple autofill: extend values downward
        const si = AppState.getState().activeSheet;
        const sheet = AppState.getActiveSheet();
        const startAddr = start.col + start.row;
        const cellData = sheet.cells[startAddr];
        if (!cellData) return;

        AppState.saveUndoSnapshot();
        const val = cellData.value;
        const formula = cellData.formula;

        const dr = end.row > start.row ? 1 : (end.row < start.row ? -1 : 0);
        if (dr === 0) return;

        let r = start.row + dr;
        const endRow = end.row;
        let step = 1;
        while ((dr > 0 && r <= endRow) || (dr < 0 && r >= endRow)) {
            const addr = start.col + r;
            if (formula) {
                const adjusted = adjustFormulaRefs(formula, 0, step * dr);
                sheet.cells[addr] = { value: FormulaEngine.evaluate(adjusted, si), formula: adjusted, format: { ...(cellData.format || {}) } };
            } else if (typeof val === 'number') {
                sheet.cells[addr] = { value: val + step, formula: null, format: { ...(cellData.format || {}) } };
            } else {
                sheet.cells[addr] = { value: val, formula: null, format: { ...(cellData.format || {}) } };
            }
            r += dr;
            step++;
        }

        AppState.notify();
        render();
    }

    function autoFitColumn(col) {
        const sheet = AppState.getActiveSheet();
        let maxWidth = 50;
        for (let r = 1; r <= TOTAL_ROWS; r++) {
            const addr = col + r;
            const cellData = sheet.cells[addr];
            if (cellData && cellData.value != null) {
                const textLen = String(cellData.value).length * 8 + 16;
                if (textLen > maxWidth) maxWidth = textLen;
            }
        }
        AppState.setColumnWidth(AppState.getState().activeSheet, col, Math.min(maxWidth, 400));
        render();
    }

    function scrollToCell(col, row) {
        const x = getColX(colLetterToIndex(col));
        const y = getRowY(row);
        gridContainer.scrollTo({ left: x - ROW_HEADER_WIDTH, top: y - HEADER_HEIGHT, behavior: 'smooth' });
    }

    function escapeHtml(str) {
        return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    function getActiveCell() { return activeCell; }
    function getEditingCell() { return editingCell; }
    function setFormulaViewMode(val) { formulaViewMode = val; }

    function pasteValuesOnly() {
        if (!clipboard || clipboard.length === 0) return;
        const si = AppState.getState().activeSheet;
        const sheet = AppState.getActiveSheet();
        AppState.saveUndoSnapshot();
        const firstAddr = parseAddress(clipboard[0].addr);
        if (!firstAddr) return;
        const colOffset = colLetterToIndex(activeCell.col) - colLetterToIndex(firstAddr.col);
        const rowOffset = activeCell.row - firstAddr.row;

        clipboard.forEach(item => {
            const parsed = parseAddress(item.addr);
            if (!parsed || !item.data) return;
            const newCol = colLetterToIndex(parsed.col) + colOffset;
            const newRow = parsed.row + rowOffset;
            if (newCol < 1 || newCol > TOTAL_COLS || newRow < 1 || newRow > TOTAL_ROWS) return;
            const newAddr = indexToColLetter(newCol) + newRow;
            if (!sheet.cells[newAddr]) sheet.cells[newAddr] = { value: null, formula: null, format: {} };
            sheet.cells[newAddr].value = item.data.value;
            sheet.cells[newAddr].formula = null;
        });
        AppState.notify();
        render();
    }

    function pasteFormulasOnly() {
        doPaste(); // default paste already copies formulas
    }

    function pasteFormattingOnly() {
        if (!clipboard || clipboard.length === 0) return;
        const si = AppState.getState().activeSheet;
        const sheet = AppState.getActiveSheet();
        AppState.saveUndoSnapshot();
        const firstAddr = parseAddress(clipboard[0].addr);
        if (!firstAddr) return;
        const colOffset = colLetterToIndex(activeCell.col) - colLetterToIndex(firstAddr.col);
        const rowOffset = activeCell.row - firstAddr.row;

        clipboard.forEach(item => {
            const parsed = parseAddress(item.addr);
            if (!parsed || !item.data) return;
            const newCol = colLetterToIndex(parsed.col) + colOffset;
            const newRow = parsed.row + rowOffset;
            if (newCol < 1 || newCol > TOTAL_COLS || newRow < 1 || newRow > TOTAL_ROWS) return;
            const newAddr = indexToColLetter(newCol) + newRow;
            if (!sheet.cells[newAddr]) sheet.cells[newAddr] = { value: null, formula: null, format: {} };
            sheet.cells[newAddr].format = JSON.parse(JSON.stringify(item.data.format || {}));
        });
        AppState.notify();
        render();
    }

    return {
        TOTAL_ROWS, TOTAL_COLS, DEFAULT_COL_WIDTH, DEFAULT_ROW_HEIGHT,
        init, render, getActiveCell, getEditingCell, setFormulaViewMode,
        setActiveCell, startEditing, commitEdit, cancelEdit,
        getSelectedAddresses, getSelectionBounds,
        doCopy, doCut, doPaste, pasteValuesOnly, pasteFormulasOnly, pasteFormattingOnly,
        clearSelection, scrollToCell, moveActive
    };
})();
