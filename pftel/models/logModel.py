str_description = """

    The data models/schemas for the PACS QR collection.

"""

from    pydantic            import BaseModel, Field
from    typing              import Optional, List, Dict
from    datetime            import datetime
from    enum                import Enum
from    pathlib             import Path
import  pudb


class logCore(BaseModel):
    """Model for the core log info saved to DB"""
    url                                 : str = "http://localhost:2223"
    username                            : str = "any"
    password                            : str = "any"
    dbDir                               : str = "/home/dicom"
    telemetryDir                        : str = "telemetry"
    description                         : str = "Add a description!"

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
    logCollection                       : str   = ""
    logEvent                            : str   = ""
    appName                             : str   = ""
    execTime                            : float = 0.0
    extra                               : str   = ""

class logPadding(Enum):
    _id                                 : int   = 5
    _timestamp                          : int   = 26
    appName                             : int   = 20
    execTime                            : int   = 10
    extra                               : int   = 40

class logFormatting(Enum):
    _id                                 : str   = "int"
    _timestamp                          : str   = "str"
    appName                             : str   = "str"
    execTime                            : str   = "float"
    extra                               : str   = "str"


class logBoolReturn(BaseModel):
    status                              : bool  = False

class logResponse(BaseModel):
    """A model returned a log is POSTed"""
    log                                 : dict
    status                              : bool
    timestamp                           : str
    message                             : str

class time(BaseModel):
    """A simple model that has a time string field"""
    time            : str

class logInit(BaseModel):
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