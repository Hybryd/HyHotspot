# HyHotspot

### Description
This project contains the needed files to create an Access Point (AP) using the NodeMCU board linked with a SD card shield. The website is stored in the root directory of the SD card and supports.

### Hardware
* NodeMCU board (see [nodeMCU's Github repository], [nodeMCU's website])
* Micro SD card shield
* Micro SD card
* Wiring:
    - **NodeMCU** ---  **MicroSD card adapter**
    - Vin --- VCC
    - GND --- GND
    - D5 --- SCK
    - D6 --- MISO
    - D7 --- MOSI
    - D2 --- CS

**Note**: Problems can appear if SD card's VCC is connected to NodeMCU's 3v3

### Installation
* Clone the git directory

        git clone https://github.com/Hybryd/HyHotspot.git

* Choose which hotspot you want to simulate, e.g. *FreeWifi*.
* Copy the webstite into the root directory of the SD card (e.g. the content of *FreeWifi/site*), and put the SD card in the shield.
* Install the ESP8266 library for Arduino IDE (see [ESP/Arduino Github repository])
* Compile the Arduino code (e.g. FreeWifi/FreeWifi/FreeWifi.ino) and transfer it into the NodeMCU.
* Reboot the NodeMCU and wait. You should see the hotspot appearing as soon as the NodeMCU has reboot. Login and passwords are stored in the *ids* file on the SD card and also written on the serial port.
 
### Remarks
  This project is to be used for educational purposes only. The author creator is in no way responsible for any misuse of the files provided.
  The title of each simulated hotspot will be "*WARNING - THIS IS A FAKE HOTSPOT*"

   [nodeMCU's website]: <http://nodemcu.com/index_en.html>
   [nodeMCU's Github repository]: <https://github.com/nodemcu/nodemcu-firmware>
   [ESP/Arduino Github repository]: <https://github.com/esp8266/Arduino>
   
