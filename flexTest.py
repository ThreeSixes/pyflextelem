# Flex telemetry test script reports position from GPSD once every 5 seconds.

import os
import traceback
import time
import gps
import threading
import math
import psutil

from flextelem import flextelem
from pprint import pprint

# Build empty GPS object.
g = None
# Should really be none ^

class telPoll(threading.Thread):
    def __init__(self):
        """
        Telemetry poller thread.
        """
        
        try:
            threading.Thread.__init__(self)
    
            # Grab GPS object.
            global g
            
            # Build GPS module
            g = gps.gps(mode=gps.WATCH_ENABLE)
            
            # Set us up as initially running.
            self.running = True
        
        except:
            raise
    
    def nuke(self):
        raise SystemExit
    
    def run(self):
        try:
            # Grab GPS object.
            global g
            
            # While the GPS is running.
            while self.running:
                # Grab all the GPS entries.
                g.next()
        
        except:
            # Stop the thread.
            self.running = False
            
            # Dump message.
            print("Exiting poller thread.")
            
            raise

def isGoodFloat(obj):
    """
    Do we have a float that is also non-NaN?
    """
    retVal = False
    
    # Do we have a NaN or a float?
    if (math.isnan(obj) == False) and isinstance(obj, float):
        retVal = True
    
    return retVal

try:
    # Build flexTelem object.
    f = flextelem("https://someserver.com/flextelem/", "someToken", "telemtest")
    
    # Create and activate GPS poller.
    p = telPoll()
    p.start()
    
    # Keep running.
    keepRunning = True

except:
    # Don't loop since something failed in setup.
    keepRunning = False
    
    # Kill the GPS poll thread.
    p.running = False
    
    # Dump exception.
    print("Unhandled exception at startup:\n%s" %traceback.format_exc())
    
# Wait for data before starting.
time.sleep(1)

try:
    # While we want to keep running...
    while keepRunning:
        # If the poller thread is not running
        if p.running == False:
            # Break out of loop.
            break
        
        try:
            # Create blank data.
            dataBody = {}
            
            # Create blank location.
            location = None
            
            # Do we have at least a 2D fix?
            if g.fix.mode > 1:
                # Create location data template.
                location = {
                    'type': 'gps',
                    'units': 'metric',
                    'mode': g.fix.mode,
                    'lat': g.fix.latitude,
                    'lon': g.fix.longitude,
                }
            
                # Do we have at least a 3D fix?
                if g.fix.mode > 2:
                    location.update({
                        'alt': g.fix.altitude,
                        'climb': g.fix.climb
                    })
                
                # Do we have a speed?
                if isGoodFloat(g.fix.speed): location.update({'track': g.fix.speed})
                
                # Do we have a track?
                if isGoodFloat(g.fix.track): location.update({'track': g.fix.track})
                
                # Do we have accuracy data points?
                if isGoodFloat(g.fix.epc): location.update({'epc': g.fix.epc})
                if isGoodFloat(g.fix.epd): location.update({'epd': g.fix.epd})
                if isGoodFloat(g.fix.eps): location.update({'eps': g.fix.eps})
                if isGoodFloat(g.fix.ept): location.update({'ept': g.fix.ept})
                if isGoodFloat(g.fix.epv): location.update({'epv': g.fix.epv})
                if isGoodFloat(g.fix.epv): location.update({'epx': g.fix.epx})
                if isGoodFloat(g.fix.epy): location.update({'epy': g.fix.epy})
                
                # Add it to the data stream.
                dataBody.update({'location': location})
            
            try:
                sysStat = {
                    'cpuPhyCt': psutil.cpu_count(logical = False),
                    'cpuLogCt': psutil.cpu_count(),
                    'cpuUsed': psutil.cpu_percent(),
                    'memTotal': psutil.virtual_memory().total,
                    'memUsed': psutil.virtual_memory().percent,
                    'swapTotal': psutil.swap_memory().total,
                    'swapUsed': psutil.swap_memory().percent
                }
                
                # Add it to our data before sending.
                dataBody.update({'system': sysStat})
            
            except:
                raise
            
            # Do we have data?
            if bool(dataBody) == True:
                try:
                    # Send event and print response.
                    print(f.send(dataBody))
                
                except:
                    print("Failed to execute request:\n%s" %traceback.format_exception_only())
            
            # Wait 5 seconds.
            time.sleep(5)
        
        except (KeyboardInterrupt, SystemExit):
            # Stop running.
            keepRunning = False
            
            # Kill the GPS poll thread.
            p.running = False
            
            print("\nCaught singal to shut down.")
        
        except:
            # Stop running.
            keepRunning = False
            
            # Kill the GPS poll thread.
            p.running = False
            
            print("Unhandled exception:\n%s" %traceback.format_exc())

except:
    print("Caught unhandled exception in main execution body:\n%s" %traceback.format_exc())
    
    # Kill the GPS poll thread.
    p.running = False

finally:
    try:
        print ("Wait for poller thread to exit.")
        
        # Wait for thread to exit.
        p.join()
    
    except:
        # IDGAF
        None
    
    print("Shutdown.")