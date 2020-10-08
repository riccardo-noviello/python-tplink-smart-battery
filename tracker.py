#!/usr/bin/python
from tkinter import *
from tkinter import messagebox, simpledialog
import asyncio
from kasa import SmartPlug, SmartDevice, Discover
from cputemp import cputemp

def powerFunction():
    current_stat = open(
        "/sys/class/power_supply/BAT0/capacity", "r").readline().strip()
    return current_stat


def chargeState():
    charge_state = open(
        "/sys/class/power_supply/BAT0/status", "r").readline().strip()
    return charge_state


async def find_host_from_alias(alias, target="255.255.255.255", timeout=1, attempts=3):
    """Discover a device identified by its alias."""
    print(
        f"Trying to discover {alias} using {attempts} attempts of {timeout} seconds"
    )
    for attempt in range(1, attempts):
        print(f"Attempt {attempt} of {attempts}")
        found_devs = await Discover.discover(target=target, timeout=timeout)
        found_devs = found_devs.items()
        for ip, dev in found_devs:
            if dev.alias.lower() == alias.lower():
                host = dev.host
                return host
    return None


async def connect_switch_plug(alias):
    host = await find_host_from_alias(alias)

    p = SmartPlug(host)
    await p.update()
    print("")
    return p


async def switch_plug(on_off, plug):
    p = plug
    if(on_off):
        await p.turn_on()
    else:
        await p.turn_off()
    return


async def main():
    root = Tk()
    root.withdraw()

    alias = simpledialog.askstring(title="Discover TP LINK Device",
                              prompt="What's the device name?:")
    if not alias:
        messagebox.showwarning(
            "Stop!", "Device not found, closing application")
        return

    powerStat = 100
    plug = await connect_switch_plug(alias)
    messagebox.showwarning(
        "Running!", "Battry Status Tracker is now running on machine")
    while int(powerStat) >= 30:
        powerStat = powerFunction()
        chargeStat = chargeState()
        temp = cputemp.convertTemp(cputemp.readTemp())
        print(str(temp) + " °C")
        if int(powerStat) >= 99 and temp >= 70.0:
            await switch_plug(False, plug)
            messagebox.showwarning(
                "Alert!", "Battery Charged! Turning plug Off")
            break

        if int(powerStat) <= 20 and chargeStat == "Discharging":
            await switch_plug(True, plug)
            messagebox.showwarning(
                "Alert!", "Battery Low!\nCharging  Required!\nYour Battery Status:"+powerStat+"% ("+chargeStat+")\n Turning plug On")
            break


if __name__ == "__main__":
    asyncio.run(main())
