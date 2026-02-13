// ============================================================
// data.js — Rich, realistic mock data for GitLab Organization
// ============================================================

// Bump this version whenever seed data changes to invalidate stale localStorage.
const SEED_DATA_VERSION = 2;

const RESERVED_NAMES = [
    'admin', 'api', 'assets', 'dashboard', 'explore', 'groups',
    'help', 'projects', 'search', 'snippets', 'uploads', 'users',
    'favicon.ico', 'robots.txt', 'sitemap.xml', '-', 'system',
    'public', 'autocomplete', 'issues', 'merge_requests', 'milestones',
    'labels', 'boards', 'wikis', 'environments', 'operations',
    'analytics', 'security', 'ci', 'cd', 'pipelines', 'jobs',
    'artifacts', 'releases', 'packages', 'container_registry',
    'infrastructure', 'terraform', 'clusters', 'integrations',
    'hooks', 'services', 'badges', 'deploy_tokens', 'feature_flags'
];

const ROLES = {
    GUEST: { id: 10, name: 'Guest', label: 'Guest', level: 10 },
    PLANNER: { id: 15, name: 'Planner', label: 'Planner', level: 15 },
    REPORTER: { id: 20, name: 'Reporter', label: 'Reporter', level: 20 },
    DEVELOPER: { id: 30, name: 'Developer', label: 'Developer', level: 30 },
    MAINTAINER: { id: 40, name: 'Maintainer', label: 'Maintainer', level: 40 },
    OWNER: { id: 50, name: 'Owner', label: 'Owner', level: 50 },
    MINIMAL_ACCESS: { id: 5, name: 'Minimal Access', label: 'Minimal Access', level: 5, premium: true }
};

const ROLES_LIST = [
    ROLES.GUEST, ROLES.PLANNER, ROLES.REPORTER,
    ROLES.DEVELOPER, ROLES.MAINTAINER, ROLES.OWNER
];

const VISIBILITY = {
    PRIVATE: { id: 'private', name: 'Private', icon: '🔒', description: 'Only members can see this group/project' },
    INTERNAL: { id: 'internal', name: 'Internal', icon: '🔓', description: 'Any logged-in user can see this group/project' },
    PUBLIC: { id: 'public', name: 'Public', icon: '🌐', description: 'Anyone can see this group/project' }
};

const MEMBERSHIP_TYPES = {
    DIRECT: 'direct',
    INHERITED: 'inherited',
    SHARED: 'shared',
    INHERITED_SHARED: 'inherited_shared'
};

// ---- Current User ----
const CURRENT_USER = {
    id: 1,
    username: 'alex.morgan',
    name: 'Alex Morgan',
    email: 'alex.morgan@example.com',
    secondaryEmails: ['alex.personal@email.com'],
    publicEmail: '',
    commitEmail: 'alex.morgan@example.com',
    privateCommitEmail: '1-alex.morgan@users.noreply.gitlab.com',
    usePrivateCommitEmail: false,
    avatar: null,
    avatarColor: '#6366f1',
    pronouns: 'they/them',
    status: { emoji: '💻', message: 'Coding', busy: false },
    bio: 'Full-stack developer. Open source enthusiast.',
    location: 'San Francisco, CA',
    organization: 'Acme Corp',
    website: 'https://alexmorgan.dev',
    linkedin: 'alexmorgan',
    discord: 'alex.morgan#1234',
    bluesky: '@alex.morgan.bsky.social',
    timezone: 'America/Los_Angeles',
    profileVisibility: 'public',
    createdAt: '2022-03-15T10:30:00Z',
    lastActivityAt: '2025-05-10T14:22:00Z',
    twoFactorEnabled: true,
    following: [2, 3, 5],
    followersCount: 47,
    followingCount: 3
};

// ---- Users ----
const USERS = [
    CURRENT_USER,
    {
        id: 2, username: 'priya.sharma', name: 'Priya Sharma',
        email: 'priya.sharma@example.com', secondaryEmails: [],
        avatar: null, avatarColor: '#ec4899',
        pronouns: 'she/her',
        status: { emoji: '🎯', message: 'In a meeting', busy: true },
        bio: 'Engineering manager with 10+ years experience.',
        location: 'Bangalore, India', organization: 'Acme Corp',
        timezone: 'Asia/Kolkata', profileVisibility: 'public',
        createdAt: '2021-09-01T08:00:00Z', lastActivityAt: '2025-05-10T09:15:00Z',
        twoFactorEnabled: true
    },
    {
        id: 3, username: 'james.chen', name: 'James Chen',
        email: 'james.chen@example.com', secondaryEmails: ['jchen@acme.com'],
        avatar: null, avatarColor: '#14b8a6',
        pronouns: 'he/him',
        status: { emoji: '', message: '', busy: false },
        bio: 'DevOps specialist. Kubernetes & Terraform.',
        location: 'Toronto, Canada', organization: 'Acme Corp',
        timezone: 'America/Toronto', profileVisibility: 'public',
        createdAt: '2022-01-20T12:00:00Z', lastActivityAt: '2025-05-09T17:45:00Z',
        twoFactorEnabled: true
    },
    {
        id: 4, username: 'maria.rodriguez', name: 'Maria Rodriguez',
        email: 'maria.rodriguez@example.com', secondaryEmails: [],
        avatar: null, avatarColor: '#f59e0b',
        pronouns: 'she/her',
        status: { emoji: '🏖️', message: 'On vacation until May 20', busy: true },
        bio: 'Backend engineer. Rust & Go.',
        location: 'Madrid, Spain', organization: 'Acme Corp',
        timezone: 'Europe/Madrid', profileVisibility: 'public',
        createdAt: '2023-06-10T09:00:00Z', lastActivityAt: '2025-05-05T11:30:00Z',
        twoFactorEnabled: false
    },
    {
        id: 5, username: 'omar.hassan', name: 'Omar Hassan',
        email: 'omar.hassan@example.com', secondaryEmails: ['omar@freelance.dev'],
        avatar: null, avatarColor: '#8b5cf6',
        pronouns: 'he/him',
        status: { emoji: '🔬', message: 'Researching new architectures', busy: false },
        bio: 'Solutions architect. Distributed systems.',
        location: 'Cairo, Egypt', organization: 'Acme Corp',
        timezone: 'Africa/Cairo', profileVisibility: 'internal',
        createdAt: '2022-08-05T15:30:00Z', lastActivityAt: '2025-05-10T12:00:00Z',
        twoFactorEnabled: true
    },
    {
        id: 6, username: 'emma.wilson', name: 'Emma Wilson',
        email: 'emma.wilson@example.com', secondaryEmails: [],
        avatar: null, avatarColor: '#ef4444',
        pronouns: 'she/her',
        status: { emoji: '', message: '', busy: false },
        bio: 'Frontend developer. React & Vue.js specialist.',
        location: 'London, UK', organization: 'Acme Corp',
        timezone: 'Europe/London', profileVisibility: 'public',
        createdAt: '2023-02-14T10:00:00Z', lastActivityAt: '2025-05-10T16:30:00Z',
        twoFactorEnabled: true
    },
    {
        id: 7, username: 'liam.oshea', name: "Liam O'Shea",
        email: 'liam.oshea@example.com', secondaryEmails: [],
        avatar: null, avatarColor: '#06b6d4',
        pronouns: 'he/him',
        status: { emoji: '📝', message: 'Writing docs', busy: false },
        bio: 'Technical writer and QA engineer.',
        location: 'Dublin, Ireland', organization: 'Acme Corp',
        timezone: 'Europe/Dublin', profileVisibility: 'public',
        createdAt: '2023-11-01T09:00:00Z', lastActivityAt: '2025-05-08T14:20:00Z',
        twoFactorEnabled: false
    },
    {
        id: 8, username: 'yuki.tanaka', name: 'Yuki Tanaka',
        email: 'yuki.tanaka@example.com', secondaryEmails: ['yuki@tanaka.jp'],
        avatar: null, avatarColor: '#d946ef',
        pronouns: '',
        status: { emoji: '🚀', message: 'Deploying to prod', busy: true },
        bio: 'SRE. Loves monitoring and observability.',
        location: 'Tokyo, Japan', organization: 'Acme Corp',
        timezone: 'Asia/Tokyo', profileVisibility: 'public',
        createdAt: '2022-05-20T08:30:00Z', lastActivityAt: '2025-05-10T23:15:00Z',
        twoFactorEnabled: true
    },
    {
        id: 9, username: 'sofia.petrov', name: 'Sofia Petrov',
        email: 'sofia.petrov@example.com', secondaryEmails: [],
        avatar: null, avatarColor: '#22c55e',
        pronouns: 'she/her',
        status: { emoji: '', message: '', busy: false },
        bio: 'Data engineer. Python & Spark.',
        location: 'Berlin, Germany', organization: 'DataStream GmbH',
        timezone: 'Europe/Berlin', profileVisibility: 'internal',
        createdAt: '2024-01-08T11:00:00Z', lastActivityAt: '2025-05-10T10:00:00Z',
        twoFactorEnabled: true
    },
    {
        id: 10, username: 'dev.bot', name: 'CI Bot (Automated)',
        email: 'ci-bot@acme.com', secondaryEmails: [],
        avatar: null, avatarColor: '#64748b',
        pronouns: '',
        status: { emoji: '🤖', message: 'Automated account', busy: false },
        bio: 'Service account for CI/CD pipelines.',
        location: '', organization: 'Acme Corp',
        timezone: 'UTC', profileVisibility: 'private',
        createdAt: '2022-01-01T00:00:00Z', lastActivityAt: '2025-05-10T23:59:00Z',
        twoFactorEnabled: false
    },
    {
        id: 11, username: 'ana.kowalski', name: 'Ana Kowalski',
        email: 'ana.kowalski@example.com', secondaryEmails: [],
        avatar: null, avatarColor: '#f97316',
        pronouns: 'she/her',
        status: { emoji: '', message: '', busy: false },
        bio: 'Security engineer. AppSec and pentesting.',
        location: 'Warsaw, Poland', organization: 'Acme Corp',
        timezone: 'Europe/Warsaw', profileVisibility: 'public',
        createdAt: '2023-04-22T14:00:00Z', lastActivityAt: '2025-05-09T18:00:00Z',
        twoFactorEnabled: true
    },
    {
        id: 12, username: 'carlos.mendes', name: 'Carlos Mendes',
        email: 'carlos.mendes@example.com', secondaryEmails: [],
        avatar: null, avatarColor: '#0ea5e9',
        pronouns: 'he/him',
        status: { emoji: '☕', message: '', busy: false },
        bio: 'Mobile developer. iOS & Android.',
        location: 'São Paulo, Brazil', organization: 'Acme Corp',
        timezone: 'America/Sao_Paulo', profileVisibility: 'public',
        createdAt: '2024-03-01T10:00:00Z', lastActivityAt: '2025-05-10T20:30:00Z',
        twoFactorEnabled: false
    }
];

// ---- Organizations ----
const ORGANIZATIONS = [
    {
        id: 1,
        name: 'Acme Corporation',
        path: 'acme-corp',
        description: 'Global technology company building next-generation developer tools and cloud infrastructure.',
        avatar: null,
        avatarColor: '#6366f1',
        visibility: 'public',
        createdAt: '2021-06-01T00:00:00Z',
        updatedAt: '2025-04-15T10:00:00Z',
        ownerId: 1
    },
    {
        id: 2,
        name: 'DataStream GmbH',
        path: 'datastream',
        description: 'Data analytics and machine learning solutions provider.',
        avatar: null,
        avatarColor: '#22c55e',
        visibility: 'private',
        createdAt: '2023-01-15T00:00:00Z',
        updatedAt: '2025-03-20T14:00:00Z',
        ownerId: 9
    }
];

// ---- Groups (Hierarchical) ----
const GROUPS = [
    // Top-level groups under Acme Corp
    {
        id: 1, name: 'Platform Engineering', path: 'platform-engineering',
        fullPath: 'acme-corp/platform-engineering',
        description: 'Core platform services, infrastructure, and developer tools.',
        parentId: null, organizationId: 1,
        visibility: 'private', avatar: null, avatarColor: '#6366f1',
        createdAt: '2021-06-15T10:00:00Z', updatedAt: '2025-04-01T09:00:00Z',
        archived: false, userCap: null, preventInvitations: false,
        disableMentions: false, preventSharingOutsideHierarchy: false,
        defaultBranchProtection: 'fully_protected',
        subgroupCreationLevel: 'maintainer', projectCreationLevel: 'developer',
        requireTwoFactor: false, readme: '# Platform Engineering\n\nWe build and maintain the core infrastructure that powers all Acme products.'
    },
    {
        id: 2, name: 'Product Development', path: 'product-dev',
        fullPath: 'acme-corp/product-dev',
        description: 'All product teams and their codebases.',
        parentId: null, organizationId: 1,
        visibility: 'internal', avatar: null, avatarColor: '#ec4899',
        createdAt: '2021-06-15T10:30:00Z', updatedAt: '2025-03-28T14:00:00Z',
        archived: false, userCap: 50, preventInvitations: false,
        disableMentions: false, preventSharingOutsideHierarchy: false,
        defaultBranchProtection: 'fully_protected',
        subgroupCreationLevel: 'owner', projectCreationLevel: 'maintainer',
        requireTwoFactor: true, readme: ''
    },
    {
        id: 3, name: 'Open Source', path: 'open-source',
        fullPath: 'acme-corp/open-source',
        description: 'Open-source projects maintained by Acme.',
        parentId: null, organizationId: 1,
        visibility: 'public', avatar: null, avatarColor: '#14b8a6',
        createdAt: '2022-01-10T08:00:00Z', updatedAt: '2025-02-15T11:00:00Z',
        archived: false, userCap: null, preventInvitations: false,
        disableMentions: false, preventSharingOutsideHierarchy: false,
        defaultBranchProtection: 'developers_can_merge',
        subgroupCreationLevel: 'developer', projectCreationLevel: 'developer',
        requireTwoFactor: false, readme: '# Open Source at Acme\n\nContributions welcome! See individual project READMEs for guidelines.'
    },
    {
        id: 4, name: 'Security', path: 'security',
        fullPath: 'acme-corp/security',
        description: 'Security team projects, audits, and compliance.',
        parentId: null, organizationId: 1,
        visibility: 'private', avatar: null, avatarColor: '#ef4444',
        createdAt: '2021-08-01T09:00:00Z', updatedAt: '2025-05-01T16:00:00Z',
        archived: false, userCap: 15, preventInvitations: true,
        disableMentions: false, preventSharingOutsideHierarchy: true,
        defaultBranchProtection: 'fully_protected',
        subgroupCreationLevel: 'owner', projectCreationLevel: 'maintainer',
        requireTwoFactor: true, readme: ''
    },
    {
        id: 5, name: 'Archived Projects', path: 'archived-projects',
        fullPath: 'acme-corp/archived-projects',
        description: 'Archived and deprecated project groups.',
        parentId: null, organizationId: 1,
        visibility: 'private', avatar: null, avatarColor: '#64748b',
        createdAt: '2023-06-01T10:00:00Z', updatedAt: '2024-11-20T12:00:00Z',
        archived: true, userCap: null, preventInvitations: true,
        disableMentions: true, preventSharingOutsideHierarchy: true,
        defaultBranchProtection: 'fully_protected',
        subgroupCreationLevel: 'owner', projectCreationLevel: 'owner',
        requireTwoFactor: false, readme: ''
    },

    // Subgroups under Platform Engineering (id: 1)
    {
        id: 6, name: 'Infrastructure', path: 'infrastructure',
        fullPath: 'acme-corp/platform-engineering/infrastructure',
        description: 'Cloud infrastructure, Terraform modules, and Kubernetes configs.',
        parentId: 1, organizationId: 1,
        visibility: 'private', avatar: null, avatarColor: '#f59e0b',
        createdAt: '2021-07-01T10:00:00Z', updatedAt: '2025-04-20T08:00:00Z',
        archived: false, userCap: null, preventInvitations: false,
        disableMentions: false, preventSharingOutsideHierarchy: false,
        defaultBranchProtection: 'fully_protected',
        subgroupCreationLevel: 'maintainer', projectCreationLevel: 'developer',
        requireTwoFactor: false, readme: ''
    },
    {
        id: 7, name: 'CI/CD', path: 'ci-cd',
        fullPath: 'acme-corp/platform-engineering/ci-cd',
        description: 'Continuous integration and deployment pipelines, shared runners.',
        parentId: 1, organizationId: 1,
        visibility: 'private', avatar: null, avatarColor: '#8b5cf6',
        createdAt: '2021-07-15T09:00:00Z', updatedAt: '2025-03-10T17:00:00Z',
        archived: false, userCap: null, preventInvitations: false,
        disableMentions: false, preventSharingOutsideHierarchy: false,
        defaultBranchProtection: 'fully_protected',
        subgroupCreationLevel: 'maintainer', projectCreationLevel: 'developer',
        requireTwoFactor: false, readme: ''
    },
    {
        id: 8, name: 'Observability', path: 'observability',
        fullPath: 'acme-corp/platform-engineering/observability',
        description: 'Monitoring, logging, and alerting infrastructure.',
        parentId: 1, organizationId: 1,
        visibility: 'private', avatar: null, avatarColor: '#06b6d4',
        createdAt: '2022-03-01T10:00:00Z', updatedAt: '2025-02-28T13:00:00Z',
        archived: false, userCap: null, preventInvitations: false,
        disableMentions: false, preventSharingOutsideHierarchy: false,
        defaultBranchProtection: 'fully_protected',
        subgroupCreationLevel: 'maintainer', projectCreationLevel: 'developer',
        requireTwoFactor: false, readme: ''
    },

    // Subgroups under Product Development (id: 2)
    {
        id: 9, name: 'Web Application', path: 'web-app',
        fullPath: 'acme-corp/product-dev/web-app',
        description: 'Main web application frontend and BFF services.',
        parentId: 2, organizationId: 1,
        visibility: 'internal', avatar: null, avatarColor: '#ec4899',
        createdAt: '2021-07-01T10:00:00Z', updatedAt: '2025-04-15T11:00:00Z',
        archived: false, userCap: null, preventInvitations: false,
        disableMentions: false, preventSharingOutsideHierarchy: false,
        defaultBranchProtection: 'fully_protected',
        subgroupCreationLevel: 'maintainer', projectCreationLevel: 'developer',
        requireTwoFactor: false, readme: ''
    },
    {
        id: 10, name: 'Mobile', path: 'mobile',
        fullPath: 'acme-corp/product-dev/mobile',
        description: 'iOS and Android applications.',
        parentId: 2, organizationId: 1,
        visibility: 'private', avatar: null, avatarColor: '#f97316',
        createdAt: '2022-06-01T09:00:00Z', updatedAt: '2025-04-10T16:00:00Z',
        archived: false, userCap: null, preventInvitations: false,
        disableMentions: false, preventSharingOutsideHierarchy: false,
        defaultBranchProtection: 'fully_protected',
        subgroupCreationLevel: 'maintainer', projectCreationLevel: 'developer',
        requireTwoFactor: false, readme: ''
    },
    {
        id: 11, name: 'API Services', path: 'api-services',
        fullPath: 'acme-corp/product-dev/api-services',
        description: 'Backend microservices and API gateways.',
        parentId: 2, organizationId: 1,
        visibility: 'internal', avatar: null, avatarColor: '#0ea5e9',
        createdAt: '2021-08-15T10:00:00Z', updatedAt: '2025-05-05T09:00:00Z',
        archived: false, userCap: null, preventInvitations: false,
        disableMentions: false, preventSharingOutsideHierarchy: false,
        defaultBranchProtection: 'fully_protected',
        subgroupCreationLevel: 'maintainer', projectCreationLevel: 'developer',
        requireTwoFactor: false, readme: ''
    },

    // Deeper nesting — subgroup of Infrastructure (id: 6)
    {
        id: 12, name: 'Terraform Modules', path: 'terraform-modules',
        fullPath: 'acme-corp/platform-engineering/infrastructure/terraform-modules',
        description: 'Shared Terraform modules for AWS, GCP, and Azure.',
        parentId: 6, organizationId: 1,
        visibility: 'private', avatar: null, avatarColor: '#a855f7',
        createdAt: '2022-02-01T10:00:00Z', updatedAt: '2025-03-15T14:00:00Z',
        archived: false, userCap: null, preventInvitations: false,
        disableMentions: false, preventSharingOutsideHierarchy: false,
        defaultBranchProtection: 'fully_protected',
        subgroupCreationLevel: 'maintainer', projectCreationLevel: 'developer',
        requireTwoFactor: false, readme: ''
    },

    // Subgroup under Security (id: 4)
    {
        id: 13, name: 'Vulnerability Research', path: 'vuln-research',
        fullPath: 'acme-corp/security/vuln-research',
        description: 'Internal vulnerability research and CVE tracking.',
        parentId: 4, organizationId: 1,
        visibility: 'private', avatar: null, avatarColor: '#dc2626',
        createdAt: '2022-09-01T09:00:00Z', updatedAt: '2025-04-28T11:00:00Z',
        archived: false, userCap: 5, preventInvitations: true,
        disableMentions: false, preventSharingOutsideHierarchy: true,
        defaultBranchProtection: 'fully_protected',
        subgroupCreationLevel: 'owner', projectCreationLevel: 'maintainer',
        requireTwoFactor: true, readme: ''
    },

    // DataStream top-level group
    {
        id: 14, name: 'Analytics Platform', path: 'analytics-platform',
        fullPath: 'datastream/analytics-platform',
        description: 'Core analytics and data processing platform.',
        parentId: null, organizationId: 2,
        visibility: 'private', avatar: null, avatarColor: '#22c55e',
        createdAt: '2023-02-01T10:00:00Z', updatedAt: '2025-04-01T09:00:00Z',
        archived: false, userCap: null, preventInvitations: false,
        disableMentions: false, preventSharingOutsideHierarchy: false,
        defaultBranchProtection: 'fully_protected',
        subgroupCreationLevel: 'maintainer', projectCreationLevel: 'developer',
        requireTwoFactor: false, readme: ''
    }
];

// ---- Projects ----
const PROJECTS = [
    // Platform Engineering > Infrastructure projects
    {
        id: 1, name: 'aws-terraform-base', path: 'aws-terraform-base',
        fullPath: 'acme-corp/platform-engineering/infrastructure/aws-terraform-base',
        description: 'Base Terraform configurations for AWS accounts.',
        groupId: 6, visibility: 'private',
        createdAt: '2021-07-10T10:00:00Z', updatedAt: '2025-05-08T14:00:00Z',
        stars: 12, forks: 3, defaultBranch: 'main',
        topics: ['terraform', 'aws', 'infrastructure'],
        archived: false, empty: false
    },
    {
        id: 2, name: 'k8s-cluster-config', path: 'k8s-cluster-config',
        fullPath: 'acme-corp/platform-engineering/infrastructure/k8s-cluster-config',
        description: 'Kubernetes cluster configurations and Helm charts.',
        groupId: 6, visibility: 'private',
        createdAt: '2021-09-01T09:00:00Z', updatedAt: '2025-05-10T11:00:00Z',
        stars: 8, forks: 1, defaultBranch: 'main',
        topics: ['kubernetes', 'helm', 'infrastructure'],
        archived: false, empty: false
    },
    // Platform Engineering > CI/CD projects
    {
        id: 3, name: 'shared-pipeline-templates', path: 'shared-pipeline-templates',
        fullPath: 'acme-corp/platform-engineering/ci-cd/shared-pipeline-templates',
        description: 'Reusable CI/CD pipeline templates for all teams.',
        groupId: 7, visibility: 'private',
        createdAt: '2021-08-01T10:00:00Z', updatedAt: '2025-04-25T16:00:00Z',
        stars: 25, forks: 8, defaultBranch: 'main',
        topics: ['ci-cd', 'templates', 'pipelines'],
        archived: false, empty: false
    },
    {
        id: 4, name: 'runner-autoscaler', path: 'runner-autoscaler',
        fullPath: 'acme-corp/platform-engineering/ci-cd/runner-autoscaler',
        description: 'Auto-scaling GitLab runner infrastructure on AWS.',
        groupId: 7, visibility: 'private',
        createdAt: '2022-04-15T10:00:00Z', updatedAt: '2025-05-02T09:00:00Z',
        stars: 6, forks: 0, defaultBranch: 'main',
        topics: ['runners', 'autoscaling', 'aws'],
        archived: false, empty: false
    },
    // Platform Engineering > Observability projects
    {
        id: 5, name: 'grafana-dashboards', path: 'grafana-dashboards',
        fullPath: 'acme-corp/platform-engineering/observability/grafana-dashboards',
        description: 'Centralized Grafana dashboard definitions.',
        groupId: 8, visibility: 'private',
        createdAt: '2022-03-15T10:00:00Z', updatedAt: '2025-04-18T12:00:00Z',
        stars: 15, forks: 2, defaultBranch: 'main',
        topics: ['grafana', 'monitoring', 'dashboards'],
        archived: false, empty: false
    },
    // Product Dev > Web App projects
    {
        id: 6, name: 'web-frontend', path: 'web-frontend',
        fullPath: 'acme-corp/product-dev/web-app/web-frontend',
        description: 'Main web application React frontend.',
        groupId: 9, visibility: 'internal',
        createdAt: '2021-07-05T10:00:00Z', updatedAt: '2025-05-10T18:00:00Z',
        stars: 34, forks: 5, defaultBranch: 'main',
        topics: ['react', 'typescript', 'frontend'],
        archived: false, empty: false
    },
    {
        id: 7, name: 'bff-gateway', path: 'bff-gateway',
        fullPath: 'acme-corp/product-dev/web-app/bff-gateway',
        description: 'Backend-for-Frontend GraphQL gateway.',
        groupId: 9, visibility: 'internal',
        createdAt: '2022-01-10T10:00:00Z', updatedAt: '2025-05-09T15:00:00Z',
        stars: 11, forks: 1, defaultBranch: 'main',
        topics: ['graphql', 'node', 'bff'],
        archived: false, empty: false
    },
    // Product Dev > Mobile projects
    {
        id: 8, name: 'ios-app', path: 'ios-app',
        fullPath: 'acme-corp/product-dev/mobile/ios-app',
        description: 'Native iOS application written in Swift.',
        groupId: 10, visibility: 'private',
        createdAt: '2022-06-15T09:00:00Z', updatedAt: '2025-05-07T17:00:00Z',
        stars: 7, forks: 0, defaultBranch: 'main',
        topics: ['ios', 'swift', 'mobile'],
        archived: false, empty: false
    },
    {
        id: 9, name: 'android-app', path: 'android-app',
        fullPath: 'acme-corp/product-dev/mobile/android-app',
        description: 'Native Android application written in Kotlin.',
        groupId: 10, visibility: 'private',
        createdAt: '2022-06-15T09:30:00Z', updatedAt: '2025-05-06T14:00:00Z',
        stars: 5, forks: 0, defaultBranch: 'main',
        topics: ['android', 'kotlin', 'mobile'],
        archived: false, empty: false
    },
    // Product Dev > API Services projects
    {
        id: 10, name: 'user-service', path: 'user-service',
        fullPath: 'acme-corp/product-dev/api-services/user-service',
        description: 'User authentication and profile management microservice.',
        groupId: 11, visibility: 'internal',
        createdAt: '2021-09-01T10:00:00Z', updatedAt: '2025-05-10T10:00:00Z',
        stars: 18, forks: 2, defaultBranch: 'main',
        topics: ['go', 'microservice', 'auth'],
        archived: false, empty: false
    },
    {
        id: 11, name: 'payment-service', path: 'payment-service',
        fullPath: 'acme-corp/product-dev/api-services/payment-service',
        description: 'Payment processing and billing microservice.',
        groupId: 11, visibility: 'private',
        createdAt: '2022-02-01T10:00:00Z', updatedAt: '2025-05-03T16:00:00Z',
        stars: 9, forks: 0, defaultBranch: 'main',
        topics: ['go', 'microservice', 'payments', 'stripe'],
        archived: false, empty: false
    },
    {
        id: 12, name: 'notification-service', path: 'notification-service',
        fullPath: 'acme-corp/product-dev/api-services/notification-service',
        description: 'Email, SMS, and push notification service.',
        groupId: 11, visibility: 'internal',
        createdAt: '2022-05-15T10:00:00Z', updatedAt: '2025-04-29T12:00:00Z',
        stars: 4, forks: 1, defaultBranch: 'main',
        topics: ['python', 'microservice', 'notifications'],
        archived: false, empty: false
    },
    // Open Source projects
    {
        id: 13, name: 'acme-cli', path: 'acme-cli',
        fullPath: 'acme-corp/open-source/acme-cli',
        description: 'Official Acme CLI tool for developers.',
        groupId: 3, visibility: 'public',
        createdAt: '2022-03-01T10:00:00Z', updatedAt: '2025-05-10T20:00:00Z',
        stars: 142, forks: 38, defaultBranch: 'main',
        topics: ['cli', 'rust', 'developer-tools'],
        archived: false, empty: false
    },
    {
        id: 14, name: 'design-system', path: 'design-system',
        fullPath: 'acme-corp/open-source/design-system',
        description: 'Acme UI component library and design tokens.',
        groupId: 3, visibility: 'public',
        createdAt: '2022-08-01T10:00:00Z', updatedAt: '2025-05-09T11:00:00Z',
        stars: 87, forks: 22, defaultBranch: 'main',
        topics: ['react', 'design-system', 'components', 'css'],
        archived: false, empty: false
    },
    // Security projects
    {
        id: 15, name: 'sast-rules', path: 'sast-rules',
        fullPath: 'acme-corp/security/sast-rules',
        description: 'Custom SAST rules and security scanning configurations.',
        groupId: 4, visibility: 'private',
        createdAt: '2021-10-01T09:00:00Z', updatedAt: '2025-05-01T15:00:00Z',
        stars: 3, forks: 0, defaultBranch: 'main',
        topics: ['security', 'sast', 'scanning'],
        archived: false, empty: false
    },
    {
        id: 16, name: 'incident-response-playbooks', path: 'incident-response-playbooks',
        fullPath: 'acme-corp/security/incident-response-playbooks',
        description: 'Documented playbooks for security incident response.',
        groupId: 4, visibility: 'private',
        createdAt: '2022-01-15T09:00:00Z', updatedAt: '2025-04-20T10:00:00Z',
        stars: 6, forks: 0, defaultBranch: 'main',
        topics: ['security', 'incident-response', 'documentation'],
        archived: false, empty: false
    },
    // Terraform Modules projects
    {
        id: 17, name: 'tf-module-vpc', path: 'tf-module-vpc',
        fullPath: 'acme-corp/platform-engineering/infrastructure/terraform-modules/tf-module-vpc',
        description: 'Terraform module for VPC provisioning across cloud providers.',
        groupId: 12, visibility: 'private',
        createdAt: '2022-02-15T10:00:00Z', updatedAt: '2025-03-20T11:00:00Z',
        stars: 10, forks: 4, defaultBranch: 'main',
        topics: ['terraform', 'vpc', 'networking'],
        archived: false, empty: false
    },
    {
        id: 18, name: 'tf-module-rds', path: 'tf-module-rds',
        fullPath: 'acme-corp/platform-engineering/infrastructure/terraform-modules/tf-module-rds',
        description: 'Terraform module for RDS database instances.',
        groupId: 12, visibility: 'private',
        createdAt: '2022-03-01T10:00:00Z', updatedAt: '2025-02-10T14:00:00Z',
        stars: 7, forks: 2, defaultBranch: 'main',
        topics: ['terraform', 'rds', 'database'],
        archived: false, empty: false
    },
    // Archived project
    {
        id: 19, name: 'legacy-monolith', path: 'legacy-monolith',
        fullPath: 'acme-corp/archived-projects/legacy-monolith',
        description: 'Deprecated monolithic application. Migrated to microservices.',
        groupId: 5, visibility: 'private',
        createdAt: '2019-03-01T10:00:00Z', updatedAt: '2024-06-15T10:00:00Z',
        stars: 2, forks: 0, defaultBranch: 'master',
        topics: ['legacy', 'ruby', 'rails'],
        archived: true, empty: false
    },
    // DataStream project
    {
        id: 20, name: 'data-pipeline', path: 'data-pipeline',
        fullPath: 'datastream/analytics-platform/data-pipeline',
        description: 'Apache Spark-based data processing pipeline.',
        groupId: 14, visibility: 'private',
        createdAt: '2023-02-15T10:00:00Z', updatedAt: '2025-04-28T16:00:00Z',
        stars: 3, forks: 0, defaultBranch: 'main',
        topics: ['spark', 'python', 'data-engineering'],
        archived: false, empty: false
    }
];

// ---- Group Memberships ----
// Each entry: { groupId, userId, role, membershipType, source, expiresAt, addedBy, addedAt }
const GROUP_MEMBERSHIPS = [
    // Platform Engineering (id:1) — direct members
    { groupId: 1, userId: 1, role: ROLES.OWNER, membershipType: 'direct', source: null, expiresAt: null, addedBy: 1, addedAt: '2021-06-15T10:00:00Z' },
    { groupId: 1, userId: 3, role: ROLES.MAINTAINER, membershipType: 'direct', source: null, expiresAt: null, addedBy: 1, addedAt: '2022-01-20T12:00:00Z' },
    { groupId: 1, userId: 8, role: ROLES.DEVELOPER, membershipType: 'direct', source: null, expiresAt: null, addedBy: 1, addedAt: '2022-05-25T08:00:00Z' },
    { groupId: 1, userId: 10, role: ROLES.DEVELOPER, membershipType: 'direct', source: null, expiresAt: null, addedBy: 3, addedAt: '2022-02-01T10:00:00Z' },

    // Product Development (id:2) — direct members
    { groupId: 2, userId: 2, role: ROLES.OWNER, membershipType: 'direct', source: null, expiresAt: null, addedBy: 1, addedAt: '2021-06-15T10:30:00Z' },
    { groupId: 2, userId: 1, role: ROLES.OWNER, membershipType: 'direct', source: null, expiresAt: null, addedBy: 2, addedAt: '2021-06-20T09:00:00Z' },
    { groupId: 2, userId: 6, role: ROLES.DEVELOPER, membershipType: 'direct', source: null, expiresAt: null, addedBy: 2, addedAt: '2023-02-15T10:00:00Z' },
    { groupId: 2, userId: 4, role: ROLES.DEVELOPER, membershipType: 'direct', source: null, expiresAt: '2025-06-30T00:00:00Z', addedBy: 2, addedAt: '2023-06-15T09:00:00Z' },
    { groupId: 2, userId: 12, role: ROLES.DEVELOPER, membershipType: 'direct', source: null, expiresAt: null, addedBy: 2, addedAt: '2024-03-05T10:00:00Z' },

    // Open Source (id:3) — direct members
    { groupId: 3, userId: 1, role: ROLES.OWNER, membershipType: 'direct', source: null, expiresAt: null, addedBy: 1, addedAt: '2022-01-10T08:00:00Z' },
    { groupId: 3, userId: 5, role: ROLES.MAINTAINER, membershipType: 'direct', source: null, expiresAt: null, addedBy: 1, addedAt: '2022-08-10T15:00:00Z' },
    { groupId: 3, userId: 7, role: ROLES.DEVELOPER, membershipType: 'direct', source: null, expiresAt: null, addedBy: 1, addedAt: '2023-11-05T09:00:00Z' },

    // Archived Projects (id:5) — direct members
    { groupId: 5, userId: 1, role: ROLES.OWNER, membershipType: 'direct', source: null, expiresAt: null, addedBy: 1, addedAt: '2023-06-01T10:00:00Z' },

    // Security (id:4) — direct members
    { groupId: 4, userId: 1, role: ROLES.OWNER, membershipType: 'direct', source: null, expiresAt: null, addedBy: 1, addedAt: '2021-08-01T09:00:00Z' },
    { groupId: 4, userId: 11, role: ROLES.MAINTAINER, membershipType: 'direct', source: null, expiresAt: null, addedBy: 1, addedAt: '2023-04-25T14:00:00Z' },
    { groupId: 4, userId: 5, role: ROLES.DEVELOPER, membershipType: 'direct', source: null, expiresAt: null, addedBy: 1, addedAt: '2022-09-01T10:00:00Z' },

    // Infrastructure (id:6) — inherits from Platform Eng + direct
    { groupId: 6, userId: 3, role: ROLES.MAINTAINER, membershipType: 'direct', source: null, expiresAt: null, addedBy: 1, addedAt: '2022-01-25T12:00:00Z' },

    // CI/CD (id:7) — direct
    { groupId: 7, userId: 3, role: ROLES.OWNER, membershipType: 'direct', source: null, expiresAt: null, addedBy: 1, addedAt: '2021-07-15T09:00:00Z' },

    // Web App (id:9) — direct
    { groupId: 9, userId: 6, role: ROLES.MAINTAINER, membershipType: 'direct', source: null, expiresAt: null, addedBy: 2, addedAt: '2023-03-01T10:00:00Z' },

    // Mobile (id:10) — direct
    { groupId: 10, userId: 12, role: ROLES.MAINTAINER, membershipType: 'direct', source: null, expiresAt: null, addedBy: 2, addedAt: '2024-03-10T10:00:00Z' },

    // API Services (id:11) — direct
    { groupId: 11, userId: 4, role: ROLES.MAINTAINER, membershipType: 'direct', source: null, expiresAt: '2025-06-30T00:00:00Z', addedBy: 2, addedAt: '2023-07-01T09:00:00Z' },

    // Terraform Modules (id:12) — direct
    { groupId: 12, userId: 3, role: ROLES.MAINTAINER, membershipType: 'direct', source: null, expiresAt: null, addedBy: 1, addedAt: '2022-02-05T10:00:00Z' },

    // Vuln Research (id:13) — direct
    { groupId: 13, userId: 11, role: ROLES.MAINTAINER, membershipType: 'direct', source: null, expiresAt: null, addedBy: 1, addedAt: '2022-09-05T09:00:00Z' },

    // DataStream Analytics (id:14) — direct
    { groupId: 14, userId: 9, role: ROLES.OWNER, membershipType: 'direct', source: null, expiresAt: null, addedBy: 9, addedAt: '2023-02-01T10:00:00Z' },
    { groupId: 14, userId: 1, role: ROLES.DEVELOPER, membershipType: 'direct', source: null, expiresAt: '2025-12-31T00:00:00Z', addedBy: 9, addedAt: '2024-01-15T10:00:00Z' }
];

// ---- Project Memberships (direct only — inherited computed at runtime) ----
const PROJECT_MEMBERSHIPS = [
    // web-frontend (id:6) — direct members beyond group inheritance
    { projectId: 6, userId: 7, role: ROLES.REPORTER, membershipType: 'direct', expiresAt: null, addedBy: 6, addedAt: '2024-01-10T10:00:00Z' },
    // payment-service (id:11) — extra direct member
    { projectId: 11, userId: 11, role: ROLES.DEVELOPER, membershipType: 'direct', expiresAt: null, addedBy: 4, addedAt: '2023-08-15T10:00:00Z' },
    // acme-cli (id:13) — external contributor
    { projectId: 13, userId: 9, role: ROLES.DEVELOPER, membershipType: 'direct', expiresAt: '2025-08-01T00:00:00Z', addedBy: 1, addedAt: '2024-06-01T10:00:00Z' },
    // design-system (id:14) — extra member
    { projectId: 14, userId: 6, role: ROLES.MAINTAINER, membershipType: 'direct', expiresAt: null, addedBy: 5, addedAt: '2023-09-01T10:00:00Z' },
    // sast-rules (id:15) — direct
    { projectId: 15, userId: 10, role: ROLES.REPORTER, membershipType: 'direct', expiresAt: null, addedBy: 11, addedAt: '2023-05-01T10:00:00Z' }
];

// ---- Group-to-Group Sharing (invitations) ----
// { sourceGroupId (invited group), targetGroupId (inviting group), maxRole, expiresAt }
const GROUP_SHARES = [
    // Security group shared with Platform Engineering (so security can review infra)
    { sourceGroupId: 4, targetGroupId: 1, maxRole: ROLES.REPORTER, expiresAt: null, addedBy: 1, addedAt: '2023-01-15T10:00:00Z' },
    // Platform Engineering shared with Product Dev (so platform team can support product)
    { sourceGroupId: 1, targetGroupId: 2, maxRole: ROLES.DEVELOPER, expiresAt: null, addedBy: 2, addedAt: '2023-03-01T10:00:00Z' }
];

// ---- Group-to-Project Sharing ----
// { sourceGroupId (invited group), targetProjectId, maxRole, expiresAt }
const PROJECT_SHARES = [
    // Open Source group invited to web-frontend (so OSS team can review UI)
    { sourceGroupId: 3, targetProjectId: 6, maxRole: ROLES.REPORTER, expiresAt: null, addedBy: 6, addedAt: '2023-05-01T10:00:00Z' },
    // Security group invited to payment-service (for security review)
    { sourceGroupId: 4, targetProjectId: 11, maxRole: ROLES.REPORTER, expiresAt: '2025-07-01T00:00:00Z', addedBy: 4, addedAt: '2024-01-10T10:00:00Z' }
];

// ---- Import Sources ----
const IMPORT_SOURCES = [
    { id: 'gitlab', name: 'GitLab export', description: 'Import from a GitLab export file (.tar.gz)', icon: '🦊', supportsGroups: true, supportsProjects: true },
    { id: 'gitlab_direct', name: 'GitLab (direct transfer)', description: 'Migrate groups and projects directly from another GitLab instance', icon: '🦊', supportsGroups: true, supportsProjects: true },
    { id: 'github', name: 'GitHub', description: 'Import repositories from GitHub.com or GitHub Enterprise', icon: '🐙', supportsGroups: false, supportsProjects: true },
    { id: 'bitbucket_server', name: 'Bitbucket Server', description: 'Import repositories from Bitbucket Server', icon: '🪣', supportsGroups: false, supportsProjects: true },
    { id: 'bitbucket_cloud', name: 'Bitbucket Cloud', description: 'Import repositories from Bitbucket Cloud', icon: '🪣', supportsGroups: false, supportsProjects: true },
    { id: 'gitea', name: 'Gitea', description: 'Import repositories from Gitea instances', icon: '🍵', supportsGroups: false, supportsProjects: true },
    { id: 'fogbugz', name: 'FogBugz', description: 'Import issues from FogBugz', icon: '🐛', supportsGroups: false, supportsProjects: true },
    { id: 'jira', name: 'Jira (issues only)', description: 'Import issues from Jira', icon: '📋', supportsGroups: false, supportsProjects: true },
    { id: 'manifest', name: 'Manifest file', description: 'Import multiple repositories from a manifest file', icon: '📄', supportsGroups: false, supportsProjects: true },
    { id: 'repo_url', name: 'Repository by URL', description: 'Import any Git repository by providing its URL', icon: '🔗', supportsGroups: false, supportsProjects: true }
];

// ---- GitLab.com Rate Limits & Settings ----
const GITLAB_COM_LIMITS = {
    repository: {
        maxSize: '10 GB',
        maxImport: '5 GiB',
        maxExport: '40 GiB',
        maxPush: '5 GiB',
        maxAttachment: '100 MiB',
        maxDiffPatch: '200 KB',
        maxDiffFiles: 3000,
        maxDiffLines: 100000
    },
    rateLimits: {
        unauthenticatedIP: { limit: 500, period: '1 minute' },
        authenticatedAPI: { limit: 2000, period: '1 minute' },
        authenticatedNonAPI: { limit: 1000, period: '1 minute' },
        protectedPaths: { limit: 10, period: '1 minute per IP' },
        rawEndpoints: { limit: 300, period: '1 minute' },
        issueCreation: { limit: 200, period: '1 minute' },
        noteCreation: { limit: 60, period: '1 minute' },
        pipelineCreation: { limit: 25, period: '1 minute' },
        groupProjectSearch: { limit: 10, period: '1 minute' },
        pagesRequests: { limit: 1000, period: '50 seconds per IP' },
        gitFailedAuthBan: { limit: 300, period: '1 minute, banned 15 min' }
    },
    cicd: {
        freeRunnerPerGroup: 50,
        freeRunnerPerProject: 50,
        paidRunnerPerGroup: 1000,
        paidRunnerPerProject: 1000,
        freePipelineSchedules: 10,
        paidPipelineSchedules: 50,
        artifactExpiry: '30 days'
    },
    misc: {
        containerRegistry: 'registry.gitlab.com',
        cdn: 'cdn.registry.gitlab-static.net',
        pagesDomain: 'gitlab.io',
        sessionTimeout: '7 days',
        emailConfirmation: 'required',
        unconfirmedDeletion: '3 days',
        delayedDeletion: '30 days',
        maxSubgroupDepth: 20,
        maxFollowing: 300
    }
};

// ---- Timezones (common subset) ----
const TIMEZONES = [
    'UTC', 'America/New_York', 'America/Chicago', 'America/Denver',
    'America/Los_Angeles', 'America/Toronto', 'America/Sao_Paulo',
    'Europe/London', 'Europe/Dublin', 'Europe/Berlin', 'Europe/Madrid',
    'Europe/Warsaw', 'Europe/Moscow', 'Africa/Cairo',
    'Asia/Kolkata', 'Asia/Tokyo', 'Asia/Shanghai', 'Asia/Singapore',
    'Australia/Sydney', 'Pacific/Auckland'
];
