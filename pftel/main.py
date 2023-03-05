str_description = """
    The main module for the service handler/system.

    This essentially creates the fastAPI app and adds
    route handlers.
"""

from    fastapi                 import FastAPI
from    fastapi.middleware.cors import CORSMiddleware
from    base.router             import helloRouter_create

from    routes.logRouter        import router   as log_router

from    os                      import path
from    pfstate                 import  S

import  pudb
from    pypx                    import  smdb
from    argparse                import  Namespace

with open(path.join(path.dirname(path.abspath(__file__)), 'ABOUT')) as f:
    str_about:str       = f.read()

with open(path.join(path.dirname(path.abspath(__file__)), 'VERSION')) as f:
    str_version:str     = f.read().strip()

tags_metadata:list = [
    {
        "name"          :   "Logger services",
        "description"   :
            """
            Provide API POST/GET/DELETE endpoints that will log payloads of various
            types from clients. This service is geared to provide a convenience
            aggregator for logging events from a group of related processes
            all providing telemetry on some compute operation.

            Logs are organized by default in a two-level "directory" hierarchy: the top
            level is called the `logObject` and the next level is the `logCollection`.
            Within each `logCollection` are `events`.

            For example, a `logObject` could be the name of a ChRIS feed type ('dylld')
            while a `logCollection` could be the name of a single execution of that
            Feed ('run1'). Within 'run1' are the logging data from each plugin in that
            feed as it executed in that run.
            """
    },
    {
        "name"          :   "pftel environmental detail",
        "description"   :
            """
            Provide API GET endpoints that provide information about the
            service itself and the compute environment in which the service
            is deployed.
            """
    }
    ]

app = FastAPI(
    title           = 'pftel',
    version         = str_version,
    openapi_tags    = tags_metadata
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
    allow_headers=["*"],
)

hello_router = helloRouter_create(
    name            = 'pfdcm_hello',
    version         = str_version,
    about           = str_about
)

app.include_router( log_router,
                    prefix  = '/api/v1')

app.include_router( hello_router,
                    prefix  = '/api/v1')
