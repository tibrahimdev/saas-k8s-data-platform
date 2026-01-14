# UX Design

From a UX/DX perspective, you want to avoid giving the user a "Toolbox" and instead give them a "Service." Here is how you handle the two paths (Existing Cluster vs. No Cluster).

---

## 1. The "Split" UX Design

You shouldn't have two completely different one-liners if you can avoid it. Instead, you have **One CLI** with two **Modes**.

### Case A: "I already have a cluster" (The Agent Mode)

* **The Command:** `curl saas.io | sh -s -- --token XYZ`
* **What happens:** The script detects the local `kubeconfig`, installs your Operator, and the Heartbeat begins immediately.
* **UX Status:** "Cluster Connected" in 30 seconds.

### Case B: "I have nothing but an AWS/GCP/Azure Account" (The Provisioner Mode)

* **The Command:** `curl saas.io | sh -s -- --token XYZ --provision aws`
* **What happens:** The script cannot find a `kubeconfig`. It asks for AWS Credentials (or uses your local environment). It then runs a **Bootstrap Provisioner** (using Terraform or Crossplane) to build the VPC and EKS.
* **UX Status:** "Building Infrastructure..." (takes 15–20 mins). Once done, it automatically pivots to Case A.

---

## 2. Architecture: "The Operator as the Closer"

To make this work, we need a "Provisioning Kind." In your SaaS Control Plane, you should design a resource called `CloudInfrastructure`.

### The Logical Flow:

1. **SaaS UI:** User selects "Create Cluster on AWS."
2. **SaaS Backend:** Generates a temporary **Provisioning Job**.
3. **The One-Liner (CLI):** * It pulls a specialized "Provisioner" binary.
* It uses your AWS credentials to create the "Minimum Viable Cluster."
* **Crucial Step:** Once the EKS cluster is ready, the CLI installs your **DataPlatform Operator** into it.


4. **Handover:** The CLI exits. The Operator takes over. It sends the first **Heartbeat**.

---

## 3. Designing the "Provisioning" Spec

Even though the Operator runs *inside* the cluster, it can manage the infrastructure *around* it if you give it permissions. However, for Day-0 (VPC/EKS), you usually want the CLI to do the heavy lifting.

### The CRD List for "Everything"

To support Case B, your platform needs these Kinds:

| Kind | Purpose |
| --- | --- |
| `CloudInfra` | Manages VPC, Subnets, and IAM Roles. |
| `ClusterControl` | Manages EKS version, NodeGroups, and Scaling. |
| `DataPlatform` | (Your current CRD) Manages the Apps and RDS inside that Infra. |

---

## 4. Why this is a "Safe Bootstrap"

If you want the "Safe Bootstrap" you mentioned earlier, the Operator needs to be **Infrastructure Aware**.

When the Operator starts up for the first time in a new EKS cluster, its heartbeat should say:

> *"I am alive in AWS Region us-west-2. I see I have no RDS instance. My SaaS Spec says I need one. I will now start the RDS provisioning."*

---

## 5. Summary of the DX

1. **User:** Runs the 1-liner.
2. **CLI:** "I see you're on AWS. I'll build EKS for you. Go grab a coffee."
3. **EKS:** Comes online.
4. **Agent:** Installs itself.
5. **Heartbeat:** Hits the SaaS API.
6. **SaaS Dashboard:** Turns Green. "Marketing-Analytics Cluster is READY."
