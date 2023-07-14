import json
import os
from pathlib import Path
import pickle
import sys

import docker

try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

save_file_path = "/tmp/to_stop.pkl"


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

    """
    try:
        print("Removing the registry's container...")
        registry_container.stop()
    except Exception:
        pass
    """
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

    client = docker.from_env()
    if sys.argv[1] == "start":
        try:
            with open("config.json", "r") as fs:
                config: dict = json.load(fs)
            targets = [
                config["base_ip"].format(id=id)
                for id in range(1, config["containers_n"] + 1)
            ]

            print(targets)
            print("Building gameserver image")
            gameserver_image = client.images.build(
                path="gameserver",
                tag="gameserver",
                quiet=False,
                rm=True,
                pull=True,
            )
            print("Building team vm image")
            team_vm_image = client.images.build(
                path=".",
                dockerfile="team_vm/vm.Dockerfile",
                tag="team_vm",
                quiet=False,
                rm=True,
                pull=True,
            )

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

            print("Starting Gameserver")
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
                network.connect(
                    container, ipv4_address=config["base_ip"].format(id=team)
                )
                team_containers.append(container)

            """
            print("Starting registry")
            registry_container = client.containers.run(
                image="registry:2",
                name=f"Registry",
                hostname=f"local_registry",
                auto_remove=True,
                detach=True,
                stdout=True,
                stderr=True,
            )
            for service_dir in Path("services").iterdir():
                if not service_dir.is_dir():
                    continue
                name = service_dir.stem
                service_image = client.images.build(
                    path=service_dir,
                    quiet=False,
                    tag=f"local_registry:5000/{name}",
                    rm=True,
                    pull=True,
                )
            """

            # Save objects to file
            with open(save_file_path, "wb") as fs:
                pickle.dump(
                    (
                        gameserver_container.id,
                        [t.id for t in team_containers],
                        network.id,
                        created_network,
                    ),
                    fs,
                )
        except Exception:
            exit_handler()
            raise
        else:
            print("Done")

    elif sys.argv[1] == "stop":
        # Load objects from file
        try:
            with open(save_file_path, "rb") as fs:
                loaded_objects = pickle.load(fs)
            (
                gameserver_container_id,
                team_containers_ids,
                network_id,
                created_network,
            ) = loaded_objects

            gameserver_container = client.containers.get(gameserver_container_id)
            team_containers = [
                client.containers.get(t_id) for t_id in team_containers_ids
            ]
            network = client.networks.get(network_id)

        except Exception:
            print("Can't find resources to remove")
            exit()
        exit_handler()
        os.remove(save_file_path)
