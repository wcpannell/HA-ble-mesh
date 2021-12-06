#!/usr/bin/env python3

"""
This is the module that is responsible for interfacing with the gateway node.
This should be made into a python library and imported as a manifest
requirement
"""

from serial import Serial
from serial.tools import list_ports
from typing import Optional, OrderedDict, List
from enum import IntEnum
from time import time, sleep
import csv
from pathlib import Path


class SensorTypes(IntEnum):
    Temperature = 0x75
    Humidity = 0x76


class SensorEvent(OrderedDict):
    node_addr: int
    sensor: SensorTypes
    value: float

    def from_buffer(self, buf: bytes) -> None:
        self.node_addr = int.from_bytes(buf[0:2], byteorder="big")
        self.sensor = SensorTypes(int.from_bytes(buf[2:4], byteorder="big"))
        self.value = int.from_bytes(buf[4:], byteorder="big") / 100


class MessageType(IntEnum):
    MSG_POLL = 0  # NULL payload
    MSG_BACKLOG = 1  # uint8_t payload
    MSG_PUB = 1  # struct msg_pub_payload
    MSG_ACK = 0xFE  # NULL payload
    MSG_NACK = 0xFF  # NULL payload


class Message(OrderedDict):
    start: int
    msg_type: MessageType
    payload_size: int
    payload: bytes
    crc: int


class EnviroNode:
    def __init__(self, node_addr: int, node_name: str) -> None:
        self.node_addr = node_addr
        self.node_name = node_name
        self.state = {
            SensorTypes.Temperature: 0.0,
            SensorTypes.Humidity: 0.0,
        }

    def update(self, event: SensorEvent) -> None:
        if event.node_addr == self.node_addr:
            self.state[event.sensor] = event.value


class Interface:
    _ser: Optional[Serial]
    csv_path: Optional[Path]
    # Hard coding in the nodes to make my life with Home Assistant Easier
    nodes: List[EnviroNode] = [
        EnviroNode(36, "Garage"),
        EnviroNode(48, "Interior"),
    ]

    def __init__(
        self, port: Optional[str] = None, log_path: Optional[str] = None
    ) -> None:

        # initialize the csv output file
        if (log_path is None) or (log_path == ""):
            self.csv_path = None
        else:
            self.csv_path = Path(log_path)
            self.write_header()

        # Initialize Serial Port
        if port is None:
            ports = list_ports.comports()
            for a_port in ports:
                if a_port.product == "Mesh Sensor Gateway":
                    try:  # it may be already in use.
                        self._ser = Serial(a_port.device, 115200)
                    except:  # narrow this down a bit
                        pass

        else:
            self._ser = Serial(port, 115200)

    @property
    def connected(self):
        if self._ser is not None:
            return self._ser.isOpen()
        else:
            return False

    def write_header(self) -> None:
        # If empty, just use default path
        if self.csv_path is None:
            self.csv_path = Path("enviro_log.csv")
        try:
            with open(self.csv_path, "xt", newline="") as f:
                w = csv.writer(f, dialect="unix")
                w.writerow(["Timestamp", "Node Addr", "Sensor", "Value"])
        except FileExistsError:
            # Assume if it exists, we wrote it, and the header is valid.
            # Good enough for now.
            pass

    def get_message(self) -> Message:
        # Just assume it's a pub event and it's good for now
        if self._ser is not None:
            buf = self._ser.read(10)
            retval = Message()

            retval.start = buf[0]
            retval.msg_type = MessageType(buf[1])
            retval.payload_size = buf[2]
            retval.payload = buf[3:9]
            retval.crc = buf[9]  # Assume crc is good. TODO: validate

            return retval
        else:
            return Message()

    def update_nodes(self, debug=False) -> List[EnviroNode]:
        while (self._ser is not None) and (self._ser.in_waiting >= 10):
            message = self.get_message()
            event = SensorEvent()
            event.from_buffer(message.payload)
            if debug:
                if event is not None:
                    print(
                        f"Got Event from {event.node_addr}: {event.sensor.name} is {event.value}"
                    )
                else:
                    print("Null event!")
            if event is not None:
                for node in self.nodes:
                    node.update(event)

        return self.nodes

    def log_event(self, event: SensorEvent) -> None:
        if self.csv_path is not None:
            with open(self.csv_path, "at", newline="") as f:
                w = csv.writer(f, dialect="unix")
                w.writerow(
                    (time(), event.node_addr, event.sensor.name, event.value)
                )


if __name__ == "__main__":
    mesh = Interface("/dev/ttyACM1")
    event = SensorEvent()
    try:
        while True:
            # message = mesh.get_message()
            # print([hex(i) for i in message.payload])
            # event.from_buffer(message.payload)
            # print(
            #    f"Got Event from {event.node_addr}: {event.sensor.name} is {event.value}\n"
            # )
            # mesh.log_event(event)

            mesh.update_nodes(debug=True)
            for node in mesh.nodes:
                print(f"{node.node_name} #{node.node_addr}: {node.state}\n")
            sleep(10)
    except KeyboardInterrupt:
        pass
