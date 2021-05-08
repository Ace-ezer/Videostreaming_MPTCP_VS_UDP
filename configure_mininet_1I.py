from mininet.net import Mininet
from mininet.cli import CLI
from mininet.link import Link, TCLink,Intf
from mininet.log import setLogLevel

from subprocess import Popen, PIPE

if __name__ == "__main__":

    setLogLevel('info')

    net = Mininet(link=TCLink)

    key = "net.mptcp.mptcp_enabled"

    value = 1

    p = Popen("sysctl -w %s=%s" % (key, value), shell=True, stdout=PIPE, stderr=PIPE)

    stdout, stderr = p.communicate()

    client = net.addHost('client')

    server = net.addHost('server')

    router = net.addHost('router')

    linkopt={'bw':100}

    net.addLink(router,client,cls=TCLink, **linkopt)
    net.addLink(router,server,cls=TCLink, **linkopt)
    
    net.build()

    router.cmd("ifconfig router-eth0 0")
    router.cmd("ifconfig router-eth1 0")

    client.cmd("ifconfig client-eth0 0")

    server.cmd("ifconfig server-eth0 0")

    router.cmd("echo 1 > /proc/sys/net/ipv4/ip_forward")
    router.cmd("ifconfig router-eth0 10.0.0.1 netmask 255.255.255.0")
    router.cmd("ifconfig router-eth1 10.0.64.1 netmask 255.255.255.0")

    client.cmd("ifconfig client-eth0 10.0.0.2 netmask 255.255.255.0")

    server.cmd("ifconfig server-eth0 10.0.64.2 netmask 255.255.255.0")

    client.cmd("ip rule add from 10.0.0.2 table 1")

    client.cmd("ip route add 10.0.0.0/24 dev client-eth0 scope link table 1")
    client.cmd("ip route add default via 10.0.0.1 dev client-eth0 table 1")
    client.cmd("ip route add default scope global nexthop via 10.0.0.1 dev client-eth0")

    server.cmd("ip rule add from 10.0.64.2 table 1")

    server.cmd("ip route add 10.0.64.0/24 dev server-eth0 scope link table 1")
    server.cmd("ip route add default via 10.0.64.1 dev server-eth0 table 1")
    server.cmd("ip route add default scope global nexthop via 10.0.64.1 dev server-eth0")

    CLI(net)
    net.stop()