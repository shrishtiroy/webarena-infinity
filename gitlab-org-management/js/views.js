// ============================================================
// views.js — All view renderers
// ============================================================

const Views = {

    // ==========================
    // HOME / DASHBOARD
    // ==========================
    home() {
        Components.renderBreadcrumb([{ label: 'Home', route: '/' }]);
        const recentGroups = AppState.groups
            .filter(g => !g.archived)
            .sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt))
            .slice(0, 6);

        const recentProjects = AppState.projects
            .filter(p => !p.archived)
            .sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt))
            .slice(0, 6);

        return `
            <div class="page-header">
                <h1 data-testid="page-title">Welcome, ${Components.escapeHtml(AppState.currentUser.name.split(' ')[0])}</h1>
                <p class="page-subtitle">Manage your organization, groups, projects, and members.</p>
            </div>

            <div class="dashboard-stats" data-testid="dashboard-stats">
                <div class="stat-card" data-testid="stat-organizations" onclick="Router.navigate('/organizations')">
                    <div class="stat-number">${AppState.organizations.length}</div>
                    <div class="stat-label">Organizations</div>
                </div>
                <div class="stat-card" data-testid="stat-groups" onclick="Router.navigate('/groups')">
                    <div class="stat-number">${AppState.groups.filter(g => !g.archived).length}</div>
                    <div class="stat-label">Active Groups</div>
                </div>
                <div class="stat-card" data-testid="stat-projects" onclick="Router.navigate('/projects')">
                    <div class="stat-number">${AppState.projects.filter(p => !p.archived).length}</div>
                    <div class="stat-label">Active Projects</div>
                </div>
                <div class="stat-card" data-testid="stat-members">
                    <div class="stat-number">${AppState.users.length}</div>
                    <div class="stat-label">Users</div>
                </div>
            </div>

            <div class="dashboard-grid">
                <div class="dashboard-section">
                    <div class="section-header">
                        <h2>Recent Groups</h2>
                        <a href="#" class="link" data-route="/groups">View all</a>
                    </div>
                    <div class="card-grid">
                        ${recentGroups.map(g => `
                            <div class="card clickable" data-testid="group-card-${g.id}" onclick="Router.navigate('/groups/${g.id}')">
                                <div class="card-header-row">
                                    ${Components.groupAvatar(g, 28)}
                                    <div class="card-title">${Components.escapeHtml(g.name)}</div>
                                    ${Components.visibilityBadge(g.visibility)}
                                </div>
                                <div class="card-description">${Components.escapeHtml(g.description || '')}</div>
                                <div class="card-meta">
                                    <span>${Components.escapeHtml(g.fullPath)}</span>
                                    <span>Updated ${Components.timeAgo(g.updatedAt)}</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                <div class="dashboard-section">
                    <div class="section-header">
                        <h2>Recent Projects</h2>
                        <a href="#" class="link" data-route="/projects">View all</a>
                    </div>
                    <div class="card-grid">
                        ${recentProjects.map(p => `
                            <div class="card clickable" data-testid="project-card-${p.id}" onclick="Router.navigate('/projects/${p.id}')">
                                <div class="card-header-row">
                                    <div class="card-title">${Components.escapeHtml(p.name)}</div>
                                    ${Components.visibilityBadge(p.visibility)}
                                </div>
                                <div class="card-description">${Components.escapeHtml(p.description || '')}</div>
                                <div class="card-meta">
                                    <span>${Components.escapeHtml(p.fullPath)}</span>
                                    <span class="project-stars">★ ${p.stars}</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    },

    // ==========================
    // ORGANIZATIONS
    // ==========================
    organizations() {
        Components.renderBreadcrumb([
            { label: 'Home', route: '/' },
            { label: 'Organizations', route: '/organizations' }
        ]);

        return `
            <div class="page-header">
                <div class="page-header-row">
                    <h1 data-testid="page-title">Organizations</h1>
                    <button class="btn btn-primary" id="createOrgBtn" data-testid="create-org-btn">New organization</button>
                </div>
                <p class="page-subtitle">Organizations are the top-level container for groups and projects.</p>
            </div>
            ${Components.infoBox('Organizations are currently in development. They serve as the top-level container above namespaces and groups.')}
            <div class="org-list" data-testid="org-list">
                ${AppState.organizations.map(org => {
                    const topGroups = AppState.getTopLevelGroups(org.id);
                    const owner = AppState.getUserById(org.ownerId);
                    return `
                        <div class="list-item" data-testid="org-item-${org.id}">
                            <div class="list-item-left">
                                ${Components.groupAvatar(org, 40)}
                                <div class="list-item-info">
                                    <div class="list-item-title clickable" onclick="Router.navigate('/organizations/${org.id}')">${Components.escapeHtml(org.name)}</div>
                                    <div class="list-item-meta">${Components.escapeHtml(org.path)} · ${topGroups.length} top-level groups · Created ${Components.formatDate(org.createdAt)}</div>
                                    <div class="list-item-description">${Components.escapeHtml(org.description)}</div>
                                </div>
                            </div>
                            <div class="list-item-right">
                                ${Components.visibilityBadge(org.visibility)}
                                <span class="text-muted">Owner: ${owner ? Components.escapeHtml(owner.name) : 'Unknown'}</span>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    },

    organizationDetail(orgId) {
        const org = AppState.getOrgById(parseInt(orgId));
        if (!org) return Views._notFound('Organization not found');

        Components.renderBreadcrumb([
            { label: 'Home', route: '/' },
            { label: 'Organizations', route: '/organizations' },
            { label: org.name, route: `/organizations/${org.id}` }
        ]);

        const topGroups = AppState.getTopLevelGroups(org.id);

        return `
            <div class="page-header">
                <div class="page-header-row">
                    <div class="page-header-title-row">
                        ${Components.groupAvatar(org, 48)}
                        <div>
                            <h1 data-testid="page-title">${Components.escapeHtml(org.name)}</h1>
                            <p class="page-subtitle">${Components.escapeHtml(org.description)}</p>
                        </div>
                    </div>
                </div>
            </div>
            <div class="detail-meta">
                ${Components.visibilityBadge(org.visibility)}
                <span class="text-muted">Path: ${Components.escapeHtml(org.path)}</span>
                <span class="text-muted">Created: ${Components.formatDate(org.createdAt)}</span>
            </div>
            <div class="section-header" style="margin-top:24px">
                <h2>Top-level Groups (${topGroups.length})</h2>
                <button class="btn btn-primary btn-sm" onclick="Views._showCreateGroupModal(null, ${org.id})" data-testid="create-group-btn">New group</button>
            </div>
            <div class="group-list" data-testid="group-list">
                ${topGroups.length === 0 ? Components.emptyState('No groups yet', 'Create a group to get started.') : ''}
                ${topGroups.map(g => Views._groupListItem(g)).join('')}
            </div>
        `;
    },

    // ==========================
    // GROUPS
    // ==========================
    groups() {
        Components.renderBreadcrumb([
            { label: 'Home', route: '/' },
            { label: 'Groups', route: '/groups' }
        ]);

        const allGroups = AppState.groups.filter(g => !g.archived);
        const topLevel = allGroups.filter(g => g.parentId === null);

        return `
            <div class="page-header">
                <div class="page-header-row">
                    <h1 data-testid="page-title">Groups</h1>
                    <button class="btn btn-primary" id="createGroupBtn" data-testid="create-group-btn">New group</button>
                </div>
                <p class="page-subtitle">Groups organize related projects and manage permissions for teams.</p>
            </div>
            <div class="list-controls">
                ${Components.searchInput('groupSearch', '', 'Search groups...')}
                <div class="list-controls-right">
                    ${Components.dropdown('groupVisFilter', [
                        { value: 'all', label: 'All visibilities' },
                        { value: 'public', label: 'Public' },
                        { value: 'internal', label: 'Internal' },
                        { value: 'private', label: 'Private' }
                    ], 'all', { placeholder: 'Visibility' })}
                </div>
            </div>
            <div class="group-tree" id="groupTree" data-testid="group-tree">
                ${topLevel.map(g => Views._groupTreeItem(g, 0)).join('')}
            </div>
            ${AppState.groups.filter(g => g.archived).length > 0 ? `
                <details class="archived-section" data-testid="archived-groups">
                    <summary>Archived groups (${AppState.groups.filter(g => g.archived).length})</summary>
                    <div class="group-list">
                        ${AppState.groups.filter(g => g.archived).map(g => Views._groupListItem(g)).join('')}
                    </div>
                </details>
            ` : ''}
        `;
    },

    _groupTreeItem(group, depth) {
        const children = AppState.getChildGroups(group.id).filter(g => !g.archived);
        const projects = AppState.getProjectsForGroup(group.id);
        const directMembers = AppState.getDirectGroupMembers(group.id);

        return `
            <div class="tree-item" style="margin-left:${depth * 24}px" data-testid="group-tree-item-${group.id}">
                <div class="tree-item-row clickable" onclick="Router.navigate('/groups/${group.id}')">
                    ${children.length > 0 ? `<span class="tree-toggle" onclick="event.stopPropagation(); this.closest('.tree-item').classList.toggle('collapsed')">▾</span>` : '<span class="tree-toggle-spacer"></span>'}
                    ${Components.groupAvatar(group, 24)}
                    <div class="tree-item-info">
                        <span class="tree-item-name">${Components.escapeHtml(group.name)}</span>
                        ${Components.visibilityBadge(group.visibility)}
                    </div>
                    <div class="tree-item-meta">
                        <span title="Subgroups">${children.length} subgroups</span>
                        <span title="Projects">${projects.length} projects</span>
                        <span title="Direct members">${directMembers.length} members</span>
                    </div>
                </div>
                ${children.length > 0 ? `<div class="tree-children">${children.map(c => Views._groupTreeItem(c, depth + 1)).join('')}</div>` : ''}
            </div>
        `;
    },

    _groupListItem(group) {
        return `
            <div class="list-item" data-testid="group-item-${group.id}">
                <div class="list-item-left">
                    ${Components.groupAvatar(group, 36)}
                    <div class="list-item-info">
                        <div class="list-item-title clickable" onclick="Router.navigate('/groups/${group.id}')">${Components.escapeHtml(group.name)}</div>
                        <div class="list-item-meta">${Components.escapeHtml(group.fullPath)}</div>
                    </div>
                </div>
                <div class="list-item-right">
                    ${group.archived ? Components.badge('Archived', 'muted') : ''}
                    ${Components.visibilityBadge(group.visibility)}
                </div>
            </div>
        `;
    },

    groupDetail(groupId) {
        const group = AppState.getGroupById(parseInt(groupId));
        if (!group) return Views._notFound('Group not found');

        const ancestors = AppState.getGroupAncestors(group.id);
        const org = AppState.getOrgById(group.organizationId);
        const bcItems = [{ label: 'Home', route: '/' }, { label: 'Groups', route: '/groups' }];
        if (org) bcItems.push({ label: org.name, route: `/organizations/${org.id}` });
        ancestors.forEach(a => bcItems.push({ label: a.name, route: `/groups/${a.id}` }));
        bcItems.push({ label: group.name, route: `/groups/${group.id}` });
        Components.renderBreadcrumb(bcItems);

        const children = AppState.getChildGroups(group.id).filter(g => !g.archived);
        const projects = AppState.getProjectsForGroup(group.id);
        const directMembers = AppState.getDirectGroupMembers(group.id);
        const allMembers = AppState.getAllGroupMembers(group.id);
        const userRole = AppState.getCurrentUserGroupRole(group.id);
        const isOwner = userRole && userRole.level >= ROLES.OWNER.level;
        const isMaintainer = userRole && userRole.level >= ROLES.MAINTAINER.level;
        const shares = AppState.groupShares.filter(s => s.targetGroupId === group.id);

        const activeTab = AppState.routeParams.tab || 'overview';

        let tabContent = '';
        if (activeTab === 'overview') {
            tabContent = Views._groupOverview(group, children, projects);
        } else if (activeTab === 'members') {
            tabContent = Views._groupMembers(group, allMembers, isOwner, isMaintainer);
        } else if (activeTab === 'settings') {
            tabContent = Views._groupSettings(group, isOwner, isMaintainer);
        } else if (activeTab === 'sharing') {
            tabContent = Views._groupSharing(group, shares, isOwner);
        }

        return `
            <div class="page-header">
                <div class="page-header-row">
                    <div class="page-header-title-row">
                        ${Components.groupAvatar(group, 48)}
                        <div>
                            <h1 data-testid="page-title">${Components.escapeHtml(group.name)}</h1>
                            <p class="page-subtitle">${Components.escapeHtml(group.description)}</p>
                        </div>
                    </div>
                    <div class="page-actions">
                        ${group.archived ? Components.badge('Archived', 'muted') : ''}
                        ${isOwner && !group.archived ? `<button class="btn btn-danger-outline btn-sm" data-testid="delete-group-btn" onclick="Views._confirmDeleteGroup(${group.id})">Delete group</button>` : ''}
                    </div>
                </div>
            </div>
            <div class="detail-meta">
                ${Components.visibilityBadge(group.visibility)}
                ${userRole ? Components.roleBadge(userRole) : ''}
                <span class="text-muted">Path: ${Components.escapeHtml(group.fullPath)}</span>
                <span class="text-muted">Created: ${Components.formatDate(group.createdAt)}</span>
                ${group.requireTwoFactor ? Components.badge('2FA Required', 'warning') : ''}
                ${group.userCap ? `<span class="text-muted">User cap: ${group.userCap}</span>` : ''}
            </div>

            ${Components.tabs('groupTabs', [
                { id: 'overview', label: 'Overview', count: undefined },
                { id: 'members', label: 'Members', count: allMembers.length },
                { id: 'sharing', label: 'Sharing', count: shares.length },
                { id: 'settings', label: 'Settings' }
            ], activeTab)}

            <div class="tab-content" id="groupTabContent" data-testid="group-tab-content">
                ${tabContent}
            </div>
        `;
    },

    _groupOverview(group, children, projects) {
        const canCreateSubgroup = !group.archived;
        const canCreateProject = !group.archived;

        return `
            ${group.readme ? `<div class="readme-box" data-testid="group-readme"><div class="readme-content">${Components.escapeHtml(group.readme)}</div></div>` : ''}
            <div class="section-header">
                <h2>Subgroups (${children.length})</h2>
                ${canCreateSubgroup ? `<button class="btn btn-primary btn-sm" onclick="Views._showCreateGroupModal(${group.id})" data-testid="create-subgroup-btn">New subgroup</button>` : ''}
            </div>
            <div class="group-list" data-testid="subgroup-list">
                ${children.length === 0 ? `<p class="text-muted">No subgroups</p>` : children.map(g => Views._groupListItem(g)).join('')}
            </div>
            <div class="section-header" style="margin-top:24px">
                <h2>Projects (${projects.length})</h2>
                ${canCreateProject ? `<button class="btn btn-primary btn-sm" onclick="Views._showCreateProjectModal(${group.id})" data-testid="create-project-btn">New project</button>` : ''}
            </div>
            <div class="project-list" data-testid="project-list">
                ${projects.length === 0 ? `<p class="text-muted">No projects</p>` : projects.map(p => `
                    <div class="list-item" data-testid="project-item-${p.id}">
                        <div class="list-item-left">
                            <div class="list-item-info">
                                <div class="list-item-title clickable" onclick="Router.navigate('/projects/${p.id}')">${Components.escapeHtml(p.name)}</div>
                                <div class="list-item-meta">${Components.escapeHtml(p.description)}</div>
                            </div>
                        </div>
                        <div class="list-item-right">
                            ${p.archived ? Components.badge('Archived', 'muted') : ''}
                            ${Components.visibilityBadge(p.visibility)}
                            <span class="project-stars">★ ${p.stars}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    },

    _groupMembers(group, allMembers, isOwner, isMaintainer) {
        const filterType = AppState.routeParams.memberFilter || 'all';
        let filteredMembers = allMembers;
        if (filterType === 'direct') filteredMembers = allMembers.filter(m => m.membershipType === 'direct');
        else if (filterType === 'inherited') filteredMembers = allMembers.filter(m => m.membershipType === 'inherited');
        else if (filterType === 'shared') filteredMembers = allMembers.filter(m => m.membershipType === 'shared' || m.membershipType === 'inherited_shared');

        return `
            <div class="list-controls">
                ${Components.searchInput('memberSearch', '', 'Search members...')}
                <div class="list-controls-right">
                    ${Components.dropdown('memberTypeFilter', [
                        { value: 'all', label: 'All members' },
                        { value: 'direct', label: 'Direct' },
                        { value: 'inherited', label: 'Inherited' },
                        { value: 'shared', label: 'Shared' }
                    ], filterType)}
                    ${isMaintainer && !group.archived ? `<button class="btn btn-primary btn-sm" onclick="Views._showAddMemberModal('group', ${group.id})" data-testid="add-member-btn">Add member</button>` : ''}
                </div>
            </div>
            ${group.userCap ? Components.warningBox(`This group has a user cap of ${group.userCap}. Current direct members: ${AppState.getDirectGroupMembers(group.id).length}/${group.userCap}`) : ''}
            ${group.preventInvitations ? Components.infoBox('New member invitations are disabled for this group.') : ''}
            <div class="member-list" data-testid="member-list">
                <div class="member-list-header">
                    <span class="member-col-user">User</span>
                    <span class="member-col-source">Source</span>
                    <span class="member-col-role">Max role</span>
                    <span class="member-col-expiry">Expiration</span>
                    <span class="member-col-actions">Actions</span>
                </div>
                ${filteredMembers.map(m => {
                    const user = AppState.getUserById(m.userId);
                    if (!user) return '';
                    const canEdit = isMaintainer && m.membershipType === 'direct' && !(m.role.level >= ROLES.OWNER.level && !isOwner);
                    const canRemove = (isOwner || (isMaintainer && m.role.level < ROLES.OWNER.level)) && m.membershipType === 'direct';
                    return `
                        <div class="member-list-row" data-testid="member-row-${user.username}">
                            <span class="member-col-user">
                                ${Components.avatar(user, 28)}
                                <div>
                                    <div class="member-name">${Components.escapeHtml(user.name)}</div>
                                    <div class="member-username">@${Components.escapeHtml(user.username)}</div>
                                </div>
                            </span>
                            <span class="member-col-source">${Components.membershipBadge(m.membershipType)}${m.source ? ` <span class="text-muted text-sm">via ${Components.escapeHtml(m.source.name)}</span>` : ''}</span>
                            <span class="member-col-role">${Components.roleBadge(m.role)}</span>
                            <span class="member-col-expiry">${m.expiresAt ? `<span class="expiry-date ${new Date(m.expiresAt) < new Date(Date.now() + 7*86400000) ? 'expiring-soon' : ''}">${Components.formatDate(m.expiresAt)}</span>` : '<span class="text-muted">No expiration</span>'}</span>
                            <span class="member-col-actions">
                                ${canEdit ? `<button class="btn btn-sm btn-secondary" onclick="Views._showEditMemberModal('group', ${group.id}, ${user.id})" data-testid="edit-member-${user.username}">Edit</button>` : ''}
                                ${canRemove ? `<button class="btn btn-sm btn-danger-outline" onclick="Views._confirmRemoveMember('group', ${group.id}, ${user.id})" data-testid="remove-member-${user.username}">Remove</button>` : ''}
                            </span>
                        </div>
                    `;
                }).join('')}
                ${filteredMembers.length === 0 ? '<div class="text-muted" style="padding:16px">No members match the current filter.</div>' : ''}
            </div>
        `;
    },

    _groupSettings(group, isOwner, isMaintainer) {
        if (!isMaintainer) {
            return Components.warningBox('You need Maintainer or Owner permissions to view group settings.');
        }

        const parentVisibilities = [];
        if (AppState.isVisibilityAllowed('private', group.parentId)) parentVisibilities.push({ value: 'private', label: 'Private', description: 'Only members can see this group' });
        if (AppState.isVisibilityAllowed('internal', group.parentId)) parentVisibilities.push({ value: 'internal', label: 'Internal', description: 'Any logged-in user can see this group' });
        if (AppState.isVisibilityAllowed('public', group.parentId)) parentVisibilities.push({ value: 'public', label: 'Public', description: 'Anyone can see this group' });

        return `
            <form id="groupSettingsForm" data-testid="group-settings-form">
                <div class="settings-section">
                    <h3>General</h3>
                    ${Components.formField('groupName', 'Group name', Components.textInput('groupName', group.name, { maxlength: 255 }), { required: true })}
                    ${Components.formField('groupPath', 'Group URL', Components.textInput('groupPath', group.path, { maxlength: 255 }), { required: true, help: `Full path: ${group.fullPath}` })}
                    ${Components.formField('groupDesc', 'Description', Components.textarea('groupDesc', group.description, { rows: 3 }))}
                    ${Components.formField('groupVisibility', 'Visibility', Components.dropdown('groupVisibility', parentVisibilities, group.visibility))}
                </div>

                <div class="settings-section">
                    <h3>Permissions</h3>
                    ${Components.formField('subgroupCreation', 'Allowed to create subgroups',
                        Components.dropdown('subgroupCreation', [
                            { value: 'owner', label: 'Owners' },
                            { value: 'maintainer', label: 'Maintainers and above' },
                            { value: 'developer', label: 'Developers and above' }
                        ], group.subgroupCreationLevel)
                    )}
                    ${Components.formField('projectCreation', 'Allowed to create projects',
                        Components.dropdown('projectCreation', [
                            { value: 'owner', label: 'Owners' },
                            { value: 'maintainer', label: 'Maintainers and above' },
                            { value: 'developer', label: 'Developers and above' },
                            { value: 'noone', label: 'No one' }
                        ], group.projectCreationLevel)
                    )}
                    ${Components.formField('branchProtection', 'Default branch protection',
                        Components.dropdown('branchProtection', [
                            { value: 'fully_protected', label: 'Fully protected' },
                            { value: 'developers_can_merge', label: 'Developers can merge' },
                            { value: 'no_protection', label: 'No protection' }
                        ], group.defaultBranchProtection)
                    )}
                </div>

                <div class="settings-section">
                    <h3>Access Restrictions</h3>
                    ${Components.formField('userCap', 'User cap', Components.textInput('userCap', group.userCap || '', { placeholder: 'No limit' }), { help: 'Maximum number of billable members. Leave empty for no limit.' })}
                    ${Components.checkbox('preventInvitations', 'Prevent invitations to this group', group.preventInvitations)}
                    ${Components.checkbox('preventSharingOutside', 'Prevent sharing projects outside the group hierarchy', group.preventSharingOutsideHierarchy)}
                    ${Components.checkbox('disableMentions', 'Disable group mentions', group.disableMentions)}
                    ${Components.checkbox('requireTwoFactor', 'Require two-factor authentication', group.requireTwoFactor)}
                </div>

                ${isOwner && !group.archived ? `
                    <div class="settings-section">
                        <h3>Archive</h3>
                        <p class="text-muted">Archiving a group disables all modifications. Subgroups and projects are also affected.</p>
                        <button type="button" class="btn btn-warning" onclick="Views._confirmArchiveGroup(${group.id})" data-testid="archive-group-btn">Archive this group</button>
                    </div>
                ` : ''}
                ${isOwner && group.archived ? `
                    <div class="settings-section">
                        <h3>Unarchive</h3>
                        <button type="button" class="btn btn-primary" onclick="Views._unarchiveGroup(${group.id})" data-testid="unarchive-group-btn">Unarchive this group</button>
                    </div>
                ` : ''}
                ${isOwner ? `
                    <div class="settings-section">
                        <h3>Transfer group</h3>
                        <p class="text-muted">Transfer this group to another parent group or make it a top-level group.</p>
                        <button type="button" class="btn btn-warning" onclick="Views._showTransferGroupModal(${group.id})" data-testid="transfer-group-btn">Transfer group</button>
                    </div>
                ` : ''}

                <div class="form-actions">
                    <button type="button" class="btn btn-primary" id="saveGroupSettingsBtn" data-testid="save-group-settings">Save changes</button>
                </div>
            </form>
        `;
    },

    _groupSharing(group, shares, isOwner) {
        return `
            <div class="list-controls">
                <h3>Groups shared with "${Components.escapeHtml(group.name)}"</h3>
                ${isOwner && !group.archived ? `<button class="btn btn-primary btn-sm" onclick="Views._showShareGroupModal(${group.id})" data-testid="share-group-btn">Invite a group</button>` : ''}
            </div>
            ${group.preventSharingOutsideHierarchy ? Components.warningBox('Sharing with groups outside the hierarchy is restricted.') : ''}
            <div class="share-list" data-testid="share-list">
                ${shares.length === 0 ? '<p class="text-muted" style="padding:16px">No groups have been invited to share with this group.</p>' : ''}
                ${shares.map(s => {
                    const sourceGroup = AppState.getGroupById(s.sourceGroupId);
                    if (!sourceGroup) return '';
                    return `
                        <div class="list-item" data-testid="share-item-${sourceGroup.id}">
                            <div class="list-item-left">
                                ${Components.groupAvatar(sourceGroup, 32)}
                                <div class="list-item-info">
                                    <div class="list-item-title">${Components.escapeHtml(sourceGroup.name)}</div>
                                    <div class="list-item-meta">Max role: ${Components.roleBadge(s.maxRole)} ${s.expiresAt ? `· Expires: ${Components.formatDate(s.expiresAt)}` : ''}</div>
                                </div>
                            </div>
                            <div class="list-item-right">
                                ${isOwner ? `<button class="btn btn-sm btn-danger-outline" onclick="Views._confirmRemoveGroupShare(${s.sourceGroupId}, ${group.id})" data-testid="remove-share-${sourceGroup.id}">Remove</button>` : ''}
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    },

    // ==========================
    // PROJECTS
    // ==========================
    projects() {
        Components.renderBreadcrumb([
            { label: 'Home', route: '/' },
            { label: 'Projects', route: '/projects' }
        ]);

        const allProjects = AppState.projects.filter(p => !p.archived);

        return `
            <div class="page-header">
                <div class="page-header-row">
                    <h1 data-testid="page-title">Projects</h1>
                    <button class="btn btn-primary" id="createProjectBtn" data-testid="create-project-btn" onclick="Views._showCreateProjectModal()">New project</button>
                </div>
                <p class="page-subtitle">Projects contain your source code, issues, merge requests, and CI/CD pipelines.</p>
            </div>
            <div class="list-controls">
                ${Components.searchInput('projectSearch', '', 'Search projects...')}
                <div class="list-controls-right">
                    ${Components.dropdown('projectVisFilter', [
                        { value: 'all', label: 'All visibilities' },
                        { value: 'public', label: 'Public' },
                        { value: 'internal', label: 'Internal' },
                        { value: 'private', label: 'Private' }
                    ], 'all')}
                </div>
            </div>
            <div class="project-list" data-testid="project-list">
                ${allProjects.map(p => {
                    const group = AppState.getGroupById(p.groupId);
                    return `
                        <div class="list-item" data-testid="project-item-${p.id}">
                            <div class="list-item-left">
                                <div class="list-item-info">
                                    <div class="list-item-title clickable" onclick="Router.navigate('/projects/${p.id}')">${Components.escapeHtml(p.name)}</div>
                                    <div class="list-item-meta">${Components.escapeHtml(p.fullPath)}</div>
                                    <div class="list-item-description">${Components.escapeHtml(p.description)}</div>
                                    ${p.topics.length ? `<div class="topic-tags">${p.topics.map(t => `<span class="topic-tag">${Components.escapeHtml(t)}</span>`).join('')}</div>` : ''}
                                </div>
                            </div>
                            <div class="list-item-right">
                                ${Components.visibilityBadge(p.visibility)}
                                <span class="project-stars">★ ${p.stars}</span>
                                <span class="text-muted">Updated ${Components.timeAgo(p.updatedAt)}</span>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    },

    projectDetail(projectId) {
        const project = AppState.getProjectById(parseInt(projectId));
        if (!project) return Views._notFound('Project not found');

        const group = AppState.getGroupById(project.groupId);
        const ancestors = group ? AppState.getGroupAncestors(group.id) : [];
        const bcItems = [{ label: 'Home', route: '/' }, { label: 'Projects', route: '/projects' }];
        ancestors.forEach(a => bcItems.push({ label: a.name, route: `/groups/${a.id}` }));
        if (group) bcItems.push({ label: group.name, route: `/groups/${group.id}` });
        bcItems.push({ label: project.name, route: `/projects/${project.id}` });
        Components.renderBreadcrumb(bcItems);

        const allMembers = AppState.getAllProjectMembers(project.id);
        const directMembers = AppState.getDirectProjectMembers(project.id);
        const userRole = AppState.getCurrentUserProjectRole(project.id);
        const isMaintainer = userRole && userRole.level >= ROLES.MAINTAINER.level;
        const isOwner = userRole && userRole.level >= ROLES.OWNER.level;
        const shares = AppState.projectShares.filter(s => s.targetProjectId === project.id);

        const activeTab = AppState.routeParams.tab || 'overview';

        let tabContent = '';
        if (activeTab === 'overview') {
            tabContent = Views._projectOverview(project);
        } else if (activeTab === 'members') {
            tabContent = Views._projectMembers(project, allMembers, isMaintainer, isOwner);
        } else if (activeTab === 'sharing') {
            tabContent = Views._projectSharing(project, shares, isMaintainer);
        } else if (activeTab === 'settings') {
            tabContent = Views._projectSettings(project, isOwner);
        }

        return `
            <div class="page-header">
                <div class="page-header-row">
                    <div class="page-header-title-row">
                        <div>
                            <h1 data-testid="page-title">${Components.escapeHtml(project.name)}</h1>
                            <p class="page-subtitle">${Components.escapeHtml(project.description)}</p>
                        </div>
                    </div>
                    <div class="page-actions">
                        ${project.archived ? Components.badge('Archived', 'muted') : ''}
                        ${isOwner ? `<button class="btn btn-danger-outline btn-sm" data-testid="delete-project-btn" onclick="Views._confirmDeleteProject(${project.id})">Delete project</button>` : ''}
                    </div>
                </div>
            </div>
            <div class="detail-meta">
                ${Components.visibilityBadge(project.visibility)}
                ${userRole ? Components.roleBadge(userRole) : ''}
                <span class="text-muted">Path: ${Components.escapeHtml(project.fullPath)}</span>
                <span class="project-stars">★ ${project.stars}</span>
                <span class="text-muted">Forks: ${project.forks}</span>
                <span class="text-muted">Default branch: ${Components.escapeHtml(project.defaultBranch)}</span>
            </div>
            ${project.topics.length ? `<div class="topic-tags" style="margin-top:8px">${project.topics.map(t => `<span class="topic-tag">${Components.escapeHtml(t)}</span>`).join('')}</div>` : ''}

            ${Components.tabs('projectTabs', [
                { id: 'overview', label: 'Overview' },
                { id: 'members', label: 'Members', count: allMembers.length },
                { id: 'sharing', label: 'Sharing', count: shares.length },
                { id: 'settings', label: 'Settings' }
            ], activeTab)}

            <div class="tab-content" id="projectTabContent" data-testid="project-tab-content">
                ${tabContent}
            </div>
        `;
    },

    _projectOverview(project) {
        return `
            <div class="project-overview" data-testid="project-overview">
                ${project.empty ? Components.infoBox('This project is empty. Initialize it by pushing code or uploading files.') : ''}
                <div class="project-info-grid">
                    <div class="info-row"><span class="info-label">Created:</span> <span>${Components.formatDate(project.createdAt)}</span></div>
                    <div class="info-row"><span class="info-label">Last updated:</span> <span>${Components.formatDateTime(project.updatedAt)}</span></div>
                    <div class="info-row"><span class="info-label">Default branch:</span> <span><code>${Components.escapeHtml(project.defaultBranch)}</code></span></div>
                    <div class="info-row"><span class="info-label">Stars:</span> <span>${project.stars}</span></div>
                    <div class="info-row"><span class="info-label">Forks:</span> <span>${project.forks}</span></div>
                </div>
            </div>
        `;
    },

    _projectMembers(project, allMembers, isMaintainer, isOwner) {
        const filterType = AppState.routeParams.memberFilter || 'all';
        let filteredMembers = allMembers;
        if (filterType === 'direct') filteredMembers = allMembers.filter(m => m.membershipType === 'direct');
        else if (filterType === 'inherited') filteredMembers = allMembers.filter(m => m.membershipType === 'inherited');
        else if (filterType === 'shared') filteredMembers = allMembers.filter(m => m.membershipType === 'shared');

        return `
            <div class="list-controls">
                ${Components.searchInput('projectMemberSearch', '', 'Search members...')}
                <div class="list-controls-right">
                    ${Components.dropdown('projectMemberTypeFilter', [
                        { value: 'all', label: 'All members' },
                        { value: 'direct', label: 'Direct' },
                        { value: 'inherited', label: 'Inherited' },
                        { value: 'shared', label: 'Shared' }
                    ], filterType)}
                    ${isMaintainer && !project.archived ? `<button class="btn btn-primary btn-sm" onclick="Views._showAddMemberModal('project', ${project.id})" data-testid="add-project-member-btn">Add member</button>` : ''}
                </div>
            </div>
            <div class="member-list" data-testid="project-member-list">
                <div class="member-list-header">
                    <span class="member-col-user">User</span>
                    <span class="member-col-source">Source</span>
                    <span class="member-col-role">Role</span>
                    <span class="member-col-expiry">Expiration</span>
                    <span class="member-col-actions">Actions</span>
                </div>
                ${filteredMembers.map(m => {
                    const user = AppState.getUserById(m.userId);
                    if (!user) return '';
                    const canRemove = isMaintainer && m.membershipType === 'direct';
                    return `
                        <div class="member-list-row" data-testid="project-member-row-${user.username}">
                            <span class="member-col-user">
                                ${Components.avatar(user, 28)}
                                <div>
                                    <div class="member-name">${Components.escapeHtml(user.name)}</div>
                                    <div class="member-username">@${Components.escapeHtml(user.username)}</div>
                                </div>
                            </span>
                            <span class="member-col-source">${Components.membershipBadge(m.membershipType)}${m.source ? ` <span class="text-muted text-sm">via ${Components.escapeHtml(m.source.name || m.source.path)}</span>` : ''}</span>
                            <span class="member-col-role">${Components.roleBadge(m.role)}</span>
                            <span class="member-col-expiry">${m.expiresAt ? Components.formatDate(m.expiresAt) : '<span class="text-muted">No expiration</span>'}</span>
                            <span class="member-col-actions">
                                ${canRemove ? `<button class="btn btn-sm btn-danger-outline" onclick="Views._confirmRemoveMember('project', ${project.id}, ${user.id})" data-testid="remove-project-member-${user.username}">Remove</button>` : ''}
                            </span>
                        </div>
                    `;
                }).join('')}
                ${filteredMembers.length === 0 ? '<div class="text-muted" style="padding:16px">No members match the current filter.</div>' : ''}
            </div>
        `;
    },

    _projectSharing(project, shares, isMaintainer) {
        const group = AppState.getGroupById(project.groupId);
        const topGroup = group ? Views._getTopLevelGroup(group) : null;
        const sharingBlocked = topGroup && topGroup.preventSharingOutsideHierarchy;

        return `
            <div class="list-controls">
                <h3>Groups shared with "${Components.escapeHtml(project.name)}"</h3>
                ${isMaintainer && !project.archived ? `<button class="btn btn-primary btn-sm" onclick="Views._showShareProjectModal(${project.id})" data-testid="share-project-btn">Invite a group</button>` : ''}
            </div>
            ${sharingBlocked ? Components.warningBox('The top-level group restricts sharing projects outside its hierarchy.') : ''}
            <div class="share-list" data-testid="project-share-list">
                ${shares.length === 0 ? '<p class="text-muted" style="padding:16px">No groups have been invited.</p>' : ''}
                ${shares.map(s => {
                    const sourceGroup = AppState.getGroupById(s.sourceGroupId);
                    if (!sourceGroup) return '';
                    return `
                        <div class="list-item" data-testid="project-share-item-${sourceGroup.id}">
                            <div class="list-item-left">
                                ${Components.groupAvatar(sourceGroup, 32)}
                                <div class="list-item-info">
                                    <div class="list-item-title">${Components.escapeHtml(sourceGroup.name)}</div>
                                    <div class="list-item-meta">Max role: ${Components.roleBadge(s.maxRole)} ${s.expiresAt ? `· Expires: ${Components.formatDate(s.expiresAt)}` : ''}</div>
                                </div>
                            </div>
                            <div class="list-item-right">
                                ${isMaintainer ? `<button class="btn btn-sm btn-danger-outline" onclick="Views._confirmRemoveProjectShare(${s.sourceGroupId}, ${project.id})" data-testid="remove-project-share-${sourceGroup.id}">Remove</button>` : ''}
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    },

    _projectSettings(project, isOwner) {
        if (!isOwner) return Components.warningBox('You need Owner permissions to modify project settings.');
        const group = AppState.getGroupById(project.groupId);

        const visOptions = [];
        visOptions.push({ value: 'private', label: 'Private' });
        if (group && (group.visibility === 'internal' || group.visibility === 'public')) {
            visOptions.push({ value: 'internal', label: 'Internal' });
        }
        if (group && group.visibility === 'public') {
            visOptions.push({ value: 'public', label: 'Public' });
        }

        return `
            <form id="projectSettingsForm" data-testid="project-settings-form">
                <div class="settings-section">
                    <h3>General</h3>
                    ${Components.formField('projectName', 'Project name', Components.textInput('projectName', project.name, { maxlength: 255 }), { required: true })}
                    ${Components.formField('projectPath', 'Project URL', Components.textInput('projectPath', project.path, { maxlength: 255 }), { required: true })}
                    ${Components.formField('projectDesc', 'Description', Components.textarea('projectDesc', project.description, { rows: 3 }))}
                    ${Components.formField('projectVisibility', 'Visibility', Components.dropdown('projectVisibility', visOptions, project.visibility), { help: 'Visibility cannot exceed the parent group visibility.' })}
                    ${Components.formField('projectTopics', 'Topics', Components.textInput('projectTopics', project.topics.join(', '), { placeholder: 'Comma-separated topics' }), { help: 'Comma-separated list of topics.' })}
                </div>
                <div class="form-actions">
                    <button type="button" class="btn btn-primary" id="saveProjectSettingsBtn" data-testid="save-project-settings">Save changes</button>
                </div>
            </form>
        `;
    },

    // ==========================
    // MEMBERS (global view)
    // ==========================
    members() {
        Components.renderBreadcrumb([
            { label: 'Home', route: '/' },
            { label: 'Members', route: '/members' }
        ]);

        return `
            <div class="page-header">
                <h1 data-testid="page-title">Members</h1>
                <p class="page-subtitle">View and manage members across groups and projects.</p>
            </div>
            <div class="list-controls">
                ${Components.searchInput('globalMemberSearch', '', 'Search users...')}
            </div>
            <div class="member-list" data-testid="global-member-list">
                <div class="member-list-header">
                    <span class="member-col-user">User</span>
                    <span class="member-col-source">Groups</span>
                    <span class="member-col-role">Status</span>
                    <span class="member-col-expiry">Last Active</span>
                    <span class="member-col-actions">2FA</span>
                </div>
                ${AppState.users.map(u => {
                    const userGroups = AppState.groupMemberships.filter(m => m.userId === u.id && m.membershipType === 'direct');
                    return `
                        <div class="member-list-row" data-testid="global-member-row-${u.username}">
                            <span class="member-col-user">
                                ${Components.avatar(u, 28)}
                                <div>
                                    <div class="member-name clickable" onclick="Router.navigate('/profile/${u.username}')">${Components.escapeHtml(u.name)}</div>
                                    <div class="member-username">@${Components.escapeHtml(u.username)}</div>
                                </div>
                            </span>
                            <span class="member-col-source">${userGroups.length} group(s)</span>
                            <span class="member-col-role">${u.status && u.status.busy ? Components.badge('Busy', 'warning') : Components.badge('Active', 'success')}</span>
                            <span class="member-col-expiry">${Components.timeAgo(u.lastActivityAt)}</span>
                            <span class="member-col-actions">${u.twoFactorEnabled ? Components.badge('Enabled', 'success') : Components.badge('Disabled', 'muted')}</span>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    },

    // ==========================
    // NAMESPACES
    // ==========================
    namespaces() {
        Components.renderBreadcrumb([
            { label: 'Home', route: '/' },
            { label: 'Namespaces', route: '/namespaces' }
        ]);

        const userNamespaces = AppState.users.map(u => ({
            type: 'user',
            name: u.username,
            owner: u.name,
            path: u.username,
            kind: 'User'
        }));
        const groupNamespaces = AppState.groups.filter(g => g.parentId === null).map(g => ({
            type: 'group',
            name: g.name,
            path: g.fullPath,
            kind: 'Group',
            owner: (() => {
                const ownerMembership = AppState.groupMemberships.find(m => m.groupId === g.id && m.role.level === ROLES.OWNER.level);
                return ownerMembership ? AppState.getUserById(ownerMembership.userId)?.name : 'Unknown';
            })()
        }));

        const allNamespaces = [...userNamespaces, ...groupNamespaces].sort((a, b) => a.path.localeCompare(b.path));

        return `
            <div class="page-header">
                <h1 data-testid="page-title">Namespaces</h1>
                <p class="page-subtitle">Namespaces organize projects and define URL paths. Each user has a personal namespace, and each group is also a namespace.</p>
            </div>
            ${Components.infoBox('Namespaces must be unique. Changing a username or group path changes the namespace and generates URL redirects.')}
            <div class="list-controls">
                ${Components.searchInput('namespaceSearch', '', 'Search namespaces...')}
            </div>
            <div class="namespace-list" data-testid="namespace-list">
                <div class="member-list-header">
                    <span class="member-col-user">Namespace</span>
                    <span class="member-col-source">Path</span>
                    <span class="member-col-role">Kind</span>
                    <span class="member-col-expiry">Owner</span>
                </div>
                ${allNamespaces.map(ns => `
                    <div class="member-list-row" data-testid="namespace-row-${ns.path}">
                        <span class="member-col-user"><strong>${Components.escapeHtml(ns.name)}</strong></span>
                        <span class="member-col-source"><code>${Components.escapeHtml(ns.path)}</code></span>
                        <span class="member-col-role">${Components.badge(ns.kind, ns.kind === 'User' ? 'info' : 'default')}</span>
                        <span class="member-col-expiry">${Components.escapeHtml(ns.owner)}</span>
                    </div>
                `).join('')}
            </div>
        `;
    },

    // ==========================
    // PROFILE
    // ==========================
    profile(username) {
        const user = username ? AppState.getUserByUsername(username) : AppState.currentUser;
        if (!user) return Views._notFound('User not found');

        const isOwnProfile = user.id === AppState.currentUser.id;

        Components.renderBreadcrumb([
            { label: 'Home', route: '/' },
            { label: isOwnProfile ? 'Your Profile' : user.name, route: isOwnProfile ? '/profile' : `/profile/${user.username}` }
        ]);

        const userGroups = AppState.groupMemberships.filter(m => m.userId === user.id && m.membershipType === 'direct');
        const activeTab = AppState.routeParams.tab || 'overview';

        let tabContent = '';
        if (activeTab === 'overview') {
            tabContent = Views._profileOverview(user, userGroups);
        } else if (activeTab === 'edit' && isOwnProfile) {
            tabContent = Views._profileEdit(user);
        } else if (activeTab === 'emails' && isOwnProfile) {
            tabContent = Views._profileEmails(user);
        } else if (activeTab === 'account' && isOwnProfile) {
            tabContent = Views._profileAccount(user);
        }

        const tabs = [{ id: 'overview', label: 'Overview' }];
        if (isOwnProfile) {
            tabs.push({ id: 'edit', label: 'Edit Profile' });
            tabs.push({ id: 'emails', label: 'Emails' });
            tabs.push({ id: 'account', label: 'Account' });
        }

        return `
            <div class="profile-header" data-testid="profile-header">
                <div class="profile-header-row">
                    ${Components.avatar(user, 80)}
                    <div class="profile-header-info">
                        <h1 data-testid="profile-name">${Components.escapeHtml(user.name)}</h1>
                        <div class="profile-username">@${Components.escapeHtml(user.username)} ${user.pronouns ? `<span class="text-muted">(${Components.escapeHtml(user.pronouns)})</span>` : ''}</div>
                        ${user.status && user.status.message ? `<div class="profile-status">${user.status.emoji || ''} ${Components.escapeHtml(user.status.message)} ${user.status.busy ? Components.badge('Busy', 'warning') : ''}</div>` : ''}
                        ${user.bio ? `<p class="profile-bio">${Components.escapeHtml(user.bio)}</p>` : ''}
                    </div>
                </div>
                <div class="profile-meta-row">
                    ${user.location ? `<span class="profile-meta-item">📍 ${Components.escapeHtml(user.location)}</span>` : ''}
                    ${user.organization ? `<span class="profile-meta-item">🏢 ${Components.escapeHtml(user.organization)}</span>` : ''}
                    ${user.website ? `<span class="profile-meta-item">🔗 ${Components.escapeHtml(user.website)}</span>` : ''}
                    <span class="profile-meta-item">Joined ${Components.formatDate(user.createdAt)}</span>
                    ${user.followersCount !== undefined ? `<span class="profile-meta-item">${user.followersCount} followers</span>` : ''}
                    ${user.followingCount !== undefined ? `<span class="profile-meta-item">${user.followingCount} following</span>` : ''}
                </div>
            </div>

            ${Components.tabs('profileTabs', tabs, activeTab)}

            <div class="tab-content" data-testid="profile-tab-content">
                ${tabContent}
            </div>
        `;
    },

    _profileOverview(user, userGroups) {
        return `
            <div class="section-header"><h2>Groups</h2></div>
            <div class="group-list">
                ${userGroups.length === 0 ? '<p class="text-muted">Not a member of any groups.</p>' : ''}
                ${userGroups.map(m => {
                    const group = AppState.getGroupById(m.groupId);
                    if (!group) return '';
                    return `
                        <div class="list-item">
                            <div class="list-item-left">
                                ${Components.groupAvatar(group, 28)}
                                <div class="list-item-info">
                                    <div class="list-item-title clickable" onclick="Router.navigate('/groups/${group.id}')">${Components.escapeHtml(group.name)}</div>
                                    <div class="list-item-meta">${Components.escapeHtml(group.fullPath)}</div>
                                </div>
                            </div>
                            <div class="list-item-right">
                                ${Components.roleBadge(m.role)}
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
            <div class="section-header" style="margin-top:24px"><h2>External Accounts</h2></div>
            <div class="external-accounts">
                ${user.linkedin ? `<div class="external-account-item">LinkedIn: <strong>${Components.escapeHtml(user.linkedin)}</strong></div>` : ''}
                ${user.discord ? `<div class="external-account-item">Discord: <strong>${Components.escapeHtml(user.discord)}</strong></div>` : ''}
                ${user.bluesky ? `<div class="external-account-item">BlueSky: <strong>${Components.escapeHtml(user.bluesky)}</strong></div>` : ''}
                ${!user.linkedin && !user.discord && !user.bluesky ? '<p class="text-muted">No external accounts linked.</p>' : ''}
            </div>
        `;
    },

    _profileEdit(user) {
        return `
            <form id="profileEditForm" data-testid="profile-edit-form">
                <div class="settings-section">
                    <h3>Public Information</h3>
                    ${Components.formField('profileName', 'Full name', Components.textInput('profileName', user.name), { required: true })}
                    ${Components.formField('profilePronouns', 'Pronouns', Components.textInput('profilePronouns', user.pronouns || '', { placeholder: 'e.g., they/them, she/her' }))}
                    ${Components.formField('profileBio', 'Bio', Components.textarea('profileBio', user.bio || '', { rows: 3, placeholder: 'Tell us about yourself' }))}
                    ${Components.formField('profileLocation', 'Location', Components.textInput('profileLocation', user.location || ''))}
                    ${Components.formField('profileOrg', 'Organization', Components.textInput('profileOrg', user.organization || ''))}
                    ${Components.formField('profileWebsite', 'Website', Components.textInput('profileWebsite', user.website || '', { placeholder: 'https://' }))}
                </div>
                <div class="settings-section">
                    <h3>Status</h3>
                    ${Components.formField('statusEmoji', 'Emoji', Components.textInput('statusEmoji', user.status?.emoji || '', { placeholder: 'e.g., 💻' }))}
                    ${Components.formField('statusMessage', 'Status message', Components.textInput('statusMessage', user.status?.message || '', { placeholder: 'What are you working on?' }))}
                    ${Components.checkbox('statusBusy', 'Set as Busy', user.status?.busy || false)}
                </div>
                <div class="settings-section">
                    <h3>External Accounts</h3>
                    ${Components.formField('profileLinkedin', 'LinkedIn', Components.textInput('profileLinkedin', user.linkedin || ''))}
                    ${Components.formField('profileDiscord', 'Discord', Components.textInput('profileDiscord', user.discord || ''))}
                    ${Components.formField('profileBluesky', 'BlueSky', Components.textInput('profileBluesky', user.bluesky || ''))}
                </div>
                <div class="settings-section">
                    <h3>Profile Visibility</h3>
                    ${Components.formField('profileVisibility', 'Visibility',
                        Components.dropdown('profileVisibility', [
                            { value: 'public', label: 'Public' },
                            { value: 'internal', label: 'Internal' },
                            { value: 'private', label: 'Private' }
                        ], user.profileVisibility)
                    )}
                </div>
                <div class="form-actions">
                    <button type="button" class="btn btn-primary" id="saveProfileBtn" data-testid="save-profile-btn">Update profile</button>
                </div>
            </form>
        `;
    },

    _profileEmails(user) {
        const allEmails = [
            { email: user.email, primary: true, verified: true },
            ...(user.secondaryEmails || []).map(e => ({ email: e, primary: false, verified: true }))
        ];

        return `
            <div class="settings-section">
                <h3>Email Addresses</h3>
                ${Components.infoBox('Your primary email is used for login, commits, and notifications. Secondary emails can be used for password recovery.')}
                <div class="email-list" data-testid="email-list">
                    ${allEmails.map(e => `
                        <div class="list-item" data-testid="email-item-${e.email}">
                            <div class="list-item-left">
                                <div class="list-item-info">
                                    <div class="list-item-title">${Components.escapeHtml(e.email)}</div>
                                    <div class="list-item-meta">${e.primary ? Components.badge('Primary', 'info') : ''} ${e.verified ? Components.badge('Verified', 'success') : Components.badge('Unverified', 'warning')}</div>
                                </div>
                            </div>
                            <div class="list-item-right">
                                ${!e.primary ? `<button class="btn btn-sm btn-danger-outline" onclick="Views._removeEmail('${Components.escapeAttr(e.email)}')" data-testid="remove-email-${e.email}">Remove</button>` : ''}
                            </div>
                        </div>
                    `).join('')}
                </div>
                <div class="add-email-form" style="margin-top:16px">
                    <div class="inline-form">
                        <input type="text" id="newEmailInput" class="form-input" placeholder="Add new email address" data-testid="new-email-input">
                        <button class="btn btn-primary btn-sm" id="addEmailBtn" data-testid="add-email-btn">Add email</button>
                    </div>
                </div>
            </div>
            <div class="settings-section">
                <h3>Commit Email</h3>
                <p class="text-muted">This email is used for web-based Git operations.</p>
                ${Components.formField('commitEmail', 'Commit email',
                    Components.dropdown('commitEmail', [
                        { value: user.email, label: user.email },
                        ...(user.secondaryEmails || []).map(e => ({ value: e, label: e })),
                        { value: 'private', label: `Use private email: ${user.privateCommitEmail || 'N/A'}` }
                    ], user.usePrivateCommitEmail ? 'private' : user.commitEmail)
                )}
            </div>
        `;
    },

    _profileAccount(user) {
        return `
            <div class="settings-section">
                <h3>Username</h3>
                ${Components.warningBox('Changing your username will change your namespace URL and create redirects from old URLs. This may break existing links.')}
                ${Components.formField('accountUsername', 'Username', Components.textInput('accountUsername', user.username, { maxlength: 255 }), { required: true, help: 'Must be 2-255 characters. Letters, digits, _, -, . allowed. Must start and end with letter or digit.' })}
                <button type="button" class="btn btn-warning btn-sm" id="changeUsernameBtn" data-testid="change-username-btn" style="margin-top:8px">Change username</button>
            </div>
            <div class="settings-section">
                <h3>Password</h3>
                <p class="text-muted">Use the password reset link to generate a new password.</p>
                <button type="button" class="btn btn-secondary btn-sm" data-testid="reset-password-btn" onclick="Components.showToast('Password reset email sent (simulated)', 'success')">Send password reset email</button>
            </div>
            <div class="settings-section">
                <h3>Two-Factor Authentication</h3>
                <p>${user.twoFactorEnabled ? Components.badge('Enabled', 'success') : Components.badge('Disabled', 'warning')}</p>
                <button type="button" class="btn btn-secondary btn-sm" data-testid="toggle-2fa-btn" onclick="Views._toggle2FA()">${user.twoFactorEnabled ? 'Disable 2FA' : 'Enable 2FA'}</button>
            </div>
            <div class="settings-section">
                <h3>Timezone</h3>
                ${Components.formField('accountTimezone', 'Timezone',
                    Components.dropdown('accountTimezone', TIMEZONES.map(tz => ({ value: tz, label: tz })), user.timezone, { searchable: true })
                )}
            </div>
            <div class="settings-section">
                <h3>Sessions</h3>
                ${Components.infoBox('Default session timeout is 7 days. Use "Remember me" for persistent sessions.')}
                <button type="button" class="btn btn-warning btn-sm" onclick="Components.showToast('All sessions revoked (simulated)', 'success')" data-testid="revoke-sessions-btn">Revoke all sessions</button>
            </div>
            <div class="settings-section">
                <h3>Delete Account</h3>
                ${Components.warningBox('Deleting your account is permanent and cannot be undone. All your data will be removed.')}
                <button type="button" class="btn btn-danger btn-sm" onclick="Components.confirm('Delete account?', 'This action is permanent. All your data will be deleted.', () => Components.showToast('Account deletion simulated', 'info'), { danger: true, confirmLabel: 'Delete account' })" data-testid="delete-account-btn">Delete account</button>
            </div>
        `;
    },

    // ==========================
    // IMPORT
    // ==========================
    importPage() {
        Components.renderBreadcrumb([
            { label: 'Home', route: '/' },
            { label: 'Import', route: '/import' }
        ]);

        return `
            <div class="page-header">
                <h1 data-testid="page-title">Import & Migrate</h1>
                <p class="page-subtitle">Import projects and groups from other platforms or GitLab instances.</p>
            </div>
            ${Components.infoBox('After importing, you can use post-migration user mapping to match contributions to GitLab users.')}
            <div class="import-sources" data-testid="import-sources">
                ${IMPORT_SOURCES.map(s => `
                    <div class="import-source-card" data-testid="import-source-${s.id}" onclick="Views._showImportModal('${s.id}')">
                        <div class="import-source-icon">${s.icon}</div>
                        <div class="import-source-info">
                            <div class="import-source-name">${Components.escapeHtml(s.name)}</div>
                            <div class="import-source-desc">${Components.escapeHtml(s.description)}</div>
                            <div class="import-source-supports">
                                ${s.supportsGroups ? Components.badge('Groups', 'info') : ''}
                                ${s.supportsProjects ? Components.badge('Projects', 'info') : ''}
                            </div>
                        </div>
                        <div class="import-source-arrow">→</div>
                    </div>
                `).join('')}
            </div>

            <div class="settings-section" style="margin-top:32px">
                <h3>Import History</h3>
                <div class="import-history" data-testid="import-history">
                    <div class="member-list-header">
                        <span>Source</span><span>Project</span><span>Status</span><span>Date</span>
                    </div>
                    <div class="member-list-row">
                        <span>GitHub</span><span>acme-corp/legacy-monolith</span><span>${Components.badge('Completed', 'success')}</span><span>Mar 1, 2019</span>
                    </div>
                    <div class="member-list-row">
                        <span>Bitbucket Server</span><span>acme-corp/platform-engineering/infrastructure/aws-terraform-base</span><span>${Components.badge('Completed', 'success')}</span><span>Jul 10, 2021</span>
                    </div>
                    <div class="member-list-row">
                        <span>Repository URL</span><span>datastream/analytics-platform/data-pipeline</span><span>${Components.badge('Completed', 'success')}</span><span>Feb 15, 2023</span>
                    </div>
                </div>
            </div>
        `;
    },

    // ==========================
    // SETTINGS (GitLab.com info)
    // ==========================
    settings() {
        Components.renderBreadcrumb([
            { label: 'Home', route: '/' },
            { label: 'Settings', route: '/settings' }
        ]);

        const limits = GITLAB_COM_LIMITS;

        return `
            <div class="page-header">
                <h1 data-testid="page-title">GitLab.com Settings & Limits</h1>
                <p class="page-subtitle">Platform-wide settings, rate limits, and constraints for GitLab.com.</p>
            </div>

            <div class="settings-grid">
                <div class="settings-card" data-testid="repo-limits">
                    <h3>Repository & File Size Limits</h3>
                    <div class="settings-table">
                        ${Object.entries(limits.repository).map(([k, v]) => `
                            <div class="settings-row"><span class="settings-key">${k.replace(/([A-Z])/g, ' $1').replace(/^./, s => s.toUpperCase())}</span><span class="settings-value">${v}</span></div>
                        `).join('')}
                    </div>
                </div>

                <div class="settings-card" data-testid="rate-limits">
                    <h3>Rate Limits</h3>
                    <div class="settings-table">
                        ${Object.entries(limits.rateLimits).map(([k, v]) => `
                            <div class="settings-row"><span class="settings-key">${k.replace(/([A-Z])/g, ' $1').replace(/^./, s => s.toUpperCase())}</span><span class="settings-value">${v.limit} / ${v.period}</span></div>
                        `).join('')}
                    </div>
                </div>

                <div class="settings-card" data-testid="cicd-limits">
                    <h3>CI/CD Limits</h3>
                    <div class="settings-table">
                        ${Object.entries(limits.cicd).map(([k, v]) => `
                            <div class="settings-row"><span class="settings-key">${k.replace(/([A-Z])/g, ' $1').replace(/^./, s => s.toUpperCase())}</span><span class="settings-value">${v}</span></div>
                        `).join('')}
                    </div>
                </div>

                <div class="settings-card" data-testid="misc-settings">
                    <h3>Miscellaneous</h3>
                    <div class="settings-table">
                        ${Object.entries(limits.misc).map(([k, v]) => `
                            <div class="settings-row"><span class="settings-key">${k.replace(/([A-Z])/g, ' $1').replace(/^./, s => s.toUpperCase())}</span><span class="settings-value">${v}</span></div>
                        `).join('')}
                    </div>
                </div>
            </div>

            <div class="settings-section" style="margin-top:32px">
                <h3>Application Data</h3>
                <p class="text-muted">All changes are automatically saved to your browser's local storage. You can reset to the original seed data if needed.</p>
                <button class="btn btn-danger" id="resetDataBtn" data-testid="reset-data-btn">Reset all data to defaults</button>
            </div>
        `;
    },

    // ==========================
    // MODAL HELPERS
    // ==========================

    _showCreateGroupModal(parentId, orgId) {
        const parentGroup = parentId ? AppState.getGroupById(parentId) : null;
        const title = parentGroup ? `New subgroup in ${parentGroup.name}` : 'New group';

        const visOptions = [];
        visOptions.push({ value: 'private', label: 'Private', description: 'Only members can see this group' });
        if (AppState.isVisibilityAllowed('internal', parentId)) {
            visOptions.push({ value: 'internal', label: 'Internal', description: 'Any logged-in user can see this group' });
        }
        if (AppState.isVisibilityAllowed('public', parentId)) {
            visOptions.push({ value: 'public', label: 'Public', description: 'Anyone can see this group' });
        }

        const bodyHtml = `
            <form id="createGroupForm" data-testid="create-group-form">
                ${Components.formField('newGroupName', 'Group name', Components.textInput('newGroupName', '', { placeholder: 'My awesome group', maxlength: 255 }), { required: true })}
                ${Components.formField('newGroupPath', 'Group URL (slug)', Components.textInput('newGroupPath', '', { placeholder: 'my-awesome-group', maxlength: 255 }), { required: true, help: 'URL-safe identifier. Letters, digits, -, _ allowed.' })}
                ${Components.formField('newGroupDesc', 'Description', Components.textarea('newGroupDesc', '', { placeholder: 'Describe this group...', rows: 2 }))}
                ${Components.formField('newGroupVisibility', 'Visibility', Components.dropdown('newGroupVisibility', visOptions, 'private'))}
                ${parentGroup ? `<input type="hidden" id="newGroupParentId" value="${parentId}">` : ''}
                <div id="createGroupErrors" data-testid="create-group-errors"></div>
            </form>
        `;

        Components.showModal(title, bodyHtml,
            `<button class="btn btn-secondary" onclick="Components.closeModal()">Cancel</button>
             <button class="btn btn-primary" id="submitCreateGroup" data-testid="submit-create-group" disabled>Create group</button>`
        );

        // Auto-generate path from name
        const nameInput = document.getElementById('newGroupName');
        const pathInput = document.getElementById('newGroupPath');
        const submitBtn = document.getElementById('submitCreateGroup');
        const errorsDiv = document.getElementById('createGroupErrors');

        nameInput.addEventListener('input', () => {
            if (!pathInput._manuallyEdited) {
                pathInput.value = nameInput.value.toLowerCase().replace(/[^a-z0-9-]/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '');
            }
            Views._validateCreateGroupForm(submitBtn, errorsDiv);
        });

        pathInput.addEventListener('input', () => {
            pathInput._manuallyEdited = true;
            Views._validateCreateGroupForm(submitBtn, errorsDiv);
        });

        submitBtn.addEventListener('click', () => {
            const name = nameInput.value.trim();
            const path = pathInput.value.trim();
            const desc = document.getElementById('newGroupDesc').value.trim();
            const visibility = document.getElementById('newGroupVisibility').getAttribute('data-value');
            const parentIdVal = document.getElementById('newGroupParentId')?.value;

            const group = AppState.createGroup({
                name, path, description: desc, visibility,
                parentId: parentIdVal ? parseInt(parentIdVal) : null,
                organizationId: orgId || 1
            });

            Components.closeModal();
            Components.showToast(`Group "${name}" created successfully`, 'success');
            Router.navigate(`/groups/${group.id}`);
        });
    },

    _validateCreateGroupForm(submitBtn, errorsDiv) {
        const name = document.getElementById('newGroupName').value.trim();
        const path = document.getElementById('newGroupPath').value.trim();
        const nameErrors = AppState.validateName(name);
        const pathErrors = AppState.validatePath(path);
        const allErrors = [...nameErrors, ...pathErrors];

        errorsDiv.innerHTML = allErrors.length ? allErrors.map(e => `<div class="error-message">${Components.escapeHtml(e)}</div>`).join('') : '';
        submitBtn.disabled = allErrors.length > 0 || !name || !path;
        submitBtn.style.opacity = submitBtn.disabled ? '0.5' : '1';
        submitBtn.style.cursor = submitBtn.disabled ? 'not-allowed' : 'pointer';
    },

    _showCreateProjectModal(groupId) {
        const groups = AppState.groups.filter(g => !g.archived);
        const groupOptions = groups.map(g => ({ value: g.id, label: g.fullPath }));

        if (groupOptions.length === 0) {
            Components.showToast('No groups available. Create a group first.', 'warning');
            return;
        }

        const selectedGroup = groupId || groups[0].id;

        const bodyHtml = `
            <form id="createProjectForm" data-testid="create-project-form">
                ${Components.formField('projectGroup', 'Group', Components.dropdown('projectGroup', groupOptions, selectedGroup, { searchable: true }), { required: true })}
                ${Components.formField('newProjectName', 'Project name', Components.textInput('newProjectName', '', { placeholder: 'my-project', maxlength: 255 }), { required: true })}
                ${Components.formField('newProjectPath', 'Project slug', Components.textInput('newProjectPath', '', { placeholder: 'my-project', maxlength: 255 }), { required: true })}
                ${Components.formField('newProjectDesc', 'Description', Components.textarea('newProjectDesc', '', { placeholder: 'Describe this project...', rows: 2 }))}
                ${Components.formField('newProjectVisibility', 'Visibility', Components.dropdown('newProjectVisibility', [
                    { value: 'private', label: 'Private' },
                    { value: 'internal', label: 'Internal' },
                    { value: 'public', label: 'Public' }
                ], 'private'))}
                ${Components.formField('newProjectTopics', 'Topics', Components.textInput('newProjectTopics', '', { placeholder: 'Comma-separated topics' }))}
                <div id="createProjectErrors" data-testid="create-project-errors"></div>
            </form>
        `;

        Components.showModal('New project', bodyHtml,
            `<button class="btn btn-secondary" onclick="Components.closeModal()">Cancel</button>
             <button class="btn btn-primary" id="submitCreateProject" data-testid="submit-create-project" disabled>Create project</button>`
        );

        const nameInput = document.getElementById('newProjectName');
        const pathInput = document.getElementById('newProjectPath');
        const submitBtn = document.getElementById('submitCreateProject');
        const errorsDiv = document.getElementById('createProjectErrors');

        nameInput.addEventListener('input', () => {
            if (!pathInput._manuallyEdited) {
                pathInput.value = nameInput.value.toLowerCase().replace(/[^a-z0-9-]/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '');
            }
            Views._validateCreateProjectForm(submitBtn, errorsDiv);
        });

        pathInput.addEventListener('input', () => {
            pathInput._manuallyEdited = true;
            Views._validateCreateProjectForm(submitBtn, errorsDiv);
        });

        // Update visibility options when group changes
        document.getElementById('projectGroup').addEventListener('change', (e) => {
            const gId = parseInt(e.detail.value);
            const g = AppState.getGroupById(gId);
            if (g) {
                const visDropdown = document.getElementById('newProjectVisibility');
                // Constrain visibility
                const visOrder = { private: 0, internal: 1, public: 2 };
                const currentVis = visDropdown.getAttribute('data-value');
                if (visOrder[currentVis] > visOrder[g.visibility]) {
                    visDropdown.setAttribute('data-value', g.visibility);
                    visDropdown.querySelector('.dropdown-trigger-text').textContent = g.visibility.charAt(0).toUpperCase() + g.visibility.slice(1);
                }
            }
        });

        submitBtn.addEventListener('click', () => {
            const gId = parseInt(document.getElementById('projectGroup').getAttribute('data-value'));
            const name = nameInput.value.trim();
            const path = pathInput.value.trim();
            const desc = document.getElementById('newProjectDesc').value.trim();
            const visibility = document.getElementById('newProjectVisibility').getAttribute('data-value');
            const topics = document.getElementById('newProjectTopics').value.split(',').map(t => t.trim()).filter(t => t);

            const project = AppState.createProject({ name, path, description: desc, groupId: gId, visibility, topics });
            Components.closeModal();
            Components.showToast(`Project "${name}" created successfully`, 'success');
            Router.navigate(`/projects/${project.id}`);
        });
    },

    _validateCreateProjectForm(submitBtn, errorsDiv) {
        const name = document.getElementById('newProjectName').value.trim();
        const path = document.getElementById('newProjectPath').value.trim();
        const nameErrors = AppState.validateName(name, 'project');
        const pathErrors = path ? AppState.validatePath(path) : ['URL slug is required'];
        const allErrors = [...nameErrors, ...pathErrors];

        errorsDiv.innerHTML = allErrors.length ? allErrors.map(e => `<div class="error-message">${Components.escapeHtml(e)}</div>`).join('') : '';
        submitBtn.disabled = allErrors.length > 0;
        submitBtn.style.opacity = submitBtn.disabled ? '0.5' : '1';
        submitBtn.style.cursor = submitBtn.disabled ? 'not-allowed' : 'pointer';
    },

    _showAddMemberModal(entityType, entityId) {
        const existingMembers = entityType === 'group'
            ? AppState.getAllGroupMembers(entityId).map(m => m.userId)
            : AppState.getAllProjectMembers(entityId).map(m => m.userId);

        const availableUsers = AppState.users.filter(u => !existingMembers.includes(u.id));

        if (availableUsers.length === 0) {
            Components.showToast('All users are already members.', 'info');
            return;
        }

        const userOptions = availableUsers.map(u => ({
            value: u.id, label: `${u.name} (@${u.username})`
        }));

        const roleOptions = ROLES_LIST.filter(r => r.level <= ROLES.MAINTAINER.level).map(r => ({
            value: r.name, label: r.name
        }));

        const entityName = entityType === 'group'
            ? AppState.getGroupById(entityId)?.name
            : AppState.getProjectById(entityId)?.name;

        const bodyHtml = `
            <form id="addMemberForm" data-testid="add-member-form">
                ${Components.formField('memberUser', 'User', Components.dropdown('memberUser', userOptions, '', { placeholder: 'Select a user...', searchable: true }), { required: true })}
                ${Components.formField('memberRole', 'Role', Components.dropdown('memberRole', roleOptions, 'Guest'), { required: true })}
                ${Components.formField('memberExpiry', 'Access expiration date', Components.dateInput('memberExpiry', '', { placeholder: 'YYYY-MM-DD (optional)' }), { help: 'Leave empty for no expiration. Email notification sent 7 days before expiry.' })}
                <div id="addMemberErrors" data-testid="add-member-errors"></div>
            </form>
        `;

        Components.showModal(`Add member to ${entityName}`, bodyHtml,
            `<button class="btn btn-secondary" onclick="Components.closeModal()">Cancel</button>
             <button class="btn btn-primary" id="submitAddMember" data-testid="submit-add-member">Add member</button>`
        );

        document.getElementById('submitAddMember').addEventListener('click', () => {
            const userId = parseInt(document.getElementById('memberUser').getAttribute('data-value'));
            const roleName = document.getElementById('memberRole').getAttribute('data-value');
            const expiryValue = document.getElementById('memberExpiry').value.trim();
            const role = ROLES_LIST.find(r => r.name === roleName) || ROLES.GUEST;

            if (!userId) {
                document.getElementById('addMemberErrors').innerHTML = '<div class="error-message">Please select a user.</div>';
                return;
            }

            // Validate expiry date
            let expiresAt = null;
            if (expiryValue) {
                const d = new Date(expiryValue);
                if (isNaN(d.getTime())) {
                    document.getElementById('addMemberErrors').innerHTML = '<div class="error-message">Invalid date format. Use YYYY-MM-DD.</div>';
                    return;
                }
                if (d <= new Date()) {
                    document.getElementById('addMemberErrors').innerHTML = '<div class="error-message">Expiration date must be in the future.</div>';
                    return;
                }
                expiresAt = d.toISOString();
            }

            if (entityType === 'group') {
                AppState.addGroupMember(entityId, userId, role, expiresAt);
            } else {
                AppState.addProjectMember(entityId, userId, role, expiresAt);
            }

            const user = AppState.getUserById(userId);
            Components.closeModal();
            Components.showToast(`${user.name} added as ${role.name}`, 'success');
            Router.refresh();
        });
    },

    _showEditMemberModal(entityType, entityId, userId) {
        const membership = entityType === 'group'
            ? AppState.groupMemberships.find(m => m.groupId === entityId && m.userId === userId && m.membershipType === 'direct')
            : AppState.projectMemberships.find(m => m.projectId === entityId && m.userId === userId);

        if (!membership) return;
        const user = AppState.getUserById(userId);
        if (!user) return;

        // Check for inherited role that limits minimum
        let minRoleLevel = ROLES.GUEST.level;
        if (entityType === 'group') {
            const inherited = AppState.getInheritedGroupMembers(entityId).find(m => m.userId === userId);
            if (inherited) minRoleLevel = inherited.role.level;
        }

        const roleOptions = ROLES_LIST.filter(r => r.level >= minRoleLevel && r.level <= ROLES.OWNER.level).map(r => ({
            value: r.name, label: r.name,
            description: r.level < minRoleLevel ? 'Cannot be lower than inherited role' : ''
        }));

        const expiryValue = membership.expiresAt ? membership.expiresAt.split('T')[0] : '';

        const bodyHtml = `
            <form id="editMemberForm" data-testid="edit-member-form">
                <div class="member-edit-user">
                    ${Components.avatar(user, 32)}
                    <div><strong>${Components.escapeHtml(user.name)}</strong><br><span class="text-muted">@${Components.escapeHtml(user.username)}</span></div>
                </div>
                ${minRoleLevel > ROLES.GUEST.level ? Components.infoBox(`This user has an inherited role of ${ROLES_LIST.find(r => r.level === minRoleLevel)?.name || 'Unknown'}. The role cannot be set lower.`) : ''}
                ${Components.formField('editMemberRole', 'Role', Components.dropdown('editMemberRole', roleOptions, membership.role.name))}
                ${Components.formField('editMemberExpiry', 'Access expiration date', Components.dateInput('editMemberExpiry', expiryValue), { help: 'Leave empty for no expiration.' })}
                <div id="editMemberErrors" data-testid="edit-member-errors"></div>
            </form>
        `;

        Components.showModal(`Edit member: ${user.name}`, bodyHtml,
            `<button class="btn btn-secondary" onclick="Components.closeModal()">Cancel</button>
             <button class="btn btn-primary" id="submitEditMember" data-testid="submit-edit-member">Save changes</button>`
        );

        document.getElementById('submitEditMember').addEventListener('click', () => {
            const roleName = document.getElementById('editMemberRole').getAttribute('data-value');
            const expiryVal = document.getElementById('editMemberExpiry').value.trim();
            const role = ROLES_LIST.find(r => r.name === roleName) || membership.role;

            let expiresAt = null;
            if (expiryVal) {
                const d = new Date(expiryVal);
                if (isNaN(d.getTime())) {
                    document.getElementById('editMemberErrors').innerHTML = '<div class="error-message">Invalid date format.</div>';
                    return;
                }
                expiresAt = d.toISOString();
            }

            if (entityType === 'group') {
                AppState.updateGroupMemberRole(entityId, userId, role);
                AppState.updateGroupMemberExpiration(entityId, userId, expiresAt);
            } else {
                const pm = AppState.projectMemberships.find(m => m.projectId === entityId && m.userId === userId);
                if (pm) { pm.role = role; pm.expiresAt = expiresAt; }
            }

            Components.closeModal();
            Components.showToast(`Member updated`, 'success');
            Router.refresh();
        });
    },

    _confirmRemoveMember(entityType, entityId, userId) {
        const user = AppState.getUserById(userId);
        if (!user) return;

        Components.confirm(
            'Remove member?',
            `Are you sure you want to remove ${user.name} (@${user.username})? They will lose access immediately.`,
            () => {
                if (entityType === 'group') {
                    AppState.removeGroupMember(entityId, userId);
                } else {
                    AppState.removeProjectMember(entityId, userId);
                }
                Components.showToast(`${user.name} has been removed`, 'success');
                Router.refresh();
            },
            { danger: true, confirmLabel: 'Remove member' }
        );
    },

    _confirmDeleteGroup(groupId) {
        const group = AppState.getGroupById(groupId);
        if (!group) return;
        const descendants = AppState.getDescendantGroups(groupId);
        const projects = AppState.projects.filter(p => {
            const allGroupIds = [groupId, ...descendants.map(d => d.id)];
            return allGroupIds.includes(p.groupId);
        });

        Components.confirm(
            'Delete group?',
            `This will permanently delete "${group.name}" along with ${descendants.length} subgroup(s) and ${projects.length} project(s). On GitLab.com, deleted groups are removed after 30 days. This cannot be undone.`,
            () => {
                AppState.deleteGroup(groupId);
                Components.showToast(`Group "${group.name}" deleted (scheduled for removal)`, 'success');
                Router.navigate('/groups');
            },
            { danger: true, confirmLabel: 'Delete group' }
        );
    },

    _confirmDeleteProject(projectId) {
        const project = AppState.getProjectById(projectId);
        if (!project) return;

        Components.confirm(
            'Delete project?',
            `This will permanently delete "${project.name}". On GitLab.com, deleted projects are removed after 30 days. This cannot be undone.`,
            () => {
                AppState.deleteProject(projectId);
                Components.showToast(`Project "${project.name}" deleted`, 'success');
                Router.navigate('/projects');
            },
            { danger: true, confirmLabel: 'Delete project' }
        );
    },

    _confirmArchiveGroup(groupId) {
        const group = AppState.getGroupById(groupId);
        if (!group) return;
        Components.confirm(
            'Archive group?',
            `Archiving "${group.name}" will disable all modifications. Subgroups and projects are also affected.`,
            () => {
                AppState.updateGroup(groupId, { archived: true });
                Components.showToast(`Group "${group.name}" archived`, 'success');
                Router.refresh();
            },
            { confirmLabel: 'Archive group' }
        );
    },

    _unarchiveGroup(groupId) {
        AppState.updateGroup(groupId, { archived: false });
        Components.showToast('Group unarchived', 'success');
        Router.refresh();
    },

    _confirmRemoveGroupShare(sourceGroupId, targetGroupId) {
        const source = AppState.getGroupById(sourceGroupId);
        Components.confirm(
            'Remove shared group?',
            `This will revoke access for members of "${source?.name}" to this group.`,
            () => {
                AppState.removeGroupShare(sourceGroupId, targetGroupId);
                Components.showToast('Group sharing removed', 'success');
                Router.refresh();
            },
            { danger: true, confirmLabel: 'Remove' }
        );
    },

    _confirmRemoveProjectShare(sourceGroupId, targetProjectId) {
        const source = AppState.getGroupById(sourceGroupId);
        Components.confirm(
            'Remove shared group?',
            `This will revoke access for members of "${source?.name}" to this project.`,
            () => {
                AppState.removeProjectShare(sourceGroupId, targetProjectId);
                Components.showToast('Project sharing removed', 'success');
                Router.refresh();
            },
            { danger: true, confirmLabel: 'Remove' }
        );
    },

    _showShareGroupModal(targetGroupId) {
        const targetGroup = AppState.getGroupById(targetGroupId);
        if (!targetGroup) return;

        const existingShares = AppState.groupShares.filter(s => s.targetGroupId === targetGroupId).map(s => s.sourceGroupId);
        const availableGroups = AppState.groups.filter(g => g.id !== targetGroupId && !existingShares.includes(g.id) && !g.archived);

        if (availableGroups.length === 0) {
            Components.showToast('No groups available to share with.', 'info');
            return;
        }

        const groupOptions = availableGroups.map(g => ({ value: g.id, label: g.name }));
        const roleOptions = ROLES_LIST.filter(r => r.level <= ROLES.MAINTAINER.level).map(r => ({ value: r.name, label: r.name }));

        const bodyHtml = `
            <form id="shareGroupForm" data-testid="share-group-form">
                ${Components.formField('shareGroupSource', 'Invite group', Components.dropdown('shareGroupSource', groupOptions, '', { placeholder: 'Select a group...', searchable: true }), { required: true })}
                ${Components.formField('shareGroupMaxRole', 'Max role', Components.dropdown('shareGroupMaxRole', roleOptions, 'Guest'), { required: true, help: 'Members of the invited group will have at most this role.' })}
                ${Components.formField('shareGroupExpiry', 'Expiration date', Components.dateInput('shareGroupExpiry'), { help: 'Optional. Leave empty for no expiration.' })}
            </form>
        `;

        Components.showModal(`Invite a group to "${targetGroup.name}"`, bodyHtml,
            `<button class="btn btn-secondary" onclick="Components.closeModal()">Cancel</button>
             <button class="btn btn-primary" id="submitShareGroup" data-testid="submit-share-group">Invite group</button>`
        );

        document.getElementById('submitShareGroup').addEventListener('click', () => {
            const sourceId = parseInt(document.getElementById('shareGroupSource').getAttribute('data-value'));
            const roleName = document.getElementById('shareGroupMaxRole').getAttribute('data-value');
            const expiryVal = document.getElementById('shareGroupExpiry').value.trim();
            const role = ROLES_LIST.find(r => r.name === roleName) || ROLES.GUEST;

            if (!sourceId) {
                Components.showToast('Please select a group.', 'warning');
                return;
            }

            let expiresAt = null;
            if (expiryVal) {
                const d = new Date(expiryVal);
                if (!isNaN(d.getTime())) expiresAt = d.toISOString();
            }

            AppState.addGroupShare(sourceId, targetGroupId, role, expiresAt);
            const sourceGroup = AppState.getGroupById(sourceId);
            Components.closeModal();
            Components.showToast(`"${sourceGroup?.name}" invited with max role ${role.name}`, 'success');
            Router.refresh();
        });
    },

    _showShareProjectModal(targetProjectId) {
        const project = AppState.getProjectById(targetProjectId);
        if (!project) return;

        const existingShares = AppState.projectShares.filter(s => s.targetProjectId === targetProjectId).map(s => s.sourceGroupId);
        const availableGroups = AppState.groups.filter(g => !existingShares.includes(g.id) && !g.archived);

        if (availableGroups.length === 0) {
            Components.showToast('No groups available to share with.', 'info');
            return;
        }

        const groupOptions = availableGroups.map(g => ({ value: g.id, label: g.name }));
        const roleOptions = ROLES_LIST.filter(r => r.level <= ROLES.MAINTAINER.level).map(r => ({ value: r.name, label: r.name }));

        const bodyHtml = `
            <form id="shareProjectForm" data-testid="share-project-form">
                ${Components.formField('shareProjectSource', 'Invite group', Components.dropdown('shareProjectSource', groupOptions, '', { placeholder: 'Select a group...', searchable: true }), { required: true })}
                ${Components.formField('shareProjectMaxRole', 'Max role', Components.dropdown('shareProjectMaxRole', roleOptions, 'Guest'), { required: true })}
                ${Components.formField('shareProjectExpiry', 'Expiration date', Components.dateInput('shareProjectExpiry'), { help: 'Optional.' })}
            </form>
        `;

        Components.showModal(`Invite a group to "${project.name}"`, bodyHtml,
            `<button class="btn btn-secondary" onclick="Components.closeModal()">Cancel</button>
             <button class="btn btn-primary" id="submitShareProject" data-testid="submit-share-project">Invite group</button>`
        );

        document.getElementById('submitShareProject').addEventListener('click', () => {
            const sourceId = parseInt(document.getElementById('shareProjectSource').getAttribute('data-value'));
            const roleName = document.getElementById('shareProjectMaxRole').getAttribute('data-value');
            const expiryVal = document.getElementById('shareProjectExpiry').value.trim();
            const role = ROLES_LIST.find(r => r.name === roleName) || ROLES.GUEST;

            if (!sourceId) {
                Components.showToast('Please select a group.', 'warning');
                return;
            }

            let expiresAt = null;
            if (expiryVal) {
                const d = new Date(expiryVal);
                if (!isNaN(d.getTime())) expiresAt = d.toISOString();
            }

            AppState.addProjectShare(sourceId, targetProjectId, role, expiresAt);
            const sourceGroup = AppState.getGroupById(sourceId);
            Components.closeModal();
            Components.showToast(`"${sourceGroup?.name}" invited with max role ${role.name}`, 'success');
            Router.refresh();
        });
    },

    _showTransferGroupModal(groupId) {
        const group = AppState.getGroupById(groupId);
        if (!group) return;

        const availableTargets = [
            { value: 'top-level', label: 'Make top-level group (no parent)' },
            ...AppState.groups
                .filter(g => g.id !== groupId && !AppState.getDescendantGroups(groupId).some(d => d.id === g.id) && !g.archived)
                .map(g => ({ value: g.id, label: g.fullPath }))
        ];

        const bodyHtml = `
            <form id="transferGroupForm" data-testid="transfer-group-form">
                ${Components.warningBox('Transferring may change the group visibility if the new parent has more restrictive visibility.')}
                ${Components.formField('transferTarget', 'Transfer to', Components.dropdown('transferTarget', availableTargets, 'top-level', { searchable: true }), { required: true })}
            </form>
        `;

        Components.showModal(`Transfer "${group.name}"`, bodyHtml,
            `<button class="btn btn-secondary" onclick="Components.closeModal()">Cancel</button>
             <button class="btn btn-warning" id="submitTransferGroup" data-testid="submit-transfer-group">Transfer group</button>`
        );

        document.getElementById('submitTransferGroup').addEventListener('click', () => {
            const targetVal = document.getElementById('transferTarget').getAttribute('data-value');
            const newParentId = targetVal === 'top-level' ? null : parseInt(targetVal);

            if (newParentId) {
                const newParent = AppState.getGroupById(newParentId);
                const visOrder = { private: 0, internal: 1, public: 2 };
                if (newParent && visOrder[group.visibility] > visOrder[newParent.visibility]) {
                    AppState.updateGroup(groupId, { parentId: newParentId, visibility: newParent.visibility });
                    Components.showToast(`Group transferred. Visibility reduced to ${newParent.visibility}.`, 'warning');
                } else {
                    AppState.updateGroup(groupId, { parentId: newParentId });
                    Components.showToast('Group transferred successfully', 'success');
                }
            } else {
                AppState.updateGroup(groupId, { parentId: null });
                Components.showToast('Group is now a top-level group', 'success');
            }

            // Rebuild full paths
            Views._rebuildGroupPaths(groupId);
            Components.closeModal();
            Router.refresh();
        });
    },

    _rebuildGroupPaths(groupId) {
        const group = AppState.getGroupById(groupId);
        if (!group) return;
        const parent = group.parentId ? AppState.getGroupById(group.parentId) : null;
        const org = AppState.getOrgById(group.organizationId);
        const prefix = parent ? parent.fullPath : (org ? org.path : '');
        group.fullPath = prefix + '/' + group.path;

        // Rebuild children
        AppState.getChildGroups(groupId).forEach(child => Views._rebuildGroupPaths(child.id));

        // Rebuild project paths
        AppState.getProjectsForGroup(groupId).forEach(p => {
            p.fullPath = group.fullPath + '/' + p.path;
        });
    },

    _showImportModal(sourceId) {
        const source = IMPORT_SOURCES.find(s => s.id === sourceId);
        if (!source) return;

        let formFields = '';
        if (sourceId === 'repo_url') {
            formFields = `
                ${Components.formField('importUrl', 'Repository URL', Components.textInput('importUrl', '', { placeholder: 'https://github.com/user/repo.git' }), { required: true })}
            `;
        } else if (sourceId === 'gitlab') {
            formFields = `
                ${Components.formField('importFile', 'Export file', `<div class="file-upload-zone" id="fileUploadZone" data-testid="file-upload-zone"><p>Click or drag a .tar.gz export file here</p><input type="text" id="importFilePath" class="form-input" placeholder="Path to .tar.gz file" style="margin-top:8px"></div>`, { required: true })}
            `;
        } else if (sourceId === 'gitlab_direct') {
            formFields = `
                ${Components.formField('importGitlabUrl', 'Source GitLab URL', Components.textInput('importGitlabUrl', '', { placeholder: 'https://gitlab.example.com' }), { required: true })}
                ${Components.formField('importGitlabToken', 'Personal access token', Components.textInput('importGitlabToken', '', { placeholder: 'glpat-xxxxxxxxxxxxxxxxxxxx' }), { required: true })}
            `;
        } else if (sourceId === 'github') {
            formFields = `
                ${Components.formField('importGithubToken', 'GitHub personal access token', Components.textInput('importGithubToken', '', { placeholder: 'ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' }), { required: true })}
            `;
        } else {
            formFields = `
                ${Components.formField('importServerUrl', 'Server URL', Components.textInput('importServerUrl', '', { placeholder: 'https://bitbucket.example.com' }), { required: true })}
                ${Components.formField('importToken', 'Access token / password', Components.textInput('importToken', ''), { required: true })}
            `;
        }

        const groups = AppState.groups.filter(g => !g.archived);
        const groupOptions = groups.map(g => ({ value: g.id, label: g.fullPath }));

        const bodyHtml = `
            <form id="importForm" data-testid="import-form">
                <div class="import-source-header">
                    <span class="import-source-icon-lg">${source.icon}</span>
                    <h3>${Components.escapeHtml(source.name)}</h3>
                </div>
                <p class="text-muted">${Components.escapeHtml(source.description)}</p>
                <div class="import-supports">
                    ${source.supportsGroups ? Components.badge('Supports groups', 'info') : ''}
                    ${source.supportsProjects ? Components.badge('Supports projects', 'info') : ''}
                </div>
                <hr>
                ${formFields}
                ${Components.formField('importTargetGroup', 'Import into group', Components.dropdown('importTargetGroup', groupOptions, groupOptions[0]?.value || '', { searchable: true }), { required: true })}
            </form>
        `;

        Components.showModal(`Import from ${source.name}`, bodyHtml,
            `<button class="btn btn-secondary" onclick="Components.closeModal()">Cancel</button>
             <button class="btn btn-primary" id="submitImport" data-testid="submit-import">Start import</button>`,
            { wide: true }
        );

        document.getElementById('submitImport').addEventListener('click', () => {
            Components.closeModal();
            Components.showToast(`Import from ${source.name} started (simulated). Check import history for progress.`, 'info');
        });
    },

    _removeEmail(email) {
        const user = AppState.currentUser;
        user.secondaryEmails = user.secondaryEmails.filter(e => e !== email);
        // Also update in users array
        const u = AppState.getUserById(user.id);
        if (u) u.secondaryEmails = user.secondaryEmails;
        Components.showToast(`Email ${email} removed`, 'success');
        AppState.notify();
        Router.refresh();
    },

    _toggle2FA() {
        AppState.currentUser.twoFactorEnabled = !AppState.currentUser.twoFactorEnabled;
        const u = AppState.getUserById(AppState.currentUser.id);
        if (u) u.twoFactorEnabled = AppState.currentUser.twoFactorEnabled;
        Components.showToast(`Two-factor authentication ${AppState.currentUser.twoFactorEnabled ? 'enabled' : 'disabled'} (simulated)`, 'success');
        AppState.notify();
        Router.refresh();
    },

    _getTopLevelGroup(group) {
        let current = group;
        while (current.parentId) {
            current = AppState.getGroupById(current.parentId) || current;
            if (!current.parentId) break;
        }
        return current;
    },

    _notFound(message) {
        return `
            <div class="page-header">
                <h1 data-testid="page-title">Not Found</h1>
                <p class="page-subtitle">${Components.escapeHtml(message)}</p>
                <button class="btn btn-primary" onclick="Router.navigate('/')">Go home</button>
            </div>
        `;
    }
};
