#!/bin/sh
set -eu

# # Defaults
DEFAULT_BRANDING=saas
DEFAULT_WORKSPACE=workspace
DEFAULT_MANIFEST_URL="https://example.com/releases/v1.0.0/install.yaml"
KUBEVELA_VERSION=1.10.6

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
TIMEOUT="120s"

echo "--------------------"
echo "Using manifest: ${MANIFEST_URL}"
echo "Workspace: ${WORKSPACE}"
echo "Namespace: ${WORKSPACE}"
echo "--------------------"

echo "Installing kubevela..."
vela install --version ${KUBEVELA_VERSION}
vela addon enable velaux
vela addon enable fluxcd

# echo "Installing ${DEPLOYMENT}..."

# # ---- namespace ----
# if kubectl get ns "$NAMESPACE" >/dev/null 2>&1; then
#     echo "Namespace '$NAMESPACE' already exists"
# else
#     echo "Creating namespace '$NAMESPACE'..."
#     kubectl create ns "$NAMESPACE"
# fi

# # ---- token check ----
# if [ -z "${BOOTSTRAP_TOKEN:-}" ]; then
#   echo "BOOTSTRAP_TOKEN is not set"
#   exit 1
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
