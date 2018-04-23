# -*- coding: utf-8 -*-
#!/usr/bin/env python

import xml.etree.ElementTree as ET
import os
import html
import sys


if not __package__:
    path = os.path.join(os.path.dirname(__file__), os.pardir)
    sys.path.insert(0, path)


class SpecificUpdate:
    def __init__(self, filename, rootfolder, **kw):
        self.xmlfile = filename
        self.rootfolder = rootfolder
        self.tree = None
        self.root = None

        self.exportIndividualMashup = kw.get("exportIndividualMashup",True)
        self.exportIndividualTemplate = kw.get("exportIndividualTemplate", True)
        self.exportIndividualShape = kw.get("exportIndividualShape", True)
        self.exportIndividualThing = kw.get("exportIndividualThing", True)
        self.exportService = kw.get("exportService", True)

        self.cleanTags = kw.get("cleanTags", False)
        self.cleanProject = kw.get("cleanProject", False)
        self.commentLast = True

        if (not os.path.exists(self.xmlfile)) or (not os.path.isfile(self.xmlfile)):
            raise FileNotFoundError("Can't find file:{}.".format(self.xmlfile))

        self.tree = ET.ElementTree(file=self.xmlfile)
        self.root = self.tree.getroot()
        print("Tree:{}, Root:{}, len:{}".format(self.tree, self.root.tag, len(self.root)))

    def UpdateApplicationKey(self,name, newkey):
        #update a specific application key with new value
        if self.tree == None or self.root == None:
            raise ValueError("Can't find parsed tree or root element.")

        export_file = os.path.join(os.path.dirname(self.xmlfile),
                                   os.path.splitext(os.path.basename(self.xmlfile))[0] + '_update.xml')

        targetNodes = self.root.findall(
            "./ApplicationKeys/ApplicationKey[@name='{}']".format(name)
        )

        if len(targetNodes)>1:
            raise ValueError("There should be only one node available!")

        for targetNode in targetNodes:
            targetNode.attrib["keyId"] = newkey

        parentNodes = self.root.findall(
            "./PersistenceProviders"
        )

        for parentNode in parentNodes:
            targetNodes = parentNode.findall(
                "./PersistenceProvider[@name='{}']".format('HTC.ForAlertPP')
            )
            for targetNode in targetNodes:
                print("node {} is being removed.".format(targetNode.attrib.get("name")))
                parentNode.remove(targetNode)

        self.tree.write(export_file, encoding = "UTF-8", xml_declaration=True)
        print("Update {} to {}".format(self.xmlfile, export_file))




