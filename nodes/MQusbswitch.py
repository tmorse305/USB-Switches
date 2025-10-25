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

    def call_dev(action):
        @ewelink.login(self.controller.getUSBPW(),self.controller.getUSBUSR())       
        async def main(client: Client):
            print(client.region)
            print(client.user.info)
            print(client.devices)
                
            device =  client.get_device(self.cmd_topic) #sonoff switch ID
            global usb_sw_state
            print(device.params)
                # Raw device specific properties
                # can be accessed easily like: device.params.switch or device.params['startup'] (a subclass of dict)
    
            print(device.state)            
            print(device.created_at)
            print("Brand Name:", device.brand.name, "Logo URL:", device.brand.logo.url)
            print("Device online?", device.online)
            usb_sw_state = device.state
            if action != 'stay':
                try:
                    # await device.on()
                    await device.edit(Power.off[0])
                    print("Power on sent")
                except DeviceOffline:
                    print("Device is offline!")
               
                
    def cmd_on(self, command):
        #self.reportCmd("DON")
        self.on = True
        self.setDriver("ST", 100)        
        # self.controller.mqtt_pub(self.cmd_topic, "ON")
        self.call_dev('on')
        LOGGER.info ("cmd on ******",usb_sw_state)

    def cmd_off(self, command):
        #self.reportCmd("DOF")
        self.on = False
        self.setDriver("ST", 0)
        # self.controller.mqtt_pub(self.cmd_topic, "OFF")
        self.call_dev('off')        
        LOGGER.info ("cmd off ******",usb_sw_state)      
    
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
        {"driver": "ST", "value": 0, "uom": 78, "name": "Power"}
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
