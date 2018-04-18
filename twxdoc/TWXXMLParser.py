# -*- coding: utf-8 -*-
#!/usr/bin/env python

import xml.etree.ElementTree as ET
import os
import html
import sys


if not __package__:
    path = os.path.join(os.path.dirname(__file__), os.pardir)
    sys.path.insert(0, path)


class ThingworxXMLParser:
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

    def export(self):
        if self.tree == None or self.root == None:
            raise ValueError("Can't find parsed element tree or can't get root.")

        if (not os.path.exists(self.rootfolder)) or (not os.path.isdir(self.rootfolder)):
            os.makedirs(self.rootfolder)

        for child in self.root:
            newroot = ET.Element(self.root.tag, self.root.attrib)
            newtree = ET.ElementTree(newroot)
            newroot.append(child)

            export_file = os.path.join(self.rootfolder, "{}.xml".format(child.tag))
            newtree.write(export_file, encoding = "UTF-8", xml_declaration=True)
            print("Exported {} to {}".format(child.tag, export_file))

        self.exportThingShapeDependences()
        self.exportThingTemplateDependences()

        if self.exportIndividualMashup:
            self.exportOneComponent("Mashup")

        if self.exportIndividualShape:
            self.exportOneComponent("ThingShape")

        if self.exportIndividualTemplate:
            self.exportOneComponent("ThingTemplate")

        if self.exportIndividualThing:
            self.exportOneComponent("Thing")

        if self.exportService:
            self.exportObjectService()

    def exportThingTemplateDependences(self):
        targetNodes = self.root.findall(
            "./ThingTemplates/ThingTemplate/Subscriptions/Subscription[@source]"
        )
        templateDependentThings = []
        for child in targetNodes:
            sourceName = child.attrib.get("source")
            if sourceName != None and sourceName != "":
                if not sourceName in templateDependentThings:
                    templateDependentThings.append(sourceName)

        if len(templateDependentThings) > 0:
            self.exportDependent("templateDependents", "Thing", templateDependentThings)

    def exportThingShapeDependences(self):

        #search for shape dependent template
        targetNodes = self.root.findall(
            './ThingShapes/ThingShape/PropertyDefinitions/PropertyDefinition[@aspect.thingTemplate]')

        shapeDependentTemplates = []
        for child in targetNodes:
            templateName = child.attrib.get("aspect.thingTemplate")
            if not templateName in shapeDependentTemplates:
                shapeDependentTemplates.append(templateName)

        #search for shape dependent thing
        targetNodes = self.root.findall("./ThingShapes/ThingShape/Subscriptions/Subscription[@source]")
        shapeDependentThings = []
        for child in targetNodes:
            sourceName = child.attrib.get("source")
            if sourceName != None and sourceName != "":
                if not sourceName in shapeDependentThings:
                    shapeDependentThings.append(sourceName)

        #search for thing of shape dependent template
        for templateName in shapeDependentTemplates:
            targetNodes = self.root.findall(
                "./ThingTemplates/ThingTemplate[@name='{}']/Subscriptions/Subscription[@source]".format(templateName)
            )
            for child in targetNodes:
                sourceName = child.attrib.get("source")
                if sourceName != None and sourceName != "":
                    if not sourceName in shapeDependentThings:
                        shapeDependentThings.append(sourceName)

        if len(shapeDependentTemplates)>0:
            self.exportDependent("ShapeDependents", "ThingTemplate", shapeDependentTemplates)

        if len(shapeDependentThings) > 0:
            self.exportDependent("ShapeDependents", "Thing", shapeDependentThings)

    def exportDependent(self, subfoldername, dependentType, dependent_list):
        exportfolder = os.path.join(self.rootfolder, subfoldername,dependentType)
        if not os.path.exists(exportfolder):
            os.makedirs(exportfolder)

        group_node = self.root.find("./{}s".format(dependentType))
        if group_node == None:
            raise ValueError("Can't find group type:{}s".format(dependentType))

        for dependence in dependent_list:
            dependenceNode = self.root.find("./{}s/{}[@name='{}']".format(
                dependentType,
                dependentType,
                dependence
            ))
            if dependenceNode != None:
                filename = "{}.xml".format(dependence)
                exportfile = os.path.join(exportfolder, filename)
                newroot = ET.Element(self.root.tag, self.root.attrib)
                newtree = ET.ElementTree(newroot)
                newroot.append(group_node)
                group_node.append(dependenceNode)

                newtree.write(exportfile, encoding="UTF-8", xml_declaration=True)
                print("Exported dependent:{}".format(exportfile))


    def exportObjectService(self):
        objectTypes = ['Thing', 'ThingShape', 'ThingTemplate']


        for objectType in objectTypes:
            objectNodes = self.root.findall('./{}s/{}'.format(objectType, objectType))
            unknown_index = 0
            for objectNode in objectNodes:
                objectName = objectNode.attrib.get("name", "Unknown_{}".format(unknown_index))
                #print("Processing...{}".format(objectName))

                unknown_index += 1
                self.exportOneNodeService(objectType, objectName, objectNode, self.rootfolder, self.commentLast)
                self.exportOneNodeSubscription(objectType, objectName, objectNode, self.rootfolder, self.commentLast)

    def retriveServiceContent(self, objectType, objectName, objectNode, serviceDefinitionNode):
        # retrive service of current serviceDefinition
        # return service name, code and comment
        serviceName = serviceDefinitionNode.attrib.get("name", None)
        if serviceName == None:
            # print("serviceName is None!")
            return None, None, None, None

        serviceImplementationNode = objectNode.find(".//ServiceImplementation[@name='{}']".format(serviceName))
        serviceComment = self.retriveServiceDefinitionContent(serviceDefinitionNode, serviceName)
        serviceCode, fileext = self.retriveServiceCodeContent(serviceImplementationNode)

        return serviceName, serviceComment, serviceCode, fileext

    def retriveServiceCodeContent(self,serviceImpNode):
        # return code and file type
        if serviceImpNode == None:
            return "", ""

        handlerName = serviceImpNode.attrib.get("handlerName")
        # serviceName = serviceImpNode.attrib.get("name")
        codetext = ""
        fileext = ""

        if handlerName != None and handlerName != "":
            # serviceName = serviceName.replace(":","_") #convert subscription name
            codeNodes = None
            if handlerName == "Script":
                fileext = ".js"
                codeNodes = serviceImpNode.findall(".//code")
            elif handlerName == "SQLCommand":
                fileext = ".sql"
                codeNodes = serviceImpNode.findall(".//sql")
            elif handlerName == "SQLQuery":
                fileext = ".sql"
                codeNodes = serviceImpNode.findall(".//sql")

            if codeNodes is None:
                return "", ""
            for codeNode in codeNodes:
                if codeNode.text != None and codeNode.text != "":
                    codetext += html.unescape(codeNode.text)

        return codetext, fileext

    def retriveServiceDefinitionContent(self, serviceDefinitionNode, serviceName):
        serviceComment = "/*//==========Definition of Service:{}==========\n".format(serviceName)
        for attribName, attribValue in serviceDefinitionNode.attrib.items():
            serviceComment += "// {}-->{}:{}\n".format(serviceName, attribName, attribValue)

        serviceComment += "//=============Result and input parameters=========\n"
        resultTypeNode = serviceDefinitionNode.find(".//ResultType")
        if resultTypeNode != None:
            serviceComment += "// {} return-->{}, BaseType:{}, Desc:{}\n".format(serviceName,
                                                                                 resultTypeNode.attrib.get("name",
                                                                                                           "Unknown"),
                                                                                 resultTypeNode.attrib.get("baseType",
                                                                                                           "Unknown"),
                                                                                 html.unescape(
                                                                                     resultTypeNode.attrib.get(
                                                                                         "description", "")))

        fieldDefinitionNodes = serviceDefinitionNode.findall("./ParameterDefinitions/FieldDefinition")
        for fieldDefinition in fieldDefinitionNodes:
            serviceComment += "// {} Input -->{},\tBaseType:{},\tDefaultValue:{},\tDesc:{}\n".format(
                serviceName,
                fieldDefinition.attrib.get("name", "Unknown"),
                fieldDefinition.attrib.get("baseType", "Unknown"),
                html.unescape(fieldDefinition.attrib.get("aspect.defaultValue", "")),
                html.unescape(fieldDefinition.attrib.get("description", "")))
        serviceComment += "*/"

        return serviceComment

    def exportOneNodeService(self, objectType, objectName, objectNode, rootFolder, exportCommentLast=True):
        # objectType: thing, thingTemplate, thingShape

        serviceDefinitionNodes = objectNode.findall('.//ServiceDefinition')
        if serviceDefinitionNodes is None:
            # print("no service definition node found for {}".format(objectName))
            return
        # print("service definition:{}".format(len(serviceDefinitionNodes)))

        for serviceDefinitionNode in serviceDefinitionNodes:
            serviceName = serviceDefinitionNode.attrib.get("name", "")
            # print("Ready to process service:{}".format(serviceName))

            serviceName, serviceComment, serviceCode, fileext = self.retriveServiceContent(objectType,
                                                                                      objectName,
                                                                                      objectNode,
                                                                                      serviceDefinitionNode)

            if serviceName == None or serviceName == "" or fileext == "":
                # print("nothing can be found for objectName{}, service:{}, ext:{}".format(objectName,
                #                                                                         serviceName,
                #                                                                         fileext))
                continue

            fileName = "{}{}".format(serviceName.replace(":", "_"), fileext)

            exportfolder = os.path.join(rootFolder, 'service', objectType, objectName)
            if not os.path.exists(exportfolder):
                os.makedirs(exportfolder)

            exportfile = os.path.join(exportfolder, fileName)

            print("Exporting:{}".format(exportfile))

            with open(exportfile, "a") as servicefile:
                if not exportCommentLast:
                    servicefile.write(serviceComment)
                    servicefile.write("\n")
                servicefile.write(serviceCode)
                if exportCommentLast:
                    servicefile.write("\n")
                    servicefile.write(serviceComment)

    # export subscription from one node

    def retriveSubscriptionContent(self, objectType, objectName, objectNode, subscriptionNode):
        # retrive Subscription service of current serviceDefinition
        # return service name, code and comment

        serviceImplementationNode = subscriptionNode.find(".//ServiceImplementation")
        if serviceImplementationNode == None:
            return None, None, None, None

        serviceName = serviceImplementationNode.attrib.get("name", None)
        serviceComment = self.retriveSubscriptionComment(subscriptionNode, serviceName)
        serviceCode, fileext = self.retriveServiceCodeContent(serviceImplementationNode)

        return serviceName, serviceComment, serviceCode, fileext

    def retriveSubscriptionComment(self, subscriptionNode, serviceName):
        serviceComment = "/*//==========Definition of Subscription:{}==========\n".format(serviceName)
        for attribName, attribValue in subscriptionNode.attrib.items():
            serviceComment += "// {}-->{}:{}\n".format(serviceName, attribName, attribValue)

        serviceComment += "*/"

        return serviceComment

    def exportOneNodeSubscription(self, objectType, objectName, objectNode, rootFolder, exportCommentLast=True):
        # objectType: thing, thingTemplate, thingShape

        subscriptionNodes = objectNode.findall('.//Subscription')
        if subscriptionNodes is None:
            # print("no subscription definition node found for {}".format(objectName))
            return
        # print("service definition:{}".format(len(serviceDefinitionNodes)))

        for subscriptionNode in subscriptionNodes:
            serviceName, serviceComment, serviceCode, fileext = self.retriveSubscriptionContent(objectType,
                                                                                           objectName,
                                                                                           objectNode,
                                                                                           subscriptionNode)

            if serviceName == None or serviceName == "" or fileext == "":
                # print("nothing can be found for objectName{}, service:{}, ext:{}".format(objectName,
                #                                                                         serviceName,
                #                                                                         fileext))
                continue

            fileName = "{}{}".format(serviceName.replace(":", "_"), fileext)

            exportfolder = os.path.join(rootFolder, 'subscription', objectType, objectName)
            if not os.path.exists(exportfolder):
                os.makedirs(exportfolder)

            exportfile = os.path.join(exportfolder, fileName)

            print("Exporting:{}".format(exportfile))

            with open(exportfile, "a") as servicefile:
                if not exportCommentLast:
                    servicefile.write(serviceComment)
                    servicefile.write("\n")
                servicefile.write(serviceCode)
                if exportCommentLast:
                    servicefile.write("\n")
                    servicefile.write(serviceComment)


    def exportOneComponent(self,component_name):
        #export mashup, thing, thingShape, Thing Template etc
        group_node = self.root.find("./{}s".format(component_name))
        if group_node == None:
            #raise ValueError("Can't find node parent for node:{}".format(component_name))
            return  #if only export from single file like thing.xml

        component_nodes = group_node.findall("./{}".format(component_name))
        component_folder = ""
        if len(component_nodes) > 0:
            component_folder=os.path.join(self.rootfolder, component_name)
            if not os.path.exists(component_folder):
                os.makedirs(component_folder)

        unknown_index = 0
        for child in component_nodes:
            newroot = ET.Element(self.root.tag, self.root.attrib)
            newtree = ET.ElementTree(newroot)

            new_group_node = ET.Element(group_node.tag, group_node.attrib)
            newroot.append(new_group_node)
            new_group_node.append(child)

            individual_name = child.get("name", "unknown_{}_{}".format(component_name, unknown_index))
            unknown_index += 1
            individual_filename = "{}.xml".format(individual_name)
            export_file = os.path.join(component_folder, individual_filename)

            newtree.write(export_file, encoding="UTF-8", xml_declaration=True)


