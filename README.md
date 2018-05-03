# twxdoc

1) make sure you have installed python 3.6.x+
2) make sure you have installed pip
3) git clone https://github.com/xudesheng/twxdoc
4) cd twxdoc
5) pip install -r requirements.txt


# How to Parse XML file
1) Download thingworx entities as xml file. (for example: AllEntities.xml)
2) python twxodc/parse_thingworx.py -file <path>/AllEntities.xml
3) XML file will be splitted into differnet pieces under folder <path>/AllEntities_export folder. (AllEntities can be any file name you gave)


# How to decode a TWX file
1) java -jar ./3rdparty/twxtool-1.01.jar -d <filename>.twx
  
# How to encode a json file to twx file
2) java -jar ./3rdparty/twxtool-1.01.jar -e <filename>.json
