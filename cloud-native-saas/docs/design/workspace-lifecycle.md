# Workspace Lifecycle

## **SaaS Tenant Agent Lifecycle**

### **Phase 0 — Bootstrap / Initial Reconciliation**

**When:** First timer run after the tenant agent is installed.

**Steps:**

1. Poll the SaaS control plane for workspace configuration.
2. Compute **desired state**:

   * Workspace metadata (name, namespace, labels, etc.)
   * Enabled apps/addons list
   * Parameters for each app
3. Create **Workspace CR** in Kubernetes.
4. For each app in the desired list:

   * Create **WorkspaceApplication CR**
   * Trigger KubeVela addon deployment
5. Mark hashes/digests of CR specs for future delta comparison.

**Key Notes:**

* Idempotent: repeated bootstrap should not create duplicates.
* All initial CRs are considered **canonical source**.

### **Phase 1 — Incremental Updates**

**When:** Timer polls periodically (day 2, day 3, …).

**Steps:**

1. Poll SaaS for workspace configuration.
2. Compute desired state hashes for apps.
3. Fetch existing WorkspaceApplication CRs for this workspace.
4. Compare:

   * **New apps:** create CRs and deploy addons.
   * **Changed apps:** update CRs → triggers redeploy/reconfigure in KubeVela.
   * **Removed apps:** either delete CRs or soft-delete (set `enabled: false`) depending on policy.
5. Optional: update Workspace CR metadata if any workspace-level fields changed.

**Key Notes:**

* Use hash comparison to avoid unnecessary updates.
* Respect soft-delete flag if enabled.
* Should be idempotent and safe to rerun if previous operations partially failed.

### **Phase 2 — Soft Delete / Disable**

**When:** SaaS marks an app as `enabled: false` instead of removing it entirely.

**Steps:**

1. Detect the app in desired state but with `enabled: false`.
2. Update WorkspaceApplication CR with `enabled: false`.
3. KubeVela addon may be scaled down / paused instead of fully deleted (optional behavior).
4. Retain CR in cluster for future reactivation.

**Key Notes:**

* Useful if SaaS user wants to temporarily disable a feature.
* Avoids full redeploy on re-enable.

### **Phase 3 — Workspace Deletion**

**When:** SaaS workspace is removed entirely.

**Steps:**

1. Detect workspace no longer exists in SaaS.
2. Delete all WorkspaceApplication CRs.

   * Triggers KubeVela to delete corresponding addons.
3. Delete Workspace CR.

**Key Notes:**

* Should be done carefully; consider a “finalizer” pattern to ensure all CRs are cleaned.
* Optional: retain backup metadata before deletion if required.

### **Phase 4 — Edge / Recovery Handling**

* Partial failure in update → keep delta comparison for next timer run.
* Manual CR edits in cluster → agent may overwrite if not explicitly excluded.
* Handle SaaS API downtime gracefully → retry timer next run.

### **High-level Summary Table**

| Phase | Trigger | Action | CR Behavior |
| --- | --- | --- | --- |
| 0 Bootstrap          | First run            | Create Workspace & App CRs | Deploy addons                     |
| 1 Incremental update | Timer run            | Diff desired vs existing   | Create/update/delete apps         |
| 2 Soft-delete        | App disabled in SaaS | Update `enabled: false`    | Retain CR, optionally pause addon |
| 3 Workspace deletion | Workspace removed    | Delete Workspace & app CRs | Delete addons                     |
| 4 Recovery           | Errors / partial ops | Retry next timer           | Idempotent operations             |
