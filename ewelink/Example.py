def call_dev(action, dev_id):
        @ewelink.login(self.controller.getUSBPW(),self.controller.getUSBUSR())       
        async def main(client: Client):
            print(client.region)
            print(client.user.info)
            print(client.devices)
                
            device =  client.get_device(dev_id) #sonoff switch ID
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
                print(device.state)
