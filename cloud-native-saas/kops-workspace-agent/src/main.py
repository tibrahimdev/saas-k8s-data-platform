import asyncio
import hashlib
import json
from typing import Optional
import kopf
import logging
import os
import requests

from kubernetes import client, config
from kubernetes.client.exceptions import ApiException
from pydantic import ValidationError
from schemas import WorkspaceAppPollResponse, WorkspacePollResponse, WorkspaceSpec

# Kopf selectors from environment
KOPF_TIMER_INTERVAL = float(os.getenv("KOPF_TIMER_INTERVAL", 10))

GROUP = os.getenv("GROUP", "platform.saas.test")
VERSION = os.getenv("VERSION", "v1alpha1")

# Workspace config
WORKSPACE_ID = os.getenv("WORKSPACE_ID", "w-12345")
WORKSPACE_CA_PATH = os.getenv(
    "WORKSPACE_CA_PATH", "../../docker/step-ca/certs/root_ca.crt"
)
WORKSPACE_CA_VERIFY = False
WORKSPACE_POLL_URL = os.getenv(
    "WORKSPACE_URL", "https://saas.test/dummyapi/workspace-w-12345-config.json"
)
WORKSPACE_SYSTEM_NAMESPACE = os.getenv("WORKSPACE_SYSTEM_NAMESPACE", "saas-system")
WORKSPACE_WORKLOAD_NAMESPACE = os.getenv(
    "WORKSPACE_WORKLOAD_NAMESPACE", "saas-workload"
)

# Status
WORKSPACE_APP_CREATED_STATUS = "PROVISIONING"

VERIFY_CA = True if WORKSPACE_CA_VERIFY else False

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


@kopf.on.startup()  # type: ignore
def configure(settings: kopf.OperatorSettings, **_):
    settings.posting.level = logging.WARNING
    settings.watching.connect_timeout = 1 * 60
    settings.watching.server_timeout = 10 * 60


@kopf.on.login()  # type: ignore
def login_fn(**kwargs):
    return kopf.login_with_service_account(**kwargs) or kopf.login_with_kubeconfig(
        **kwargs
    )


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
            group=GROUP,
            version=VERSION,
            namespace=WORKSPACE_SYSTEM_NAMESPACE,
            plural="workspaces",
            name=name,
        )
        logger.info(f"Deleted Workspace CR: {name}")
    except ApiException as e:
        logger.error(f"Failed to delete Workspace CR {name}: {e}")


def compute_digest(spec):
    spec_bytes = json.dumps(spec, sort_keys=True).encode("utf-8")
    return hashlib.sha256(spec_bytes).hexdigest()


def desired_workspace_application_cr(app_name, workspace_name, status, namespace):
    return {
        "apiVersion": f"{GROUP}/{VERSION}",
        "kind": "WorkspaceApplication",
        "metadata": {
            "name": app_name,
            "namespace": namespace,
        },
        "spec": {
            "workspaceRef": workspace_name,
            "name": app_name,
            "status": status,
        },
    }


def create_workspace_application_cr(app_name, status, logger):
    body = {
        "apiVersion": f"{GROUP}/{VERSION}",
        "kind": "WorkspaceApplication",
        "metadata": {
            "name": app_name,
            "namespace": WORKSPACE_SYSTEM_NAMESPACE,
        },
        "spec": {
            "workspaceRef": WORKSPACE_ID,
            "name": app_name,
            "status": status,
        },
    }
    api.create_namespaced_custom_object(
        group=GROUP,
        version=VERSION,
        namespace=WORKSPACE_SYSTEM_NAMESPACE,
        plural="workspaceapplications",
        body=body,
    )
    return "created"


def get_or_create_workspace_app(name, logger):
    try:
        obj = api.get_namespaced_custom_object(
            group=GROUP,
            version=VERSION,
            namespace=WORKSPACE_SYSTEM_NAMESPACE,
            plural="workspaceapplications",
            name=name,
        )
        logger.info(f"Workspace application found: {name}")
        return obj
    except ApiException as e:
        if e.status == 404:
            body = {
                "apiVersion": f"{GROUP}/{VERSION}",
                "kind": "WorkspaceApplication",
                "metadata": {
                    "name": name,
                    "namespace": WORKSPACE_SYSTEM_NAMESPACE,
                },
                "spec": {
                    "workspaceRef": WORKSPACE_ID,
                    "name": name,
                    "status": WORKSPACE_APP_CREATED_STATUS,
                },
            }
            obj = api.create_namespaced_custom_object(
                group=GROUP,
                version=VERSION,
                namespace=WORKSPACE_SYSTEM_NAMESPACE,
                plural="workspaceapplications",
                body=body,
            )
            logger.info(f"Workspace application is created: {name}")
            return obj
        else:
            logger.error(f"Workspace application error: {name} {e.reason}")


@kopf.timer(
    GROUP,
    VERSION,
    "workspace",
    interval=KOPF_TIMER_INTERVAL,
)  # type: ignore
def reconcile_workspace(name, namespace, spec, status, patch, logger, **kwargs):

    # Poll workspace to control plane API
    workspace = fetch_workspace()
    if not workspace:
        logger.error("Workspace cant be None")
        return

    extWorkspaceId = workspace.extWorkspaceId

    # Validate workspace CR
    try:
        ws_spec = WorkspaceSpec(**spec)
    except ValidationError as e:
        logger.error(f"Invalid spec for workspace {name}: {e}")
        return

    # Handle workspace deletion
    # Must consider the child/owned resources
    # Delete must disallowed if still have childs
    if workspace.status in ("DELETING", "DELETED"):
        delete_workspace_cr(extWorkspaceId, logger)

    # Handle workspace apps
    desired_apps = workspace.workspaceApps
    for app in desired_apps:

        app_name = app.name
        app_status = app.status

        if app.status in ("DELETING", "DELETED"):
            logger.error("Delete workspace application not implemented yet!")
            continue

        # Get existing or create new workspace app CR
        app_cr = get_or_create_workspace_app(app_name, logger)
        print(app_cr)
