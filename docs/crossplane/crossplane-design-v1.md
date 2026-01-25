# Design

> **Do NOT let apps directly choose `CloudNativePG` vs `RDS`**
> **DO introduce a Database abstraction XR and let WorkspaceApp bind to it**


## The core principle (important)

Apps should say **what they need**, not **how it’s implemented**.

Exactly like:

* Apps don’t choose Helm
* Apps shouldn’t choose PostgreSQL operators either


## The correct abstraction stack

```
Workspace
  └─ environment, namespace

Database (XR)                ← infra abstraction
  ├─ postgres
  ├─ mysql
  └─ ...

WorkspaceApp (XR)            ← app abstraction
  └─ binds to Database
```

CloudNativePG and RDS live **behind** the Database XR.


## What users should write (clean API)

### 1️⃣ Database XR (infra team / advanced users)

```yaml
apiVersion: platform.saas.test/v1alpha1
kind: Database
metadata:
  name: jupyterhub-db
spec:
  engine: postgres
  size: small
  highAvailability: true
```

No mention of:

* CNPG
* RDS
* operators
* cloud vendors


### 2️⃣ WorkspaceApp references it

```yaml
apiVersion: platform.saas.test/v1alpha1
kind: WorkspaceApp
metadata:
  name: jupyterhub
spec:
  workspaceRef:
    name: saas-workspace

  app:
    type: jupyterhub

  databaseRef:
    name: jupyterhub-db
```

That’s it.


## How choice actually happens (where flexibility lives)

### Option A (recommended): **CompositionSelector on Database**

The **Database XR** selects its implementation:

```yaml
spec:
  compositionSelector:
    matchLabels:
      platform.saas.test/db-provider: cnpg
```

or:

```yaml
matchLabels:
  platform.saas.test/db-provider: rds
```

This can be:

* environment default
* workspace default
* explicitly set by advanced users


## Database XRD (simple, stable)

```yaml
kind: CompositeResourceDefinition
spec:
  names:
    kind: Database
  versions:
    - name: v1alpha1
      schema:
        openAPIV3Schema:
          properties:
            spec:
              properties:
                engine:
                  type: string
                  enum: [postgres]
                size:
                  type: string
                highAvailability:
                  type: boolean
```

No provider logic here.


## Database Compositions (one per backend)

### CloudNativePG

```yaml
metadata:
  name: database-postgres-cnpg
  labels:
    platform.saas.test/db-provider: cnpg
```

Pipeline:

```
render-cnpg-cluster
create-secret
expose-connection
```


### RDS

```yaml
metadata:
  name: database-postgres-rds
  labels:
    platform.saas.test/db-provider: rds
```

Pipeline:

```
provision-rds
create-secret
expose-connection
```


## How WorkspaceApp consumes the DB (important)

### Contract between Database → App

Database XR **must publish**:

```yaml
status:
  connection:
    host
    port
    username
    passwordSecretRef
```

WorkspaceApp pipeline:

* reads `databaseRef`
* injects connection into Helm values
* never knows the backend


## Why NOT let WorkspaceApp choose CNPG vs RDS directly

If you do this:

```yaml
spec:
  database:
    type: cnpg
```

You immediately get:

* app logic coupled to infra
* harder migrations
* painful deprecations
* duplicated infra logic across apps

This is the same mistake as:

> “App chooses Helm vs Kustomize”


## Who gets to choose the backend?

You still allow flexibility — just at the **right layer**:

| Layer         | Chooses              |
| ------------- | -------------------- |
| Platform team | default DB backend   |
| Workspace     | override policy      |
| App           | just references a DB |

You can enforce this with:

* defaults
* admission
* policy (OPA)


## Bonus: future migrations become trivial

Want to move:

```
CloudNativePG → RDS
```

You:

1. Create new Database XR
2. Update `WorkspaceApp.databaseRef`
3. App redeploys

No chart changes.
No app logic changes.


## TL;DR

* Introduce **Database XR**
* Backend choice lives in **Database Composition**
* Apps reference databases, not providers
* Same abstraction pattern as ProviderConfig
* This keeps your platform evolvable
