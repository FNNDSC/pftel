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
):
    """
    Use this API entry point to simply record some log string to some
    backend resource.

    The specific details of _how_ this resource exists is less relevant
    to the client -- it could be a file/database/etc. In order to "read"
    previous telemetry logs, perform a GET request.

    Args:
        logPayload (logModel.log): the log object to record

    Returns:
        _type_: _description_
    """
    pudb.set_trace()
    d_write = await logController.save(logPayload)
    return d_write

@router.get(
    "/log/list/",
    response_model  = List,
    summary         = "GET the list of configured log element objects"
)
async def logList_get():
    """
    GET the list of configured log element objects
    """
    # pudb.set_trace()
    return logController.internalObjects_getList()

@router.get(
    "/log/{logName}/",
    response_model  = logModel.logReturnModel,
    summary         = "GET the information for a given PACS"
)
async def logObject_get(
    logName: str
):
    """
    GET the setup info pertinent to a log object element called`logName`
    """
    pudb.set_trace()
    return logController.internalObject_get(logName)
