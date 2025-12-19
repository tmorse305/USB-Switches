"""
mqtt-poly-pg3x NodeServer/Plugin for EISY/Polisy

(C) 2024

node MQusbswitch
"""

import udi_interface
import aiohttp
import ewelink
import asyncio
from ewelink import Client, DeviceOffline, Power


LOGGER = udi_interface.LOGGER


class MQusbswitch(udi_interface.Node):
    id = 'MQUSBSW'
    usb_sw_state = "none"  # global variable to store sonoff switch status (on/off)
    """
    This is the class that all the Nodes will be represented by. You will
    add this to Polyglot/ISY with the interface.addNode method.

    Class Variables:
    self.primary: String address of the parent node.
    self.address: String address of this Node 14 character limit.
                  (ISY limitation)
    self.added: Boolean Confirmed added to ISY

    Class Methods:
    setDriver('ST', 1, report = True, force = False):
        This sets the driver 'ST' to 1. If report is False we do not report
        it to Polyglot/ISY. If force is True, we send a report even if the
        value hasn't changed.
    reportDriver(driver, force): report the driver value to Polyglot/ISY if
        it has changed.  if force is true, send regardless.
    reportDrivers(): Forces a full update of all drivers to Polyglot/ISY.
    query(): Called when ISY sends a query request to Polyglot for this
        specific node
    """

    def __init__(self, polyglot, primary, address, name, device):
        """
        Optional.
        Super runs all the parent class necessities. You do NOT have
        to override the __init__ method, but if you do, you MUST call super.

        :param polyglot: Reference to the Interface class
        :param primary: Parent address
        :param address: This nodes address
        :param name: This nodes name
        """
        super().__init__(polyglot, primary, address, name)
        self.controller = self.poly.getNode(self.primary)
        self.cmd_topic = device["cmd_topic"]
        self.on = False

    def updateInfo(self, payload, topic: str):
        if payload == "ON":
            if not self.on:
                self.reportCmd("DON")
                self.on = True
            self.setDriver("ST", 100)
        elif payload == "OFF":
            if self.on:
                self.reportCmd("DOF")
                self.on = False
            self.setDriver("ST", 0)
        else:
            LOGGER.error("Invalid payload {}".format(payload)) 
            
    async def cancel_ping_poll_tasks():
        current_task = asyncio.current_task()
        tasks = [t for t in asyncio.all_tasks() if t is not current_task]
        for task in tasks:
            if task.get_name() == "ping_task" and not task.done():
                #print("Cancelling task",task)
                task.cancel()
            if task.get_name() == "poll_task" and not task.done():
                #print("Cancelling task",task)
                task.cancel()
    
        # Wait for all tasks to finish (handle cancellation)
        await asyncio.gather(*tasks, return_exceptions=True)
        
    def Sonoff_Main(pstate,device_num):
        @ewelink.login(self.controller.getUSBPW(),self.controller.getUSBUSR()) #the function (main) is not wrapped in decorator code so it will execute immediately
        async def main(client):   # client: Client is a hint that client is expected to be type Client
            device =  client.get_device(self.cmd_topic) #sonoff switch ID           
            global usb_sw_state
            usb_sw_state = device.state
           
            try:
                #await device.on()
                obj = Power
                method = getattr(obj, pstate)
                #tasks = asyncio.all_tasks()
                #print (f"method:",{method[0]})
                #print("before",tasks)
                #print(len(tasks))
                await device.edit(method[device_num])  # Change from 0 to 1 to trigger update but no change
                #print(f"Command sent",{method})
                await cancel_ping_poll_tasks()
                if device.online == True:
                    value = 1
                else:
                    value = 0
                self.setDriver("GV1", value)  
    
            except DeviceOffline:
                print("Device is offline!")
                usb_sw_state = "offline"
                await cancel_ping_poll_tasks()
    
    def cmd_on(self, command):
        #self.reportCmd("DON")
        self.on = True
        self.setDriver("ST", 100)
        Sonoff_Main("on",0)

    def cmd_off(self, command):
        #self.reportCmd("DOF")
        self.on = False
        self.setDriver("ST", 0)
        Sonoff_Main("off",0)
       
    def query(self, command=None):
        """
            Called by ISY to report all drivers for this node. This is done in
            the parent class, so you don't need to override this method unless
            there is a need.
            """
        # self.controller.mqtt_pub(self.cmd_topic, "")
        # self.reportDrivers()
   

    # all the drivers - for reference
    drivers = [
        {"driver": "ST", "value": 0, "uom": 78, "name": "Power"},
        {"driver": "GV1", "value": 0, "uom": 25}
    ]

    """
    This is a dictionary of commands. If ISY sends a command to the NodeServer,
    this tells it which method to call. DON calls setOn, etc.
    """
    commands = {
        "QUERY": query,
        "DON": cmd_on,
        "DOF": cmd_off}

    hint = [4, 2, 0, 0]
