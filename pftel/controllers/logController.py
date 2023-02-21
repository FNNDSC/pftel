str_description = """
    This module contains logic pertinent to the PACS setup "subsystem"
    of the `pfdcm` service.
"""

from    concurrent.futures  import  ProcessPoolExecutor, ThreadPoolExecutor, Future

from    fastapi             import  APIRouter, Query
from    fastapi.encoders    import  jsonable_encoder
from    fastapi.concurrency import  run_in_threadpool
from    pydantic            import  BaseModel, Field
from    typing              import  Optional, List, Dict, Callable, Any

from    .jobController      import  jobber
import  asyncio
import  subprocess
from    models              import  logModel
import  logging
import  os
from    datetime            import  datetime

import  pudb
from    pudb.remote         import set_trace
import  config
import  json
import  pypx

import  pathlib
import  sys
import  time
from    loguru                  import logger
LOG             = logger.debug

logger_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> │ "
    "<level>{level: <5}</level> │ "
    "<yellow>{name: >28}</yellow>::"
    "<cyan>{function: <30}</cyan> @"
    "<cyan>{line: <4}</cyan> ║ "
    "<level>{message}</level>"
)
logger.remove()
logger.opt(colors = True)
logger.add(sys.stderr, format=logger_format)
LOG     = logger.info


threadpool: ThreadPoolExecutor      = ThreadPoolExecutor()
processpool: ProcessPoolExecutor    = ProcessPoolExecutor()

class Log:
    """
    """

def noop():
    """
    A dummy function that does nothing.
    """
    return {
        'status':   True
    }

def save(
        payload             : logModel.logStructured
) -> dict:
    """
    Parse the incoming payload, and write appropriate
    information to some storage resource.

    The "directory" analogous organization:

        

    Args:
        payload (logModel.logStructured): the load payload
    """
    timestamp = lambda : '%s' % datetime.now()
    list_logObjects         = \
        lambda      : config.dbAPI.telemetryService_listObjs()
    logCollection_exists  = \
        lambda      : config.dbAPI.DB.exists(payload.logCollection, path = str_logObjDir)
    logCollection_create  = \
        lambda      : config.dbAPI.DB.mkdir(str_collectionDir)
    logEvents_get = \
        lambda      : config.dbAPI.telemetryService_eventList(
                            payload.logObject,
                            payload.logCollection
                    )
    logEvent_getCSV = \
        lambda x    : config.dbAPI.telemetryService_dictAsCSV(
                        config.dbAPI.telemetryService_event(
                            payload.logObject,
                            payload.logCollection,
                            x
                        )
        )
    logContainer_load       = \
        lambda      : config.dbAPI.DB.cat(str_container)
    logEvent_write      = \
        lambda x    : config.dbAPI.DB.touch(str_event, x)
    logEvent_commit     = \
        lambda      : config.dbAPI.DB.node_save('',
                            startPath       = str_containerDir,
                            pathDiskRoot    = '%s' % (
                                config.dbAPI.str_FSprefix,
                            ),
                            failOnDirExist  = False
                    )

    d_logEvent:dict      = {
        '__id'          : -1,
        '__timestamp'   : timestamp(),
        'appName'       : payload.appName,
        'execTime'      : payload.execTime,
        'extra'         : payload.extra
    }
    d_ret:dict          = {
        'log'           : d_logEvent,
        'status'        : False,
        'timestamp'     : d_logEvent['__timestamp'],
        'message'       :
            f"Nothing was saved -- logObject '{payload.logObject}' doesn't exist. Create with an appropriate PUT request!"
    }
    str_logObjDir:str       = '%s/%s'   % (config.dbAPI.dobj_DB.DB, payload.logObject)
    str_containerDir:str    = '%s/%s'   % (str_logObjDir, payload.logCollection)
    # str_logEvent:str        = '%s'      % payload.logEvent
    # str_container:str   = '%s/%s'   % (str_containerDir, str_logEvent)

    if not payload.logObject in list_logObjects():
        return d_ret

    d_existingLog:dict      = {}
    if not logContainerDir_exists():
        logContainerDir_create()
    d_ret['log']['__id']    = len(logEvents_get())
    str_logEvent:str        = '%s-%s'   % (d_ret['log']['__id'], payload.logEvent)
    str_container:str       = '%s/%s'   % (str_containerDir, str_logEvent)
    d_existingLog.update(d_logEvent)
    logContainer_write(d_existingLog)
    logContainer_commit()
    d_ret['status'] = True
    d_ret['message'] = f"Saved log {str_container}"
    LOG(logEvent_getCSV(str_logEvent))
    return d_ret

def internalObject_initOrUpdate(
        logObj:str,
        d_data:logModel.logCore
) -> logModel.logInit:
    """Create a new (or made updates to a) log object.

    Args:
        logObj (str): Log Object to create or update

    Returns:
        logModel.logResponse: create/update response
    """
    d_ret:dict = config.dbAPI.telemetryService_initObj(
        logObj, d_data
    )
    LOG(d_ret['message'])
    return d_ret

def internalObjects_getList() -> list:
    """
    Return a list of internal object names
    """
    return list(config.dbAPI.telemetryService_listObjs())

def internalObject_getInfo(
            objName:str
) -> dict:
    """
    Return a dictionary representation of a single PACS object
    """
    return dict(config.dbAPI.telemetryService_info(objName))

def internalObject_getCollections(
            objName:str
) -> list:
    """
    Return a list representation of all the "collections" that
    exist for this object. A "collection" is a named grouping
    that houses all the logs from applications that together
    constitute some logical group -- for example all the apps
    is a given ChRIS feed could constitute one collection.
    """
    return config.dbAPI.telemetryService_collectionList(
        objName
    )

def internalObjectCollection_get(
            objName:str,
            collectionName:str
) -> list:
    """
    Return a list representation of all the "events" details
    for this collection.
    """
    return config.dbAPI.telemetryService_collectionGet(
        objName, collectionName
    )

def internalObjectCollection_getCSV(
            objName:str,
            collectionName:str
) -> str:
    """
    Return a list representation of all the "events" details
    for this collection.
    """
    return config.dbAPI.telemetryService_collectionGetCSV(
        objName, collectionName
    )

def internalObjectCollection_getEvents(
            objName:str,
            collectionName:str
) -> list:
    """
    Return a list representation of all the "events" that
    exist for this collection. An "event" is the atomic element
    in the logger universe, and is the actual telemetry data
    transmitted by an application, for instance an application
    in a given ChRIS feed.
    """
    return config.dbAPI.telemetryService_eventList(
        objName, collectionName
    )

def internalObjectCollection_getEvent(
            objName:str,
            collectionName:str,
            eventName:str
) -> dict:
    """
    Return the "raw" (JSON) telemetry data that was transmitted
    by an event.
    """
    return config.dbAPI.telemetryService_event(
        objName, collectionName, eventName
    )
