"""
cloud-native-saas.kops-workspace-agent.src.main

A minimal Kopf operator example for the Workspace resource.

This operator demonstrates:
- Watching a custom resource of kind Workspace
- Running a periodic timer to sync/reconcile
- Logging spec fields for demonstration purposes

Expected environment variables:
- KOPF_GROUP_SELECTOR: CRD group (default: "platform.saas.test")
- KOPF_VERSION_SELECTOR: CRD version (default: "v1alpha1")
- KOPF_KIND_SELECTOR: CRD kind (default: "workspace")
- KOPF_TIMER_INTERVAL: Timer interval in seconds (default: 10)
"""

import asyncio
from typing import Optional
import kopf
import logging
import os
import requests

from kubernetes import client, config
from kubernetes.client.exceptions import ApiException
from pydantic import ValidationError
from schemas import WorkspacePollResponse, WorkspaceSpec

# Kopf selectors from environment
KOPF_GROUP_SELECTOR = os.getenv("KOPF_GROUP_SELECTOR", "platform.saas.test")
KOPF_VERSION_SELECTOR = os.getenv("KOPF_VERSION_SELECTOR", "v1alpha1")
KOPF_KIND_SELECTOR = os.getenv("KOPF_KIND_SELECTOR", "workspace")
KOPF_TIMER_INTERVAL = float(os.getenv("KOPF_TIMER_INTERVAL", 10))

# Workspace config
WORKSPACE_CA_PATH = os.getenv("WORKSPACE_CA_PATH", "../../docker/step-ca/certs/root_ca.crt")
WORKSPACE_CA_ENABLE = False
WORKSPACE_POLL_URL = os.getenv(
    "WORKSPACE_URL", "https://saas.test/dummyapi/workspace-w-12345-config.json"
)
WORKSPACE_NAMESPACE = os.getenv("WORKSPACE_NAMESPACE", "saas-system")

VERIFY_CA = True if WORKSPACE_CA_ENABLE else False

LOCK: asyncio.Lock

# Load Kubernetes config safely at runtime
try:
    config.load_incluster_config()
except:
    config.load_kube_config()

api = client.CustomObjectsApi()


@kopf.on.startup()  # type: ignore
async def startup_fn(logger, **kwargs):
    global LOCK
    LOCK = asyncio.Lock()

@kopf.on.startup() # type: ignore
def configure(settings: kopf.OperatorSettings, **_):
    settings.posting.level = logging.WARNING
    settings.watching.connect_timeout = 1 * 60
    settings.watching.server_timeout = 10 * 60

@kopf.on.login() # type: ignore
def login_fn(**kwargs):
    return kopf.login_with_service_account(**kwargs) or kopf.login_with_kubeconfig(**kwargs)

@kopf.on.cleanup()  # type: ignore
async def cleanup_fn(logger, **kwargs):
    pass


def fetch_workspace() -> Optional[WorkspacePollResponse]:
    try:
        response = requests.get(WORKSPACE_POLL_URL, timeout=5, verify=VERIFY_CA)
        response.raise_for_status()
        config = response.json()
        # logging.info(f"Fetched workspace config: {config}")
        logging.info(f"Fetched workspace config")
        return WorkspacePollResponse(**config)
    except requests.RequestException as e:
        logging.error(f"Failed to fetch workspace config: {e}")
        return None

def delete_workspace_cr(name, logger):
    logger.info(f"Deleting Workspace {name}")
    try:
        api.delete_namespaced_custom_object(
            group=KOPF_GROUP_SELECTOR,
            version=KOPF_VERSION_SELECTOR,
            namespace=WORKSPACE_NAMESPACE,
            plural="workspaces",
            name=name,
        )
        logger.info(f"Deleted Workspace CR: {name}")
    except ApiException as e:
        logger.error(f"Failed to delete Workspace CR {name}: {e}")

@kopf.timer(
    KOPF_GROUP_SELECTOR,
    KOPF_VERSION_SELECTOR,
    KOPF_KIND_SELECTOR,
    interval=KOPF_TIMER_INTERVAL,
)  # type: ignore
def reconcile_workspace(name, namespace, spec, status, patch, logger, **kwargs):
    """
    Periodic sync handler for Workspace resources.

    Args:
        name (str): Name of the Workspace CR.
        namespace (str): Namespace of the Workspace CR.
        spec (dict): The spec field of the CR.
        status (dict): Current status of the CR.
        patch (kopf.Patch): Patch object to modify status.
        logger (logging.Logger): Logger for output.
        **kwargs: Additional Kopf-provided arguments.

    Logs a field from the Workspace spec every interval.
    """
    # Poll workspace
    workspace = fetch_workspace()
    if not workspace:
        logger.error("Workspace cant be None")
        return

    # Validate workspace CR
    try:
        ws_spec = WorkspaceSpec(**spec)
    except ValidationError as e:
        logger.error(f"Invalid spec for workspace {name}: {e}")
        return
    
    if workspace.status in ('DELETING', 'DELETED'):
        delete_workspace_cr(workspace.extWorkspaceId, logger)

    # # Safely access 'field' in spec, fallback if not present
    # field_value = spec.get("field", "<not-set>")
    # logger.info(f"[Workspace Sync] {name=} in {namespace=}: field={field_value!r}")
