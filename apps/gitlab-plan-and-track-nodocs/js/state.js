/* ============================================================
   GitLab Plan & Track — State Management
   ============================================================ */

const AppState = {
    // ── Persisted data ─────────────────────────────────────
    currentUser: null,
    users: [],
    labels: [],
    milestones: [],
    iterationCadences: [],
    iterations: [],
    epics: [],
    issues: [],
    boards: [],
    issueTemplates: [],
    notificationSettings: null,
    notificationFeed: [],

    // ID counters
    _nextIssueId: 200,
    _nextLabelId: 100,
    _nextMilestoneId: 100,
    _nextIterationId: 100,
    _nextEpicId: 100,
    _nextBoardId: 100,
    _nextBoardListId: 100,
    _nextCommentId: 1000,
    _nextNotificationId: 100,

    // ── UI state (transient, not persisted) ────────────────
    currentSection: 'issues',
    currentView: 'list',       // list, detail, create, board
    selectedIssueId: null,
    selectedMilestoneId: null,
    selectedEpicId: null,
    selectedIterationId: null,
    selectedBoardId: null,
    activeModal: null,
    modalData: null,
    sidebarCollapsed: false,

    // Filters
    issueFilters: {
        status: 'opened',
        search: '',
        authorId: null,
        assigneeId: null,
        labelIds: [],
        milestoneId: null,
        iterationId: null,
        epicId: null,
        weight: null,
        confidential: null,
        type: null,
        sort: 'created_desc'
    },
    boardFilters: {
        assigneeId: null,
        labelIds: [],
        milestoneId: null,
        iterationId: null
    },

    // Pagination
    issuesPage: 1,
    issuesPerPage: 20,

    // Bulk selection
    selectedIssueIds: [],

    // ── Subscribers ────────────────────────────────────────
    _listeners: [],

    subscribe(fn) {
        this._listeners.push(fn);
    },

    notify() {
        this._persist();
        this._pushStateToServer();
        this._listeners.forEach(fn => fn());
    },

    // ── Initialization ─────────────────────────────────────
    init() {
        const saved = localStorage.getItem('gitlabPlanTrackState');
        if (saved) {
            try {
                const parsed = JSON.parse(saved);
                if (parsed._seedVersion === SEED_DATA_VERSION) {
                    this._restoreFrom(parsed);
                    return;
                }
            } catch (e) { /* fall through to seed */ }
            localStorage.removeItem('gitlabPlanTrackState');
        }
        this._loadSeedData();
    },

    _loadSeedData() {
        this.currentUser = JSON.parse(JSON.stringify(CURRENT_USER));
        this.users = JSON.parse(JSON.stringify(USERS));
        this.labels = JSON.parse(JSON.stringify(LABELS));
        this.milestones = JSON.parse(JSON.stringify(MILESTONES));
        this.iterationCadences = JSON.parse(JSON.stringify(ITERATION_CADENCES));
        this.iterations = JSON.parse(JSON.stringify(ITERATIONS));
        this.epics = JSON.parse(JSON.stringify(EPICS));
        this.issues = JSON.parse(JSON.stringify(ISSUES));
        this.boards = JSON.parse(JSON.stringify(BOARDS));
        this.issueTemplates = JSON.parse(JSON.stringify(ISSUE_TEMPLATES));
        this.notificationSettings = JSON.parse(JSON.stringify(NOTIFICATION_SETTINGS));
        this.notificationFeed = JSON.parse(JSON.stringify(NOTIFICATION_FEED));

        this._nextIssueId = Math.max(...this.issues.map(i => i.id)) + 1;
        this._nextLabelId = Math.max(...this.labels.map(l => l.id)) + 1;
        this._nextMilestoneId = Math.max(...this.milestones.map(m => m.id)) + 1;
        this._nextIterationId = Math.max(...this.iterations.map(i => i.id)) + 1;
        this._nextEpicId = Math.max(...this.epics.map(e => e.id)) + 1;
        this._nextBoardId = Math.max(...this.boards.map(b => b.id)) + 1;
        this._nextBoardListId = Math.max(...this.boards.flatMap(b => b.lists.map(l => l.id))) + 1;
        this._nextCommentId = 1000;
        this._nextNotificationId = Math.max(...this.notificationFeed.map(n => n.id)) + 1;
    },

    _restoreFrom(parsed) {
        this.currentUser = parsed.currentUser;
        this.users = parsed.users;
        this.labels = parsed.labels;
        this.milestones = parsed.milestones;
        this.iterationCadences = parsed.iterationCadences;
        this.iterations = parsed.iterations;
        this.epics = parsed.epics;
        this.issues = parsed.issues;
        this.boards = parsed.boards;
        this.issueTemplates = parsed.issueTemplates || JSON.parse(JSON.stringify(ISSUE_TEMPLATES));
        this.notificationSettings = parsed.notificationSettings;
        this.notificationFeed = parsed.notificationFeed;
        this._nextIssueId = parsed._nextIssueId;
        this._nextLabelId = parsed._nextLabelId;
        this._nextMilestoneId = parsed._nextMilestoneId;
        this._nextIterationId = parsed._nextIterationId;
        this._nextEpicId = parsed._nextEpicId;
        this._nextBoardId = parsed._nextBoardId;
        this._nextBoardListId = parsed._nextBoardListId;
        this._nextCommentId = parsed._nextCommentId;
        this._nextNotificationId = parsed._nextNotificationId;
    },

    // ── Persistence ────────────────────────────────────────
    _persist() {
        const data = {
            _seedVersion: SEED_DATA_VERSION,
            currentUser: this.currentUser,
            users: this.users,
            labels: this.labels,
            milestones: this.milestones,
            iterationCadences: this.iterationCadences,
            iterations: this.iterations,
            epics: this.epics,
            issues: this.issues,
            boards: this.boards,
            issueTemplates: this.issueTemplates,
            notificationSettings: this.notificationSettings,
            notificationFeed: this.notificationFeed,
            _nextIssueId: this._nextIssueId,
            _nextLabelId: this._nextLabelId,
            _nextMilestoneId: this._nextMilestoneId,
            _nextIterationId: this._nextIterationId,
            _nextEpicId: this._nextEpicId,
            _nextBoardId: this._nextBoardId,
            _nextBoardListId: this._nextBoardListId,
            _nextCommentId: this._nextCommentId,
            _nextNotificationId: this._nextNotificationId
        };
        localStorage.setItem('gitlabPlanTrackState', JSON.stringify(data));
    },

    _pushStateToServer() {
        const data = {
            _seedVersion: SEED_DATA_VERSION,
            currentUser: this.currentUser,
            users: this.users,
            labels: this.labels,
            milestones: this.milestones,
            iterationCadences: this.iterationCadences,
            iterations: this.iterations,
            epics: this.epics,
            issues: this.issues,
            boards: this.boards,
            issueTemplates: this.issueTemplates,
            notificationSettings: this.notificationSettings,
            notificationFeed: this.notificationFeed,
            _nextIssueId: this._nextIssueId,
            _nextLabelId: this._nextLabelId,
            _nextMilestoneId: this._nextMilestoneId,
            _nextIterationId: this._nextIterationId,
            _nextEpicId: this._nextEpicId,
            _nextBoardId: this._nextBoardId,
            _nextBoardListId: this._nextBoardListId,
            _nextCommentId: this._nextCommentId,
            _nextNotificationId: this._nextNotificationId
        };
        fetch('/api/state', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).catch(() => {});
    },

    resetToSeedData() {
        localStorage.removeItem('gitlabPlanTrackState');
        this._loadSeedData();
        this.currentSection = 'issues';
        this.currentView = 'list';
        this.selectedIssueId = null;
        this.selectedMilestoneId = null;
        this.selectedEpicId = null;
        this.selectedIterationId = null;
        this.selectedBoardId = null;
        this.issueFilters = {
            status: 'opened', search: '', authorId: null, assigneeId: null,
            labelIds: [], milestoneId: null, iterationId: null, epicId: null,
            weight: null, confidential: null, type: null, sort: 'created_desc'
        };
        this.boardFilters = { assigneeId: null, labelIds: [], milestoneId: null, iterationId: null };
        this.issuesPage = 1;
        this.selectedIssueIds = [];
        this.activeModal = null;
        this.modalData = null;
        this.notify();
    },

    // ── Lookup Helpers ─────────────────────────────────────
    getUserById(id) { return this.users.find(u => u.id === id); },
    getLabelById(id) { return this.labels.find(l => l.id === id); },
    getMilestoneById(id) { return this.milestones.find(m => m.id === id); },
    getIterationById(id) { return this.iterations.find(i => i.id === id); },
    getCadenceById(id) { return this.iterationCadences.find(c => c.id === id); },
    getEpicById(id) { return this.epics.find(e => e.id === id); },
    getIssueById(id) { return this.issues.find(i => i.id === id); },
    getBoardById(id) { return this.boards.find(b => b.id === id); },

    // ── Computed Queries ───────────────────────────────────
    getFilteredIssues() {
        const f = this.issueFilters;
        let result = this.issues.slice();

        if (f.status === 'opened') result = result.filter(i => i.state === 'opened');
        else if (f.status === 'closed') result = result.filter(i => i.state === 'closed');
        // 'all' — no filter

        if (f.search) {
            const q = f.search.toLowerCase();
            result = result.filter(i =>
                i.title.toLowerCase().includes(q) ||
                (i.description && i.description.toLowerCase().includes(q)) ||
                String(i.iid).includes(q)
            );
        }
        if (f.authorId) result = result.filter(i => i.authorId === f.authorId);
        if (f.assigneeId) result = result.filter(i => i.assignees.includes(f.assigneeId));
        if (f.labelIds.length > 0) result = result.filter(i => f.labelIds.every(lid => i.labels.includes(lid)));
        if (f.milestoneId) result = result.filter(i => i.milestoneId === f.milestoneId);
        if (f.iterationId) result = result.filter(i => i.iterationId === f.iterationId);
        if (f.epicId) result = result.filter(i => i.epicId === f.epicId);
        if (f.weight !== null) result = result.filter(i => i.weight === f.weight);
        if (f.confidential !== null) result = result.filter(i => i.confidential === f.confidential);
        if (f.type) result = result.filter(i => i.type === f.type);

        // Sort
        result = this._sortIssues(result, f.sort);
        return result;
    },

    _sortIssues(issues, sortKey) {
        const cmp = (a, b) => {
            switch (sortKey) {
                case 'created_desc': return new Date(b.createdAt) - new Date(a.createdAt);
                case 'created_asc': return new Date(a.createdAt) - new Date(b.createdAt);
                case 'updated_desc': return new Date(b.updatedAt) - new Date(a.updatedAt);
                case 'updated_asc': return new Date(a.updatedAt) - new Date(b.updatedAt);
                case 'due_date_asc': {
                    if (!a.dueDate && !b.dueDate) return 0;
                    if (!a.dueDate) return 1;
                    if (!b.dueDate) return -1;
                    return new Date(a.dueDate) - new Date(b.dueDate);
                }
                case 'due_date_desc': {
                    if (!a.dueDate && !b.dueDate) return 0;
                    if (!a.dueDate) return 1;
                    if (!b.dueDate) return -1;
                    return new Date(b.dueDate) - new Date(a.dueDate);
                }
                case 'priority_desc': {
                    const prio = lid => {
                        if (issues === undefined) return 999;
                        const map = { 11: 1, 12: 2, 13: 3, 14: 4 };
                        for (const l of (a === undefined ? [] : a.labels || [])) { if (map[l]) return map[l]; }
                        return 999;
                    };
                    const pa = (() => { const map = {11:1,12:2,13:3,14:4}; for (const l of (a.labels||[])) { if(map[l]) return map[l]; } return 999; })();
                    const pb = (() => { const map = {11:1,12:2,13:3,14:4}; for (const l of (b.labels||[])) { if(map[l]) return map[l]; } return 999; })();
                    return pa - pb;
                }
                case 'priority_asc': {
                    const pa = (() => { const map = {11:1,12:2,13:3,14:4}; for (const l of (a.labels||[])) { if(map[l]) return map[l]; } return 999; })();
                    const pb = (() => { const map = {11:1,12:2,13:3,14:4}; for (const l of (b.labels||[])) { if(map[l]) return map[l]; } return 999; })();
                    return pb - pa;
                }
                case 'popularity_desc': return (b.upvotes - b.downvotes) - (a.upvotes - a.downvotes);
                case 'weight_desc': return (b.weight || 0) - (a.weight || 0);
                case 'weight_asc': return (a.weight || 0) - (b.weight || 0);
                default: return new Date(b.createdAt) - new Date(a.createdAt);
            }
        };
        return issues.sort(cmp);
    },

    getPaginatedIssues() {
        const filtered = this.getFilteredIssues();
        const start = (this.issuesPage - 1) * this.issuesPerPage;
        return {
            issues: filtered.slice(start, start + this.issuesPerPage),
            total: filtered.length,
            page: this.issuesPage,
            totalPages: Math.max(1, Math.ceil(filtered.length / this.issuesPerPage))
        };
    },

    getIssuesForMilestone(milestoneId) {
        return this.issues.filter(i => i.milestoneId === milestoneId);
    },

    getIssuesForIteration(iterationId) {
        return this.issues.filter(i => i.iterationId === iterationId);
    },

    getIssuesForEpic(epicId) {
        return this.issues.filter(i => i.epicId === epicId);
    },

    getChildEpics(epicId) {
        return this.epics.filter(e => e.parentEpicId === epicId);
    },

    getMilestoneProgress(milestoneId) {
        const issues = this.getIssuesForMilestone(milestoneId);
        const total = issues.length;
        const closed = issues.filter(i => i.state === 'closed').length;
        return { total, closed, open: total - closed, percentage: total > 0 ? Math.round((closed / total) * 100) : 0 };
    },

    getEpicProgress(epicId) {
        const issues = this.getIssuesForEpic(epicId);
        const childEpics = this.getChildEpics(epicId);
        const total = issues.length;
        const closed = issues.filter(i => i.state === 'closed').length;
        return { total, closed, open: total - closed, childEpicsCount: childEpics.length, percentage: total > 0 ? Math.round((closed / total) * 100) : 0 };
    },

    getIterationProgress(iterationId) {
        const issues = this.getIssuesForIteration(iterationId);
        const total = issues.length;
        const closed = issues.filter(i => i.state === 'closed').length;
        const totalWeight = issues.reduce((s, i) => s + (i.weight || 0), 0);
        const closedWeight = issues.filter(i => i.state === 'closed').reduce((s, i) => s + (i.weight || 0), 0);
        return { total, closed, open: total - closed, totalWeight, closedWeight, percentage: total > 0 ? Math.round((closed / total) * 100) : 0 };
    },

    // ── Issue Mutations ────────────────────────────────────
    createIssue(data) {
        const now = new Date().toISOString();
        const maxIid = Math.max(0, ...this.issues.map(i => i.iid));
        const issue = {
            id: this._nextIssueId++,
            iid: maxIid + 1,
            title: data.title,
            description: data.description || '',
            state: 'opened',
            type: data.type || 'issue',
            authorId: this.currentUser.id,
            assignees: data.assignees || [],
            labels: data.labels || [],
            milestoneId: data.milestoneId || null,
            iterationId: data.iterationId || null,
            epicId: data.epicId || null,
            weight: data.weight || null,
            dueDate: data.dueDate || null,
            confidential: data.confidential || false,
            timeEstimate: data.timeEstimate || null,
            timeSpent: 0,
            createdAt: now,
            updatedAt: now,
            closedAt: null,
            closedBy: null,
            upvotes: 0,
            downvotes: 0,
            subscribed: true,
            relatedIssues: [],
            activities: []
        };
        this.issues.unshift(issue);
        this.notify();
        return issue;
    },

    updateIssue(issueId, updates) {
        const issue = this.getIssueById(issueId);
        if (!issue) return;
        Object.assign(issue, updates, { updatedAt: new Date().toISOString() });
        this.notify();
    },

    closeIssue(issueId) {
        const issue = this.getIssueById(issueId);
        if (!issue) return;
        const now = new Date().toISOString();
        issue.state = 'closed';
        issue.closedAt = now;
        issue.closedBy = this.currentUser.id;
        issue.updatedAt = now;
        issue.activities.push({
            id: this._nextCommentId++,
            type: 'status_change',
            authorId: this.currentUser.id,
            content: 'Closed this issue',
            createdAt: now
        });
        this.notify();
    },

    reopenIssue(issueId) {
        const issue = this.getIssueById(issueId);
        if (!issue) return;
        const now = new Date().toISOString();
        issue.state = 'opened';
        issue.closedAt = null;
        issue.closedBy = null;
        issue.updatedAt = now;
        issue.activities.push({
            id: this._nextCommentId++,
            type: 'status_change',
            authorId: this.currentUser.id,
            content: 'Reopened this issue',
            createdAt: now
        });
        this.notify();
    },

    addComment(issueId, content) {
        const issue = this.getIssueById(issueId);
        if (!issue) return;
        const now = new Date().toISOString();
        issue.activities.push({
            id: this._nextCommentId++,
            type: 'comment',
            authorId: this.currentUser.id,
            content: content,
            createdAt: now
        });
        issue.updatedAt = now;
        this.notify();
    },

    addRelatedIssue(issueId, relatedIssueId, linkType) {
        const issue = this.getIssueById(issueId);
        if (!issue) return;
        if (issue.relatedIssues.some(r => r.issueId === relatedIssueId)) return;
        issue.relatedIssues.push({ issueId: relatedIssueId, linkType });
        // Add reverse relation
        const related = this.getIssueById(relatedIssueId);
        if (related) {
            const reverse = linkType === 'blocks' ? 'is_blocked_by' : linkType === 'is_blocked_by' ? 'blocks' : 'relates_to';
            if (!related.relatedIssues.some(r => r.issueId === issueId)) {
                related.relatedIssues.push({ issueId: issueId, linkType: reverse });
            }
        }
        this.notify();
    },

    removeRelatedIssue(issueId, relatedIssueId) {
        const issue = this.getIssueById(issueId);
        if (!issue) return;
        issue.relatedIssues = issue.relatedIssues.filter(r => r.issueId !== relatedIssueId);
        const related = this.getIssueById(relatedIssueId);
        if (related) {
            related.relatedIssues = related.relatedIssues.filter(r => r.issueId !== issueId);
        }
        this.notify();
    },

    logTimeSpent(issueId, seconds) {
        const issue = this.getIssueById(issueId);
        if (!issue) return;
        issue.timeSpent = (issue.timeSpent || 0) + seconds;
        issue.updatedAt = new Date().toISOString();
        issue.activities.push({
            id: this._nextCommentId++,
            type: 'time_spent',
            authorId: this.currentUser.id,
            content: `Added ${Components.formatDuration(seconds)} of time spent`,
            createdAt: new Date().toISOString()
        });
        this.notify();
    },

    setTimeEstimate(issueId, seconds) {
        const issue = this.getIssueById(issueId);
        if (!issue) return;
        issue.timeEstimate = seconds;
        issue.updatedAt = new Date().toISOString();
        this.notify();
    },

    bulkUpdateIssues(issueIds, updates) {
        const now = new Date().toISOString();
        issueIds.forEach(id => {
            const issue = this.getIssueById(id);
            if (!issue) return;
            if (updates.state === 'closed' && issue.state !== 'closed') {
                issue.state = 'closed';
                issue.closedAt = now;
                issue.closedBy = this.currentUser.id;
            }
            if (updates.state === 'opened' && issue.state !== 'opened') {
                issue.state = 'opened';
                issue.closedAt = null;
                issue.closedBy = null;
            }
            if (updates.assigneeId && !issue.assignees.includes(updates.assigneeId)) {
                issue.assignees.push(updates.assigneeId);
            }
            if (updates.labelId && !issue.labels.includes(updates.labelId)) {
                issue.labels.push(updates.labelId);
            }
            if (updates.milestoneId !== undefined) {
                issue.milestoneId = updates.milestoneId;
            }
            if (updates.iterationId !== undefined) {
                issue.iterationId = updates.iterationId;
            }
            issue.updatedAt = now;
        });
        this.selectedIssueIds = [];
        this.notify();
    },

    // ── Label Mutations ────────────────────────────────────
    createLabel(data) {
        const label = {
            id: this._nextLabelId++,
            name: data.name,
            description: data.description || '',
            color: data.color,
            textColor: this._getContrastColor(data.color),
            scoped: data.name.includes('::')
        };
        this.labels.push(label);
        this.notify();
        return label;
    },

    updateLabel(labelId, updates) {
        const label = this.getLabelById(labelId);
        if (!label) return;
        if (updates.name !== undefined) {
            label.name = updates.name;
            label.scoped = updates.name.includes('::');
        }
        if (updates.description !== undefined) label.description = updates.description;
        if (updates.color !== undefined) {
            label.color = updates.color;
            label.textColor = this._getContrastColor(updates.color);
        }
        this.notify();
    },

    deleteLabel(labelId) {
        this.labels = this.labels.filter(l => l.id !== labelId);
        this.issues.forEach(issue => {
            issue.labels = issue.labels.filter(lid => lid !== labelId);
        });
        this.notify();
    },

    _getContrastColor(hex) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
        return luminance > 0.5 ? '#333333' : '#ffffff';
    },

    // ── Milestone Mutations ────────────────────────────────
    createMilestone(data) {
        const milestone = {
            id: this._nextMilestoneId++,
            title: data.title,
            description: data.description || '',
            startDate: data.startDate || null,
            dueDate: data.dueDate || null,
            state: 'active',
            createdAt: new Date().toISOString()
        };
        this.milestones.push(milestone);
        this.notify();
        return milestone;
    },

    updateMilestone(milestoneId, updates) {
        const m = this.getMilestoneById(milestoneId);
        if (!m) return;
        Object.assign(m, updates);
        this.notify();
    },

    closeMilestone(milestoneId) {
        const m = this.getMilestoneById(milestoneId);
        if (m) { m.state = 'closed'; this.notify(); }
    },

    activateMilestone(milestoneId) {
        const m = this.getMilestoneById(milestoneId);
        if (m) { m.state = 'active'; this.notify(); }
    },

    deleteMilestone(milestoneId) {
        this.milestones = this.milestones.filter(m => m.id !== milestoneId);
        this.issues.forEach(i => { if (i.milestoneId === milestoneId) i.milestoneId = null; });
        this.notify();
    },

    // ── Iteration Mutations ────────────────────────────────
    createIteration(data) {
        const iteration = {
            id: this._nextIterationId++,
            cadenceId: data.cadenceId,
            title: data.title,
            startDate: data.startDate,
            endDate: data.endDate,
            state: 'upcoming',
            createdAt: new Date().toISOString()
        };
        this.iterations.push(iteration);
        this.notify();
        return iteration;
    },

    createCadence(data) {
        const cadence = {
            id: this._nextIterationId++,
            title: data.title,
            description: data.description || '',
            durationWeeks: data.durationWeeks,
            autoSchedule: data.autoSchedule || false,
            createdAt: new Date().toISOString()
        };
        this.iterationCadences.push(cadence);
        this.notify();
        return cadence;
    },

    // ── Epic Mutations ─────────────────────────────────────
    createEpic(data) {
        const now = new Date().toISOString();
        const epic = {
            id: this._nextEpicId++,
            title: data.title,
            description: data.description || '',
            state: 'opened',
            authorId: this.currentUser.id,
            labels: data.labels || [],
            confidential: data.confidential || false,
            startDate: data.startDate || null,
            dueDate: data.dueDate || null,
            parentEpicId: data.parentEpicId || null,
            createdAt: now,
            updatedAt: now
        };
        this.epics.push(epic);
        this.notify();
        return epic;
    },

    updateEpic(epicId, updates) {
        const epic = this.getEpicById(epicId);
        if (!epic) return;
        Object.assign(epic, updates, { updatedAt: new Date().toISOString() });
        this.notify();
    },

    closeEpic(epicId) {
        const epic = this.getEpicById(epicId);
        if (epic) { epic.state = 'closed'; epic.updatedAt = new Date().toISOString(); this.notify(); }
    },

    reopenEpic(epicId) {
        const epic = this.getEpicById(epicId);
        if (epic) { epic.state = 'opened'; epic.updatedAt = new Date().toISOString(); this.notify(); }
    },

    // ── Board Mutations ────────────────────────────────────
    addBoardList(boardId, labelId) {
        const board = this.getBoardById(boardId);
        if (!board) return;
        const label = this.getLabelById(labelId);
        if (!label) return;
        if (board.lists.some(l => l.labelId === labelId)) return;
        const closedList = board.lists.find(l => l.type === 'closed');
        const position = closedList ? closedList.position : board.lists.length;
        if (closedList) closedList.position++;
        board.lists.push({
            id: this._nextBoardListId++,
            type: 'label',
            labelId: labelId,
            title: label.name,
            position: position
        });
        board.lists.sort((a, b) => a.position - b.position);
        this.notify();
    },

    removeBoardList(boardId, listId) {
        const board = this.getBoardById(boardId);
        if (!board) return;
        board.lists = board.lists.filter(l => l.id !== listId);
        board.lists.forEach((l, i) => l.position = i);
        this.notify();
    },

    moveIssueOnBoard(issueId, fromListId, toListId, boardId) {
        const board = this.getBoardById(boardId);
        if (!board) return;
        const issue = this.getIssueById(issueId);
        if (!issue) return;

        const fromList = board.lists.find(l => l.id === fromListId);
        const toList = board.lists.find(l => l.id === toListId);
        if (!fromList || !toList) return;

        // Remove from source label
        if (fromList.type === 'label' && fromList.labelId) {
            issue.labels = issue.labels.filter(lid => lid !== fromList.labelId);
        }

        // Add to target
        if (toList.type === 'label' && toList.labelId) {
            if (!issue.labels.includes(toList.labelId)) {
                // Remove any scoped labels from the same scope
                const targetLabel = this.getLabelById(toList.labelId);
                if (targetLabel && targetLabel.scoped) {
                    const scope = targetLabel.name.split('::')[0];
                    issue.labels = issue.labels.filter(lid => {
                        const l = this.getLabelById(lid);
                        return !(l && l.scoped && l.name.startsWith(scope + '::'));
                    });
                }
                issue.labels.push(toList.labelId);
            }
        } else if (toList.type === 'closed') {
            issue.state = 'closed';
            issue.closedAt = new Date().toISOString();
            issue.closedBy = this.currentUser.id;
        } else if (toList.type === 'backlog' && issue.state === 'closed') {
            issue.state = 'opened';
            issue.closedAt = null;
            issue.closedBy = null;
        }

        issue.updatedAt = new Date().toISOString();
        this.notify();
    },

    // ── Notification Mutations ─────────────────────────────
    markNotificationRead(notifId) {
        const n = this.notificationFeed.find(n => n.id === notifId);
        if (n) { n.read = true; this.notify(); }
    },

    markAllNotificationsRead() {
        this.notificationFeed.forEach(n => n.read = true);
        this.notify();
    },

    updateNotificationSettings(updates) {
        Object.assign(this.notificationSettings, updates);
        this.notify();
    },

    // ── Quick Actions (slash commands) ─────────────────────
    processQuickActions(issueId, text) {
        const issue = this.getIssueById(issueId);
        if (!issue) return text;

        const lines = text.split('\n');
        const remainingLines = [];
        const now = new Date().toISOString();

        lines.forEach(line => {
            const trimmed = line.trim();
            let matched = false;

            // /assign @username
            const assignMatch = trimmed.match(/^\/assign\s+@(\S+)/);
            if (assignMatch) {
                const user = this.users.find(u => u.username === assignMatch[1]);
                if (user && !issue.assignees.includes(user.id)) {
                    issue.assignees.push(user.id);
                    issue.activities.push({ id: this._nextCommentId++, type: 'assignment', authorId: this.currentUser.id, content: `Assigned to @${user.username}`, createdAt: now });
                }
                matched = true;
            }

            // /label ~name
            const labelMatch = trimmed.match(/^\/label\s+~"?([^"]+)"?/);
            if (labelMatch) {
                const label = this.labels.find(l => l.name === labelMatch[1]);
                if (label && !issue.labels.includes(label.id)) {
                    issue.labels.push(label.id);
                    issue.activities.push({ id: this._nextCommentId++, type: 'label_add', authorId: this.currentUser.id, content: `Added label ~"${label.name}"`, createdAt: now });
                }
                matched = true;
            }

            // /milestone %title
            const milestoneMatch = trimmed.match(/^\/milestone\s+%"?([^"]+)"?/);
            if (milestoneMatch) {
                const ms = this.milestones.find(m => m.title === milestoneMatch[1]);
                if (ms) {
                    issue.milestoneId = ms.id;
                    issue.activities.push({ id: this._nextCommentId++, type: 'milestone_change', authorId: this.currentUser.id, content: `Changed milestone to ${ms.title}`, createdAt: now });
                }
                matched = true;
            }

            // /close
            if (trimmed === '/close') {
                if (issue.state === 'opened') {
                    issue.state = 'closed';
                    issue.closedAt = now;
                    issue.closedBy = this.currentUser.id;
                    issue.activities.push({ id: this._nextCommentId++, type: 'status_change', authorId: this.currentUser.id, content: 'Closed this issue', createdAt: now });
                }
                matched = true;
            }

            // /reopen
            if (trimmed === '/reopen') {
                if (issue.state === 'closed') {
                    issue.state = 'opened';
                    issue.closedAt = null;
                    issue.closedBy = null;
                    issue.activities.push({ id: this._nextCommentId++, type: 'status_change', authorId: this.currentUser.id, content: 'Reopened this issue', createdAt: now });
                }
                matched = true;
            }

            // /weight N
            const weightMatch = trimmed.match(/^\/weight\s+(\d+)/);
            if (weightMatch) {
                issue.weight = parseInt(weightMatch[1]);
                matched = true;
            }

            // /due YYYY-MM-DD
            const dueMatch = trimmed.match(/^\/due\s+(\d{4}-\d{2}-\d{2})/);
            if (dueMatch) {
                issue.dueDate = dueMatch[1];
                matched = true;
            }

            // /estimate Nh or NhMm
            const estMatch = trimmed.match(/^\/estimate\s+(\d+)h(?:\s*(\d+)m)?/);
            if (estMatch) {
                issue.timeEstimate = parseInt(estMatch[1]) * 3600 + (parseInt(estMatch[2] || 0) * 60);
                matched = true;
            }

            // /spend Nh or NhMm
            const spendMatch = trimmed.match(/^\/spend\s+(\d+)h(?:\s*(\d+)m)?/);
            if (spendMatch) {
                const seconds = parseInt(spendMatch[1]) * 3600 + (parseInt(spendMatch[2] || 0) * 60);
                issue.timeSpent = (issue.timeSpent || 0) + seconds;
                issue.activities.push({ id: this._nextCommentId++, type: 'time_spent', authorId: this.currentUser.id, content: `Added ${Components.formatDuration(seconds)} of time spent`, createdAt: now });
                matched = true;
            }

            if (!matched) remainingLines.push(line);
        });

        issue.updatedAt = now;
        this.notify();
        return remainingLines.join('\n').trim();
    }
};
