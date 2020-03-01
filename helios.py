from pymodbus.client.sync import ModbusTcpClient
from time import sleep


class HeliosModBus:
    _unit = 180
    _address = 1

    def __init__(self, host='127.0.0.1', port='502'):
        self.client = ModbusTcpClient(host=host, port=port)
        self.client.connect()

        self.reg_id = None

    def set_reg_id(self, reg_id):
        self.reg_id = "v{:05d}".format(reg_id)

    def write_registers(self, value=None):
        if self.reg_id is None:
            raise ValueError

        tx_str = self.reg_id

        if value is not None:
            tx_str += "=" + str(value)
        # terminate string with NUL byte
        tx_str += '\0'

        tx_value = self.str_to_list(tx_str)
        self.client.write_registers(address=self._address, values=tx_value, unit=self._unit)

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
        values = self.list_to_str(registers_list.registers).rstrip('\0').split('=')
        values[0] = int(values[0][1:])
        return values

    @staticmethod
    def str_to_list(string: str):
        chars = [ord(c) for c in list(string)]
        u16_list = []
        for num, c in enumerate(chars):
            if not num % 2:
                val = (c & 0xFF) << 8
            else:
                val |= c & 0xFF
                u16_list.append(val)
        if not num % 2:
            u16_list.append(val)
        return u16_list

    @staticmethod
    def list_to_str(lst) -> str:
        ret_val = ''
        for v in lst:
            ret_val += chr((v >> 8) & 0xFF)
            ret_val += chr(v & 0xFF)
        return ret_val

def main():
    client = HeliosModBus(host='helios.fritz.box')
    reg_id = 0
    client.set_reg_id(reg_id)
    print("Sending command: v{:05d}".format(reg_id))
    #client.write_registers()
    result = client.read_registers(length=32)
    print(f"Received command {result[0]}")
    device_name = result[1]
    print(f"Device type: {device_name}")

    tx_cmd = 4
    print("Sending command: v{:05d}".format(tx_cmd))
    #client.write_registers()
    client.set_reg_id(tx_cmd)
    result = client.read_registers(length=32)
    rx_cmd = result[0]
    print(f"Received command v{rx_cmd:05d}")
    system_date = result[1]
    print(f"System date: {system_date}")

    tx_cmd = 5
    print("Sending command: v{:05d}".format(tx_cmd))
    client.set_reg_id(tx_cmd)
    #client.write_registers()
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

    #client.close()


if __name__ == "__main__":
    main()
