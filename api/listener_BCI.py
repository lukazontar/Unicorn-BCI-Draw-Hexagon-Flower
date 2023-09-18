import json
import re
import socket


def receive_item(ip_address: str, port_number: int):
    """
    Attempts to receive an item via UDP socket on given IP address and port number.
    :param ip_address: IP address.
    :param port_number: Port number.
    :return: Received item or null if no item was received.
    """

    received_item = None
    udp_client = None
    try:
        # Create an endpoint from the specified IP address and port number.
        end_point = (ip_address, port_number)
        # Create a UDP socket.
        udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Bind the socket to the specified end point.
        udp_client.bind(end_point)

        # Receive data from the UDP socket
        received_bytes, sender_address = udp_client.recvfrom(32184)

        # Deserialize the byte stream - extract with regular expressions
        received_item = re.search(
            pattern=r'ITEM\[(.*?)\]',
            string=str(received_bytes)
        ).group(1)

    except socket.error as e:
        print("An error occurred accessing the socket:", e)
    finally:
        try:
            # Close the UDP socket
            if udp_client:
                udp_client.close()
        except socket.error as e:
            print("An error occurred while accessing the socket:", e)
    return received_item


if __name__ == "__main__":
    # Specify local IP address and port from where to receive data
    # Unicorn Speller must send the data to this endpoint
    ip_address = "127.0.0.1"
    port = 20
    print(f"Running on {ip_address} port {port}.")

    while True:
        # Block until an item from Unicorn Speller is received
        item = receive_item(ip_address, port)

        if item is not None:
            # Save new item to brain interface data.
            with open('../data/brain_interface_data.json', 'r+') as file:
                # Read state of brain interface data.
                data = json.load(file)

                print(f"Item '{item}' was received.")

                # Check if item is color.
                if item in ('red', 'green', 'blue'):
                    data['color'] = item
                # Check if item is 'confirm'
                elif item == 'confirm':
                    data['confirm'] = True
                # Check if item is 'clear'
                elif item == 'clear':
                    data['personal_id'] = ""
                # Check if item is 'back'
                elif item == 'back':
                    data['personal_id'] = data['personal_id'][:-1]
                # Check if item is numeric.
                elif item.isnumeric() and len(item) == 1:
                    data['personal_id'] += item
                # Throw error if item is not recognized.
                else:
                    raise RuntimeError('Unknown item transmitted from Unicorn websocket.')

                # Writing to json.
                file.seek(0)
                json.dump(data, file, indent=4)
                file.truncate()
