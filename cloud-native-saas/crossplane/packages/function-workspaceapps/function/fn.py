"""A Crossplane composition function."""

import grpc
from crossplane.function import logging, response
from crossplane.function.proto.v1 import run_function_pb2 as fnv1
from crossplane.function.proto.v1 import run_function_pb2_grpc as grpcv1

from database import get_default_database

# from jupyterhub import x

DEFAULT_NAMESPACE = "saas-workload"


class FunctionRunner(grpcv1.FunctionRunnerService):
    """A FunctionRunner handles gRPC RunFunctionRequests."""

    def __init__(self):
        """Create a new FunctionRunner."""
        self.log = logging.get_logger()

    async def RunFunction(
        self, req: fnv1.RunFunctionRequest, _: grpc.aio.ServicerContext
    ) -> fnv1.RunFunctionResponse:
        """Run the function."""
        # Create a logger for this request.
        log = self.log.bind(tag=req.meta.tag)
        log.info("Running function")

        # Create a response to the request. This copies the desired state and
        # pipeline context from the request to the response.
        rsp = response.to(req)

        observed_xr = req.observed.composite.resource
        print(observed_xr)

        # Get spec data
        name = req.observed.composite.resource["metadata"]["name"]
        database = req.observed.composite.resource["spec"]["database"]

        # print("name", name)
        # print("database", database, database["engine"])

        # check if requesting database
        if not (database):
            print("database not specified")

            desired_database = get_default_database(
                namespace=DEFAULT_NAMESPACE,
                base_name=name,
            )
            rsp.desired.resources[f"workspaceapp-{name}"].resource.update(desired_database)
            # rsp.desired.resources[f"workspaceapp-{name}-db"].resource.update(
            #     {
            #         "apiVersion": "postgresql.cnpg.io/v1",
            #         "kind": "Cluster",
            #         "metadata": {
            #             "name": f"{name}-db",
            #             "namespace": DEFAULT_NAMESPACE,
            #         },
            #     }
            # )

        # create helm release
        rsp.desired.resources[f"workspaceapp-{name}-helm"].resource.update(
            {
                "apiVersion": "helm.m.crossplane.io/v1beta1",
                "kind": "Release",
                "metadata": {
                    "name": name,
                },
                "spec": {
                    "providerConfigRef": {
                        "name": "provider-helm",
                        "kind": "ProviderConfig",
                    },
                },
                "forProvider": {
                    "chart": {
                        "name": "jupyterhub",
                        "repository": "https://jupyterhub.github.io/helm-chart/",
                        "version": "4.3.2",
                    }
                },
                "namespace": "saas-workload",
                "values": {},
            }
        )

        # # Let's say your workspace CRD is "Workspaces.platform.saas.test"
        # workspace = next((r for r in req.resources if r.kind == "Workspace"), None)

        # if workspace:
        #     # The CRD spec is usually in .spec
        #     workspace_name = workspace.spec.get("name")
        #     log.info(f"Found workspace: {workspace_name}")

        # # Get the region and a list of bucket names from the observed composite
        # # resource (XR). Crossplane represents resources using the Struct
        # # well-known protobuf type. The Struct Python object can be accessed
        # # like a dictionary.
        # region = req.observed.composite.resource["spec"]["region"]
        # names = req.observed.composite.resource["spec"]["names"]

        # # Add a desired S3 bucket for each name.
        # for name in names:
        #     # Crossplane represents desired composed resources using a protobuf
        #     # map of messages. This works a little like a Python defaultdict.
        #     # Instead of assigning to a new key in the dict-like map, you access
        #     # the key and mutate its value as if it did exist.
        #     #
        #     # The below code works because accessing the xbuckets-{name} key
        #     # automatically creates a new, empty fnv1.Resource message. The
        #     # Resource message has a resource field containing an empty Struct
        #     # object that can be populated from a dictionary by calling update.
        #     #
        #     # https://protobuf.dev/reference/python/python-generated/#map-fields
        #     rsp.desired.resources[f"xbuckets-{name}"].resource.update(
        #         {
        #             "apiVersion": "s3.aws.m.upbound.io/v1beta1",
        #             "kind": "Bucket",
        #             "metadata": {
        #                 "annotations": {
        #                     "crossplane.io/external-name": name,
        #                 },
        #             },
        #             "spec": {
        #                 "forProvider": {
        #                     "region": region,
        #                 },
        #             },
        #         }
        #     )

        # # Log what the function did. This will only appear in the function's pod
        # # logs. A function can use response.normal() and response.warning() to
        # # emit Kubernetes events associated with the XR it's operating on.
        # log.info("Added desired buckets", region=region, count=len(names))

        return rsp
