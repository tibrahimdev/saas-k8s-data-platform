#!/bin/sh
set -eu

START_TIME=$(date +%s)
echo "Starting bootstrap..."

# ---- token check ----
if [ -z "${BOOTSTRAP_TOKEN:-}" ]; then
  echo "BOOTSTRAP_TOKEN is not set. Exiting"
  exit 1
fi

# Defaults
DEFAULT_BRANDING=saas
DEFAULT_WORKSPACE=workspace
DEFAULT_MANIFEST_URL="https://saas.test/manifests/cluster-bootstrap-0.0.1.yaml"
DEFAULT_KUBEVELA_HELM_URI=https://saas.test/charts/vela-core-1.10.6-saas.1.tgz

# Versions
CLOUDNATIVEPG_VERSION=1.28

# ---- preflight ----
echo "Prerequisite checks:"
if command -v kubectl >/dev/null 2>&1; then
  echo "kubectl available"
else
  echo "kubectl not installed. Installing..."
fi

if command -v vela >/dev/null 2>&1; then
  echo "vela available"
else
  echo "vela not installed. Installing..."
  curl -fsSl https://kubevela.io/script/install.sh | bash
fi

echo "Preflight OK"
echo "--------------------"

BRANDING="${1:-${BRANDING:-$DEFAULT_BRANDING}}"
WORKSPACE="${1:-${WORKSPACE:-$DEFAULT_WORKSPACE}}"
NAMESPACE=$WORKSPACE
DEPLOYMENT="${BRANDING}-controller"
MANIFEST_URL="${1:-${MANIFEST_URL:-$DEFAULT_MANIFEST_URL}}"

SYSTEM_NAMESPACE="${BRANDING}-system"
WORKLOAD_NAMESPACE="${BRANDING}-workload"
KUBEVELA_SYSTEM_NAMESPACE=vela-system

# TIMEOUT="120s"

echo "--------------------"
echo "Using manifest: ${MANIFEST_URL}"
echo "Workspace: ${WORKSPACE}"
echo "--------------------"

# Namespace preparation
# It creates 2 namespace: saas-system, saas-workload
# And apply delete protection using ValidatingAdmissionPolicy
echo "Setting up namespaces..."
curl -sSL https://saas.test/manifests/cluster-bootstrap-0.0.1.yaml | kubectl apply -f -

# KubeVela
# Allow user to answer n, but continue
echo "Installing KubeVela control plane..."
if ! vela install -f $DEFAULT_KUBEVELA_HELM_URI -n $KUBEVELA_SYSTEM_NAMESPACE; then
  echo "KubeVela installation skipped (existing installation preserved). Continuing bootstrap..."
fi

# VelaUX
echo "Installing addon velaux..."
vela addon enable velaux 

# FluxCD
echo "Installing addon fluxcd..."
vela addon enable fluxcd namespace=$SYSTEM_NAMESPACE

# CloudNativePG
echo "Installing addon CloudNativePG operator..."
curl -sSfL \
  https://raw.githubusercontent.com/cloudnative-pg/artifacts/release-${CLOUDNATIVEPG_VERSION}/manifests/operator-manifest.yaml | \
  kubectl apply --server-side -f -

# echo "Installing ${DEPLOYMENT}..."

# # ---- namespace ----
# if kubectl get ns "$NAMESPACE" >/dev/null 2>&1; then
#     echo "Namespace '$NAMESPACE' already exists"
# else
#     echo "Creating namespace '$NAMESPACE'..."
#     kubectl create ns "$NAMESPACE"
# fi

# # ---- secret (idempotent) ----
# kubectl create secret generic control-plane-token \
#   -n "$NAMESPACE" \
#   --from-literal=token="$BOOTSTRAP_TOKEN" \
#   --dry-run=client -o yaml | kubectl apply -f -

# # # ---- install ----
# # kubectl apply -f "$MANIFEST_URL"

# # # ---- wait for health ----
# # kubectl wait \
# #   --for=condition=Available \
# #   deployment/"$DEPLOYMENT" \
# #   -n "$NAMESPACE" \
# #   --timeout="$TIMEOUT"

# echo "--------------------"
# echo "Control plane agent installed and healthy"

sleep 5

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Convert seconds to human-readable format
hours=$((DURATION / 3600))
minutes=$(( (DURATION % 3600) / 60 ))
seconds=$((DURATION % 60))

echo "--------------------"
echo "✅ Cluster bootstrap completed successfully."
echo "Cluster bootstrap completed in ${hours}h ${minutes}m ${seconds}s"
