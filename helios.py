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

    def set_reg_id(self, reg_id):
        self.reg_id = "v{:05d}".format(reg_id)

    def write_registers(self, value=None):
        if self.reg_id is None:
            raise ValueError

        builder = BinaryPayloadBuilder(byteorder=Endian.Big,
                                       wordorder=Endian.Little)
        builder.add_string(self.reg_id)

        if value is not None:
            builder.add_string("=" + str(value))
        # terminate string with NUL byte
        builder.add_string('\0')

        payload = builder.to_registers()

        self.client.write_registers(address=self.ADDRESS, values=payload, unit=self.UNIT)

    def read_registers(self, length) -> [int, str]:
        """
        Read registers from modbus

        First write requested register id, then read answer
        :param length: length of requested data
        :return: List containing register id as int and value as string
        """
        if self.reg_id is None:
            raise ValueError

        self.write_registers()
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
    client.set_reg_id(reg_id)
    print("Sending command: v{:05d}".format(reg_id))
    result = client.read_registers(length=32)
    print(f"Received command {result[0]}")
    device_name = result[1]
    print(f"Device type: {device_name}")

    tx_cmd = 4
    print("Sending command: v{:05d}".format(tx_cmd))
    client.set_reg_id(tx_cmd)
    result = client.read_registers(length=32)
    rx_cmd = result[0]
    print(f"Received command v{rx_cmd:05d}")
    system_date = result[1]
    print(f"System date: {system_date}")

    tx_cmd = 5
    print("Sending command: v{:05d}".format(tx_cmd))
    client.set_reg_id(tx_cmd)
    result = client.read_registers(length=32)
    rx_cmd = result[0]
    print(f"Received command v{rx_cmd:05d}")
    system_time = result[1]
    print(f"System time: {system_time}")

    tx_cmd = 102
    tx_value = 1
    print("Sending command: v{:05d} with value {}".format(tx_cmd, tx_value))
    client.set_reg_id(tx_cmd)
    client.write_registers(value=tx_value)
    result = client.read_registers(length=10)
    rx_cmd = result[0]
    print(f"Received command v{rx_cmd:05d}")
    fan_setting = result[1]
    print(f"fan percent: {fan_setting}")

    client.close()

if __name__ == "__main__":
    main()
