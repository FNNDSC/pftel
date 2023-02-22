str_description = """
    This route module handles logic pertaining to associating
    routes to actual logic in the controller module. For the
    most part, this module mostly has route method defintions
    and UI swagger for documentation.

    In most methods, the actual logic is simply a call out
    to the real method in the controller module that performs
    the application logic as well as any surface contact with
    the DB module/service.
"""


from    fastapi             import  APIRouter, Query, HTTPException, BackgroundTasks
from    fastapi.encoders    import  jsonable_encoder
from    typing              import  List, Dict

from    models              import  logModel
from    controllers         import  logController

from    datetime            import datetime, timezone
import  pudb

router          = APIRouter()
router.tags     = ['Logger services']

@router.put(
    "/log/{logObj}/",
    response_model  = logModel.logInit,
    summary         = "PUT information to a (possibly new) pftel object"
)
async def logSetup_put(
    logObj          : str,
    logSetupData    : logModel.logCore
) -> logModel.logInit:
    """
    Description
    -----------
    PUT an entire object. If the object already exists, overwrite.
    If it does not exist, append to the space of available objects.
    """
    return logController.internalObject_initOrUpdate(
        logObj, logSetupData
    )

@router.post(
    '/log/',
    response_model  = logModel.logResponse,
    summary         = '''
    Use this API route to POST a freeform text payload to the
    logger.
    '''
)
async def log_write(
    logPayload      : logModel.logStructured
) -> logModel.logResponse:
    """
    Description
    -----------
    Use this API entry point to simply record some log string to some
    backend resource.

    The specific details of _how_ this resource exists is less relevant
    to the client -- it could be a file/database/etc. In order to "read"
    previous telemetry logs, perform a GET request.

    """
    pudb.set_trace()
    d_ret:logModel.logResponse = logController.save(logPayload)
    return d_ret

@router.get(
    "/log/",
    response_model  = List,
    summary         = """
    GET the list of configured log element objects
    """
)
async def logList_get() -> list:
    """
    Description
    -----------
    GET the list of configured log element objects handlers.
    These objects constitute the most general level of log aggregation.
    At this level, each handler can be thought of as a handler for a
    large group of logging collections.
    """
    return logController.internalObjects_getList()

@router.get(
    "/log/{logObject}/info/",
    response_model  = logModel.logInit,
    summary         = "GET the meta information for a given log object"
)
async def logInfo_getForObject(
    logObject: str
) -> dict:
    """
    Description
    -----------
    GET the setup info pertinent to a log object element called `logName`.
    """
    return logController.internalObject_getInfo(logObject)

@router.get(
    "/log/{logObject}/collections/",
    response_model  = List,
    summary         = """
    GET the collections that constitute this log object
    """
)
async def logCollections_getForObject(
    logObject: str
) -> list:
    """
    Description
    -----------
    GET the list of collections in `logObject`. A _collection_ gathers
    a set of events. For instance, a _collection_ called **02Feb2024** could
    collect all events from the 2nd Feb 2024.
    """
    return logController.internalObject_getCollections(logObject)

@router.get(
    "/log/{logObject}/{logCollection}/events/",
    response_model  = List,
    summary         = """
    GET the events that exist in the log object collection.
    """
)
async def logEvents_getForObjectCollection(
    logObject:str,
    logCollection:str
) -> list:
    """
    Description
    -----------
    GET the list of events that have sent telemtryto the `logCollection`
    of `logObject`.
    """
    return logController.internalObjectCollection_getEvents(
        logObject,
        logCollection
    )

@router.get(
    "/log/{logObject}/{logCollection}/{logEvent}/",
    response_model  = Dict,
    summary         = """
    GET a specific event that exists in this log object collection.
    """
)
async def logEvent_getForObjectCollection(
    logObject:str,
    logCollection:str,
    logEvent:str
) -> dict:
    """
    Description
    -----------
    GET the specific details of event `logEvent` in the collection
    `logCollection` of the object `logObject`.
    """
    return logController.internalObjectCollection_getEvent(
        logObject,
        logCollection,
        logEvent
    )

@router.get(
    "/log/{logObject}/{logCollection}/",
    response_model  = List,
    summary         = """
    GET all the events comprising this log object collection as
    a list of JSON objects.
    """
)
async def log_getForObjectCollection(
    logObject:str,
    logCollection:str
) -> list:
    """
    Description
    -----------
    GET all the events in the collection `logCollection` of the object
    `logObject` as a JSON return.
    """
    return logController.internalObjectCollection_get(
        logObject,
        logCollection
    )

@router.get(
    "/log/{logObject}/{logCollection}/csv",
    response_model  = str,
    summary         = """
    GET all the events comprising this log object collection as
    a CSV formatted string
    """
)
async def log_getForObjectCollectionAsCSV(
    logObject:str,
    logCollection:str,
    style:str = 'plain'
) -> str:
    """
    Description
    -----------
    GET all the events in the collection `logCollection` of the object
    `logObject` as a CSV formatted string.

    By passing a URl query as `style=fancy` a _fancy_ CSV payload is
    returned.
    """
    return logController.internalObjectCollection_getCSV(
        logObject,
        logCollection,
        format = style
    )
