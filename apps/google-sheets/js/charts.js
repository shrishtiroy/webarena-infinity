const Charts = (function() {
    let dragState = null;
    let resizeState = null;

    function renderCharts(sheetIndex) {
        const sheet = AppState.getState().sheets[sheetIndex];
        if (!sheet.charts || sheet.charts.length === 0) return '';

        let html = '';
        sheet.charts.forEach((chart, i) => {
            html += renderChart(chart, sheetIndex);
        });
        return html;
    }

    function renderChart(chart, sheetIndex) {
        const x = chart.position?.x || 200;
        const y = chart.position?.y || 100;
        const w = chart.size?.width || 400;
        const h = chart.size?.height || 300;

        let html = `<div class="chart-container" data-chart-id="${chart.id}" data-testid="${chart.id}"
            style="left:${x}px;top:${y}px;width:${w}px;height:${h}px;">`;
        html += `<div class="chart-header">`;
        html += `<span class="chart-title">${Components.escapeHtml(chart.title || 'Chart')}</span>`;
        html += `<div class="chart-actions">`;
        html += `<button class="chart-action-btn" data-chart-action="edit" data-chart-id="${chart.id}" title="Edit">&#9998;</button>`;
        html += `<button class="chart-action-btn" data-chart-action="duplicate" data-chart-id="${chart.id}" title="Duplicate">&#10064;</button>`;
        html += `<button class="chart-action-btn" data-chart-action="delete" data-chart-id="${chart.id}" title="Delete">&times;</button>`;
        html += `</div></div>`;
        html += `<canvas class="chart-canvas" id="canvas-${chart.id}" width="${w - 20}" height="${h - 50}"></canvas>`;
        html += `<div class="chart-resize-handle" data-chart-id="${chart.id}"></div>`;
        html += `</div>`;
        return html;
    }

    function drawAllCharts(sheetIndex) {
        const sheet = AppState.getState().sheets[sheetIndex];
        if (!sheet.charts) return;

        sheet.charts.forEach(chart => {
            const canvas = document.getElementById('canvas-' + chart.id);
            if (!canvas) return;
            const ctx = canvas.getContext('2d');
            drawChart(ctx, chart, canvas.width, canvas.height, sheetIndex);
        });
    }

    function drawChart(ctx, chart, width, height, sheetIndex) {
        ctx.clearRect(0, 0, width, height);
        const data = getChartData(chart, sheetIndex);
        if (!data || data.series.length === 0) {
            ctx.fillStyle = '#999';
            ctx.font = '14px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText('No data', width / 2, height / 2);
            return;
        }

        const padding = { top: 20, right: 20, bottom: 50, left: 60 };
        const plotW = width - padding.left - padding.right;
        const plotH = height - padding.top - padding.bottom;

        const colors = chart.colors || ['#4285f4', '#ea4335', '#fbbc04', '#34a853', '#ff6d01', '#46bdc6', '#7baaf7', '#f07b72'];

        switch (chart.type) {
            case 'bar': drawBarChart(ctx, data, padding, plotW, plotH, colors, false); break;
            case 'horizontal_bar': drawBarChart(ctx, data, padding, plotW, plotH, colors, true); break;
            case 'line': drawLineChart(ctx, data, padding, plotW, plotH, colors); break;
            case 'pie': drawPieChart(ctx, data, width, height, colors); break;
            case 'scatter': drawScatterChart(ctx, data, padding, plotW, plotH, colors); break;
            default: drawBarChart(ctx, data, padding, plotW, plotH, colors, false);
        }

        // Axis labels
        ctx.fillStyle = '#333';
        ctx.font = '11px sans-serif';
        if (chart.xAxisLabel) {
            ctx.textAlign = 'center';
            ctx.fillText(chart.xAxisLabel, padding.left + plotW / 2, height - 5);
        }
        if (chart.yAxisLabel) {
            ctx.save();
            ctx.translate(12, padding.top + plotH / 2);
            ctx.rotate(-Math.PI / 2);
            ctx.textAlign = 'center';
            ctx.fillText(chart.yAxisLabel, 0, 0);
            ctx.restore();
        }

        // Legend
        if (chart.showLegend !== false && data.seriesLabels.length > 1) {
            drawLegend(ctx, data.seriesLabels, colors, width, padding, chart.legendPosition || 'top');
        }
    }

    function getChartData(chart, sheetIndex) {
        if (!chart.dataRange) return null;
        const cells = expandRange(chart.dataRange, sheetIndex);
        if (cells.length === 0) return null;

        // Determine grid dimensions
        const rows = {};
        const cols = {};
        cells.forEach(c => {
            const p = parseAddress(c.addr);
            if (p) {
                rows[p.row] = true;
                cols[p.col] = true;
            }
        });

        const rowKeys = Object.keys(rows).map(Number).sort((a, b) => a - b);
        const colKeys = Object.keys(cols).sort((a, b) => colLetterToIndex(a) - colLetterToIndex(b));

        if (rowKeys.length < 2 || colKeys.length < 2) return null;

        // First row = headers (series labels)
        const seriesLabels = [];
        for (let ci = 1; ci < colKeys.length; ci++) {
            const addr = colKeys[ci] + rowKeys[0];
            const val = AppState.getCellValue(sheetIndex, addr);
            seriesLabels.push(String(val ?? 'Series ' + ci));
        }

        // First column = categories
        const categories = [];
        for (let ri = 1; ri < rowKeys.length; ri++) {
            const addr = colKeys[0] + rowKeys[ri];
            const val = AppState.getCellValue(sheetIndex, addr);
            categories.push(String(val ?? ''));
        }

        // Data series
        const series = [];
        for (let ci = 1; ci < colKeys.length; ci++) {
            const values = [];
            for (let ri = 1; ri < rowKeys.length; ri++) {
                const addr = colKeys[ci] + rowKeys[ri];
                const val = AppState.getCellValue(sheetIndex, addr);
                values.push(typeof val === 'number' ? val : (Number(val) || 0));
            }
            series.push(values);
        }

        return { categories, series, seriesLabels };
    }

    function drawBarChart(ctx, data, padding, plotW, plotH, colors, horizontal) {
        const { categories, series } = data;
        const numGroups = categories.length;
        const numSeries = series.length;

        // Find min/max
        let maxVal = 0;
        let minVal = 0;
        series.forEach(s => s.forEach(v => {
            if (v > maxVal) maxVal = v;
            if (v < minVal) minVal = v;
        }));
        maxVal = maxVal * 1.1 || 1;

        if (!horizontal) {
            const groupW = plotW / numGroups;
            const barW = (groupW * 0.7) / numSeries;
            const barGap = groupW * 0.15;

            // Y axis
            drawYAxis(ctx, padding, plotH, minVal, maxVal);

            // Bars
            series.forEach((s, si) => {
                s.forEach((v, gi) => {
                    const x = padding.left + gi * groupW + barGap + si * barW;
                    const barH = (v / maxVal) * plotH;
                    const y = padding.top + plotH - barH;
                    ctx.fillStyle = colors[si % colors.length];
                    ctx.fillRect(x, y, barW - 1, barH);
                });
            });

            // X labels
            ctx.fillStyle = '#666';
            ctx.font = '10px sans-serif';
            ctx.textAlign = 'center';
            categories.forEach((cat, i) => {
                const x = padding.left + i * groupW + groupW / 2;
                const label = cat.length > 10 ? cat.substring(0, 10) + '..' : cat;
                ctx.fillText(label, x, padding.top + plotH + 15);
            });
        } else {
            const groupH = plotH / numGroups;
            const barH = (groupH * 0.7) / numSeries;
            const barGap = groupH * 0.15;

            drawXAxis(ctx, padding, plotW, plotH, minVal, maxVal);

            series.forEach((s, si) => {
                s.forEach((v, gi) => {
                    const y = padding.top + gi * groupH + barGap + si * barH;
                    const barW = (v / maxVal) * plotW;
                    ctx.fillStyle = colors[si % colors.length];
                    ctx.fillRect(padding.left, y, barW, barH - 1);
                });
            });

            ctx.fillStyle = '#666';
            ctx.font = '10px sans-serif';
            ctx.textAlign = 'right';
            categories.forEach((cat, i) => {
                const y = padding.top + i * groupH + groupH / 2;
                const label = cat.length > 12 ? cat.substring(0, 12) + '..' : cat;
                ctx.fillText(label, padding.left - 5, y + 3);
            });
        }
    }

    function drawLineChart(ctx, data, padding, plotW, plotH, colors) {
        const { categories, series } = data;
        let maxVal = 0;
        series.forEach(s => s.forEach(v => { if (v > maxVal) maxVal = v; }));
        maxVal = maxVal * 1.1 || 1;

        drawYAxis(ctx, padding, plotH, 0, maxVal);

        const stepX = plotW / (categories.length - 1 || 1);

        series.forEach((s, si) => {
            ctx.strokeStyle = colors[si % colors.length];
            ctx.lineWidth = 2;
            ctx.beginPath();
            s.forEach((v, i) => {
                const x = padding.left + i * stepX;
                const y = padding.top + plotH - (v / maxVal) * plotH;
                if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
            });
            ctx.stroke();

            // Dots
            ctx.fillStyle = colors[si % colors.length];
            s.forEach((v, i) => {
                const x = padding.left + i * stepX;
                const y = padding.top + plotH - (v / maxVal) * plotH;
                ctx.beginPath();
                ctx.arc(x, y, 3, 0, Math.PI * 2);
                ctx.fill();
            });
        });

        ctx.fillStyle = '#666';
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'center';
        categories.forEach((cat, i) => {
            const x = padding.left + i * stepX;
            const label = cat.length > 8 ? cat.substring(0, 8) + '..' : cat;
            ctx.fillText(label, x, padding.top + plotH + 15);
        });
    }

    function drawPieChart(ctx, data, width, height, colors) {
        const values = data.series[0] || [];
        const labels = data.categories;
        const total = values.reduce((s, v) => s + Math.abs(v), 0);
        if (total === 0) return;

        const cx = width / 2;
        const cy = height / 2 - 10;
        const r = Math.min(cx, cy) - 30;

        let angle = -Math.PI / 2;
        values.forEach((v, i) => {
            const sliceAngle = (Math.abs(v) / total) * Math.PI * 2;
            ctx.fillStyle = colors[i % colors.length];
            ctx.beginPath();
            ctx.moveTo(cx, cy);
            ctx.arc(cx, cy, r, angle, angle + sliceAngle);
            ctx.closePath();
            ctx.fill();

            // Label
            const midAngle = angle + sliceAngle / 2;
            const labelR = r * 0.7;
            const lx = cx + Math.cos(midAngle) * labelR;
            const ly = cy + Math.sin(midAngle) * labelR;
            ctx.fillStyle = '#fff';
            ctx.font = '10px sans-serif';
            ctx.textAlign = 'center';
            if (labels[i]) {
                const pct = ((Math.abs(v) / total) * 100).toFixed(0) + '%';
                ctx.fillText(pct, lx, ly + 4);
            }

            angle += sliceAngle;
        });
    }

    function drawScatterChart(ctx, data, padding, plotW, plotH, colors) {
        if (data.series.length < 1) return;
        const xVals = data.series[0];
        const yVals = data.series.length > 1 ? data.series[1] : data.series[0];

        let maxX = Math.max(...xVals) * 1.1 || 1;
        let maxY = Math.max(...yVals) * 1.1 || 1;

        drawYAxis(ctx, padding, plotH, 0, maxY);
        drawXAxis(ctx, padding, plotW, plotH, 0, maxX);

        ctx.fillStyle = colors[0];
        for (let i = 0; i < xVals.length; i++) {
            const x = padding.left + (xVals[i] / maxX) * plotW;
            const y = padding.top + plotH - (yVals[i] / maxY) * plotH;
            ctx.beginPath();
            ctx.arc(x, y, 4, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    function drawYAxis(ctx, padding, plotH, minVal, maxVal) {
        const steps = 5;
        ctx.strokeStyle = '#e0e0e0';
        ctx.fillStyle = '#666';
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'right';
        ctx.lineWidth = 1;
        for (let i = 0; i <= steps; i++) {
            const val = minVal + (maxVal - minVal) * (i / steps);
            const y = padding.top + plotH - (i / steps) * plotH;
            ctx.beginPath();
            ctx.moveTo(padding.left, y);
            ctx.lineTo(padding.left + 1000, y);
            ctx.stroke();
            ctx.fillText(formatAxisValue(val), padding.left - 5, y + 3);
        }
    }

    function drawXAxis(ctx, padding, plotW, plotH, minVal, maxVal) {
        const steps = 5;
        ctx.strokeStyle = '#e0e0e0';
        ctx.fillStyle = '#666';
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'center';
        for (let i = 0; i <= steps; i++) {
            const val = minVal + (maxVal - minVal) * (i / steps);
            const x = padding.left + (i / steps) * plotW;
            ctx.fillText(formatAxisValue(val), x, padding.top + plotH + 15);
        }
    }

    function drawLegend(ctx, labels, colors, width, padding, position) {
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'left';
        const y = position === 'bottom' ? padding.top + 280 : 10;
        let x = padding.left;
        labels.forEach((label, i) => {
            ctx.fillStyle = colors[i % colors.length];
            ctx.fillRect(x, y, 10, 10);
            ctx.fillStyle = '#333';
            ctx.fillText(label, x + 14, y + 9);
            x += ctx.measureText(label).width + 30;
        });
    }

    function formatAxisValue(val) {
        if (Math.abs(val) >= 1000000) return (val / 1000000).toFixed(1) + 'M';
        if (Math.abs(val) >= 1000) return (val / 1000).toFixed(1) + 'K';
        if (val === Math.floor(val)) return String(val);
        return val.toFixed(1);
    }

    function initChartDrag() {
        document.addEventListener('mousedown', (e) => {
            const chartEl = e.target.closest('.chart-container');
            if (!chartEl) return;

            // Resize handle
            if (e.target.classList.contains('chart-resize-handle')) {
                resizeState = {
                    chartId: chartEl.dataset.chartId,
                    startX: e.clientX,
                    startY: e.clientY,
                    startW: chartEl.offsetWidth,
                    startH: chartEl.offsetHeight
                };
                e.preventDefault();
                return;
            }

            // Drag from header
            if (e.target.closest('.chart-header') && !e.target.closest('.chart-action-btn')) {
                dragState = {
                    chartId: chartEl.dataset.chartId,
                    startX: e.clientX,
                    startY: e.clientY,
                    origX: parseInt(chartEl.style.left),
                    origY: parseInt(chartEl.style.top)
                };
                e.preventDefault();
            }
        });

        document.addEventListener('mousemove', (e) => {
            if (dragState) {
                const dx = e.clientX - dragState.startX;
                const dy = e.clientY - dragState.startY;
                const chartEl = document.querySelector(`[data-chart-id="${dragState.chartId}"]`);
                if (chartEl) {
                    chartEl.style.left = (dragState.origX + dx) + 'px';
                    chartEl.style.top = (dragState.origY + dy) + 'px';
                }
            }
            if (resizeState) {
                const dx = e.clientX - resizeState.startX;
                const dy = e.clientY - resizeState.startY;
                const chartEl = document.querySelector(`[data-chart-id="${resizeState.chartId}"]`);
                if (chartEl) {
                    const w = Math.max(200, resizeState.startW + dx);
                    const h = Math.max(150, resizeState.startH + dy);
                    chartEl.style.width = w + 'px';
                    chartEl.style.height = h + 'px';
                    const canvas = chartEl.querySelector('canvas');
                    if (canvas) {
                        canvas.width = w - 20;
                        canvas.height = h - 50;
                    }
                }
            }
        });

        document.addEventListener('mouseup', (e) => {
            if (dragState) {
                const chartEl = document.querySelector(`[data-chart-id="${dragState.chartId}"]`);
                if (chartEl) {
                    const si = AppState.getState().activeSheet;
                    AppState.updateChart(si, dragState.chartId, {
                        position: { x: parseInt(chartEl.style.left), y: parseInt(chartEl.style.top) }
                    });
                }
                dragState = null;
            }
            if (resizeState) {
                const chartEl = document.querySelector(`[data-chart-id="${resizeState.chartId}"]`);
                if (chartEl) {
                    const si = AppState.getState().activeSheet;
                    AppState.updateChart(si, resizeState.chartId, {
                        size: { width: chartEl.offsetWidth, height: chartEl.offsetHeight }
                    });
                    // Redraw
                    const chart = AppState.getState().sheets[si].charts.find(c => c.id === resizeState.chartId);
                    if (chart) {
                        const canvas = chartEl.querySelector('canvas');
                        if (canvas) {
                            const ctx = canvas.getContext('2d');
                            drawChart(ctx, chart, canvas.width, canvas.height, si);
                        }
                    }
                }
                resizeState = null;
            }
        });
    }

    return {
        renderCharts, drawAllCharts, initChartDrag, getChartData, drawChart
    };
})();
