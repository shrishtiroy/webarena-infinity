const FormulaEngine = (function() {

    function evaluate(formula, sheetIndex) {
        if (!formula || !formula.startsWith('=')) return formula;
        try {
            const expr = formula.substring(1).trim();
            const result = evaluateExpression(expr, sheetIndex);
            if (result === null || result === undefined) return 0;
            return result;
        } catch (e) {
            if (e.message && e.message.startsWith('#')) return e.message;
            return '#VALUE!';
        }
    }

    function tokenize(expr) {
        const tokens = [];
        let i = 0;
        while (i < expr.length) {
            if (expr[i] === ' ') { i++; continue; }
            if (expr[i] === '"') {
                let s = '';
                i++;
                while (i < expr.length && expr[i] !== '"') {
                    s += expr[i]; i++;
                }
                i++; // closing quote
                tokens.push({ type: 'string', value: s });
                continue;
            }
            if ('+-*/&(),:'.includes(expr[i])) {
                tokens.push({ type: 'op', value: expr[i] });
                i++; continue;
            }
            if (expr.substring(i, i + 2) === '<>' || expr.substring(i, i + 2) === '>=' || expr.substring(i, i + 2) === '<=') {
                tokens.push({ type: 'op', value: expr.substring(i, i + 2) });
                i += 2; continue;
            }
            if ('><='.includes(expr[i])) {
                tokens.push({ type: 'op', value: expr[i] });
                i++; continue;
            }
            // Number
            if (/\d/.test(expr[i]) || (expr[i] === '.' && i + 1 < expr.length && /\d/.test(expr[i + 1]))) {
                let num = '';
                while (i < expr.length && (/\d/.test(expr[i]) || expr[i] === '.')) {
                    num += expr[i]; i++;
                }
                tokens.push({ type: 'number', value: parseFloat(num) });
                continue;
            }
            // Cell ref, range, function name, or sheet reference
            if (/[A-Za-z$_!'"]/.test(expr[i])) {
                let word = '';
                // Handle quoted sheet names like 'Sheet Name'!A1
                if (expr[i] === "'") {
                    word += "'";
                    i++;
                    while (i < expr.length && expr[i] !== "'") {
                        word += expr[i]; i++;
                    }
                    if (i < expr.length) { word += "'"; i++; }
                }
                while (i < expr.length && /[A-Za-z0-9$_!.]/.test(expr[i])) {
                    word += expr[i]; i++;
                }
                // Check for range (A1:B2)
                if (i < expr.length && expr[i] === ':') {
                    word += ':'; i++;
                    while (i < expr.length && /[A-Za-z0-9$]/.test(expr[i])) {
                        word += expr[i]; i++;
                    }
                    tokens.push({ type: 'range', value: word });
                } else if (i < expr.length && expr[i] === '(') {
                    tokens.push({ type: 'function', value: word.toUpperCase() });
                } else {
                    // Cell ref or named range
                    if (/^(\$?[A-Z]+\$?\d+|'[^']*'!\$?[A-Z]+\$?\d+|[A-Za-z]+!\$?[A-Z]+\$?\d+)$/i.test(word)) {
                        tokens.push({ type: 'cellref', value: word.toUpperCase() });
                    } else if (/[!]/.test(word) && word.includes(':')) {
                        tokens.push({ type: 'range', value: word });
                    } else {
                        tokens.push({ type: 'name', value: word });
                    }
                }
                continue;
            }
            i++;
        }
        return tokens;
    }

    function evaluateExpression(expr, sheetIndex) {
        const tokens = tokenize(expr);
        let pos = 0;

        function peek() { return pos < tokens.length ? tokens[pos] : null; }
        function consume() { return tokens[pos++]; }

        function parseExpr() {
            return parseComparison();
        }

        function parseComparison() {
            let left = parseConcat();
            while (peek() && peek().type === 'op' && ['>', '<', '=', '>=', '<=', '<>'].includes(peek().value)) {
                const op = consume().value;
                const right = parseConcat();
                switch (op) {
                    case '>': left = left > right; break;
                    case '<': left = left < right; break;
                    case '=': left = left == right; break;
                    case '>=': left = left >= right; break;
                    case '<=': left = left <= right; break;
                    case '<>': left = left != right; break;
                }
                left = left ? true : false;
            }
            return left;
        }

        function parseConcat() {
            let left = parseAddSub();
            while (peek() && peek().type === 'op' && peek().value === '&') {
                consume();
                const right = parseAddSub();
                left = String(left ?? '') + String(right ?? '');
            }
            return left;
        }

        function parseAddSub() {
            let left = parseMulDiv();
            while (peek() && peek().type === 'op' && (peek().value === '+' || peek().value === '-')) {
                const op = consume().value;
                const right = parseMulDiv();
                left = op === '+' ? (Number(left) + Number(right)) : (Number(left) - Number(right));
            }
            return left;
        }

        function parseMulDiv() {
            let left = parseUnary();
            while (peek() && peek().type === 'op' && (peek().value === '*' || peek().value === '/')) {
                const op = consume().value;
                const right = parseUnary();
                if (op === '/') {
                    if (Number(right) === 0) throw new Error('#DIV/0!');
                    left = Number(left) / Number(right);
                } else {
                    left = Number(left) * Number(right);
                }
            }
            return left;
        }

        function parseUnary() {
            if (peek() && peek().type === 'op' && peek().value === '-') {
                consume();
                return -Number(parsePrimary());
            }
            if (peek() && peek().type === 'op' && peek().value === '+') {
                consume();
                return Number(parsePrimary());
            }
            return parsePrimary();
        }

        function parsePrimary() {
            const t = peek();
            if (!t) throw new Error('#VALUE!');

            if (t.type === 'number') {
                consume();
                return t.value;
            }
            if (t.type === 'string') {
                consume();
                return t.value;
            }
            if (t.type === 'op' && t.value === '(') {
                consume();
                const val = parseExpr();
                if (peek() && peek().value === ')') consume();
                return val;
            }
            if (t.type === 'function') {
                return parseFunction();
            }
            if (t.type === 'cellref') {
                consume();
                return resolveCellRef(t.value, sheetIndex);
            }
            if (t.type === 'range') {
                consume();
                return resolveRange(t.value, sheetIndex);
            }
            if (t.type === 'name') {
                consume();
                // Check named ranges
                const state = AppState.getState();
                if (state.namedRanges[t.value]) {
                    const ref = state.namedRanges[t.value];
                    if (ref.includes(':')) {
                        return resolveRange(ref, sheetIndex);
                    }
                    return resolveCellRef(ref, sheetIndex);
                }
                // Boolean literals
                if (t.value.toUpperCase() === 'TRUE') return true;
                if (t.value.toUpperCase() === 'FALSE') return false;
                throw new Error('#NAME?');
            }
            consume();
            throw new Error('#VALUE!');
        }

        function parseFunction() {
            const fname = consume().value;
            if (!peek() || peek().value !== '(') throw new Error('#NAME?');
            consume(); // (
            const args = [];
            if (peek() && peek().value !== ')') {
                args.push(parseExpr());
                while (peek() && peek().value === ',') {
                    consume();
                    args.push(parseExpr());
                }
            }
            if (peek() && peek().value === ')') consume();
            return callFunction(fname, args, sheetIndex);
        }

        const result = parseExpr();
        return result;
    }

    function resolveCellRef(ref, defaultSheetIndex) {
        let si = defaultSheetIndex;
        let addr = ref;

        if (ref.includes('!')) {
            const parts = ref.split('!');
            const sheetName = parts[0].replace(/'/g, '');
            const sheets = AppState.getState().sheets;
            const idx = sheets.findIndex(s => s.name.toUpperCase() === sheetName.toUpperCase());
            if (idx < 0) throw new Error('#REF!');
            si = idx;
            addr = parts[1];
        }

        addr = addr.replace(/\$/g, '');
        const val = AppState.getCellValue(si, addr);
        return val === undefined ? 0 : val;
    }

    function resolveRange(rangeStr, defaultSheetIndex) {
        const cells = expandRange(rangeStr, defaultSheetIndex);
        return cells.map(c => {
            const val = AppState.getCellValue(c.sheetIndex, c.addr);
            return val === undefined ? null : val;
        });
    }

    function flattenArgs(args) {
        const flat = [];
        for (const a of args) {
            if (Array.isArray(a)) {
                flat.push(...a);
            } else {
                flat.push(a);
            }
        }
        return flat;
    }

    function numericArgs(args) {
        return flattenArgs(args).filter(v => v !== null && v !== '' && typeof v !== 'boolean' && !isNaN(Number(v))).map(Number);
    }

    function callFunction(name, args, sheetIndex) {
        switch (name) {
            case 'SUM': {
                const nums = numericArgs(args);
                return nums.reduce((s, n) => s + n, 0);
            }
            case 'AVERAGE': {
                const nums = numericArgs(args);
                if (nums.length === 0) throw new Error('#DIV/0!');
                return nums.reduce((s, n) => s + n, 0) / nums.length;
            }
            case 'COUNT': {
                return numericArgs(args).length;
            }
            case 'COUNTA': {
                return flattenArgs(args).filter(v => v !== null && v !== '' && v !== undefined).length;
            }
            case 'MIN': {
                const nums = numericArgs(args);
                if (nums.length === 0) return 0;
                return Math.min(...nums);
            }
            case 'MAX': {
                const nums = numericArgs(args);
                if (nums.length === 0) return 0;
                return Math.max(...nums);
            }
            case 'ROUND': {
                const val = Number(args[0]);
                const places = args.length > 1 ? Number(args[1]) : 0;
                const factor = Math.pow(10, places);
                return Math.round(val * factor) / factor;
            }
            case 'ABS': {
                return Math.abs(Number(args[0]));
            }
            case 'IF': {
                const cond = args[0];
                const trueVal = args.length > 1 ? args[1] : true;
                const falseVal = args.length > 2 ? args[2] : false;
                return cond ? trueVal : falseVal;
            }
            case 'AND': {
                const flat = flattenArgs(args);
                return flat.every(v => !!v);
            }
            case 'OR': {
                const flat = flattenArgs(args);
                return flat.some(v => !!v);
            }
            case 'NOT': {
                return !args[0];
            }
            case 'VLOOKUP': {
                const searchVal = args[0];
                const range = args[1];
                const colIdx = Number(args[2]);
                const exactMatch = args.length > 3 ? !args[3] : true;

                if (!Array.isArray(range)) throw new Error('#VALUE!');
                // Need to figure out the range dimensions
                // range is a flat array from resolveRange, we need to know columns
                // We'll re-parse from the original token... simplified approach:
                // assume the range was passed as an array of values in row-major order
                // We need to get the original range string to know dimensions
                throw new Error('#N/A');
            }
            case 'CONCATENATE': {
                return flattenArgs(args).map(v => v === null ? '' : String(v)).join('');
            }
            case 'LEN': {
                return String(args[0] ?? '').length;
            }
            case 'TRIM': {
                return String(args[0] ?? '').trim();
            }
            case 'UPPER': {
                return String(args[0] ?? '').toUpperCase();
            }
            case 'LOWER': {
                return String(args[0] ?? '').toLowerCase();
            }
            case 'LEFT': {
                const str = String(args[0] ?? '');
                const n = args.length > 1 ? Number(args[1]) : 1;
                return str.substring(0, n);
            }
            case 'RIGHT': {
                const str = String(args[0] ?? '');
                const n = args.length > 1 ? Number(args[1]) : 1;
                return str.substring(str.length - n);
            }
            case 'MID': {
                const str = String(args[0] ?? '');
                const start = Number(args[1]) - 1;
                const len = Number(args[2]);
                return str.substring(start, start + len);
            }
            case 'NOW': {
                return new Date().toLocaleString();
            }
            case 'TODAY': {
                return new Date().toLocaleDateString();
            }
            default:
                throw new Error('#NAME?');
        }
    }

    function extractRefs(formula, sheetIndex) {
        if (!formula || !formula.startsWith('=')) return [];
        const expr = formula.substring(1);
        const tokens = tokenize(expr);
        const refs = [];
        for (const t of tokens) {
            if (t.type === 'cellref') {
                let si = sheetIndex;
                let addr = t.value;
                if (t.value.includes('!')) {
                    const parts = t.value.split('!');
                    const sheetName = parts[0].replace(/'/g, '');
                    const sheets = AppState.getState().sheets;
                    const idx = sheets.findIndex(s => s.name.toUpperCase() === sheetName.toUpperCase());
                    if (idx >= 0) si = idx;
                    addr = parts[1];
                }
                addr = addr.replace(/\$/g, '');
                refs.push({ sheetIndex: si, addr });
            } else if (t.type === 'range') {
                const cells = expandRange(t.value, sheetIndex);
                refs.push(...cells);
            }
        }
        return refs;
    }

    function topologicalSort(cellAddrs, sheetIndex) {
        // Simple sort - for now just return in order, dependency tracking
        // would require a full graph build. Cells with no deps first.
        const noDeps = [];
        const withDeps = [];
        const state = AppState.getState();
        const sheet = state.sheets[sheetIndex];

        cellAddrs.forEach(addr => {
            const c = sheet.cells[addr];
            if (!c || !c.formula) { noDeps.push(addr); return; }
            const refs = extractRefs(c.formula, sheetIndex);
            const hasLocalDep = refs.some(r => r.sheetIndex === sheetIndex && cellAddrs.includes(r.addr));
            if (hasLocalDep) {
                withDeps.push(addr);
            } else {
                noDeps.push(addr);
            }
        });

        return [...noDeps, ...withDeps];
    }

    return {
        evaluate,
        extractRefs,
        topologicalSort,
        tokenize
    };
})();
