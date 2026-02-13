// ============================================================
// state.js — Centralized state management with localStorage persistence
// ============================================================

const STORAGE_KEY = 'gitlabOrgAppState';

function _loadSeedData() {
    return {
        _seedVersion: SEED_DATA_VERSION,
        currentUser: JSON.parse(JSON.stringify(CURRENT_USER)),
        users: JSON.parse(JSON.stringify(USERS)),
        organizations: JSON.parse(JSON.stringify(ORGANIZATIONS)),
        groups: JSON.parse(JSON.stringify(GROUPS)),
        projects: JSON.parse(JSON.stringify(PROJECTS)),
        groupMemberships: JSON.parse(JSON.stringify(GROUP_MEMBERSHIPS)),
        projectMemberships: JSON.parse(JSON.stringify(PROJECT_MEMBERSHIPS)),
        groupShares: JSON.parse(JSON.stringify(GROUP_SHARES)),
        projectShares: JSON.parse(JSON.stringify(PROJECT_SHARES)),
        _nextUserId: 13,
        _nextGroupId: 15,
        _nextProjectId: 21,
        _nextOrgId: 3
    };
}

function _loadPersistedData() {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (!raw) {
            console.log('[AppState] No persisted data found, using seed data');
            return null;
        }
        const parsed = JSON.parse(raw);
        // Invalidate stale localStorage when seed data has been updated
        if (parsed._seedVersion !== SEED_DATA_VERSION) {
            console.log('[AppState] Seed data version changed, discarding stale localStorage');
            localStorage.removeItem(STORAGE_KEY);
            return null;
        }
        console.log('[AppState] Loaded persisted data — groups:', parsed.groups?.length, 'projects:', parsed.projects?.length);
        return parsed;
    } catch (e) {
        console.error('[AppState] Failed to load persisted data:', e);
        return null;
    }
}

const _initial = _loadPersistedData() || _loadSeedData();

const AppState = {
    currentUser: _initial.currentUser,
    users: _initial.users,
    organizations: _initial.organizations,
    groups: _initial.groups,
    projects: _initial.projects,
    groupMemberships: _initial.groupMemberships,
    projectMemberships: _initial.projectMemberships,
    groupShares: _initial.groupShares,
    projectShares: _initial.projectShares,

    // Seed data version (persisted to detect stale localStorage)
    _seedVersion: _initial._seedVersion,

    // UI state (transient — not persisted)
    currentRoute: '/',
    routeParams: {},
    sidebarOpen: true,
    modalOpen: false,
    validationErrors: {},
    toasts: [],

    // Counters for new IDs
    _nextUserId: _initial._nextUserId,
    _nextGroupId: _initial._nextGroupId,
    _nextProjectId: _initial._nextProjectId,
    _nextOrgId: _initial._nextOrgId,

    // Listeners
    _listeners: [],

    subscribe(fn) {
        this._listeners.push(fn);
        return () => {
            this._listeners = this._listeners.filter(l => l !== fn);
        };
    },

    notify() {
        this._listeners.forEach(fn => fn(this));
        this._persist();
    },

    // ---- Persistence ----

    _getPersistable() {
        return {
            _seedVersion: this._seedVersion,
            currentUser: this.currentUser,
            users: this.users,
            organizations: this.organizations,
            groups: this.groups,
            projects: this.projects,
            groupMemberships: this.groupMemberships,
            projectMemberships: this.projectMemberships,
            groupShares: this.groupShares,
            projectShares: this.projectShares,
            _nextUserId: this._nextUserId,
            _nextGroupId: this._nextGroupId,
            _nextProjectId: this._nextProjectId,
            _nextOrgId: this._nextOrgId
        };
    },

    _persist() {
        try {
            const persistable = this._getPersistable();
            const json = JSON.stringify(persistable);
            localStorage.setItem(STORAGE_KEY, json);
            // Sync to server (fire-and-forget)
            fetch('/api/state', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: json
            }).catch(() => {});
        } catch (e) {
            console.error('[AppState] Failed to persist state:', e);
        }
    },

    resetToSeedData() {
        localStorage.removeItem(STORAGE_KEY);
        const seed = _loadSeedData();
        this.currentUser = seed.currentUser;
        this.users = seed.users;
        this.organizations = seed.organizations;
        this.groups = seed.groups;
        this.projects = seed.projects;
        this.groupMemberships = seed.groupMemberships;
        this.projectMemberships = seed.projectMemberships;
        this.groupShares = seed.groupShares;
        this.projectShares = seed.projectShares;
        this._seedVersion = seed._seedVersion;
        this._nextUserId = seed._nextUserId;
        this._nextGroupId = seed._nextGroupId;
        this._nextProjectId = seed._nextProjectId;
        this._nextOrgId = seed._nextOrgId;
        this._listeners.forEach(fn => fn(this));
        // Sync seed state to server
        fetch('/api/state', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(this._getPersistable())
        }).catch(() => {});
    },

    // ---- Helper Methods ----

    getUserById(id) {
        return this.users.find(u => u.id === id);
    },

    getUserByUsername(username) {
        return this.users.find(u => u.username === username);
    },

    getGroupById(id) {
        return this.groups.find(g => g.id === id);
    },

    getProjectById(id) {
        return this.projects.find(p => p.id === id);
    },

    getOrgById(id) {
        return this.organizations.find(o => o.id === id);
    },

    // Get all ancestor groups (parent chain)
    getGroupAncestors(groupId) {
        const ancestors = [];
        let current = this.getGroupById(groupId);
        while (current && current.parentId) {
            const parent = this.getGroupById(current.parentId);
            if (parent) {
                ancestors.unshift(parent);
                current = parent;
            } else break;
        }
        return ancestors;
    },

    // Get direct children of a group
    getChildGroups(groupId) {
        return this.groups.filter(g => g.parentId === groupId);
    },

    // Get all descendants recursively
    getDescendantGroups(groupId) {
        const descendants = [];
        const stack = [groupId];
        while (stack.length) {
            const id = stack.pop();
            const children = this.groups.filter(g => g.parentId === id);
            children.forEach(c => {
                descendants.push(c);
                stack.push(c.id);
            });
        }
        return descendants;
    },

    // Top-level groups for an organization
    getTopLevelGroups(orgId) {
        return this.groups.filter(g => g.parentId === null && g.organizationId === orgId);
    },

    // Projects within a group
    getProjectsForGroup(groupId) {
        return this.projects.filter(p => p.groupId === groupId);
    },

    // ---- Membership Logic ----

    // Get direct group memberships
    getDirectGroupMembers(groupId) {
        return this.groupMemberships.filter(m => m.groupId === groupId && m.membershipType === 'direct');
    },

    // Get inherited memberships (from parent groups)
    getInheritedGroupMembers(groupId) {
        const ancestors = this.getGroupAncestors(groupId);
        const inherited = [];
        const seen = new Set();

        // Direct members of this group (to check for overrides)
        const directUserIds = new Set(this.getDirectGroupMembers(groupId).map(m => m.userId));

        for (const ancestor of ancestors) {
            const ancestorDirectMembers = this.groupMemberships.filter(
                m => m.groupId === ancestor.id && m.membershipType === 'direct'
            );
            for (const m of ancestorDirectMembers) {
                if (!seen.has(m.userId) && !directUserIds.has(m.userId)) {
                    seen.add(m.userId);
                    inherited.push({
                        ...m,
                        membershipType: 'inherited',
                        source: ancestor
                    });
                }
            }
        }
        return inherited;
    },

    // Get shared members (from group-to-group invitations)
    getSharedGroupMembers(groupId) {
        const shares = this.groupShares.filter(s => s.targetGroupId === groupId);
        const shared = [];
        for (const share of shares) {
            const sourceMembers = this.groupMemberships.filter(
                m => m.groupId === share.sourceGroupId && m.membershipType === 'direct'
            );
            for (const m of sourceMembers) {
                const effectiveRole = m.role.level <= share.maxRole.level ? m.role : share.maxRole;
                shared.push({
                    groupId: groupId,
                    userId: m.userId,
                    role: effectiveRole,
                    membershipType: 'shared',
                    source: this.getGroupById(share.sourceGroupId),
                    expiresAt: share.expiresAt,
                    addedBy: share.addedBy,
                    addedAt: share.addedAt
                });
            }
        }
        return shared;
    },

    // Get all members of a group (direct + inherited + shared)
    getAllGroupMembers(groupId) {
        const direct = this.getDirectGroupMembers(groupId);
        const inherited = this.getInheritedGroupMembers(groupId);
        const shared = this.getSharedGroupMembers(groupId);
        return [...direct, ...inherited, ...shared];
    },

    // Get direct project memberships
    getDirectProjectMembers(projectId) {
        return this.projectMemberships.filter(m => m.projectId === projectId);
    },

    // Get inherited project members (from group membership chain)
    getInheritedProjectMembers(projectId) {
        const project = this.getProjectById(projectId);
        if (!project) return [];

        const group = this.getGroupById(project.groupId);
        if (!group) return [];

        const allGroupMembers = this.getAllGroupMembers(group.id);
        const directProjectUserIds = new Set(this.getDirectProjectMembers(projectId).map(m => m.userId));

        return allGroupMembers
            .filter(m => !directProjectUserIds.has(m.userId))
            .map(m => ({
                projectId,
                userId: m.userId,
                role: m.role,
                membershipType: m.membershipType === 'direct' ? 'inherited' : m.membershipType,
                source: m.source || this.getGroupById(m.groupId),
                expiresAt: m.expiresAt,
                addedBy: m.addedBy,
                addedAt: m.addedAt
            }));
    },

    // Get shared project members (from project shares)
    getSharedProjectMembers(projectId) {
        const shares = this.projectShares.filter(s => s.targetProjectId === projectId);
        const shared = [];
        for (const share of shares) {
            const sourceMembers = this.groupMemberships.filter(
                m => m.groupId === share.sourceGroupId && m.membershipType === 'direct'
            );
            for (const m of sourceMembers) {
                const effectiveRole = m.role.level <= share.maxRole.level ? m.role : share.maxRole;
                shared.push({
                    projectId,
                    userId: m.userId,
                    role: effectiveRole,
                    membershipType: 'shared',
                    source: this.getGroupById(share.sourceGroupId),
                    expiresAt: share.expiresAt,
                    addedBy: share.addedBy,
                    addedAt: share.addedAt
                });
            }
        }
        return shared;
    },

    // All project members
    getAllProjectMembers(projectId) {
        const direct = this.getDirectProjectMembers(projectId);
        const inherited = this.getInheritedProjectMembers(projectId);
        const shared = this.getSharedProjectMembers(projectId);
        return [...direct, ...inherited, ...shared];
    },

    // Get current user's role in a group
    getCurrentUserGroupRole(groupId) {
        const allMembers = this.getAllGroupMembers(groupId);
        const memberships = allMembers.filter(m => m.userId === this.currentUser.id);
        if (memberships.length === 0) return null;
        return memberships.reduce((best, m) => m.role.level > best.role.level ? m : best).role;
    },

    // Get current user's role in a project
    getCurrentUserProjectRole(projectId) {
        const allMembers = this.getAllProjectMembers(projectId);
        const memberships = allMembers.filter(m => m.userId === this.currentUser.id);
        if (memberships.length === 0) return null;
        return memberships.reduce((best, m) => m.role.level > best.role.level ? m : best).role;
    },

    // ---- Mutation Methods ----

    addGroupMember(groupId, userId, role, expiresAt = null) {
        const existing = this.groupMemberships.find(
            m => m.groupId === groupId && m.userId === userId && m.membershipType === 'direct'
        );
        if (existing) {
            existing.role = role;
            existing.expiresAt = expiresAt;
        } else {
            this.groupMemberships.push({
                groupId, userId, role, membershipType: 'direct',
                source: null, expiresAt, addedBy: this.currentUser.id,
                addedAt: new Date().toISOString()
            });
        }
        this.notify();
    },

    removeGroupMember(groupId, userId) {
        this.groupMemberships = this.groupMemberships.filter(
            m => !(m.groupId === groupId && m.userId === userId && m.membershipType === 'direct')
        );
        this.notify();
    },

    updateGroupMemberRole(groupId, userId, newRole) {
        const m = this.groupMemberships.find(
            mem => mem.groupId === groupId && mem.userId === userId && mem.membershipType === 'direct'
        );
        if (m) {
            m.role = newRole;
            this.notify();
        }
    },

    updateGroupMemberExpiration(groupId, userId, expiresAt) {
        const m = this.groupMemberships.find(
            mem => mem.groupId === groupId && mem.userId === userId && mem.membershipType === 'direct'
        );
        if (m) {
            m.expiresAt = expiresAt;
            this.notify();
        }
    },

    addProjectMember(projectId, userId, role, expiresAt = null) {
        const existing = this.projectMemberships.find(
            m => m.projectId === projectId && m.userId === userId
        );
        if (existing) {
            existing.role = role;
            existing.expiresAt = expiresAt;
        } else {
            this.projectMemberships.push({
                projectId, userId, role, membershipType: 'direct',
                expiresAt, addedBy: this.currentUser.id,
                addedAt: new Date().toISOString()
            });
        }
        this.notify();
    },

    removeProjectMember(projectId, userId) {
        this.projectMemberships = this.projectMemberships.filter(
            m => !(m.projectId === projectId && m.userId === userId)
        );
        this.notify();
    },

    createGroup(data) {
        const id = this._nextGroupId++;
        const parentGroup = data.parentId ? this.getGroupById(data.parentId) : null;
        const org = parentGroup ? this.getOrgById(parentGroup.organizationId) : this.getOrgById(data.organizationId || 1);
        const parentPath = parentGroup ? parentGroup.fullPath : (org ? org.path : '');

        const group = {
            id,
            name: data.name,
            path: data.path || data.name.toLowerCase().replace(/[^a-z0-9-]/g, '-').replace(/-+/g, '-'),
            fullPath: parentPath + '/' + (data.path || data.name.toLowerCase().replace(/[^a-z0-9-]/g, '-').replace(/-+/g, '-')),
            description: data.description || '',
            parentId: data.parentId || null,
            organizationId: parentGroup ? parentGroup.organizationId : (data.organizationId || 1),
            visibility: data.visibility || 'private',
            avatar: null,
            avatarColor: data.avatarColor || '#' + Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0'),
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            archived: false,
            userCap: data.userCap || null,
            preventInvitations: data.preventInvitations || false,
            disableMentions: false,
            preventSharingOutsideHierarchy: data.preventSharingOutsideHierarchy || false,
            defaultBranchProtection: data.defaultBranchProtection || 'fully_protected',
            subgroupCreationLevel: data.subgroupCreationLevel || 'maintainer',
            projectCreationLevel: data.projectCreationLevel || 'developer',
            requireTwoFactor: data.requireTwoFactor || false,
            readme: ''
        };
        this.groups.push(group);

        // Add current user as owner
        this.groupMemberships.push({
            groupId: id, userId: this.currentUser.id, role: ROLES.OWNER,
            membershipType: 'direct', source: null, expiresAt: null,
            addedBy: this.currentUser.id, addedAt: new Date().toISOString()
        });

        this.notify();
        return group;
    },

    updateGroup(groupId, data) {
        const group = this.getGroupById(groupId);
        if (!group) return null;
        Object.assign(group, data, { updatedAt: new Date().toISOString() });
        this.notify();
        return group;
    },

    deleteGroup(groupId) {
        // Remove group and all descendants
        const descendants = this.getDescendantGroups(groupId);
        const idsToRemove = new Set([groupId, ...descendants.map(d => d.id)]);

        // Remove projects in these groups
        const projectsToRemove = this.projects.filter(p => idsToRemove.has(p.groupId));
        const projectIdsToRemove = new Set(projectsToRemove.map(p => p.id));

        this.projects = this.projects.filter(p => !projectIdsToRemove.has(p.id));
        this.groups = this.groups.filter(g => !idsToRemove.has(g.id));
        this.groupMemberships = this.groupMemberships.filter(m => !idsToRemove.has(m.groupId));
        this.projectMemberships = this.projectMemberships.filter(m => !projectIdsToRemove.has(m.projectId));
        this.groupShares = this.groupShares.filter(s => !idsToRemove.has(s.sourceGroupId) && !idsToRemove.has(s.targetGroupId));
        this.projectShares = this.projectShares.filter(s => !projectIdsToRemove.has(s.targetProjectId) && !idsToRemove.has(s.sourceGroupId));

        this.notify();
    },

    createProject(data) {
        const id = this._nextProjectId++;
        const group = this.getGroupById(data.groupId);
        const project = {
            id,
            name: data.name,
            path: data.path || data.name.toLowerCase().replace(/[^a-z0-9-]/g, '-').replace(/-+/g, '-'),
            fullPath: group ? group.fullPath + '/' + (data.path || data.name.toLowerCase().replace(/[^a-z0-9-]/g, '-').replace(/-+/g, '-')) : '',
            description: data.description || '',
            groupId: data.groupId,
            visibility: data.visibility || 'private',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            stars: 0, forks: 0, defaultBranch: 'main',
            topics: data.topics || [],
            archived: false, empty: true
        };
        this.projects.push(project);
        this.notify();
        return project;
    },

    deleteProject(projectId) {
        this.projects = this.projects.filter(p => p.id !== projectId);
        this.projectMemberships = this.projectMemberships.filter(m => m.projectId !== projectId);
        this.projectShares = this.projectShares.filter(s => s.targetProjectId !== projectId);
        this.notify();
    },

    addGroupShare(sourceGroupId, targetGroupId, maxRole, expiresAt = null) {
        const existing = this.groupShares.find(
            s => s.sourceGroupId === sourceGroupId && s.targetGroupId === targetGroupId
        );
        if (existing) {
            existing.maxRole = maxRole;
            existing.expiresAt = expiresAt;
        } else {
            this.groupShares.push({
                sourceGroupId, targetGroupId, maxRole, expiresAt,
                addedBy: this.currentUser.id, addedAt: new Date().toISOString()
            });
        }
        this.notify();
    },

    removeGroupShare(sourceGroupId, targetGroupId) {
        this.groupShares = this.groupShares.filter(
            s => !(s.sourceGroupId === sourceGroupId && s.targetGroupId === targetGroupId)
        );
        this.notify();
    },

    addProjectShare(sourceGroupId, targetProjectId, maxRole, expiresAt = null) {
        const existing = this.projectShares.find(
            s => s.sourceGroupId === sourceGroupId && s.targetProjectId === targetProjectId
        );
        if (existing) {
            existing.maxRole = maxRole;
            existing.expiresAt = expiresAt;
        } else {
            this.projectShares.push({
                sourceGroupId, targetProjectId, maxRole, expiresAt,
                addedBy: this.currentUser.id, addedAt: new Date().toISOString()
            });
        }
        this.notify();
    },

    removeProjectShare(sourceGroupId, targetProjectId) {
        this.projectShares = this.projectShares.filter(
            s => !(s.sourceGroupId === sourceGroupId && s.targetProjectId === targetProjectId)
        );
        this.notify();
    },

    // Validate group/project/username naming
    validateName(name, type = 'group') {
        const errors = [];
        if (!name || name.trim().length === 0) {
            errors.push('Name is required');
            return errors;
        }
        const trimmed = name.trim();
        if (trimmed.length < 2) errors.push('Must be at least 2 characters');
        if (trimmed.length > 255) errors.push('Must be at most 255 characters');
        if (!/^[a-zA-Z0-9]/.test(trimmed)) errors.push('Must start with a letter or digit');
        if (!/[a-zA-Z0-9]$/.test(trimmed)) errors.push('Must end with a letter or digit');
        if (/[._-]{2,}/.test(trimmed)) errors.push('Cannot contain consecutive special characters');
        if (trimmed.endsWith('.git')) errors.push('Cannot end in .git');
        if (trimmed.endsWith('.atom')) errors.push('Cannot end in .atom');
        if (RESERVED_NAMES.includes(trimmed.toLowerCase())) errors.push(`"${trimmed}" is a reserved name`);
        return errors;
    },

    validatePath(path) {
        const errors = [];
        if (!path || path.trim().length === 0) {
            errors.push('URL slug is required');
            return errors;
        }
        const trimmed = path.trim();
        if (!/^[a-zA-Z0-9][a-zA-Z0-9._-]*[a-zA-Z0-9]$/.test(trimmed) && trimmed.length > 1) {
            errors.push('URL slug must start and end with a letter or digit, and contain only letters, digits, underscores, dashes, or dots');
        }
        if (trimmed.length < 2) errors.push('Must be at least 2 characters');
        if (RESERVED_NAMES.includes(trimmed.toLowerCase())) errors.push(`"${trimmed}" is a reserved name`);
        return errors;
    },

    // Visibility constraints
    getMaxVisibility(parentGroupId) {
        if (!parentGroupId) return 'public';
        const parent = this.getGroupById(parentGroupId);
        if (!parent) return 'public';
        return parent.visibility;
    },

    isVisibilityAllowed(visibility, parentGroupId) {
        const maxVis = this.getMaxVisibility(parentGroupId);
        const order = { private: 0, internal: 1, public: 2 };
        return order[visibility] <= order[maxVis];
    }
};

// Push initial state to server on page load
fetch('/api/state', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(AppState._getPersistable())
}).catch(() => {});
