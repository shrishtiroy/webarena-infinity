const Views = (function() {

    function renderToolbar() {
        const pres = AppState.getPresentation();
        const ui = AppState.getUI();
        let html = '<div class="toolbar">';

        // Left: Logo + Title
        html += '<div class="toolbar-left">';
        html += '<div class="toolbar-logo"><svg width="20" height="20" viewBox="0 0 24 24" fill="none"><rect x="2" y="2" width="9" height="9" rx="2" fill="#6366f1"/><rect x="13" y="2" width="9" height="9" rx="2" fill="#ec4899"/><rect x="2" y="13" width="9" height="9" rx="2" fill="#14b8a6"/><rect x="13" y="13" width="9" height="9" rx="4.5" fill="#f59e0b"/></svg></div>';
        html += '<span class="toolbar-title" data-action="edit-title" title="Click to edit">' + Components.escapeHtml(pres.title) + '</span>';
        html += '</div>';

        // Center: Element tools (only in editor)
        if (ui.currentView === 'editor') {
            html += '<div class="toolbar-center">';
            html += '<button class="tool-btn" data-action="add-text" title="Add Text"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 7V4h16v3"/><path d="M9 20h6"/><path d="M12 4v16"/></svg></button>';
            html += '<button class="tool-btn" data-action="add-shape" title="Add Shape"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/></svg></button>';
            html += '<div class="toolbar-separator"></div>';
            html += '<button class="tool-btn' + (ui.showGrid ? ' active' : '') + '" data-action="toggle-grid" title="Toggle Grid"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3h18v18H3z"/><path d="M3 9h18"/><path d="M3 15h18"/><path d="M9 3v18"/><path d="M15 3v18"/></svg></button>';
            html += '<button class="tool-btn' + (ui.showRulers ? ' active' : '') + '" data-action="toggle-rulers" title="Toggle Rulers"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3h18v18H3z"/><path d="M3 7h4"/><path d="M3 11h2"/><path d="M3 15h4"/><path d="M3 19h2"/><path d="M7 3v4"/><path d="M11 3v2"/><path d="M15 3v4"/><path d="M19 3v2"/></svg></button>';
            html += '<div class="toolbar-separator"></div>';
            html += '<span class="zoom-control">';
            html += '<button class="tool-btn tool-btn-sm" data-action="zoom-out" title="Zoom Out">-</button>';
            html += '<span class="zoom-value">' + ui.zoom + '%</span>';
            html += '<button class="tool-btn tool-btn-sm" data-action="zoom-in" title="Zoom In">+</button>';
            html += '</span>';
            html += '</div>';
        }

        // Right: Actions
        html += '<div class="toolbar-right">';
        if (ui.currentView === 'editor') {
            html += '<button class="tool-btn" data-action="open-comments" title="Comments"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>';
            const unresolved = (AppState.getComments() || []).filter(c => !c.resolved).length;
            if (unresolved > 0) html += '<span class="toolbar-badge">' + unresolved + '</span>';
            html += '</button>';
            html += '<button class="tool-btn" data-action="open-templates" title="Templates"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg></button>';
            html += '<button class="tool-btn" data-action="open-settings" title="Presentation Settings"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 01-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.32 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg></button>';
        }
        html += '<button class="btn btn-primary btn-sm" data-action="present" title="Present"><svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="5,3 19,12 5,21"/></svg> Present</button>';
        if (ui.currentView === 'editor') {
            html += '<button class="tool-btn" data-action="open-export" title="Export & Share"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 12v8a2 2 0 002 2h12a2 2 0 002-2v-8"/><polyline points="16 6 12 2 8 6"/><line x1="12" y1="2" x2="12" y2="15"/></svg></button>';
        }
        if (ui.currentView !== 'editor') {
            html += '<button class="btn btn-secondary btn-sm" data-action="back-to-editor">Back to Editor</button>';
        }
        html += '</div>';
        html += '</div>';
        return html;
    }

    function renderSlidePanel() {
        const slides = AppState.getSlides();
        const ui = AppState.getUI();
        let html = '<div class="slide-panel">';
        html += '<div class="slide-panel-header">';
        html += '<span class="slide-panel-title">Slides (' + slides.length + ')</span>';
        html += '<button class="tool-btn tool-btn-sm" data-action="add-slide" title="Add Slide">+</button>';
        html += '</div>';
        html += '<div class="slide-panel-list" id="slideList">';
        slides.forEach(function(slide, idx) {
            html += Components.slideThumbnail(slide, slide.id === ui.currentSlideId, idx);
        });
        html += '</div>';
        html += '</div>';
        return html;
    }

    function renderCanvas() {
        const slide = AppState.getCurrentSlide();
        const ui = AppState.getUI();
        if (!slide) return '<div class="canvas-area"><div class="canvas-empty">No slide selected</div></div>';

        const theme = AppState.getCurrentTheme() || { bgColor: '#1a1a2e' };
        const bg = slide.backgroundColor || theme.bgColor;
        const zoom = ui.zoom / 100;

        let html = '<div class="canvas-area">';

        if (ui.showRulers) {
            html += '<div class="ruler ruler-horizontal"><div class="ruler-marks">';
            for (let i = 0; i <= 1920; i += 100) {
                html += '<span class="ruler-mark" style="left:' + (i * zoom * 0.13) + 'px">' + i + '</span>';
            }
            html += '</div></div>';
        }

        html += '<div class="canvas-wrapper" id="canvasWrapper">';
        html += '<div class="canvas-slide" id="canvasSlide" style="background:' + Components.escapeAttr(bg) + ';transform:scale(' + zoom + ')">';

        if (ui.showGrid) {
            html += '<div class="canvas-grid"></div>';
        }

        (slide.elements || []).forEach(function(el) {
            html += renderCanvasElement(el, slide.id);
        });

        html += '</div></div></div>';
        return html;
    }

    function renderCanvasElement(el, slideId) {
        if (!el.visible) return '';
        const ui = AppState.getUI();
        const isSelected = el.id === ui.selectedElementId;
        const lockedClass = el.locked ? ' locked' : '';

        let html = '<div class="canvas-element' + (isSelected ? ' selected' : '') + lockedClass + '" ';
        html += 'data-element-id="' + Components.escapeAttr(el.id) + '" ';
        html += 'data-slide-id="' + Components.escapeAttr(slideId) + '" ';
        html += 'style="left:' + el.x + 'px;top:' + el.y + 'px;width:' + el.width + 'px;height:' + el.height + 'px">';

        if (el.type === 'text') {
            const s = el.style || {};
            let textStyle = 'font-family:' + (s.fontFamily || 'Inter') + ';';
            textStyle += 'font-size:' + (s.fontSize || 16) + 'px;';
            textStyle += 'font-weight:' + (s.fontWeight || 'normal') + ';';
            textStyle += 'color:' + (s.color || '#ffffff') + ';';
            textStyle += 'text-align:' + (s.textAlign || 'left') + ';';
            if (s.italic) textStyle += 'font-style:italic;';
            if (s.underline) textStyle += 'text-decoration:underline;';
            const content = (el.content || '').replace(/\n/g, '<br>');
            html += '<div class="element-text" style="' + textStyle + '">' + Components.escapeHtml(el.content || '').replace(/\n/g, '<br>') + '</div>';
        } else if (el.type === 'shape') {
            const s = el.style || {};
            let shapeStyle = '';
            if (s.fill && s.fill !== 'none') shapeStyle += 'background:' + s.fill + ';';
            if (s.stroke && s.stroke !== 'none') shapeStyle += 'border:' + (s.strokeWidth || 1) + 'px solid ' + s.stroke + ';';
            if (s.opacity !== undefined) shapeStyle += 'opacity:' + s.opacity + ';';

            if (el.shapeType === 'circle') {
                shapeStyle += 'border-radius:50%;';
            } else if (el.shapeType === 'rounded-rectangle') {
                shapeStyle += 'border-radius:' + (s.cornerRadius || 8) + 'px;';
            } else if (el.shapeType === 'triangle') {
                shapeStyle = 'width:0;height:0;border-left:' + (el.width / 2) + 'px solid transparent;border-right:' + (el.width / 2) + 'px solid transparent;border-bottom:' + el.height + 'px solid ' + (s.fill || '#6366f1') + ';background:none;';
            } else if (el.shapeType === 'diamond') {
                shapeStyle += 'transform:rotate(45deg);';
            } else {
                shapeStyle += 'border-radius:' + (s.cornerRadius || 0) + 'px;';
            }

            html += '<div class="element-shape" style="' + shapeStyle + '"></div>';
        }

        if (isSelected) {
            html += '<div class="resize-handle resize-nw" data-resize="nw"></div>';
            html += '<div class="resize-handle resize-ne" data-resize="ne"></div>';
            html += '<div class="resize-handle resize-sw" data-resize="sw"></div>';
            html += '<div class="resize-handle resize-se" data-resize="se"></div>';
        }

        html += '</div>';
        return html;
    }

    function renderRightPanel() {
        const ui = AppState.getUI();
        if (ui.rightPanel === 'comments') return renderCommentsPanel();
        if (ui.rightPanel === 'transitions') return renderTransitionsPanel();
        if (ui.rightPanel === 'animations') return renderAnimationsPanel();
        return renderPropertiesPanel();
    }

    function renderPropertiesPanel() {
        const el = AppState.getSelectedElement();
        const slide = AppState.getCurrentSlide();
        const ui = AppState.getUI();

        let html = '<div class="right-panel">';
        html += '<div class="panel-tabs">';
        html += '<button class="panel-tab active" data-action="set-panel" data-panel="properties">Properties</button>';
        html += '<button class="panel-tab" data-action="set-panel" data-panel="transitions">Transitions</button>';
        html += '<button class="panel-tab" data-action="set-panel" data-panel="animations">Animations</button>';
        html += '</div>';

        if (el) {
            html += renderElementProperties(el);
        } else if (slide) {
            html += renderSlideProperties(slide);
        }

        html += '</div>';
        return html;
    }

    function renderElementProperties(el) {
        const s = el.style || {};
        let html = '<div class="panel-section">';
        html += '<div class="panel-section-header">';
        html += '<span class="panel-section-title">' + (el.type === 'text' ? 'Text' : 'Shape') + ' Properties</span>';
        html += '<div class="element-actions">';
        html += '<button class="tool-btn tool-btn-sm" data-action="toggle-lock" data-element-id="' + Components.escapeAttr(el.id) + '" title="' + (el.locked ? 'Unlock' : 'Lock') + '">' + (el.locked ? '&#128274;' : '&#128275;') + '</button>';
        html += '<button class="tool-btn tool-btn-sm" data-action="toggle-visibility" data-element-id="' + Components.escapeAttr(el.id) + '" title="' + (el.visible ? 'Hide' : 'Show') + '">' + (el.visible ? '&#128065;' : '&#128065;&#8211;') + '</button>';
        html += '<button class="tool-btn tool-btn-sm btn-danger-icon" data-action="delete-element" data-element-id="' + Components.escapeAttr(el.id) + '" title="Delete">&times;</button>';
        html += '</div></div>';

        // Position & Size
        html += '<div class="prop-group">';
        html += '<div class="prop-label">Position & Size</div>';
        html += '<div class="prop-row">';
        html += '<div class="prop-field"><label>X</label><input type="number" class="prop-input" id="prop-x" value="' + Math.round(el.x) + '" data-prop="x"></div>';
        html += '<div class="prop-field"><label>Y</label><input type="number" class="prop-input" id="prop-y" value="' + Math.round(el.y) + '" data-prop="y"></div>';
        html += '</div>';
        html += '<div class="prop-row">';
        html += '<div class="prop-field"><label>W</label><input type="number" class="prop-input" id="prop-width" value="' + Math.round(el.width) + '" data-prop="width"></div>';
        html += '<div class="prop-field"><label>H</label><input type="number" class="prop-input" id="prop-height" value="' + Math.round(el.height) + '" data-prop="height"></div>';
        html += '</div></div>';

        if (el.type === 'text') {
            html += renderTextProperties(el);
        } else if (el.type === 'shape') {
            html += renderShapeProperties(el);
        }

        // Layer order
        html += '<div class="prop-group">';
        html += '<div class="prop-label">Layer Order</div>';
        html += '<div class="prop-row layer-btns">';
        html += '<button class="tool-btn tool-btn-sm" data-action="reorder-element" data-direction="top" title="Bring to Front">\u21C8</button>';
        html += '<button class="tool-btn tool-btn-sm" data-action="reorder-element" data-direction="up" title="Bring Forward">\u2191</button>';
        html += '<button class="tool-btn tool-btn-sm" data-action="reorder-element" data-direction="down" title="Send Backward">\u2193</button>';
        html += '<button class="tool-btn tool-btn-sm" data-action="reorder-element" data-direction="bottom" title="Send to Back">\u21CA</button>';
        html += '</div></div>';

        html += '</div>';
        return html;
    }

    function renderTextProperties(el) {
        const s = el.style || {};
        let html = '<div class="prop-group">';
        html += '<div class="prop-label">Typography</div>';

        // Font family dropdown
        const fontOptions = AppState.getFontFamilies().map(function(f) { return { value: f, label: f }; });
        html += '<div class="prop-field-full">';
        html += Components.dropdown('prop-font-family', fontOptions, s.fontFamily || 'Inter', 'Font family');
        html += '</div>';

        // Font size, weight
        html += '<div class="prop-row">';
        html += '<div class="prop-field">';
        const sizeOptions = AppState.getFontSizes().map(function(sz) { return { value: String(sz), label: String(sz) }; });
        html += Components.dropdown('prop-font-size', sizeOptions, String(s.fontSize || 16), 'Size');
        html += '</div>';
        html += '<div class="prop-field">';
        const weightOptions = [
            { value: 'normal', label: 'Regular' },
            { value: 'bold', label: 'Bold' },
            { value: '100', label: 'Thin' },
            { value: '300', label: 'Light' },
            { value: '500', label: 'Medium' },
            { value: '600', label: 'Semibold' },
            { value: '800', label: 'Extra Bold' }
        ];
        html += Components.dropdown('prop-font-weight', weightOptions, s.fontWeight || 'normal', 'Weight');
        html += '</div></div>';

        // Style toggles
        html += '<div class="prop-row style-toggles">';
        html += '<button class="style-toggle' + (s.italic ? ' active' : '') + '" data-action="toggle-italic" title="Italic"><em>I</em></button>';
        html += '<button class="style-toggle' + (s.underline ? ' active' : '') + '" data-action="toggle-underline" title="Underline"><u>U</u></button>';
        html += '</div>';

        // Text alignment
        html += '<div class="prop-row alignment-btns">';
        html += '<button class="style-toggle' + (s.textAlign === 'left' ? ' active' : '') + '" data-action="set-align" data-value="left" title="Align Left">\u2261</button>';
        html += '<button class="style-toggle' + (s.textAlign === 'center' ? ' active' : '') + '" data-action="set-align" data-value="center" title="Center">\u2263</button>';
        html += '<button class="style-toggle' + (s.textAlign === 'right' ? ' active' : '') + '" data-action="set-align" data-value="right" title="Align Right">\u2262</button>';
        html += '</div>';

        // Text color
        html += '<div class="prop-label">Text Color</div>';
        html += '<div class="color-picker-inline">';
        html += '<div class="color-preview" style="background:' + Components.escapeAttr(s.color || '#ffffff') + '"></div>';
        html += '<input type="text" class="prop-input color-hex-input" id="prop-text-color" value="' + Components.escapeAttr(s.color || '#ffffff') + '" data-style-prop="color">';
        html += '</div>';
        html += '<div class="color-swatches">';
        AppState.getElementColors().forEach(function(c) {
            html += Components.colorSwatch(c, c === (s.color || '#ffffff'));
        });
        html += '</div>';

        // Content editing
        html += '<div class="prop-label">Content</div>';
        html += '<textarea class="prop-textarea" id="prop-content" rows="4">' + Components.escapeHtml(el.content || '') + '</textarea>';

        html += '</div>';
        return html;
    }

    function renderShapeProperties(el) {
        const s = el.style || {};
        let html = '<div class="prop-group">';
        html += '<div class="prop-label">Shape</div>';

        // Shape type
        const shapeOptions = AppState.getShapeTypes().map(function(t) {
            return { value: t, label: t.replace(/-/g, ' ').replace(/\b\w/g, function(c) { return c.toUpperCase(); }) };
        });
        html += '<div class="prop-field-full">';
        html += Components.dropdown('prop-shape-type', shapeOptions, el.shapeType || 'rectangle', 'Shape type');
        html += '</div>';

        // Fill color
        html += '<div class="prop-label">Fill</div>';
        html += '<div class="color-picker-inline">';
        html += '<div class="color-preview" style="background:' + Components.escapeAttr(s.fill || '#6366f1') + '"></div>';
        html += '<input type="text" class="prop-input color-hex-input" id="prop-fill-color" value="' + Components.escapeAttr(s.fill || '#6366f1') + '" data-style-prop="fill">';
        html += '</div>';
        html += '<div class="color-swatches">';
        AppState.getElementColors().forEach(function(c) {
            html += Components.colorSwatch(c, c === (s.fill || '#6366f1'));
        });
        html += '</div>';

        // Stroke
        html += '<div class="prop-label">Stroke</div>';
        html += '<div class="prop-row">';
        html += '<div class="prop-field">';
        html += '<input type="text" class="prop-input color-hex-input" id="prop-stroke-color" value="' + Components.escapeAttr(s.stroke || 'none') + '" data-style-prop="stroke">';
        html += '</div>';
        html += '<div class="prop-field">';
        html += '<label>Width</label><input type="number" class="prop-input" id="prop-stroke-width" value="' + (s.strokeWidth || 0) + '" min="0" max="20" data-style-prop="strokeWidth">';
        html += '</div></div>';

        // Corner radius
        html += '<div class="prop-row">';
        html += '<div class="prop-field"><label>Radius</label><input type="number" class="prop-input" id="prop-corner-radius" value="' + (s.cornerRadius || 0) + '" min="0" data-style-prop="cornerRadius"></div>';
        html += '<div class="prop-field"><label>Opacity</label><input type="number" class="prop-input" id="prop-opacity" value="' + (s.opacity !== undefined ? s.opacity : 1) + '" min="0" max="1" step="0.1" data-style-prop="opacity"></div>';
        html += '</div>';

        html += '</div>';
        return html;
    }

    function renderSlideProperties(slide) {
        let html = '<div class="panel-section">';
        html += '<div class="panel-section-header"><span class="panel-section-title">Slide Properties</span></div>';

        // Background color
        html += '<div class="prop-group">';
        html += '<div class="prop-label">Background Color</div>';
        html += '<div class="color-picker-inline">';
        html += '<div class="color-preview" style="background:' + Components.escapeAttr(slide.backgroundColor || '#1a1a2e') + '"></div>';
        html += '<input type="text" class="prop-input color-hex-input" id="prop-slide-bg" value="' + Components.escapeAttr(slide.backgroundColor || '#1a1a2e') + '" data-slide-prop="backgroundColor">';
        html += '</div>';
        html += '<div class="color-swatches">';
        AppState.getElementColors().forEach(function(c) {
            html += Components.colorSwatch(c, c === slide.backgroundColor);
        });
        html += '</div></div>';

        // Template type info
        html += '<div class="prop-group">';
        html += '<div class="prop-label">Template</div>';
        html += '<div class="prop-value">' + Components.escapeHtml(slide.templateType || 'blank') + '</div>';
        html += '<button class="btn btn-secondary btn-sm" data-action="open-templates" style="margin-top:8px">Change Template</button>';
        html += '</div>';

        // Elements list
        html += '<div class="prop-group">';
        html += '<div class="prop-label">Elements (' + (slide.elements || []).length + ')</div>';
        html += '<div class="elements-list">';
        (slide.elements || []).slice().reverse().forEach(function(el) {
            const icon = el.type === 'text' ? 'T' : (el.type === 'shape' ? '\u25A0' : '\u25C6');
            const name = el.type === 'text' ? (el.content || 'Text').substring(0, 25) : (el.shapeType || el.type);
            const cls = el.id === AppState.getUI().selectedElementId ? 'element-list-item active' : 'element-list-item';
            html += '<div class="' + cls + '" data-action="select-element" data-element-id="' + Components.escapeAttr(el.id) + '">';
            html += '<span class="el-icon">' + icon + '</span>';
            html += '<span class="el-name">' + Components.escapeHtml(name) + '</span>';
            if (!el.visible) html += '<span class="el-hidden-badge">hidden</span>';
            if (el.locked) html += '<span class="el-locked-badge">locked</span>';
            html += '</div>';
        });
        html += '</div></div>';

        // Slide actions
        html += '<div class="prop-group">';
        html += '<div class="prop-label">Slide Actions</div>';
        html += '<div class="slide-actions-list">';
        html += '<button class="btn btn-secondary btn-sm btn-full" data-action="duplicate-slide" data-slide-id="' + Components.escapeAttr(slide.id) + '">Duplicate Slide</button>';
        html += '<button class="btn btn-secondary btn-sm btn-full" data-action="save-as-template" data-slide-id="' + Components.escapeAttr(slide.id) + '">Save as Template</button>';
        if (AppState.getSlides().length > 1) {
            html += '<button class="btn btn-danger btn-sm btn-full" data-action="delete-slide" data-slide-id="' + Components.escapeAttr(slide.id) + '">Delete Slide</button>';
        }
        html += '</div></div>';

        html += '</div>';
        return html;
    }

    function renderTransitionsPanel() {
        const slide = AppState.getCurrentSlide();
        const pres = AppState.getPresentation();
        let html = '<div class="right-panel">';
        html += '<div class="panel-tabs">';
        html += '<button class="panel-tab" data-action="set-panel" data-panel="properties">Properties</button>';
        html += '<button class="panel-tab active" data-action="set-panel" data-panel="transitions">Transitions</button>';
        html += '<button class="panel-tab" data-action="set-panel" data-panel="animations">Animations</button>';
        html += '</div>';

        if (slide) {
            const tr = slide.transition || { type: 'none', duration: 0 };
            html += '<div class="panel-section">';
            html += '<div class="panel-section-header"><span class="panel-section-title">Slide Transition</span></div>';

            html += '<div class="prop-group">';
            html += '<div class="prop-label">Transition Type</div>';
            const trOptions = AppState.getTransitionTypes().map(function(t) {
                return { value: t, label: t.replace(/-/g, ' ').replace(/\b\w/g, function(c) { return c.toUpperCase(); }) };
            });
            html += Components.dropdown('prop-transition-type', trOptions, tr.type || 'none', 'None');
            html += '</div>';

            html += '<div class="prop-group">';
            html += '<div class="prop-label">Duration (ms)</div>';
            html += '<input type="number" class="prop-input" id="prop-transition-duration" value="' + (tr.duration || 0) + '" min="0" max="5000" step="100">';
            html += '</div>';

            html += '<div class="prop-group">';
            html += '<div class="prop-label">Default Transition</div>';
            const defTr = pres.defaultTransition || { type: 'none', duration: 0 };
            html += Components.dropdown('prop-default-transition-type', trOptions, defTr.type || 'none', 'None');
            html += '<div style="margin-top:8px">';
            html += '<div class="prop-label">Default Duration (ms)</div>';
            html += '<input type="number" class="prop-input" id="prop-default-transition-duration" value="' + (defTr.duration || 0) + '" min="0" max="5000" step="100">';
            html += '</div></div>';

            html += '<button class="btn btn-secondary btn-sm btn-full" data-action="apply-default-transition" style="margin-top:8px">Apply Default to This Slide</button>';

            html += '</div>';
        }

        html += '</div>';
        return html;
    }

    function renderAnimationsPanel() {
        const slide = AppState.getCurrentSlide();
        const el = AppState.getSelectedElement();

        let html = '<div class="right-panel">';
        html += '<div class="panel-tabs">';
        html += '<button class="panel-tab" data-action="set-panel" data-panel="properties">Properties</button>';
        html += '<button class="panel-tab" data-action="set-panel" data-panel="transitions">Transitions</button>';
        html += '<button class="panel-tab active" data-action="set-panel" data-panel="animations">Animations</button>';
        html += '</div>';

        if (el) {
            const anim = el.animation || { type: 'none', duration: 0, delay: 0, order: 0 };
            html += '<div class="panel-section">';
            html += '<div class="panel-section-header"><span class="panel-section-title">Element Animation</span></div>';
            html += '<div class="prop-info">Selected: ' + Components.escapeHtml(el.type === 'text' ? (el.content || 'Text').substring(0, 20) : el.shapeType || el.type) + '</div>';

            html += '<div class="prop-group">';
            html += '<div class="prop-label">Animation Type</div>';
            const animOptions = AppState.getAnimationTypes().map(function(t) {
                return { value: t, label: t.replace(/-/g, ' ').replace(/\b\w/g, function(c) { return c.toUpperCase(); }) };
            });
            html += Components.dropdown('prop-animation-type', animOptions, anim.type || 'none', 'None');
            html += '</div>';

            html += '<div class="prop-group">';
            html += '<div class="prop-label">Duration (ms)</div>';
            html += '<input type="number" class="prop-input" id="prop-animation-duration" value="' + (anim.duration || 0) + '" min="0" max="5000" step="100">';
            html += '</div>';

            html += '<div class="prop-group">';
            html += '<div class="prop-label">Delay (ms)</div>';
            html += '<input type="number" class="prop-input" id="prop-animation-delay" value="' + (anim.delay || 0) + '" min="0" max="10000" step="100">';
            html += '</div>';

            html += '<div class="prop-group">';
            html += '<div class="prop-label">Order</div>';
            html += '<input type="number" class="prop-input" id="prop-animation-order" value="' + (anim.order || 0) + '" min="0" max="99">';
            html += '</div>';

            html += '</div>';
        } else if (slide) {
            html += '<div class="panel-section">';
            html += '<div class="panel-empty-state">Select an element to configure its animation.</div>';

            // Show animation summary for all elements
            html += '<div class="prop-group">';
            html += '<div class="prop-label">Animation Order</div>';
            const animated = (slide.elements || []).filter(function(e) { return e.animation && e.animation.type !== 'none'; });
            animated.sort(function(a, b) { return (a.animation.order || 0) - (b.animation.order || 0); });
            if (animated.length === 0) {
                html += '<div class="prop-info">No animations configured</div>';
            } else {
                html += '<div class="animation-order-list">';
                animated.forEach(function(e) {
                    const name = e.type === 'text' ? (e.content || 'Text').substring(0, 20) : e.shapeType || e.type;
                    html += '<div class="anim-order-item" data-action="select-element" data-element-id="' + Components.escapeAttr(e.id) + '">';
                    html += '<span class="anim-order-num">' + (e.animation.order || 0) + '</span>';
                    html += '<span class="anim-order-name">' + Components.escapeHtml(name) + '</span>';
                    html += '<span class="anim-order-type">' + Components.escapeHtml(e.animation.type) + '</span>';
                    html += '</div>';
                });
                html += '</div>';
            }
            html += '</div></div>';
        }

        html += '</div>';
        return html;
    }

    function renderCommentsPanel() {
        const ui = AppState.getUI();
        const comments = AppState.getFilteredComments();
        const currentSlide = AppState.getCurrentSlide();

        let html = '<div class="right-panel comments-panel">';
        html += '<div class="panel-tabs">';
        html += '<button class="panel-tab" data-action="set-panel" data-panel="properties">Properties</button>';
        html += '<button class="panel-tab active" data-action="set-panel" data-panel="comments">Comments</button>';
        html += '</div>';

        html += '<div class="panel-section">';
        // Filter
        html += '<div class="comments-filter">';
        html += '<button class="filter-btn' + (ui.filterResolved === 'all' ? ' active' : '') + '" data-action="filter-comments" data-value="all">All</button>';
        html += '<button class="filter-btn' + (ui.filterResolved === 'open' ? ' active' : '') + '" data-action="filter-comments" data-value="open">Open</button>';
        html += '<button class="filter-btn' + (ui.filterResolved === 'resolved' ? ' active' : '') + '" data-action="filter-comments" data-value="resolved">Resolved</button>';
        html += '</div>';

        // Add comment
        html += '<div class="add-comment-form">';
        html += '<textarea class="comment-textarea" id="newCommentText" placeholder="Add a comment..." rows="2"></textarea>';
        html += '<button class="btn btn-primary btn-sm" data-action="add-comment">Post</button>';
        html += '</div>';

        // Comments list
        html += '<div class="comments-list">';
        if (comments.length === 0) {
            html += '<div class="panel-empty-state">No comments found.</div>';
        }
        comments.forEach(function(cmt) {
            const author = AppState.getUserById(cmt.author);
            const slide = AppState.getSlideById(cmt.slideId);
            const slideIdx = slide ? AppState.getSlides().indexOf(slide) + 1 : '?';
            html += '<div class="comment-item' + (cmt.resolved ? ' resolved' : '') + '" data-comment-id="' + Components.escapeAttr(cmt.id) + '">';
            html += '<div class="comment-header">';
            html += Components.avatar(author, 24);
            html += '<span class="comment-author">' + Components.escapeHtml(author ? author.name : 'Unknown') + '</span>';
            html += '<span class="comment-time">' + Components.timeAgo(cmt.createdAt) + '</span>';
            html += '<span class="comment-slide-badge" data-action="goto-comment-slide" data-slide-id="' + Components.escapeAttr(cmt.slideId) + '">Slide ' + slideIdx + '</span>';
            html += '</div>';
            html += '<div class="comment-text">' + Components.escapeHtml(cmt.text) + '</div>';
            html += '<div class="comment-actions">';
            html += '<button class="comment-action-btn" data-action="resolve-comment" data-comment-id="' + Components.escapeAttr(cmt.id) + '">' + (cmt.resolved ? 'Reopen' : 'Resolve') + '</button>';
            html += '<button class="comment-action-btn" data-action="delete-comment" data-comment-id="' + Components.escapeAttr(cmt.id) + '">Delete</button>';
            html += '</div>';

            // Replies
            if (cmt.replies && cmt.replies.length > 0) {
                html += '<div class="comment-replies">';
                cmt.replies.forEach(function(reply) {
                    const replyAuthor = AppState.getUserById(reply.author);
                    html += '<div class="reply-item">';
                    html += '<div class="comment-header">';
                    html += Components.avatar(replyAuthor, 20);
                    html += '<span class="comment-author">' + Components.escapeHtml(replyAuthor ? replyAuthor.name : 'Unknown') + '</span>';
                    html += '<span class="comment-time">' + Components.timeAgo(reply.createdAt) + '</span>';
                    html += '</div>';
                    html += '<div class="comment-text">' + Components.escapeHtml(reply.text) + '</div>';
                    html += '<div class="comment-actions">';
                    html += '<button class="comment-action-btn" data-action="delete-reply" data-comment-id="' + Components.escapeAttr(cmt.id) + '" data-reply-id="' + Components.escapeAttr(reply.id) + '">Delete</button>';
                    html += '</div>';
                    html += '</div>';
                });
                html += '</div>';
            }

            // Reply form
            html += '<div class="reply-form">';
            html += '<input type="text" class="reply-input" placeholder="Reply..." data-comment-id="' + Components.escapeAttr(cmt.id) + '">';
            html += '</div>';

            html += '</div>';
        });
        html += '</div></div></div>';
        return html;
    }

    function renderSpeakerNotesBar() {
        const slide = AppState.getCurrentSlide();
        const ui = AppState.getUI();
        if (!ui.showSpeakerNotes) return '';

        let html = '<div class="speaker-notes-bar">';
        html += '<div class="notes-header">';
        html += '<span class="notes-title">Speaker Notes</span>';
        html += '<button class="tool-btn tool-btn-sm" data-action="toggle-notes" title="Toggle Notes">&#8722;</button>';
        html += '</div>';
        if (slide) {
            html += '<textarea class="notes-textarea" id="speakerNotesInput" placeholder="Add speaker notes..." rows="3">' + Components.escapeHtml(slide.speakerNotes || '') + '</textarea>';
        }
        html += '</div>';
        return html;
    }

    function renderEditorView() {
        let html = '<div class="editor-layout">';
        html += renderSlidePanel();
        html += '<div class="editor-main">';
        html += renderCanvas();
        html += renderSpeakerNotesBar();
        html += '</div>';
        html += renderRightPanel();
        html += '</div>';
        return html;
    }

    function renderPresenterView() {
        const slides = AppState.getSlides();
        const ui = AppState.getUI();
        const idx = ui.presenterSlideIndex;
        const currentSlide = slides[idx];
        const nextSlide = slides[idx + 1];

        if (!currentSlide) return '<div class="presenter-view"><div class="presenter-empty">No slides</div></div>';

        let html = '<div class="presenter-view">';

        // Main slide display
        html += '<div class="presenter-main">';
        html += '<div class="presenter-slide" style="background:' + Components.escapeAttr(currentSlide.backgroundColor || '#1a1a2e') + '">';
        (currentSlide.elements || []).forEach(function(el) {
            if (!el.visible) return;
            html += renderPresenterElement(el);
        });
        html += '</div></div>';

        // Sidebar with notes and next slide preview
        html += '<div class="presenter-sidebar">';

        // Next slide preview
        html += '<div class="presenter-next">';
        html += '<div class="presenter-next-label">Next Slide</div>';
        if (nextSlide) {
            html += '<div class="presenter-next-preview" style="background:' + Components.escapeAttr(nextSlide.backgroundColor || '#1a1a2e') + '">';
            (nextSlide.elements || []).filter(function(e) { return e.visible; }).forEach(function(el) {
                html += renderPresenterElement(el, 0.25);
            });
            html += '</div>';
        } else {
            html += '<div class="presenter-next-preview presenter-end">End of Presentation</div>';
        }
        html += '</div>';

        // Speaker notes
        html += '<div class="presenter-notes">';
        html += '<div class="presenter-notes-label">Speaker Notes</div>';
        html += '<div class="presenter-notes-content">' + Components.escapeHtml(currentSlide.speakerNotes || 'No notes for this slide.').replace(/\n/g, '<br>') + '</div>';
        html += '</div>';

        // Controls
        html += '<div class="presenter-controls">';
        html += '<button class="presenter-btn" data-action="presenter-prev" ' + (idx === 0 ? 'disabled' : '') + '>&larr; Previous</button>';
        html += '<span class="presenter-counter">' + (idx + 1) + ' / ' + slides.length + '</span>';
        html += '<button class="presenter-btn" data-action="presenter-next" ' + (idx >= slides.length - 1 ? 'disabled' : '') + '>Next &rarr;</button>';
        html += '</div>';

        html += '</div></div>';
        return html;
    }

    function renderPresenterElement(el, scale) {
        scale = scale || 0.5;
        const s = el.style || {};
        let style = 'left:' + (el.x * scale) + 'px;top:' + (el.y * scale) + 'px;width:' + (el.width * scale) + 'px;height:' + (el.height * scale) + 'px;position:absolute;';

        if (el.type === 'text') {
            style += 'font-family:' + (s.fontFamily || 'Inter') + ';';
            style += 'font-size:' + ((s.fontSize || 16) * scale) + 'px;';
            style += 'font-weight:' + (s.fontWeight || 'normal') + ';';
            style += 'color:' + (s.color || '#ffffff') + ';';
            style += 'text-align:' + (s.textAlign || 'left') + ';';
            if (s.italic) style += 'font-style:italic;';
            if (s.underline) style += 'text-decoration:underline;';
            style += 'overflow:hidden;line-height:1.3;';
            return '<div style="' + style + '">' + Components.escapeHtml(el.content || '').replace(/\n/g, '<br>') + '</div>';
        } else if (el.type === 'shape') {
            if (s.fill && s.fill !== 'none') style += 'background:' + s.fill + ';';
            if (s.stroke && s.stroke !== 'none') style += 'border:' + Math.max(1, (s.strokeWidth || 0) * scale) + 'px solid ' + s.stroke + ';';
            if (s.opacity !== undefined) style += 'opacity:' + s.opacity + ';';
            if (el.shapeType === 'circle') style += 'border-radius:50%;';
            else if (el.shapeType === 'rounded-rectangle') style += 'border-radius:' + ((s.cornerRadius || 8) * scale) + 'px;';
            else style += 'border-radius:' + ((s.cornerRadius || 0) * scale) + 'px;';
            return '<div style="' + style + '"></div>';
        }
        return '';
    }

    function renderTemplatesView() {
        const templates = AppState.getTemplates();
        const currentSlide = AppState.getCurrentSlide();
        const theme = AppState.getCurrentTheme() || { bgColor: '#1a1a2e' };

        let html = '<div class="templates-view">';
        html += '<div class="templates-header">';
        html += '<h2>Slide Templates</h2>';
        html += '<button class="btn btn-secondary btn-sm" data-action="back-to-editor">Close</button>';
        html += '</div>';

        if (currentSlide) {
            html += '<div class="templates-hint">Click a template to apply it to the current slide (Slide ' + (AppState.getSlides().indexOf(currentSlide) + 1) + ')</div>';
        }

        html += '<div class="templates-grid">';
        templates.forEach(function(tmpl) {
            html += '<div class="template-card" data-action="apply-template" data-template-id="' + Components.escapeAttr(tmpl.id) + '">';
            html += '<div class="template-preview" style="background:' + Components.escapeAttr(theme.bgColor) + '">';
            (tmpl.elements || []).forEach(function(el) {
                html += renderPresenterElement(el, 0.12);
            });
            html += '</div>';
            html += '<div class="template-info">';
            html += '<div class="template-name">' + Components.escapeHtml(tmpl.name) + '</div>';
            html += '<div class="template-desc">' + Components.escapeHtml(tmpl.description || '') + '</div>';
            if (tmpl.id.startsWith('tmpl_custom_')) {
                html += '<button class="btn btn-danger btn-sm" data-action="delete-template" data-template-id="' + Components.escapeAttr(tmpl.id) + '" style="margin-top:4px">Delete</button>';
            }
            html += '</div></div>';
        });
        html += '</div></div>';
        return html;
    }

    function renderExportView() {
        const pres = AppState.getPresentation();

        let html = '<div class="export-view">';
        html += '<div class="export-header">';
        html += '<h2>Export & Share</h2>';
        html += '<button class="btn btn-secondary btn-sm" data-action="back-to-editor">Close</button>';
        html += '</div>';

        html += '<div class="export-sections">';

        // Export section
        html += '<div class="export-section">';
        html += '<h3>Export</h3>';
        html += '<div class="export-options">';
        const formatOptions = [
            { value: 'pdf', label: 'PDF Document' },
            { value: 'png', label: 'PNG Images' },
            { value: 'svg', label: 'SVG Vector' },
            { value: 'pptx', label: 'PowerPoint' }
        ];
        html += '<div class="prop-label">Format</div>';
        html += Components.dropdown('export-format', formatOptions, pres.exportFormat || 'pdf', 'Select format');
        html += '<button class="btn btn-primary btn-full" data-action="export-presentation" style="margin-top:12px">Export Presentation</button>';
        html += '</div></div>';

        // Share section
        html += '<div class="export-section">';
        html += '<h3>Share</h3>';
        html += '<div class="share-options">';
        html += '<div class="prop-label">Share Link</div>';
        html += '<div class="share-link-row">';
        html += '<input type="text" class="text-input" id="shareLink" value="' + Components.escapeAttr(pres.shareLink || '') + '" readonly>';
        html += '<button class="btn btn-secondary btn-sm" data-action="copy-share-link" title="Copy">Copy</button>';
        html += '</div>';

        html += '<div class="prop-label" style="margin-top:12px">Permission</div>';
        const permOptions = [
            { value: 'view', label: 'Can View' },
            { value: 'comment', label: 'Can Comment' },
            { value: 'edit', label: 'Can Edit' }
        ];
        html += Components.dropdown('share-permission', permOptions, pres.sharePermission || 'view', 'Permission');

        html += '<div style="margin-top:12px">';
        html += Components.toggle('embed-enabled', pres.embedEnabled || false, 'Enable embed link');
        html += '</div>';
        html += '</div></div>';

        // Presentation settings
        html += '<div class="export-section">';
        html += '<h3>Presentation Settings</h3>';
        html += '<div class="pres-settings">';
        html += Components.toggle('show-slide-numbers', pres.showSlideNumbers || false, 'Show slide numbers');
        html += Components.toggle('loop-presentation', pres.loopPresentation || false, 'Loop presentation');
        html += Components.toggle('auto-advance', pres.autoAdvance || false, 'Auto-advance slides');
        html += '<div class="prop-label" style="margin-top:8px">Auto-advance interval (ms)</div>';
        html += '<input type="number" class="prop-input" id="auto-advance-interval" value="' + (pres.autoAdvanceInterval || 5000) + '" min="1000" max="60000" step="1000">';
        html += '</div></div>';

        // Theme
        html += '<div class="export-section">';
        html += '<h3>Theme</h3>';
        html += '<div class="theme-grid">';
        AppState.getThemes().forEach(function(theme) {
            const isActive = theme.id === pres.themeId;
            html += '<div class="theme-card' + (isActive ? ' active' : '') + '" data-action="set-theme" data-theme-id="' + Components.escapeAttr(theme.id) + '">';
            html += '<div class="theme-preview" style="background:' + Components.escapeAttr(theme.bgColor) + '">';
            html += '<span style="color:' + Components.escapeAttr(theme.textColor) + ';font-size:11px">Aa</span>';
            html += '<span class="theme-accent" style="background:' + Components.escapeAttr(theme.accentColor) + '"></span>';
            html += '</div>';
            html += '<div class="theme-name">' + Components.escapeHtml(theme.name) + '</div>';
            html += '</div>';
        });
        html += '</div></div>';

        // Collaborators
        html += '<div class="export-section">';
        html += '<h3>Collaborators</h3>';
        html += '<div class="collaborators-list">';
        AppState.getUsers().forEach(function(user) {
            const isOwner = user.id === pres.owner;
            const isCollab = (pres.collaborators || []).includes(user.id);
            html += '<div class="collaborator-item">';
            html += Components.avatar(user, 28);
            html += '<div class="collab-info">';
            html += '<span class="collab-name">' + Components.escapeHtml(user.name) + '</span>';
            html += '<span class="collab-role">' + (isOwner ? 'Owner' : user.role) + '</span>';
            html += '</div>';
            if (!isOwner) {
                html += '<button class="btn btn-secondary btn-sm" data-action="toggle-collaborator" data-user-id="' + Components.escapeAttr(user.id) + '">' + (isCollab ? 'Remove' : 'Add') + '</button>';
            }
            html += '</div>';
        });
        html += '</div></div>';

        html += '</div></div>';
        return html;
    }

    function renderSettingsView() {
        const pres = AppState.getPresentation();

        let html = '<div class="settings-view">';
        html += '<div class="settings-header">';
        html += '<h2>Presentation Settings</h2>';
        html += '<button class="btn btn-secondary btn-sm" data-action="back-to-editor">Close</button>';
        html += '</div>';

        html += '<div class="settings-form">';

        html += '<div class="prop-group">';
        html += Components.textInput('settings-title', pres.title, 'Presentation title', 'Title');
        html += '</div>';

        html += '<div class="prop-group">';
        html += '<div class="prop-label">Slide Dimensions</div>';
        html += '<div class="prop-row">';
        html += '<div class="prop-field"><label>Width</label><input type="number" class="prop-input" id="settings-width" value="' + (pres.slideWidth || 1920) + '" min="640" max="3840"></div>';
        html += '<div class="prop-field"><label>Height</label><input type="number" class="prop-input" id="settings-height" value="' + (pres.slideHeight || 1080) + '" min="480" max="2160"></div>';
        html += '</div></div>';

        html += '<div class="prop-group">';
        html += '<div class="prop-label">Default Transition</div>';
        const trOptions = AppState.getTransitionTypes().map(function(t) {
            return { value: t, label: t.replace(/-/g, ' ').replace(/\b\w/g, function(c) { return c.toUpperCase(); }) };
        });
        html += Components.dropdown('settings-default-transition', trOptions, (pres.defaultTransition || {}).type || 'none', 'None');
        html += '<div style="margin-top:8px">';
        html += '<div class="prop-label">Duration (ms)</div>';
        html += '<input type="number" class="prop-input" id="settings-default-duration" value="' + ((pres.defaultTransition || {}).duration || 0) + '" min="0" max="5000" step="100">';
        html += '</div></div>';

        html += '<button class="btn btn-primary" data-action="save-settings" style="margin-top:16px">Save Settings</button>';

        html += '</div></div>';
        return html;
    }

    function renderContent() {
        const ui = AppState.getUI();
        switch (ui.currentView) {
            case 'presenter': return renderPresenterView();
            case 'templates': return renderTemplatesView();
            case 'export': return renderExportView();
            case 'settings': return renderSettingsView();
            default: return renderEditorView();
        }
    }

    return {
        renderToolbar, renderContent, renderSlidePanel, renderCanvas,
        renderRightPanel, renderSpeakerNotesBar, renderEditorView,
        renderPresenterView, renderTemplatesView, renderExportView,
        renderSettingsView, renderCommentsPanel
    };
})();
