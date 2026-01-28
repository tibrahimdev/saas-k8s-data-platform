import asyncio
import hashlib
import json
from typing import Optional
from dotenv import load_dotenv
import kopf
import logging
import os
import requests

from kubernetes import client, config
from kubernetes.client.exceptions import ApiException
from pydantic import ValidationError
import yaml
from schemas import WorkspaceAppPollResponse, WorkspacePollResponse, WorkspaceSpec

import urllib3
import subprocess

urllib3.disable_warnings()
load_dotenv()

# Environment variables
CONTROLLER_TIMER_INTERVAL = float(os.getenv("CONTROLLER_TIMER_INTERVAL", 10))
CONTROLLER_VERIFY_CA = False

# Platform variables
PLATFORM_GROUP = os.getenv("PLATFORM_GROUP", "platform.saas.test")
PLATFORM_VERSION = os.getenv("PLATFORM_VERSION", "v1alpha1")

# KubeVela variables
VELA_SYSTEM_NAMESPACE = "vela-system"

# Workspace variables
WORKSPACE_ID = os.getenv("WORKSPACE_ID", "w-12345")
WORKSPACE_CA_PATH = os.getenv(
    "WORKSPACE_CA_PATH", "../../docker/step-ca/certs/root_ca.crt"
)
WORKSPACE_POLLING_URL = os.getenv(
    "WORKSPACE_URL", "https://saas.test/dummyapi/workspace-w-12345-config.json"
)
WORKSPACE_NAMESPACE = os.getenv("WORKSPACE_NAMESPACE", "saas-workspace")

# Status
WORKSPACE_APP_CREATED_STATUS = "PROVISIONING"

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
    level = os.getenv("LOG_LEVEL", "WARNING").upper()
    settings.posting.level = getattr(logging, level, logging.WARNING)
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


# ----------------------------------------------------------------------------------------


def fetch_workspace(logger) -> Optional[WorkspacePollResponse]:
    try:
        response = requests.get(
            WORKSPACE_POLLING_URL, timeout=5, verify=CONTROLLER_VERIFY_CA
        )
        response.raise_for_status()
        config = response.json()
        logger.debug(f"Fetched workspace config: {config}")
        logger.info(f"Fetched workspace config")
        return WorkspacePollResponse(**config)
    except requests.RequestException as e:
        logger.error(f"Failed to fetch workspace config: {e}")
        return None


def delete_workspace_cr(name, logger):
    logger.info(f"Deleting Workspace {name}")
    try:
        api.delete_namespaced_custom_object(
            group=PLATFORM_GROUP,
            version=PLATFORM_VERSION,
            namespace=WORKSPACE_NAMESPACE,
            plural="workspaces",
            name=name,
        )
        logger.info(f"Deleted Workspace CR: {name}")
    except ApiException as e:
        logger.error(f"Failed to delete Workspace CR {name}: {e}")


@kopf.timer(
    PLATFORM_GROUP,
    PLATFORM_VERSION,
    "workspace",
    interval=CONTROLLER_TIMER_INTERVAL,
)  # type: ignore
def reconcile_workspace(name, namespace, spec, status, patch, logger, **kwargs):

    # Poll workspace to control plane API
    workspace = fetch_workspace(logger=logger)
    if not workspace:
        logger.error("Workspace cant be None")
        return

    extWorkspaceId = workspace.extWorkspaceId

    # # Validate workspace CR
    # try:
    #     ws_spec = WorkspaceSpec(**spec)
    # except ValidationError as e:
    #     logger.error(f"Invalid spec for workspace {name}: {e}")
    #     return

    # Handle workspace deletion
    # Must consider the child/owned resources
    # Delete must disallowed if still have childs
    if workspace.status in ("DELETING", "DELETED"):
        delete_workspace_cr(extWorkspaceId, logger)

    # # Handle workspace apps
    # desired_apps = workspace.workspaceApps
    # for app in desired_apps:

    #     app_name = app.name
    #     app_status = app.status

    #     # Handle workspace app deletion
    #     if app.status in ("DELETING", "DELETED"):
    #         logger.error("Delete workspace application not implemented yet!")
    #         continue

    #     # Handle workspace app enable, update, upgrade
    #     # Currently implemented using KubeVela Addon
    #     handle_workspace_app_addon(app, logger)


# ----------------------------------------------------------------------------------------


def compute_digest(spec):
    spec_bytes = json.dumps(spec, sort_keys=True).encode("utf-8")
    return hashlib.sha256(spec_bytes).hexdigest()


def desired_workspace_application_cr(app_name, workspace_name, status, namespace):
    return {
        "apiVersion": f"{PLATFORM_GROUP}/{PLATFORM_VERSION}",
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


def create_workspace_application_cr(app_name, logger):
    body = {
        "apiVersion": f"{PLATFORM_GROUP}/{PLATFORM_VERSION}",
        "kind": "WorkspaceApplication",
        "metadata": {
            "name": app_name,
            "namespace": WORKSPACE_NAMESPACE,
        },
        "spec": {
            "workspaceRef": WORKSPACE_ID,
            "name": app_name,
        },
    }

    api.create_namespaced_custom_object(
        group=PLATFORM_GROUP,
        version=PLATFORM_VERSION,
        namespace=WORKSPACE_NAMESPACE,
        plural="workspaceapplications",
        body=body,
    )

    return "created"


def get_or_create_workspace_app(name, logger):
    try:
        obj = api.get_namespaced_custom_object(
            group=PLATFORM_GROUP,
            version=PLATFORM_VERSION,
            namespace=WORKSPACE_NAMESPACE,
            plural="workspaceapplications",
            name=name,
        )
        status = obj.get("status", {}).get("phase")
        logger.info(f"Workspace application found: {name} [{status}]")
        return obj
    except ApiException as e:
        if e.status == 404:
            body = {
                "apiVersion": f"{PLATFORM_GROUP}/{PLATFORM_VERSION}",
                "kind": "WorkspaceApplication",
                "metadata": {
                    "name": name,
                    "namespace": WORKSPACE_NAMESPACE,
                },
                "spec": {
                    "workspaceRef": WORKSPACE_ID,
                    "name": name,
                },
            }
            obj = api.create_namespaced_custom_object(
                group=PLATFORM_GROUP,
                version=PLATFORM_VERSION,
                namespace=WORKSPACE_NAMESPACE,
                plural="workspaceapplications",
                body=body,
            )
            logger.info(f"Workspace application is created: {name}")
            return obj
        else:
            logger.error(f"Workspace application error: {name} {e.reason}")


def handle_workspace_app_addon(app: WorkspaceAppPollResponse, logger: logging.Logger):
    addon_name = f"addon-{app.name}"
    logger.info(f"Handling workspace app addon: {addon_name}")

    # Check if Addon exist
    addon_exists = get_addon(addon_name, logger)
    addon_status = (
        addon_exists.get("status", {}).get("status") if addon_exists else None
    )
    print(addon_name, addon_status)

    #
    if addon_status != "running" or addon_status is None:
        install_vela_addon()


"""
The main Workspace controller timer loop
- Watch <PLATFORM_GROUP>/<PLATFORM_VERSION>/workspaces resources
"""


# @kopf.on.create(PLATFORM_GROUP, PLATFORM_VERSION, "workspaceapplications")  # type: ignore
# def on_create(spec, patch, logger, **_):
#     """
#     On create a workspaceapplication:
#     - Set status phase as Pending

#     :param spec: Description
#     :param patch: Description
#     :param logger: Description
#     :param _: Description
#     """
#     patch.status["phase"] = "Pending"


def run_vela_addon(
    args: list, logger: logging.Logger, capture_output: bool = True
) -> Optional[str]:
    """
    Run a `vela addon` CLI command.

    Args:
        args (list(str)): The CLI command arguments after `vela addon`, e.g. ["list"] or ["enable", "my-addon"]
        capture_output (bool): If True, returns the command output as a string.
                               If False, prints output directly.

    Returns:
        Optional[str]: The command output if capture_output is True, otherwise None.
    """
    full_command = ["vela", "addon"] + args
    logger.info(f"Running command: {full_command}")

    try:
        if capture_output:
            # Capture output
            result = subprocess.run(
                full_command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            output = result.stdout.strip()
            return output
        else:
            # Just run and show output directly
            subprocess.run(full_command, check=True)
            return None
    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}")
        print("stdout:", e.stdout)
        print("stderr:", e.stderr)
        return None


def get_addon(addon_name, logger):
    try:
        obj = api.get_namespaced_custom_object(
            group="core.oam.dev",
            version="v1beta1",
            namespace=VELA_SYSTEM_NAMESPACE,
            plural="applications",
            name=addon_name,
        )
        logger.info(f"Addon {addon_name} found in namespace {VELA_SYSTEM_NAMESPACE}")
        return obj
    except ApiException as e:
        if e.status == 404:
            logger.warn(
                f"Addon {addon_name} is not found in namespace {VELA_SYSTEM_NAMESPACE}"
            )
            return None
        else:
            raise


def install_vela_addon(addon_name, addon_version, addon_parameters, logger):
    logger.info(f"Installing addon: {addon_name}")

    addon_render_output = run_vela_addon(
        ["enable", addon_name, "--version", addon_version, "--dry-run"],
        logger,
        capture_output=True,
    )
    print(addon_render_output)

    body = yaml.safe_load(str(addon_render_output))
    api.create_namespaced_custom_object(
        group="core.oam.dev",
        version="v1beta1",
        namespace=VELA_SYSTEM_NAMESPACE,
        plural="applications",
        body=body,
    )
    return


def uninstall_vela_addon(addon_name, logger):
    logger.info(f"Uninstalling addon: {addon_name}")
    output = run_vela_addon(
        ["uninstall", addon_name],
        logger,
        capture_output=False,
    )
    logger.info(f"Uninstall addon {addon_name} output: {output}")


# @kopf.timer(PLATFORM_GROUP, PLATFORM_VERSION, "workspaceapplications", interval=10)  # type: ignore
# def sync_workspace_app(spec, status, patch, logger, name, namespace, **_):
#     phase = status.get("phase")
#     print("phase", phase)
#     addon_name = "addon-" + name

#     # 1. Ready → do nothing
#     if phase == "Ready":
#         return

#     # logger.info(f"Phase: {phase}, syncing {name} in {WORKSPACE_NAMESPACE}")

#     # 2. Check if Addon exist
#     addon_exists = get_addon(addon_name, logger)
#     addon_status = addon_exists.get('status', {}).get("status") if addon_exists else None

#     # # 3. Decide what to do
#     # if phase in (None, "Pending") or not addon_exists:
#     #     patch.status["phase"] = "Reconciling"
#     #     logger.info(f"Enabling addon: {addon_name}")
#     #     addon_request = run_vela_addon(
#     #         ["enable", name, "--dry-run"], logger, capture_output=True
#     #     )
#     #     print(addon_request)
#     #     api.create_namespaced_custom_object(
#     #         group='core.oam.dev',
#     #         version='v1beta1',
#     #         namespace=VELA_SYSTEM_NAMESPACE,
#     #         plural="applications",
#     #         body=yaml.safe_load(str(addon_request)),
#     #     )
#     #     return

#     if phase == "Reconciling":
#         if addon_status == 'running':
#             logger.info(f"Marking workspace app {name} as Running")
#             patch.status["phase"] = "Running"
