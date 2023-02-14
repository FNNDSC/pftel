str_description = """

    The data models/schemas for the PACS QR collection.

"""

from    pydantic            import BaseModel, Field
from    typing              import Optional, List, Dict
from    datetime            import datetime

from    pathlib             import Path
from    db                  import pfdb
import  pudb


class logCore(BaseModel):
    """Model for the core log info saved to DB"""
    url                                 : str = ""
    username                            : str = ""
    password                            : str = ""
    dbDir                               : str = ""
    telemetryDir                        : str = ""

class logFile(BaseModel):
    """Model for the log file"""
    path                                : Path
    filename                            : str

class logSimple(BaseModel):
    """The simplest log model POST"""
    prefix                              : str   = ""
    message                             : str   = ""

class logStructured(BaseModel):
    """A simple structured log model"""
    logObject                           : str   = "default"
    logName                             : str   = ""
    appName                             : str   = ""
    execTime                            : float = 0.0
    extra                               : str   = ""

class logResponse(BaseModel):
    """A model returned a log is POSTed"""
    response                            : dict
    echo                                : str
    timestamp                           : str

class time(BaseModel):
    """A simple model that has a time string field"""
    time            : str

class logReturnModel(BaseModel):
    """
    A full model that is returned from a query call
    """
    info            : logCore
    time_created    : time
    time_modified   : time
    message         : str

# Some "helper" classes
class ValueStr(BaseModel):
    value           : str = ""