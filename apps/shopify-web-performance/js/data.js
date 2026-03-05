// ============================================================
// data.js — Rich, realistic seed data for Shopify Web Performance Dashboard
// ============================================================
const SEED_DATA_VERSION = 1;

// ---- Current Store ----
const STORE_INFO = {
    id: 'store_4827',
    name: 'Evergreen Outdoor Co.',
    domain: 'evergreen-outdoor.myshopify.com',
    customDomain: 'www.evergreenoutdoor.com',
    plan: 'Shopify Plus',
    currency: 'USD',
    timezone: 'America/New_York',
    passwordProtected: false,
    createdAt: '2022-03-15T14:22:00Z'
};

// ---- Current User ----
const CURRENT_USER = {
    id: 'user_1',
    name: 'Jordan Mitchell',
    email: 'jordan@evergreenoutdoor.com',
    role: 'Store Owner',
    avatarColor: '#5c6ac4'
};

// ---- Themes ----
const THEMES = [
    {
        id: 'theme_001',
        name: 'Horizon - Outdoors',
        role: 'main',
        version: '14.2.0',
        developer: 'Shopify',
        family: 'Horizon',
        isOnlineStore2: true,
        isOptimized: true,
        installedAt: '2025-11-10T09:30:00Z',
        updatedAt: '2026-02-18T11:00:00Z',
        sectionsPerPage: { home: 12, product: 8, collection: 6, cart: 4, blog: 5 },
        hasPageTransitions: false,
        hasAnimations: true,
        status: 'published'
    },
    {
        id: 'theme_002',
        name: 'Dawn (backup)',
        role: 'unpublished',
        version: '12.0.0',
        developer: 'Shopify',
        family: 'Dawn',
        isOnlineStore2: true,
        isOptimized: true,
        installedAt: '2024-06-01T10:00:00Z',
        updatedAt: '2025-08-12T14:00:00Z',
        sectionsPerPage: { home: 8, product: 6, collection: 5, cart: 3, blog: 4 },
        hasPageTransitions: false,
        hasAnimations: false,
        status: 'unpublished'
    },
    {
        id: 'theme_003',
        name: 'Prestige',
        role: 'unpublished',
        version: '9.1.3',
        developer: 'Maestrooo',
        family: 'Prestige',
        isOnlineStore2: true,
        isOptimized: false,
        installedAt: '2024-01-20T08:00:00Z',
        updatedAt: '2025-04-10T16:00:00Z',
        sectionsPerPage: { home: 18, product: 12, collection: 9, cart: 5, blog: 7 },
        hasPageTransitions: true,
        hasAnimations: true,
        status: 'unpublished'
    }
];

// ---- Installed Apps ----
const APPS = [
    {
        id: 'app_001',
        name: 'Klaviyo: Email Marketing & SMS',
        developer: 'Klaviyo',
        category: 'marketing',
        installedAt: '2023-04-12T10:00:00Z',
        status: 'active',
        performanceImpact: 'moderate',
        estimatedLcpImpact: 320,
        estimatedInpImpact: 45,
        loadsOnStorefront: true,
        scriptsCount: 3,
        description: 'Email marketing automation and SMS campaigns'
    },
    {
        id: 'app_002',
        name: 'Judge.me Product Reviews',
        developer: 'Judge.me',
        category: 'social-proof',
        installedAt: '2023-06-20T14:00:00Z',
        status: 'active',
        performanceImpact: 'low',
        estimatedLcpImpact: 80,
        estimatedInpImpact: 15,
        loadsOnStorefront: true,
        scriptsCount: 1,
        description: 'Product reviews and star ratings widget'
    },
    {
        id: 'app_003',
        name: 'Google Analytics (GA4)',
        developer: 'Google',
        category: 'analytics',
        installedAt: '2022-03-16T10:00:00Z',
        status: 'active',
        performanceImpact: 'moderate',
        estimatedLcpImpact: 150,
        estimatedInpImpact: 60,
        loadsOnStorefront: true,
        scriptsCount: 2,
        description: 'Website analytics and conversion tracking'
    },
    {
        id: 'app_004',
        name: 'Meta Pixel & Conversions API',
        developer: 'Meta',
        category: 'analytics',
        installedAt: '2023-01-08T09:00:00Z',
        status: 'active',
        performanceImpact: 'moderate',
        estimatedLcpImpact: 200,
        estimatedInpImpact: 55,
        loadsOnStorefront: true,
        scriptsCount: 2,
        description: 'Facebook/Instagram ad tracking and retargeting'
    },
    {
        id: 'app_005',
        name: 'Shopify Inbox',
        developer: 'Shopify',
        category: 'customer-support',
        installedAt: '2023-09-14T11:00:00Z',
        status: 'active',
        performanceImpact: 'low',
        estimatedLcpImpact: 60,
        estimatedInpImpact: 20,
        loadsOnStorefront: true,
        scriptsCount: 1,
        description: 'Live chat widget for customer support'
    },
    {
        id: 'app_006',
        name: 'Recharge Subscriptions',
        developer: 'Recharge',
        category: 'subscriptions',
        installedAt: '2024-02-10T13:00:00Z',
        status: 'active',
        performanceImpact: 'high',
        estimatedLcpImpact: 450,
        estimatedInpImpact: 80,
        loadsOnStorefront: true,
        scriptsCount: 4,
        description: 'Subscription billing and recurring orders'
    },
    {
        id: 'app_007',
        name: 'Privy ‑ Pop Ups, Email, & SMS',
        developer: 'Privy',
        category: 'marketing',
        installedAt: '2024-05-01T08:00:00Z',
        status: 'active',
        performanceImpact: 'high',
        estimatedLcpImpact: 380,
        estimatedInpImpact: 95,
        loadsOnStorefront: true,
        scriptsCount: 3,
        description: 'Pop-up modals, banners, and email capture'
    },
    {
        id: 'app_008',
        name: 'Yotpo Loyalty & Rewards',
        developer: 'Yotpo',
        category: 'loyalty',
        installedAt: '2024-08-22T10:00:00Z',
        status: 'active',
        performanceImpact: 'moderate',
        estimatedLcpImpact: 240,
        estimatedInpImpact: 50,
        loadsOnStorefront: true,
        scriptsCount: 2,
        description: 'Loyalty points and referral program'
    },
    {
        id: 'app_009',
        name: 'Hotjar Heatmaps & Recordings',
        developer: 'Hotjar',
        category: 'analytics',
        installedAt: '2025-01-15T09:00:00Z',
        status: 'active',
        performanceImpact: 'high',
        estimatedLcpImpact: 350,
        estimatedInpImpact: 110,
        loadsOnStorefront: true,
        scriptsCount: 2,
        description: 'Heatmaps, session recordings, and user feedback'
    },
    {
        id: 'app_010',
        name: 'Shippo - Shipping Labels',
        developer: 'Shippo',
        category: 'shipping',
        installedAt: '2023-07-05T12:00:00Z',
        status: 'active',
        performanceImpact: 'none',
        estimatedLcpImpact: 0,
        estimatedInpImpact: 0,
        loadsOnStorefront: false,
        scriptsCount: 0,
        description: 'Shipping labels and rate comparison'
    },
    {
        id: 'app_011',
        name: 'Bold Product Options',
        developer: 'Bold Commerce',
        category: 'product',
        installedAt: '2024-11-03T15:00:00Z',
        status: 'active',
        performanceImpact: 'moderate',
        estimatedLcpImpact: 180,
        estimatedInpImpact: 70,
        loadsOnStorefront: true,
        scriptsCount: 2,
        description: 'Custom product options and variant swatches'
    },
    {
        id: 'app_012',
        name: 'TikTok Channel',
        developer: 'TikTok',
        category: 'sales-channel',
        installedAt: '2025-06-10T08:00:00Z',
        status: 'active',
        performanceImpact: 'moderate',
        estimatedLcpImpact: 260,
        estimatedInpImpact: 40,
        loadsOnStorefront: true,
        scriptsCount: 2,
        description: 'TikTok shopping and ad pixel integration'
    },
    {
        id: 'app_013',
        name: 'SEO Manager',
        developer: 'venntov',
        category: 'seo',
        installedAt: '2023-11-28T10:00:00Z',
        status: 'disabled',
        performanceImpact: 'low',
        estimatedLcpImpact: 40,
        estimatedInpImpact: 10,
        loadsOnStorefront: false,
        scriptsCount: 0,
        description: 'SEO optimization and structured data management'
    },
    {
        id: 'app_014',
        name: 'Infinite Options',
        developer: 'ShopPad',
        category: 'product',
        installedAt: '2024-03-18T14:00:00Z',
        status: 'disabled',
        performanceImpact: 'moderate',
        estimatedLcpImpact: 190,
        estimatedInpImpact: 65,
        loadsOnStorefront: false,
        scriptsCount: 0,
        description: 'Unlimited custom product options (disabled)'
    },
    {
        id: 'app_015',
        name: 'Back in Stock Alerts',
        developer: 'Swym',
        category: 'marketing',
        installedAt: '2025-09-02T11:00:00Z',
        status: 'active',
        performanceImpact: 'low',
        estimatedLcpImpact: 50,
        estimatedInpImpact: 15,
        loadsOnStorefront: true,
        scriptsCount: 1,
        description: 'Notify customers when out-of-stock items return'
    }
];

// ---- Tag Manager Tags ----
const TAG_MANAGER_TAGS = [
    { id: 'tag_001', name: 'Google Analytics 4', status: 'active', category: 'analytics', fireRate: 'all-pages', addedAt: '2022-03-16T10:00:00Z' },
    { id: 'tag_002', name: 'Meta Pixel', status: 'active', category: 'advertising', fireRate: 'all-pages', addedAt: '2023-01-08T09:00:00Z' },
    { id: 'tag_003', name: 'Google Ads Conversion', status: 'active', category: 'advertising', fireRate: 'checkout-only', addedAt: '2023-05-20T08:00:00Z' },
    { id: 'tag_004', name: 'TikTok Pixel', status: 'active', category: 'advertising', fireRate: 'all-pages', addedAt: '2025-06-10T08:00:00Z' },
    { id: 'tag_005', name: 'Hotjar Tracking', status: 'active', category: 'analytics', fireRate: 'all-pages', addedAt: '2025-01-15T09:00:00Z' },
    { id: 'tag_006', name: 'Pinterest Tag', status: 'inactive', category: 'advertising', fireRate: 'all-pages', addedAt: '2024-04-12T10:00:00Z' },
    { id: 'tag_007', name: 'Snapchat Pixel', status: 'inactive', category: 'advertising', fireRate: 'all-pages', addedAt: '2024-07-30T11:00:00Z' },
    { id: 'tag_008', name: 'Microsoft Clarity', status: 'active', category: 'analytics', fireRate: 'all-pages', addedAt: '2025-10-05T12:00:00Z' },
    { id: 'tag_009', name: 'Affirm Messaging', status: 'active', category: 'payments', fireRate: 'product-pages', addedAt: '2025-03-22T14:00:00Z' },
    { id: 'tag_010', name: 'Lucky Orange', status: 'inactive', category: 'analytics', fireRate: 'all-pages', addedAt: '2024-09-15T09:00:00Z' }
];

// ---- Page Types ----
const PAGE_TYPES = [
    { id: 'home', name: 'Home', urlPattern: '/' },
    { id: 'product', name: 'Product', urlPattern: '/products/*' },
    { id: 'collection', name: 'Collection', urlPattern: '/collections/*' },
    { id: 'cart', name: 'Cart', urlPattern: '/cart' },
    { id: 'blog', name: 'Blog', urlPattern: '/blogs/*' },
    { id: 'page', name: 'Page', urlPattern: '/pages/*' },
    { id: 'search', name: 'Search', urlPattern: '/search' },
    { id: 'account', name: 'Account', urlPattern: '/account/*' },
    { id: 'checkout', name: 'Checkout', urlPattern: '/checkouts/*' }
];

// ---- Store Pages (individual URLs tracked) ----
const PAGES = [
    { id: 'page_001', url: '/', title: 'Home', pageType: 'home', visits30d: 48720, visits7d: 11430, visitsToday: 1587 },
    { id: 'page_002', url: '/products/alpine-pro-hiking-boots', title: 'Alpine Pro Hiking Boots', pageType: 'product', visits30d: 12840, visits7d: 3210, visitsToday: 445 },
    { id: 'page_003', url: '/products/summit-down-jacket', title: 'Summit Down Jacket', pageType: 'product', visits30d: 9650, visits7d: 2412, visitsToday: 338 },
    { id: 'page_004', url: '/products/trail-runner-x2', title: 'Trail Runner X2 Shoes', pageType: 'product', visits30d: 8230, visits7d: 2057, visitsToday: 290 },
    { id: 'page_005', url: '/products/basecamp-tent-4p', title: 'BaseCamp 4-Person Tent', pageType: 'product', visits30d: 7180, visits7d: 1795, visitsToday: 252 },
    { id: 'page_006', url: '/products/evergreen-water-bottle-32oz', title: 'Evergreen Water Bottle 32oz', pageType: 'product', visits30d: 5420, visits7d: 1355, visitsToday: 189 },
    { id: 'page_007', url: '/products/ultralight-backpack-65l', title: 'Ultralight Backpack 65L', pageType: 'product', visits30d: 6890, visits7d: 1722, visitsToday: 240 },
    { id: 'page_008', url: '/products/merino-base-layer', title: 'Merino Wool Base Layer', pageType: 'product', visits30d: 4100, visits7d: 1025, visitsToday: 143 },
    { id: 'page_009', url: '/products/solar-lantern-pro', title: 'Solar Lantern Pro', pageType: 'product', visits30d: 3250, visits7d: 812, visitsToday: 112 },
    { id: 'page_010', url: '/products/compass-navigator-elite', title: 'Compass Navigator Elite', pageType: 'product', visits30d: 1890, visits7d: 472, visitsToday: 65 },
    { id: 'page_011', url: '/products/trekking-poles-carbon', title: 'Carbon Trekking Poles', pageType: 'product', visits30d: 2730, visits7d: 682, visitsToday: 95 },
    { id: 'page_012', url: '/products/rain-shell-packable', title: 'Packable Rain Shell', pageType: 'product', visits30d: 3890, visits7d: 972, visitsToday: 135 },
    { id: 'page_013', url: '/products/camp-stove-ultralite', title: 'Camp Stove UltraLite', pageType: 'product', visits30d: 2150, visits7d: 537, visitsToday: 74 },
    { id: 'page_014', url: '/products/sleeping-bag-0f', title: 'Zero-Degree Sleeping Bag', pageType: 'product', visits30d: 4560, visits7d: 1140, visitsToday: 158 },
    { id: 'page_015', url: '/products/headlamp-400lm', title: 'Headlamp 400 Lumen', pageType: 'product', visits30d: 1650, visits7d: 412, visitsToday: 56 },
    { id: 'page_016', url: '/collections/hiking-footwear', title: 'Hiking Footwear', pageType: 'collection', visits30d: 15200, visits7d: 3800, visitsToday: 530 },
    { id: 'page_017', url: '/collections/camping-gear', title: 'Camping Gear', pageType: 'collection', visits30d: 11340, visits7d: 2835, visitsToday: 395 },
    { id: 'page_018', url: '/collections/winter-essentials', title: 'Winter Essentials', pageType: 'collection', visits30d: 9870, visits7d: 2467, visitsToday: 343 },
    { id: 'page_019', url: '/collections/backpacks', title: 'Backpacks', pageType: 'collection', visits30d: 7620, visits7d: 1905, visitsToday: 265 },
    { id: 'page_020', url: '/collections/sale', title: 'Sale Items', pageType: 'collection', visits30d: 13450, visits7d: 3362, visitsToday: 468 },
    { id: 'page_021', url: '/collections/new-arrivals', title: 'New Arrivals', pageType: 'collection', visits30d: 8940, visits7d: 2235, visitsToday: 311 },
    { id: 'page_022', url: '/collections/accessories', title: 'Accessories', pageType: 'collection', visits30d: 5670, visits7d: 1417, visitsToday: 197 },
    { id: 'page_023', url: '/collections/lighting', title: 'Lighting', pageType: 'collection', visits30d: 2340, visits7d: 585, visitsToday: 81 },
    { id: 'page_024', url: '/cart', title: 'Shopping Cart', pageType: 'cart', visits30d: 22100, visits7d: 5525, visitsToday: 768 },
    { id: 'page_025', url: '/blogs/trail-talk', title: 'Trail Talk Blog', pageType: 'blog', visits30d: 6780, visits7d: 1695, visitsToday: 235 },
    { id: 'page_026', url: '/blogs/trail-talk/winter-hiking-tips', title: 'Winter Hiking Tips', pageType: 'blog', visits30d: 3420, visits7d: 855, visitsToday: 118 },
    { id: 'page_027', url: '/blogs/trail-talk/gear-maintenance-guide', title: 'Gear Maintenance Guide', pageType: 'blog', visits30d: 2180, visits7d: 545, visitsToday: 75 },
    { id: 'page_028', url: '/pages/about-us', title: 'About Us', pageType: 'page', visits30d: 4230, visits7d: 1057, visitsToday: 147 },
    { id: 'page_029', url: '/pages/contact', title: 'Contact Us', pageType: 'page', visits30d: 1890, visits7d: 472, visitsToday: 65 },
    { id: 'page_030', url: '/pages/size-guide', title: 'Size Guide', pageType: 'page', visits30d: 5670, visits7d: 1417, visitsToday: 197 },
    { id: 'page_031', url: '/pages/shipping-policy', title: 'Shipping Policy', pageType: 'page', visits30d: 3150, visits7d: 787, visitsToday: 109 },
    { id: 'page_032', url: '/pages/returns', title: 'Returns & Exchanges', pageType: 'page', visits30d: 2480, visits7d: 620, visitsToday: 86 },
    { id: 'page_033', url: '/search', title: 'Search Results', pageType: 'search', visits30d: 9870, visits7d: 2467, visitsToday: 343 },
    { id: 'page_034', url: '/account/login', title: 'Account Login', pageType: 'account', visits30d: 7230, visits7d: 1807, visitsToday: 251 },
    { id: 'page_035', url: '/account', title: 'My Account', pageType: 'account', visits30d: 4560, visits7d: 1140, visitsToday: 158 },
    { id: 'page_036', url: '/products/fleece-hoodie-recycled', title: 'Recycled Fleece Hoodie', pageType: 'product', visits30d: 5890, visits7d: 1472, visitsToday: 204 },
    { id: 'page_037', url: '/products/climbing-harness-pro', title: 'Climbing Harness Pro', pageType: 'product', visits30d: 1230, visits7d: 307, visitsToday: 42 },
    { id: 'page_038', url: '/products/insulated-mug-camp', title: 'Insulated Camp Mug', pageType: 'product', visits30d: 980, visits7d: 245, visitsToday: 34 },
    { id: 'page_039', url: '/collections/climbing', title: 'Climbing Gear', pageType: 'collection', visits30d: 3450, visits7d: 862, visitsToday: 120 },
    { id: 'page_040', url: '/blogs/trail-talk/best-national-parks-2026', title: 'Best National Parks 2026', pageType: 'blog', visits30d: 8920, visits7d: 2230, visitsToday: 310 }
];

// ---- Helper: Generate realistic time-series performance data ----
function _generateDailyData(days, baseValue, variance, trend, spikes) {
    const data = [];
    const now = new Date('2026-03-02T00:00:00Z');
    for (let i = days - 1; i >= 0; i--) {
        const date = new Date(now);
        date.setDate(date.getDate() - i);
        const dateStr = date.toISOString().split('T')[0];
        // Add trend
        let value = baseValue + (trend * (days - i) / days);
        // Add variance
        value += (Math.sin(i * 0.7) * variance * 0.4) + ((i % 7 === 0 ? 1 : 0) * variance * 0.3);
        // Add spikes
        for (const spike of spikes) {
            if (i === spike.day) value += spike.amount;
        }
        // Add some noise
        value += (Math.sin(i * 2.3 + 1.7) * variance * 0.2);
        data.push({ date: dateStr, value: Math.max(0, Math.round(value)) });
    }
    return data;
}

function _generateClsData(days, baseValue, variance, trend, spikes) {
    const data = [];
    const now = new Date('2026-03-02T00:00:00Z');
    for (let i = days - 1; i >= 0; i--) {
        const date = new Date(now);
        date.setDate(date.getDate() - i);
        const dateStr = date.toISOString().split('T')[0];
        let value = baseValue + (trend * (days - i) / days);
        value += (Math.sin(i * 0.7) * variance * 0.4);
        for (const spike of spikes) {
            if (i === spike.day) value += spike.amount;
        }
        value += (Math.sin(i * 2.3 + 1.7) * variance * 0.15);
        data.push({ date: dateStr, value: Math.max(0, parseFloat(value.toFixed(3))) });
    }
    return data;
}

// ---- Performance Data: Over Time (30 days) ----
// LCP data (milliseconds) — baseline ~2200ms with some spikes
const LCP_OVER_TIME_DESKTOP = _generateDailyData(30, 1850, 300, 150, [
    { day: 22, amount: 600 },  // spike from app install
    { day: 15, amount: -200 }, // improvement from optimization
    { day: 5, amount: 400 }    // spike from new sections
]);

const LCP_OVER_TIME_MOBILE = _generateDailyData(30, 2800, 500, 200, [
    { day: 22, amount: 900 },
    { day: 15, amount: -350 },
    { day: 5, amount: 650 }
]);

// INP data (milliseconds) — baseline ~150ms
const INP_OVER_TIME_DESKTOP = _generateDailyData(30, 120, 40, 30, [
    { day: 22, amount: 80 },
    { day: 10, amount: 50 }
]);

const INP_OVER_TIME_MOBILE = _generateDailyData(30, 210, 60, 40, [
    { day: 22, amount: 120 },
    { day: 10, amount: 70 }
]);

// CLS data (score) — baseline ~0.08
const CLS_OVER_TIME_DESKTOP = _generateClsData(30, 0.06, 0.03, 0.02, [
    { day: 18, amount: 0.08 },
    { day: 8, amount: -0.02 }
]);

const CLS_OVER_TIME_MOBILE = _generateClsData(30, 0.11, 0.05, 0.03, [
    { day: 18, amount: 0.12 },
    { day: 8, amount: -0.03 }
]);

// ---- Performance Data: By Page ----
// Each page has performance metrics for both desktop and mobile
function _pagePerf(lcpDesktop, lcpMobile, inpDesktop, inpMobile, clsDesktop, clsMobile, distLcp, distInp, distCls) {
    return {
        desktop: {
            lcp: { p75: lcpDesktop, distribution: distLcp.desktop },
            inp: { p75: inpDesktop, distribution: distInp.desktop },
            cls: { p75: clsDesktop, distribution: distCls.desktop }
        },
        mobile: {
            lcp: { p75: lcpMobile, distribution: distLcp.mobile },
            inp: { p75: inpMobile, distribution: distInp.mobile },
            cls: { p75: clsMobile, distribution: distCls.mobile }
        }
    };
}

const PAGE_PERFORMANCE = {
    'page_001': _pagePerf(1920, 3100, 130, 220, 0.05, 0.12,
        { desktop: { good: 68, moderate: 22, poor: 10 }, mobile: { good: 42, moderate: 35, poor: 23 } },
        { desktop: { good: 82, moderate: 14, poor: 4 }, mobile: { good: 60, moderate: 28, poor: 12 } },
        { desktop: { good: 90, moderate: 8, poor: 2 }, mobile: { good: 72, moderate: 20, poor: 8 } }),
    'page_002': _pagePerf(1650, 2600, 110, 185, 0.04, 0.09,
        { desktop: { good: 78, moderate: 16, poor: 6 }, mobile: { good: 55, moderate: 30, poor: 15 } },
        { desktop: { good: 88, moderate: 10, poor: 2 }, mobile: { good: 68, moderate: 24, poor: 8 } },
        { desktop: { good: 92, moderate: 6, poor: 2 }, mobile: { good: 80, moderate: 15, poor: 5 } }),
    'page_003': _pagePerf(1780, 2850, 125, 210, 0.06, 0.11,
        { desktop: { good: 72, moderate: 20, poor: 8 }, mobile: { good: 48, moderate: 32, poor: 20 } },
        { desktop: { good: 84, moderate: 12, poor: 4 }, mobile: { good: 62, moderate: 26, poor: 12 } },
        { desktop: { good: 88, moderate: 9, poor: 3 }, mobile: { good: 74, moderate: 18, poor: 8 } }),
    'page_004': _pagePerf(1580, 2450, 105, 175, 0.03, 0.07,
        { desktop: { good: 80, moderate: 15, poor: 5 }, mobile: { good: 58, moderate: 28, poor: 14 } },
        { desktop: { good: 90, moderate: 8, poor: 2 }, mobile: { good: 72, moderate: 20, poor: 8 } },
        { desktop: { good: 94, moderate: 5, poor: 1 }, mobile: { good: 84, moderate: 12, poor: 4 } }),
    'page_005': _pagePerf(2100, 3400, 140, 245, 0.08, 0.15,
        { desktop: { good: 62, moderate: 26, poor: 12 }, mobile: { good: 38, moderate: 36, poor: 26 } },
        { desktop: { good: 78, moderate: 16, poor: 6 }, mobile: { good: 52, moderate: 32, poor: 16 } },
        { desktop: { good: 85, moderate: 11, poor: 4 }, mobile: { good: 65, moderate: 24, poor: 11 } }),
    'page_006': _pagePerf(1450, 2300, 95, 165, 0.03, 0.06,
        { desktop: { good: 82, moderate: 14, poor: 4 }, mobile: { good: 62, moderate: 26, poor: 12 } },
        { desktop: { good: 92, moderate: 6, poor: 2 }, mobile: { good: 75, moderate: 18, poor: 7 } },
        { desktop: { good: 95, moderate: 4, poor: 1 }, mobile: { good: 88, moderate: 9, poor: 3 } }),
    'page_007': _pagePerf(1820, 2900, 128, 215, 0.05, 0.10,
        { desktop: { good: 71, moderate: 20, poor: 9 }, mobile: { good: 46, moderate: 33, poor: 21 } },
        { desktop: { good: 83, moderate: 13, poor: 4 }, mobile: { good: 61, moderate: 27, poor: 12 } },
        { desktop: { good: 90, moderate: 7, poor: 3 }, mobile: { good: 76, moderate: 17, poor: 7 } }),
    'page_016': _pagePerf(2250, 3600, 155, 260, 0.09, 0.18,
        { desktop: { good: 58, moderate: 28, poor: 14 }, mobile: { good: 35, moderate: 38, poor: 27 } },
        { desktop: { good: 74, moderate: 18, poor: 8 }, mobile: { good: 48, moderate: 34, poor: 18 } },
        { desktop: { good: 82, moderate: 13, poor: 5 }, mobile: { good: 60, moderate: 27, poor: 13 } }),
    'page_017': _pagePerf(2100, 3350, 145, 240, 0.07, 0.14,
        { desktop: { good: 63, moderate: 25, poor: 12 }, mobile: { good: 40, moderate: 35, poor: 25 } },
        { desktop: { good: 76, moderate: 17, poor: 7 }, mobile: { good: 54, moderate: 30, poor: 16 } },
        { desktop: { good: 86, moderate: 10, poor: 4 }, mobile: { good: 68, moderate: 22, poor: 10 } }),
    'page_018': _pagePerf(2180, 3500, 150, 250, 0.08, 0.16,
        { desktop: { good: 60, moderate: 27, poor: 13 }, mobile: { good: 37, moderate: 37, poor: 26 } },
        { desktop: { good: 75, moderate: 17, poor: 8 }, mobile: { good: 50, moderate: 33, poor: 17 } },
        { desktop: { good: 84, moderate: 12, poor: 4 }, mobile: { good: 63, moderate: 25, poor: 12 } }),
    'page_020': _pagePerf(2350, 3750, 160, 270, 0.10, 0.19,
        { desktop: { good: 55, moderate: 30, poor: 15 }, mobile: { good: 32, moderate: 39, poor: 29 } },
        { desktop: { good: 72, moderate: 19, poor: 9 }, mobile: { good: 45, moderate: 35, poor: 20 } },
        { desktop: { good: 80, moderate: 14, poor: 6 }, mobile: { good: 58, moderate: 28, poor: 14 } }),
    'page_024': _pagePerf(1350, 2100, 88, 155, 0.02, 0.05,
        { desktop: { good: 85, moderate: 12, poor: 3 }, mobile: { good: 65, moderate: 24, poor: 11 } },
        { desktop: { good: 93, moderate: 5, poor: 2 }, mobile: { good: 78, moderate: 16, poor: 6 } },
        { desktop: { good: 96, moderate: 3, poor: 1 }, mobile: { good: 90, moderate: 8, poor: 2 } }),
    'page_025': _pagePerf(1680, 2650, 115, 190, 0.04, 0.08,
        { desktop: { good: 76, moderate: 17, poor: 7 }, mobile: { good: 53, moderate: 31, poor: 16 } },
        { desktop: { good: 87, moderate: 10, poor: 3 }, mobile: { good: 67, moderate: 24, poor: 9 } },
        { desktop: { good: 93, moderate: 5, poor: 2 }, mobile: { good: 82, moderate: 13, poor: 5 } }),
    'page_033': _pagePerf(1950, 3150, 135, 225, 0.06, 0.13,
        { desktop: { good: 67, moderate: 22, poor: 11 }, mobile: { good: 44, moderate: 34, poor: 22 } },
        { desktop: { good: 81, moderate: 14, poor: 5 }, mobile: { good: 58, moderate: 29, poor: 13 } },
        { desktop: { good: 89, moderate: 8, poor: 3 }, mobile: { good: 70, moderate: 21, poor: 9 } }),
    'page_040': _pagePerf(1550, 2400, 100, 170, 0.03, 0.07,
        { desktop: { good: 79, moderate: 16, poor: 5 }, mobile: { good: 57, moderate: 29, poor: 14 } },
        { desktop: { good: 91, moderate: 7, poor: 2 }, mobile: { good: 73, moderate: 19, poor: 8 } },
        { desktop: { good: 94, moderate: 4, poor: 2 }, mobile: { good: 85, moderate: 11, poor: 4 } })
};

// Fill remaining pages with generated performance data
for (const page of PAGES) {
    if (!PAGE_PERFORMANCE[page.id]) {
        const isHighTraffic = page.visits30d > 5000;
        const baseLcp = isHighTraffic ? 1700 + Math.floor(Math.random() * 600) : 1500 + Math.floor(Math.random() * 800);
        const mobileMultiplier = 1.5 + Math.random() * 0.3;
        PAGE_PERFORMANCE[page.id] = _pagePerf(
            baseLcp, Math.round(baseLcp * mobileMultiplier),
            90 + Math.floor(Math.random() * 60), Math.round((90 + Math.floor(Math.random() * 60)) * mobileMultiplier),
            parseFloat((0.02 + Math.random() * 0.08).toFixed(3)), parseFloat((0.05 + Math.random() * 0.15).toFixed(3)),
            { desktop: { good: 65 + Math.floor(Math.random() * 20), moderate: 15 + Math.floor(Math.random() * 10), poor: 5 + Math.floor(Math.random() * 10) },
              mobile: { good: 40 + Math.floor(Math.random() * 25), moderate: 25 + Math.floor(Math.random() * 15), poor: 10 + Math.floor(Math.random() * 15) } },
            { desktop: { good: 75 + Math.floor(Math.random() * 15), moderate: 10 + Math.floor(Math.random() * 10), poor: 2 + Math.floor(Math.random() * 5) },
              mobile: { good: 55 + Math.floor(Math.random() * 20), moderate: 20 + Math.floor(Math.random() * 10), poor: 5 + Math.floor(Math.random() * 10) } },
            { desktop: { good: 85 + Math.floor(Math.random() * 10), moderate: 5 + Math.floor(Math.random() * 8), poor: 1 + Math.floor(Math.random() * 4) },
              mobile: { good: 65 + Math.floor(Math.random() * 20), moderate: 15 + Math.floor(Math.random() * 10), poor: 3 + Math.floor(Math.random() * 10) } }
        );
    }
}

// ---- Performance by Page Type (aggregate) ----
const PAGE_TYPE_PERFORMANCE = {
    home: _pagePerf(1920, 3100, 130, 220, 0.05, 0.12,
        { desktop: { good: 68, moderate: 22, poor: 10 }, mobile: { good: 42, moderate: 35, poor: 23 } },
        { desktop: { good: 82, moderate: 14, poor: 4 }, mobile: { good: 60, moderate: 28, poor: 12 } },
        { desktop: { good: 90, moderate: 8, poor: 2 }, mobile: { good: 72, moderate: 20, poor: 8 } }),
    product: _pagePerf(1750, 2780, 118, 200, 0.05, 0.10,
        { desktop: { good: 74, moderate: 18, poor: 8 }, mobile: { good: 50, moderate: 32, poor: 18 } },
        { desktop: { good: 86, moderate: 11, poor: 3 }, mobile: { good: 65, moderate: 25, poor: 10 } },
        { desktop: { good: 91, moderate: 7, poor: 2 }, mobile: { good: 78, moderate: 15, poor: 7 } }),
    collection: _pagePerf(2200, 3520, 152, 255, 0.08, 0.16,
        { desktop: { good: 59, moderate: 27, poor: 14 }, mobile: { good: 36, moderate: 37, poor: 27 } },
        { desktop: { good: 74, moderate: 18, poor: 8 }, mobile: { good: 50, moderate: 33, poor: 17 } },
        { desktop: { good: 83, moderate: 12, poor: 5 }, mobile: { good: 62, moderate: 26, poor: 12 } }),
    cart: _pagePerf(1350, 2100, 88, 155, 0.02, 0.05,
        { desktop: { good: 85, moderate: 12, poor: 3 }, mobile: { good: 65, moderate: 24, poor: 11 } },
        { desktop: { good: 93, moderate: 5, poor: 2 }, mobile: { good: 78, moderate: 16, poor: 6 } },
        { desktop: { good: 96, moderate: 3, poor: 1 }, mobile: { good: 90, moderate: 8, poor: 2 } }),
    blog: _pagePerf(1620, 2550, 108, 185, 0.04, 0.08,
        { desktop: { good: 77, moderate: 17, poor: 6 }, mobile: { good: 55, moderate: 30, poor: 15 } },
        { desktop: { good: 88, moderate: 9, poor: 3 }, mobile: { good: 68, moderate: 23, poor: 9 } },
        { desktop: { good: 93, moderate: 5, poor: 2 }, mobile: { good: 82, moderate: 13, poor: 5 } }),
    page: _pagePerf(1480, 2350, 98, 170, 0.03, 0.06,
        { desktop: { good: 81, moderate: 14, poor: 5 }, mobile: { good: 60, moderate: 27, poor: 13 } },
        { desktop: { good: 91, moderate: 7, poor: 2 }, mobile: { good: 73, moderate: 19, poor: 8 } },
        { desktop: { good: 95, moderate: 4, poor: 1 }, mobile: { good: 87, moderate: 10, poor: 3 } }),
    search: _pagePerf(1950, 3150, 135, 225, 0.06, 0.13,
        { desktop: { good: 67, moderate: 22, poor: 11 }, mobile: { good: 44, moderate: 34, poor: 22 } },
        { desktop: { good: 81, moderate: 14, poor: 5 }, mobile: { good: 58, moderate: 29, poor: 13 } },
        { desktop: { good: 89, moderate: 8, poor: 3 }, mobile: { good: 70, moderate: 21, poor: 9 } }),
    account: _pagePerf(1380, 2200, 92, 160, 0.02, 0.05,
        { desktop: { good: 84, moderate: 12, poor: 4 }, mobile: { good: 63, moderate: 25, poor: 12 } },
        { desktop: { good: 92, moderate: 6, poor: 2 }, mobile: { good: 76, moderate: 17, poor: 7 } },
        { desktop: { good: 96, moderate: 3, poor: 1 }, mobile: { good: 89, moderate: 8, poor: 3 } }),
    checkout: _pagePerf(1250, 1950, 82, 145, 0.02, 0.04,
        { desktop: { good: 88, moderate: 10, poor: 2 }, mobile: { good: 70, moderate: 22, poor: 8 } },
        { desktop: { good: 94, moderate: 4, poor: 2 }, mobile: { good: 80, moderate: 14, poor: 6 } },
        { desktop: { good: 97, moderate: 2, poor: 1 }, mobile: { good: 92, moderate: 6, poor: 2 } })
};

// ---- Events / Annotations (things that changed and show on timeline) ----
const PERFORMANCE_EVENTS = [
    { id: 'evt_001', date: '2026-02-02', type: 'theme_update', title: 'Theme updated to v14.2.0', description: 'Horizon - Outdoors theme updated from v14.1.2 to v14.2.0', impact: 'positive' },
    { id: 'evt_002', date: '2026-02-05', type: 'app_install', title: 'Hotjar installed', description: 'Hotjar Heatmaps & Recordings app was installed', impact: 'negative' },
    { id: 'evt_003', date: '2026-02-08', type: 'app_install', title: 'Recharge Subscriptions configured', description: 'Recharge subscription widgets added to product pages', impact: 'negative' },
    { id: 'evt_004', date: '2026-02-12', type: 'code_change', title: 'Added hero carousel to homepage', description: '3 new image slides added to homepage hero section', impact: 'negative' },
    { id: 'evt_005', date: '2026-02-15', type: 'optimization', title: 'Image optimization pass', description: 'Compressed and resized 45 product images', impact: 'positive' },
    { id: 'evt_006', date: '2026-02-17', type: 'code_change', title: 'New collection pages created', description: 'Added Winter Essentials and Sale collection pages with 50+ products each', impact: 'negative' },
    { id: 'evt_007', date: '2026-02-20', type: 'app_uninstall', title: 'Lucky Orange removed', description: 'Lucky Orange analytics app was uninstalled', impact: 'positive' },
    { id: 'evt_008', date: '2026-02-22', type: 'app_install', title: 'TikTok Channel installed', description: 'TikTok Channel app installed with pixel tracking', impact: 'negative' },
    { id: 'evt_009', date: '2026-02-25', type: 'theme_change', title: 'Added 4 sections to homepage', description: 'Added Instagram feed, newsletter signup, featured collection, and testimonials sections', impact: 'negative' },
    { id: 'evt_010', date: '2026-02-27', type: 'optimization', title: 'Disabled Pinterest & Snapchat tags', description: 'Deactivated unused advertising pixels in tag manager', impact: 'positive' },
    { id: 'evt_011', date: '2026-02-28', type: 'code_change', title: 'Lazy loading added for reviews', description: 'Judge.me reviews now load on scroll instead of page load', impact: 'positive' },
    { id: 'evt_012', date: '2026-03-01', type: 'app_update', title: 'Klaviyo script updated', description: 'Klaviyo updated their tracking script to a lighter version', impact: 'positive' }
];

// ---- Session Data by Device Type ----
const SESSIONS_BY_DEVICE = {
    last30d: { desktop: 89420, mobile: 142680, tablet: 12340 },
    last7d: { desktop: 21250, mobile: 33870, tablet: 2930 },
    today: { desktop: 2950, mobile: 4700, tablet: 407 }
};

// ---- Overall Performance Score (composite) ----
const OVERALL_PERFORMANCE = {
    score: 72,
    comparisonScore: 68,
    comparisonLabel: 'Similar stores',
    percentile: 62,
    trend: 'improving'
};

// ---- Optimization Recommendations ----
const RECOMMENDATIONS = [
    {
        id: 'rec_001',
        priority: 'high',
        metric: 'lcp',
        title: 'Reduce the impact of third-party scripts',
        description: 'Your store loads 14 third-party scripts that add approximately 2.8 seconds to page load time. Consider removing unused scripts or deferring non-critical ones.',
        category: 'scripts',
        estimatedImprovement: '500-800ms LCP improvement',
        status: 'open',
        affectedPages: ['home', 'product', 'collection']
    },
    {
        id: 'rec_002',
        priority: 'high',
        metric: 'lcp',
        title: 'Optimize large hero images on homepage',
        description: 'The homepage hero carousel contains 3 images averaging 1.2MB each. Resize to appropriate display dimensions and use WebP format.',
        category: 'images',
        estimatedImprovement: '300-500ms LCP improvement',
        status: 'open',
        affectedPages: ['home']
    },
    {
        id: 'rec_003',
        priority: 'medium',
        metric: 'inp',
        title: 'Reduce JavaScript execution on product pages',
        description: 'Recharge Subscriptions and Bold Product Options scripts add ~150ms to interaction responsiveness on product pages.',
        category: 'scripts',
        estimatedImprovement: '50-100ms INP improvement',
        status: 'open',
        affectedPages: ['product']
    },
    {
        id: 'rec_004',
        priority: 'medium',
        metric: 'cls',
        title: 'Set explicit dimensions for product images',
        description: 'Collection pages experience layout shifts when product images load. Set width and height attributes on all product image elements.',
        category: 'layout',
        estimatedImprovement: '0.05-0.10 CLS improvement',
        status: 'open',
        affectedPages: ['collection']
    },
    {
        id: 'rec_005',
        priority: 'medium',
        metric: 'lcp',
        title: 'Evaluate Privy pop-up timing',
        description: 'Privy pop-ups load scripts on every page immediately. Consider delaying the pop-up script until after page load completes.',
        category: 'apps',
        estimatedImprovement: '200-400ms LCP improvement',
        status: 'open',
        affectedPages: ['home', 'product', 'collection']
    },
    {
        id: 'rec_006',
        priority: 'low',
        metric: 'lcp',
        title: 'Enable pagination for large collections',
        description: 'The Sale Items and Hiking Footwear collections load 60+ products at once. Enable pagination to limit initial load to 24 products.',
        category: 'theme',
        estimatedImprovement: '100-300ms LCP improvement',
        status: 'open',
        affectedPages: ['collection']
    },
    {
        id: 'rec_007',
        priority: 'low',
        metric: 'inp',
        title: 'Audit tag manager for unused tags',
        description: 'Your tag manager contains 3 inactive tags (Pinterest, Snapchat, Lucky Orange). While disabled, their configuration still loads. Remove them entirely.',
        category: 'tags',
        estimatedImprovement: '10-30ms INP improvement',
        status: 'resolved',
        affectedPages: ['all']
    },
    {
        id: 'rec_008',
        priority: 'high',
        metric: 'cls',
        title: 'Reserve space for Privy pop-up banner',
        description: 'The Privy email signup banner pushes content down when it appears, causing a layout shift of ~0.15 on mobile. Reserve space or use an overlay instead.',
        category: 'apps',
        estimatedImprovement: '0.10-0.15 CLS improvement',
        status: 'open',
        affectedPages: ['home', 'collection']
    },
    {
        id: 'rec_009',
        priority: 'medium',
        metric: 'lcp',
        title: 'Reduce homepage sections',
        description: 'Your homepage has 12 sections. Pages with fewer sections typically load faster. Consider removing or combining low-engagement sections.',
        category: 'theme',
        estimatedImprovement: '200-400ms LCP improvement',
        status: 'open',
        affectedPages: ['home']
    },
    {
        id: 'rec_010',
        priority: 'low',
        metric: 'cls',
        title: 'Preload web fonts',
        description: 'Custom fonts cause a flash of unstyled text on first load. Preload the primary brand font to reduce CLS.',
        category: 'fonts',
        estimatedImprovement: '0.02-0.05 CLS improvement',
        status: 'open',
        affectedPages: ['all']
    }
];

// ---- Report Definitions ----
const REPORTS = [
    { id: 'report_lcp_time', name: 'Largest Contentful Paint: Over Time', metric: 'lcp', type: 'over_time', unit: 'ms' },
    { id: 'report_inp_time', name: 'Interaction to Next Paint: Over Time', metric: 'inp', type: 'over_time', unit: 'ms' },
    { id: 'report_cls_time', name: 'Cumulative Layout Shift: Over Time', metric: 'cls', type: 'over_time', unit: 'score' },
    { id: 'report_lcp_url', name: 'Largest Contentful Paint: Page URL', metric: 'lcp', type: 'by_page_url', unit: 'ms' },
    { id: 'report_inp_url', name: 'Interaction to Next Paint: Page URL', metric: 'inp', type: 'by_page_url', unit: 'ms' },
    { id: 'report_cls_url', name: 'Cumulative Layout Shift: Page URL', metric: 'cls', type: 'by_page_url', unit: 'score' },
    { id: 'report_lcp_type', name: 'Largest Contentful Paint: Page Type', metric: 'lcp', type: 'by_page_type', unit: 'ms' },
    { id: 'report_inp_type', name: 'Interaction to Next Paint: Page Type', metric: 'inp', type: 'by_page_type', unit: 'ms' },
    { id: 'report_cls_type', name: 'Cumulative Layout Shift: Page Type', metric: 'cls', type: 'by_page_type', unit: 'score' }
];

// ---- Settings / Preferences ----
const SETTINGS = {
    dateRange: 'last_7_days',
    deviceFilter: 'all',
    reportPercentile: 'p75',
    dateGrouping: 'daily',
    showAnnotations: true,
    selectedThemeId: 'theme_001',
    comparisonEnabled: true,
    notificationsEnabled: true,
    performanceAlerts: {
        lcpThreshold: 2500,
        inpThreshold: 200,
        clsThreshold: 0.1,
        alertOnPoor: true,
        alertOnDegradation: true,
        emailAlerts: true,
        degradationPercent: 15
    }
};
