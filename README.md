# Domoticz X10 plugin (based on Mochad)

Untill now i integrated my CM15Pro by using Homegenie as an adapter for X10. From Domoticz I was sending HTTP-commands to Homegenie. The reason for this was that:
- Dimming was not supported by the Domoticz-X10 Mochad plugin
- Mochad sometimes hangs

Therefore I created a plugin which solves this. 

## Requirements
- Only tested on Raspberry PI 2 (Should work on all platforms)
- For Mochad restarting to work a Linux platform is needed with `pkill` installed

## Key features
- Direct integratrion with Mochad
- Dimming support
- Will create devices when detected (easy to by sending command: `echo "pl a1 on | nc localhost 1099"`)
- Will check Domoticz <-> Mochad <-> X10-unit (CM15) connectivity on heartbeat
- Optionally restarts Mochad when the Mochad-command is specified in the configuration

## Installation
- Currently the beta-version of Domoticz has the plugin-functionality enabled, so this is needed
- Create a directory under <Domoticz-folder>/plugins/ named X10_mochad for example
- Put the plugin.py in that directory
- Restart Domoticz

## Configuration
- In Domoticz the hardware can be added
- See configuration options in the hardware-config
