const AppState = (function() {
    let state = null;
    let undoStack = [];
    let redoStack = [];
    let listeners = [];

    function init() {
        const persisted = loadPersistedData();
        if (persisted) {
            state = persisted;
        } else {
            state = getSeedData();
        }
        recalcAllFormulas();
        notify();
    }

    function loadPersistedData() {
        try {
            const saved = localStorage.getItem('googleSheetsState');
            if (!saved) return null;
            const parsed = JSON.parse(saved);
            if (parsed._seedVersion !== SEED_DATA_VERSION) {
                localStorage.removeItem('googleSheetsState');
                return null;
            }
            return parsed;
        } catch (e) {
            localStorage.removeItem('googleSheetsState');
            return null;
        }
    }

    function persist() {
        try {
            localStorage.setItem('googleSheetsState', JSON.stringify(state));
        } catch (e) {
            console.warn('Failed to persist state:', e);
        }
    }

    function pushToServer() {
        try {
            fetch('/api/state', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(state)
            });
        } catch (e) {
            console.warn('Failed to push state:', e);
        }
    }

    function notify() {
        persist();
        pushToServer();
        listeners.forEach(fn => fn(state));
    }

    function onChange(fn) {
        listeners.push(fn);
    }

    function getState() {
        return state;
    }

    function getActiveSheet() {
        return state.sheets[state.activeSheet];
    }

    function setActiveSheet(index) {
        if (index >= 0 && index < state.sheets.length) {
            state.activeSheet = index;
            notify();
        }
    }

    function saveUndoSnapshot() {
        undoStack.push(JSON.stringify(state));
        if (undoStack.length > 100) undoStack.shift();
        redoStack = [];
    }

    function undo() {
        if (undoStack.length === 0) return false;
        redoStack.push(JSON.stringify(state));
        state = JSON.parse(undoStack.pop());
        recalcAllFormulas();
        notify();
        return true;
    }

    function redo() {
        if (redoStack.length === 0) return false;
        undoStack.push(JSON.stringify(state));
        state = JSON.parse(redoStack.pop());
        recalcAllFormulas();
        notify();
        return true;
    }

    function getCellValue(sheetIndex, addr) {
        const sheet = state.sheets[sheetIndex];
        if (!sheet) return undefined;
        const c = sheet.cells[addr];
        return c ? c.value : undefined;
    }

    function getCellRaw(sheetIndex, addr) {
        const sheet = state.sheets[sheetIndex];
        if (!sheet) return null;
        return sheet.cells[addr] || null;
    }

    function setCellValue(sheetIndex, addr, rawInput) {
        const sheet = state.sheets[sheetIndex];
        if (!sheet) return;
        saveUndoSnapshot();

        if (rawInput === '' || rawInput === null || rawInput === undefined) {
            delete sheet.cells[addr];
        } else {
            if (!sheet.cells[addr]) {
                sheet.cells[addr] = { value: null, formula: null, format: {} };
            }
            const c = sheet.cells[addr];
            if (typeof rawInput === 'string' && rawInput.startsWith('=')) {
                c.formula = rawInput;
                c.value = FormulaEngine.evaluate(rawInput, sheetIndex);
            } else {
                c.formula = null;
                const num = Number(rawInput);
                c.value = (rawInput !== '' && !isNaN(num) && isFinite(num)) ? num : rawInput;
            }
        }

        recalcDependents(sheetIndex, addr);
        notify();
    }

    function setCellFormat(sheetIndex, addr, formatProp, value) {
        const sheet = state.sheets[sheetIndex];
        if (!sheet) return;
        if (!sheet.cells[addr]) {
            sheet.cells[addr] = { value: null, formula: null, format: {} };
        }
        sheet.cells[addr].format[formatProp] = value;
    }

    function applyFormatToRange(sheetIndex, addresses, formatProp, value) {
        saveUndoSnapshot();
        addresses.forEach(addr => {
            setCellFormat(sheetIndex, addr, formatProp, value);
        });
        notify();
    }

    function recalcAllFormulas() {
        state.sheets.forEach((sheet, si) => {
            const formulaCells = [];
            for (const addr in sheet.cells) {
                if (sheet.cells[addr].formula) {
                    formulaCells.push(addr);
                }
            }
            const sorted = FormulaEngine.topologicalSort(formulaCells, si);
            sorted.forEach(addr => {
                const c = sheet.cells[addr];
                if (c && c.formula) {
                    c.value = FormulaEngine.evaluate(c.formula, si);
                }
            });
        });
    }

    function recalcDependents(sheetIndex, changedAddr) {
        const visited = new Set();
        const queue = [{ si: sheetIndex, addr: changedAddr }];
        while (queue.length > 0) {
            const { si, addr } = queue.shift();
            const key = si + ':' + addr;
            if (visited.has(key)) continue;
            visited.add(key);

            state.sheets.forEach((sheet, si2) => {
                for (const a in sheet.cells) {
                    const c = sheet.cells[a];
                    if (c && c.formula) {
                        const refs = FormulaEngine.extractRefs(c.formula, si2);
                        for (const ref of refs) {
                            if (ref.sheetIndex === si && ref.addr === addr) {
                                c.value = FormulaEngine.evaluate(c.formula, si2);
                                queue.push({ si: si2, addr: a });
                                break;
                            }
                        }
                    }
                }
            });
        }
    }

    function addSheet(name) {
        saveUndoSnapshot();
        const sheetName = name || 'Sheet' + (state.sheets.length + 1);
        state.sheets.push(createEmptySheetState(sheetName));
        state.activeSheet = state.sheets.length - 1;
        notify();
    }

    function deleteSheet(index) {
        if (state.sheets.length <= 1) return;
        saveUndoSnapshot();
        state.sheets.splice(index, 1);
        if (state.activeSheet >= state.sheets.length) {
            state.activeSheet = state.sheets.length - 1;
        }
        notify();
    }

    function duplicateSheet(index) {
        saveUndoSnapshot();
        const copy = JSON.parse(JSON.stringify(state.sheets[index]));
        copy.name = copy.name + ' (Copy)';
        state.sheets.splice(index + 1, 0, copy);
        state.activeSheet = index + 1;
        notify();
    }

    function renameSheet(index, newName) {
        if (!newName || newName.trim() === '') return;
        saveUndoSnapshot();
        state.sheets[index].name = newName.trim();
        notify();
    }

    function moveSheet(fromIndex, toIndex) {
        if (fromIndex === toIndex) return;
        saveUndoSnapshot();
        const sheet = state.sheets.splice(fromIndex, 1)[0];
        state.sheets.splice(toIndex, 0, sheet);
        if (state.activeSheet === fromIndex) {
            state.activeSheet = toIndex;
        } else if (state.activeSheet > fromIndex && state.activeSheet <= toIndex) {
            state.activeSheet--;
        } else if (state.activeSheet < fromIndex && state.activeSheet >= toIndex) {
            state.activeSheet++;
        }
        notify();
    }

    function insertRow(sheetIndex, afterRow) {
        saveUndoSnapshot();
        const sheet = state.sheets[sheetIndex];
        const newCells = {};
        for (const addr in sheet.cells) {
            const parsed = parseAddress(addr);
            if (!parsed) { newCells[addr] = sheet.cells[addr]; continue; }
            if (parsed.row > afterRow) {
                newCells[parsed.col + (parsed.row + 1)] = sheet.cells[addr];
            } else {
                newCells[addr] = sheet.cells[addr];
            }
        }
        sheet.cells = newCells;
        notify();
    }

    function insertColumn(sheetIndex, afterCol) {
        saveUndoSnapshot();
        const sheet = state.sheets[sheetIndex];
        const afterColIndex = colLetterToIndex(afterCol);
        const newCells = {};
        for (const addr in sheet.cells) {
            const parsed = parseAddress(addr);
            if (!parsed) { newCells[addr] = sheet.cells[addr]; continue; }
            const ci = colLetterToIndex(parsed.col);
            if (ci > afterColIndex) {
                newCells[indexToColLetter(ci + 1) + parsed.row] = sheet.cells[addr];
            } else {
                newCells[addr] = sheet.cells[addr];
            }
        }
        sheet.cells = newCells;
        notify();
    }

    function deleteRow(sheetIndex, row) {
        saveUndoSnapshot();
        const sheet = state.sheets[sheetIndex];
        const newCells = {};
        for (const addr in sheet.cells) {
            const parsed = parseAddress(addr);
            if (!parsed) continue;
            if (parsed.row === row) continue;
            if (parsed.row > row) {
                newCells[parsed.col + (parsed.row - 1)] = sheet.cells[addr];
            } else {
                newCells[addr] = sheet.cells[addr];
            }
        }
        sheet.cells = newCells;
        notify();
    }

    function deleteColumn(sheetIndex, colLetter) {
        saveUndoSnapshot();
        const sheet = state.sheets[sheetIndex];
        const colIndex = colLetterToIndex(colLetter);
        const newCells = {};
        for (const addr in sheet.cells) {
            const parsed = parseAddress(addr);
            if (!parsed) continue;
            const ci = colLetterToIndex(parsed.col);
            if (ci === colIndex) continue;
            if (ci > colIndex) {
                newCells[indexToColLetter(ci - 1) + parsed.row] = sheet.cells[addr];
            } else {
                newCells[addr] = sheet.cells[addr];
            }
        }
        sheet.cells = newCells;
        notify();
    }

    function setNamedRange(name, reference) {
        saveUndoSnapshot();
        state.namedRanges[name] = reference;
        notify();
    }

    function deleteNamedRange(name) {
        saveUndoSnapshot();
        delete state.namedRanges[name];
        notify();
    }

    function addConditionalFormat(sheetIndex, rule) {
        saveUndoSnapshot();
        state.sheets[sheetIndex].conditionalFormats.push(rule);
        notify();
    }

    function removeConditionalFormat(sheetIndex, ruleIndex) {
        saveUndoSnapshot();
        state.sheets[sheetIndex].conditionalFormats.splice(ruleIndex, 1);
        notify();
    }

    function setFilter(sheetIndex, col, filterConfig) {
        saveUndoSnapshot();
        const sheet = state.sheets[sheetIndex];
        if (filterConfig === null) {
            delete sheet.filters[col];
        } else {
            sheet.filters[col] = filterConfig;
        }
        notify();
    }

    function toggleFilterMode(sheetIndex) {
        saveUndoSnapshot();
        const sheet = state.sheets[sheetIndex];
        sheet.filterMode = !sheet.filterMode;
        if (!sheet.filterMode) {
            sheet.filters = {};
        }
        notify();
    }

    function setFrozenRows(sheetIndex, count) {
        saveUndoSnapshot();
        state.sheets[sheetIndex].frozenRows = count;
        notify();
    }

    function setFrozenCols(sheetIndex, count) {
        saveUndoSnapshot();
        state.sheets[sheetIndex].frozenCols = count;
        notify();
    }

    function mergeCells(sheetIndex, rangeStr) {
        saveUndoSnapshot();
        const sheet = state.sheets[sheetIndex];
        if (!sheet.mergedCells.includes(rangeStr)) {
            sheet.mergedCells.push(rangeStr);
        }
        notify();
    }

    function unmergeCells(sheetIndex, rangeStr) {
        saveUndoSnapshot();
        const sheet = state.sheets[sheetIndex];
        const idx = sheet.mergedCells.indexOf(rangeStr);
        if (idx >= 0) sheet.mergedCells.splice(idx, 1);
        notify();
    }

    function setColumnWidth(sheetIndex, col, width) {
        state.sheets[sheetIndex].columnWidths[col] = width;
        notify();
    }

    function setRowHeight(sheetIndex, row, height) {
        state.sheets[sheetIndex].rowHeights[row] = height;
        notify();
    }

    function addChart(sheetIndex, chart) {
        saveUndoSnapshot();
        const sheet = state.sheets[sheetIndex];
        chart.id = 'chart-' + (Date.now() % 100000);
        sheet.charts.push(chart);
        notify();
        return chart.id;
    }

    function updateChart(sheetIndex, chartId, updates) {
        saveUndoSnapshot();
        const sheet = state.sheets[sheetIndex];
        const chart = sheet.charts.find(c => c.id === chartId);
        if (chart) {
            Object.assign(chart, updates);
            notify();
        }
    }

    function deleteChart(sheetIndex, chartId) {
        saveUndoSnapshot();
        const sheet = state.sheets[sheetIndex];
        const idx = sheet.charts.findIndex(c => c.id === chartId);
        if (idx >= 0) {
            sheet.charts.splice(idx, 1);
            notify();
        }
    }

    function resetToSeed() {
        state = getSeedData();
        undoStack = [];
        redoStack = [];
        recalcAllFormulas();
        notify();
    }

    function setupSSE() {
        const eventSource = new EventSource('/api/events');
        eventSource.onmessage = function(e) {
            if (e.data === 'reset') {
                resetToSeed();
                if (typeof App !== 'undefined' && App.render) App.render();
            }
        };
    }

    function setDataValidation(sheetIndex, addr, validation) {
        const sheet = state.sheets[sheetIndex];
        if (!sheet.cells[addr]) {
            sheet.cells[addr] = { value: null, formula: null, format: {} };
        }
        sheet.cells[addr].validation = validation;
        notify();
    }

    return {
        init, getState, getActiveSheet, setActiveSheet, onChange, notify,
        getCellValue, getCellRaw, setCellValue, setCellFormat, applyFormatToRange,
        saveUndoSnapshot, undo, redo,
        addSheet, deleteSheet, duplicateSheet, renameSheet, moveSheet,
        insertRow, insertColumn, deleteRow, deleteColumn,
        setNamedRange, deleteNamedRange,
        addConditionalFormat, removeConditionalFormat,
        setFilter, toggleFilterMode,
        setFrozenRows, setFrozenCols,
        mergeCells, unmergeCells,
        setColumnWidth, setRowHeight,
        addChart, updateChart, deleteChart,
        resetToSeed, setupSSE, recalcAllFormulas,
        setDataValidation
    };
})();

// Address utility functions
function parseAddress(addr) {
    const match = addr.match(/^([A-Z]+)(\d+)$/);
    if (!match) return null;
    return { col: match[1], row: parseInt(match[2]) };
}

function colLetterToIndex(col) {
    let idx = 0;
    for (let i = 0; i < col.length; i++) {
        idx = idx * 26 + (col.charCodeAt(i) - 64);
    }
    return idx;
}

function indexToColLetter(idx) {
    let s = '';
    while (idx > 0) {
        let rem = (idx - 1) % 26;
        s = String.fromCharCode(65 + rem) + s;
        idx = Math.floor((idx - 1) / 26);
    }
    return s;
}

function expandRange(rangeStr, defaultSheetIndex) {
    let sheetIndex = defaultSheetIndex;
    let rangePart = rangeStr;

    if (rangeStr.includes('!')) {
        const parts = rangeStr.split('!');
        const sheetName = parts[0].replace(/'/g, '');
        const stateSheets = AppState.getState().sheets;
        const si = stateSheets.findIndex(s => s.name === sheetName);
        if (si >= 0) sheetIndex = si;
        rangePart = parts[1];
    }

    if (!rangePart.includes(':')) {
        return [{ sheetIndex, addr: rangePart }];
    }

    const [start, end] = rangePart.split(':');
    const startParsed = parseAddress(start);
    const endParsed = parseAddress(end);
    if (!startParsed || !endParsed) return [];

    const startCol = colLetterToIndex(startParsed.col);
    const endCol = colLetterToIndex(endParsed.col);
    const startRow = startParsed.row;
    const endRow = endParsed.row;

    const result = [];
    for (let r = Math.min(startRow, endRow); r <= Math.max(startRow, endRow); r++) {
        for (let c = Math.min(startCol, endCol); c <= Math.max(startCol, endCol); c++) {
            result.push({ sheetIndex, addr: indexToColLetter(c) + r });
        }
    }
    return result;
}
