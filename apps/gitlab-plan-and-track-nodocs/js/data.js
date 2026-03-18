/* ============================================================
   GitLab Plan & Track — Seed Data
   ============================================================ */

const SEED_DATA_VERSION = 1;

// ── Users ──────────────────────────────────────────────────
const CURRENT_USER = {
    id: 1,
    username: 'schen',
    name: 'Sarah Chen',
    email: 'sarah.chen@acmecorp.io',
    avatar: null,
    role: 'Owner',
    state: 'active'
};

const USERS = [
    { id: 1, username: 'schen', name: 'Sarah Chen', email: 'sarah.chen@acmecorp.io', avatar: null, role: 'Owner', state: 'active' },
    { id: 2, username: 'mjohnson', name: 'Marcus Johnson', email: 'marcus.j@acmecorp.io', avatar: null, role: 'Maintainer', state: 'active' },
    { id: 3, username: 'ppatel', name: 'Priya Patel', email: 'priya.patel@acmecorp.io', avatar: null, role: 'Developer', state: 'active' },
    { id: 4, username: 'akim', name: 'Alex Kim', email: 'alex.kim@acmecorp.io', avatar: null, role: 'Developer', state: 'active' },
    { id: 5, username: 'jwilliams', name: 'Jordan Williams', email: 'jordan.w@acmecorp.io', avatar: null, role: 'Developer', state: 'active' },
    { id: 6, username: 'erodriguez', name: 'Elena Rodriguez', email: 'elena.r@acmecorp.io', avatar: null, role: 'Maintainer', state: 'active' },
    { id: 7, username: 'dthompson', name: 'David Thompson', email: 'david.t@acmecorp.io', avatar: null, role: 'Developer', state: 'active' },
    { id: 8, username: 'lwang', name: 'Lisa Wang', email: 'lisa.wang@acmecorp.io', avatar: null, role: 'Reporter', state: 'active' },
    { id: 9, username: 'ohassan', name: 'Omar Hassan', email: 'omar.h@acmecorp.io', avatar: null, role: 'Developer', state: 'active' },
    { id: 10, username: 'rgreen', name: 'Rachel Green', email: 'rachel.g@acmecorp.io', avatar: null, role: 'Reporter', state: 'active' },
    { id: 11, username: 'knakamura', name: 'Kai Nakamura', email: 'kai.n@acmecorp.io', avatar: null, role: 'Maintainer', state: 'active' },
    { id: 12, username: 'smartin', name: 'Sophie Martin', email: 'sophie.m@acmecorp.io', avatar: null, role: 'Developer', state: 'blocked' }
];

// ── Labels ─────────────────────────────────────────────────
const LABELS = [
    { id: 1, name: 'bug', description: 'Something is broken or not working as expected', color: '#d9534f', textColor: '#ffffff', scoped: false },
    { id: 2, name: 'feature', description: 'New functionality or capability', color: '#428bca', textColor: '#ffffff', scoped: false },
    { id: 3, name: 'enhancement', description: 'Improvement to existing functionality', color: '#5cb85c', textColor: '#ffffff', scoped: false },
    { id: 4, name: 'documentation', description: 'Documentation updates or additions', color: '#f0ad4e', textColor: '#333333', scoped: false },
    { id: 5, name: 'security', description: 'Security-related issue or improvement', color: '#d9534f', textColor: '#ffffff', scoped: false },
    { id: 6, name: 'performance', description: 'Performance optimization or issue', color: '#9b59b6', textColor: '#ffffff', scoped: false },
    { id: 7, name: 'infrastructure', description: 'Infrastructure and deployment related', color: '#95a5a6', textColor: '#ffffff', scoped: false },
    { id: 8, name: 'needs-triage', description: 'Needs initial assessment and categorization', color: '#e67e22', textColor: '#ffffff', scoped: false },
    { id: 9, name: 'ready-for-dev', description: 'Ready to be picked up for development', color: '#27ae60', textColor: '#ffffff', scoped: false },
    { id: 10, name: 'tech-debt', description: 'Technical debt that needs addressing', color: '#8e44ad', textColor: '#ffffff', scoped: false },
    { id: 11, name: 'priority::critical', description: 'Critical priority — must fix immediately', color: '#c0392b', textColor: '#ffffff', scoped: true },
    { id: 12, name: 'priority::high', description: 'High priority — address this sprint', color: '#e74c3c', textColor: '#ffffff', scoped: true },
    { id: 13, name: 'priority::medium', description: 'Medium priority — plan for next sprint', color: '#f39c12', textColor: '#333333', scoped: true },
    { id: 14, name: 'priority::low', description: 'Low priority — address when possible', color: '#3498db', textColor: '#ffffff', scoped: true },
    { id: 15, name: 'status::in-progress', description: 'Currently being worked on', color: '#2980b9', textColor: '#ffffff', scoped: true },
    { id: 16, name: 'status::review', description: 'In code review or awaiting approval', color: '#8e44ad', textColor: '#ffffff', scoped: true },
    { id: 17, name: 'status::blocked', description: 'Blocked by external dependency or issue', color: '#e74c3c', textColor: '#ffffff', scoped: true },
    { id: 18, name: 'status::done', description: 'Completed and verified', color: '#27ae60', textColor: '#ffffff', scoped: true },
    { id: 19, name: 'workflow::design', description: 'Requires design work before development', color: '#1abc9c', textColor: '#ffffff', scoped: true },
    { id: 20, name: 'workflow::backend', description: 'Backend development work', color: '#2c3e50', textColor: '#ffffff', scoped: true },
    { id: 21, name: 'workflow::frontend', description: 'Frontend development work', color: '#16a085', textColor: '#ffffff', scoped: true },
    { id: 22, name: 'UX', description: 'User experience improvements', color: '#e91e63', textColor: '#ffffff', scoped: false },
    { id: 23, name: 'regression', description: 'Previously working feature now broken', color: '#ff5722', textColor: '#ffffff', scoped: false },
    { id: 24, name: 'breaking-change', description: 'Introduces a breaking API change', color: '#b71c1c', textColor: '#ffffff', scoped: false }
];

// ── Milestones ─────────────────────────────────────────────
const MILESTONES = [
    {
        id: 1, title: 'v4.0 Release', description: 'Major release with authentication overhaul and new API endpoints.',
        startDate: '2025-10-01', dueDate: '2025-12-15', state: 'closed', createdAt: '2025-09-15T10:00:00Z'
    },
    {
        id: 2, title: 'v4.1 Patch', description: 'Bug fixes and security patches for v4.0.',
        startDate: '2025-12-16', dueDate: '2026-01-31', state: 'closed', createdAt: '2025-12-10T14:30:00Z'
    },
    {
        id: 3, title: 'v4.2 Release', description: 'Performance improvements and mobile responsiveness. Current active milestone.',
        startDate: '2026-02-01', dueDate: '2026-04-15', state: 'active', createdAt: '2026-01-20T09:00:00Z'
    },
    {
        id: 4, title: 'v4.3 Release', description: 'Dark mode, accessibility compliance, and CI/CD enhancements.',
        startDate: '2026-04-16', dueDate: '2026-06-30', state: 'active', createdAt: '2026-02-01T11:00:00Z'
    },
    {
        id: 5, title: 'v5.0 Major Release', description: 'Complete platform redesign with new architecture. Planning phase.',
        startDate: '2026-07-01', dueDate: '2026-12-31', state: 'active', createdAt: '2026-01-05T08:00:00Z'
    },
    {
        id: 6, title: 'Backlog', description: 'Unscheduled items for future consideration.',
        startDate: null, dueDate: null, state: 'active', createdAt: '2025-06-01T10:00:00Z'
    }
];

// ── Iteration Cadences ─────────────────────────────────────
const ITERATION_CADENCES = [
    {
        id: 1, title: 'Sprint Cycle', description: 'Two-week development sprints',
        durationWeeks: 2, autoSchedule: true, createdAt: '2025-09-01T10:00:00Z'
    },
    {
        id: 2, title: 'Monthly Planning', description: 'Monthly planning and review cycle',
        durationWeeks: 4, autoSchedule: false, createdAt: '2025-09-01T10:00:00Z'
    }
];

const ITERATIONS = [
    { id: 1, cadenceId: 1, title: 'Sprint 22', startDate: '2026-01-20', endDate: '2026-02-02', state: 'closed', createdAt: '2026-01-15T10:00:00Z' },
    { id: 2, cadenceId: 1, title: 'Sprint 23', startDate: '2026-02-03', endDate: '2026-02-16', state: 'closed', createdAt: '2026-01-29T10:00:00Z' },
    { id: 3, cadenceId: 1, title: 'Sprint 24', startDate: '2026-02-17', endDate: '2026-03-02', state: 'closed', createdAt: '2026-02-12T10:00:00Z' },
    { id: 4, cadenceId: 1, title: 'Sprint 25', startDate: '2026-03-03', endDate: '2026-03-16', state: 'closed', createdAt: '2026-02-26T10:00:00Z' },
    { id: 5, cadenceId: 1, title: 'Sprint 26', startDate: '2026-03-17', endDate: '2026-03-30', state: 'current', createdAt: '2026-03-12T10:00:00Z' },
    { id: 6, cadenceId: 1, title: 'Sprint 27', startDate: '2026-03-31', endDate: '2026-04-13', state: 'upcoming', createdAt: '2026-03-12T10:00:00Z' },
    { id: 7, cadenceId: 2, title: 'March 2026', startDate: '2026-03-01', endDate: '2026-03-31', state: 'current', createdAt: '2026-02-25T10:00:00Z' },
    { id: 8, cadenceId: 2, title: 'April 2026', startDate: '2026-04-01', endDate: '2026-04-30', state: 'upcoming', createdAt: '2026-03-01T10:00:00Z' }
];

// ── Epics ──────────────────────────────────────────────────
const EPICS = [
    {
        id: 1, title: 'User Authentication Overhaul', description: 'Complete rewrite of the authentication system to support OAuth 2.0, SAML, and MFA.\n\n## Goals\n- Migrate from legacy session-based auth to JWT tokens\n- Add support for SAML SSO\n- Implement TOTP-based MFA\n- Deprecate API v1 auth endpoints',
        state: 'opened', authorId: 1, labels: [5, 12], confidential: false,
        startDate: '2025-10-01', dueDate: '2026-04-30',
        parentEpicId: null, createdAt: '2025-09-20T08:00:00Z', updatedAt: '2026-03-10T14:22:00Z'
    },
    {
        id: 2, title: 'API v3 Migration', description: 'Migrate all public API endpoints from v2 to v3. Includes breaking changes to response formats and new rate limiting.',
        state: 'opened', authorId: 2, labels: [24, 12], confidential: false,
        startDate: '2026-01-15', dueDate: '2026-06-30',
        parentEpicId: null, createdAt: '2025-12-01T11:00:00Z', updatedAt: '2026-03-15T09:30:00Z'
    },
    {
        id: 3, title: 'API v3 - Breaking Changes', description: 'Track and communicate all breaking changes in the v3 API migration.',
        state: 'opened', authorId: 2, labels: [24, 4], confidential: false,
        startDate: '2026-02-01', dueDate: '2026-05-31',
        parentEpicId: 2, createdAt: '2026-01-10T14:00:00Z', updatedAt: '2026-03-12T16:00:00Z'
    },
    {
        id: 4, title: 'Performance Optimization Q1', description: 'Q1 2026 performance targets: reduce p95 latency by 40%, optimize database queries, implement caching layer.',
        state: 'closed', authorId: 6, labels: [6], confidential: false,
        startDate: '2026-01-01', dueDate: '2026-03-31',
        parentEpicId: null, createdAt: '2025-12-15T10:00:00Z', updatedAt: '2026-03-15T17:00:00Z'
    },
    {
        id: 5, title: 'Mobile Responsive Redesign', description: 'Make all pages fully responsive for mobile and tablet viewports. Focus on navigation, tables, and forms.',
        state: 'opened', authorId: 1, labels: [22, 21], confidential: false,
        startDate: '2026-02-15', dueDate: '2026-05-31',
        parentEpicId: null, createdAt: '2026-01-25T09:00:00Z', updatedAt: '2026-03-14T11:00:00Z'
    },
    {
        id: 6, title: 'CI/CD Pipeline Improvements', description: 'Reduce build times by 50%, add parallel test execution, implement canary deployments.',
        state: 'opened', authorId: 11, labels: [7, 13], confidential: false,
        startDate: '2026-03-01', dueDate: '2026-07-31',
        parentEpicId: null, createdAt: '2026-02-10T13:00:00Z', updatedAt: '2026-03-16T10:00:00Z'
    },
    {
        id: 7, title: 'Documentation Revamp', description: 'Rewrite all public-facing documentation. Migrate from wiki to structured docs site with versioning.',
        state: 'opened', authorId: 8, labels: [4], confidential: false,
        startDate: '2026-03-15', dueDate: '2026-08-31',
        parentEpicId: null, createdAt: '2026-02-20T15:00:00Z', updatedAt: '2026-03-10T09:00:00Z'
    },
    {
        id: 8, title: 'Security Audit Remediation', description: 'Address all findings from the Q4 2025 external security audit. 12 critical, 28 high, 45 medium findings.',
        state: 'opened', authorId: 1, labels: [5, 11], confidential: true,
        startDate: '2026-01-10', dueDate: '2026-04-30',
        parentEpicId: null, createdAt: '2026-01-05T08:00:00Z', updatedAt: '2026-03-17T14:00:00Z'
    },
    {
        id: 9, title: 'Dark Mode Implementation', description: 'Add dark mode theme support across all pages. Must respect system preference and allow manual override.',
        state: 'opened', authorId: 4, labels: [22, 21], confidential: false,
        startDate: '2026-04-01', dueDate: '2026-06-15',
        parentEpicId: null, createdAt: '2026-02-28T10:00:00Z', updatedAt: '2026-03-05T16:00:00Z'
    },
    {
        id: 10, title: 'Accessibility Compliance (WCAG 2.1 AA)', description: 'Achieve full WCAG 2.1 AA compliance across the platform. Includes screen reader support, keyboard navigation, and color contrast fixes.',
        state: 'opened', authorId: 3, labels: [22, 13], confidential: false,
        startDate: '2026-05-01', dueDate: '2026-09-30',
        parentEpicId: null, createdAt: '2026-03-01T09:00:00Z', updatedAt: '2026-03-10T11:00:00Z'
    },
    {
        id: 11, title: 'Data Export/Import Feature', description: 'Allow users to export and import project data in CSV, JSON, and XML formats.',
        state: 'closed', authorId: 9, labels: [2], confidential: false,
        startDate: '2025-08-01', dueDate: '2025-11-30',
        parentEpicId: null, createdAt: '2025-07-15T10:00:00Z', updatedAt: '2025-11-28T17:00:00Z'
    },
    {
        id: 12, title: 'Notification System Overhaul', description: 'Redesign notification delivery pipeline. Add email digest, Slack integration, and in-app notification center.',
        state: 'opened', authorId: 6, labels: [2, 20], confidential: false,
        startDate: '2026-04-15', dueDate: '2026-08-15',
        parentEpicId: null, createdAt: '2026-03-05T14:00:00Z', updatedAt: '2026-03-15T10:00:00Z'
    }
];

// ── Issue Templates ────────────────────────────────────────
const ISSUE_TEMPLATES = [
    { id: 1, name: 'Bug Report', content: '## Summary\n\n## Steps to Reproduce\n1. \n2. \n3. \n\n## Expected Behavior\n\n## Actual Behavior\n\n## Environment\n- Browser: \n- OS: \n- Version: ' },
    { id: 2, name: 'Feature Request', content: '## Problem Statement\n\n## Proposed Solution\n\n## Alternatives Considered\n\n## Additional Context\n' },
    { id: 3, name: 'Task', content: '## Description\n\n## Acceptance Criteria\n- [ ] \n- [ ] \n\n## Dependencies\n' }
];

// ── Boards ─────────────────────────────────────────────────
const BOARDS = [
    {
        id: 1, name: 'Development Board', createdAt: '2025-09-01T10:00:00Z',
        lists: [
            { id: 1, type: 'backlog', title: 'Open', position: 0 },
            { id: 2, type: 'label', labelId: 9, title: 'To Do', position: 1 },
            { id: 3, type: 'label', labelId: 15, title: 'In Progress', position: 2 },
            { id: 4, type: 'label', labelId: 16, title: 'Review', position: 3 },
            { id: 5, type: 'closed', title: 'Done', position: 4 }
        ]
    },
    {
        id: 2, name: 'Bug Triage Board', createdAt: '2025-11-15T14:00:00Z',
        lists: [
            { id: 6, type: 'backlog', title: 'Open', position: 0 },
            { id: 7, type: 'label', labelId: 11, title: 'Critical', position: 1 },
            { id: 8, type: 'label', labelId: 12, title: 'High', position: 2 },
            { id: 9, type: 'label', labelId: 13, title: 'Medium', position: 3 },
            { id: 10, type: 'label', labelId: 14, title: 'Low', position: 4 },
            { id: 11, type: 'closed', title: 'Closed', position: 5 }
        ]
    }
];

// ── Notification Settings ──────────────────────────────────
const NOTIFICATION_SETTINGS = {
    level: 'participating',
    email: {
        newIssue: true,
        reassignedIssue: true,
        closedIssue: false,
        newComment: true,
        mentioned: true,
        milestoneChanged: false
    }
};

const NOTIFICATION_FEED = [
    { id: 1, type: 'assigned', issueId: 5, actorId: 2, message: 'Marcus Johnson assigned you to issue #105', read: false, createdAt: '2026-03-18T09:15:00Z' },
    { id: 2, type: 'mentioned', issueId: 12, actorId: 3, message: 'Priya Patel mentioned you in a comment on #112', read: false, createdAt: '2026-03-18T08:30:00Z' },
    { id: 3, type: 'status_change', issueId: 22, actorId: 6, message: 'Elena Rodriguez closed issue #122', read: false, createdAt: '2026-03-17T17:45:00Z' },
    { id: 4, type: 'label_change', issueId: 8, actorId: 4, message: 'Alex Kim added label priority::critical to #108', read: true, createdAt: '2026-03-17T14:20:00Z' },
    { id: 5, type: 'assigned', issueId: 15, actorId: 11, message: 'Kai Nakamura assigned you to issue #115', read: true, createdAt: '2026-03-17T11:00:00Z' },
    { id: 6, type: 'mentioned', issueId: 30, actorId: 9, message: 'Omar Hassan mentioned you in #130', read: true, createdAt: '2026-03-16T16:30:00Z' },
    { id: 7, type: 'new_comment', issueId: 3, actorId: 7, message: 'David Thompson commented on #103', read: true, createdAt: '2026-03-16T10:15:00Z' },
    { id: 8, type: 'milestone_change', issueId: 18, actorId: 2, message: 'Marcus Johnson moved #118 to milestone v4.2 Release', read: true, createdAt: '2026-03-15T15:00:00Z' },
    { id: 9, type: 'status_change', issueId: 42, actorId: 5, message: 'Jordan Williams reopened issue #142', read: true, createdAt: '2026-03-15T09:20:00Z' },
    { id: 10, type: 'assigned', issueId: 55, actorId: 1, message: 'You assigned yourself to issue #155', read: true, createdAt: '2026-03-14T14:00:00Z' }
];

// ── Issues ─────────────────────────────────────────────────
const ISSUES = [
    // --- Active high-priority issues ---
    {
        id: 1, iid: 101, title: 'Login page returns 500 error when SAML provider is unavailable',
        description: '## Summary\nWhen the configured SAML identity provider is down or unreachable, the login page throws a 500 error instead of gracefully falling back to username/password authentication.\n\n## Steps to Reproduce\n1. Configure SAML SSO with an IdP\n2. Take the IdP offline\n3. Navigate to /login\n4. Observe 500 error\n\n## Expected Behavior\nLogin page should show username/password form with a warning that SSO is unavailable.\n\n## Actual Behavior\n500 Internal Server Error',
        state: 'opened', type: 'issue', authorId: 1, assignees: [2, 3], labels: [1, 5, 11],
        milestoneId: 3, iterationId: 5, epicId: 1, weight: 5, dueDate: '2026-03-25',
        confidential: false, timeEstimate: 28800, timeSpent: 14400,
        createdAt: '2026-03-10T08:30:00Z', updatedAt: '2026-03-17T16:45:00Z',
        closedAt: null, closedBy: null, upvotes: 12, downvotes: 0, subscribed: true,
        relatedIssues: [{ issueId: 2, linkType: 'blocks' }, { issueId: 8, linkType: 'relates_to' }],
        activities: [
            { id: 1, type: 'comment', authorId: 2, content: 'I can reproduce this consistently. The SAML middleware doesn\'t have a timeout handler.', createdAt: '2026-03-10T10:15:00Z' },
            { id: 2, type: 'label_add', authorId: 1, content: 'Added label ~"priority::critical"', createdAt: '2026-03-10T08:35:00Z' },
            { id: 3, type: 'label_add', authorId: 1, content: 'Added label ~security', createdAt: '2026-03-10T08:35:00Z' },
            { id: 4, type: 'assignment', authorId: 1, content: 'Assigned to @mjohnson and @ppatel', createdAt: '2026-03-10T09:00:00Z' },
            { id: 5, type: 'comment', authorId: 3, content: 'Working on a fallback mechanism. PR incoming by EOD tomorrow.', createdAt: '2026-03-12T14:30:00Z' },
            { id: 6, type: 'time_spent', authorId: 3, content: 'Added 4h of time spent', createdAt: '2026-03-15T17:00:00Z' }
        ]
    },
    {
        id: 2, iid: 102, title: 'OAuth token refresh fails silently after 30 days',
        description: 'OAuth refresh tokens expire after 30 days but the client library doesn\'t handle the expiry gracefully. Users get logged out without warning.',
        state: 'opened', type: 'issue', authorId: 2, assignees: [3], labels: [1, 5, 12],
        milestoneId: 3, iterationId: 5, epicId: 1, weight: 4, dueDate: '2026-03-28',
        confidential: false, timeEstimate: 21600, timeSpent: 7200,
        createdAt: '2026-03-08T11:00:00Z', updatedAt: '2026-03-16T09:30:00Z',
        closedAt: null, closedBy: null, upvotes: 8, downvotes: 0, subscribed: true,
        relatedIssues: [{ issueId: 1, linkType: 'is_blocked_by' }],
        activities: [
            { id: 7, type: 'comment', authorId: 3, content: 'Need to add token refresh retry logic with exponential backoff.', createdAt: '2026-03-09T10:00:00Z' },
            { id: 8, type: 'milestone_change', authorId: 2, content: 'Changed milestone to v4.2 Release', createdAt: '2026-03-08T11:05:00Z' }
        ]
    },
    {
        id: 3, iid: 103, title: 'Implement MFA enrollment flow for TOTP authenticators',
        description: 'Add the ability for users to enroll in multi-factor authentication using TOTP apps (Google Authenticator, Authy, etc.).\n\n## Acceptance Criteria\n- [ ] QR code generation for secret key\n- [ ] Manual secret key entry option\n- [ ] Verification step with 6-digit code\n- [ ] Recovery codes generation (10 codes)\n- [ ] Backup codes download as text file',
        state: 'opened', type: 'issue', authorId: 1, assignees: [4, 5], labels: [2, 5, 15],
        milestoneId: 3, iterationId: 5, epicId: 1, weight: 8, dueDate: '2026-04-05',
        confidential: false, timeEstimate: 57600, timeSpent: 28800,
        createdAt: '2026-02-15T09:00:00Z', updatedAt: '2026-03-17T11:20:00Z',
        closedAt: null, closedBy: null, upvotes: 15, downvotes: 0, subscribed: true,
        relatedIssues: [{ issueId: 8, linkType: 'relates_to' }],
        activities: [
            { id: 9, type: 'comment', authorId: 4, content: 'QR code generation is done. Working on the verification step now.', createdAt: '2026-03-05T15:00:00Z' },
            { id: 10, type: 'label_add', authorId: 1, content: 'Added label ~"status::in-progress"', createdAt: '2026-03-01T09:00:00Z' },
            { id: 11, type: 'time_spent', authorId: 4, content: 'Added 8h of time spent', createdAt: '2026-03-10T17:00:00Z' }
        ]
    },
    {
        id: 4, iid: 104, title: 'Database query N+1 issue in project listing endpoint',
        description: 'The `/api/v2/projects` endpoint makes N+1 queries when loading project members. With 200+ projects, response time exceeds 5 seconds.',
        state: 'opened', type: 'issue', authorId: 6, assignees: [6], labels: [1, 6, 12, 20],
        milestoneId: 3, iterationId: 5, epicId: 4, weight: 3, dueDate: '2026-03-22',
        confidential: false, timeEstimate: 14400, timeSpent: 10800,
        createdAt: '2026-03-01T14:00:00Z', updatedAt: '2026-03-17T10:00:00Z',
        closedAt: null, closedBy: null, upvotes: 6, downvotes: 0, subscribed: false,
        relatedIssues: [],
        activities: [
            { id: 12, type: 'comment', authorId: 6, content: 'Using eager loading reduced query count from 203 to 4. PR #847 is up.', createdAt: '2026-03-15T16:00:00Z' },
            { id: 13, type: 'label_add', authorId: 6, content: 'Added label ~"status::review"', createdAt: '2026-03-15T16:05:00Z' }
        ]
    },
    {
        id: 5, iid: 105, title: 'Add responsive navigation menu for mobile viewports',
        description: 'The main navigation menu is not usable on screens smaller than 768px. Implement a hamburger menu with slide-out drawer.',
        state: 'opened', type: 'issue', authorId: 1, assignees: [7, 4], labels: [2, 22, 21, 13],
        milestoneId: 4, iterationId: 6, epicId: 5, weight: 5, dueDate: '2026-04-20',
        confidential: false, timeEstimate: 36000, timeSpent: 0,
        createdAt: '2026-03-05T10:00:00Z', updatedAt: '2026-03-18T09:15:00Z',
        closedAt: null, closedBy: null, upvotes: 4, downvotes: 0, subscribed: true,
        relatedIssues: [{ issueId: 6, linkType: 'relates_to' }],
        activities: [
            { id: 14, type: 'assignment', authorId: 2, content: 'Assigned to @dthompson and @akim', createdAt: '2026-03-18T09:15:00Z' },
            { id: 15, type: 'comment', authorId: 7, content: 'Starting wireframes this week.', createdAt: '2026-03-18T09:30:00Z' }
        ]
    },
    {
        id: 6, iid: 106, title: 'Table component overflows on screens below 1024px',
        description: 'Data tables with more than 6 columns overflow horizontally without scroll indicator on medium screens.',
        state: 'opened', type: 'issue', authorId: 8, assignees: [4], labels: [1, 22, 21, 13],
        milestoneId: 4, iterationId: null, epicId: 5, weight: 2, dueDate: '2026-04-25',
        confidential: false, timeEstimate: 7200, timeSpent: 0,
        createdAt: '2026-03-12T11:30:00Z', updatedAt: '2026-03-12T11:30:00Z',
        closedAt: null, closedBy: null, upvotes: 3, downvotes: 0, subscribed: false,
        relatedIssues: [{ issueId: 5, linkType: 'relates_to' }],
        activities: []
    },
    {
        id: 7, iid: 107, title: 'Migrate /api/v2/users endpoints to v3 format',
        description: 'Update the users API endpoints to use the v3 response format:\n- Snake case to camel case field names\n- Nested user profile object\n- Pagination via cursor instead of offset\n- Rate limit headers in response',
        state: 'opened', type: 'issue', authorId: 2, assignees: [9], labels: [2, 24, 15],
        milestoneId: 4, iterationId: 6, epicId: 2, weight: 5, dueDate: '2026-04-15',
        confidential: false, timeEstimate: 43200, timeSpent: 21600,
        createdAt: '2026-02-20T13:00:00Z', updatedAt: '2026-03-16T15:00:00Z',
        closedAt: null, closedBy: null, upvotes: 2, downvotes: 0, subscribed: false,
        relatedIssues: [{ issueId: 10, linkType: 'blocks' }],
        activities: [
            { id: 16, type: 'comment', authorId: 9, content: 'User listing endpoint migrated. Working on user detail and update endpoints now.', createdAt: '2026-03-10T11:00:00Z' },
            { id: 17, type: 'label_add', authorId: 9, content: 'Added label ~"status::in-progress"', createdAt: '2026-03-05T09:00:00Z' }
        ]
    },
    {
        id: 8, iid: 108, title: 'XSS vulnerability in Markdown preview renderer',
        description: 'The Markdown preview does not properly sanitize script tags in code blocks when using certain Unicode escape sequences.\n\n**Severity:** High\n**CVSS:** 7.1\n**Vector:** Network',
        state: 'opened', type: 'incident', authorId: 11, assignees: [2, 11], labels: [5, 11, 23],
        milestoneId: 3, iterationId: 5, epicId: 8, weight: 8, dueDate: '2026-03-20',
        confidential: true, timeEstimate: 14400, timeSpent: 10800,
        createdAt: '2026-03-14T07:00:00Z', updatedAt: '2026-03-17T18:00:00Z',
        closedAt: null, closedBy: null, upvotes: 0, downvotes: 0, subscribed: true,
        relatedIssues: [{ issueId: 1, linkType: 'relates_to' }, { issueId: 3, linkType: 'relates_to' }],
        activities: [
            { id: 18, type: 'comment', authorId: 11, content: 'Patched the HTML sanitizer. Need security team review before merge.', createdAt: '2026-03-15T16:00:00Z' },
            { id: 19, type: 'label_add', authorId: 4, content: 'Added label ~"priority::critical"', createdAt: '2026-03-17T14:20:00Z' }
        ]
    },
    {
        id: 9, iid: 109, title: 'Add dark mode CSS custom properties',
        description: 'Define CSS custom properties (variables) for all color tokens to support dark mode theming.\n\n## Tasks\n- [x] Audit existing color usage\n- [x] Define light mode variables\n- [ ] Define dark mode variables\n- [ ] Add theme toggle component\n- [ ] Test contrast ratios',
        state: 'opened', type: 'issue', authorId: 4, assignees: [4], labels: [2, 21, 19],
        milestoneId: 4, iterationId: null, epicId: 9, weight: 5, dueDate: '2026-05-01',
        confidential: false, timeEstimate: 28800, timeSpent: 14400,
        createdAt: '2026-03-01T10:00:00Z', updatedAt: '2026-03-14T16:00:00Z',
        closedAt: null, closedBy: null, upvotes: 18, downvotes: 1, subscribed: false,
        relatedIssues: [],
        activities: [
            { id: 20, type: 'comment', authorId: 4, content: 'Light mode variables are done. 147 color tokens defined. Starting dark mode mapping.', createdAt: '2026-03-14T16:00:00Z' }
        ]
    },
    {
        id: 10, iid: 110, title: 'Write API v3 migration guide for external consumers',
        description: 'Create comprehensive migration guide for API consumers transitioning from v2 to v3. Include code examples in Python, JavaScript, Ruby, and Go.',
        state: 'opened', type: 'task', authorId: 8, assignees: [8, 10], labels: [4, 13],
        milestoneId: 4, iterationId: null, epicId: 3, weight: 3, dueDate: '2026-05-15',
        confidential: false, timeEstimate: 21600, timeSpent: 3600,
        createdAt: '2026-03-01T14:00:00Z', updatedAt: '2026-03-10T11:00:00Z',
        closedAt: null, closedBy: null, upvotes: 5, downvotes: 0, subscribed: false,
        relatedIssues: [{ issueId: 7, linkType: 'is_blocked_by' }],
        activities: []
    },
    // --- Recently closed issues ---
    {
        id: 11, iid: 111, title: 'Fix timezone handling in scheduled reports',
        description: 'Scheduled reports use server timezone instead of user\'s configured timezone. Reports generated at wrong times for non-UTC users.',
        state: 'closed', type: 'issue', authorId: 10, assignees: [5], labels: [1, 12, 18],
        milestoneId: 3, iterationId: 4, epicId: null, weight: 3, dueDate: '2026-03-15',
        confidential: false, timeEstimate: 14400, timeSpent: 10800,
        createdAt: '2026-02-28T09:00:00Z', updatedAt: '2026-03-14T17:00:00Z',
        closedAt: '2026-03-14T17:00:00Z', closedBy: 5, upvotes: 4, downvotes: 0, subscribed: false,
        relatedIssues: [],
        activities: [
            { id: 21, type: 'status_change', authorId: 5, content: 'Closed this issue', createdAt: '2026-03-14T17:00:00Z' },
            { id: 22, type: 'comment', authorId: 5, content: 'Fixed in commit a4f8c2d. All date-time operations now use the user\'s timezone preference.', createdAt: '2026-03-14T16:55:00Z' }
        ]
    },
    {
        id: 12, iid: 112, title: 'Optimize Docker image size — reduce from 1.2GB to under 400MB',
        description: 'Production Docker image is 1.2GB due to dev dependencies and unneeded build artifacts. Target: under 400MB using multi-stage builds.',
        state: 'closed', type: 'issue', authorId: 11, assignees: [11], labels: [6, 7, 18],
        milestoneId: 3, iterationId: 3, epicId: null, weight: 3, dueDate: '2026-03-01',
        confidential: false, timeEstimate: 21600, timeSpent: 18000,
        createdAt: '2026-02-10T10:00:00Z', updatedAt: '2026-03-18T08:30:00Z',
        closedAt: '2026-02-28T16:00:00Z', closedBy: 11, upvotes: 7, downvotes: 0, subscribed: false,
        relatedIssues: [],
        activities: [
            { id: 23, type: 'status_change', authorId: 11, content: 'Closed this issue', createdAt: '2026-02-28T16:00:00Z' },
            { id: 24, type: 'comment', authorId: 11, content: 'Final image size: 347MB. Used multi-stage build with Alpine base.', createdAt: '2026-02-28T15:55:00Z' },
            { id: 25, type: 'comment', authorId: 3, content: '@ppatel mentioned you in #112 — Great work on this optimization!', createdAt: '2026-03-18T08:30:00Z' }
        ]
    },
    {
        id: 13, iid: 113, title: 'Add Redis caching layer for session management',
        description: 'Replace in-memory session store with Redis for horizontal scaling support. Must handle session serialization for complex user preference objects.',
        state: 'closed', type: 'issue', authorId: 6, assignees: [6, 9], labels: [6, 7, 20, 18],
        milestoneId: 2, iterationId: 2, epicId: 4, weight: 5, dueDate: '2026-02-15',
        confidential: false, timeEstimate: 36000, timeSpent: 32400,
        createdAt: '2026-01-15T11:00:00Z', updatedAt: '2026-02-14T18:00:00Z',
        closedAt: '2026-02-14T18:00:00Z', closedBy: 6, upvotes: 9, downvotes: 0, subscribed: false,
        relatedIssues: [],
        activities: [
            { id: 26, type: 'status_change', authorId: 6, content: 'Closed this issue', createdAt: '2026-02-14T18:00:00Z' }
        ]
    },
    {
        id: 14, iid: 114, title: 'Implement rate limiting for public API endpoints',
        description: 'Add rate limiting:\n- Anonymous: 60 req/min\n- Authenticated: 600 req/min\n- Premium: 6000 req/min\n\nReturn `X-RateLimit-*` headers.',
        state: 'closed', type: 'issue', authorId: 2, assignees: [2], labels: [5, 7, 18],
        milestoneId: 2, iterationId: 1, epicId: null, weight: 4, dueDate: '2026-01-30',
        confidential: false, timeEstimate: 28800, timeSpent: 25200,
        createdAt: '2026-01-10T09:00:00Z', updatedAt: '2026-01-29T17:00:00Z',
        closedAt: '2026-01-29T17:00:00Z', closedBy: 2, upvotes: 11, downvotes: 0, subscribed: false,
        relatedIssues: [],
        activities: [
            { id: 27, type: 'status_change', authorId: 2, content: 'Closed this issue', createdAt: '2026-01-29T17:00:00Z' }
        ]
    },
    {
        id: 15, iid: 115, title: 'Parallel test execution in CI pipeline',
        description: 'Split test suite across 4 parallel runners to reduce CI pipeline duration from 45 minutes to under 15 minutes.',
        state: 'opened', type: 'issue', authorId: 11, assignees: [11, 1], labels: [3, 7, 15],
        milestoneId: 4, iterationId: 5, epicId: 6, weight: 5, dueDate: '2026-04-01',
        confidential: false, timeEstimate: 36000, timeSpent: 18000,
        createdAt: '2026-02-25T10:00:00Z', updatedAt: '2026-03-17T11:00:00Z',
        closedAt: null, closedBy: null, upvotes: 13, downvotes: 0, subscribed: true,
        relatedIssues: [],
        activities: [
            { id: 28, type: 'comment', authorId: 11, content: 'Test splitting configuration done. Average pipeline now at 18 minutes. Optimizing further.', createdAt: '2026-03-15T14:00:00Z' }
        ]
    },
    // --- More varied issues ---
    {
        id: 16, iid: 116, title: 'Form validation errors not announced to screen readers',
        description: 'When form validation fails, error messages appear visually but are not announced by screen readers. Need to add aria-live regions and proper ARIA attributes.',
        state: 'opened', type: 'issue', authorId: 3, assignees: [3], labels: [1, 22, 21, 13],
        milestoneId: 5, iterationId: null, epicId: 10, weight: 3, dueDate: null,
        confidential: false, timeEstimate: 14400, timeSpent: 0,
        createdAt: '2026-03-10T09:00:00Z', updatedAt: '2026-03-10T09:00:00Z',
        closedAt: null, closedBy: null, upvotes: 2, downvotes: 0, subscribed: false,
        relatedIssues: [], activities: []
    },
    {
        id: 17, iid: 117, title: 'Implement canary deployment strategy for production releases',
        description: 'Set up canary deployments that route 5% of traffic to new version before full rollout. Integrate with monitoring to auto-rollback on error rate spike.',
        state: 'opened', type: 'issue', authorId: 11, assignees: [], labels: [2, 7, 12],
        milestoneId: 4, iterationId: null, epicId: 6, weight: 8, dueDate: '2026-05-15',
        confidential: false, timeEstimate: 57600, timeSpent: 0,
        createdAt: '2026-03-08T14:00:00Z', updatedAt: '2026-03-08T14:00:00Z',
        closedAt: null, closedBy: null, upvotes: 6, downvotes: 0, subscribed: false,
        relatedIssues: [], activities: []
    },
    {
        id: 18, iid: 118, title: 'Refactor notification delivery to use message queue',
        description: 'Current synchronous notification sending blocks request threads. Move to async processing with RabbitMQ or similar.',
        state: 'opened', type: 'issue', authorId: 6, assignees: [6], labels: [3, 20, 10],
        milestoneId: 4, iterationId: 6, epicId: 12, weight: 5, dueDate: '2026-05-01',
        confidential: false, timeEstimate: 43200, timeSpent: 7200,
        createdAt: '2026-03-05T11:00:00Z', updatedAt: '2026-03-16T14:00:00Z',
        closedAt: null, closedBy: null, upvotes: 3, downvotes: 0, subscribed: false,
        relatedIssues: [], activities: [
            { id: 29, type: 'milestone_change', authorId: 2, content: 'Changed milestone to v4.2 Release', createdAt: '2026-03-15T15:00:00Z' }
        ]
    },
    {
        id: 19, iid: 119, title: 'CSV export generates corrupted files for records with commas in fields',
        description: 'Exporting data to CSV does not properly escape fields containing commas, leading to column misalignment. Need to wrap fields in quotes.',
        state: 'opened', type: 'issue', authorId: 10, assignees: [5], labels: [1, 14],
        milestoneId: 6, iterationId: null, epicId: null, weight: 1, dueDate: null,
        confidential: false, timeEstimate: 3600, timeSpent: 0,
        createdAt: '2026-03-15T10:00:00Z', updatedAt: '2026-03-15T10:00:00Z',
        closedAt: null, closedBy: null, upvotes: 1, downvotes: 0, subscribed: false,
        relatedIssues: [], activities: []
    },
    {
        id: 20, iid: 120, title: 'Add keyboard shortcuts for common actions (j/k navigation, e to edit)',
        description: 'Implement Gmail-style keyboard shortcuts:\n- `j`/`k` to navigate up/down in lists\n- `e` to edit selected item\n- `c` to create new issue\n- `?` to show shortcut help\n- `Esc` to close modals/panels',
        state: 'opened', type: 'issue', authorId: 4, assignees: [4], labels: [2, 22, 14],
        milestoneId: 6, iterationId: null, epicId: null, weight: 3, dueDate: null,
        confidential: false, timeEstimate: 21600, timeSpent: 0,
        createdAt: '2026-03-07T16:00:00Z', updatedAt: '2026-03-07T16:00:00Z',
        closedAt: null, closedBy: null, upvotes: 22, downvotes: 2, subscribed: false,
        relatedIssues: [], activities: []
    },
    {
        id: 21, iid: 121, title: 'Memory leak in WebSocket connection manager',
        description: 'The WebSocket connection manager does not properly clean up event listeners when connections are closed, leading to memory growth over time. Production instances hit 4GB after 48 hours.',
        state: 'opened', type: 'incident', authorId: 6, assignees: [6, 2], labels: [1, 6, 11],
        milestoneId: 3, iterationId: 5, epicId: null, weight: 5, dueDate: '2026-03-21',
        confidential: false, timeEstimate: 21600, timeSpent: 14400,
        createdAt: '2026-03-13T06:00:00Z', updatedAt: '2026-03-17T12:00:00Z',
        closedAt: null, closedBy: null, upvotes: 8, downvotes: 0, subscribed: true,
        relatedIssues: [],
        activities: [
            { id: 30, type: 'comment', authorId: 6, content: 'Found the leak. WeakRef map for listeners should fix it. Testing now.', createdAt: '2026-03-16T10:00:00Z' },
            { id: 31, type: 'label_add', authorId: 6, content: 'Added label ~"priority::critical"', createdAt: '2026-03-13T06:05:00Z' }
        ]
    },
    {
        id: 22, iid: 122, title: 'Upgrade PostgreSQL from 14 to 16',
        description: 'Upgrade production PostgreSQL from 14.8 to 16.2. Includes testing logical replication, pg_dump compatibility, and extension support.\n\nBlocked until the Redis migration (#13) is complete to avoid concurrent infrastructure changes.',
        state: 'closed', type: 'issue', authorId: 11, assignees: [11], labels: [7, 3, 18],
        milestoneId: 3, iterationId: 4, epicId: null, weight: 5, dueDate: '2026-03-10',
        confidential: false, timeEstimate: 28800, timeSpent: 36000,
        createdAt: '2026-02-15T10:00:00Z', updatedAt: '2026-03-17T17:45:00Z',
        closedAt: '2026-03-09T18:00:00Z', closedBy: 11, upvotes: 5, downvotes: 0, subscribed: false,
        relatedIssues: [],
        activities: [
            { id: 32, type: 'comment', authorId: 6, content: 'Elena Rodriguez closed issue #122', createdAt: '2026-03-17T17:45:00Z' },
            { id: 33, type: 'status_change', authorId: 11, content: 'Closed this issue', createdAt: '2026-03-09T18:00:00Z' }
        ]
    },
    {
        id: 23, iid: 123, title: 'Implement email digest notification option',
        description: 'Allow users to receive a daily or weekly email digest instead of individual notification emails. Should aggregate by project.',
        state: 'opened', type: 'issue', authorId: 8, assignees: [], labels: [2, 13],
        milestoneId: null, iterationId: null, epicId: 12, weight: 5, dueDate: null,
        confidential: false, timeEstimate: 36000, timeSpent: 0,
        createdAt: '2026-03-06T15:00:00Z', updatedAt: '2026-03-06T15:00:00Z',
        closedAt: null, closedBy: null, upvotes: 9, downvotes: 0, subscribed: false,
        relatedIssues: [], activities: []
    },
    {
        id: 24, iid: 124, title: 'Broken pagination on filtered issue lists',
        description: 'When applying label or assignee filters to issue lists, the pagination component shows incorrect total count. Page 2+ returns unfiltered results.',
        state: 'opened', type: 'issue', authorId: 10, assignees: [7], labels: [1, 21, 12],
        milestoneId: 3, iterationId: 5, epicId: null, weight: 3, dueDate: '2026-03-25',
        confidential: false, timeEstimate: 10800, timeSpent: 3600,
        createdAt: '2026-03-11T14:00:00Z', updatedAt: '2026-03-16T09:00:00Z',
        closedAt: null, closedBy: null, upvotes: 4, downvotes: 0, subscribed: false,
        relatedIssues: [],
        activities: [
            { id: 34, type: 'comment', authorId: 7, content: 'The issue is in the SQL query builder — filter params are not passed to the count query.', createdAt: '2026-03-15T11:00:00Z' }
        ]
    },
    {
        id: 25, iid: 125, title: 'Add Slack integration for issue status change notifications',
        description: 'Send Slack messages to configured channels when issue status changes (opened, closed, reopened). Support webhook and bot token methods.',
        state: 'opened', type: 'issue', authorId: 9, assignees: [9], labels: [2, 20, 13],
        milestoneId: null, iterationId: null, epicId: 12, weight: 5, dueDate: null,
        confidential: false, timeEstimate: 28800, timeSpent: 0,
        createdAt: '2026-03-02T10:00:00Z', updatedAt: '2026-03-02T10:00:00Z',
        closedAt: null, closedBy: null, upvotes: 7, downvotes: 0, subscribed: false,
        relatedIssues: [], activities: []
    },
    // --- Older closed issues ---
    {
        id: 26, iid: 126, title: 'Fix CORS configuration for staging environment',
        description: 'CORS headers are not set correctly for the staging domain, breaking API calls from the staging frontend.',
        state: 'closed', type: 'issue', authorId: 5, assignees: [5], labels: [1, 7, 18],
        milestoneId: 2, iterationId: 2, epicId: null, weight: 2, dueDate: '2026-02-10',
        confidential: false, timeEstimate: 7200, timeSpent: 5400,
        createdAt: '2026-02-05T09:00:00Z', updatedAt: '2026-02-09T16:00:00Z',
        closedAt: '2026-02-09T16:00:00Z', closedBy: 5, upvotes: 2, downvotes: 0, subscribed: false,
        relatedIssues: [], activities: [{ id: 35, type: 'status_change', authorId: 5, content: 'Closed this issue', createdAt: '2026-02-09T16:00:00Z' }]
    },
    {
        id: 27, iid: 127, title: 'Implement project data export in JSON format',
        description: 'Allow project owners to export all project data (issues, milestones, labels, boards) as a JSON file.',
        state: 'closed', type: 'issue', authorId: 9, assignees: [9], labels: [2, 20, 18],
        milestoneId: 1, iterationId: null, epicId: 11, weight: 5, dueDate: '2025-11-30',
        confidential: false, timeEstimate: 36000, timeSpent: 32400,
        createdAt: '2025-10-15T10:00:00Z', updatedAt: '2025-11-28T17:00:00Z',
        closedAt: '2025-11-28T17:00:00Z', closedBy: 9, upvotes: 4, downvotes: 0, subscribed: false,
        relatedIssues: [], activities: [{ id: 36, type: 'status_change', authorId: 9, content: 'Closed this issue', createdAt: '2025-11-28T17:00:00Z' }]
    },
    {
        id: 28, iid: 128, title: 'Add CSV import for bulk issue creation',
        description: 'Support bulk creation of issues via CSV upload. Map columns to issue fields (title, description, assignee, labels, milestone).',
        state: 'closed', type: 'issue', authorId: 8, assignees: [9, 5], labels: [2, 18],
        milestoneId: 1, iterationId: null, epicId: 11, weight: 5, dueDate: '2025-11-15',
        confidential: false, timeEstimate: 43200, timeSpent: 39600,
        createdAt: '2025-10-01T11:00:00Z', updatedAt: '2025-11-14T16:00:00Z',
        closedAt: '2025-11-14T16:00:00Z', closedBy: 9, upvotes: 6, downvotes: 0, subscribed: false,
        relatedIssues: [], activities: [{ id: 37, type: 'status_change', authorId: 9, content: 'Closed this issue', createdAt: '2025-11-14T16:00:00Z' }]
    },
    {
        id: 29, iid: 129, title: 'GraphQL schema validation fails on nested nullable types',
        description: 'The GraphQL schema generator produces invalid schema definitions when a type has nested nullable fields within a non-nullable parent.',
        state: 'opened', type: 'issue', authorId: 7, assignees: [7], labels: [1, 20, 12],
        milestoneId: 3, iterationId: 5, epicId: 2, weight: 3, dueDate: '2026-03-28',
        confidential: false, timeEstimate: 14400, timeSpent: 7200,
        createdAt: '2026-03-09T13:00:00Z', updatedAt: '2026-03-15T10:00:00Z',
        closedAt: null, closedBy: null, upvotes: 3, downvotes: 0, subscribed: false,
        relatedIssues: [],
        activities: [
            { id: 38, type: 'comment', authorId: 7, content: 'Root cause found in the type resolver. Fix ready for review.', createdAt: '2026-03-15T10:00:00Z' }
        ]
    },
    {
        id: 30, iid: 130, title: 'Implement burndown chart for iteration view',
        description: 'Add a burndown chart to the iteration detail page showing:\n- Ideal burndown line\n- Actual progress line\n- Added scope indicator\n- Daily data points',
        state: 'opened', type: 'issue', authorId: 1, assignees: [4], labels: [2, 21, 13],
        milestoneId: 4, iterationId: null, epicId: null, weight: 5, dueDate: '2026-04-30',
        confidential: false, timeEstimate: 28800, timeSpent: 0,
        createdAt: '2026-03-04T09:00:00Z', updatedAt: '2026-03-16T16:30:00Z',
        closedAt: null, closedBy: null, upvotes: 11, downvotes: 0, subscribed: false,
        relatedIssues: [],
        activities: [
            { id: 39, type: 'comment', authorId: 9, content: 'Omar Hassan mentioned you in #130', createdAt: '2026-03-16T16:30:00Z' }
        ]
    }
];

// Generate additional issues for realistic volume
(function generateAdditionalIssues() {
    const titles = [
        'Update dependency versions for security patches',
        'Add input validation for user registration form',
        'Fix race condition in concurrent file uploads',
        'Implement audit log for admin actions',
        'Add support for custom fields on issues',
        'Optimize front-end bundle size — target under 500KB',
        'Fix incorrect sort order in milestone issue list',
        'Add two-factor authentication backup via SMS',
        'Implement project archiving functionality',
        'Add real-time collaboration indicators (who is viewing)',
        'Fix email notification formatting on Outlook clients',
        'Create onboarding wizard for new project setup',
        'Add support for issue templates with custom fields',
        'Implement webhook retry logic with exponential backoff',
        'Fix memory usage spike during large file diff generation',
        'Add API endpoint for bulk label operations',
        'Implement user activity heatmap on profile page',
        'Fix timezone display inconsistency in activity feed',
        'Add support for nested task lists in issue descriptions',
        'Implement auto-assignment rules based on labels',
        'Fix search indexing delay for newly created issues',
        'Add merge request integration to issue sidebar',
        'Implement custom notification rules per label',
        'Fix API rate limiter not resetting on sliding window',
        'Add project template cloning functionality',
        'Implement issue weight auto-estimation using ML',
        'Fix broken links in exported PDF reports',
        'Add support for emoji reactions on comments',
        'Implement board swimlanes by assignee',
        'Fix incorrect character count in description editor',
        'Add support for time tracking via slash commands',
        'Implement label priority ordering',
        'Fix SSO session not invalidating on password change',
        'Add project-level notification preferences',
        'Implement drag-and-drop file attachments',
        'Fix flaky integration tests in CI pipeline',
        'Add burnup chart alongside burndown',
        'Implement cross-project issue search',
        'Fix PostgreSQL connection pool exhaustion under load',
        'Add support for relating merge requests to epics',
        'Implement group-level issue analytics dashboard',
        'Fix incorrect date parsing for DD/MM/YYYY format users',
        'Add configurable auto-close rules for stale issues',
        'Implement comment threading and replies',
        'Fix CSS grid layout breaking in Safari 15',
        'Add batch operations for iteration assignment',
        'Implement read-only project mode for archived projects',
        'Fix GraphQL subscription memory leak',
        'Add support for custom dashboard widgets',
        'Implement issue dependency graph visualization',
        'Fix slow query in milestone progress calculation',
        'Add API v3 endpoint for board management',
        'Implement workspace-level label management',
        'Fix Unicode normalization issues in search',
        'Add support for confidential comments on public issues',
        'Implement automated regression detection in CI',
        'Fix websocket reconnection loop on network change',
        'Add support for multiple assignee workflow rules',
        'Implement label-based SLA tracking',
        'Fix pagination cursor encoding for non-ASCII characters',
        'Add health check endpoint for load balancer',
        'Implement project forking with issue reference linking',
        'Fix incorrect diff rendering for binary files',
        'Add support for scheduled issue creation',
        'Implement configurable issue numbering schemes',
        'Fix localStorage quota exceeded error on large projects',
        'Add keyboard navigation for board view',
        'Implement epic roadmap PDF export',
        'Fix time tracking widget not updating in real-time',
        'Add integration tests for OAuth flow'
    ];
    const descriptions = [
        'This needs investigation and implementation. See related tickets for context.',
        'Reported by multiple users. Priority should be set based on impact assessment.',
        'Follow up from the last sprint review. Needs design review before implementation.',
        'Tech debt item identified during code review. Should be addressed before next release.',
        'Customer-facing issue reported via support ticket #8472.',
        'Performance regression identified in latest monitoring dashboard.',
        'Compliance requirement from security team audit.',
        'Feature request from product roadmap discussion.',
        'Infrastructure improvement for better reliability.',
        'UX improvement based on user research findings.'
    ];
    const states = ['opened', 'opened', 'opened', 'opened', 'opened', 'closed', 'closed', 'closed'];
    const types = ['issue', 'issue', 'issue', 'issue', 'task', 'task', 'incident'];
    const weights = [null, 1, 1, 2, 2, 3, 3, 3, 5, 5, 8];

    let nextId = 31;
    for (let i = 0; i < titles.length; i++) {
        const state = states[i % states.length];
        const authorId = (i % 11) + 1;
        const numAssignees = Math.random() < 0.3 ? 0 : Math.random() < 0.7 ? 1 : 2;
        const assignees = [];
        for (let a = 0; a < numAssignees; a++) {
            let aId = ((i + a * 3) % 11) + 1;
            if (!assignees.includes(aId)) assignees.push(aId);
        }
        const numLabels = Math.floor(Math.random() * 3) + 1;
        const labelSet = new Set();
        for (let l = 0; l < numLabels; l++) {
            labelSet.add(Math.floor(Math.random() * 24) + 1);
        }
        const milestoneId = Math.random() < 0.6 ? [3, 4, 5, 6][Math.floor(Math.random() * 4)] : null;
        const iterationId = Math.random() < 0.4 ? [4, 5, 6][Math.floor(Math.random() * 3)] : null;
        const epicId = Math.random() < 0.3 ? Math.floor(Math.random() * 12) + 1 : null;
        const daysAgo = Math.floor(Math.random() * 90) + 1;
        const createdDate = new Date(2026, 2, 18);
        createdDate.setDate(createdDate.getDate() - daysAgo);
        const updatedDate = new Date(createdDate);
        updatedDate.setDate(updatedDate.getDate() + Math.floor(Math.random() * Math.min(daysAgo, 30)));
        const closedAt = state === 'closed' ? updatedDate.toISOString() : null;
        const closedBy = state === 'closed' ? assignees[0] || authorId : null;
        const dueDate = Math.random() < 0.5 ? (() => {
            const d = new Date(createdDate);
            d.setDate(d.getDate() + Math.floor(Math.random() * 60) + 7);
            return d.toISOString().split('T')[0];
        })() : null;
        const weight = weights[Math.floor(Math.random() * weights.length)];
        const te = Math.random() < 0.4 ? (Math.floor(Math.random() * 10) + 1) * 3600 : null;
        const ts = te && Math.random() < 0.6 ? Math.floor(te * Math.random()) : 0;

        ISSUES.push({
            id: nextId,
            iid: 100 + nextId,
            title: titles[i],
            description: descriptions[i % descriptions.length],
            state: state,
            type: types[i % types.length],
            authorId: authorId,
            assignees: assignees,
            labels: Array.from(labelSet),
            milestoneId: milestoneId,
            iterationId: iterationId,
            epicId: epicId,
            weight: weight,
            dueDate: dueDate,
            confidential: Math.random() < 0.05,
            timeEstimate: te,
            timeSpent: ts,
            createdAt: createdDate.toISOString(),
            updatedAt: updatedDate.toISOString(),
            closedAt: closedAt,
            closedBy: closedBy,
            upvotes: Math.floor(Math.random() * 15),
            downvotes: Math.floor(Math.random() * 3),
            subscribed: Math.random() < 0.2,
            relatedIssues: [],
            activities: []
        });
        nextId++;
    }
})();

// ── Sort Options ───────────────────────────────────────────
const SORT_OPTIONS = [
    { value: 'created_desc', label: 'Created date (newest)' },
    { value: 'created_asc', label: 'Created date (oldest)' },
    { value: 'updated_desc', label: 'Updated date (newest)' },
    { value: 'updated_asc', label: 'Updated date (oldest)' },
    { value: 'due_date_asc', label: 'Due date (soonest)' },
    { value: 'due_date_desc', label: 'Due date (latest)' },
    { value: 'priority_desc', label: 'Priority (highest)' },
    { value: 'priority_asc', label: 'Priority (lowest)' },
    { value: 'popularity_desc', label: 'Popularity (most)' },
    { value: 'weight_desc', label: 'Weight (heaviest)' },
    { value: 'weight_asc', label: 'Weight (lightest)' }
];

const ISSUE_TYPES = [
    { value: 'issue', label: 'Issue' },
    { value: 'incident', label: 'Incident' },
    { value: 'task', label: 'Task' }
];
