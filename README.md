# twxdoc installation

1) make sure you have installed python 3.6.x+
2) make sure you have installed pip
3) git clone https://github.com/xudesheng/twxdoc
4) cd twxdoc
5) pip install -r requirements.txt


# How to Parse XML file
1) Download thingworx entities as xml file. (for example: AllEntities.xml)
2) python twxodc/parse_thingworx.py -file yourpath/AllEntities.xml
3) XML file will be splitted into differnet pieces under folder yourpath/AllEntities_export folder. (AllEntities can be any file name you gave)


# How to decode a TWX file to JSON file
1) java -jar ./3rdparty/twxtool-1.01.jar -d yourfilename.twx
  
# How to encode a JSON file to TWX file
2) java -jar ./3rdparty/twxtool-1.01.jar -e yourfilename.json
