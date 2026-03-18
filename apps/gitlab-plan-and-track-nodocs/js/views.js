/* ============================================================
   GitLab Plan & Track — View Renderers
   ============================================================ */

const Views = {

    // ── Sidebar ────────────────────────────────────────────
    renderSidebar() {
        const s = AppState.currentSection;
        return `
            <div class="sidebar-section">
                <div class="sidebar-header">Plan</div>
                <a class="sidebar-link${s === 'issues' ? ' active' : ''}" data-action="navigate" data-section="issues">
                    <span class="sidebar-icon">&#9673;</span> Issues
                </a>
                <a class="sidebar-link${s === 'boards' ? ' active' : ''}" data-action="navigate" data-section="boards">
                    <span class="sidebar-icon">&#9638;</span> Boards
                </a>
                <a class="sidebar-link${s === 'milestones' ? ' active' : ''}" data-action="navigate" data-section="milestones">
                    <span class="sidebar-icon">&#9872;</span> Milestones
                </a>
                <a class="sidebar-link${s === 'iterations' ? ' active' : ''}" data-action="navigate" data-section="iterations">
                    <span class="sidebar-icon">&#8634;</span> Iterations
                </a>
                <a class="sidebar-link${s === 'epics' ? ' active' : ''}" data-action="navigate" data-section="epics">
                    <span class="sidebar-icon">&#9733;</span> Epics
                </a>
                <a class="sidebar-link${s === 'roadmap' ? ' active' : ''}" data-action="navigate" data-section="roadmap">
                    <span class="sidebar-icon">&#9776;</span> Roadmap
                </a>
            </div>
            <div class="sidebar-section">
                <div class="sidebar-header">Manage</div>
                <a class="sidebar-link${s === 'labels' ? ' active' : ''}" data-action="navigate" data-section="labels">
                    <span class="sidebar-icon">&#9903;</span> Labels
                </a>
            </div>
            <div class="sidebar-section">
                <div class="sidebar-header">User</div>
                <a class="sidebar-link${s === 'notifications' ? ' active' : ''}" data-action="navigate" data-section="notifications">
                    <span class="sidebar-icon">&#128276;</span> Notifications
                    ${AppState.notificationFeed.filter(n => !n.read).length > 0 ? `<span class="sidebar-badge">${AppState.notificationFeed.filter(n => !n.read).length}</span>` : ''}
                </a>
            </div>
        `;
    },

    // ── Content Router ─────────────────────────────────────
    renderContent() {
        switch (AppState.currentSection) {
            case 'issues':
                if (AppState.currentView === 'detail' && AppState.selectedIssueId) return this.renderIssueDetail();
                if (AppState.currentView === 'create') return this.renderIssueCreate();
                return this.renderIssuesList();
            case 'boards': return this.renderBoards();
            case 'milestones':
                if (AppState.currentView === 'detail' && AppState.selectedMilestoneId) return this.renderMilestoneDetail();
                return this.renderMilestonesList();
            case 'iterations':
                if (AppState.currentView === 'detail' && AppState.selectedIterationId) return this.renderIterationDetail();
                return this.renderIterationsList();
            case 'epics':
                if (AppState.currentView === 'detail' && AppState.selectedEpicId) return this.renderEpicDetail();
                return this.renderEpicsList();
            case 'roadmap': return this.renderRoadmap();
            case 'labels': return this.renderLabels();
            case 'notifications': return this.renderNotifications();
            default: return this.renderIssuesList();
        }
    },

    // ════════════════════════════════════════════════════════
    //  ISSUES LIST
    // ════════════════════════════════════════════════════════
    renderIssuesList() {
        const f = AppState.issueFilters;
        const { issues, total, page, totalPages } = AppState.getPaginatedIssues();
        const userOpts = AppState.users.filter(u => u.state === 'active').map(u => ({ value: String(u.id), label: u.name }));
        const labelOpts = AppState.labels.map(l => ({ value: String(l.id), label: l.name, color: l.color }));
        const msOpts = [{ value: '', label: 'Any Milestone' }, ...AppState.milestones.map(m => ({ value: String(m.id), label: m.title }))];
        const iterOpts = [{ value: '', label: 'Any Iteration' }, ...AppState.iterations.map(i => ({ value: String(i.id), label: i.title }))];
        const sortOpts = SORT_OPTIONS.map(s => ({ value: s.value, label: s.label }));
        const typeOpts = [{ value: '', label: 'All Types' }, ...ISSUE_TYPES.map(t => ({ value: t.value, label: t.label }))];

        const hasSelection = AppState.selectedIssueIds.length > 0;

        return `
            <div class="page-header">
                <div class="page-header-top">
                    <h1>Issues</h1>
                    <button class="btn btn-primary" data-action="createIssue">New issue</button>
                </div>
                ${Components.breadcrumb([{ label: 'Project', section: 'issues' }, { label: 'Issues' }])}
            </div>

            <div class="issues-toolbar">
                <div class="status-tabs">
                    <button class="status-tab${f.status === 'opened' ? ' active' : ''}" data-action="filterStatus" data-status="opened">
                        Open <span class="count">${AppState.issues.filter(i => i.state === 'opened').length}</span>
                    </button>
                    <button class="status-tab${f.status === 'closed' ? ' active' : ''}" data-action="filterStatus" data-status="closed">
                        Closed <span class="count">${AppState.issues.filter(i => i.state === 'closed').length}</span>
                    </button>
                    <button class="status-tab${f.status === 'all' ? ' active' : ''}" data-action="filterStatus" data-status="all">
                        All <span class="count">${AppState.issues.length}</span>
                    </button>
                </div>
                ${Components.searchInput('issueSearch', f.search, 'Search issues...')}
            </div>

            <div class="filter-bar">
                <div class="filter-group">
                    ${Components.dropdown('filterAuthor', [{ value: '', label: 'Author' }, ...userOpts], f.authorId ? String(f.authorId) : '', { small: true })}
                    ${Components.dropdown('filterAssignee', [{ value: '', label: 'Assignee' }, ...userOpts], f.assigneeId ? String(f.assigneeId) : '', { small: true })}
                    ${Components.multiSelectDropdown('filterLabels', labelOpts, f.labelIds.map(String), { placeholder: 'Labels', searchable: true })}
                    ${Components.dropdown('filterMilestone', msOpts, f.milestoneId ? String(f.milestoneId) : '', { small: true })}
                    ${Components.dropdown('filterType', typeOpts, f.type || '', { small: true })}
                </div>
                <div class="filter-group">
                    ${Components.dropdown('sortIssues', sortOpts, f.sort, { small: true })}
                </div>
            </div>

            ${hasSelection ? `
                <div class="bulk-actions-bar">
                    <span>${AppState.selectedIssueIds.length} selected</span>
                    <button class="btn btn-sm" data-action="bulkClose">Close</button>
                    <button class="btn btn-sm" data-action="bulkReopen">Reopen</button>
                    ${Components.dropdown('bulkAssignee', [{ value: '', label: 'Assign...' }, ...userOpts], '', { small: true })}
                    ${Components.dropdown('bulkLabel', [{ value: '', label: 'Label...' }, ...labelOpts], '', { small: true })}
                    ${Components.dropdown('bulkMilestone', msOpts, '', { small: true })}
                    <button class="btn btn-sm btn-link" data-action="clearSelection">Clear</button>
                </div>
            ` : ''}

            ${issues.length === 0 ? Components.emptyState('No issues found', 'Try adjusting your filters or create a new issue.', '<button class="btn btn-primary" data-action="createIssue">New issue</button>') : `
                <div class="issues-list">
                    <div class="issues-list-header">
                        <label class="custom-checkbox issue-checkbox-all">
                            <input type="checkbox" id="selectAllIssues" ${AppState.selectedIssueIds.length === issues.length && issues.length > 0 ? 'checked' : ''}>
                            <span class="checkbox-mark"></span>
                        </label>
                        <span class="issues-list-col col-title">Title</span>
                        <span class="issues-list-col col-meta">Assignee</span>
                        <span class="issues-list-col col-meta">Milestone</span>
                        <span class="issues-list-col col-date">Updated</span>
                    </div>
                    ${issues.map(issue => this._issueRow(issue)).join('')}
                </div>
                ${Components.pagination(page, totalPages, total)}
            `}
        `;
    },

    _issueRow(issue) {
        const author = AppState.getUserById(issue.authorId);
        const assignees = issue.assignees.map(id => AppState.getUserById(id)).filter(Boolean);
        const labels = issue.labels.map(id => AppState.getLabelById(id)).filter(Boolean);
        const milestone = issue.milestoneId ? AppState.getMilestoneById(issue.milestoneId) : null;
        const isSelected = AppState.selectedIssueIds.includes(issue.id);

        return `
            <div class="issue-row${isSelected ? ' selected' : ''}${issue.confidential ? ' confidential' : ''}" data-issue-id="${issue.id}">
                <label class="custom-checkbox issue-checkbox">
                    <input type="checkbox" data-action="toggleIssueSelect" data-issue-id="${issue.id}" ${isSelected ? 'checked' : ''}>
                    <span class="checkbox-mark"></span>
                </label>
                <div class="issue-row-main">
                    <div class="issue-row-title-line">
                        ${Components.priorityIcon(issue.labels)}
                        ${issue.confidential ? '<span class="confidential-icon" title="Confidential">&#128274;</span>' : ''}
                        <a class="issue-title-link" data-action="viewIssue" data-issue-id="${issue.id}">${Components.escapeHtml(issue.title)}</a>
                        <span class="issue-iid">#${issue.iid}</span>
                        ${labels.slice(0, 4).map(l => Components.labelChip(l)).join('')}
                        ${labels.length > 4 ? `<span class="label-more">+${labels.length - 4}</span>` : ''}
                    </div>
                    <div class="issue-row-meta">
                        ${Components.typeBadge(issue.type)}
                        <span>opened ${Components.timeAgo(issue.createdAt)} by ${Components.escapeHtml(author ? author.name : 'Unknown')}</span>
                        ${issue.weight ? `<span class="issue-weight" title="Weight: ${issue.weight}">&#9878; ${issue.weight}</span>` : ''}
                        ${issue.dueDate ? `<span class="issue-due${new Date(issue.dueDate) < new Date() && issue.state === 'opened' ? ' overdue' : ''}" title="Due: ${issue.dueDate}">&#128197; ${Components.formatDate(issue.dueDate)}</span>` : ''}
                        ${issue.upvotes > 0 ? `<span class="issue-votes">&#128077; ${issue.upvotes}</span>` : ''}
                        ${(issue.timeEstimate || issue.timeSpent) ? `<span class="issue-time">&#9201; ${Components.formatDuration(issue.timeSpent || 0)}</span>` : ''}
                    </div>
                </div>
                <div class="issue-row-assignees">
                    ${assignees.length > 0 ? assignees.slice(0, 3).map(u => Components.avatar(u, 24)).join('') : '<span class="text-muted">-</span>'}
                </div>
                <div class="issue-row-milestone">
                    ${milestone ? `<span class="milestone-ref" title="${Components.escapeAttr(milestone.title)}">&#9872; ${Components.escapeHtml(milestone.title)}</span>` : '<span class="text-muted">-</span>'}
                </div>
                <div class="issue-row-date">
                    ${Components.timeAgo(issue.updatedAt)}
                </div>
            </div>
        `;
    },

    // ════════════════════════════════════════════════════════
    //  ISSUE DETAIL
    // ════════════════════════════════════════════════════════
    renderIssueDetail() {
        const issue = AppState.getIssueById(AppState.selectedIssueId);
        if (!issue) return Components.emptyState('Issue not found', 'This issue may have been deleted.');

        const author = AppState.getUserById(issue.authorId);
        const assignees = issue.assignees.map(id => AppState.getUserById(id)).filter(Boolean);
        const labels = issue.labels.map(id => AppState.getLabelById(id)).filter(Boolean);
        const milestone = issue.milestoneId ? AppState.getMilestoneById(issue.milestoneId) : null;
        const iteration = issue.iterationId ? AppState.getIterationById(issue.iterationId) : null;
        const epic = issue.epicId ? AppState.getEpicById(issue.epicId) : null;

        const userOpts = AppState.users.filter(u => u.state === 'active').map(u => ({ value: String(u.id), label: u.name }));
        const labelOpts = AppState.labels.map(l => ({ value: String(l.id), label: l.name, color: l.color }));
        const msOpts = [{ value: '', label: 'No milestone' }, ...AppState.milestones.filter(m => m.state === 'active').map(m => ({ value: String(m.id), label: m.title }))];
        const iterOpts = [{ value: '', label: 'No iteration' }, ...AppState.iterations.filter(i => i.state !== 'closed').map(i => ({ value: String(i.id), label: i.title }))];
        const epicOpts = [{ value: '', label: 'No epic' }, ...AppState.epics.filter(e => e.state === 'opened').map(e => ({ value: String(e.id), label: e.title }))];

        return `
            <div class="page-header">
                ${Components.breadcrumb([
                    { label: 'Project', section: 'issues' },
                    { label: 'Issues', section: 'issues' },
                    { label: `#${issue.iid}` }
                ])}
            </div>

            <div class="issue-detail-layout">
                <div class="issue-detail-main">
                    <div class="issue-detail-header">
                        <div class="issue-title-row">
                            <h1 class="issue-detail-title" id="issueTitle" contenteditable="true" data-issue-id="${issue.id}">${Components.escapeHtml(issue.title)}</h1>
                            <button class="btn btn-sm btn-secondary" data-action="saveIssueTitle" data-issue-id="${issue.id}" style="display:none" id="saveTitleBtn">Save</button>
                        </div>
                        <div class="issue-detail-meta">
                            ${Components.stateBadge(issue.state)}
                            ${Components.typeBadge(issue.type)}
                            ${issue.confidential ? '<span class="badge badge-warning">Confidential</span>' : ''}
                            <span>Opened ${Components.timeAgo(issue.createdAt)} by ${Components.avatar(author, 20)} ${Components.escapeHtml(author ? author.name : 'Unknown')}</span>
                        </div>
                    </div>

                    <div class="issue-description">
                        <div class="description-content" id="descriptionContent">
                            ${issue.description ? Components.renderMarkdown(issue.description) : '<p class="text-muted">No description provided.</p>'}
                        </div>
                        <button class="btn btn-sm btn-link" data-action="editDescription" data-issue-id="${issue.id}" id="editDescBtn">Edit</button>
                        <div class="description-editor" id="descriptionEditor" style="display:none">
                            <textarea class="form-textarea" id="descriptionTextarea" rows="10">${Components.escapeHtml(issue.description || '')}</textarea>
                            <div class="description-editor-actions">
                                <button class="btn btn-sm btn-primary" data-action="saveDescription" data-issue-id="${issue.id}">Save</button>
                                <button class="btn btn-sm btn-secondary" data-action="cancelEditDescription">Cancel</button>
                            </div>
                        </div>
                    </div>

                    ${this._renderRelatedIssues(issue)}
                    ${this._renderTimeTracking(issue)}
                    ${this._renderActivityFeed(issue)}
                    ${this._renderCommentBox(issue)}
                </div>

                <div class="issue-detail-sidebar">
                    <div class="sidebar-field">
                        <label class="sidebar-label">Assignees</label>
                        ${Components.multiSelectDropdown('issueAssignees', userOpts, issue.assignees.map(String), { placeholder: 'Select assignees', searchable: true })}
                        <div class="sidebar-value">
                            ${assignees.length > 0 ? assignees.map(u => `<div class="assignee-item">${Components.avatar(u, 24)} ${Components.escapeHtml(u.name)}</div>`).join('') : '<span class="text-muted">None</span>'}
                        </div>
                    </div>

                    <div class="sidebar-field">
                        <label class="sidebar-label">Labels</label>
                        ${Components.multiSelectDropdown('issueLabels', labelOpts, issue.labels.map(String), { placeholder: 'Select labels', searchable: true })}
                        <div class="sidebar-value label-list">
                            ${labels.length > 0 ? labels.map(l => Components.labelChip(l)).join('') : '<span class="text-muted">None</span>'}
                        </div>
                    </div>

                    <div class="sidebar-field">
                        <label class="sidebar-label">Milestone</label>
                        ${Components.dropdown('issueMilestone', msOpts, issue.milestoneId ? String(issue.milestoneId) : '', { small: true, searchable: true })}
                    </div>

                    <div class="sidebar-field">
                        <label class="sidebar-label">Iteration</label>
                        ${Components.dropdown('issueIteration', iterOpts, issue.iterationId ? String(issue.iterationId) : '', { small: true })}
                    </div>

                    <div class="sidebar-field">
                        <label class="sidebar-label">Epic</label>
                        ${Components.dropdown('issueEpic', epicOpts, issue.epicId ? String(issue.epicId) : '', { small: true, searchable: true })}
                    </div>

                    <div class="sidebar-field">
                        <label class="sidebar-label">Weight</label>
                        <input type="number" class="form-input form-input-sm" id="issueWeight" value="${issue.weight || ''}" min="0" max="99" placeholder="None" data-issue-id="${issue.id}">
                    </div>

                    <div class="sidebar-field">
                        <label class="sidebar-label">Due date</label>
                        ${Components.dateInput('issueDueDate', issue.dueDate)}
                    </div>

                    <div class="sidebar-field">
                        <label class="sidebar-label">Confidential</label>
                        ${Components.toggle('issueConfidential', issue.confidential)}
                    </div>

                    <div class="sidebar-field">
                        <label class="sidebar-label">Notifications</label>
                        ${Components.toggle('issueSubscribed', issue.subscribed)}
                        <span class="sidebar-hint">${issue.subscribed ? 'Subscribed' : 'Not subscribed'}</span>
                    </div>

                    <div class="sidebar-actions">
                        ${issue.state === 'opened'
                            ? `<button class="btn btn-warning btn-block" data-action="closeIssue" data-issue-id="${issue.id}">Close issue</button>`
                            : `<button class="btn btn-success btn-block" data-action="reopenIssue" data-issue-id="${issue.id}">Reopen issue</button>`
                        }
                    </div>
                </div>
            </div>
        `;
    },

    _renderRelatedIssues(issue) {
        if (issue.relatedIssues.length === 0) return '';
        const linkLabels = { blocks: 'Blocks', is_blocked_by: 'Is blocked by', relates_to: 'Related to' };
        return `
            <div class="related-issues-section">
                <h3>Related Issues</h3>
                <div class="related-issues-list">
                    ${issue.relatedIssues.map(r => {
                        const related = AppState.getIssueById(r.issueId);
                        if (!related) return '';
                        return `<div class="related-issue-item">
                            <span class="related-link-type">${linkLabels[r.linkType] || r.linkType}</span>
                            ${Components.stateBadge(related.state)}
                            <a class="related-issue-link" data-action="viewIssue" data-issue-id="${related.id}">#${related.iid} ${Components.escapeHtml(related.title)}</a>
                            <button class="btn btn-icon btn-sm" data-action="removeRelatedIssue" data-issue-id="${issue.id}" data-related-id="${related.id}" title="Remove">&times;</button>
                        </div>`;
                    }).join('')}
                </div>
                <button class="btn btn-sm btn-link" data-action="addRelatedIssue" data-issue-id="${issue.id}">+ Add related issue</button>
            </div>
        `;
    },

    _renderTimeTracking(issue) {
        return `
            <div class="time-tracking-section">
                <h3>Time Tracking</h3>
                ${Components.timeTrackingBar(issue.timeEstimate, issue.timeSpent)}
                <div class="time-tracking-actions">
                    <button class="btn btn-sm btn-link" data-action="setEstimate" data-issue-id="${issue.id}">Set estimate</button>
                    <button class="btn btn-sm btn-link" data-action="logTime" data-issue-id="${issue.id}">Log time</button>
                </div>
            </div>
        `;
    },

    _renderActivityFeed(issue) {
        const activities = (issue.activities || []).slice().sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
        return `
            <div class="activity-feed">
                <h3>Activity <span class="count">${activities.length}</span></h3>
                ${activities.length === 0 ? '<p class="text-muted">No activity yet.</p>' : ''}
                ${activities.map(a => {
                    const actor = AppState.getUserById(a.authorId);
                    const isComment = a.type === 'comment';
                    return `
                        <div class="activity-item ${isComment ? 'activity-comment' : 'activity-event'}">
                            <div class="activity-avatar">${Components.avatar(actor, 28)}</div>
                            <div class="activity-body">
                                <div class="activity-header">
                                    <strong>${Components.escapeHtml(actor ? actor.name : 'Unknown')}</strong>
                                    ${isComment ? 'commented' : ''}
                                    <span class="activity-time">${Components.timeAgo(a.createdAt)}</span>
                                </div>
                                <div class="activity-content">
                                    ${isComment ? Components.renderMarkdown(a.content) : `<span class="activity-event-text">${Components.escapeHtml(a.content)}</span>`}
                                </div>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    },

    _renderCommentBox(issue) {
        return `
            <div class="comment-box">
                <div class="comment-box-header">
                    ${Components.avatar(AppState.currentUser, 32)}
                    <span>Write a comment...</span>
                </div>
                <textarea class="form-textarea" id="commentTextarea" rows="4" placeholder="Write a comment or use slash commands (/assign, /label, /close, /weight, /due, /estimate, /spend)..."></textarea>
                <div class="comment-box-hint">
                    Supports: /assign @user, /label ~name, /milestone %title, /close, /reopen, /weight N, /due YYYY-MM-DD, /estimate Nh, /spend NhMm
                </div>
                <div class="comment-box-actions">
                    <button class="btn btn-primary" data-action="submitComment" data-issue-id="${issue.id}">Comment</button>
                </div>
            </div>
        `;
    },

    // ════════════════════════════════════════════════════════
    //  ISSUE CREATE
    // ════════════════════════════════════════════════════════
    renderIssueCreate() {
        const userOpts = AppState.users.filter(u => u.state === 'active').map(u => ({ value: String(u.id), label: u.name }));
        const labelOpts = AppState.labels.map(l => ({ value: String(l.id), label: l.name, color: l.color }));
        const msOpts = [{ value: '', label: 'No milestone' }, ...AppState.milestones.filter(m => m.state === 'active').map(m => ({ value: String(m.id), label: m.title }))];
        const iterOpts = [{ value: '', label: 'No iteration' }, ...AppState.iterations.filter(i => i.state !== 'closed').map(i => ({ value: String(i.id), label: i.title }))];
        const epicOpts = [{ value: '', label: 'No epic' }, ...AppState.epics.filter(e => e.state === 'opened').map(e => ({ value: String(e.id), label: e.title }))];
        const typeOpts = ISSUE_TYPES.map(t => ({ value: t.value, label: t.label }));
        const templateOpts = [{ value: '', label: 'No template' }, ...AppState.issueTemplates.map(t => ({ value: String(t.id), label: t.name }))];

        return `
            <div class="page-header">
                ${Components.breadcrumb([
                    { label: 'Project', section: 'issues' },
                    { label: 'Issues', section: 'issues' },
                    { label: 'New Issue' }
                ])}
                <h1>New Issue</h1>
            </div>

            <div class="issue-create-form">
                <div class="issue-create-main">
                    ${Components.formField('newIssueType', 'Type', Components.dropdown('newIssueType', typeOpts, 'issue'))}
                    ${Components.formField('newIssueTemplate', 'Template', Components.dropdown('newIssueTemplate', templateOpts, ''))}
                    ${Components.formField('newIssueTitle', 'Title', Components.textInput('newIssueTitle', '', { placeholder: 'Enter issue title' }), { required: true })}
                    ${Components.formField('newIssueDescription', 'Description', Components.textarea('newIssueDescription', '', { placeholder: 'Describe the issue using Markdown...', rows: 10 }))}

                    <div class="form-row">
                        ${Components.formField('newIssueAssignees', 'Assignees', Components.multiSelectDropdown('newIssueAssignees', userOpts, [], { placeholder: 'Select assignees', searchable: true }))}
                        ${Components.formField('newIssueLabels', 'Labels', Components.multiSelectDropdown('newIssueLabels', labelOpts, [], { placeholder: 'Select labels', searchable: true }))}
                    </div>

                    <div class="form-row">
                        ${Components.formField('newIssueMilestone', 'Milestone', Components.dropdown('newIssueMilestone', msOpts, '', { searchable: true }))}
                        ${Components.formField('newIssueIteration', 'Iteration', Components.dropdown('newIssueIteration', iterOpts, ''))}
                    </div>

                    <div class="form-row">
                        ${Components.formField('newIssueEpic', 'Epic', Components.dropdown('newIssueEpic', epicOpts, '', { searchable: true }))}
                        ${Components.formField('newIssueWeight', 'Weight', Components.numberInput('newIssueWeight', null, { min: 0, max: 99, placeholder: 'None' }))}
                    </div>

                    <div class="form-row">
                        ${Components.formField('newIssueDueDate', 'Due date', Components.dateInput('newIssueDueDate', ''))}
                        ${Components.formField('newIssueConfidential', 'Confidential', Components.checkbox('newIssueConfidentialCheck', 'This issue is confidential', false))}
                    </div>

                    <div class="form-actions">
                        <button class="btn btn-secondary" data-action="cancelCreate">Cancel</button>
                        <button class="btn btn-primary" data-action="submitNewIssue" id="submitNewIssueBtn">Create issue</button>
                    </div>
                </div>
            </div>
        `;
    },

    // ════════════════════════════════════════════════════════
    //  BOARDS (KANBAN)
    // ════════════════════════════════════════════════════════
    renderBoards() {
        const boards = AppState.boards;
        const selectedBoard = AppState.selectedBoardId ? AppState.getBoardById(AppState.selectedBoardId) : boards[0];
        if (!selectedBoard) return Components.emptyState('No boards', 'Create a board to organize your issues.');

        if (AppState.selectedBoardId === null && boards.length > 0) {
            AppState.selectedBoardId = boards[0].id;
        }

        const boardOpts = boards.map(b => ({ value: String(b.id), label: b.name }));
        const bf = AppState.boardFilters;

        // Get issues for each list
        let boardIssues = AppState.issues.filter(i => {
            if (bf.assigneeId && !i.assignees.includes(bf.assigneeId)) return false;
            if (bf.milestoneId && i.milestoneId !== bf.milestoneId) return false;
            if (bf.labelIds.length > 0 && !bf.labelIds.every(lid => i.labels.includes(lid))) return false;
            return true;
        });

        return `
            <div class="page-header">
                <div class="page-header-top">
                    <h1>Boards</h1>
                    <div class="board-controls">
                        ${Components.dropdown('boardSelect', boardOpts, String(selectedBoard.id), { small: true })}
                    </div>
                </div>
            </div>

            <div class="board-container" data-board-id="${selectedBoard.id}">
                ${selectedBoard.lists.map(list => {
                    const listIssues = this._getIssuesForList(list, boardIssues, selectedBoard);
                    return `
                        <div class="board-list" data-list-id="${list.id}" data-list-type="${list.type}">
                            <div class="board-list-header">
                                <span class="board-list-title">${Components.escapeHtml(list.title)}</span>
                                <span class="board-list-count">${listIssues.length}</span>
                                ${list.type === 'label' ? `<button class="btn btn-icon btn-sm board-list-remove" data-action="removeBoardList" data-list-id="${list.id}" data-board-id="${selectedBoard.id}" title="Remove list">&times;</button>` : ''}
                            </div>
                            <div class="board-list-body" data-list-id="${list.id}" data-board-id="${selectedBoard.id}">
                                ${listIssues.map(issue => this._boardCard(issue)).join('')}
                            </div>
                            ${list.type !== 'closed' ? `<button class="btn btn-sm btn-link board-add-issue" data-action="createIssueFromBoard" data-list-id="${list.id}" data-board-id="${selectedBoard.id}">+ New issue</button>` : ''}
                        </div>
                    `;
                }).join('')}
                <div class="board-list board-list-add">
                    <button class="btn btn-sm btn-link" data-action="addBoardList" data-board-id="${selectedBoard.id}">+ Add list</button>
                </div>
            </div>
        `;
    },

    _getIssuesForList(list, allIssues, board) {
        if (list.type === 'closed') {
            return allIssues.filter(i => i.state === 'closed');
        }
        if (list.type === 'backlog') {
            // Open issues not in any label-based list
            const labelListIds = board.lists.filter(l => l.type === 'label' && l.labelId).map(l => l.labelId);
            return allIssues.filter(i => i.state === 'opened' && !i.labels.some(lid => labelListIds.includes(lid)));
        }
        if (list.type === 'label' && list.labelId) {
            return allIssues.filter(i => i.state === 'opened' && i.labels.includes(list.labelId));
        }
        return [];
    },

    _boardCard(issue) {
        const assignees = issue.assignees.map(id => AppState.getUserById(id)).filter(Boolean);
        const labels = issue.labels.map(id => AppState.getLabelById(id)).filter(Boolean);
        return `
            <div class="board-card" draggable="true" data-issue-id="${issue.id}">
                <div class="board-card-title">
                    <a data-action="viewIssue" data-issue-id="${issue.id}">${Components.escapeHtml(issue.title)}</a>
                    <span class="issue-iid">#${issue.iid}</span>
                </div>
                <div class="board-card-labels">
                    ${labels.slice(0, 3).map(l => Components.labelChip(l)).join('')}
                </div>
                <div class="board-card-footer">
                    <div class="board-card-assignees">
                        ${assignees.slice(0, 2).map(u => Components.avatar(u, 20)).join('')}
                    </div>
                    ${issue.weight ? `<span class="issue-weight-sm">&#9878; ${issue.weight}</span>` : ''}
                </div>
            </div>
        `;
    },

    // ════════════════════════════════════════════════════════
    //  MILESTONES
    // ════════════════════════════════════════════════════════
    renderMilestonesList() {
        const active = AppState.milestones.filter(m => m.state === 'active');
        const closed = AppState.milestones.filter(m => m.state === 'closed');

        return `
            <div class="page-header">
                <div class="page-header-top">
                    <h1>Milestones</h1>
                    <button class="btn btn-primary" data-action="createMilestone">New milestone</button>
                </div>
            </div>

            ${Components.tabs('milestoneTabs', [
                { key: 'active', label: 'Active', count: active.length },
                { key: 'closed', label: 'Closed', count: closed.length }
            ], AppState._milestoneTab || 'active')}

            <div class="milestones-list">
                ${(AppState._milestoneTab === 'closed' ? closed : active).map(m => {
                    const progress = AppState.getMilestoneProgress(m.id);
                    return `
                        <div class="milestone-item" data-milestone-id="${m.id}">
                            <div class="milestone-item-header">
                                <a class="milestone-title-link" data-action="viewMilestone" data-milestone-id="${m.id}">
                                    &#9872; ${Components.escapeHtml(m.title)}
                                </a>
                                <div class="milestone-actions">
                                    <button class="btn btn-sm btn-link" data-action="editMilestone" data-milestone-id="${m.id}">Edit</button>
                                    ${m.state === 'active'
                                        ? `<button class="btn btn-sm btn-link" data-action="closeMilestone" data-milestone-id="${m.id}">Close</button>`
                                        : `<button class="btn btn-sm btn-link" data-action="activateMilestone" data-milestone-id="${m.id}">Reopen</button>`
                                    }
                                    <button class="btn btn-sm btn-link btn-danger-link" data-action="deleteMilestone" data-milestone-id="${m.id}">Delete</button>
                                </div>
                            </div>
                            <div class="milestone-item-meta">
                                ${m.startDate ? `<span>Start: ${Components.formatDate(m.startDate)}</span>` : ''}
                                ${m.dueDate ? `<span>Due: ${Components.formatDate(m.dueDate)}</span>` : '<span>No due date</span>'}
                            </div>
                            ${m.description ? `<p class="milestone-desc">${Components.escapeHtml(m.description)}</p>` : ''}
                            <div class="milestone-progress">
                                ${Components.progressBar(progress.percentage)}
                                <span class="milestone-progress-text">${progress.closed} closed / ${progress.open} open</span>
                            </div>
                        </div>
                    `;
                }).join('')}
                ${((AppState._milestoneTab === 'closed' ? closed : active).length === 0) ? Components.emptyState('No milestones', 'Create a milestone to track progress.') : ''}
            </div>
        `;
    },

    renderMilestoneDetail() {
        const ms = AppState.getMilestoneById(AppState.selectedMilestoneId);
        if (!ms) return Components.emptyState('Milestone not found', '');
        const progress = AppState.getMilestoneProgress(ms.id);
        const issues = AppState.getIssuesForMilestone(ms.id);
        const openIssues = issues.filter(i => i.state === 'opened');
        const closedIssues = issues.filter(i => i.state === 'closed');

        return `
            <div class="page-header">
                ${Components.breadcrumb([
                    { label: 'Project', section: 'issues' },
                    { label: 'Milestones', section: 'milestones' },
                    { label: ms.title }
                ])}
                <h1>&#9872; ${Components.escapeHtml(ms.title)}</h1>
                <div class="milestone-detail-meta">
                    ${Components.badge(ms.state, ms.state === 'active' ? 'success' : 'default')}
                    ${ms.startDate ? `<span>Start: ${Components.formatDate(ms.startDate)}</span>` : ''}
                    ${ms.dueDate ? `<span>Due: ${Components.formatDate(ms.dueDate)}</span>` : ''}
                </div>
            </div>

            ${ms.description ? `<div class="milestone-description">${Components.renderMarkdown(ms.description)}</div>` : ''}

            <div class="milestone-progress-detail">
                ${Components.progressBar(progress.percentage)}
                <div class="milestone-stats">
                    <span>${progress.percentage}% complete</span>
                    <span>${progress.closed} closed</span>
                    <span>${progress.open} open</span>
                    <span>${progress.total} total</span>
                </div>
            </div>

            ${Components.tabs('milestoneIssueTabs', [
                { key: 'open', label: 'Open', count: openIssues.length },
                { key: 'closed', label: 'Closed', count: closedIssues.length }
            ], AppState._milestoneIssueTab || 'open')}

            <div class="issues-list compact">
                ${(AppState._milestoneIssueTab === 'closed' ? closedIssues : openIssues).map(i => this._issueRow(i)).join('')}
                ${((AppState._milestoneIssueTab === 'closed' ? closedIssues : openIssues).length === 0) ? '<p class="text-muted pad">No issues.</p>' : ''}
            </div>
        `;
    },

    // ════════════════════════════════════════════════════════
    //  ITERATIONS
    // ════════════════════════════════════════════════════════
    renderIterationsList() {
        const cadences = AppState.iterationCadences;

        return `
            <div class="page-header">
                <div class="page-header-top">
                    <h1>Iterations</h1>
                    <button class="btn btn-primary" data-action="createIteration">New iteration</button>
                </div>
            </div>

            ${cadences.map(c => {
                const iters = AppState.iterations.filter(i => i.cadenceId === c.id);
                return `
                    <div class="cadence-section">
                        <div class="cadence-header">
                            <h2>${Components.escapeHtml(c.title)}</h2>
                            <span class="text-muted">${Components.escapeHtml(c.description || '')} &middot; ${c.durationWeeks}-week cycles</span>
                        </div>
                        <div class="iterations-list">
                            ${iters.map(it => {
                                const progress = AppState.getIterationProgress(it.id);
                                const stateClass = it.state === 'current' ? 'badge-success' : it.state === 'upcoming' ? 'badge-info' : 'badge-default';
                                return `
                                    <div class="iteration-item" data-iteration-id="${it.id}">
                                        <div class="iteration-item-header">
                                            <a class="iteration-title-link" data-action="viewIteration" data-iteration-id="${it.id}">
                                                ${Components.escapeHtml(it.title)}
                                            </a>
                                            <span class="badge ${stateClass}">${it.state}</span>
                                        </div>
                                        <div class="iteration-item-meta">
                                            <span>${Components.formatDate(it.startDate)} — ${Components.formatDate(it.endDate)}</span>
                                            <span>${progress.total} issues</span>
                                            <span>${progress.totalWeight} weight</span>
                                        </div>
                                        ${Components.progressBar(progress.percentage, { size: 'small' })}
                                    </div>
                                `;
                            }).join('')}
                            ${iters.length === 0 ? '<p class="text-muted">No iterations in this cadence.</p>' : ''}
                        </div>
                    </div>
                `;
            }).join('')}
        `;
    },

    renderIterationDetail() {
        const it = AppState.getIterationById(AppState.selectedIterationId);
        if (!it) return Components.emptyState('Iteration not found', '');
        const cadence = AppState.getCadenceById(it.cadenceId);
        const progress = AppState.getIterationProgress(it.id);
        const issues = AppState.getIssuesForIteration(it.id);
        const openIssues = issues.filter(i => i.state === 'opened');
        const closedIssues = issues.filter(i => i.state === 'closed');
        const stateClass = it.state === 'current' ? 'badge-success' : it.state === 'upcoming' ? 'badge-info' : 'badge-default';

        return `
            <div class="page-header">
                ${Components.breadcrumb([
                    { label: 'Project', section: 'issues' },
                    { label: 'Iterations', section: 'iterations' },
                    { label: it.title }
                ])}
                <h1>${Components.escapeHtml(it.title)}</h1>
                <div class="iteration-detail-meta">
                    <span class="badge ${stateClass}">${it.state}</span>
                    ${cadence ? `<span>${Components.escapeHtml(cadence.title)}</span>` : ''}
                    <span>${Components.formatDate(it.startDate)} — ${Components.formatDate(it.endDate)}</span>
                </div>
            </div>

            <div class="iteration-stats-row">
                <div class="stat-card"><div class="stat-value">${progress.total}</div><div class="stat-label">Total Issues</div></div>
                <div class="stat-card"><div class="stat-value">${progress.closed}</div><div class="stat-label">Completed</div></div>
                <div class="stat-card"><div class="stat-value">${progress.open}</div><div class="stat-label">Remaining</div></div>
                <div class="stat-card"><div class="stat-value">${progress.totalWeight}</div><div class="stat-label">Total Weight</div></div>
                <div class="stat-card"><div class="stat-value">${progress.percentage}%</div><div class="stat-label">Complete</div></div>
            </div>

            ${Components.progressBar(progress.percentage)}

            <div class="burndown-placeholder">
                <div class="burndown-chart">
                    <div class="burndown-label">Burndown Chart</div>
                    <div class="burndown-visual">
                        ${this._renderSimpleBurndown(it, issues)}
                    </div>
                </div>
            </div>

            ${Components.tabs('iterationIssueTabs', [
                { key: 'open', label: 'Open', count: openIssues.length },
                { key: 'closed', label: 'Closed', count: closedIssues.length }
            ], AppState._iterationIssueTab || 'open')}

            <div class="issues-list compact">
                ${(AppState._iterationIssueTab === 'closed' ? closedIssues : openIssues).map(i => this._issueRow(i)).join('')}
                ${((AppState._iterationIssueTab === 'closed' ? closedIssues : openIssues).length === 0) ? '<p class="text-muted pad">No issues.</p>' : ''}
            </div>
        `;
    },

    _renderSimpleBurndown(iteration, issues) {
        const start = new Date(iteration.startDate);
        const end = new Date(iteration.endDate);
        const totalDays = Math.ceil((end - start) / 86400000);
        const totalWeight = issues.reduce((s, i) => s + (i.weight || 1), 0);

        // Simple SVG burndown
        const width = 600;
        const height = 200;
        const padding = 40;

        // Ideal line
        const idealLine = `M${padding},${padding} L${width - padding},${height - padding}`;

        // Calculate actual burndown points
        let points = [`${padding},${padding}`];
        let remaining = totalWeight;
        const closedIssues = issues.filter(i => i.state === 'closed' && i.closedAt).sort((a, b) => new Date(a.closedAt) - new Date(b.closedAt));

        closedIssues.forEach(issue => {
            const closedDate = new Date(issue.closedAt);
            const dayIndex = Math.max(0, Math.ceil((closedDate - start) / 86400000));
            const x = padding + (dayIndex / totalDays) * (width - 2 * padding);
            remaining -= (issue.weight || 1);
            const y = padding + ((totalWeight - remaining) / totalWeight) * (height - 2 * padding);
            points.push(`${x},${height - y + padding}`);
        });

        // Extend to today
        const today = new Date();
        const todayIndex = Math.max(0, Math.ceil((today - start) / 86400000));
        const todayX = Math.min(width - padding, padding + (todayIndex / totalDays) * (width - 2 * padding));
        const todayY = padding + ((totalWeight - remaining) / totalWeight) * (height - 2 * padding);
        points.push(`${todayX},${height - todayY + padding}`);

        return `
            <svg width="${width}" height="${height}" class="burndown-svg">
                <line x1="${padding}" y1="${padding}" x2="${width - padding}" y2="${height - padding}" stroke="#ddd" stroke-width="2" stroke-dasharray="5,5"/>
                <polyline points="${points.join(' ')}" fill="none" stroke="#3498db" stroke-width="2"/>
                <text x="${padding}" y="${height - 5}" font-size="11" fill="#999">${Components.formatDate(iteration.startDate)}</text>
                <text x="${width - padding - 60}" y="${height - 5}" font-size="11" fill="#999">${Components.formatDate(iteration.endDate)}</text>
                <text x="${padding - 5}" y="${padding - 5}" font-size="11" fill="#999">${totalWeight}</text>
                <text x="${padding - 5}" y="${height - padding + 15}" font-size="11" fill="#999">0</text>
            </svg>
        `;
    },

    // ════════════════════════════════════════════════════════
    //  EPICS
    // ════════════════════════════════════════════════════════
    renderEpicsList() {
        const opened = AppState.epics.filter(e => e.state === 'opened');
        const closed = AppState.epics.filter(e => e.state === 'closed');
        const topLevel = (AppState._epicTab === 'closed' ? closed : opened).filter(e => !e.parentEpicId);

        return `
            <div class="page-header">
                <div class="page-header-top">
                    <h1>Epics</h1>
                    <button class="btn btn-primary" data-action="createEpic">New epic</button>
                </div>
            </div>

            ${Components.tabs('epicTabs', [
                { key: 'opened', label: 'Open', count: opened.length },
                { key: 'closed', label: 'Closed', count: closed.length }
            ], AppState._epicTab || 'opened')}

            <div class="epics-list">
                ${topLevel.map(epic => this._epicItem(epic, 0)).join('')}
                ${topLevel.length === 0 ? Components.emptyState('No epics', 'Create an epic to group related issues.') : ''}
            </div>
        `;
    },

    _epicItem(epic, depth) {
        const progress = AppState.getEpicProgress(epic.id);
        const labels = epic.labels.map(id => AppState.getLabelById(id)).filter(Boolean);
        const childEpics = AppState.getChildEpics(epic.id);

        return `
            <div class="epic-item" style="margin-left:${depth * 24}px" data-epic-id="${epic.id}">
                <div class="epic-item-header">
                    <a class="epic-title-link" data-action="viewEpic" data-epic-id="${epic.id}">
                        ${epic.confidential ? '<span class="confidential-icon">&#128274;</span>' : ''}
                        ${Components.escapeHtml(epic.title)}
                    </a>
                    ${Components.stateBadge(epic.state)}
                    ${labels.map(l => Components.labelChip(l)).join('')}
                </div>
                <div class="epic-item-meta">
                    ${epic.startDate ? `<span>${Components.formatDate(epic.startDate)}</span>` : ''}
                    ${epic.startDate && epic.dueDate ? '<span>—</span>' : ''}
                    ${epic.dueDate ? `<span>${Components.formatDate(epic.dueDate)}</span>` : ''}
                    <span>${progress.total} issues</span>
                    ${progress.childEpicsCount > 0 ? `<span>${progress.childEpicsCount} child epics</span>` : ''}
                </div>
                ${Components.progressBar(progress.percentage, { size: 'small' })}
            </div>
            ${childEpics.map(child => this._epicItem(child, depth + 1)).join('')}
        `;
    },

    renderEpicDetail() {
        const epic = AppState.getEpicById(AppState.selectedEpicId);
        if (!epic) return Components.emptyState('Epic not found', '');
        const progress = AppState.getEpicProgress(epic.id);
        const issues = AppState.getIssuesForEpic(epic.id);
        const childEpics = AppState.getChildEpics(epic.id);
        const labels = epic.labels.map(id => AppState.getLabelById(id)).filter(Boolean);
        const author = AppState.getUserById(epic.authorId);
        const parentEpic = epic.parentEpicId ? AppState.getEpicById(epic.parentEpicId) : null;

        return `
            <div class="page-header">
                ${Components.breadcrumb([
                    { label: 'Project', section: 'issues' },
                    { label: 'Epics', section: 'epics' },
                    { label: epic.title }
                ])}
                <h1>${epic.confidential ? '<span class="confidential-icon">&#128274;</span> ' : ''}${Components.escapeHtml(epic.title)}</h1>
                <div class="epic-detail-meta">
                    ${Components.stateBadge(epic.state)}
                    <span>Created ${Components.timeAgo(epic.createdAt)} by ${Components.escapeHtml(author ? author.name : 'Unknown')}</span>
                    ${parentEpic ? `<span>Parent: <a data-action="viewEpic" data-epic-id="${parentEpic.id}">${Components.escapeHtml(parentEpic.title)}</a></span>` : ''}
                </div>
            </div>

            <div class="epic-detail-layout">
                <div class="epic-detail-main">
                    ${epic.description ? `<div class="epic-description">${Components.renderMarkdown(epic.description)}</div>` : ''}

                    <div class="epic-progress-section">
                        <h3>Progress</h3>
                        ${Components.progressBar(progress.percentage)}
                        <div class="milestone-stats">
                            <span>${progress.percentage}% complete</span>
                            <span>${progress.closed} closed</span>
                            <span>${progress.open} open</span>
                        </div>
                    </div>

                    ${epic.startDate && epic.dueDate ? `
                        <div class="epic-roadmap-bar">
                            <h3>Timeline</h3>
                            <div class="roadmap-single-bar">
                                <span class="roadmap-date">${Components.formatDate(epic.startDate)}</span>
                                <div class="roadmap-bar-track">
                                    <div class="roadmap-bar-fill" style="width:${this._getTimelineProgress(epic.startDate, epic.dueDate)}%"></div>
                                </div>
                                <span class="roadmap-date">${Components.formatDate(epic.dueDate)}</span>
                            </div>
                        </div>
                    ` : ''}

                    ${childEpics.length > 0 ? `
                        <div class="epic-children-section">
                            <h3>Child Epics (${childEpics.length})</h3>
                            ${childEpics.map(child => this._epicItem(child, 0)).join('')}
                        </div>
                    ` : ''}

                    <div class="epic-issues-section">
                        <h3>Issues (${issues.length})</h3>
                        <div class="issues-list compact">
                            ${issues.map(i => this._issueRow(i)).join('')}
                            ${issues.length === 0 ? '<p class="text-muted">No issues assigned to this epic.</p>' : ''}
                        </div>
                    </div>
                </div>

                <div class="epic-detail-sidebar">
                    <div class="sidebar-field">
                        <label class="sidebar-label">Labels</label>
                        <div class="sidebar-value label-list">
                            ${labels.length > 0 ? labels.map(l => Components.labelChip(l)).join('') : '<span class="text-muted">None</span>'}
                        </div>
                    </div>
                    <div class="sidebar-field">
                        <label class="sidebar-label">Start date</label>
                        <span>${epic.startDate ? Components.formatDate(epic.startDate) : 'None'}</span>
                    </div>
                    <div class="sidebar-field">
                        <label class="sidebar-label">Due date</label>
                        <span>${epic.dueDate ? Components.formatDate(epic.dueDate) : 'None'}</span>
                    </div>
                    <div class="sidebar-field">
                        <label class="sidebar-label">Confidential</label>
                        <span>${epic.confidential ? 'Yes' : 'No'}</span>
                    </div>
                    <div class="sidebar-actions">
                        ${epic.state === 'opened'
                            ? `<button class="btn btn-warning btn-block" data-action="closeEpic" data-epic-id="${epic.id}">Close epic</button>`
                            : `<button class="btn btn-success btn-block" data-action="reopenEpic" data-epic-id="${epic.id}">Reopen epic</button>`
                        }
                    </div>
                </div>
            </div>
        `;
    },

    _getTimelineProgress(startDate, dueDate) {
        const now = new Date();
        const start = new Date(startDate);
        const end = new Date(dueDate);
        if (now <= start) return 0;
        if (now >= end) return 100;
        return Math.round(((now - start) / (end - start)) * 100);
    },

    // ════════════════════════════════════════════════════════
    //  ROADMAP
    // ════════════════════════════════════════════════════════
    renderRoadmap() {
        const epics = AppState.epics.filter(e => e.startDate && e.dueDate);
        const milestones = AppState.milestones.filter(m => m.startDate && m.dueDate);

        // Determine time range
        const allDates = [...epics.flatMap(e => [new Date(e.startDate), new Date(e.dueDate)]), ...milestones.flatMap(m => [new Date(m.startDate), new Date(m.dueDate)])];
        if (allDates.length === 0) return Components.emptyState('No roadmap data', 'Add start and due dates to epics to see them on the roadmap.');

        const minDate = new Date(Math.min(...allDates));
        const maxDate = new Date(Math.max(...allDates));
        // Add padding
        minDate.setDate(minDate.getDate() - 14);
        maxDate.setDate(maxDate.getDate() + 14);
        const totalDays = Math.ceil((maxDate - minDate) / 86400000);

        // Generate month headers
        const months = [];
        const d = new Date(minDate.getFullYear(), minDate.getMonth(), 1);
        while (d <= maxDate) {
            const monthStart = new Date(d);
            const leftPct = Math.max(0, ((monthStart - minDate) / (maxDate - minDate)) * 100);
            months.push({ label: d.toLocaleDateString('en-US', { month: 'short', year: 'numeric' }), leftPct });
            d.setMonth(d.getMonth() + 1);
        }

        // Today marker
        const todayPct = ((new Date() - minDate) / (maxDate - minDate)) * 100;

        return `
            <div class="page-header">
                <h1>Roadmap</h1>
            </div>

            <div class="roadmap-container">
                <div class="roadmap-header">
                    ${months.map(m => `<div class="roadmap-month" style="left:${m.leftPct}%">${m.label}</div>`).join('')}
                </div>
                <div class="roadmap-today" style="left:${todayPct}%"><span class="roadmap-today-label">Today</span></div>

                <div class="roadmap-section">
                    <h3>Epics</h3>
                    ${epics.map(epic => {
                        const start = new Date(epic.startDate);
                        const end = new Date(epic.dueDate);
                        const leftPct = ((start - minDate) / (maxDate - minDate)) * 100;
                        const widthPct = ((end - start) / (maxDate - minDate)) * 100;
                        const progress = AppState.getEpicProgress(epic.id);
                        return `
                            <div class="roadmap-row">
                                <div class="roadmap-row-label">
                                    <a data-action="viewEpic" data-epic-id="${epic.id}">${Components.escapeHtml(epic.title)}</a>
                                </div>
                                <div class="roadmap-row-bar">
                                    <div class="roadmap-bar" style="left:${leftPct}%;width:${widthPct}%" title="${Components.escapeAttr(epic.title)} (${Components.formatDate(epic.startDate)} - ${Components.formatDate(epic.dueDate)})">
                                        <div class="roadmap-bar-progress" style="width:${progress.percentage}%"></div>
                                        <span class="roadmap-bar-label">${progress.percentage}%</span>
                                    </div>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>

                <div class="roadmap-section">
                    <h3>Milestones</h3>
                    ${milestones.map(ms => {
                        const start = new Date(ms.startDate);
                        const end = new Date(ms.dueDate);
                        const leftPct = ((start - minDate) / (maxDate - minDate)) * 100;
                        const widthPct = ((end - start) / (maxDate - minDate)) * 100;
                        const progress = AppState.getMilestoneProgress(ms.id);
                        return `
                            <div class="roadmap-row">
                                <div class="roadmap-row-label">
                                    <a data-action="viewMilestone" data-milestone-id="${ms.id}">&#9872; ${Components.escapeHtml(ms.title)}</a>
                                </div>
                                <div class="roadmap-row-bar">
                                    <div class="roadmap-bar roadmap-bar-milestone" style="left:${leftPct}%;width:${widthPct}%">
                                        <div class="roadmap-bar-progress" style="width:${progress.percentage}%"></div>
                                        <span class="roadmap-bar-label">${progress.percentage}%</span>
                                    </div>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    },

    // ════════════════════════════════════════════════════════
    //  LABELS
    // ════════════════════════════════════════════════════════
    renderLabels() {
        const labels = AppState.labels;
        const scopedGroups = {};
        const unscopedLabels = [];

        labels.forEach(l => {
            if (l.scoped) {
                const scope = l.name.split('::')[0];
                if (!scopedGroups[scope]) scopedGroups[scope] = [];
                scopedGroups[scope].push(l);
            } else {
                unscopedLabels.push(l);
            }
        });

        return `
            <div class="page-header">
                <div class="page-header-top">
                    <h1>Labels</h1>
                    <button class="btn btn-primary" data-action="createLabel">New label</button>
                </div>
            </div>

            ${Object.keys(scopedGroups).length > 0 ? `
                <div class="label-section">
                    <h3>Scoped Labels</h3>
                    ${Object.entries(scopedGroups).map(([scope, scopeLabels]) => `
                        <div class="label-group">
                            <div class="label-group-header">${Components.escapeHtml(scope)}::</div>
                            ${scopeLabels.map(l => this._labelRow(l)).join('')}
                        </div>
                    `).join('')}
                </div>
            ` : ''}

            <div class="label-section">
                <h3>Labels</h3>
                ${unscopedLabels.map(l => this._labelRow(l)).join('')}
                ${unscopedLabels.length === 0 ? '<p class="text-muted">No labels.</p>' : ''}
            </div>
        `;
    },

    _labelRow(label) {
        const issueCount = AppState.issues.filter(i => i.labels.includes(label.id)).length;
        return `
            <div class="label-row" data-label-id="${label.id}">
                <div class="label-row-main">
                    ${Components.labelChip(label)}
                    <span class="label-description">${Components.escapeHtml(label.description || '')}</span>
                </div>
                <div class="label-row-meta">
                    <span class="label-issue-count">${issueCount} issues</span>
                    <button class="btn btn-sm btn-link" data-action="editLabel" data-label-id="${label.id}">Edit</button>
                    <button class="btn btn-sm btn-link btn-danger-link" data-action="deleteLabel" data-label-id="${label.id}">Delete</button>
                </div>
            </div>
        `;
    },

    // ════════════════════════════════════════════════════════
    //  NOTIFICATIONS
    // ════════════════════════════════════════════════════════
    renderNotifications() {
        const feed = AppState.notificationFeed;
        const settings = AppState.notificationSettings;
        const unread = feed.filter(n => !n.read);
        const levelOpts = [
            { value: 'global', label: 'Global' },
            { value: 'watch', label: 'Watch' },
            { value: 'participating', label: 'On mention / participating' },
            { value: 'disabled', label: 'Disabled' }
        ];

        return `
            <div class="page-header">
                <div class="page-header-top">
                    <h1>Notifications</h1>
                    ${unread.length > 0 ? `<button class="btn btn-secondary" data-action="markAllRead">Mark all as read</button>` : ''}
                </div>
            </div>

            ${Components.tabs('notifTabs', [
                { key: 'feed', label: 'Feed', count: unread.length },
                { key: 'settings', label: 'Settings' }
            ], AppState._notifTab || 'feed')}

            ${(AppState._notifTab || 'feed') === 'feed' ? `
                <div class="notification-feed">
                    ${feed.length === 0 ? Components.emptyState('No notifications', 'You\'re all caught up!') : ''}
                    ${feed.map(n => {
                        const actor = AppState.getUserById(n.actorId);
                        return `
                            <div class="notification-item${n.read ? '' : ' unread'}" data-notif-id="${n.id}">
                                <div class="notification-avatar">${Components.avatar(actor, 32)}</div>
                                <div class="notification-body">
                                    <div class="notification-message">${Components.escapeHtml(n.message)}</div>
                                    <div class="notification-time">${Components.timeAgo(n.createdAt)}</div>
                                </div>
                                ${!n.read ? `<button class="btn btn-sm btn-link" data-action="markRead" data-notif-id="${n.id}">Mark read</button>` : ''}
                            </div>
                        `;
                    }).join('')}
                </div>
            ` : `
                <div class="notification-settings">
                    <div class="setting-row">
                        <div class="setting-info">
                            <label class="setting-label">Notification level</label>
                            <p class="setting-desc">Choose when to receive notifications for this project.</p>
                        </div>
                        ${Components.dropdown('notifLevel', levelOpts, settings.level)}
                    </div>

                    <h3>Email Notifications</h3>
                    <div class="setting-row">
                        <div class="setting-info"><label class="setting-label">New issues</label></div>
                        ${Components.toggle('notifNewIssue', settings.email.newIssue)}
                    </div>
                    <div class="setting-row">
                        <div class="setting-info"><label class="setting-label">Reassigned issues</label></div>
                        ${Components.toggle('notifReassigned', settings.email.reassignedIssue)}
                    </div>
                    <div class="setting-row">
                        <div class="setting-info"><label class="setting-label">Closed issues</label></div>
                        ${Components.toggle('notifClosed', settings.email.closedIssue)}
                    </div>
                    <div class="setting-row">
                        <div class="setting-info"><label class="setting-label">New comments</label></div>
                        ${Components.toggle('notifComment', settings.email.newComment)}
                    </div>
                    <div class="setting-row">
                        <div class="setting-info"><label class="setting-label">Mentioned</label></div>
                        ${Components.toggle('notifMentioned', settings.email.mentioned)}
                    </div>
                    <div class="setting-row">
                        <div class="setting-info"><label class="setting-label">Milestone changes</label></div>
                        ${Components.toggle('notifMilestone', settings.email.milestoneChanged)}
                    </div>
                </div>
            `}
        `;
    }
};
