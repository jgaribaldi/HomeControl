import asyncio
import pprint
from typing import Any, Dict, Union

import DomoticzEx as Domoticz  # type: ignore
from pywizlight import discovery, wizlight

# Domoticz framework globals (injected at runtime)
Parameters: Dict[str, str]

"""
<plugin key="wiz_control_plugin" name="HomeControl" author="Juli" version="1.0.0">
    <params>
        <param field="Mode1" label="Network Subnet" width="200px" required="true" default="192.168.1.0/24"/>
        <param field="Mode2" label="Update Interval (seconds)" width="100px" required="true" default="10"/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="true"/>
            </options>
        </param>
    </params>
</plugin>
"""


class WizControlPlugin:
    def __init__(self) -> None:
        self.discovered_bulbs: Dict[str, wizlight] = (
            {}
        )  # Store discovered bulbs by MAC address

    def onStart(self) -> None:
        Domoticz.Debugging("WizControlPlugin :: onStart()")
        # TODO: configure discovery mechanism for Wiz bulbs (UDP broadcast)
        pass

    def onStop(self) -> None:
        Domoticz.Debugging("WizControlPlugin :: onStop()")
        pass

    def onConnect(self, connection: Any, status: int, description: str) -> None:
        Domoticz.Debugging(
            f"WizControlPlugin :: onConnect() : status={status} description={description}"
        )
        pass

    def onDisconnect(self, connection: Any) -> None:
        Domoticz.Debugging("WizControlPlugin :: onDisconnect()")
        pass

    def onMessage(self, connection: Any, data: Union[Dict[str, Any], bytes]) -> None:
        Domoticz.Debugging(
            f"WizControlPlugin :: onMessage() : data={pprint.pprint(data)}"
        )
        # TODO: process hardware response message and create new devices (device is discovered)
        pass

    def onCommand(
        self, device_id: str, unit: int, command: str, level: int, color: str
    ) -> None:
        Domoticz.Debugging(
            f"WizControlPlugin :: onCommand() : device_id={device_id} unit={unit} command={command} level={level} color={color}"
        )
        # TODO: send commands to hardware
        pass

    def onHeartbeat(self) -> None:
        Domoticz.Debugging("WizControlPlugin :: onHeartbeat()")
        broadcast_ip = self._get_broadcast_ip()

        try:
            self._execute_bulb_discovery(broadcast_ip)
        except Exception as e:
            Domoticz.Error(f"Discovery failed: {e}")

    def _get_broadcast_ip(self) -> str:
        # Get network subnet from plugin parameters with fallback
        try:
            subnet = Parameters["Mode1"]
            if not subnet:
                subnet = "192.168.1.0/24"
        except (NameError, KeyError):
            # Fallback when Parameters is not available (testing/development)
            subnet = "192.168.1.0/24"

        # Convert subnet to broadcast address (simple implementation)
        return subnet.replace("/24", ".255")

    def _execute_bulb_discovery(self, broadcast_ip: str) -> None:
        bulbs = asyncio.run(discovery.discover_lights(broadcast_space=broadcast_ip))
        Domoticz.Log(f"Discovered {len(bulbs)} Wiz bulbs")

        # Process discovered bulbs
        for bulb in bulbs:
            mac_address = bulb.mac
            if mac_address:
                self.discovered_bulbs[mac_address] = bulb
                Domoticz.Log(f"Found bulb: {bulb.ip} (MAC: {mac_address})")

    def onNotification(
        self,
        name: str,
        subject: str,
        text: str,
        status: str,
        priority: int,
        sound: str,
        image_file: str,
    ) -> None:
        Domoticz.Debugging(
            f"WizControlPlugin :: onNotification() : name={name} subject={subject} text={text} status={status} priority={priority} sound={sound} image_file={image_file}"
        )
        pass


global _plugin
_plugin = WizControlPlugin()


def onStart():
    global _plugin
    _plugin.onStart()


def onStop():
    global _plugin
    _plugin.onStop()


def onConnect(connection: Any, status: int, description: str):
    global _plugin
    _plugin.onConnect(connection, status, description)


def onDisconnect(connection: Any):
    global _plugin
    _plugin.onDisconnect(connection)


def onMessage(connection: Any, data: Union[Dict[str, Any], bytes]):
    global _plugin
    _plugin.onMessage(connection, data)


def onCommand(device_id: str, unit: int, command: str, level: int, color: str):
    global _plugin
    _plugin.onCommand(device_id, unit, command, level, color)


def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()


def onNotification(
    name: str,
    subject: str,
    text: str,
    status: str,
    priority: int,
    sound: str,
    image_file: str,
):
    global _plugin
    _plugin.onNotification(name, subject, text, status, priority, sound, image_file)
