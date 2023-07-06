I'm very sad because I couldn't finish my attacker/submitter project in time for the CCIT2023 finals 😢

I always had to wait for demos to test any changes I made and they were always broken.

So now I made a **S**imple **A**ttack-**D**efense environment that I can use to test what I want when I want 🤯🤯🤯

Note: Gameserver for inserting/checking status/validating flags is still missing

# Dependencies

This project relies on [sysbox](https://github.com/nestybox/sysbox) for a good Docker-in-Docker runtime
## Debian-based:
```bash
sudo apt install sysbox
```
Make sure your Docker is installed as system package and not snap 🤢
## Other distros:
[Check if your distro is supported](https://github.com/nestybox/sysbox/blob/master/docs/distro-compat.md). We're gonna need to build from source, but it's fairly easy.
```bash
git clone --recursive https://github.com/nestybox/sysbox.git
```
```bash
make sysbox-static
```
```bash
sudo make install
```

# Configuration
Modify the config.json file according to your needs.
Add services to the `services/` dir. 
Each service should be a directory containing at least one well-known entrypoint.
The valid entrypoints are, in order of priority:
1. deploy.sh
2. docker-compose.yml
2. docker-compose.yaml

The first entrypoint found will be used to start the service and everything else will be ignored

# Run
```bash
python3 runSAD.py start
```
```bash
python3 runSAD.py stop
```
should be pretty self-descriptive 🧐

# Disclaimer
<div>
<img style="float: left; margin: 2px 12px 2px 2px" alt="meme" src="https://koinbulteni.com/wp-content/uploads/03933cec60880354d306c92062e557db-768x470.jpg" width="220">

*So, with just a few changes I could use this to host a small A/D ctf!*

Eh. Probably. Seems like a bad idea. Do what you want, but keep in mind that this is not, never was and **probably** never will be this project's intended use. 

I did my best to have the team's containers run as close as possible as VMs but no matter what a container is not a VM.

</div>

<!-- BADGIE TIME -->
<!-- END BADGIE TIME -->