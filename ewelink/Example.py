import ewelink
from ewelink import Client, DeviceOffline, Power

import sys

# Print the sys.path variable
print("sys.path:")
for path in sys.path:
    print(path)


@ewelink.login('Tea4twoA@eWL','tmorse305@comcast.net')
async def main(client: Client):
    print(client.region)
    print(client.user.info)
    print(client.devices)

    device =  client.get_device('100118ee7e') #Mickey's ID
    print(device.params)
        # Raw device specific properties
        # can be accessed easily like: device.params.switch or device.params['startup'] (a subclass of dict)

    print(device.state)
    print(device.created_at)
    print("Brand Name:", device.brand.name, "Logo URL:", device.brand.logo.url)
    print("Device online?", device.online)

    try:
        #await device.on()
        await device.edit(Power.off [0])
        print("Power on sent")
    except DeviceOffline:
        print("Device is offline!")