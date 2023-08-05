import os
import pickle
import sys
import tomllib
from pathlib import Path

import docker
import requests

try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

save_file_path = "/tmp/to_stop.pkl"

client = docker.from_env()


def stop():
    global gameserver_container, team_containers, network, created_network, mongodb_container

    try:
        # Load objects from file
        with open(save_file_path, "rb") as fs:
            loaded_objects = pickle.load(fs)
        (
            gameserver_container_id,
            team_containers_ids,
            network_id,
            created_network,
            mongodb_container_id,
        ) = loaded_objects

        try:
            gameserver_container = client.containers.get(gameserver_container_id)
        except requests.exceptions.HTTPError:
            pass

        try:
            team_containers = [
                client.containers.get(t_id) for t_id in team_containers_ids
            ]
        except requests.exceptions.HTTPError:
            pass

        try:
            network = client.networks.get(network_id)
        except requests.exceptions.HTTPError:
            pass

        try:
            mongodb_container = client.containers.get(mongodb_container_id)
        except requests.exceptions.HTTPError:
            pass

    except FileNotFoundError:
        print("Can't find resources to remove")
    except Exception:
        raise
    else:
        exit_handler()


def start():
    if Path(save_file_path).exists():
        print("There's already an instance running")
        exit()

    try:
        global gameserver_container, team_containers, network, created_network, mongodb_container
        with open("config.toml", "rb") as fs:
            config: dict = tomllib.load(fs)
        targets = [
            config["base_ip"].format(id=id)
            for id in range(1, config["containers_n"] + 1)
        ]

        print(targets)
        print("Building gameserver image")
        gameserver_image, _ = client.images.build(
            path="gameserver",
            tag="gameserver",
            quiet=False,
            rm=True,
            pull=True,
        )
        print("Building team vm image")
        team_vm_image, _ = client.images.build(
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

        print("Starting DB")
        mongodb_container = client.containers.run(
            image="mongo:jammy",
            name="mongo",
            hostname="mongo",
            auto_remove=True,
            detach=True,
            stdout=True,
            stderr=True,
        )
        network.connect(mongodb_container)

        print("Starting Gameserver")
        gameserver_container = client.containers.run(
            image=gameserver_image,
            name="Gameserver",
            hostname="gameserver",
            detach=True,
            auto_remove=True,
            stdout=True,
            stderr=True,
        )
        network.connect(gameserver_container, ipv4_address=config["gameserver_ip"])

        print("Starting teams' containers")
        team_containers = []
        for team in range(1, config["containers_n"] + 1):
            container = client.containers.run(
                image=team_vm_image.id,
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

        # Pre-building services
        # To have this work properly we need a function that scans docker-compose files and extract all the relevant information for pre-building the images
        """
        for service_dir in Path("services").iterdir():
            if not service_dir.is_dir():
                continue
            name = service_dir.stem
            service_image = client.images.build(
                path=service_dir,
                quiet=False,
                tag=name,
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
                    mongodb_container.id,
                ),
                fs,
            )
    except docker.errors.BuildError:
        print("[ERROR] Unable to connect to dockerhub, please check your connection.")
        exit_handler()
    except Exception:
        exit_handler()
        raise
    else:
        print("Done")
        print(
            "Starting the services may take a while! Please be patient while the containers build"
        )
        print(
            "If you want to check, attach a shell to any of the team containers and run\n`journalctl --follow -u services_starter.service`\nor\n`systemctl status services_starter.service`"
        )


def exit_handler():
    try:
        print("Press CTRL+C to force quitting but be wary of dangling resources.")
        try:
            print("Removing the gameserver's container...")
            gameserver_container.stop()
        except Exception:
            pass

        try:
            print("Removing the database's container...")
            mongodb_container.stop()
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
    except KeyboardInterrupt:
        pass
    try:
        os.remove(save_file_path)
    except FileNotFoundError:
        pass


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Please provide a command: start, stop or restart")
        exit()

    if sys.argv[1] == "stop":
        stop()
    elif sys.argv[1] == "start":
        start()
    elif sys.argv[1] == "restart":
        stop()
        start()
