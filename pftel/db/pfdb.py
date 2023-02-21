from    pydantic        import BaseModel, Field

import  json
from    datetime        import datetime

from    pfstate         import  S
from    pfmisc.C_snode  import C_stree
import  config
import  sys

import  pudb

class DBstate(S):
    """

    All state data, i.e. trackers of information:

        * telemetry meta data

    are kept in this object

    """

    str_designNotes = """
            This module simulates some external data base service, used
            to save logging information to actual resources in the
            storage medium.

            Internally, the "db" is a pfstate object. There can be
            typically only one such object per namespace, so the db
            "wrapper" returns from this object in a manner that
            does not require the caller to understand this internal
            organization. This usage of pfstate is historical, and
            should probably be discouraged for future use.

    """
    str_apologies = """

            The idea with this module is to _simulate_ an external DB and
            design the system around that. All calls to any state information
            are thus routed through this module and should, in theory, be
            easily updated in future to an actual separate DB.

    """
    DB : str = '/DB/service'

    def __init__(self, *args, **kwargs):
        """
        An object to hold some generic/global-ish system state, in C_snode
        trees.

        Note that in C_snode trees, the paradigm for constructing a tree from
        a dictionary is interpreted to mean that any dictionary element is a
        tree branch and any dictionary value becomes a tree leaf at that branch.

        Thus, if storing a dictionary as a leaf is needed, then the model is to
        convert that dictionary to a JSON string and save that as a tree leaf.
        This protects the JSON dictionary from being expanded out to its own
        nested tree branch/leaf structure. Of course, remember then to interpret
        the JSON string back into a dictionary if needed by any access methods!
        """
        self.state_create(
        {
            'DB' :
            {
                'service':
                {
                    'default':
                    {
                        'json_created'   : json.dumps({'time' : '%s' % datetime.now()}),
                        'json_modified'  : json.dumps({'time' : '%s' % datetime.now()})
                    }
                }
            }
        },
        *args, **kwargs)

class PFdb():
    """
    An object that is meant to simulate interaction with some external
    (idiosyncratic) data base.

    Actual data is kept in the DBstate object, and this class
    provides a python API to manipulate data objects and
    and returns models of the objects where appropriate.

    The actual objects that contain data are never directly accessed
    by non db services.

    """

    # The DB object is stored directly in the class definition
    # and not in a per-object instance basis. There is afterall
    # only one DB per pfdcm session
    dobj_DB             = None

    # Data pertaining to the telemetry logger
    d_telemetryCore         : dict  = {
        'url':              'localhost:22223',
        'username':         'telemetry',
        'password':         'telemetry1234',
        'dbDir':            '/home/dicom',
        'telemetryDir':     'telemetry',
        'description':      'A telemetry object used to group together collections and events'
    }

    str_FSprefix    : str   = "%s/%s" % (d_telemetryCore['dbDir'], 'telemetry')

    def telemetryService_initObj(self,
            str_objName : str,
            d_data      : dict) -> dict:
        """
        Add (or update) information about a new (or existing) telemetry server
        to the service.
        """
        str_message     : str   = ""
        if str_objName not in self.telemetryService_listObjs():
            self.DB.mkdir('%s/%s'   % (DBstate.DB, str_objName))
            self.DB.touch(
                    '%s/%s/json_created'   % (DBstate.DB, str_objName),
                    json.dumps({'time' : '%s' % datetime.now()})
            )
            str_message     = "New object '%s' created" % str_objName
        else:
            str_message     = "Existing object '%s' modified" % str_objName

        self.DB.touch('%s/%s/info' % (DBstate.DB, str_objName), dict(d_data))
        self.DB.touch(
                '%s/%s/json_modified'     % (DBstate.DB, str_objName),
                json.dumps({'time' : '%s' % datetime.now()})
        )
        self.DB.node_save('',
                        startPath       = '%s/%s' % (DBstate.DB, str_objName),
                        pathDiskRoot    = self.str_FSprefix,
                        failOnDirExist  = False
        )
        return {
            'info'          : self.DB.cat(
                                '%s/%s/info'           % (DBstate.DB, str_objName)
                            ),
            'time_created'  : json.loads(self.DB.cat(
                                '%s/%s/json_created'   % (DBstate.DB, str_objName))
                            ),
            'time_modified' : json.loads(self.DB.cat(
                                '%s/%s/json_modified'  % (DBstate.DB, str_objName))
                            ),
            'message'       : str_message
        }


    def __init__(self, *args, **kwargs) -> None:
        """
        Constructor -- creates default data structures.

        Two "construction" possibilities exist:

        1. The _de novo_ mode, when this is the first time any telemetry is
        being managed. No other telemetry prior telemetry exists. In this case
        build an initial (mostly empty) DB, commit that, and continue.

        2. We are being constructed in an environment where previous telemetry
        exists. Perhaps a previous server crashed? Or a second telementry service
        is created on the same DB? Regardless, if previous artifacts are found,
        read from that DB into active memory.

        Note it is probably possible for multi-process/threading to collide, but
        the DB in external storage _should_ be ok with this.
        """
        self.str_loginName  = ''
        self.str_passwd     = ''
        # pudb.set_trace()
        for k,v in kwargs.items():
            if k == 'login' :   self.str_loginName  = v
            if k == 'passwd':   self.str_passwd     = v

        # Create the basic DB, mostly empty very first DB from the state object.
        PFdb.dobj_DB:DBstate        = DBstate(*args, **dict(kwargs, useGlobalState = True))
        # NB!!!! self.DB is separate from PFdb.dobj.DB.T!!!!
        self.DB:C_stree             = PFdb.dobj_DB.T

        self.telemetryService_initObj("default", PFdb.d_telemetryCore)
        # # Now add the default telemetry details
        # self.DB.touch(
        #     '%s/default/info' % DBstate.DB, PFdb.d_telemetryCore
        # )

        # With an instantiated DB, let's see if there isn't one already on storage
        # from some prior telemetry server.
        T_onDisk:C_stree            = C_stree.tree_load(pathDiskRoot = self.str_FSprefix)
        # If the size of this object is '48', then it is an empty tree and we save
        # our initial state out to storage and move on. Otherwise, we shift to using
        # this already-there DB.

        if len( '%s' % T_onDisk) < 10:
            self.DB.tree_save(startPath = '/', pathDiskRoot = self.str_FSprefix)
        else:
            self.DB                     = T_onDisk

    def telemetryService_listObjs(self)-> list:
        return list(self.DB.lstr_lsnode(DBstate.DB))

    def telemetryService_info(self, str_objName) -> dict:
        """
        Return a model conforming representation of a given
        log element object
        """
        if str_objName in self.telemetryService_listObjs():
            return {
                'info'          : self.DB.cat(
                                    '%s/%s/info'           % (DBstate.DB, str_objName)
                                ),
                'time_created'  : json.loads(self.DB.cat(
                                    '%s/%s/json_created'   % (DBstate.DB, str_objName))
                                ),
                'time_modified' : json.loads(self.DB.cat(
                                    '%s/%s/json_modified'  % (DBstate.DB, str_objName))
                                ),
                'message'       : "Service information for '%s'"        % str_objName
            }

    def telemetryService_collectionList(self, str_objName) -> list:
        """
        Return a list of "collections" for the passed log object
        """
        l_ret:list  = []
        if str_objName in self.telemetryService_listObjs():
            l_ret = list(self.DB.lstr_lsnode('%s/%s' % (DBstate.DB, str_objName)))
        return l_ret

    def telemetryService_eventList(self, str_objName, str_collectionName) -> list:
        """
        Return a list of "events" for the passed obj/collection
        """
        l_ret:list  = []
        if str_collectionName in self.telemetryService_collectionList(str_objName):
            l_ret = list(self.DB.lsf('%s/%s/%s' % (DBstate.DB, str_objName, str_collectionName)))
        return l_ret

    def telemetryService_event(self,
                str_objName,
                str_collectionName,
                str_eventName) -> dict:
        """
        Return a dictionary of the requested event for the passed
        obj/collection/event
        """
        d_ret:dict  = {}
        if str_eventName in self.telemetryService_eventList(str_objName, str_collectionName):
            d_ret = self.DB.cat('%s/%s/%s/%s' % (
                DBstate.DB, str_objName, str_collectionName, str_eventName)
            )
        return d_ret

    def telemetryService_collectionGet(self,
                str_objName,
                str_collectionName) -> list:
        """
        Return a list of "event" data for the passed obj/collection
        """
        l_ret:list  = [
            self.telemetryService_event(
                str_objName, str_collectionName, x
            ) for x in self.telemetryService_eventList(
                            str_objName, str_collectionName
                        )
        ]
        return l_ret

    def telemetryService_dictAsCSV(self,
                d_event:dict)-> str:
        """Convert a dictionary into a CSV string

        Args:
            d_event (dict): an arbitrary dictionary

        Returns:
            str: a CSV formatted string representation of the dictionary values
        """
        str_CSV:str     = ""
        str_CSV += ','.join(str(x) for x in d_event.values())
        str_CSV += '\n'
        return str_CSV

    def telemetryService_collectionGetCSV(self,
                str_objName,
                str_collectionName) -> str:
        """
        Return a CSV formatted string of "event" data for the passed obj/collection
        """
        str_CSV:str     = ""
        l_events:list   = [
            self.telemetryService_event(
                str_objName, str_collectionName, x
            ) for x in self.telemetryService_eventList(
                            str_objName, str_collectionName
                        )
        ]
        if len(l_events):
            str_CSV = ','.join(l_events[0].keys()) + '\n'
            for el in l_events:
                str_CSV += ','.join(str(x) for x in el.values())
                str_CSV += '\n'
        return str_CSV
