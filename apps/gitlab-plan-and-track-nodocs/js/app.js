/* ============================================================
   GitLab Plan & Track — Application Router & Event Handlers
   ============================================================ */

const App = {
    init() {
        AppState.init();
        AppState.subscribe(() => this.render());
        this.render();
        AppState.notify(); // Push initial state to server

        // SSE listener for reset
        const es = new EventSource('/api/events');
        es.onmessage = (e) => {
            if (e.data === 'reset') {
                AppState.resetToSeedData();
                this.render();
            }
        };
    },

    render() {
        const sidebar = document.getElementById('sidebarNav');
        const content = document.getElementById('contentWrapper');
        if (sidebar) sidebar.innerHTML = Views.renderSidebar();
        if (content) content.innerHTML = Views.renderContent();
        this.attachHandlers();
    },

    navigate(section, view, params) {
        AppState.currentSection = section;
        AppState.currentView = view || 'list';
        if (params) {
            if (params.issueId !== undefined) AppState.selectedIssueId = params.issueId;
            if (params.milestoneId !== undefined) AppState.selectedMilestoneId = params.milestoneId;
            if (params.epicId !== undefined) AppState.selectedEpicId = params.epicId;
            if (params.iterationId !== undefined) AppState.selectedIterationId = params.iterationId;
            if (params.boardId !== undefined) AppState.selectedBoardId = params.boardId;
        }
        AppState.issuesPage = 1;
        AppState.selectedIssueIds = [];
        this.render();
        // Scroll to top
        const main = document.querySelector('.main-content');
        if (main) main.scrollTop = 0;
    },

    attachHandlers() {
        const content = document.getElementById('contentWrapper');
        if (!content) return;

        content.onclick = (e) => this.handleClick(e);
        content.onchange = (e) => this.handleChange(e);
        content.oninput = (e) => this.handleInput(e);

        // Handle dropdown-change custom events
        content.addEventListener('dropdown-change', (e) => this.handleDropdownChange(e));

        // Drag and drop for boards
        this._setupBoardDragDrop();
    },

    // ── Click Handler ──────────────────────────────────────
    handleClick(e) {
        const action = e.target.closest('[data-action]');
        if (!action) return;

        const act = action.dataset.action;

        switch (act) {
            // Navigation
            case 'navigate': {
                const section = action.dataset.section;
                const params = action.dataset.params ? JSON.parse(action.dataset.params) : {};
                this.navigate(section, 'list', params);
                break;
            }

            // Issue actions
            case 'createIssue':
                this.navigate('issues', 'create');
                break;

            case 'viewIssue': {
                const issueId = parseInt(action.dataset.issueId);
                this.navigate('issues', 'detail', { issueId });
                break;
            }

            case 'closeIssue': {
                const id = parseInt(action.dataset.issueId);
                AppState.closeIssue(id);
                this.render();
                Components.showToast('Issue closed', 'success');
                break;
            }

            case 'reopenIssue': {
                const id = parseInt(action.dataset.issueId);
                AppState.reopenIssue(id);
                this.render();
                Components.showToast('Issue reopened', 'success');
                break;
            }

            case 'saveIssueTitle': {
                const titleEl = document.getElementById('issueTitle');
                if (titleEl) {
                    const newTitle = titleEl.textContent.trim();
                    if (newTitle) {
                        AppState.updateIssue(AppState.selectedIssueId, { title: newTitle });
                        Components.showToast('Title updated', 'success');
                    }
                }
                break;
            }

            case 'editDescription': {
                const content = document.getElementById('descriptionContent');
                const editor = document.getElementById('descriptionEditor');
                const btn = document.getElementById('editDescBtn');
                if (content) content.style.display = 'none';
                if (editor) editor.style.display = 'block';
                if (btn) btn.style.display = 'none';
                break;
            }

            case 'saveDescription': {
                const textarea = document.getElementById('descriptionTextarea');
                if (textarea) {
                    AppState.updateIssue(AppState.selectedIssueId, { description: textarea.value });
                    this.render();
                    Components.showToast('Description updated', 'success');
                }
                break;
            }

            case 'cancelEditDescription': {
                this.render();
                break;
            }

            case 'submitComment': {
                const issueId = parseInt(action.dataset.issueId);
                const textarea = document.getElementById('commentTextarea');
                if (textarea && textarea.value.trim()) {
                    const text = textarea.value.trim();
                    // Process quick actions
                    const remaining = AppState.processQuickActions(issueId, text);
                    // Add remaining text as comment
                    if (remaining) {
                        AppState.addComment(issueId, remaining);
                    }
                    this.render();
                    Components.showToast('Comment added', 'success');
                }
                break;
            }

            case 'submitNewIssue': {
                this._handleCreateIssue();
                break;
            }

            case 'cancelCreate':
                this.navigate('issues', 'list');
                break;

            // Bulk actions
            case 'toggleIssueSelect': {
                const issueId = parseInt(action.dataset.issueId);
                const idx = AppState.selectedIssueIds.indexOf(issueId);
                if (idx >= 0) AppState.selectedIssueIds.splice(idx, 1);
                else AppState.selectedIssueIds.push(issueId);
                this.render();
                break;
            }

            case 'clearSelection':
                AppState.selectedIssueIds = [];
                this.render();
                break;

            case 'bulkClose':
                AppState.bulkUpdateIssues(AppState.selectedIssueIds, { state: 'closed' });
                this.render();
                Components.showToast(`${AppState.selectedIssueIds.length} issues closed`, 'success');
                break;

            case 'bulkReopen':
                AppState.bulkUpdateIssues(AppState.selectedIssueIds, { state: 'opened' });
                this.render();
                Components.showToast('Issues reopened', 'success');
                break;

            // Filter status
            case 'filterStatus': {
                AppState.issueFilters.status = action.dataset.status;
                AppState.issuesPage = 1;
                this.render();
                break;
            }

            // Related issues
            case 'removeRelatedIssue': {
                const issueId = parseInt(action.dataset.issueId);
                const relatedId = parseInt(action.dataset.relatedId);
                AppState.removeRelatedIssue(issueId, relatedId);
                this.render();
                break;
            }

            case 'addRelatedIssue': {
                const issueId = parseInt(action.dataset.issueId);
                this._showAddRelatedIssueModal(issueId);
                break;
            }

            // Time tracking
            case 'setEstimate': {
                this._showTimeEstimateModal(parseInt(action.dataset.issueId));
                break;
            }

            case 'logTime': {
                this._showLogTimeModal(parseInt(action.dataset.issueId));
                break;
            }

            // Milestones
            case 'viewMilestone': {
                const id = parseInt(action.dataset.milestoneId);
                this.navigate('milestones', 'detail', { milestoneId: id });
                break;
            }

            case 'createMilestone':
                this._showCreateMilestoneModal();
                break;

            case 'editMilestone': {
                const id = parseInt(action.dataset.milestoneId);
                this._showEditMilestoneModal(id);
                break;
            }

            case 'closeMilestone': {
                const id = parseInt(action.dataset.milestoneId);
                AppState.closeMilestone(id);
                this.render();
                Components.showToast('Milestone closed', 'success');
                break;
            }

            case 'activateMilestone': {
                const id = parseInt(action.dataset.milestoneId);
                AppState.activateMilestone(id);
                this.render();
                Components.showToast('Milestone reopened', 'success');
                break;
            }

            case 'deleteMilestone': {
                const id = parseInt(action.dataset.milestoneId);
                const ms = AppState.getMilestoneById(id);
                Components.confirm('Delete Milestone', `Are you sure you want to delete "${ms ? ms.title : ''}"? Issues will be unassigned from this milestone.`, () => {
                    AppState.deleteMilestone(id);
                    this.render();
                    Components.showToast('Milestone deleted', 'success');
                });
                break;
            }

            // Iterations
            case 'viewIteration': {
                const id = parseInt(action.dataset.iterationId);
                this.navigate('iterations', 'detail', { iterationId: id });
                break;
            }

            case 'createIteration':
                this._showCreateIterationModal();
                break;

            // Epics
            case 'viewEpic': {
                const id = parseInt(action.dataset.epicId);
                this.navigate('epics', 'detail', { epicId: id });
                break;
            }

            case 'createEpic':
                this._showCreateEpicModal();
                break;

            case 'closeEpic': {
                const id = parseInt(action.dataset.epicId);
                AppState.closeEpic(id);
                this.render();
                Components.showToast('Epic closed', 'success');
                break;
            }

            case 'reopenEpic': {
                const id = parseInt(action.dataset.epicId);
                AppState.reopenEpic(id);
                this.render();
                Components.showToast('Epic reopened', 'success');
                break;
            }

            // Labels
            case 'createLabel':
                this._showCreateLabelModal();
                break;

            case 'editLabel': {
                const id = parseInt(action.dataset.labelId);
                this._showEditLabelModal(id);
                break;
            }

            case 'deleteLabel': {
                const id = parseInt(action.dataset.labelId);
                const label = AppState.getLabelById(id);
                Components.confirm('Delete Label', `Are you sure you want to delete "${label ? label.name : ''}"? It will be removed from all issues.`, () => {
                    AppState.deleteLabel(id);
                    this.render();
                    Components.showToast('Label deleted', 'success');
                });
                break;
            }

            // Board actions
            case 'addBoardList': {
                const boardId = parseInt(action.dataset.boardId);
                this._showAddBoardListModal(boardId);
                break;
            }

            case 'removeBoardList': {
                const boardId = parseInt(action.dataset.boardId);
                const listId = parseInt(action.dataset.listId);
                AppState.removeBoardList(boardId, listId);
                this.render();
                break;
            }

            case 'createIssueFromBoard': {
                this.navigate('issues', 'create');
                break;
            }

            // Notifications
            case 'markRead': {
                const notifId = parseInt(action.dataset.notifId);
                AppState.markNotificationRead(notifId);
                this.render();
                break;
            }

            case 'markAllRead':
                AppState.markAllNotificationsRead();
                this.render();
                Components.showToast('All notifications marked as read', 'success');
                break;

            // Modal actions
            case 'closeModal':
                Components.closeModal();
                break;

            case 'confirmAction':
                if (window._pendingConfirmAction) {
                    window._pendingConfirmAction();
                    window._pendingConfirmAction = null;
                }
                Components.closeModal();
                break;

            case 'submitModal':
                this._handleModalSubmit();
                break;

            // Pagination
            default:
                break;
        }

        // Pagination click
        const pageBtn = e.target.closest('[data-page]');
        if (pageBtn && !pageBtn.disabled) {
            AppState.issuesPage = parseInt(pageBtn.dataset.page);
            this.render();
        }

        // Tab click
        const tabBtn = e.target.closest('[data-tab]');
        if (tabBtn) {
            const tabGroup = tabBtn.dataset.tabGroup;
            const tabKey = tabBtn.dataset.tab;
            if (tabGroup === 'milestoneTabs') { AppState._milestoneTab = tabKey; this.render(); }
            else if (tabGroup === 'milestoneIssueTabs') { AppState._milestoneIssueTab = tabKey; this.render(); }
            else if (tabGroup === 'iterationIssueTabs') { AppState._iterationIssueTab = tabKey; this.render(); }
            else if (tabGroup === 'epicTabs') { AppState._epicTab = tabKey; this.render(); }
            else if (tabGroup === 'notifTabs') { AppState._notifTab = tabKey; this.render(); }
        }

        // Select all issues checkbox
        if (e.target.id === 'selectAllIssues') {
            const { issues } = AppState.getPaginatedIssues();
            if (e.target.checked) {
                AppState.selectedIssueIds = issues.map(i => i.id);
            } else {
                AppState.selectedIssueIds = [];
            }
            this.render();
        }
    },

    // ── Change Handler ─────────────────────────────────────
    handleChange(e) {
        const target = e.target;

        // Issue sidebar toggles
        if (target.id === 'issueConfidential') {
            AppState.updateIssue(AppState.selectedIssueId, { confidential: target.checked });
            this.render();
        }
        if (target.id === 'issueSubscribed') {
            const issue = AppState.getIssueById(AppState.selectedIssueId);
            if (issue) { issue.subscribed = target.checked; AppState.notify(); this.render(); }
        }

        // Weight
        if (target.id === 'issueWeight') {
            const val = target.value === '' ? null : parseInt(target.value);
            AppState.updateIssue(AppState.selectedIssueId, { weight: val });
        }

        // Due date
        if (target.id === 'issueDueDate') {
            const val = target.value.match(/^\d{4}-\d{2}-\d{2}$/) ? target.value : null;
            AppState.updateIssue(AppState.selectedIssueId, { dueDate: val });
        }

        // Notification settings toggles
        if (target.id === 'notifNewIssue') {
            AppState.notificationSettings.email.newIssue = target.checked;
            AppState.notify();
        }
        if (target.id === 'notifReassigned') {
            AppState.notificationSettings.email.reassignedIssue = target.checked;
            AppState.notify();
        }
        if (target.id === 'notifClosed') {
            AppState.notificationSettings.email.closedIssue = target.checked;
            AppState.notify();
        }
        if (target.id === 'notifComment') {
            AppState.notificationSettings.email.newComment = target.checked;
            AppState.notify();
        }
        if (target.id === 'notifMentioned') {
            AppState.notificationSettings.email.mentioned = target.checked;
            AppState.notify();
        }
        if (target.id === 'notifMilestone') {
            AppState.notificationSettings.email.milestoneChanged = target.checked;
            AppState.notify();
        }
    },

    // ── Input Handler ──────────────────────────────────────
    handleInput(e) {
        const target = e.target;

        // Issue search
        if (target.id === 'issueSearch') {
            AppState.issueFilters.search = target.value;
            AppState.issuesPage = 1;
            this.render();
            // Re-focus and restore cursor
            const newInput = document.getElementById('issueSearch');
            if (newInput) {
                newInput.focus();
                newInput.setSelectionRange(target.value.length, target.value.length);
            }
        }

        // Title editing
        if (target.id === 'issueTitle') {
            const saveBtn = document.getElementById('saveTitleBtn');
            if (saveBtn) saveBtn.style.display = 'inline-block';
        }
    },

    // ── Dropdown Change Handler ────────────────────────────
    handleDropdownChange(e) {
        const { id, value, values } = e.detail;

        // Issue list filters
        if (id === 'filterAuthor') {
            AppState.issueFilters.authorId = value ? parseInt(value) : null;
            AppState.issuesPage = 1;
            this.render();
        }
        if (id === 'filterAssignee') {
            AppState.issueFilters.assigneeId = value ? parseInt(value) : null;
            AppState.issuesPage = 1;
            this.render();
        }
        if (id === 'filterLabels') {
            AppState.issueFilters.labelIds = (values || []).map(v => parseInt(v));
            AppState.issuesPage = 1;
            this.render();
        }
        if (id === 'filterMilestone') {
            AppState.issueFilters.milestoneId = value ? parseInt(value) : null;
            AppState.issuesPage = 1;
            this.render();
        }
        if (id === 'filterType') {
            AppState.issueFilters.type = value || null;
            AppState.issuesPage = 1;
            this.render();
        }
        if (id === 'sortIssues') {
            AppState.issueFilters.sort = value;
            this.render();
        }

        // Bulk action dropdowns
        if (id === 'bulkAssignee' && value) {
            AppState.bulkUpdateIssues(AppState.selectedIssueIds, { assigneeId: parseInt(value) });
            this.render();
            Components.showToast('Assignee updated', 'success');
        }
        if (id === 'bulkLabel' && value) {
            AppState.bulkUpdateIssues(AppState.selectedIssueIds, { labelId: parseInt(value) });
            this.render();
            Components.showToast('Label added', 'success');
        }
        if (id === 'bulkMilestone') {
            AppState.bulkUpdateIssues(AppState.selectedIssueIds, { milestoneId: value ? parseInt(value) : null });
            this.render();
            Components.showToast('Milestone updated', 'success');
        }

        // Issue detail sidebar
        if (id === 'issueAssignees') {
            AppState.updateIssue(AppState.selectedIssueId, { assignees: (values || []).map(v => parseInt(v)) });
            this.render();
        }
        if (id === 'issueLabels') {
            AppState.updateIssue(AppState.selectedIssueId, { labels: (values || []).map(v => parseInt(v)) });
            this.render();
        }
        if (id === 'issueMilestone') {
            AppState.updateIssue(AppState.selectedIssueId, { milestoneId: value ? parseInt(value) : null });
            this.render();
        }
        if (id === 'issueIteration') {
            AppState.updateIssue(AppState.selectedIssueId, { iterationId: value ? parseInt(value) : null });
            this.render();
        }
        if (id === 'issueEpic') {
            AppState.updateIssue(AppState.selectedIssueId, { epicId: value ? parseInt(value) : null });
            this.render();
        }

        // Board selector
        if (id === 'boardSelect') {
            AppState.selectedBoardId = parseInt(value);
            this.render();
        }

        // Notification level
        if (id === 'notifLevel') {
            AppState.notificationSettings.level = value;
            AppState.notify();
        }

        // Template selection
        if (id === 'newIssueTemplate' && value) {
            const template = AppState.issueTemplates.find(t => t.id === parseInt(value));
            if (template) {
                const textarea = document.getElementById('newIssueDescription');
                if (textarea) textarea.value = template.content;
            }
        }
    },

    // ── Issue Creation ─────────────────────────────────────
    _handleCreateIssue() {
        const titleInput = document.getElementById('newIssueTitle');
        const descInput = document.getElementById('newIssueDescription');

        if (!titleInput || !titleInput.value.trim()) {
            Components.showToast('Title is required', 'error');
            return;
        }

        const typeDd = document.getElementById('newIssueType');
        const msDd = document.getElementById('newIssueMilestone');
        const iterDd = document.getElementById('newIssueIteration');
        const epicDd = document.getElementById('newIssueEpic');
        const weightInput = document.getElementById('newIssueWeight');
        const dueDateInput = document.getElementById('newIssueDueDate');
        const confCheck = document.getElementById('newIssueConfidentialCheck');

        // Get multi-select values
        const assigneeDd = document.getElementById('newIssueAssignees');
        const labelDd = document.getElementById('newIssueLabels');

        const assignees = assigneeDd ? Array.from(assigneeDd.querySelectorAll('.dropdown-item.selected')).map(i => parseInt(i.dataset.value)) : [];
        const labels = labelDd ? Array.from(labelDd.querySelectorAll('.dropdown-item.selected')).map(i => parseInt(i.dataset.value)) : [];

        const issue = AppState.createIssue({
            title: titleInput.value.trim(),
            description: descInput ? descInput.value : '',
            type: typeDd ? typeDd.dataset.value || 'issue' : 'issue',
            assignees: assignees,
            labels: labels,
            milestoneId: msDd && msDd.dataset.value ? parseInt(msDd.dataset.value) : null,
            iterationId: iterDd && iterDd.dataset.value ? parseInt(iterDd.dataset.value) : null,
            epicId: epicDd && epicDd.dataset.value ? parseInt(epicDd.dataset.value) : null,
            weight: weightInput && weightInput.value ? parseInt(weightInput.value) : null,
            dueDate: dueDateInput && dueDateInput.value.match(/^\d{4}-\d{2}-\d{2}$/) ? dueDateInput.value : null,
            confidential: confCheck ? confCheck.checked : false
        });

        Components.showToast(`Issue #${issue.iid} created`, 'success');
        this.navigate('issues', 'detail', { issueId: issue.id });
    },

    // ── Modal Creators ─────────────────────────────────────
    _showCreateMilestoneModal() {
        AppState.activeModal = 'createMilestone';
        Components.showModal('New Milestone', `
            ${Components.formField('modalMsTitle', 'Title', Components.textInput('modalMsTitle', '', { placeholder: 'Milestone title' }), { required: true })}
            ${Components.formField('modalMsDesc', 'Description', Components.textarea('modalMsDesc', '', { placeholder: 'Description', rows: 3 }))}
            ${Components.formField('modalMsStart', 'Start date', Components.dateInput('modalMsStart', ''))}
            ${Components.formField('modalMsDue', 'Due date', Components.dateInput('modalMsDue', ''))}
        `, `
            <button class="btn btn-secondary" data-action="closeModal">Cancel</button>
            <button class="btn btn-primary" data-action="submitModal">Create milestone</button>
        `);
    },

    _showEditMilestoneModal(id) {
        const ms = AppState.getMilestoneById(id);
        if (!ms) return;
        AppState.activeModal = 'editMilestone';
        AppState.modalData = { milestoneId: id };
        Components.showModal('Edit Milestone', `
            ${Components.formField('modalMsTitle', 'Title', Components.textInput('modalMsTitle', ms.title, { placeholder: 'Milestone title' }), { required: true })}
            ${Components.formField('modalMsDesc', 'Description', Components.textarea('modalMsDesc', ms.description || '', { placeholder: 'Description', rows: 3 }))}
            ${Components.formField('modalMsStart', 'Start date', Components.dateInput('modalMsStart', ms.startDate || ''))}
            ${Components.formField('modalMsDue', 'Due date', Components.dateInput('modalMsDue', ms.dueDate || ''))}
        `, `
            <button class="btn btn-secondary" data-action="closeModal">Cancel</button>
            <button class="btn btn-primary" data-action="submitModal">Save</button>
        `);
    },

    _showCreateIterationModal() {
        AppState.activeModal = 'createIteration';
        const cadenceOpts = AppState.iterationCadences.map(c => ({ value: String(c.id), label: c.title }));
        Components.showModal('New Iteration', `
            ${Components.formField('modalIterCadence', 'Cadence', Components.dropdown('modalIterCadence', cadenceOpts, cadenceOpts[0]?.value || ''))}
            ${Components.formField('modalIterTitle', 'Title', Components.textInput('modalIterTitle', '', { placeholder: 'Iteration title' }), { required: true })}
            ${Components.formField('modalIterStart', 'Start date', Components.dateInput('modalIterStart', ''), { required: true })}
            ${Components.formField('modalIterEnd', 'End date', Components.dateInput('modalIterEnd', ''), { required: true })}
        `, `
            <button class="btn btn-secondary" data-action="closeModal">Cancel</button>
            <button class="btn btn-primary" data-action="submitModal">Create iteration</button>
        `);
    },

    _showCreateEpicModal() {
        AppState.activeModal = 'createEpic';
        const labelOpts = AppState.labels.map(l => ({ value: String(l.id), label: l.name, color: l.color }));
        const parentOpts = [{ value: '', label: 'No parent' }, ...AppState.epics.filter(e => e.state === 'opened').map(e => ({ value: String(e.id), label: e.title }))];
        Components.showModal('New Epic', `
            ${Components.formField('modalEpicTitle', 'Title', Components.textInput('modalEpicTitle', '', { placeholder: 'Epic title' }), { required: true })}
            ${Components.formField('modalEpicDesc', 'Description', Components.textarea('modalEpicDesc', '', { placeholder: 'Description', rows: 4 }))}
            ${Components.formField('modalEpicLabels', 'Labels', Components.multiSelectDropdown('modalEpicLabels', labelOpts, [], { placeholder: 'Select labels', searchable: true }))}
            ${Components.formField('modalEpicParent', 'Parent Epic', Components.dropdown('modalEpicParent', parentOpts, ''))}
            <div class="form-row">
                ${Components.formField('modalEpicStart', 'Start date', Components.dateInput('modalEpicStart', ''))}
                ${Components.formField('modalEpicDue', 'Due date', Components.dateInput('modalEpicDue', ''))}
            </div>
            ${Components.formField('modalEpicConf', 'Confidential', Components.checkbox('modalEpicConfCheck', 'This epic is confidential', false))}
        `, `
            <button class="btn btn-secondary" data-action="closeModal">Cancel</button>
            <button class="btn btn-primary" data-action="submitModal">Create epic</button>
        `);
    },

    _showCreateLabelModal() {
        AppState.activeModal = 'createLabel';
        Components.showModal('New Label', `
            ${Components.formField('modalLabelName', 'Name', Components.textInput('modalLabelName', '', { placeholder: 'Label name (e.g., bug or priority::high)' }), { required: true })}
            ${Components.formField('modalLabelDesc', 'Description', Components.textInput('modalLabelDesc', '', { placeholder: 'Description' }))}
            ${Components.formField('modalLabelColor', 'Color', Components.colorPicker('modalLabelColor', '#428bca'))}
        `, `
            <button class="btn btn-secondary" data-action="closeModal">Cancel</button>
            <button class="btn btn-primary" data-action="submitModal">Create label</button>
        `);
    },

    _showEditLabelModal(id) {
        const label = AppState.getLabelById(id);
        if (!label) return;
        AppState.activeModal = 'editLabel';
        AppState.modalData = { labelId: id };
        Components.showModal('Edit Label', `
            ${Components.formField('modalLabelName', 'Name', Components.textInput('modalLabelName', label.name, { placeholder: 'Label name' }), { required: true })}
            ${Components.formField('modalLabelDesc', 'Description', Components.textInput('modalLabelDesc', label.description || '', { placeholder: 'Description' }))}
            ${Components.formField('modalLabelColor', 'Color', Components.colorPicker('modalLabelColor', label.color))}
        `, `
            <button class="btn btn-secondary" data-action="closeModal">Cancel</button>
            <button class="btn btn-primary" data-action="submitModal">Save</button>
        `);
    },

    _showAddBoardListModal(boardId) {
        AppState.activeModal = 'addBoardList';
        AppState.modalData = { boardId };
        const board = AppState.getBoardById(boardId);
        const existingLabelIds = board ? board.lists.filter(l => l.labelId).map(l => l.labelId) : [];
        const labelOpts = AppState.labels.filter(l => !existingLabelIds.includes(l.id)).map(l => ({ value: String(l.id), label: l.name, color: l.color }));
        Components.showModal('Add List', `
            <p>Select a label to create a new board list:</p>
            ${Components.dropdown('modalBoardLabel', labelOpts, '', { searchable: true })}
        `, `
            <button class="btn btn-secondary" data-action="closeModal">Cancel</button>
            <button class="btn btn-primary" data-action="submitModal">Add list</button>
        `);
    },

    _showAddRelatedIssueModal(issueId) {
        AppState.activeModal = 'addRelatedIssue';
        AppState.modalData = { issueId };
        const currentIssue = AppState.getIssueById(issueId);
        const existingIds = [issueId, ...(currentIssue ? currentIssue.relatedIssues.map(r => r.issueId) : [])];
        const issueOpts = AppState.issues.filter(i => !existingIds.includes(i.id)).map(i => ({ value: String(i.id), label: `#${i.iid} ${i.title}` }));
        const linkTypeOpts = [
            { value: 'relates_to', label: 'Related to' },
            { value: 'blocks', label: 'Blocks' },
            { value: 'is_blocked_by', label: 'Is blocked by' }
        ];
        Components.showModal('Add Related Issue', `
            ${Components.formField('modalRelatedIssue', 'Issue', Components.dropdown('modalRelatedIssue', issueOpts, '', { searchable: true }))}
            ${Components.formField('modalLinkType', 'Relationship', Components.dropdown('modalLinkType', linkTypeOpts, 'relates_to'))}
        `, `
            <button class="btn btn-secondary" data-action="closeModal">Cancel</button>
            <button class="btn btn-primary" data-action="submitModal">Add</button>
        `);
    },

    _showTimeEstimateModal(issueId) {
        AppState.activeModal = 'setEstimate';
        AppState.modalData = { issueId };
        const issue = AppState.getIssueById(issueId);
        const currentHours = issue && issue.timeEstimate ? Math.floor(issue.timeEstimate / 3600) : '';
        const currentMins = issue && issue.timeEstimate ? Math.floor((issue.timeEstimate % 3600) / 60) : '';
        Components.showModal('Set Time Estimate', `
            <div class="form-row">
                ${Components.formField('modalEstHours', 'Hours', Components.numberInput('modalEstHours', currentHours, { min: 0, placeholder: '0' }))}
                ${Components.formField('modalEstMins', 'Minutes', Components.numberInput('modalEstMins', currentMins, { min: 0, max: 59, placeholder: '0' }))}
            </div>
        `, `
            <button class="btn btn-secondary" data-action="closeModal">Cancel</button>
            <button class="btn btn-primary" data-action="submitModal">Set estimate</button>
        `);
    },

    _showLogTimeModal(issueId) {
        AppState.activeModal = 'logTime';
        AppState.modalData = { issueId };
        Components.showModal('Log Time', `
            <div class="form-row">
                ${Components.formField('modalLogHours', 'Hours', Components.numberInput('modalLogHours', '', { min: 0, placeholder: '0' }))}
                ${Components.formField('modalLogMins', 'Minutes', Components.numberInput('modalLogMins', '', { min: 0, max: 59, placeholder: '0' }))}
            </div>
        `, `
            <button class="btn btn-secondary" data-action="closeModal">Cancel</button>
            <button class="btn btn-primary" data-action="submitModal">Log time</button>
        `);
    },

    // ── Modal Submit Handler ───────────────────────────────
    _handleModalSubmit() {
        const modal = AppState.activeModal;

        switch (modal) {
            case 'createMilestone': {
                const title = document.getElementById('modalMsTitle')?.value?.trim();
                if (!title) { Components.showToast('Title is required', 'error'); return; }
                AppState.createMilestone({
                    title,
                    description: document.getElementById('modalMsDesc')?.value || '',
                    startDate: document.getElementById('modalMsStart')?.value || null,
                    dueDate: document.getElementById('modalMsDue')?.value || null
                });
                Components.closeModal();
                this.render();
                Components.showToast('Milestone created', 'success');
                break;
            }

            case 'editMilestone': {
                const title = document.getElementById('modalMsTitle')?.value?.trim();
                if (!title) { Components.showToast('Title is required', 'error'); return; }
                AppState.updateMilestone(AppState.modalData.milestoneId, {
                    title,
                    description: document.getElementById('modalMsDesc')?.value || '',
                    startDate: document.getElementById('modalMsStart')?.value || null,
                    dueDate: document.getElementById('modalMsDue')?.value || null
                });
                Components.closeModal();
                this.render();
                Components.showToast('Milestone updated', 'success');
                break;
            }

            case 'createIteration': {
                const title = document.getElementById('modalIterTitle')?.value?.trim();
                const startDate = document.getElementById('modalIterStart')?.value;
                const endDate = document.getElementById('modalIterEnd')?.value;
                const cadenceDd = document.getElementById('modalIterCadence');
                if (!title || !startDate || !endDate) {
                    Components.showToast('All fields are required', 'error');
                    return;
                }
                AppState.createIteration({
                    cadenceId: cadenceDd ? parseInt(cadenceDd.dataset.value) : 1,
                    title, startDate, endDate
                });
                Components.closeModal();
                this.render();
                Components.showToast('Iteration created', 'success');
                break;
            }

            case 'createEpic': {
                const title = document.getElementById('modalEpicTitle')?.value?.trim();
                if (!title) { Components.showToast('Title is required', 'error'); return; }
                const labelDd = document.getElementById('modalEpicLabels');
                const labels = labelDd ? Array.from(labelDd.querySelectorAll('.dropdown-item.selected')).map(i => parseInt(i.dataset.value)) : [];
                const parentDd = document.getElementById('modalEpicParent');
                AppState.createEpic({
                    title,
                    description: document.getElementById('modalEpicDesc')?.value || '',
                    labels,
                    parentEpicId: parentDd && parentDd.dataset.value ? parseInt(parentDd.dataset.value) : null,
                    startDate: document.getElementById('modalEpicStart')?.value || null,
                    dueDate: document.getElementById('modalEpicDue')?.value || null,
                    confidential: document.getElementById('modalEpicConfCheck')?.checked || false
                });
                Components.closeModal();
                this.render();
                Components.showToast('Epic created', 'success');
                break;
            }

            case 'createLabel': {
                const name = document.getElementById('modalLabelName')?.value?.trim();
                if (!name) { Components.showToast('Name is required', 'error'); return; }
                const colorInput = document.getElementById('modalLabelColor-hex');
                const color = colorInput?.value || '#428bca';
                AppState.createLabel({
                    name,
                    description: document.getElementById('modalLabelDesc')?.value || '',
                    color
                });
                Components.closeModal();
                this.render();
                Components.showToast('Label created', 'success');
                break;
            }

            case 'editLabel': {
                const name = document.getElementById('modalLabelName')?.value?.trim();
                if (!name) { Components.showToast('Name is required', 'error'); return; }
                const colorInput = document.getElementById('modalLabelColor-hex');
                const color = colorInput?.value || '#428bca';
                AppState.updateLabel(AppState.modalData.labelId, {
                    name,
                    description: document.getElementById('modalLabelDesc')?.value || '',
                    color
                });
                Components.closeModal();
                this.render();
                Components.showToast('Label updated', 'success');
                break;
            }

            case 'addBoardList': {
                const dd = document.getElementById('modalBoardLabel');
                if (!dd || !dd.dataset.value) { Components.showToast('Select a label', 'error'); return; }
                AppState.addBoardList(AppState.modalData.boardId, parseInt(dd.dataset.value));
                Components.closeModal();
                this.render();
                break;
            }

            case 'addRelatedIssue': {
                const issueDd = document.getElementById('modalRelatedIssue');
                const typeDd = document.getElementById('modalLinkType');
                if (!issueDd || !issueDd.dataset.value) { Components.showToast('Select an issue', 'error'); return; }
                AppState.addRelatedIssue(
                    AppState.modalData.issueId,
                    parseInt(issueDd.dataset.value),
                    typeDd?.dataset.value || 'relates_to'
                );
                Components.closeModal();
                this.render();
                Components.showToast('Related issue added', 'success');
                break;
            }

            case 'setEstimate': {
                const hours = parseInt(document.getElementById('modalEstHours')?.value || '0');
                const mins = parseInt(document.getElementById('modalEstMins')?.value || '0');
                const totalSeconds = hours * 3600 + mins * 60;
                AppState.setTimeEstimate(AppState.modalData.issueId, totalSeconds > 0 ? totalSeconds : null);
                Components.closeModal();
                this.render();
                Components.showToast('Estimate updated', 'success');
                break;
            }

            case 'logTime': {
                const hours = parseInt(document.getElementById('modalLogHours')?.value || '0');
                const mins = parseInt(document.getElementById('modalLogMins')?.value || '0');
                const totalSeconds = hours * 3600 + mins * 60;
                if (totalSeconds <= 0) { Components.showToast('Enter time to log', 'error'); return; }
                AppState.logTimeSpent(AppState.modalData.issueId, totalSeconds);
                Components.closeModal();
                this.render();
                Components.showToast('Time logged', 'success');
                break;
            }
        }
    },

    // ── Board Drag & Drop ──────────────────────────────────
    _setupBoardDragDrop() {
        const cards = document.querySelectorAll('.board-card');
        const listBodies = document.querySelectorAll('.board-list-body');

        cards.forEach(card => {
            card.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('text/plain', card.dataset.issueId);
                card.classList.add('dragging');
                const parentList = card.closest('.board-list');
                if (parentList) {
                    e.dataTransfer.setData('source-list-id', parentList.querySelector('.board-list-body').dataset.listId);
                }
            });
            card.addEventListener('dragend', () => {
                card.classList.remove('dragging');
                document.querySelectorAll('.board-list-body').forEach(b => b.classList.remove('drag-over'));
            });
        });

        listBodies.forEach(body => {
            body.addEventListener('dragover', (e) => {
                e.preventDefault();
                body.classList.add('drag-over');
            });
            body.addEventListener('dragleave', () => {
                body.classList.remove('drag-over');
            });
            body.addEventListener('drop', (e) => {
                e.preventDefault();
                body.classList.remove('drag-over');
                const issueId = parseInt(e.dataTransfer.getData('text/plain'));
                const sourceListId = parseInt(e.dataTransfer.getData('source-list-id'));
                const targetListId = parseInt(body.dataset.listId);
                const boardId = parseInt(body.dataset.boardId);
                if (sourceListId !== targetListId) {
                    AppState.moveIssueOnBoard(issueId, sourceListId, targetListId, boardId);
                    this.render();
                }
            });
        });
    }
};

// ── Sidebar click handler (outside content wrapper) ────────
document.addEventListener('click', function(e) {
    const navLink = e.target.closest('.sidebar-link[data-action="navigate"]');
    if (navLink) {
        App.navigate(navLink.dataset.section, 'list');
    }

    // Sidebar toggle
    if (e.target.closest('.sidebar-toggle')) {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) sidebar.classList.toggle('collapsed');
    }

    // Reset data button
    if (e.target.closest('[data-action="resetData"]')) {
        AppState.resetToSeedData();
        App.render();
        Components.showToast('Data reset to initial state', 'info');
    }
});

// ── Initialize on load ─────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => App.init());
