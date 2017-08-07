# X10 Python Plugin 
#
# Author: Casper Polhout
#
"""
<plugin key="X10_Mochad" name="X10-plugin for Mochad with DIM-support" author="Casper Polhout" version="1.0.0" wikilink="http://" externallink="https://www.google.com/">
 <params>
  <param field="Address" label="Mochad IP Address" width="200px" required="true" default="127.0.0.1"/>
  <param field="Port" label="Mochad Port" width="100px" required="true" default="1099"/>
#  <param field="Mode1" label="HouseCode" width="30px" required="true" default="M"/>
  <param field="Mode2" label="CM15 RF repeater disabled" width="75px">
       <options>
           <option label="True" value="True"/>
           <option label="False" value="False"  default="True" />
       </options>
   </param>
   <param field="Mode4" label="Mochad Eexecutable (restarts Mochad when no response) : " width="300px" required="false" default=""/>
   <param field="Mode3" label="Debugging enabled" width="75px">
       <options>
           <option label="True" value="True"/>
           <option label="False" value="False"  default="True" />
       </options>
   </param>
 </params>
</plugin>
"""
import Domoticz
import time
import os
housecodes=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P']
con = None 
activeUnit=""
connected=False #The connection object does not give a correct value. 
mochadST=True   #This boolean will state if Mochad is reachable
mochadCMD=""

class BasePlugin:
    enabled = False
    def __init__(self):
        #self.var = 123
        return

    def onStart(self):
        global con,mochadCMD
        if Parameters["Mode3"]=="True":
            Domoticz.Debugging(1)
        if len(Parameters["Mode4"])>2:
            mochadCMD=Parameters["Mode4"]
        Domoticz.Log("X10-Mochad module started!")
        con=Domoticz.Connection(Name="Mochad", Transport="TCP/IP", Protocol="line", Address=Parameters["Address"], Port=Parameters["Port"])
        con.Connect()

    def onStop(self):
        Domoticz.Log("onStop called")
        con.Disconnect()

    def onConnect(self, Connection, Status, Description):
        global connected,mochadST
        Domoticz.Debug("Connection status:" + str(Status))
        Domoticz.Debug("Connection desc:" + str(Description))
        if con.Connected:
          Domoticz.Debug("Connection bool:TRUE")
        if Status!=0:  #Error conecting
           connected=False
           mochadST=False
           con.Disconnect()
           restartMochad()
           Domoticz.Log("Connection to Mochad error...retry in 10s")
           con.Connect()
        else:
          connected=True
          mochadST=True
          Domoticz.Log("Connected to Mochad:" + str(Status) + "," + str(Description))
          if Parameters["Mode2"]=="True":
            send("rftopl 0\n")
          else:
            send("rftopl *\n")

    def onMessage(self, Connection, Data):
        global activeUnit, mochadST
        cmd=""
        #d=str(Data)[2:-1]
        Domoticz.Debug("Mochad Received:" + str(Data))
        Domoticz.Debug("LINES:" + str(Data.splitlines()))
        for line in Data.splitlines():
          line=str(line)
          Domoticz.Debug("LINE:" + line)
          if "End status" in line:
            mochadST=True
            waitRES=False
            Domoticz.Debug("Status check succeeded!")
          if "HouseUnit" in line:
            activeUnit=line[-3:-1]
            Domoticz.Debug("Unit:" + activeUnit)
          elif "Func:" in line:
            pos=line.find("Func:")
            cmd=line[pos+6:-1]
            Domoticz.Debug("Command:" + cmd)
            #if mochadSend==(activeUnit,cmd[:3].lower()):
            #  waitRES=False
            #updateDevice(activeUnit,cmd,0)
        

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("X10 plugin called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        updateLight(Unit,str(Command), Level)


    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        global connected
        connected=False
        Domoticz.Log("onDisconnect called")

    def onHeartbeat(self):
        global connected, mochadST
        Domoticz.Debug("onHeartbeat called: MochadStatus: " + str(mochadST))
        if mochadST==False:
          restartMochad()
          mochadST==True
          con.Connect()
        if connected and con.Connected:
          mochadST=False
          send("st\n")
          waitRES=True
        else:
          con.Connect()

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data, *args):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return

def code2unit(code):
    global housecodes
    unitnr=housecodes.index(code[0])*16+int(code[1:])
    Domoticz.Debug("code=" + code + "   unit=" + str(unitnr))
    return unitnr

def unit2code(unit):
    global housecodes
    x=divmod(unit,16)
    code=housecodes[x[0]]+str(x[1])
    Domoticz.Debug("unit=" + str(unit) + "   code=" + code)
    return code

def updateDevice(unit,cmd, newLevel):
    DumpConfigToLog()
    global housecodes
    Domoticz.Debug("updateDevice called:" + str(unit) + "," + cmd + "," + str(newLevel))
    unitnr=code2unit(unit)
    if not (unitnr in Devices):
      #Domoticz.Device(Name=unit, Unit=unitnr, TypeName="Switch", Switchtype=7).Create()
      Domoticz.Device(Name=unit, Unit=unitnr, Type=17, Subtype=0, Switchtype=7).Create()
      Domoticz.Log("Created new X10-device:" + unit + " (" + str(unitnr) + ")")
    if newLevel==0:
      newLevel=Devices[unitnr].sValue
    if cmd=='On':
      Domoticz.Debug("UPDATING DEVICE TO ON IN DOMOTICZ")
      Devices[unitnr].Update(1,str(newLevel))
    elif cmd=='Off':
      Domoticz.Debug("UPDATING DEVICE TO OFF IN DOMOTICZ")
      Devices[unitnr].Update(0,str(newLevel))


def updateLight(nr, cmd, newLevel):
    DumpConfigToLog()
    code=unit2code(nr)
    lastLevel=int(Devices[nr].LastLevel)
    Domoticz.Debug("Lastlevel: " + str(lastLevel))
    if cmd.lower()=='off':
      Devices[nr].Update(0,str(newLevel))
      sendX10(code, "off")
    elif cmd.lower()=='on':
      sendX10(code, "on")
      Devices[nr].Update(1,str(newLevel))
    else:
      Domoticz.Debug("UPDATING DEVICE TO LEVEL " + str(newLevel) + " IN DOMOTICZ")
      Devices[nr].Update(1,str(newLevel))
      sendX10(code,"on", wait=False)
      if newLevel==15:
        sendX10(code, "bright 32")
      else: 
        newLevel=int(newLevel*100/15) #Switch type has 15 steps, lastLevel is based on 100%, X10 uses 32 steps
        if newLevel>lastLevel:
          dif=newLevel-lastLevel
          delta=int(32/100*dif)
          sendX10(code, "bright " + str(delta))
        elif newLevel<lastLevel:
          dif=lastLevel-newLevel
          delta=int(32/100*dif)
          sendX10(code, "dim " + str(delta))

def sendX10(code, command, wait=True):
    Domoticz.Debug("Try sending to Mochad:" + "pl " + code + " " + command.lower() + "\n")
    Domoticz.Debug("X10 Plugin send to Mochad:" + "pl " + code + " " + command.lower() + "\n")
    mochadSend=(code,command[:3].lower())
    send("pl " + code + " " + command.lower() + "\n")

def send(data):
    global connected, con
    Domoticz.Debug("Send called")
    retry=0
    while (not (connected and con.Connected)) and  retry<5:
      retry+=1
      Domoticz.Log("Connection Lost...trying to reconnect..")
      con.Connect()
      time.sleep(0.2)
    con.Send(data)

def restartMochad():
    global mochadCMD, s
    if len(mochadCMD)>2:
      Domoticz.Debug("Restarting Mochad")
      os.system("pkill -9 -f " + mochadCMD)
      os.system(mochadCMD + " >/tmp/mochad.out 2>&1")
