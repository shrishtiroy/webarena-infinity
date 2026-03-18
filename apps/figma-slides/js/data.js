const SEED_DATA_VERSION = 1;

const USERS = [
    { id: 'usr_1', name: 'Sarah Chen', email: 'sarah.chen@acme.io', avatarColor: '#6366f1', role: 'owner' },
    { id: 'usr_2', name: 'Alex Rivera', email: 'alex.rivera@acme.io', avatarColor: '#ec4899', role: 'editor' },
    { id: 'usr_3', name: 'Jordan Kim', email: 'jordan.kim@acme.io', avatarColor: '#14b8a6', role: 'editor' },
    { id: 'usr_4', name: 'Morgan Taylor', email: 'morgan.taylor@acme.io', avatarColor: '#f59e0b', role: 'viewer' },
    { id: 'usr_5', name: 'Casey Patel', email: 'casey.patel@acme.io', avatarColor: '#ef4444', role: 'editor' },
    { id: 'usr_6', name: 'Riley Zhang', email: 'riley.zhang@acme.io', avatarColor: '#8b5cf6', role: 'viewer' },
    { id: 'usr_7', name: 'Quinn Nakamura', email: 'quinn.nakamura@acme.io', avatarColor: '#06b6d4', role: 'commenter' },
    { id: 'usr_8', name: 'Avery Johnson', email: 'avery.johnson@acme.io', avatarColor: '#84cc16', role: 'editor' }
];

const CURRENT_USER = USERS[0];

const THEMES = [
    { id: 'theme_modern_dark', name: 'Modern Dark', bgColor: '#1a1a2e', textColor: '#ffffff', accentColor: '#6366f1', secondaryBg: '#16213e' },
    { id: 'theme_clean_light', name: 'Clean Light', bgColor: '#ffffff', textColor: '#1f2937', accentColor: '#3b82f6', secondaryBg: '#f3f4f6' },
    { id: 'theme_warm_earth', name: 'Warm Earth', bgColor: '#fef3c7', textColor: '#78350f', accentColor: '#d97706', secondaryBg: '#fffbeb' },
    { id: 'theme_ocean_breeze', name: 'Ocean Breeze', bgColor: '#0c4a6e', textColor: '#e0f2fe', accentColor: '#38bdf8', secondaryBg: '#075985' },
    { id: 'theme_forest_green', name: 'Forest Green', bgColor: '#064e3b', textColor: '#d1fae5', accentColor: '#34d399', secondaryBg: '#065f46' },
    { id: 'theme_sunset_gradient', name: 'Sunset Gradient', bgColor: '#7c2d12', textColor: '#fff7ed', accentColor: '#fb923c', secondaryBg: '#9a3412' },
    { id: 'theme_minimal_gray', name: 'Minimal Gray', bgColor: '#f9fafb', textColor: '#374151', accentColor: '#6b7280', secondaryBg: '#e5e7eb' },
    { id: 'theme_bold_purple', name: 'Bold Purple', bgColor: '#3b0764', textColor: '#f5f3ff', accentColor: '#a855f7', secondaryBg: '#4c1d95' },
    { id: 'theme_coral_pop', name: 'Coral Pop', bgColor: '#fff1f2', textColor: '#9f1239', accentColor: '#fb7185', secondaryBg: '#ffe4e6' },
    { id: 'theme_midnight_blue', name: 'Midnight Blue', bgColor: '#0f172a', textColor: '#e2e8f0', accentColor: '#60a5fa', secondaryBg: '#1e293b' }
];

const FONT_FAMILIES = [
    'Inter', 'Roboto', 'Open Sans', 'Montserrat', 'Playfair Display',
    'Lato', 'Poppins', 'Source Sans Pro', 'Raleway', 'Nunito',
    'Merriweather', 'PT Sans', 'Ubuntu', 'Oswald', 'Fira Sans'
];

const FONT_SIZES = [10, 12, 14, 16, 18, 20, 24, 28, 32, 36, 40, 48, 56, 64, 72, 80, 96];

const TRANSITION_TYPES = ['none', 'fade', 'slide-left', 'slide-right', 'slide-up', 'slide-down', 'dissolve', 'push', 'zoom-in', 'zoom-out'];

const ANIMATION_TYPES = ['none', 'appear', 'fade-in', 'fade-out', 'move-in-left', 'move-in-right', 'move-in-top', 'move-in-bottom', 'zoom-in', 'zoom-out', 'bounce', 'spin'];

const SHAPE_TYPES = ['rectangle', 'circle', 'line', 'arrow', 'triangle', 'diamond', 'star', 'rounded-rectangle', 'pentagon', 'hexagon'];

const ELEMENT_COLORS = [
    '#6366f1', '#ec4899', '#14b8a6', '#f59e0b', '#ef4444',
    '#8b5cf6', '#06b6d4', '#84cc16', '#3b82f6', '#f97316',
    '#10b981', '#e11d48', '#0ea5e9', '#a855f7', '#22c55e',
    '#ffffff', '#000000', '#374151', '#9ca3af', '#d1d5db',
    '#fbbf24', '#34d399', '#60a5fa', '#fb7185', '#c084fc'
];

const TEMPLATES = [
    {
        id: 'tmpl_title',
        name: 'Title Slide',
        type: 'title',
        description: 'A bold title slide with centered heading and subtitle',
        elements: [
            { type: 'text', x: 160, y: 340, width: 1600, height: 140, content: 'Presentation Title', style: { fontFamily: 'Inter', fontSize: 72, fontWeight: 'bold', color: '#ffffff', textAlign: 'center', italic: false, underline: false } },
            { type: 'text', x: 360, y: 520, width: 1200, height: 60, content: 'Subtitle or description goes here', style: { fontFamily: 'Inter', fontSize: 28, fontWeight: 'normal', color: '#94a3b8', textAlign: 'center', italic: false, underline: false } },
            { type: 'shape', x: 760, y: 620, width: 400, height: 4, content: '', style: { fill: '#6366f1', stroke: 'none', strokeWidth: 0, cornerRadius: 2, opacity: 1 }, shapeType: 'rectangle' }
        ]
    },
    {
        id: 'tmpl_title_content',
        name: 'Title + Content',
        type: 'title-content',
        description: 'Title at the top with a content area below',
        elements: [
            { type: 'text', x: 120, y: 80, width: 1680, height: 80, content: 'Slide Title', style: { fontFamily: 'Inter', fontSize: 48, fontWeight: 'bold', color: '#ffffff', textAlign: 'left', italic: false, underline: false } },
            { type: 'shape', x: 120, y: 170, width: 200, height: 4, content: '', style: { fill: '#6366f1', stroke: 'none', strokeWidth: 0, cornerRadius: 2, opacity: 1 }, shapeType: 'rectangle' },
            { type: 'text', x: 120, y: 220, width: 1680, height: 600, content: 'Add your content here. Use bullet points, descriptions, or any text to convey your message effectively.', style: { fontFamily: 'Inter', fontSize: 24, fontWeight: 'normal', color: '#cbd5e1', textAlign: 'left', italic: false, underline: false } }
        ]
    },
    {
        id: 'tmpl_two_column',
        name: 'Two Column',
        type: 'two-column',
        description: 'Title with two equal-width content columns',
        elements: [
            { type: 'text', x: 120, y: 80, width: 1680, height: 80, content: 'Two Column Layout', style: { fontFamily: 'Inter', fontSize: 48, fontWeight: 'bold', color: '#ffffff', textAlign: 'left', italic: false, underline: false } },
            { type: 'shape', x: 120, y: 170, width: 200, height: 4, content: '', style: { fill: '#6366f1', stroke: 'none', strokeWidth: 0, cornerRadius: 2, opacity: 1 }, shapeType: 'rectangle' },
            { type: 'text', x: 120, y: 220, width: 800, height: 600, content: 'Left column content goes here.', style: { fontFamily: 'Inter', fontSize: 24, fontWeight: 'normal', color: '#cbd5e1', textAlign: 'left', italic: false, underline: false } },
            { type: 'text', x: 1000, y: 220, width: 800, height: 600, content: 'Right column content goes here.', style: { fontFamily: 'Inter', fontSize: 24, fontWeight: 'normal', color: '#cbd5e1', textAlign: 'left', italic: false, underline: false } }
        ]
    },
    {
        id: 'tmpl_section_header',
        name: 'Section Header',
        type: 'section-header',
        description: 'Large centered text for section breaks',
        elements: [
            { type: 'text', x: 260, y: 380, width: 1400, height: 120, content: 'Section Title', style: { fontFamily: 'Inter', fontSize: 64, fontWeight: 'bold', color: '#ffffff', textAlign: 'center', italic: false, underline: false } },
            { type: 'shape', x: 810, y: 530, width: 300, height: 4, content: '', style: { fill: '#6366f1', stroke: 'none', strokeWidth: 0, cornerRadius: 2, opacity: 1 }, shapeType: 'rectangle' }
        ]
    },
    {
        id: 'tmpl_blank',
        name: 'Blank',
        type: 'blank',
        description: 'Empty slide for complete creative freedom',
        elements: []
    },
    {
        id: 'tmpl_image_focused',
        name: 'Image Focused',
        type: 'image-focused',
        description: 'Large image area with a caption below',
        elements: [
            { type: 'shape', x: 160, y: 80, width: 1600, height: 780, content: '', style: { fill: '#1e293b', stroke: '#334155', strokeWidth: 2, cornerRadius: 12, opacity: 1 }, shapeType: 'rounded-rectangle' },
            { type: 'text', x: 560, y: 400, width: 800, height: 40, content: 'Image placeholder', style: { fontFamily: 'Inter', fontSize: 20, fontWeight: 'normal', color: '#64748b', textAlign: 'center', italic: true, underline: false } },
            { type: 'text', x: 160, y: 900, width: 1600, height: 50, content: 'Caption text goes here', style: { fontFamily: 'Inter', fontSize: 18, fontWeight: 'normal', color: '#94a3b8', textAlign: 'center', italic: false, underline: false } }
        ]
    },
    {
        id: 'tmpl_comparison',
        name: 'Comparison',
        type: 'comparison',
        description: 'Side-by-side comparison with headers',
        elements: [
            { type: 'text', x: 120, y: 80, width: 1680, height: 80, content: 'Comparison', style: { fontFamily: 'Inter', fontSize: 48, fontWeight: 'bold', color: '#ffffff', textAlign: 'center', italic: false, underline: false } },
            { type: 'shape', x: 120, y: 200, width: 820, height: 700, content: '', style: { fill: '#1e293b', stroke: '#334155', strokeWidth: 1, cornerRadius: 8, opacity: 1 }, shapeType: 'rounded-rectangle' },
            { type: 'text', x: 160, y: 220, width: 740, height: 50, content: 'Option A', style: { fontFamily: 'Inter', fontSize: 32, fontWeight: 'bold', color: '#6366f1', textAlign: 'center', italic: false, underline: false } },
            { type: 'text', x: 160, y: 290, width: 740, height: 560, content: 'Details about option A', style: { fontFamily: 'Inter', fontSize: 20, fontWeight: 'normal', color: '#cbd5e1', textAlign: 'left', italic: false, underline: false } },
            { type: 'shape', x: 980, y: 200, width: 820, height: 700, content: '', style: { fill: '#1e293b', stroke: '#334155', strokeWidth: 1, cornerRadius: 8, opacity: 1 }, shapeType: 'rounded-rectangle' },
            { type: 'text', x: 1020, y: 220, width: 740, height: 50, content: 'Option B', style: { fontFamily: 'Inter', fontSize: 32, fontWeight: 'bold', color: '#ec4899', textAlign: 'center', italic: false, underline: false } },
            { type: 'text', x: 1020, y: 290, width: 740, height: 560, content: 'Details about option B', style: { fontFamily: 'Inter', fontSize: 20, fontWeight: 'normal', color: '#cbd5e1', textAlign: 'left', italic: false, underline: false } }
        ]
    },
    {
        id: 'tmpl_quote',
        name: 'Quote',
        type: 'quote',
        description: 'Centered quote with attribution',
        elements: [
            { type: 'text', x: 260, y: 120, width: 100, height: 200, content: '\u201C', style: { fontFamily: 'Playfair Display', fontSize: 180, fontWeight: 'bold', color: '#6366f1', textAlign: 'left', italic: false, underline: false } },
            { type: 'text', x: 300, y: 300, width: 1320, height: 240, content: 'The best way to predict the future is to create it.', style: { fontFamily: 'Playfair Display', fontSize: 40, fontWeight: 'normal', color: '#ffffff', textAlign: 'center', italic: true, underline: false } },
            { type: 'shape', x: 860, y: 580, width: 200, height: 3, content: '', style: { fill: '#6366f1', stroke: 'none', strokeWidth: 0, cornerRadius: 1, opacity: 1 }, shapeType: 'rectangle' },
            { type: 'text', x: 560, y: 620, width: 800, height: 40, content: '- Peter Drucker', style: { fontFamily: 'Inter', fontSize: 20, fontWeight: 'normal', color: '#94a3b8', textAlign: 'center', italic: false, underline: false } }
        ]
    },
    {
        id: 'tmpl_three_column',
        name: 'Three Column',
        type: 'three-column',
        description: 'Title with three content columns',
        elements: [
            { type: 'text', x: 120, y: 80, width: 1680, height: 80, content: 'Three Pillars', style: { fontFamily: 'Inter', fontSize: 48, fontWeight: 'bold', color: '#ffffff', textAlign: 'center', italic: false, underline: false } },
            { type: 'shape', x: 120, y: 200, width: 520, height: 680, content: '', style: { fill: '#1e293b', stroke: '#334155', strokeWidth: 1, cornerRadius: 8, opacity: 1 }, shapeType: 'rounded-rectangle' },
            { type: 'text', x: 160, y: 230, width: 440, height: 50, content: 'Column 1', style: { fontFamily: 'Inter', fontSize: 28, fontWeight: 'bold', color: '#6366f1', textAlign: 'center', italic: false, underline: false } },
            { type: 'shape', x: 700, y: 200, width: 520, height: 680, content: '', style: { fill: '#1e293b', stroke: '#334155', strokeWidth: 1, cornerRadius: 8, opacity: 1 }, shapeType: 'rounded-rectangle' },
            { type: 'text', x: 740, y: 230, width: 440, height: 50, content: 'Column 2', style: { fontFamily: 'Inter', fontSize: 28, fontWeight: 'bold', color: '#ec4899', textAlign: 'center', italic: false, underline: false } },
            { type: 'shape', x: 1280, y: 200, width: 520, height: 680, content: '', style: { fill: '#1e293b', stroke: '#334155', strokeWidth: 1, cornerRadius: 8, opacity: 1 }, shapeType: 'rounded-rectangle' },
            { type: 'text', x: 1320, y: 230, width: 440, height: 50, content: 'Column 3', style: { fontFamily: 'Inter', fontSize: 28, fontWeight: 'bold', color: '#14b8a6', textAlign: 'center', italic: false, underline: false } }
        ]
    },
    {
        id: 'tmpl_stats',
        name: 'Statistics',
        type: 'stats',
        description: 'Showcase key numbers and statistics',
        elements: [
            { type: 'text', x: 120, y: 80, width: 1680, height: 80, content: 'Key Metrics', style: { fontFamily: 'Inter', fontSize: 48, fontWeight: 'bold', color: '#ffffff', textAlign: 'center', italic: false, underline: false } },
            { type: 'text', x: 160, y: 300, width: 360, height: 100, content: '99.9%', style: { fontFamily: 'Inter', fontSize: 72, fontWeight: 'bold', color: '#6366f1', textAlign: 'center', italic: false, underline: false } },
            { type: 'text', x: 160, y: 400, width: 360, height: 40, content: 'Uptime', style: { fontFamily: 'Inter', fontSize: 20, fontWeight: 'normal', color: '#94a3b8', textAlign: 'center', italic: false, underline: false } },
            { type: 'text', x: 600, y: 300, width: 360, height: 100, content: '2.4M', style: { fontFamily: 'Inter', fontSize: 72, fontWeight: 'bold', color: '#ec4899', textAlign: 'center', italic: false, underline: false } },
            { type: 'text', x: 600, y: 400, width: 360, height: 40, content: 'Users', style: { fontFamily: 'Inter', fontSize: 20, fontWeight: 'normal', color: '#94a3b8', textAlign: 'center', italic: false, underline: false } },
            { type: 'text', x: 1040, y: 300, width: 360, height: 100, content: '340+', style: { fontFamily: 'Inter', fontSize: 72, fontWeight: 'bold', color: '#14b8a6', textAlign: 'center', italic: false, underline: false } },
            { type: 'text', x: 1040, y: 400, width: 360, height: 40, content: 'Integrations', style: { fontFamily: 'Inter', fontSize: 20, fontWeight: 'normal', color: '#94a3b8', textAlign: 'center', italic: false, underline: false } },
            { type: 'text', x: 1480, y: 300, width: 360, height: 100, content: '4.8', style: { fontFamily: 'Inter', fontSize: 72, fontWeight: 'bold', color: '#f59e0b', textAlign: 'center', italic: false, underline: false } },
            { type: 'text', x: 1480, y: 400, width: 360, height: 40, content: 'Rating', style: { fontFamily: 'Inter', fontSize: 20, fontWeight: 'normal', color: '#94a3b8', textAlign: 'center', italic: false, underline: false } }
        ]
    }
];

function _generateElementId() {
    return 'el_' + Math.random().toString(36).substr(2, 9);
}

const PRESENTATION = {
    id: 'pres_1',
    title: 'Q1 2026 Product Strategy',
    createdAt: '2026-01-15T09:00:00Z',
    updatedAt: '2026-03-15T14:30:00Z',
    owner: 'usr_1',
    collaborators: ['usr_2', 'usr_3', 'usr_5', 'usr_8'],
    themeId: 'theme_modern_dark',
    slideWidth: 1920,
    slideHeight: 1080,
    defaultTransition: { type: 'fade', duration: 500 },
    shareLink: 'https://slides.figma.com/p/q1-2026-strategy-xK9mP2',
    sharePermission: 'view',
    embedEnabled: false,
    exportFormat: 'pdf',
    showSlideNumbers: true,
    loopPresentation: false,
    autoAdvance: false,
    autoAdvanceInterval: 5000
};

const SLIDES = [
    {
        id: 'slide_1',
        position: 0,
        templateType: 'title',
        backgroundColor: '#1a1a2e',
        transition: { type: 'fade', duration: 500 },
        speakerNotes: 'Welcome everyone to the Q1 2026 product strategy review. Today we will cover our vision, key metrics, roadmap, and next steps.',
        elements: [
            { id: 'el_s1_1', type: 'text', x: 160, y: 280, width: 1600, height: 140, content: 'Q1 2026 Product Strategy', style: { fontFamily: 'Inter', fontSize: 72, fontWeight: 'bold', color: '#ffffff', textAlign: 'center', italic: false, underline: false }, animation: { type: 'fade-in', duration: 800, delay: 0, order: 1 }, locked: false, visible: true },
            { id: 'el_s1_2', type: 'text', x: 460, y: 460, width: 1000, height: 60, content: 'Acme Corporation \u2022 Internal Strategy Review', style: { fontFamily: 'Inter', fontSize: 28, fontWeight: 'normal', color: '#94a3b8', textAlign: 'center', italic: false, underline: false }, animation: { type: 'fade-in', duration: 800, delay: 200, order: 2 }, locked: false, visible: true },
            { id: 'el_s1_3', type: 'shape', x: 760, y: 560, width: 400, height: 4, content: '', shapeType: 'rectangle', style: { fill: '#6366f1', stroke: 'none', strokeWidth: 0, cornerRadius: 2, opacity: 1 }, animation: { type: 'appear', duration: 400, delay: 400, order: 3 }, locked: false, visible: true },
            { id: 'el_s1_4', type: 'text', x: 560, y: 600, width: 800, height: 40, content: 'March 18, 2026', style: { fontFamily: 'Inter', fontSize: 20, fontWeight: 'normal', color: '#64748b', textAlign: 'center', italic: false, underline: false }, animation: { type: 'fade-in', duration: 600, delay: 600, order: 4 }, locked: false, visible: true }
        ]
    },
    {
        id: 'slide_2',
        position: 1,
        templateType: 'title-content',
        backgroundColor: '#1a1a2e',
        transition: { type: 'slide-left', duration: 400 },
        speakerNotes: 'Here is our agenda for today. We have a packed session covering five major topics.',
        elements: [
            { id: 'el_s2_1', type: 'text', x: 120, y: 80, width: 1680, height: 80, content: 'Agenda', style: { fontFamily: 'Inter', fontSize: 48, fontWeight: 'bold', color: '#ffffff', textAlign: 'left', italic: false, underline: false }, animation: { type: 'none', duration: 0, delay: 0, order: 0 }, locked: false, visible: true },
            { id: 'el_s2_2', type: 'shape', x: 120, y: 170, width: 200, height: 4, content: '', shapeType: 'rectangle', style: { fill: '#6366f1', stroke: 'none', strokeWidth: 0, cornerRadius: 2, opacity: 1 }, animation: { type: 'none', duration: 0, delay: 0, order: 0 }, locked: false, visible: true },
            { id: 'el_s2_3', type: 'text', x: 160, y: 230, width: 1600, height: 500, content: '1. Company Vision & Mission Update\n2. Market Overview & Competitive Landscape\n3. Key Performance Metrics\n4. Product Roadmap & Feature Highlights\n5. Team, Budget & Next Steps', style: { fontFamily: 'Inter', fontSize: 32, fontWeight: 'normal', color: '#cbd5e1', textAlign: 'left', italic: false, underline: false }, animation: { type: 'fade-in', duration: 600, delay: 0, order: 1 }, locked: false, visible: true },
            { id: 'el_s2_4', type: 'shape', x: 120, y: 230, width: 6, height: 500, content: '', shapeType: 'rectangle', style: { fill: '#6366f1', stroke: 'none', strokeWidth: 0, cornerRadius: 3, opacity: 0.6 }, animation: { type: 'none', duration: 0, delay: 0, order: 0 }, locked: false, visible: true }
        ]
    },
    {
        id: 'slide_3',
        position: 2,
        templateType: 'section-header',
        backgroundColor: '#16213e',
        transition: { type: 'fade', duration: 600 },
        speakerNotes: '',
        elements: [
            { id: 'el_s3_1', type: 'text', x: 260, y: 380, width: 1400, height: 120, content: 'Company Vision', style: { fontFamily: 'Inter', fontSize: 64, fontWeight: 'bold', color: '#ffffff', textAlign: 'center', italic: false, underline: false }, animation: { type: 'zoom-in', duration: 800, delay: 0, order: 1 }, locked: false, visible: true },
            { id: 'el_s3_2', type: 'shape', x: 810, y: 530, width: 300, height: 4, content: '', shapeType: 'rectangle', style: { fill: '#6366f1', stroke: 'none', strokeWidth: 0, cornerRadius: 2, opacity: 1 }, animation: { type: 'appear', duration: 400, delay: 400, order: 2 }, locked: false, visible: true },
            { id: 'el_s3_3', type: 'text', x: 460, y: 560, width: 1000, height: 50, content: 'Where we are heading in 2026 and beyond', style: { fontFamily: 'Inter', fontSize: 24, fontWeight: 'normal', color: '#94a3b8', textAlign: 'center', italic: true, underline: false }, animation: { type: 'fade-in', duration: 600, delay: 600, order: 3 }, locked: false, visible: true }
        ]
    },
    {
        id: 'slide_4',
        position: 3,
        templateType: 'title-content',
        backgroundColor: '#1a1a2e',
        transition: { type: 'slide-left', duration: 400 },
        speakerNotes: 'Our vision remains unchanged but our approach has evolved. We are now focusing on AI-first experiences across all products. This is a significant shift from our previous mobile-first strategy.',
        elements: [
            { id: 'el_s4_1', type: 'text', x: 120, y: 80, width: 1680, height: 80, content: 'Our Vision', style: { fontFamily: 'Inter', fontSize: 48, fontWeight: 'bold', color: '#ffffff', textAlign: 'left', italic: false, underline: false }, animation: { type: 'none', duration: 0, delay: 0, order: 0 }, locked: false, visible: true },
            { id: 'el_s4_2', type: 'shape', x: 120, y: 170, width: 200, height: 4, content: '', shapeType: 'rectangle', style: { fill: '#6366f1', stroke: 'none', strokeWidth: 0, cornerRadius: 2, opacity: 1 }, animation: { type: 'none', duration: 0, delay: 0, order: 0 }, locked: true, visible: true },
            { id: 'el_s4_3', type: 'text', x: 120, y: 220, width: 1200, height: 160, content: 'To empower every team with intelligent tools that transform how they build, collaborate, and ship products.', style: { fontFamily: 'Playfair Display', fontSize: 36, fontWeight: 'normal', color: '#e2e8f0', textAlign: 'left', italic: true, underline: false }, animation: { type: 'fade-in', duration: 800, delay: 0, order: 1 }, locked: false, visible: true },
            { id: 'el_s4_4', type: 'shape', x: 120, y: 440, width: 800, height: 400, content: '', shapeType: 'rounded-rectangle', style: { fill: '#1e293b', stroke: '#334155', strokeWidth: 1, cornerRadius: 12, opacity: 1 }, animation: { type: 'fade-in', duration: 600, delay: 200, order: 2 }, locked: false, visible: true },
            { id: 'el_s4_5', type: 'text', x: 160, y: 470, width: 720, height: 340, content: 'Core Pillars:\n\u2022 AI-First Design\n\u2022 Real-time Collaboration\n\u2022 Developer Experience\n\u2022 Enterprise Security', style: { fontFamily: 'Inter', fontSize: 24, fontWeight: 'normal', color: '#cbd5e1', textAlign: 'left', italic: false, underline: false }, animation: { type: 'move-in-left', duration: 600, delay: 400, order: 3 }, locked: false, visible: true },
            { id: 'el_s4_6', type: 'shape', x: 1000, y: 440, width: 800, height: 400, content: '', shapeType: 'rounded-rectangle', style: { fill: '#1e293b', stroke: '#334155', strokeWidth: 1, cornerRadius: 12, opacity: 1 }, animation: { type: 'fade-in', duration: 600, delay: 200, order: 2 }, locked: false, visible: true },
            { id: 'el_s4_7', type: 'text', x: 1040, y: 470, width: 720, height: 340, content: '2026 Focus Areas:\n\u2022 Launch AI Assistant v2\n\u2022 Mobile app redesign\n\u2022 SOC 2 Type II certification\n\u2022 APAC market expansion', style: { fontFamily: 'Inter', fontSize: 24, fontWeight: 'normal', color: '#cbd5e1', textAlign: 'left', italic: false, underline: false }, animation: { type: 'move-in-right', duration: 600, delay: 400, order: 3 }, locked: false, visible: true }
        ]
    },
    {
        id: 'slide_5',
        position: 4,
        templateType: 'section-header',
        backgroundColor: '#16213e',
        transition: { type: 'dissolve', duration: 700 },
        speakerNotes: '',
        elements: [
            { id: 'el_s5_1', type: 'text', x: 260, y: 380, width: 1400, height: 120, content: 'Market Overview', style: { fontFamily: 'Inter', fontSize: 64, fontWeight: 'bold', color: '#ffffff', textAlign: 'center', italic: false, underline: false }, animation: { type: 'zoom-in', duration: 800, delay: 0, order: 1 }, locked: false, visible: true },
            { id: 'el_s5_2', type: 'shape', x: 810, y: 530, width: 300, height: 4, content: '', shapeType: 'rectangle', style: { fill: '#ec4899', stroke: 'none', strokeWidth: 0, cornerRadius: 2, opacity: 1 }, animation: { type: 'appear', duration: 400, delay: 400, order: 2 }, locked: false, visible: true }
        ]
    },
    {
        id: 'slide_6',
        position: 5,
        templateType: 'title-content',
        backgroundColor: '#1a1a2e',
        transition: { type: 'slide-left', duration: 400 },
        speakerNotes: 'The market is growing rapidly. Our TAM has increased by 34% year-over-year. Key drivers include remote work adoption and AI integration demand.',
        elements: [
            { id: 'el_s6_1', type: 'text', x: 120, y: 80, width: 1680, height: 80, content: 'Market Landscape', style: { fontFamily: 'Inter', fontSize: 48, fontWeight: 'bold', color: '#ffffff', textAlign: 'left', italic: false, underline: false }, animation: { type: 'none', duration: 0, delay: 0, order: 0 }, locked: false, visible: true },
            { id: 'el_s6_2', type: 'shape', x: 120, y: 170, width: 200, height: 4, content: '', shapeType: 'rectangle', style: { fill: '#ec4899', stroke: 'none', strokeWidth: 0, cornerRadius: 2, opacity: 1 }, animation: { type: 'none', duration: 0, delay: 0, order: 0 }, locked: false, visible: true },
            { id: 'el_s6_3', type: 'text', x: 120, y: 220, width: 1680, height: 180, content: 'The collaboration software market is projected to reach $85.2B by 2027, growing at 13.2% CAGR. AI-powered tools represent the fastest-growing segment at 42% year-over-year.', style: { fontFamily: 'Inter', fontSize: 24, fontWeight: 'normal', color: '#cbd5e1', textAlign: 'left', italic: false, underline: false }, animation: { type: 'fade-in', duration: 600, delay: 0, order: 1 }, locked: false, visible: true },
            { id: 'el_s6_4', type: 'shape', x: 120, y: 450, width: 520, height: 440, content: '', shapeType: 'rounded-rectangle', style: { fill: '#1e293b', stroke: '#334155', strokeWidth: 1, cornerRadius: 8, opacity: 1 }, animation: { type: 'fade-in', duration: 400, delay: 200, order: 2 }, locked: false, visible: true },
            { id: 'el_s6_5', type: 'text', x: 160, y: 480, width: 440, height: 380, content: 'Key Trends\n\u2022 AI-first workflows\n\u2022 Async collaboration\n\u2022 Design-to-code\n\u2022 No-code/low-code\n\u2022 Edge computing', style: { fontFamily: 'Inter', fontSize: 22, fontWeight: 'normal', color: '#cbd5e1', textAlign: 'left', italic: false, underline: false }, animation: { type: 'move-in-left', duration: 500, delay: 300, order: 3 }, locked: false, visible: true },
            { id: 'el_s6_6', type: 'shape', x: 700, y: 450, width: 520, height: 440, content: '', shapeType: 'rounded-rectangle', style: { fill: '#1e293b', stroke: '#334155', strokeWidth: 1, cornerRadius: 8, opacity: 1 }, animation: { type: 'fade-in', duration: 400, delay: 200, order: 2 }, locked: false, visible: true },
            { id: 'el_s6_7', type: 'text', x: 740, y: 480, width: 440, height: 380, content: 'Opportunities\n\u2022 Enterprise segment\n\u2022 APAC expansion\n\u2022 API marketplace\n\u2022 Education sector\n\u2022 Government contracts', style: { fontFamily: 'Inter', fontSize: 22, fontWeight: 'normal', color: '#cbd5e1', textAlign: 'left', italic: false, underline: false }, animation: { type: 'move-in-bottom', duration: 500, delay: 400, order: 4 }, locked: false, visible: true },
            { id: 'el_s6_8', type: 'shape', x: 1280, y: 450, width: 520, height: 440, content: '', shapeType: 'rounded-rectangle', style: { fill: '#1e293b', stroke: '#334155', strokeWidth: 1, cornerRadius: 8, opacity: 1 }, animation: { type: 'fade-in', duration: 400, delay: 200, order: 2 }, locked: false, visible: true },
            { id: 'el_s6_9', type: 'text', x: 1320, y: 480, width: 440, height: 380, content: 'Threats\n\u2022 New AI-native entrants\n\u2022 Platform consolidation\n\u2022 Open-source alternatives\n\u2022 Regulatory changes\n\u2022 Economic slowdown', style: { fontFamily: 'Inter', fontSize: 22, fontWeight: 'normal', color: '#cbd5e1', textAlign: 'left', italic: false, underline: false }, animation: { type: 'move-in-right', duration: 500, delay: 500, order: 5 }, locked: false, visible: true }
        ]
    },
    {
        id: 'slide_7',
        position: 6,
        templateType: 'comparison',
        backgroundColor: '#1a1a2e',
        transition: { type: 'slide-left', duration: 400 },
        speakerNotes: 'We maintain a strong position against competitors. Our collaboration features are best-in-class but we need to close the gap on AI capabilities. Figma acquired AI startup Diagram last year.',
        elements: [
            { id: 'el_s7_1', type: 'text', x: 120, y: 80, width: 1680, height: 80, content: 'Competitive Analysis', style: { fontFamily: 'Inter', fontSize: 48, fontWeight: 'bold', color: '#ffffff', textAlign: 'center', italic: false, underline: false }, animation: { type: 'none', duration: 0, delay: 0, order: 0 }, locked: false, visible: true },
            { id: 'el_s7_2', type: 'shape', x: 120, y: 200, width: 540, height: 360, content: '', shapeType: 'rounded-rectangle', style: { fill: '#1e293b', stroke: '#6366f1', strokeWidth: 2, cornerRadius: 8, opacity: 1 }, animation: { type: 'fade-in', duration: 400, delay: 0, order: 1 }, locked: false, visible: true },
            { id: 'el_s7_3', type: 'text', x: 160, y: 220, width: 460, height: 40, content: 'Acme Platform', style: { fontFamily: 'Inter', fontSize: 28, fontWeight: 'bold', color: '#6366f1', textAlign: 'center', italic: false, underline: false }, animation: { type: 'none', duration: 0, delay: 0, order: 0 }, locked: false, visible: true },
            { id: 'el_s7_4', type: 'text', x: 160, y: 280, width: 460, height: 250, content: '\u2713 Real-time collab\n\u2713 Enterprise SSO\n\u2713 Design systems\n\u2713 99.9% uptime\n\u25CB AI features (Q2)', style: { fontFamily: 'Inter', fontSize: 20, fontWeight: 'normal', color: '#cbd5e1', textAlign: 'left', italic: false, underline: false }, animation: { type: 'fade-in', duration: 400, delay: 200, order: 2 }, locked: false, visible: true },
            { id: 'el_s7_5', type: 'shape', x: 700, y: 200, width: 540, height: 360, content: '', shapeType: 'rounded-rectangle', style: { fill: '#1e293b', stroke: '#334155', strokeWidth: 1, cornerRadius: 8, opacity: 1 }, animation: { type: 'fade-in', duration: 400, delay: 100, order: 1 }, locked: false, visible: true },
            { id: 'el_s7_6', type: 'text', x: 740, y: 220, width: 460, height: 40, content: 'Competitor A', style: { fontFamily: 'Inter', fontSize: 28, fontWeight: 'bold', color: '#94a3b8', textAlign: 'center', italic: false, underline: false }, animation: { type: 'none', duration: 0, delay: 0, order: 0 }, locked: false, visible: true },
            { id: 'el_s7_7', type: 'text', x: 740, y: 280, width: 460, height: 250, content: '\u2713 AI-native\n\u2713 Free tier\n\u25CB Limited collab\n\u25CB No SSO\n\u25CB Startup stage', style: { fontFamily: 'Inter', fontSize: 20, fontWeight: 'normal', color: '#cbd5e1', textAlign: 'left', italic: false, underline: false }, animation: { type: 'fade-in', duration: 400, delay: 300, order: 3 }, locked: false, visible: true },
            { id: 'el_s7_8', type: 'shape', x: 1280, y: 200, width: 540, height: 360, content: '', shapeType: 'rounded-rectangle', style: { fill: '#1e293b', stroke: '#334155', strokeWidth: 1, cornerRadius: 8, opacity: 1 }, animation: { type: 'fade-in', duration: 400, delay: 200, order: 1 }, locked: false, visible: true },
            { id: 'el_s7_9', type: 'text', x: 1320, y: 220, width: 460, height: 40, content: 'Competitor B', style: { fontFamily: 'Inter', fontSize: 28, fontWeight: 'bold', color: '#94a3b8', textAlign: 'center', italic: false, underline: false }, animation: { type: 'none', duration: 0, delay: 0, order: 0 }, locked: false, visible: true },
            { id: 'el_s7_10', type: 'text', x: 1320, y: 280, width: 460, height: 250, content: '\u2713 Market leader\n\u2713 Full ecosystem\n\u2713 AI features\n\u25CB Expensive\n\u25CB Complex UX', style: { fontFamily: 'Inter', fontSize: 20, fontWeight: 'normal', color: '#cbd5e1', textAlign: 'left', italic: false, underline: false }, animation: { type: 'fade-in', duration: 400, delay: 400, order: 4 }, locked: false, visible: true },
            { id: 'el_s7_11', type: 'text', x: 120, y: 620, width: 1680, height: 100, content: 'Our differentiation: Deep real-time collaboration + enterprise security at competitive pricing. AI gap closing rapidly with Q2 AI Assistant launch.', style: { fontFamily: 'Inter', fontSize: 22, fontWeight: 'normal', color: '#94a3b8', textAlign: 'center', italic: true, underline: false }, animation: { type: 'fade-in', duration: 600, delay: 600, order: 5 }, locked: false, visible: true }
        ]
    },
    {
        id: 'slide_8',
        position: 7,
        templateType: 'section-header',
        backgroundColor: '#16213e',
        transition: { type: 'zoom-in', duration: 500 },
        speakerNotes: '',
        elements: [
            { id: 'el_s8_1', type: 'text', x: 260, y: 380, width: 1400, height: 120, content: 'Key Metrics', style: { fontFamily: 'Inter', fontSize: 64, fontWeight: 'bold', color: '#ffffff', textAlign: 'center', italic: false, underline: false }, animation: { type: 'zoom-in', duration: 800, delay: 0, order: 1 }, locked: false, visible: true },
            { id: 'el_s8_2', type: 'shape', x: 810, y: 530, width: 300, height: 4, content: '', shapeType: 'rectangle', style: { fill: '#14b8a6', stroke: 'none', strokeWidth: 0, cornerRadius: 2, opacity: 1 }, animation: { type: 'appear', duration: 400, delay: 400, order: 2 }, locked: false, visible: true }
        ]
    },
    {
        id: 'slide_9',
        position: 8,
        templateType: 'stats',
        backgroundColor: '#1a1a2e',
        transition: { type: 'fade', duration: 500 },
        speakerNotes: 'These numbers represent our strongest quarter yet. Revenue is up 47% from Q4. Daily active users crossed the 50K milestone for the first time. NPS improved from 62 to 71.',
        elements: [
            { id: 'el_s9_1', type: 'text', x: 120, y: 60, width: 1680, height: 80, content: 'Q1 2026 Performance', style: { fontFamily: 'Inter', fontSize: 48, fontWeight: 'bold', color: '#ffffff', textAlign: 'center', italic: false, underline: false }, animation: { type: 'none', duration: 0, delay: 0, order: 0 }, locked: false, visible: true },
            { id: 'el_s9_2', type: 'shape', x: 120, y: 180, width: 400, height: 340, content: '', shapeType: 'rounded-rectangle', style: { fill: '#1e293b', stroke: '#334155', strokeWidth: 1, cornerRadius: 12, opacity: 1 }, animation: { type: 'fade-in', duration: 400, delay: 0, order: 1 }, locked: false, visible: true },
            { id: 'el_s9_3', type: 'text', x: 140, y: 210, width: 360, height: 100, content: '$4.2M', style: { fontFamily: 'Inter', fontSize: 56, fontWeight: 'bold', color: '#6366f1', textAlign: 'center', italic: false, underline: false }, animation: { type: 'zoom-in', duration: 600, delay: 100, order: 2 }, locked: false, visible: true },
            { id: 'el_s9_4', type: 'text', x: 140, y: 310, width: 360, height: 40, content: 'ARR', style: { fontFamily: 'Inter', fontSize: 20, fontWeight: 'normal', color: '#94a3b8', textAlign: 'center', italic: false, underline: false }, animation: { type: 'none', duration: 0, delay: 0, order: 0 }, locked: false, visible: true },
            { id: 'el_s9_5', type: 'text', x: 140, y: 360, width: 360, height: 30, content: '\u2191 47% from Q4', style: { fontFamily: 'Inter', fontSize: 16, fontWeight: 'bold', color: '#34d399', textAlign: 'center', italic: false, underline: false }, animation: { type: 'none', duration: 0, delay: 0, order: 0 }, locked: false, visible: true },
            { id: 'el_s9_6', type: 'shape', x: 560, y: 180, width: 400, height: 340, content: '', shapeType: 'rounded-rectangle', style: { fill: '#1e293b', stroke: '#334155', strokeWidth: 1, cornerRadius: 12, opacity: 1 }, animation: { type: 'fade-in', duration: 400, delay: 100, order: 1 }, locked: false, visible: true },
            { id: 'el_s9_7', type: 'text', x: 580, y: 210, width: 360, height: 100, content: '52.4K', style: { fontFamily: 'Inter', fontSize: 56, fontWeight: 'bold', color: '#ec4899', textAlign: 'center', italic: false, underline: false }, animation: { type: 'zoom-in', duration: 600, delay: 200, order: 3 }, locked: false, visible: true },
            { id: 'el_s9_8', type: 'text', x: 580, y: 310, width: 360, height: 40, content: 'Daily Active Users', style: { fontFamily: 'Inter', fontSize: 20, fontWeight: 'normal', color: '#94a3b8', textAlign: 'center', italic: false, underline: false }, animation: { type: 'none', duration: 0, delay: 0, order: 0 }, locked: false, visible: true },
            { id: 'el_s9_9', type: 'text', x: 580, y: 360, width: 360, height: 30, content: '\u2191 28% from Q4', style: { fontFamily: 'Inter', fontSize: 16, fontWeight: 'bold', color: '#34d399', textAlign: 'center', italic: false, underline: false }, animation: { type: 'none', duration: 0, delay: 0, order: 0 }, locked: false, visible: true },
            { id: 'el_s9_10', type: 'shape', x: 1000, y: 180, width: 400, height: 340, content: '', shapeType: 'rounded-rectangle', style: { fill: '#1e293b', stroke: '#334155', strokeWidth: 1, cornerRadius: 12, opacity: 1 }, animation: { type: 'fade-in', duration: 400, delay: 200, order: 1 }, locked: false, visible: true },
            { id: 'el_s9_11', type: 'text', x: 1020, y: 210, width: 360, height: 100, content: '71', style: { fontFamily: 'Inter', fontSize: 56, fontWeight: 'bold', color: '#14b8a6', textAlign: 'center', italic: false, underline: false }, animation: { type: 'zoom-in', duration: 600, delay: 300, order: 4 }, locked: false, visible: true },
            { id: 'el_s9_12', type: 'text', x: 1020, y: 310, width: 360, height: 40, content: 'NPS Score', style: { fontFamily: 'Inter', fontSize: 20, fontWeight: 'normal', color: '#94a3b8', textAlign: 'center', italic: false, underline: false }, animation: { type: 'none', duration: 0, delay: 0, order: 0 }, locked: false, visible: true },
            { id: 'el_s9_13', type: 'text', x: 1020, y: 360, width: 360, height: 30, content: '\u2191 9 points from Q4', style: { fontFamily: 'Inter', fontSize: 16, fontWeight: 'bold', color: '#34d399', textAlign: 'center', italic: false, underline: false }, animation: { type: 'none', duration: 0, delay: 0, order: 0 }, locked: false, visible: true },
            { id: 'el_s9_14', type: 'shape', x: 1440, y: 180, width: 400, height: 340, content: '', shapeType: 'rounded-rectangle', style: { fill: '#1e293b', stroke: '#334155', strokeWidth: 1, cornerRadius: 12, opacity: 1 }, animation: { type: 'fade-in', duration: 400, delay: 300, order: 1 }, locked: false, visible: true },
            { id: 'el_s9_15', type: 'text', x: 1460, y: 210, width: 360, height: 100, content: '99.97%', style: { fontFamily: 'Inter', fontSize: 56, fontWeight: 'bold', color: '#f59e0b', textAlign: 'center', italic: false, underline: false }, animation: { type: 'zoom-in', duration: 600, delay: 400, order: 5 }, locked: false, visible: true },
            { id: 'el_s9_16', type: 'text', x: 1460, y: 310, width: 360, height: 40, content: 'Uptime', style: { fontFamily: 'Inter', fontSize: 20, fontWeight: 'normal', color: '#94a3b8', textAlign: 'center', italic: false, underline: false }, animation: { type: 'none', duration: 0, delay: 0, order: 0 }, locked: false, visible: true },
            { id: 'el_s9_17', type: 'text', x: 1460, y: 360, width: 360, height: 30, content: 'Target: 99.95%', style: { fontFamily: 'Inter', fontSize: 16, fontWeight: 'normal', color: '#94a3b8', textAlign: 'center', italic: false, underline: false }, animation: { type: 'none', duration: 0, delay: 0, order: 0 }, locked: false, visible: true },
            { id: 'el_s9_18', type: 'text', x: 120, y: 580, width: 1680, height: 320, content: 'Additional Metrics:\n\u2022 Customer churn rate: 2.1% (down from 3.4%)\n\u2022 Average contract value: $18,400/year\n\u2022 Support ticket resolution: 4.2 hours avg\n\u2022 Feature adoption rate: 68% within 30 days\n\u2022 Enterprise pipeline: $12.8M qualified\n\u2022 Free-to-paid conversion: 14.2%', style: { fontFamily: 'Inter', fontSize: 22, fontWeight: 'normal', color: '#cbd5e1', textAlign: 'left', italic: false, underline: false }, animation: { type: 'fade-in', duration: 600, delay: 500, order: 6 }, locked: false, visible: true }
        ]
    },
    {
        id: 'slide_10',
        position: 9,
        templateType: 'section-header',
        backgroundColor: '#16213e',
        transition: { type: 'push', duration: 500 },
        speakerNotes: '',
        elements: [
            { id: 'el_s10_1', type: 'text', x: 260, y: 380, width: 1400, height: 120, content: 'Product Roadmap', style: { fontFamily: 'Inter', fontSize: 64, fontWeight: 'bold', color: '#ffffff', textAlign: 'center', italic: false, underline: false }, animation: { type: 'zoom-in', duration: 800, delay: 0, order: 1 }, locked: false, visible: true },
            { id: 'el_s10_2', type: 'shape', x: 810, y: 530, width: 300, height: 4, content: '', shapeType: 'rectangle', style: { fill: '#f59e0b', stroke: 'none', strokeWidth: 0, cornerRadius: 2, opacity: 1 }, animation: { type: 'appear', duration: 400, delay: 400, order: 2 }, locked: false, visible: true }
        ]
    },
    {
        id: 'slide_11',
        position: 10,
        templateType: 'title-content',
        backgroundColor: '#1a1a2e',
        transition: { type: 'slide-left', duration: 400 },
        speakerNotes: 'The AI Assistant is our top priority for Q2. We have already completed the NLP pipeline and are working on the UI integration. Beta launch is targeted for April 15.',
        elements: [
            { id: 'el_s11_1', type: 'text', x: 120, y: 60, width: 1680, height: 80, content: 'Feature Highlight: AI Assistant v2', style: { fontFamily: 'Inter', fontSize: 44, fontWeight: 'bold', color: '#ffffff', textAlign: 'left', italic: false, underline: false }, animation: { type: 'none', duration: 0, delay: 0, order: 0 }, locked: false, visible: true },
            { id: 'el_s11_2', type: 'shape', x: 120, y: 150, width: 200, height: 4, content: '', shapeType: 'rectangle', style: { fill: '#f59e0b', stroke: 'none', strokeWidth: 0, cornerRadius: 2, opacity: 1 }, animation: { type: 'none', duration: 0, delay: 0, order: 0 }, locked: false, visible: true },
            { id: 'el_s11_3', type: 'shape', x: 120, y: 190, width: 860, height: 500, content: '', shapeType: 'rounded-rectangle', style: { fill: '#1e293b', stroke: '#334155', strokeWidth: 1, cornerRadius: 12, opacity: 1 }, animation: { type: 'fade-in', duration: 400, delay: 0, order: 1 }, locked: false, visible: true },
            { id: 'el_s11_4', type: 'text', x: 160, y: 210, width: 780, height: 460, content: 'Capabilities:\n\u2022 Natural language queries\n\u2022 Auto-generate designs from prompts\n\u2022 Smart component suggestions\n\u2022 Code generation from designs\n\u2022 Contextual help & documentation\n\u2022 Multi-language support (12 languages)\n\nPowered by fine-tuned LLM with proprietary design knowledge base', style: { fontFamily: 'Inter', fontSize: 22, fontWeight: 'normal', color: '#cbd5e1', textAlign: 'left', italic: false, underline: false }, animation: { type: 'fade-in', duration: 600, delay: 100, order: 2 }, locked: false, visible: true },
            { id: 'el_s11_5', type: 'shape', x: 1020, y: 190, width: 780, height: 500, content: '', shapeType: 'rounded-rectangle', style: { fill: '#1e293b', stroke: '#f59e0b', strokeWidth: 2, cornerRadius: 12, opacity: 1 }, animation: { type: 'fade-in', duration: 400, delay: 200, order: 1 }, locked: false, visible: true },
            { id: 'el_s11_6', type: 'text', x: 1060, y: 210, width: 700, height: 460, content: 'Timeline:\n\u2022 Jan: NLP pipeline complete \u2713\n\u2022 Feb: UI integration \u2713\n\u2022 Mar: Internal beta (current)\n\u2022 Apr 15: Public beta launch\n\u2022 May: GA release\n\nStatus: On Track\nTeam: 8 engineers, 2 ML specialists', style: { fontFamily: 'Inter', fontSize: 22, fontWeight: 'normal', color: '#cbd5e1', textAlign: 'left', italic: false, underline: false }, animation: { type: 'fade-in', duration: 600, delay: 300, order: 3 }, locked: false, visible: true },
            { id: 'el_s11_7', type: 'text', x: 120, y: 730, width: 1680, height: 60, content: 'Expected impact: 25% increase in user productivity, 15% improvement in retention', style: { fontFamily: 'Inter', fontSize: 20, fontWeight: 'normal', color: '#f59e0b', textAlign: 'center', italic: true, underline: false }, animation: { type: 'fade-in', duration: 600, delay: 500, order: 4 }, locked: false, visible: true }
        ]
    },
    {
        id: 'slide_12',
        position: 11,
        templateType: 'title-content',
        backgroundColor: '#1a1a2e',
        transition: { type: 'slide-left', duration: 400 },
        speakerNotes: 'Mobile redesign focuses on touch-first interactions. We conducted 47 user interviews and identified key pain points with the current mobile experience.',
        elements: [
            { id: 'el_s12_1', type: 'text', x: 120, y: 60, width: 1680, height: 80, content: 'Feature Highlight: Mobile Redesign', style: { fontFamily: 'Inter', fontSize: 44, fontWeight: 'bold', color: '#ffffff', textAlign: 'left', italic: false, underline: false }, animation: { type: 'none', duration: 0, delay: 0, order: 0 }, locked: false, visible: true },
            { id: 'el_s12_2', type: 'shape', x: 120, y: 150, width: 200, height: 4, content: '', shapeType: 'rectangle', style: { fill: '#f59e0b', stroke: 'none', strokeWidth: 0, cornerRadius: 2, opacity: 1 }, animation: { type: 'none', duration: 0, delay: 0, order: 0 }, locked: false, visible: true },
            { id: 'el_s12_3', type: 'text', x: 120, y: 200, width: 1680, height: 600, content: 'Key Improvements:\n\n\u2022 Touch-first gesture navigation\n\u2022 Offline mode with smart sync\n\u2022 Redesigned component inspector\n\u2022 Quick actions toolbar\n\u2022 Biometric authentication\n\u2022 Dark mode support\n\u2022 Haptic feedback for precision tools\n\nUser Research: 47 interviews, 2,400 survey responses\nTimeline: Beta in Q2, GA in Q3', style: { fontFamily: 'Inter', fontSize: 24, fontWeight: 'normal', color: '#cbd5e1', textAlign: 'left', italic: false, underline: false }, animation: { type: 'fade-in', duration: 600, delay: 0, order: 1 }, locked: false, visible: true }
        ]
    },
    {
        id: 'slide_13',
        position: 12,
        templateType: 'quote',
        backgroundColor: '#1a1a2e',
        transition: { type: 'dissolve', duration: 600 },
        speakerNotes: 'This quote from our VP of Engineering captures the team sentiment well. We are building something special.',
        elements: [
            { id: 'el_s13_1', type: 'text', x: 260, y: 120, width: 100, height: 200, content: '\u201C', style: { fontFamily: 'Playfair Display', fontSize: 180, fontWeight: 'bold', color: '#6366f1', textAlign: 'left', italic: false, underline: false }, animation: { type: 'fade-in', duration: 800, delay: 0, order: 1 }, locked: false, visible: true },
            { id: 'el_s13_2', type: 'text', x: 300, y: 300, width: 1320, height: 200, content: 'We are not just building tools. We are reshaping how creative teams think, collaborate, and ship their best work.', style: { fontFamily: 'Playfair Display', fontSize: 36, fontWeight: 'normal', color: '#ffffff', textAlign: 'center', italic: true, underline: false }, animation: { type: 'fade-in', duration: 1000, delay: 200, order: 2 }, locked: false, visible: true },
            { id: 'el_s13_3', type: 'shape', x: 860, y: 540, width: 200, height: 3, content: '', shapeType: 'rectangle', style: { fill: '#6366f1', stroke: 'none', strokeWidth: 0, cornerRadius: 1, opacity: 1 }, animation: { type: 'appear', duration: 400, delay: 800, order: 3 }, locked: false, visible: true },
            { id: 'el_s13_4', type: 'text', x: 560, y: 580, width: 800, height: 40, content: 'Maya Rodriguez, VP of Engineering', style: { fontFamily: 'Inter', fontSize: 20, fontWeight: 'normal', color: '#94a3b8', textAlign: 'center', italic: false, underline: false }, animation: { type: 'fade-in', duration: 600, delay: 1000, order: 4 }, locked: false, visible: true }
        ]
    },
    {
        id: 'slide_14',
        position: 13,
        templateType: 'title-content',
        backgroundColor: '#1a1a2e',
        transition: { type: 'slide-left', duration: 400 },
        speakerNotes: 'We are hiring aggressively in Q2. Engineering headcount will increase by 40%. Focus areas are AI/ML, mobile, and platform reliability. Budget approved by CFO last week.',
        elements: [
            { id: 'el_s14_1', type: 'text', x: 120, y: 60, width: 1680, height: 80, content: 'Team & Budget', style: { fontFamily: 'Inter', fontSize: 48, fontWeight: 'bold', color: '#ffffff', textAlign: 'left', italic: false, underline: false }, animation: { type: 'none', duration: 0, delay: 0, order: 0 }, locked: false, visible: true },
            { id: 'el_s14_2', type: 'shape', x: 120, y: 150, width: 200, height: 4, content: '', shapeType: 'rectangle', style: { fill: '#14b8a6', stroke: 'none', strokeWidth: 0, cornerRadius: 2, opacity: 1 }, animation: { type: 'none', duration: 0, delay: 0, order: 0 }, locked: false, visible: true },
            { id: 'el_s14_3', type: 'shape', x: 120, y: 190, width: 860, height: 480, content: '', shapeType: 'rounded-rectangle', style: { fill: '#1e293b', stroke: '#334155', strokeWidth: 1, cornerRadius: 12, opacity: 1 }, animation: { type: 'fade-in', duration: 400, delay: 0, order: 1 }, locked: false, visible: true },
            { id: 'el_s14_4', type: 'text', x: 160, y: 210, width: 780, height: 430, content: 'Current Team (82 people):\n\u2022 Engineering: 45\n\u2022 Design: 12\n\u2022 Product: 8\n\u2022 Sales & Marketing: 11\n\u2022 Operations: 6\n\nQ2 Hiring Plan: +18 roles\n\u2022 6 ML Engineers\n\u2022 4 Mobile Developers\n\u2022 3 Platform Engineers\n\u2022 3 Sales Reps\n\u2022 2 UX Researchers', style: { fontFamily: 'Inter', fontSize: 20, fontWeight: 'normal', color: '#cbd5e1', textAlign: 'left', italic: false, underline: false }, animation: { type: 'fade-in', duration: 600, delay: 100, order: 2 }, locked: false, visible: true },
            { id: 'el_s14_5', type: 'shape', x: 1020, y: 190, width: 780, height: 480, content: '', shapeType: 'rounded-rectangle', style: { fill: '#1e293b', stroke: '#334155', strokeWidth: 1, cornerRadius: 12, opacity: 1 }, animation: { type: 'fade-in', duration: 400, delay: 0, order: 1 }, locked: false, visible: true },
            { id: 'el_s14_6', type: 'text', x: 1060, y: 210, width: 700, height: 430, content: 'Q2 Budget Allocation:\n\u2022 Engineering: $2.8M (45%)\n\u2022 Infrastructure: $1.1M (18%)\n\u2022 Sales & Marketing: $1.2M (19%)\n\u2022 Operations: $0.5M (8%)\n\u2022 R&D / Innovation: $0.6M (10%)\n\nTotal Q2 Budget: $6.2M\n(+22% from Q1)\n\nApproved by CFO on Mar 12, 2026', style: { fontFamily: 'Inter', fontSize: 20, fontWeight: 'normal', color: '#cbd5e1', textAlign: 'left', italic: false, underline: false }, animation: { type: 'fade-in', duration: 600, delay: 200, order: 3 }, locked: false, visible: true }
        ]
    },
    {
        id: 'slide_15',
        position: 14,
        templateType: 'title-content',
        backgroundColor: '#1a1a2e',
        transition: { type: 'slide-left', duration: 400 },
        speakerNotes: 'These are our key action items for the next 90 days. Each item has a clear owner and deadline. We will review progress bi-weekly in the product sync.',
        elements: [
            { id: 'el_s15_1', type: 'text', x: 120, y: 60, width: 1680, height: 80, content: 'Next Steps & Action Items', style: { fontFamily: 'Inter', fontSize: 48, fontWeight: 'bold', color: '#ffffff', textAlign: 'left', italic: false, underline: false }, animation: { type: 'none', duration: 0, delay: 0, order: 0 }, locked: false, visible: true },
            { id: 'el_s15_2', type: 'shape', x: 120, y: 150, width: 200, height: 4, content: '', shapeType: 'rectangle', style: { fill: '#ef4444', stroke: 'none', strokeWidth: 0, cornerRadius: 2, opacity: 1 }, animation: { type: 'none', duration: 0, delay: 0, order: 0 }, locked: false, visible: true },
            { id: 'el_s15_3', type: 'text', x: 120, y: 200, width: 1680, height: 620, content: 'Immediate (This Week):\n\u2022 Finalize AI Assistant beta test group \u2014 Sarah Chen\n\u2022 Submit SOC 2 Type II audit documentation \u2014 Legal team\n\u2022 Review mobile UX research findings \u2014 Design team\n\nShort-term (30 days):\n\u2022 Launch AI Assistant public beta \u2014 Engineering\n\u2022 Complete APAC market analysis \u2014 Strategy team\n\u2022 Hire 3 ML engineers \u2014 Talent acquisition\n\nMedium-term (90 days):\n\u2022 AI Assistant GA release\n\u2022 Mobile app beta launch\n\u2022 SOC 2 certification received\n\u2022 Q2 board presentation preparation', style: { fontFamily: 'Inter', fontSize: 24, fontWeight: 'normal', color: '#cbd5e1', textAlign: 'left', italic: false, underline: false }, animation: { type: 'fade-in', duration: 800, delay: 0, order: 1 }, locked: false, visible: true }
        ]
    },
    {
        id: 'slide_16',
        position: 15,
        templateType: 'title',
        backgroundColor: '#1a1a2e',
        transition: { type: 'fade', duration: 800 },
        speakerNotes: 'Thank you all for your time and attention. I am happy to take any questions now. Remember, the full deck is shared in the team drive.',
        elements: [
            { id: 'el_s16_1', type: 'text', x: 260, y: 300, width: 1400, height: 120, content: 'Thank You', style: { fontFamily: 'Inter', fontSize: 72, fontWeight: 'bold', color: '#ffffff', textAlign: 'center', italic: false, underline: false }, animation: { type: 'fade-in', duration: 1000, delay: 0, order: 1 }, locked: false, visible: true },
            { id: 'el_s16_2', type: 'text', x: 460, y: 460, width: 1000, height: 60, content: 'Questions & Discussion', style: { fontFamily: 'Inter', fontSize: 32, fontWeight: 'normal', color: '#94a3b8', textAlign: 'center', italic: false, underline: false }, animation: { type: 'fade-in', duration: 800, delay: 300, order: 2 }, locked: false, visible: true },
            { id: 'el_s16_3', type: 'shape', x: 810, y: 560, width: 300, height: 4, content: '', shapeType: 'rectangle', style: { fill: '#6366f1', stroke: 'none', strokeWidth: 0, cornerRadius: 2, opacity: 1 }, animation: { type: 'appear', duration: 400, delay: 600, order: 3 }, locked: false, visible: true },
            { id: 'el_s16_4', type: 'text', x: 560, y: 620, width: 800, height: 80, content: 'sarah.chen@acme.io\nSlides shared at: team-drive/q1-strategy-2026', style: { fontFamily: 'Inter', fontSize: 18, fontWeight: 'normal', color: '#64748b', textAlign: 'center', italic: false, underline: false }, animation: { type: 'fade-in', duration: 600, delay: 800, order: 4 }, locked: false, visible: true }
        ]
    }
];

const COMMENTS = [
    {
        id: 'cmt_1',
        slideId: 'slide_4',
        elementId: 'el_s4_5',
        author: 'usr_2',
        text: 'Should we add "Data Privacy" as a fifth core pillar? Given the regulatory landscape, it feels like a strategic differentiator.',
        createdAt: '2026-03-12T10:30:00Z',
        resolved: false,
        replies: [
            { id: 'reply_1', author: 'usr_1', text: 'Great point. Let me check with legal about how to position it. Maybe a sub-item under Enterprise Security?', createdAt: '2026-03-12T11:15:00Z' },
            { id: 'reply_2', author: 'usr_3', text: 'I agree with Alex. Customers are asking about GDPR compliance specifically.', createdAt: '2026-03-12T14:20:00Z' }
        ]
    },
    {
        id: 'cmt_2',
        slideId: 'slide_6',
        elementId: null,
        author: 'usr_3',
        text: 'The TAM figure seems conservative. Latest Gartner report puts it at $92B by 2027.',
        createdAt: '2026-03-13T09:45:00Z',
        resolved: false,
        replies: [
            { id: 'reply_3', author: 'usr_1', text: 'Good catch. I will update this with the Gartner numbers and cite the source.', createdAt: '2026-03-13T10:05:00Z' }
        ]
    },
    {
        id: 'cmt_3',
        slideId: 'slide_7',
        elementId: 'el_s7_7',
        author: 'usr_5',
        text: 'Competitor A just announced their Series C. They might not be "startup stage" much longer.',
        createdAt: '2026-03-14T08:00:00Z',
        resolved: false,
        replies: []
    },
    {
        id: 'cmt_4',
        slideId: 'slide_9',
        elementId: 'el_s9_3',
        author: 'usr_8',
        text: 'Can we break down ARR by segment? Enterprise vs SMB vs self-serve would tell a better story.',
        createdAt: '2026-03-14T11:30:00Z',
        resolved: false,
        replies: [
            { id: 'reply_4', author: 'usr_1', text: 'Great idea! Enterprise is 62%, SMB is 28%, self-serve is 10%. I will add a breakdown.', createdAt: '2026-03-14T13:00:00Z' }
        ]
    },
    {
        id: 'cmt_5',
        slideId: 'slide_9',
        elementId: null,
        author: 'usr_2',
        text: 'The churn rate improvement is impressive! Worth highlighting this more prominently.',
        createdAt: '2026-03-14T15:20:00Z',
        resolved: true,
        replies: [
            { id: 'reply_5', author: 'usr_1', text: 'Agreed. I moved it to the main metrics cards.', createdAt: '2026-03-14T16:00:00Z' }
        ]
    },
    {
        id: 'cmt_6',
        slideId: 'slide_11',
        elementId: 'el_s11_6',
        author: 'usr_3',
        text: 'April 15 beta launch might conflict with our infrastructure migration. Can we push to April 22?',
        createdAt: '2026-03-15T09:00:00Z',
        resolved: false,
        replies: [
            { id: 'reply_6', author: 'usr_5', text: 'The migration is scheduled for April 10-12. We should be stable by the 15th.', createdAt: '2026-03-15T09:30:00Z' },
            { id: 'reply_7', author: 'usr_1', text: 'Let us keep April 15 for now but have April 22 as a fallback. I will flag this as a risk.', createdAt: '2026-03-15T10:15:00Z' }
        ]
    },
    {
        id: 'cmt_7',
        slideId: 'slide_12',
        elementId: null,
        author: 'usr_7',
        text: 'Love the offline mode feature! This was the #1 request from our mobile users in the last survey.',
        createdAt: '2026-03-15T11:00:00Z',
        resolved: true,
        replies: []
    },
    {
        id: 'cmt_8',
        slideId: 'slide_1',
        elementId: 'el_s1_2',
        author: 'usr_5',
        text: 'Should we change the subtitle to include the date? Makes it clearer for reference later.',
        createdAt: '2026-03-10T14:00:00Z',
        resolved: true,
        replies: [
            { id: 'reply_8', author: 'usr_1', text: 'Done, added the date on a separate line below.', createdAt: '2026-03-10T14:30:00Z' }
        ]
    },
    {
        id: 'cmt_9',
        slideId: 'slide_14',
        elementId: 'el_s14_6',
        author: 'usr_8',
        text: 'The R&D budget seems low at 10%. Industry average for SaaS companies is 15-20%. Can we make a case for increasing it?',
        createdAt: '2026-03-16T08:30:00Z',
        resolved: false,
        replies: [
            { id: 'reply_9', author: 'usr_1', text: 'The AI team budget is under Engineering, not R&D. If we combine them it is closer to 55% of budget going to product development.', createdAt: '2026-03-16T09:00:00Z' }
        ]
    },
    {
        id: 'cmt_10',
        slideId: 'slide_15',
        elementId: null,
        author: 'usr_2',
        text: 'We should add a dependency map for the action items. Several of these are interdependent.',
        createdAt: '2026-03-16T10:00:00Z',
        resolved: false,
        replies: []
    },
    {
        id: 'cmt_11',
        slideId: 'slide_2',
        elementId: 'el_s2_3',
        author: 'usr_4',
        text: 'Typo: should be numbered consistently. Consider using icons instead of numbers.',
        createdAt: '2026-03-11T16:00:00Z',
        resolved: true,
        replies: []
    },
    {
        id: 'cmt_12',
        slideId: 'slide_13',
        elementId: 'el_s13_2',
        author: 'usr_6',
        text: 'Beautiful quote! Maybe we should attribute it more prominently. Maya deserves the recognition.',
        createdAt: '2026-03-15T13:00:00Z',
        resolved: false,
        replies: []
    },
    {
        id: 'cmt_13',
        slideId: 'slide_6',
        elementId: 'el_s6_9',
        author: 'usr_5',
        text: 'The regulatory changes threat is real. GDPR enforcement has increased 300% in the last year.',
        createdAt: '2026-03-14T16:45:00Z',
        resolved: false,
        replies: [
            { id: 'reply_10', author: 'usr_3', text: 'We should cross-reference this with the Data Privacy pillar discussion on slide 4.', createdAt: '2026-03-14T17:00:00Z' }
        ]
    },
    {
        id: 'cmt_14',
        slideId: 'slide_16',
        elementId: null,
        author: 'usr_4',
        text: 'Can we add QR code for the team drive link? Makes it easier during the live presentation.',
        createdAt: '2026-03-16T11:00:00Z',
        resolved: false,
        replies: []
    },
    {
        id: 'cmt_15',
        slideId: 'slide_9',
        elementId: 'el_s9_7',
        author: 'usr_3',
        text: 'DAU crossed 50K! We should celebrate this milestone with the team. Planning a small event?',
        createdAt: '2026-03-14T12:00:00Z',
        resolved: true,
        replies: [
            { id: 'reply_11', author: 'usr_1', text: 'Already on it! Pizza party on Friday. Will send the invite.', createdAt: '2026-03-14T12:30:00Z' }
        ]
    },
    {
        id: 'cmt_16',
        slideId: 'slide_11',
        elementId: 'el_s11_4',
        author: 'usr_8',
        text: 'The "12 languages" claim - do we have a confirmed list? Last I checked we were at 9 with 3 in progress.',
        createdAt: '2026-03-16T14:00:00Z',
        resolved: false,
        replies: [
            { id: 'reply_12', author: 'usr_5', text: 'Current: EN, ES, FR, DE, JA, KO, ZH, PT, IT. In progress: AR, HI, TH.', createdAt: '2026-03-16T14:30:00Z' },
            { id: 'reply_13', author: 'usr_1', text: 'Good call. I will change it to "9 languages (12 by GA)" to be accurate.', createdAt: '2026-03-16T15:00:00Z' }
        ]
    },
    {
        id: 'cmt_17',
        slideId: 'slide_14',
        elementId: 'el_s14_4',
        author: 'usr_2',
        text: 'Do we have enough UX researchers? With 2 new hires we would still be at 4 total, supporting 100+ people.',
        createdAt: '2026-03-17T09:00:00Z',
        resolved: false,
        replies: []
    },
    {
        id: 'cmt_18',
        slideId: 'slide_7',
        elementId: 'el_s7_4',
        author: 'usr_3',
        text: 'Can we quantify "99.9% uptime"? That is 8.76 hours of downtime per year. Actual was 2.3 hours last year.',
        createdAt: '2026-03-17T10:30:00Z',
        resolved: false,
        replies: []
    }
];

function getSeedData() {
    return {
        presentation: JSON.parse(JSON.stringify(PRESENTATION)),
        slides: JSON.parse(JSON.stringify(SLIDES)),
        templates: JSON.parse(JSON.stringify(TEMPLATES)),
        comments: JSON.parse(JSON.stringify(COMMENTS)),
        users: JSON.parse(JSON.stringify(USERS)),
        currentUser: JSON.parse(JSON.stringify(CURRENT_USER)),
        themes: JSON.parse(JSON.stringify(THEMES)),
        fontFamilies: [...FONT_FAMILIES],
        fontSizes: [...FONT_SIZES],
        transitionTypes: [...TRANSITION_TYPES],
        animationTypes: [...ANIMATION_TYPES],
        shapeTypes: [...SHAPE_TYPES],
        elementColors: [...ELEMENT_COLORS],
        _nextElementId: 200,
        _nextSlideId: 20,
        _nextCommentId: 20,
        _nextReplyId: 20,
        _seedVersion: SEED_DATA_VERSION
    };
}
