const App = (function() {
    let _dragSlideId = null;
    let _dragOverSlideId = null;
    let _elementDrag = null;
    let _debounceTimer = null;

    function init() {
        AppState.init();
        _setupSSE();
        AppState.subscribe(render);
        _setupEventListeners();
        render();
    }

    function _setupSSE() {
        try {
            const es = new EventSource('/api/events');
            es.onmessage = function(e) {
                if (e.data === 'reset') {
                    AppState.resetToSeedData();
                }
            };
            es.onerror = function() {
                setTimeout(_setupSSE, 5000);
                es.close();
            };
        } catch (e) {}
    }

    function render() {
        const toolbarEl = document.getElementById('toolbar');
        const contentEl = document.getElementById('content');
        if (toolbarEl) toolbarEl.innerHTML = Views.renderToolbar();
        if (contentEl) contentEl.innerHTML = Views.renderContent();
    }

    function _setupEventListeners() {
        document.addEventListener('click', _handleClick);
        document.addEventListener('input', _handleInput);
        document.addEventListener('change', _handleChange);
        document.addEventListener('keydown', _handleKeydown);
        document.addEventListener('mousedown', _handleMouseDown);
        document.addEventListener('dblclick', _handleDblClick);

        // Slide filmstrip drag
        document.addEventListener('dragstart', _handleSlideDragStart);
        document.addEventListener('dragover', _handleSlideDragOver);
        document.addEventListener('dragleave', _handleSlideDragLeave);
        document.addEventListener('drop', _handleSlideDrop);
        document.addEventListener('dragend', _handleSlideDragEnd);
    }

    function _handleClick(e) {
        const target = e.target;

        // Close dropdowns on outside click
        if (!target.closest('.custom-dropdown')) {
            document.querySelectorAll('.dropdown-menu.open').forEach(function(m) {
                m.classList.remove('open');
            });
        }

        // Dropdown trigger
        const ddTrigger = target.closest('[data-dropdown-trigger]');
        if (ddTrigger) {
            e.stopPropagation();
            const ddId = ddTrigger.getAttribute('data-dropdown-trigger');
            _toggleDropdown(ddId);
            return;
        }

        // Dropdown item
        const ddItem = target.closest('[data-dropdown-item]');
        if (ddItem) {
            e.stopPropagation();
            _handleDropdownSelect(ddItem);
            return;
        }

        // Color swatch
        const swatch = target.closest('[data-color]');
        if (swatch && swatch.classList.contains('color-swatch')) {
            _handleColorSwatchClick(swatch);
            return;
        }

        // Action buttons
        const actionEl = target.closest('[data-action]');
        if (actionEl) {
            e.preventDefault();
            _handleAction(actionEl.getAttribute('data-action'), actionEl);
            return;
        }

        // Slide thumbnail click
        const slideThumb = target.closest('.slide-thumbnail');
        if (slideThumb && !target.closest('[data-action]')) {
            const slideId = slideThumb.getAttribute('data-slide-id');
            AppState.setCurrentSlide(slideId);
            return;
        }

        // Canvas element click
        const canvasEl = target.closest('.canvas-element');
        if (canvasEl) {
            e.stopPropagation();
            const elId = canvasEl.getAttribute('data-element-id');
            AppState.setSelectedElement(elId);
            return;
        }

        // Click on canvas background (deselect)
        if (target.closest('.canvas-slide') && !target.closest('.canvas-element')) {
            AppState.setSelectedElement(null);
            return;
        }

        // Modal overlay click
        if (target.id === 'modalOverlay') {
            Components.closeModal();
            return;
        }
    }

    function _handleAction(action, el) {
        const ui = AppState.getUI();
        const slideId = ui.currentSlideId;

        switch (action) {
            // Toolbar actions
            case 'add-text': {
                AppState.addElement(slideId, {
                    type: 'text',
                    x: 400, y: 300, width: 400, height: 60,
                    content: 'New text block',
                    style: { fontFamily: 'Inter', fontSize: 24, fontWeight: 'normal', color: '#ffffff', textAlign: 'left', italic: false, underline: false }
                });
                Components.showToast('Text element added');
                break;
            }
            case 'add-shape': {
                AppState.addElement(slideId, {
                    type: 'shape',
                    x: 600, y: 350, width: 200, height: 200,
                    shapeType: 'rectangle',
                    style: { fill: '#6366f1', stroke: '#334155', strokeWidth: 1, cornerRadius: 0, opacity: 1 }
                });
                Components.showToast('Shape added');
                break;
            }
            case 'toggle-grid':
                AppState.setUI('showGrid', !ui.showGrid);
                break;
            case 'toggle-rulers':
                AppState.setUI('showRulers', !ui.showRulers);
                break;
            case 'zoom-in':
                AppState.setUI('zoom', Math.min(200, ui.zoom + 10));
                break;
            case 'zoom-out':
                AppState.setUI('zoom', Math.max(25, ui.zoom - 10));
                break;

            // Navigation actions
            case 'present':
                AppState.setUI('currentView', 'presenter');
                AppState.setUI('presenterSlideIndex', AppState.getSlides().findIndex(function(s) { return s.id === slideId; }) || 0);
                break;
            case 'back-to-editor':
                AppState.setUI('currentView', 'editor');
                break;
            case 'open-templates':
                AppState.setUI('currentView', 'templates');
                break;
            case 'open-export':
                AppState.setUI('currentView', 'export');
                break;
            case 'open-settings':
                AppState.setUI('currentView', 'settings');
                break;
            case 'open-comments':
                if (ui.rightPanel === 'comments') {
                    AppState.setUI('rightPanel', 'properties');
                } else {
                    AppState.setUI('rightPanel', 'comments');
                }
                break;

            // Panel tabs
            case 'set-panel':
                AppState.setUI('rightPanel', el.getAttribute('data-panel'));
                break;

            // Slide actions
            case 'add-slide':
                AppState.addSlide(null, slideId);
                Components.showToast('Slide added');
                break;
            case 'duplicate-slide': {
                const dupId = el.getAttribute('data-slide-id') || slideId;
                AppState.duplicateSlide(dupId);
                Components.showToast('Slide duplicated');
                break;
            }
            case 'delete-slide': {
                const delId = el.getAttribute('data-slide-id') || slideId;
                Components.confirmDanger('Delete this slide? This cannot be undone.', function() {
                    AppState.deleteSlide(delId);
                    Components.showToast('Slide deleted');
                });
                break;
            }
            case 'save-as-template': {
                const tmplSlideId = el.getAttribute('data-slide-id') || slideId;
                Components.showModal('Save as Template',
                    '<div class="prop-group">' + Components.textInput('template-name', '', 'Template name', 'Name') + '</div>',
                    '<button class="btn btn-secondary" data-action="close-modal">Cancel</button> <button class="btn btn-primary" id="saveTemplateBtn">Save</button>'
                );
                setTimeout(function() {
                    var btn = document.getElementById('saveTemplateBtn');
                    if (btn) {
                        btn.addEventListener('click', function() {
                            var nameInput = document.getElementById('template-name');
                            var name = nameInput ? nameInput.value.trim() : '';
                            if (!name) { Components.showToast('Name is required'); return; }
                            AppState.saveAsTemplate(tmplSlideId, name);
                            Components.closeModal();
                            Components.showToast('Template saved');
                        });
                    }
                }, 50);
                break;
            }

            // Template actions
            case 'apply-template': {
                const tmplId = el.getAttribute('data-template-id');
                if (slideId && tmplId) {
                    Components.confirm('Apply this template? Current slide content will be replaced.', function() {
                        AppState.applyTemplate(slideId, tmplId);
                        AppState.setUI('currentView', 'editor');
                        Components.showToast('Template applied');
                    });
                }
                break;
            }
            case 'delete-template': {
                const delTmplId = el.getAttribute('data-template-id');
                Components.confirmDanger('Delete this custom template?', function() {
                    AppState.deleteTemplate(delTmplId);
                    Components.showToast('Template deleted');
                });
                break;
            }

            // Element actions
            case 'select-element': {
                const elId = el.getAttribute('data-element-id');
                AppState.setSelectedElement(elId);
                break;
            }
            case 'delete-element': {
                const delElId = el.getAttribute('data-element-id');
                Components.confirmDanger('Delete this element?', function() {
                    AppState.deleteElement(slideId, delElId);
                    Components.showToast('Element deleted');
                });
                break;
            }
            case 'toggle-lock': {
                const lockElId = el.getAttribute('data-element-id');
                AppState.toggleElementLock(slideId, lockElId);
                break;
            }
            case 'toggle-visibility': {
                const visElId = el.getAttribute('data-element-id');
                AppState.toggleElementVisibility(slideId, visElId);
                break;
            }
            case 'reorder-element': {
                const direction = el.getAttribute('data-direction');
                const selEl = AppState.getUI().selectedElementId;
                if (selEl) AppState.reorderElement(slideId, selEl, direction);
                break;
            }

            // Text style actions
            case 'toggle-italic': {
                const sel = AppState.getSelectedElement();
                if (sel && sel.type === 'text') {
                    AppState.updateElement(slideId, sel.id, { style: { italic: !sel.style.italic } });
                }
                break;
            }
            case 'toggle-underline': {
                const sel2 = AppState.getSelectedElement();
                if (sel2 && sel2.type === 'text') {
                    AppState.updateElement(slideId, sel2.id, { style: { underline: !sel2.style.underline } });
                }
                break;
            }
            case 'set-align': {
                const align = el.getAttribute('data-value');
                const sel3 = AppState.getSelectedElement();
                if (sel3 && sel3.type === 'text') {
                    AppState.updateElement(slideId, sel3.id, { style: { textAlign: align } });
                }
                break;
            }

            // Comment actions
            case 'add-comment': {
                const textEl = document.getElementById('newCommentText');
                const text = textEl ? textEl.value.trim() : '';
                if (!text) { Components.showToast('Comment text required'); return; }
                AppState.addComment(slideId, null, text);
                Components.showToast('Comment added');
                break;
            }
            case 'resolve-comment': {
                const cmtId = el.getAttribute('data-comment-id');
                AppState.resolveComment(cmtId);
                break;
            }
            case 'delete-comment': {
                const delCmtId = el.getAttribute('data-comment-id');
                Components.confirmDanger('Delete this comment and all its replies?', function() {
                    AppState.deleteComment(delCmtId);
                    Components.showToast('Comment deleted');
                });
                break;
            }
            case 'delete-reply': {
                const replyCmtId = el.getAttribute('data-comment-id');
                const replyId = el.getAttribute('data-reply-id');
                AppState.deleteReply(replyCmtId, replyId);
                break;
            }
            case 'filter-comments': {
                const filter = el.getAttribute('data-value');
                AppState.setUI('filterResolved', filter);
                break;
            }
            case 'goto-comment-slide': {
                const gotoSlideId = el.getAttribute('data-slide-id');
                AppState.setCurrentSlide(gotoSlideId);
                break;
            }

            // Transition actions
            case 'apply-default-transition': {
                const pres = AppState.getPresentation();
                const defTr = pres.defaultTransition || { type: 'none', duration: 0 };
                AppState.updateSlide(slideId, { transition: JSON.parse(JSON.stringify(defTr)) });
                Components.showToast('Default transition applied');
                break;
            }

            // Presenter actions
            case 'presenter-prev':
                if (ui.presenterSlideIndex > 0) {
                    AppState.setUI('presenterSlideIndex', ui.presenterSlideIndex - 1);
                }
                break;
            case 'presenter-next':
                if (ui.presenterSlideIndex < AppState.getSlides().length - 1) {
                    AppState.setUI('presenterSlideIndex', ui.presenterSlideIndex + 1);
                }
                break;

            // Export actions
            case 'export-presentation':
                Components.showToast('Export started (simulated)');
                break;
            case 'copy-share-link': {
                const linkInput = document.getElementById('shareLink');
                if (linkInput) {
                    linkInput.select();
                    try { document.execCommand('copy'); } catch(e) {}
                    Components.showToast('Link copied to clipboard');
                }
                break;
            }

            // Theme
            case 'set-theme': {
                const themeId = el.getAttribute('data-theme-id');
                AppState.updatePresentation({ themeId: themeId });
                Components.showToast('Theme updated');
                break;
            }

            // Collaborator
            case 'toggle-collaborator': {
                const userId = el.getAttribute('data-user-id');
                const pres = AppState.getPresentation();
                const collabs = pres.collaborators || [];
                const idx = collabs.indexOf(userId);
                if (idx >= 0) {
                    collabs.splice(idx, 1);
                } else {
                    collabs.push(userId);
                }
                AppState.updatePresentation({ collaborators: collabs });
                break;
            }

            // Settings
            case 'save-settings': {
                const titleInput = document.getElementById('settings-title');
                const widthInput = document.getElementById('settings-width');
                const heightInput = document.getElementById('settings-height');
                const durationInput = document.getElementById('settings-default-duration');
                const updates = {};
                if (titleInput) updates.title = titleInput.value.trim() || 'Untitled';
                if (widthInput) updates.slideWidth = parseInt(widthInput.value) || 1920;
                if (heightInput) updates.slideHeight = parseInt(heightInput.value) || 1080;
                // Default transition is handled by dropdown
                const defTrMenu = document.getElementById('settings-default-transition-menu');
                if (defTrMenu) {
                    const selItem = defTrMenu.querySelector('.dropdown-item.selected');
                    const trType = selItem ? selItem.getAttribute('data-value') : 'none';
                    updates.defaultTransition = { type: trType, duration: parseInt(durationInput ? durationInput.value : 0) || 0 };
                }
                AppState.updatePresentation(updates);
                AppState.setUI('currentView', 'editor');
                Components.showToast('Settings saved');
                break;
            }

            // Title edit
            case 'edit-title': {
                const presTitle = AppState.getPresentation().title;
                Components.showModal('Edit Title',
                    '<div class="prop-group">' + Components.textInput('modal-title', presTitle, 'Presentation title', 'Title') + '</div>',
                    '<button class="btn btn-secondary" data-action="close-modal">Cancel</button> <button class="btn btn-primary" id="saveTitleBtn">Save</button>'
                );
                setTimeout(function() {
                    var btn = document.getElementById('saveTitleBtn');
                    if (btn) {
                        btn.addEventListener('click', function() {
                            var input = document.getElementById('modal-title');
                            var title = input ? input.value.trim() : '';
                            if (title) {
                                AppState.updatePresentation({ title: title });
                                Components.closeModal();
                            }
                        });
                    }
                }, 50);
                break;
            }

            // Speaker notes toggle
            case 'toggle-notes':
                AppState.setUI('showSpeakerNotes', !ui.showSpeakerNotes);
                break;

            // Modal
            case 'close-modal':
                Components.closeModal();
                break;
            case 'confirm-modal':
                Components.executeConfirm();
                break;
        }
    }

    function _toggleDropdown(id) {
        var menu = document.getElementById(id + '-menu');
        if (!menu) return;
        // Close all other dropdowns
        document.querySelectorAll('.dropdown-menu.open').forEach(function(m) {
            if (m.id !== id + '-menu') m.classList.remove('open');
        });
        menu.classList.toggle('open');
    }

    function _handleDropdownSelect(item) {
        var ddId = item.getAttribute('data-dropdown-item');
        var value = item.getAttribute('data-value');
        var menu = document.getElementById(ddId + '-menu');

        // Update selected state
        if (menu) {
            menu.querySelectorAll('.dropdown-item').forEach(function(i) { i.classList.remove('selected'); });
            item.classList.add('selected');
            menu.classList.remove('open');

            // Update trigger label
            var trigger = document.querySelector('[data-dropdown-trigger="' + ddId + '"] .dropdown-label');
            if (trigger) trigger.textContent = item.textContent;
        }

        // Handle specific dropdowns
        var slideId = AppState.getUI().currentSlideId;
        var sel = AppState.getSelectedElement();

        switch (ddId) {
            case 'prop-font-family':
                if (sel) AppState.updateElement(slideId, sel.id, { style: { fontFamily: value } });
                break;
            case 'prop-font-size':
                if (sel) AppState.updateElement(slideId, sel.id, { style: { fontSize: parseInt(value) } });
                break;
            case 'prop-font-weight':
                if (sel) AppState.updateElement(slideId, sel.id, { style: { fontWeight: value } });
                break;
            case 'prop-shape-type':
                if (sel) AppState.updateElement(slideId, sel.id, { shapeType: value });
                break;
            case 'prop-transition-type':
                if (slideId) {
                    var slide = AppState.getSlideById(slideId);
                    if (slide) {
                        var dur = slide.transition ? slide.transition.duration : 500;
                        AppState.updateSlide(slideId, { transition: { type: value, duration: dur } });
                    }
                }
                break;
            case 'prop-default-transition-type': {
                var pres = AppState.getPresentation();
                var defDur = pres.defaultTransition ? pres.defaultTransition.duration : 500;
                AppState.updatePresentation({ defaultTransition: { type: value, duration: defDur } });
                break;
            }
            case 'prop-animation-type':
                if (sel) AppState.updateElement(slideId, sel.id, { animation: { type: value } });
                break;
            case 'export-format':
                AppState.updatePresentation({ exportFormat: value });
                break;
            case 'share-permission':
                AppState.updatePresentation({ sharePermission: value });
                break;
            case 'settings-default-transition':
                // Handled by save-settings
                break;
        }
    }

    function _handleColorSwatchClick(swatch) {
        var color = swatch.getAttribute('data-color');
        var slideId = AppState.getUI().currentSlideId;
        var sel = AppState.getSelectedElement();

        // Check context: which color picker is this in?
        var parent = swatch.closest('.prop-group, .panel-section');
        if (!parent) return;

        // Check for slide background color context
        var slideBgInput = parent.querySelector('#prop-slide-bg');
        if (slideBgInput) {
            AppState.updateSlide(slideId, { backgroundColor: color });
            return;
        }

        if (!sel) return;

        // Check for fill color context (shape)
        var fillInput = parent.querySelector('#prop-fill-color');
        if (fillInput) {
            AppState.updateElement(slideId, sel.id, { style: { fill: color } });
            return;
        }

        // Check for text color context
        var textColorInput = parent.querySelector('#prop-text-color');
        if (textColorInput) {
            AppState.updateElement(slideId, sel.id, { style: { color: color } });
            return;
        }
    }

    function _handleInput(e) {
        var target = e.target;
        var slideId = AppState.getUI().currentSlideId;
        var sel = AppState.getSelectedElement();

        // Speaker notes
        if (target.id === 'speakerNotesInput') {
            clearTimeout(_debounceTimer);
            _debounceTimer = setTimeout(function() {
                AppState.updateSlide(slideId, { speakerNotes: target.value });
            }, 300);
            return;
        }

        // Element content textarea
        if (target.id === 'prop-content' && sel) {
            clearTimeout(_debounceTimer);
            _debounceTimer = setTimeout(function() {
                AppState.updateElement(slideId, sel.id, { content: target.value });
            }, 300);
            return;
        }

        // Position & size props
        if (target.getAttribute('data-prop') && sel) {
            var prop = target.getAttribute('data-prop');
            var val = parseInt(target.value);
            if (!isNaN(val)) {
                var update = {};
                update[prop] = val;
                clearTimeout(_debounceTimer);
                _debounceTimer = setTimeout(function() {
                    AppState.updateElement(slideId, sel.id, update);
                }, 200);
            }
            return;
        }

        // Style props (fill, stroke, color hex inputs)
        if (target.getAttribute('data-style-prop') && sel) {
            var styleProp = target.getAttribute('data-style-prop');
            var styleVal = target.value;
            if (styleProp === 'strokeWidth' || styleProp === 'cornerRadius' || styleProp === 'opacity') {
                styleVal = parseFloat(styleVal);
                if (isNaN(styleVal)) return;
            }
            var styleUpdate = {};
            styleUpdate[styleProp] = styleVal;
            clearTimeout(_debounceTimer);
            _debounceTimer = setTimeout(function() {
                AppState.updateElement(slideId, sel.id, { style: styleUpdate });
            }, 300);
            return;
        }

        // Slide background prop
        if (target.getAttribute('data-slide-prop')) {
            var slideProp = target.getAttribute('data-slide-prop');
            clearTimeout(_debounceTimer);
            _debounceTimer = setTimeout(function() {
                var up = {};
                up[slideProp] = target.value;
                AppState.updateSlide(slideId, up);
            }, 300);
            return;
        }

        // Transition duration
        if (target.id === 'prop-transition-duration') {
            var slide = AppState.getSlideById(slideId);
            if (slide) {
                var trType = slide.transition ? slide.transition.type : 'none';
                AppState.updateSlide(slideId, { transition: { type: trType, duration: parseInt(target.value) || 0 } });
            }
            return;
        }

        // Default transition duration
        if (target.id === 'prop-default-transition-duration') {
            var pres = AppState.getPresentation();
            var defType = pres.defaultTransition ? pres.defaultTransition.type : 'none';
            AppState.updatePresentation({ defaultTransition: { type: defType, duration: parseInt(target.value) || 0 } });
            return;
        }

        // Animation props
        if (target.id === 'prop-animation-duration' && sel) {
            AppState.updateElement(slideId, sel.id, { animation: { duration: parseInt(target.value) || 0 } });
            return;
        }
        if (target.id === 'prop-animation-delay' && sel) {
            AppState.updateElement(slideId, sel.id, { animation: { delay: parseInt(target.value) || 0 } });
            return;
        }
        if (target.id === 'prop-animation-order' && sel) {
            AppState.updateElement(slideId, sel.id, { animation: { order: parseInt(target.value) || 0 } });
            return;
        }

        // Auto-advance interval
        if (target.id === 'auto-advance-interval') {
            AppState.updatePresentation({ autoAdvanceInterval: parseInt(target.value) || 5000 });
            return;
        }

        // Reply input (enter to submit)
        if (target.classList.contains('reply-input') && e.inputType === 'insertLineBreak') {
            return; // handled by keydown
        }
    }

    function _handleChange(e) {
        var target = e.target;

        // Toggles in export view
        if (target.id === 'show-slide-numbers') {
            AppState.updatePresentation({ showSlideNumbers: target.checked });
        } else if (target.id === 'loop-presentation') {
            AppState.updatePresentation({ loopPresentation: target.checked });
        } else if (target.id === 'auto-advance') {
            AppState.updatePresentation({ autoAdvance: target.checked });
        } else if (target.id === 'embed-enabled') {
            AppState.updatePresentation({ embedEnabled: target.checked });
        }
    }

    function _handleKeydown(e) {
        var ui = AppState.getUI();

        // Reply input: Enter to submit
        if (e.key === 'Enter' && e.target.classList.contains('reply-input')) {
            var text = e.target.value.trim();
            if (!text) return;
            var cmtId = e.target.getAttribute('data-comment-id');
            AppState.addReply(cmtId, text);
            e.target.value = '';
            return;
        }

        // Presenter: arrow keys
        if (ui.currentView === 'presenter') {
            if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ') {
                e.preventDefault();
                if (ui.presenterSlideIndex < AppState.getSlides().length - 1) {
                    AppState.setUI('presenterSlideIndex', ui.presenterSlideIndex + 1);
                }
            } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
                e.preventDefault();
                if (ui.presenterSlideIndex > 0) {
                    AppState.setUI('presenterSlideIndex', ui.presenterSlideIndex - 1);
                }
            } else if (e.key === 'Escape') {
                AppState.setUI('currentView', 'editor');
            }
            return;
        }

        // Delete selected element
        if (e.key === 'Delete' || e.key === 'Backspace') {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
            var selId = ui.selectedElementId;
            if (selId) {
                AppState.deleteElement(ui.currentSlideId, selId);
            }
        }

        // Escape to deselect
        if (e.key === 'Escape') {
            if (ui.selectedElementId) {
                AppState.setSelectedElement(null);
            }
        }
    }

    function _handleMouseDown(e) {
        var canvasEl = e.target.closest('.canvas-element');
        if (!canvasEl) return;

        var elId = canvasEl.getAttribute('data-element-id');
        var slideIdAttr = canvasEl.getAttribute('data-slide-id');
        var element = AppState.getElementById(slideIdAttr, elId);
        if (!element || element.locked) return;

        // Check for resize handle
        var resizeHandle = e.target.closest('.resize-handle');
        if (resizeHandle) {
            _startResize(e, canvasEl, element, resizeHandle.getAttribute('data-resize'));
            return;
        }

        // Start drag
        _startElementDrag(e, canvasEl, element);
    }

    function _startElementDrag(e, canvasEl, element) {
        e.preventDefault();
        var slideEl = document.getElementById('canvasSlide');
        if (!slideEl) return;

        var zoom = AppState.getUI().zoom / 100;
        var startX = e.clientX;
        var startY = e.clientY;
        var origX = element.x;
        var origY = element.y;
        var slideId = AppState.getUI().currentSlideId;

        function onMouseMove(ev) {
            var dx = (ev.clientX - startX) / zoom;
            var dy = (ev.clientY - startY) / zoom;
            canvasEl.style.left = (origX + dx) + 'px';
            canvasEl.style.top = (origY + dy) + 'px';
        }

        function onMouseUp(ev) {
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
            var dx = (ev.clientX - startX) / zoom;
            var dy = (ev.clientY - startY) / zoom;
            if (Math.abs(dx) > 2 || Math.abs(dy) > 2) {
                AppState.moveElement(slideId, element.id, Math.round(origX + dx), Math.round(origY + dy));
            }
        }

        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
    }

    function _startResize(e, canvasEl, element, direction) {
        e.preventDefault();
        e.stopPropagation();
        var zoom = AppState.getUI().zoom / 100;
        var startX = e.clientX;
        var startY = e.clientY;
        var origW = element.width;
        var origH = element.height;
        var origX = element.x;
        var origY = element.y;
        var slideId = AppState.getUI().currentSlideId;

        function onMouseMove(ev) {
            var dx = (ev.clientX - startX) / zoom;
            var dy = (ev.clientY - startY) / zoom;
            var newW = origW, newH = origH, newX = origX, newY = origY;
            if (direction.includes('e')) { newW = Math.max(20, origW + dx); }
            if (direction.includes('w')) { newW = Math.max(20, origW - dx); newX = origX + dx; }
            if (direction.includes('s')) { newH = Math.max(20, origH + dy); }
            if (direction.includes('n')) { newH = Math.max(20, origH - dy); newY = origY + dy; }
            canvasEl.style.width = newW + 'px';
            canvasEl.style.height = newH + 'px';
            canvasEl.style.left = newX + 'px';
            canvasEl.style.top = newY + 'px';
        }

        function onMouseUp(ev) {
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
            var dx = (ev.clientX - startX) / zoom;
            var dy = (ev.clientY - startY) / zoom;
            var newW = origW, newH = origH, newX = origX, newY = origY;
            if (direction.includes('e')) { newW = Math.max(20, origW + dx); }
            if (direction.includes('w')) { newW = Math.max(20, origW - dx); newX = origX + dx; }
            if (direction.includes('s')) { newH = Math.max(20, origH + dy); }
            if (direction.includes('n')) { newH = Math.max(20, origH - dy); newY = origY + dy; }
            AppState.updateElement(slideId, element.id, {
                x: Math.round(newX), y: Math.round(newY),
                width: Math.round(newW), height: Math.round(newH)
            });
        }

        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
    }

    function _handleDblClick(e) {
        // Double-click on text element to edit inline (future feature hint)
        var canvasEl = e.target.closest('.canvas-element');
        if (canvasEl) {
            var elId = canvasEl.getAttribute('data-element-id');
            var slideIdAttr = canvasEl.getAttribute('data-slide-id');
            var element = AppState.getElementById(slideIdAttr, elId);
            if (element && element.type === 'text') {
                // Focus the content textarea in properties panel
                AppState.setSelectedElement(elId);
                setTimeout(function() {
                    var textarea = document.getElementById('prop-content');
                    if (textarea) textarea.focus();
                }, 100);
            }
        }
    }

    // Slide filmstrip drag & drop
    function _handleSlideDragStart(e) {
        var thumb = e.target.closest('.slide-thumbnail');
        if (!thumb) return;
        _dragSlideId = thumb.getAttribute('data-slide-id');
        thumb.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', _dragSlideId);
    }

    function _handleSlideDragOver(e) {
        var thumb = e.target.closest('.slide-thumbnail');
        if (!thumb || !_dragSlideId) return;
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        _dragOverSlideId = thumb.getAttribute('data-slide-id');
        document.querySelectorAll('.slide-thumbnail.drag-over').forEach(function(t) { t.classList.remove('drag-over'); });
        thumb.classList.add('drag-over');
    }

    function _handleSlideDragLeave(e) {
        var thumb = e.target.closest('.slide-thumbnail');
        if (thumb) thumb.classList.remove('drag-over');
    }

    function _handleSlideDrop(e) {
        e.preventDefault();
        var thumb = e.target.closest('.slide-thumbnail');
        if (!thumb || !_dragSlideId) return;

        var targetId = thumb.getAttribute('data-slide-id');
        if (targetId !== _dragSlideId) {
            var targetSlide = AppState.getSlideById(targetId);
            if (targetSlide) {
                AppState.moveSlide(_dragSlideId, targetSlide.position);
            }
        }
        _cleanupDrag();
    }

    function _handleSlideDragEnd() {
        _cleanupDrag();
    }

    function _cleanupDrag() {
        _dragSlideId = null;
        _dragOverSlideId = null;
        document.querySelectorAll('.slide-thumbnail.dragging, .slide-thumbnail.drag-over').forEach(function(t) {
            t.classList.remove('dragging', 'drag-over');
        });
    }

    return { init, render };
})();

document.addEventListener('DOMContentLoaded', App.init);
