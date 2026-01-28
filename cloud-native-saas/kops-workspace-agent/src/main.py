import asyncio
from dotenv import load_dotenv
import kopf
import logging
import os
import urllib3
from kubernetes import config

from settings import app_settings
from workspace import delete_workspace_cr, fetch_workspace

urllib3.disable_warnings()
load_dotenv()

LOCK: asyncio.Lock

# Load Kubernetes config safely at runtime
try:
    config.load_incluster_config()
except:
    config.load_kube_config()


@kopf.on.startup()  # type: ignore
async def startup_fn(logger, **kwargs):
    global LOCK
    LOCK = asyncio.Lock()


@kopf.on.startup()  # type: ignore
def configure(settings: kopf.OperatorSettings, **_):
    log_level = os.getenv("LOG_LEVEL", "WARNING").upper()
    settings.posting.level = getattr(logging, log_level, logging.WARNING)
    settings.posting.enabled = False
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


@kopf.timer(
    app_settings.platform_group,
    app_settings.platform_version,
    "workspace",
    interval=app_settings.controller_timer_interval,
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

    # Handle workspace apps
    desired_apps = workspace.workspaceApps
    app_names = [a.name for a in desired_apps]
    logger.info(f"Configured apps: {app_names}")
    for app in desired_apps:

        app_name = app.name
        app_status = app.status

        # Check if workspace app exists

        # Handle workspace app deletion
        if app.status in ("DELETING", "DELETED"):
            logger.error("Delete workspace application not implemented yet!")
            continue

        # Handle workspace app enable, update, upgrade
        # Currently implemented using KubeVela Addon
    #     handle_workspace_app_addon(app, logger)


"""
The main Workspace controller timer loop
- Watch <app_settings.platform_group>/<app_settings.platform_version>/workspaces resources
"""


# @kopf.on.create(app_settings.platform_group, app_settings.platform_version, "workspaceapplications")  # type: ignore
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
