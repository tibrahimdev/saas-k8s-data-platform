# **SaaS Tenant Agent Lifecycle Blueprint**

## **1. Day 0 — Bootstrap**

* 1.1 Bootstrap script creates:
   - CRDs
   - Workspace CR: name, bootstrapToken

* 1.2 **Poll SaaS workspace config** → get list of apps/addons + workspace metadata.
* 1.3 **For each app in desired list**:

  * 1.3.1 Create **WorkspaceApplication CR**
  * 1.3.2 Trigger KubeVela addon deployment.

* 1.4 **Mark state/digest** of CR specs for future delta detection.
* 1.5 **Result:** Workspace fully represented in K8s, all desired apps deployed.

**Visual state:**

```
Workspace CR -> exists
App1 CR -> deployed
App2 CR -> deployed
App3 CR -> deployed
```

## **Day 1–N — Incremental Updates**

* **Poll SaaS workspace config** → compute desired state.
* **Compare with existing CRs** using digest/hash:

  * **New apps** → create CR + deploy addon.
  * **Updated apps** → update CR → triggers redeploy.
  * **Removed apps**:

    * Delete CR → triggers addon deletion **OR**
    * Soft-delete (`enabled: false`) → pause without deleting.
* **Update Workspace CR metadata** if workspace-level fields changed.

**Visual state example:**

* App2 config changed → updated
* App4 added → new CR + deployed
* App3 removed → soft-deleted or deleted

```
Workspace CR -> exists
App1 CR -> unchanged
App2 CR -> updated
App3 CR -> soft-deleted
App4 CR -> deployed
```

## **Soft-delete / Disable apps**

* **SaaS marks app as `enabled: false`**
* Agent updates CR with `enabled: false`
* KubeVela addon may scale down / pause
* Retain CR in cluster for reactivation

**Visual state:**

```
App3 CR -> enabled: false (paused)
```

## **Workspace Deletion**

* **SaaS removes workspace**
* Agent detects workspace no longer exists
* Delete all WorkspaceApplication CRs → triggers addon deletion
* Delete Workspace CR

**Visual state:**

```
Workspace CR -> deleted
All App CRs -> deleted
```

## **Edge/Recovery**

* **Partial failure / network issues** → retry in next poll
* **Manual edits in cluster** → agent can overwrite unless explicitly excluded
* **SaaS API downtime** → agent waits for next timer run

## **Optional Enhancements**

1. **Delta cache** → keep hash of last applied state to avoid unnecessary updates.
2. **Batch CR operations** → reduce K8s API calls.
3. **Finalizers** → ensure complete cleanup on workspace deletion.
4. **Soft-delete history** → retain metadata for auditing or quick rollback.
