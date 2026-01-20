# **Terraform on Alibaba Cloud — Secure Setup with RAM + STS**

## **Prerequisites**

* Alibaba Cloud root account (enable **MFA**).
  - Turn on Account Protection
  - Select scenes: Login
  - Select verification: TOTP (authenticator)
* Terraform installed locally (v1.5+ recommended).
* Aliyun CLI installed (optional but useful for testing).

---

## **Step 1: Create an Initial RAM User (Bootstrap)**

> Only account owner should do this in the first time account creation.

1. Log in as root → **RAM Console → Users → Create User**.
2. Create a user: e.g., `admin-bootstrap`
3. Disable console access.
4. Enable **AccessKey** for this user (temporary credentials can’t be created without an initial key).
5. Attach policy: `PowerUserAccess` (can scope later if you want fine-grained permissions).

> You now have a **permanent Access Key/Secret** for this user — **only for bootstrapping**.
> Do not use this `admin-bootstrap` for day to day work or development.

## Real world example
Perfect — let’s build a **realistic Alibaba Cloud account structure** for a team using Terraform and console access, showing **bootstrap admin, Terraform automation, and daily users**. This mirrors best practices like AWS but Alibaba Cloud style.

---

### **1. Bootstrap User**

* **Name:** `admin-bootstrap`
* **Purpose:** Temporary admin used **only to create roles and policies**.
* **Permissions:** `PowerUserAccess` (power user privileges).
* **Credentials:** Long-lived AccessKey (only used once or a few times).
* **Usage:**

  * Create Terraform roles.
  * Create initial RAM users for the team.
* **Lifecycle:** Disable or delete after roles/users are created.

### **2. Terraform Automation Role**

* **Name:** `TerraformAdminRole`
* **Type:** RAM Role
* **Purpose:** Used by Terraform for provisioning resources.
* **Permissions:** Scoped to resources Terraform needs (e.g., ECS, RDS, VPC).
* **Usage:**

  * Automation pipelines, local Terraform runs.
  * Assumed via STS temporary credentials.
* **Credentials:** Temporary only (via STS).

### **3. Developers / Team Users**

* **Type:** RAM Users
* **Purpose:** Daily console and CLI access for team members.
* **Naming convention examples:**

  * `dev-alice` → developer environment access
  * `qa-bob` → QA/test environment
  * `ops-charlie` → operations/monitoring access
* **Permissions:** Least privilege principle

  * Example: `dev-alice` → ECS read/write in dev VPC only
  * `ops-charlie` → monitoring, scaling, alert policies
* **Credentials:** Can use AccessKeys or assume roles.

### **4. Optional Roles for Team**

* **Read-only Audit Role**

  * Name: `ReadOnlyAuditRole`
  * Purpose: For auditing or monitoring by security team
  * Permissions: `ReadOnlyAccess` on all resources

* **Environment-specific Roles**

  * Name: `DevOpsRole-Dev`, `DevOpsRole-Prod`
  * Purpose: Scoped access for automation in each environment
  * Usage: CI/CD pipelines assume these roles instead of full TerraformAdminRole

### **5. Typical Workflow**

1. **Bootstrap:**

   * Log in as `admin-bootstrap` → create `TerraformAdminRole` and team users.
2. **Terraform:**

   * Assume `TerraformAdminRole` via STS → run `init/plan/apply`.
3. **Developers:**

   * Use their own RAM users → limited permissions for day-to-day tasks.
4. **Audit/Monitoring:**

   * Use `ReadOnlyAuditRole` → STS or console login.
5. **Root Account:**

   * Offline, MFA enabled, only for emergency account recovery.

### **Example Structure Table**

| Identity           | Type     | Permissions               | Usage                             | Credentials                     |
| ------------------ | -------- | ------------------------- | --------------------------------- | ------------------------------- |
| admin-bootstrap    | RAM User | PowerUserAccess       | Initial setup, create roles/users | Long-lived (delete after setup) |
| TerraformAdminRole | RAM Role | Scoped Terraform policies | Terraform automation              | Temporary via STS               |
| dev-alice          | RAM User | ECS/RDS dev permissions   | Dev work, testing                 | AccessKey or STS                |
| qa-bob             | RAM User | ECS/RDS QA permissions    | QA, testing                       | AccessKey or STS                |
| ops-charlie        | RAM User | Monitoring / scaling      | Ops / alerts                      | AccessKey or STS                |
| ReadOnlyAuditRole  | RAM Role | Read-only                 | Security audits                   | STS temporary                   |
| Root Account       | Root     | Full                      | Emergency only                    | Offline, MFA enabled            |

```
                               +----------------+
                               |  Root Account  |
                               |  (Offline, MFA)|
                               +--------+-------+
                                        |
                                        v
                             +---------------------+
                             |  admin-bootstrap    |
                             |  (RAM User)        |
                             |  Initial Setup      |
                             +--------+------------+
                                      |
                +---------------------+----------------------+
                |                                            |
                v                                            v
      +--------------------+                       +--------------------+
      | TerraformAdminRole  |                       | Team RAM Users     |
      | (RAM Role)          |                       |-------------------|
      | - Scoped policies   |                       | dev-alice          |
      | - STS temp creds    |                       | qa-bob             |
      | - Terraform / CI/CD |                       | ops-charlie        |
      +--------------------+                       +-------------------+
                |
                v
      +---------------------+
      | Optional Roles      |
      | ReadOnlyAuditRole   |
      | Env-specific roles  |
      +---------------------+
```

---

## **Step 2: Create a Terraform RAM Role**

1. Go to **RAM → Roles → Create Role**.
2. Choose **Trusted Entity:** RAM User
3. Attach required policies (e.g., ECS, RDS, VPC access) → Role name: `TerraformAdminRole`.
4. Note the **Role ARN**:

```text
acs:ram::1234567890123456:role/TerraformAdminRole
```

---

## **Step 3: Assume the Role using STS**

Use the bootstrap RAM user to assume the role:

```bash
aliyun configure set --profile admin-bootstrap \
  --access-key YOUR_BOOTSTRAP_KEY \
  --secret-key YOUR_BOOTSTRAP_SECRET \
  --region cn-hangzhou

aliyun sts AssumeRole \
  --RoleArn "acs:ram::1234567890123456:role/TerraformAdminRole" \
  --RoleSessionName "TerraformSession" \
  --profile bootstrap
```

You will get JSON output:

```json
{
  "Credentials": {
    "AccessKeyId": "TEMP_KEY_ID",
    "AccessKeySecret": "TEMP_SECRET",
    "SecurityToken": "TEMP_SECURITY_TOKEN",
    "Expiration": "2026-01-19T12:00:00Z"
  }
}
```

---

## **Step 4: Configure Terraform Provider**

Create `provider.tf`:

```hcl
provider "alicloud" {
  region         = "cn-hangzhou"
  access_key     = var.access_key
  secret_key     = var.secret_key
  security_token = var.security_token
}
```

Create `variables.tf`:

```hcl
variable "access_key" {}
variable "secret_key" {}
variable "security_token" {}
```

---

## **Step 5: Export Temporary Credentials**

```bash
export ALICLOUD_ACCESS_KEY="TEMP_KEY_ID"
export ALICLOUD_SECRET_KEY="TEMP_SECRET"
export ALICLOUD_SECURITY_TOKEN="TEMP_SECURITY_TOKEN"
export ALICLOUD_REGION="cn-hangzhou"
```

Terraform can now automatically pick these up.

---

## **Step 6: Initialize Terraform**

```bash
terraform init
```

* Downloads provider and sets up backend.

---

## **Step 7: Plan Terraform Changes**

```bash
terraform plan \
  -var "access_key=$ALICLOUD_ACCESS_KEY" \
  -var "secret_key=$ALICLOUD_SECRET_KEY" \
  -var "security_token=$ALICLOUD_SECURITY_TOKEN"
```

* Review the actions Terraform will perform.

---

## **Step 8: Apply Terraform Changes**

```bash
terraform apply \
  -var "access_key=$ALICLOUD_ACCESS_KEY" \
  -var "secret_key=$ALICLOUD_SECRET_KEY" \
  -var "security_token=$ALICLOUD_SECURITY_TOKEN"
```

* Confirms and creates resources.

> Remember: **temporary credentials expire** (1–12 hours). Re-run Step 3 if needed.

---

## **Step 9: Post-Bootstrap Cleanup**

* **Keep root account offline** with MFA enabled.
* Delete bootstrap RAM user **or rotate keys** after initial role setup, if desired.
* All Terraform runs should now use **STS temporary credentials from the role**.

---

## ✅ **Best Practices Summary**

1. Never use the root account for Terraform or daily operations.
2. Use a **RAM Role + STS temporary credentials** for automation.
3. Limit permissions to only what Terraform needs.
4. Consider running Terraform on ECS with an attached RAM Role → credentials fetched automatically.
5. Audit actions via **RAM user logs**.
