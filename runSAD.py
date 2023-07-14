import json
import sys

import docker

try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

import atexit


def exit_handler():
    print("Quitting")
    print(
        "Press CTRL+C again if you want to kill me immediately but be wary of dangling resources."
    )
    try:
        print("Removing the gameserver's container...")
        gameserver_container.stop()
    except Exception:
        pass

    try:
        print("Removing the teams' containers:")
        for t in team_containers:
            print("Removed ", t.name)
            t.stop()
    except Exception:
        pass

    try:
        if created_network:
            print("Removing the game network...")
            network.remove()
    except Exception:
        pass


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Please provide a command: start or stop")
        exit()
    if sys.argv[1] == "start":
        atexit.register(func=exit_handler)
        with open("config.json", "r") as fs:
            config: dict = json.load(fs)
        targets = [
            config["base_ip"].format(id=id)
            for id in range(1, config["containers_n"] + 1)
        ]

        print(targets)
        client = docker.from_env()
        gameserver_image = client.images.build(
            path="gameserver", quiet=False, tag="gameserver", rm=True, pull=True
        )
        print("got gameserver image")
        team_vm_image = client.images.build(
            path="services", quiet=False, tag="team_vm", rm=True, pull=True
        )
        print("got team vm image")

        network = None
        created_network = False
        for net in client.networks.list():
            try:
                gateway = net.attrs["IPAM"]["Config"][0]["Gateway"]
                subnet = net.attrs["IPAM"]["Config"][0]["Subnet"]
                if gateway == config["gateway"] and subnet == config["subnet"]:
                    network = client.networks.get(net.id)
            except Exception:
                continue

        if not network:
            ipam_pool = docker.types.IPAMPool(
                subnet=config["subnet"], gateway=config["gateway"]
            )
            ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])
            network = client.networks.create(
                name="game", driver="bridge", ipam=ipam_config
            )
            created_network = True

        gameserver_container = client.containers.run(
            image=gameserver_image[0].id,
            name="Gameserver",
            hostname="gameserver",
            auto_remove=True,
            detach=True,
            stdout=True,
            stderr=True,
        )
        network.connect(gameserver_container, ipv4_address=config["gameserver_ip"])
        print("Started Gameserver")
        print("Starting teams' containers")
        team_containers = []
        for team in range(1, config["containers_n"] + 1):
            container = client.containers.run(
                image=team_vm_image[0].id,
                name=f"Team_{team}",
                hostname=f"team_{team}",
                runtime="sysbox-runc",
                auto_remove=True,
                detach=True,
                stdout=True,
                stderr=True,
            )
            network.connect(container, ipv4_address=config["base_ip"].format(id=team))
            team_containers.append(container)

        print("Done")

    elif sys.argv[1] == "stop":
        exit_handler()
