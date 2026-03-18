const AppState = (function() {
    let _state = {};
    let _listeners = [];

    // UI state (not persisted)
    let _ui = {
        currentView: 'editor',
        currentSlideId: null,
        selectedElementId: null,
        rightPanel: 'properties',
        showSpeakerNotes: true,
        showGrid: false,
        showRulers: false,
        zoom: 100,
        presenterSlideIndex: 0,
        searchQuery: '',
        filterResolved: 'all',
        editingElementText: false
    };

    function init() {
        const saved = localStorage.getItem('figmaSlidesState');
        if (saved) {
            try {
                const parsed = JSON.parse(saved);
                if (parsed._seedVersion === SEED_DATA_VERSION) {
                    _state = parsed;
                } else {
                    localStorage.removeItem('figmaSlidesState');
                    _state = getSeedData();
                }
            } catch (e) {
                _state = getSeedData();
            }
        } else {
            _state = getSeedData();
        }
        if (_state.slides && _state.slides.length > 0) {
            _ui.currentSlideId = _state.slides[0].id;
        }
        notify();
    }

    function resetToSeedData() {
        localStorage.removeItem('figmaSlidesState');
        _state = getSeedData();
        _ui.currentView = 'editor';
        _ui.currentSlideId = _state.slides[0] ? _state.slides[0].id : null;
        _ui.selectedElementId = null;
        _ui.rightPanel = 'properties';
        _ui.presenterSlideIndex = 0;
        notify();
    }

    function _persist() {
        localStorage.setItem('figmaSlidesState', JSON.stringify(_state));
    }

    function _pushStateToServer() {
        const serializable = getSerializableState();
        fetch('/api/state', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(serializable)
        }).catch(() => {});
    }

    function getSerializableState() {
        return JSON.parse(JSON.stringify(_state));
    }

    function notify() {
        _persist();
        _pushStateToServer();
        _listeners.forEach(fn => fn());
    }

    function subscribe(fn) {
        _listeners.push(fn);
    }

    // Getters
    function getPresentation() { return _state.presentation; }
    function getSlides() { return _state.slides || []; }
    function getSlideById(id) { return (_state.slides || []).find(s => s.id === id); }
    function getCurrentSlide() { return getSlideById(_ui.currentSlideId); }
    function getTemplates() { return _state.templates || []; }
    function getTemplateById(id) { return (_state.templates || []).find(t => t.id === id); }
    function getComments() { return _state.comments || []; }
    function getCommentsForSlide(slideId) { return (_state.comments || []).filter(c => c.slideId === slideId); }
    function getCommentById(id) { return (_state.comments || []).find(c => c.id === id); }
    function getUsers() { return _state.users || []; }
    function getUserById(id) { return (_state.users || []).find(u => u.id === id); }
    function getCurrentUser() { return _state.currentUser; }
    function getThemes() { return _state.themes || []; }
    function getThemeById(id) { return (_state.themes || []).find(t => t.id === id); }
    function getCurrentTheme() { return getThemeById(_state.presentation.themeId); }
    function getFontFamilies() { return _state.fontFamilies || []; }
    function getFontSizes() { return _state.fontSizes || []; }
    function getTransitionTypes() { return _state.transitionTypes || []; }
    function getAnimationTypes() { return _state.animationTypes || []; }
    function getShapeTypes() { return _state.shapeTypes || []; }
    function getElementColors() { return _state.elementColors || []; }

    function getFilteredComments() {
        let comments = _state.comments || [];
        if (_ui.filterResolved === 'open') {
            comments = comments.filter(c => !c.resolved);
        } else if (_ui.filterResolved === 'resolved') {
            comments = comments.filter(c => c.resolved);
        }
        if (_ui.searchQuery) {
            const q = _ui.searchQuery.toLowerCase();
            comments = comments.filter(c =>
                c.text.toLowerCase().includes(q) ||
                (getUserById(c.author) || {}).name.toLowerCase().includes(q)
            );
        }
        return comments;
    }

    function getElementById(slideId, elementId) {
        const slide = getSlideById(slideId);
        if (!slide) return null;
        return (slide.elements || []).find(e => e.id === elementId);
    }

    function getSelectedElement() {
        if (!_ui.selectedElementId || !_ui.currentSlideId) return null;
        return getElementById(_ui.currentSlideId, _ui.selectedElementId);
    }

    // UI state
    function getUI() { return _ui; }
    function setUI(key, value) {
        _ui[key] = value;
        _listeners.forEach(fn => fn());
    }

    function setCurrentSlide(slideId) {
        _ui.currentSlideId = slideId;
        _ui.selectedElementId = null;
        _listeners.forEach(fn => fn());
    }

    function setSelectedElement(elementId) {
        _ui.selectedElementId = elementId;
        _listeners.forEach(fn => fn());
    }

    // Mutations: Presentation
    function updatePresentation(updates) {
        Object.assign(_state.presentation, updates);
        _state.presentation.updatedAt = new Date().toISOString();
        notify();
    }

    // Mutations: Slides
    function addSlide(templateId, afterSlideId) {
        const template = templateId ? getTemplateById(templateId) : null;
        const id = 'slide_' + (_state._nextSlideId++);
        const theme = getCurrentTheme() || THEMES[0];

        let position;
        if (afterSlideId) {
            const afterSlide = getSlideById(afterSlideId);
            position = afterSlide ? afterSlide.position + 1 : _state.slides.length;
        } else {
            position = _state.slides.length;
        }

        // Shift positions of slides after the insertion point
        _state.slides.forEach(s => {
            if (s.position >= position) s.position++;
        });

        const elements = template ? template.elements.map(el => ({
            ...JSON.parse(JSON.stringify(el)),
            id: 'el_' + (_state._nextElementId++),
            animation: { type: 'none', duration: 0, delay: 0, order: 0 },
            locked: false,
            visible: true
        })) : [];

        const newSlide = {
            id: id,
            position: position,
            templateType: template ? template.type : 'blank',
            backgroundColor: theme.bgColor,
            transition: JSON.parse(JSON.stringify(_state.presentation.defaultTransition)),
            speakerNotes: '',
            elements: elements
        };

        _state.slides.push(newSlide);
        _state.slides.sort((a, b) => a.position - b.position);
        _ui.currentSlideId = id;
        _ui.selectedElementId = null;
        notify();
        return newSlide;
    }

    function duplicateSlide(slideId) {
        const source = getSlideById(slideId);
        if (!source) return null;

        const id = 'slide_' + (_state._nextSlideId++);
        const position = source.position + 1;

        _state.slides.forEach(s => {
            if (s.position >= position) s.position++;
        });

        const newSlide = JSON.parse(JSON.stringify(source));
        newSlide.id = id;
        newSlide.position = position;
        newSlide.elements = newSlide.elements.map(el => ({
            ...el,
            id: 'el_' + (_state._nextElementId++)
        }));

        _state.slides.push(newSlide);
        _state.slides.sort((a, b) => a.position - b.position);
        _ui.currentSlideId = id;
        _ui.selectedElementId = null;
        notify();
        return newSlide;
    }

    function deleteSlide(slideId) {
        const idx = _state.slides.findIndex(s => s.id === slideId);
        if (idx === -1 || _state.slides.length <= 1) return false;

        const deletedPosition = _state.slides[idx].position;
        _state.slides.splice(idx, 1);

        _state.slides.forEach(s => {
            if (s.position > deletedPosition) s.position--;
        });
        _state.slides.sort((a, b) => a.position - b.position);

        // Remove comments for this slide
        _state.comments = _state.comments.filter(c => c.slideId !== slideId);

        if (_ui.currentSlideId === slideId) {
            _ui.currentSlideId = _state.slides[Math.min(idx, _state.slides.length - 1)].id;
            _ui.selectedElementId = null;
        }
        notify();
        return true;
    }

    function moveSlide(slideId, newPosition) {
        const slide = getSlideById(slideId);
        if (!slide) return;

        const oldPosition = slide.position;
        if (oldPosition === newPosition) return;

        _state.slides.forEach(s => {
            if (oldPosition < newPosition) {
                if (s.position > oldPosition && s.position <= newPosition) s.position--;
            } else {
                if (s.position >= newPosition && s.position < oldPosition) s.position++;
            }
        });
        slide.position = newPosition;
        _state.slides.sort((a, b) => a.position - b.position);
        notify();
    }

    function updateSlide(slideId, updates) {
        const slide = getSlideById(slideId);
        if (!slide) return;
        Object.assign(slide, updates);
        notify();
    }

    function applyTemplate(slideId, templateId) {
        const slide = getSlideById(slideId);
        const template = getTemplateById(templateId);
        if (!slide || !template) return;

        const theme = getCurrentTheme() || THEMES[0];
        slide.templateType = template.type;
        slide.elements = template.elements.map(el => ({
            ...JSON.parse(JSON.stringify(el)),
            id: 'el_' + (_state._nextElementId++),
            animation: { type: 'none', duration: 0, delay: 0, order: 0 },
            locked: false,
            visible: true
        }));
        // Adjust text colors based on theme
        slide.elements.forEach(el => {
            if (el.type === 'text' && el.style) {
                if (el.style.color === '#ffffff') el.style.color = theme.textColor;
            }
        });
        notify();
    }

    // Mutations: Elements
    function addElement(slideId, elementData) {
        const slide = getSlideById(slideId);
        if (!slide) return null;

        const id = 'el_' + (_state._nextElementId++);
        const element = {
            id: id,
            type: elementData.type || 'text',
            x: elementData.x || 400,
            y: elementData.y || 300,
            width: elementData.width || 400,
            height: elementData.height || 60,
            content: elementData.content || (elementData.type === 'text' ? 'New text' : ''),
            style: elementData.style || (elementData.type === 'text'
                ? { fontFamily: 'Inter', fontSize: 24, fontWeight: 'normal', color: '#ffffff', textAlign: 'left', italic: false, underline: false }
                : { fill: '#6366f1', stroke: '#334155', strokeWidth: 1, cornerRadius: 0, opacity: 1 }),
            shapeType: elementData.shapeType || undefined,
            animation: { type: 'none', duration: 0, delay: 0, order: 0 },
            locked: false,
            visible: true
        };
        if (elementData.type === 'shape' && !element.shapeType) {
            element.shapeType = 'rectangle';
        }
        slide.elements.push(element);
        _ui.selectedElementId = id;
        notify();
        return element;
    }

    function updateElement(slideId, elementId, updates) {
        const el = getElementById(slideId, elementId);
        if (!el) return;
        // Deep merge for style and animation
        if (updates.style) {
            el.style = { ...el.style, ...updates.style };
            delete updates.style;
        }
        if (updates.animation) {
            el.animation = { ...el.animation, ...updates.animation };
            delete updates.animation;
        }
        Object.assign(el, updates);
        notify();
    }

    function deleteElement(slideId, elementId) {
        const slide = getSlideById(slideId);
        if (!slide) return;
        const idx = slide.elements.findIndex(e => e.id === elementId);
        if (idx === -1) return;
        slide.elements.splice(idx, 1);
        if (_ui.selectedElementId === elementId) {
            _ui.selectedElementId = null;
        }
        // Remove element-specific comments
        _state.comments = _state.comments.filter(c => c.elementId !== elementId);
        notify();
    }

    function moveElement(slideId, elementId, x, y) {
        const el = getElementById(slideId, elementId);
        if (!el || el.locked) return;
        el.x = x;
        el.y = y;
        notify();
    }

    function resizeElement(slideId, elementId, width, height) {
        const el = getElementById(slideId, elementId);
        if (!el || el.locked) return;
        el.width = Math.max(20, width);
        el.height = Math.max(20, height);
        notify();
    }

    function toggleElementLock(slideId, elementId) {
        const el = getElementById(slideId, elementId);
        if (!el) return;
        el.locked = !el.locked;
        notify();
    }

    function toggleElementVisibility(slideId, elementId) {
        const el = getElementById(slideId, elementId);
        if (!el) return;
        el.visible = !el.visible;
        notify();
    }

    function reorderElement(slideId, elementId, direction) {
        const slide = getSlideById(slideId);
        if (!slide) return;
        const idx = slide.elements.findIndex(e => e.id === elementId);
        if (idx === -1) return;

        if (direction === 'up' && idx < slide.elements.length - 1) {
            [slide.elements[idx], slide.elements[idx + 1]] = [slide.elements[idx + 1], slide.elements[idx]];
        } else if (direction === 'down' && idx > 0) {
            [slide.elements[idx], slide.elements[idx - 1]] = [slide.elements[idx - 1], slide.elements[idx]];
        } else if (direction === 'top') {
            const el = slide.elements.splice(idx, 1)[0];
            slide.elements.push(el);
        } else if (direction === 'bottom') {
            const el = slide.elements.splice(idx, 1)[0];
            slide.elements.unshift(el);
        }
        notify();
    }

    // Mutations: Comments
    function addComment(slideId, elementId, text) {
        const id = 'cmt_' + (_state._nextCommentId++);
        const comment = {
            id: id,
            slideId: slideId,
            elementId: elementId || null,
            author: _state.currentUser.id,
            text: text,
            createdAt: new Date().toISOString(),
            resolved: false,
            replies: []
        };
        _state.comments.push(comment);
        notify();
        return comment;
    }

    function addReply(commentId, text) {
        const comment = getCommentById(commentId);
        if (!comment) return;
        const id = 'reply_' + (_state._nextReplyId++);
        comment.replies.push({
            id: id,
            author: _state.currentUser.id,
            text: text,
            createdAt: new Date().toISOString()
        });
        notify();
    }

    function resolveComment(commentId) {
        const comment = getCommentById(commentId);
        if (!comment) return;
        comment.resolved = !comment.resolved;
        notify();
    }

    function deleteComment(commentId) {
        const idx = _state.comments.findIndex(c => c.id === commentId);
        if (idx === -1) return;
        _state.comments.splice(idx, 1);
        notify();
    }

    function deleteReply(commentId, replyId) {
        const comment = getCommentById(commentId);
        if (!comment) return;
        const idx = comment.replies.findIndex(r => r.id === replyId);
        if (idx === -1) return;
        comment.replies.splice(idx, 1);
        notify();
    }

    // Custom template
    function saveAsTemplate(slideId, name) {
        const slide = getSlideById(slideId);
        if (!slide) return null;

        const id = 'tmpl_custom_' + Date.now();
        const template = {
            id: id,
            name: name,
            type: 'custom',
            description: 'Custom template saved from slide',
            elements: slide.elements.map(el => {
                const copy = JSON.parse(JSON.stringify(el));
                delete copy.id;
                delete copy.animation;
                delete copy.locked;
                delete copy.visible;
                return copy;
            })
        };
        _state.templates.push(template);
        notify();
        return template;
    }

    function deleteTemplate(templateId) {
        // Only allow deleting custom templates
        const idx = _state.templates.findIndex(t => t.id === templateId);
        if (idx === -1) return;
        if (!_state.templates[idx].id.startsWith('tmpl_custom_')) return;
        _state.templates.splice(idx, 1);
        notify();
    }

    return {
        init, resetToSeedData, subscribe, notify, getSerializableState,
        getPresentation, getSlides, getSlideById, getCurrentSlide,
        getTemplates, getTemplateById,
        getComments, getCommentsForSlide, getCommentById, getFilteredComments,
        getUsers, getUserById, getCurrentUser,
        getThemes, getThemeById, getCurrentTheme,
        getFontFamilies, getFontSizes, getTransitionTypes, getAnimationTypes,
        getShapeTypes, getElementColors,
        getElementById, getSelectedElement,
        getUI, setUI, setCurrentSlide, setSelectedElement,
        updatePresentation,
        addSlide, duplicateSlide, deleteSlide, moveSlide, updateSlide, applyTemplate,
        addElement, updateElement, deleteElement, moveElement, resizeElement,
        toggleElementLock, toggleElementVisibility, reorderElement,
        addComment, addReply, resolveComment, deleteComment, deleteReply,
        saveAsTemplate, deleteTemplate
    };
})();
