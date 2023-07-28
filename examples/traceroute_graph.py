import socket

from scapy.layers.inet import traceroute

# target = ["192.168.1.254"]
# target = ["1.1.1.1"]
# target = ["8.8.8.8"]
target = ["www.google.com"]
# for i in range(3):
traceroute_result, packets = traceroute(target, maxttl=32)

# print(traceroute_result, "\n")
for packet in packets:
    ip_address = packet.src
    hostname = socket.gethostbyaddr(ip_address)
    # print(packet, "\t", hostname)
