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

    Args:
        payload (logModel.logStructured): the load payload
    """
    b_saved:bool        = False
    message:str         = "Nothing was saved -- logObject probably doesn't exist"
    str_containerDir:str= '%s/%s/%s'% (config.dbAPI.dobj_DB.DB, payload.logObject, payload.logCollection)
    str_logThis:str     = '%s'      % payload.logEvent
    str_container:str   = '%s/%s'   % (str_containerDir, str_logThis)

    list_logObjects         = lambda    : config.dbAPI.telemetryService_listObjs()
    logContainerDir_exists  = lambda    : config.dbAPI.DB.exists(
                                              str_logThis, path = str_containerDir)
    logContainerDir_create  = lambda    : config.dbAPI.DB.mkdir(str_containerDir)
    logContainer_load       = lambda    : config.dbAPI.DB.cat(str_container)
    logContainer_write      = lambda x  : config.dbAPI.DB.touch(str_container, x)
    logContainer_commit     = lambda    : config.dbAPI.DB.node_save('',
                                            startPath       = str_containerDir,
                                            pathDiskRoot    = '%s' % (
                                                config.dbAPI.str_FSprefix,
                                            ),
                                            failOnDirExist  = False
                                    )

    d_logThis       : dict  = {
        'appName'   : payload.appName,
        'execTime'  : payload.execTime,
        'extra'     : payload.extra
    }
    d_existingLog   : dict  = {}
    if payload.logObject in list_logObjects():
        if not logContainerDir_exists():
            logContainerDir_create()
        d_existingLog.update(d_logThis)
        logContainer_write(d_existingLog)
        logContainer_commit()
        b_saved = True
        message = f"Saved log {str_container}"
    LOG(message)
    return {
        'response':     d_logThis,
        'status':       b_saved,
        'timestamp':    '%s' % datetime.now(),
        'message':      message
    }

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
    return config.dbAPI.telemetryService_initObj(
        logObj, d_data
    )

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
    Return a list representation of all the "events" thatubuntu ping package
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
