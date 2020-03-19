from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.payload import BinaryPayloadDecoder


class HeliosModBus:
    UNIT = 180
    ADDRESS = 1

    def __init__(self, host='127.0.0.1', port='502'):
        self.client = ModbusTcpClient(host=host, port=port)
        self.connect()

        self.reg_id = None

    def connect(self):
        """
        Connect to Modbus device
        """
        self.client.connect()

    def close(self):
        """
        Close connection to Modbus device
        """
        self.client.close()

    def write_registers(self, reg_id: int, value=None):
        if reg_id is None:
            raise ValueError

        reg_str = "v{:05d}".format(reg_id)

        builder = BinaryPayloadBuilder(byteorder=Endian.Big,
                                       wordorder=Endian.Little)
        builder.add_string(reg_str)

        if value is not None:
            builder.add_string("=" + str(value))
        # terminate string with NUL byte
        builder.add_string('\0')

        payload = builder.to_registers()

        self.client.write_registers(address=self.ADDRESS, values=payload, unit=self.UNIT)

    def read_registers(self, reg_id: int, length: int) -> [int, str]:
        """
        Read registers from modbus

        First write requested register id, then read answer.
        :param reg_id: id of the register to read from
        :param length: length of requested data
        :return: List containing register id as int and value as string
        """
        if reg_id is None:
            raise ValueError

        self.write_registers(reg_id=reg_id)
        registers_list = self.client.read_holding_registers(address=1, count=length, unit=180)
        decoder = BinaryPayloadDecoder.fromRegisters(registers_list.registers,
                                                     byteorder=Endian.Big,
                                                     wordorder=Endian.Little)
        decoded = decoder.decode_string(length).decode()
        values = decoded.rstrip('\x00').split('=')
        values[0] = int(values[0][1:])
        return values


def main():
    client = HeliosModBus(host='helios.fritz.box')
    reg_id = 0
    print("Sending command: v{:05d}".format(reg_id))
    result = client.read_registers(reg_id=reg_id, length=32)
    print(f"Received command {result[0]}")
    device_name = result[1]
    print(f"Device type: {device_name}")

    reg_id = 4
    print("Sending command: v{:05d}".format(reg_id))
    result = client.read_registers(reg_id=reg_id, length=32)
    rx_cmd = result[0]
    print(f"Received command v{rx_cmd:05d}")
    system_date = result[1]
    print(f"System date: {system_date}")

    reg_id = 5
    print("Sending command: v{:05d}".format(reg_id))
    result = client.read_registers(reg_id=reg_id, length=32)
    rx_cmd = result[0]
    print(f"Received command v{rx_cmd:05d}")
    system_time = result[1]
    print(f"System time: {system_time}")

    reg_id = 102
    tx_value = 1
    print("Sending command: v{:05d} with value {}".format(reg_id, tx_value))
    client.write_registers(reg_id=reg_id, value=tx_value)
    result = client.read_registers(reg_id=reg_id, length=10)
    rx_cmd = result[0]
    print(f"Received command v{rx_cmd:05d}")
    fan_setting = result[1]
    print(f"fan level: {fan_setting}")

    client.close()


if __name__ == "__main__":
    main()
