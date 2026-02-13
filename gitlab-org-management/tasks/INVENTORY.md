# Task Inventory

Detailed reference for all 24 evaluation tasks in the GitLab organization management benchmark. For general design principles, see [../EVAL.md](../EVAL.md).

## Current User

All tasks execute as **Alex Morgan** (`alex.morgan`, id=1). Key seed-data roles:

| Group | Role | Notes |
|-------|------|-------|
| Platform Engineering (id=1) | Owner | Grants inherited access to all subgroups (Infrastructure, CI/CD, Observability, Terraform Modules) |
| Product Development (id=2) | Owner | Grants inherited access to Web Application, Mobile, API Services |
| Open Source (id=3) | Owner | |
| Security (id=4) | Owner | |
| Archived Projects (id=5) | Owner | Required for E2 (delete project) and E6 (unarchive) |
| DataStream Analytics (id=14) | Developer | Expires 2025-12-31 |

## Workflow Coverage

| Workflow | Tasks | Count |
|----------|-------|-------|
| Group creation | E1, M6, H2 | 3 |
| Group settings | M7, H6 | 2 |
| Group archive/unarchive | E6 | 1 |
| Group sharing (invite) | M4 | 1 |
| Group share revocation | M8 | 1 |
| Project creation | M1, H1 | 2 |
| Project settings | H8 | 1 |
| Project deletion | E2 | 1 |
| Project sharing (invite) | H1, H7 | 2 |
| Member addition (group) | M2, H2, H5 | 3 |
| Member role change (group) | M3 | 1 |
| Member removal (group) | M5 | 1 |
| Member addition (project) | H3 | 1 |
| Member removal (project) | H3 | 1 |
| Profile editing | E3, E8, H4 | 3 |
| Account settings (username) | H4 | 1 |
| Account settings (2FA) | E5 | 1 |
| Email management | E4, E7 | 2 |
| Cross-org operations | H7 | 1 |
| Deep navigation (3+ levels) | M3, H5 | 2 |
| Custom date picker | H5, H7 | 2 |

## Verification Patterns by Task

| Pattern | Tasks | Description |
|---------|-------|-------------|
| Entity existence (by name) | E1, M1, M6, H1, H2 | Search by name/path, not by ID (IDs are auto-incremented) |
| Entity absence | E2, M5, M8 | Confirm deletion or removal succeeded |
| Property match | E3, E5, E8, M7, H6, H8 | Check specific field values after update |
| Side effect check | E1, E2, M6 | E.g., creating a group also creates an Owner membership |
| Membership with constraints | M2, H5 | Check role, membership type, and optional expiry date |
| Relationship check | M1, M4, M6, H1, H7 | Verify parent-child or share relationships between entities |
| Multi-condition | H3, H4, H6, H8 | Multiple independent checks must all pass |
| State sync | E3, E5, H4 | Verify both `currentUser` and `users[]` array are consistent |

## App-Specific Notes

### Role serialization

In this app, roles are stored as objects (`ROLES.OWNER = {id: 50, name: "Owner", level: 50, ...}`). When `AppState` is serialized via `GET /api/state`, roles remain as objects. All verifiers use `membership.get("role", {}).get("name")` (not `== "string"`). This affected E1, M2, M3, M4, M6, H1, H2, H3, H5, H7.

### State persistence (`AppState.notify`)

The app uses SSE + a `PUT /api/state` pattern. Handlers that directly mutate `currentUser` properties (toggle 2FA, remove email, add email, change username) must call `AppState.notify()` before `Router.refresh()` so the server has the updated state when verifiers call `GET /api/state`. This affected E4, E5, E7, H4.

### Verifier field names

Group settings use `subgroupCreationLevel` and `projectCreationLevel` (not `subgroupCreation`/`projectCreation`). The verifier for H6 was fixed to use the correct names.

### "No one" dropdown option

The H6 verifier expects `projectCreationLevel == "noone"`, so the project creation dropdown in `views.js` includes `{value: 'noone', label: 'No one'}`.

### Share dropdown labels

The invite-group dropdowns in `_showShareGroupModal` and `_showShareProjectModal` use `g.name` (human-readable, e.g., "Analytics Platform") as labels, not `g.fullPath` (path with hyphens, e.g., "datastream/analytics-platform"). This ensures the dropdown search matches task instruction language. All group names are unique in the seed data. This affected H7.

---

## Easy Tasks (E1–E8)

### E1 — Create group 'DevOps Team'

| | |
|---|---|
| **Instruction** | Create a new group called 'DevOps Team' with public visibility. |
| **Workflow** | Group creation |
| **Navigation** | Sidebar → Groups → New Group |
| **Verifier** | `task_e1.py` |
| **Checks** | (1) Group named "DevOps Team" exists; (2) visibility is `public`; (3) user 1 is Owner of new group |
| **Entities** | New group (auto-ID) |
| **Preconditions** | None |

### E2 — Delete project 'legacy-monolith'

| | |
|---|---|
| **Instruction** | Delete the project 'legacy-monolith'. |
| **Workflow** | Project deletion |
| **Navigation** | Navigate to project → Settings tab → Delete button → confirm |
| **Verifier** | `task_e2.py` |
| **Checks** | Project named "legacy-monolith" no longer exists in state |
| **Entities** | Project: legacy-monolith (id=19, group=Archived Projects id=5) |
| **Preconditions** | User must be Owner of Archived Projects group (id=5). Seed data grants this. |

### E3 — Change bio

| | |
|---|---|
| **Instruction** | Change your bio to 'Full-stack developer with 10 years of experience'. |
| **Workflow** | Profile editing |
| **Navigation** | Sidebar → Profile → edit bio field → Save |
| **Verifier** | `task_e3.py` |
| **Checks** | `currentUser.bio` and matching entry in `users[]` both equal the target string |
| **Entities** | Current user profile |
| **Preconditions** | None |

### E4 — Add secondary email

| | |
|---|---|
| **Instruction** | Add 'alex.backup@gmail.com' as a secondary email address to your account. |
| **Workflow** | Email management |
| **Navigation** | Profile → Emails tab → type email → Add button |
| **Verifier** | `task_e4.py` |
| **Checks** | `alex.backup@gmail.com` exists in `currentUser.secondaryEmails` |
| **Entities** | Current user profile |
| **Preconditions** | None |

### E5 — Turn off 2FA

| | |
|---|---|
| **Instruction** | Turn off two-factor authentication on your account. |
| **Workflow** | Account settings |
| **Navigation** | Profile → Account tab → 2FA toggle |
| **Verifier** | `task_e5.py` |
| **Checks** | `currentUser.twoFactorEnabled` is `false`; consistent in `users[]` |
| **Entities** | Current user profile (seed: `twoFactorEnabled: true`) |
| **Preconditions** | None |

### E6 — Unarchive 'Archived Projects'

| | |
|---|---|
| **Instruction** | Unarchive the 'Archived Projects' group. |
| **Workflow** | Group archive toggle |
| **Navigation** | Navigate to Archived Projects group → Settings → Unarchive button |
| **Verifier** | `task_e6.py` |
| **Checks** | Group id=5 has `archived: false` |
| **Entities** | Group: Archived Projects (id=5) |
| **Preconditions** | User must be Owner of group 5. Seed data grants this. |

### E7 — Remove secondary email

| | |
|---|---|
| **Instruction** | Remove your secondary email 'alex.personal@email.com'. |
| **Workflow** | Email management |
| **Navigation** | Profile → Emails tab → remove button next to the email |
| **Verifier** | `task_e7.py` |
| **Checks** | `alex.personal@email.com` is absent from `currentUser.secondaryEmails` |
| **Entities** | Current user profile (seed: `secondaryEmails: ['alex.personal@email.com']`) |
| **Preconditions** | Seed data email must match instruction exactly. |

### E8 — Set status to 'On vacation' + busy

| | |
|---|---|
| **Instruction** | Set your current status message to 'On vacation' and mark yourself as busy. |
| **Workflow** | Profile status editing |
| **Navigation** | Profile → edit status fields → Save |
| **Verifier** | `task_e8.py` |
| **Checks** | `currentUser.status.message == "On vacation"` and `currentUser.status.busy == true` |
| **Entities** | Current user profile |
| **Preconditions** | None |

---

## Medium Tasks (M1–M8)

### M1 — Create project 'monitoring-service' in Observability

| | |
|---|---|
| **Instruction** | Create a new project called 'monitoring-service' in the 'Observability' group. |
| **Workflow** | Project creation |
| **Navigation** | Platform Engineering → Observability → New Project |
| **Verifier** | `task_m1.py` |
| **Checks** | Project "monitoring-service" exists with `groupId == 8` |
| **Entities** | Group: Observability (id=8, parent=Platform Engineering id=1) |
| **Preconditions** | User is Owner of Platform Engineering, inherited into Observability. `projectCreationLevel: 'developer'` — sufficient. |

### M2 — Add Emma Wilson as Developer to CI/CD

| | |
|---|---|
| **Instruction** | Add Emma Wilson as a Developer to the 'CI/CD' group. |
| **Workflow** | Member addition |
| **Navigation** | Platform Engineering → CI/CD → Members tab → Add member modal |
| **Verifier** | `task_m2.py` |
| **Checks** | Emma Wilson (id=6) has direct membership in group 7 with `role.name == "Developer"` |
| **Entities** | User: Emma Wilson (id=6); Group: CI/CD (id=7, parent=Platform Engineering id=1) |
| **Preconditions** | User is Owner of Platform Engineering (inherited into CI/CD). Emma Wilson must NOT be an existing member (direct or inherited) of CI/CD. She is a member of Product Development (id=2) and Web Application (id=9) — neither is an ancestor of CI/CD. |

### M3 — Change James Chen's role in Terraform Modules to Owner

| | |
|---|---|
| **Instruction** | Change James Chen's role in the 'Terraform Modules' group from Maintainer to Owner. |
| **Workflow** | Member role change |
| **Navigation** | Platform Engineering → Infrastructure → Terraform Modules → Members → edit role |
| **Verifier** | `task_m3.py` |
| **Checks** | James Chen (id=3) membership in group 12 has `role.name == "Owner"` |
| **Entities** | User: James Chen (id=3); Group: Terraform Modules (id=12, parent=Infrastructure id=6) |
| **Preconditions** | User is Owner of Platform Engineering (inherited through Infrastructure into Terraform Modules). James Chen has direct Maintainer membership in group 12. |

### M4 — Invite Open Source group to Product Development

| | |
|---|---|
| **Instruction** | Invite the 'Open Source' group to the 'Product Development' group with a maximum role of Reporter. |
| **Workflow** | Group sharing (invite) |
| **Navigation** | Product Development → Sharing tab → Invite group modal |
| **Verifier** | `task_m4.py` |
| **Checks** | `groupShares` entry with `sourceGroupId=3, targetGroupId=2, maxRole.name == "Reporter"` |
| **Entities** | Source: Open Source (id=3); Target: Product Development (id=2) |
| **Preconditions** | User must be Owner of Product Development (id=2). Seed data grants Owner role. |

### M5 — Remove Maria Rodriguez from Product Development

| | |
|---|---|
| **Instruction** | Remove Maria Rodriguez from the 'Product Development' group. |
| **Workflow** | Member removal |
| **Navigation** | Product Development → Members tab → find Maria → remove |
| **Verifier** | `task_m5.py` |
| **Checks** | No membership for user 4 in group 2 |
| **Entities** | User: Maria Rodriguez (id=4); Group: Product Development (id=2) |
| **Preconditions** | Maria has direct Developer membership in group 2 (with expiry). |

### M6 — Create subgroup 'Performance Testing' under Web Application

| | |
|---|---|
| **Instruction** | Create a subgroup called 'Performance Testing' under the 'Web Application' group. |
| **Workflow** | Subgroup creation |
| **Navigation** | Product Development → Web Application → New Subgroup |
| **Verifier** | `task_m6.py` |
| **Checks** | (1) Group "Performance Testing" exists with `parentId == 9`; (2) user 1 is Owner of new group |
| **Entities** | Parent: Web Application (id=9, parent=Product Development id=2) |
| **Preconditions** | User is Owner of Product Development (inherited into Web Application). |

### M7 — Update Platform Engineering settings

| | |
|---|---|
| **Instruction** | Update the Platform Engineering group: change its description to 'Core infrastructure and platform services' and enable 'Require two-factor authentication'. |
| **Workflow** | Group settings (multi-field) |
| **Navigation** | Platform Engineering → Settings tab → edit fields → Save |
| **Verifier** | `task_m7.py` |
| **Checks** | Group 1: `description == "Core infrastructure and platform services"` and `requireTwoFactor == true` |
| **Entities** | Group: Platform Engineering (id=1) |
| **Preconditions** | User is Owner of group 1. |

### M8 — Revoke Security's access to Platform Engineering

| | |
|---|---|
| **Instruction** | Revoke the 'Security' group's access to 'Platform Engineering'. |
| **Workflow** | Share revocation |
| **Navigation** | Platform Engineering → Sharing tab → remove Security share |
| **Verifier** | `task_m8.py` |
| **Checks** | No `groupShares` entry with `sourceGroupId=4, targetGroupId=1` |
| **Entities** | Source: Security (id=4); Target: Platform Engineering (id=1) |
| **Preconditions** | Seed data has share: Security → Platform Engineering (Reporter). |
| **Notes** | **Trick task**: The agent must understand that Security is shared *into* Platform Engineering, so the revocation happens from Platform Engineering's Sharing tab (not Security's). |

---

## Hard Tasks — Multi-step (H1–H4)

### H1 — Create 'community-tools' project and share with Product Development

| | |
|---|---|
| **Instruction** | Create a new public project called 'community-tools' in the 'Open Source' group, then share it with the 'Product Development' group with Developer access. |
| **Workflows** | Project creation + project sharing |
| **Navigation** | Open Source → New Project → (create) → new project → Sharing tab → invite group |
| **Verifier** | `task_h1.py` |
| **Checks** | (1) Project "community-tools" exists in group 3 with `visibility == "public"`; (2) `projectShares` entry with `sourceGroupId=2, targetProjectId=<new>, maxRole.name == "Developer"` |
| **Entities** | Group: Open Source (id=3); Group: Product Development (id=2) |
| **Preconditions** | User is Owner of Open Source (id=3). |

### H2 — Create 'Threat Intelligence' subgroup and add Priya Sharma

| | |
|---|---|
| **Instruction** | Create a new subgroup called 'Threat Intelligence' under the 'Security' group, then add Priya Sharma as a Developer to the new subgroup. |
| **Workflows** | Subgroup creation + member addition |
| **Navigation** | Security → New Subgroup → (create) → new subgroup → Members tab → add member |
| **Verifier** | `task_h2.py` |
| **Checks** | (1) Group "Threat Intelligence" exists with `parentId == 4`; (2) Priya Sharma (id=2) is direct member with `role.name == "Developer"` |
| **Entities** | Parent: Security (id=4); User: Priya Sharma (id=2) |
| **Preconditions** | User is Owner of Security. Security has `preventInvitations: true` (info banner only, doesn't block adding members). |

### H3 — Remove Liam, add Sofia to web-frontend

| | |
|---|---|
| **Instruction** | Remove Liam O'Shea from the 'web-frontend' project and add Sofia Petrov as a Developer to the same project. |
| **Workflows** | Member removal + member addition |
| **Navigation** | Product Development → Web Application → web-frontend → Members tab → remove Liam → add Sofia |
| **Verifier** | `task_h3.py` |
| **Checks** | (1) No `projectMemberships` entry for user 7 in project 6; (2) Sofia (id=9) has direct membership in project 6 with `role.name == "Developer"` |
| **Entities** | Project: web-frontend (id=6, group=Web Application id=9); Users: Liam O'Shea (id=7), Sofia Petrov (id=9) |
| **Preconditions** | User is Owner of Product Development (inherited into Web Application and web-frontend). Liam has direct Reporter membership in project 6. |

### H4 — Change username and display name

| | |
|---|---|
| **Instruction** | Change your username to 'alex.m' and update your display name to 'Alex M.'. |
| **Workflows** | Account settings (username) + Profile editing (name) |
| **Navigation** | Profile → Account tab → change username (with confirm dialog) → Profile tab → change name → Save |
| **Verifier** | `task_h4.py` |
| **Checks** | `currentUser.username == "alex.m"` and `currentUser.name == "Alex M."`; consistent in `users[]` |
| **Entities** | Current user profile |
| **Preconditions** | None |
| **Notes** | Username change requires a confirmation dialog. |

---

## Hard Tasks — Deep-constraint (H5–H8)

### H5 — Add Omar Hassan to Terraform Modules with expiry

| | |
|---|---|
| **Instruction** | Add Omar Hassan as a member of the 'Terraform Modules' group with the Maintainer role and set the membership to expire on 2027-12-31. |
| **Workflow** | Member addition with expiry |
| **Navigation** | Platform Engineering → Infrastructure → Terraform Modules → Members → Add member (with date picker) |
| **Verifier** | `task_h5.py` |
| **Checks** | Omar Hassan (id=5) has direct membership in group 12 with `role.name == "Maintainer"` and `expiresAt` containing `"2027-12-31"` |
| **Entities** | User: Omar Hassan (id=5); Group: Terraform Modules (id=12) |
| **Preconditions** | User is Owner of Platform Engineering (inherited through Infrastructure into Terraform Modules). Omar is not a current member of group 12 or any ancestor. |
| **Notes** | 3 levels deep navigation. Custom date picker (non-native, YYYY-MM-DD). |

### H6 — Multi-field settings update on Observability

| | |
|---|---|
| **Instruction** | In the 'Observability' group, change the name to 'Monitoring & Observability', set subgroup creation to 'Owners only', project creation to 'No one', and enable the 'Disable group mentions' option. |
| **Workflow** | Group settings (4 fields) |
| **Navigation** | Platform Engineering → Observability → Settings → edit 4 fields → Save |
| **Verifier** | `task_h6.py` |
| **Checks** | Group 8: `name == "Monitoring & Observability"`, `subgroupCreationLevel == "owner"`, `projectCreationLevel == "noone"`, `disableMentions == true` |
| **Entities** | Group: Observability (id=8, parent=Platform Engineering id=1) |
| **Preconditions** | User is Owner of Platform Engineering (inherited into Observability). |
| **Notes** | The "No one" option (`value: 'noone'`) must exist in the project creation dropdown. The checkbox label is "Disable group mentions" (not "email mentions"). The verifier uses `subgroupCreationLevel` and `projectCreationLevel` (the `AppState` property names). |

### H7 — Cross-org project sharing with expiry

| | |
|---|---|
| **Instruction** | Invite the 'Analytics Platform' group to the 'design-system' project with Reporter access and an expiration date of 2027-06-15. |
| **Workflow** | Project sharing (cross-organization) |
| **Navigation** | Open Source → design-system → Sharing tab → invite group (with date picker) |
| **Verifier** | `task_h7.py` |
| **Checks** | `projectShares` entry with `sourceGroupId=14, targetProjectId=14, maxRole.name == "Reporter"`, `expiresAt` containing `"2027-06-15"` |
| **Entities** | Source: Analytics Platform (id=14, org=DataStream); Target: design-system (project id=14, group=Open Source id=3) |
| **Preconditions** | User is Owner of Open Source (owns design-system's parent group). |
| **Notes** | Cross-organization sharing. Analytics Platform is in DataStream GmbH, design-system is in Acme Corp. Custom date picker. |

### H8 — Multi-field project settings update on web-frontend

| | |
|---|---|
| **Instruction** | On the 'web-frontend' project, update the settings: change the project name to 'web-app-frontend', set the description to 'Main customer-facing web application', set the topics to 'react', 'vue', 'frontend', and change the visibility to 'private'. |
| **Workflow** | Project settings (4 fields) |
| **Navigation** | Product Development → Web Application → web-frontend → Settings tab → edit fields → Save |
| **Verifier** | `task_h8.py` |
| **Checks** | Project 6: `name == "web-app-frontend"`, `description == "Main customer-facing web application"`, `topics == ["react", "vue", "frontend"]`, `visibility == "private"` |
| **Entities** | Project: web-frontend (id=6, group=Web Application id=9, parent=Product Development id=2) |
| **Preconditions** | User must be Owner of Product Development (id=2). Seed data grants Owner role. |
| **Notes** | Topics are comma-separated text input (current: `['react', 'typescript', 'frontend']` → replace 'typescript' with 'vue'). Visibility change from `internal` to `private` is valid (more restrictive). |
