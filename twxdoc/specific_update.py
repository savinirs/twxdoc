# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os, sys
import logging
import argparse


if not __package__:
    path = os.path.join(os.path.dirname(__file__), os.pardir)
    sys.path.insert(0, path)

import TWXSpecificUpdate

def commandline_parser():
    cmd_parser = argparse.ArgumentParser("TWX parser command line.")
    cmd_parser.add_argument('-file', action = "store", dest = 'sourcefile', required = True,
                            help = "XML file for parser and export.")
    cmd_parser.add_argument('-folder', action = "store", dest="folder", required=False,
                            default = "", help="folder to save exported content, default is file name+export.")
    cmd_parser.add_argument('-noindividual', action='store_false', dest = 'individual', required=False,
                            default = True, help="whether export individual thing/template/shape/mashup or not.")
    cmd_parser.add_argument('-noservice', action='store_false', dest='service', required=False,
                            default=True, help="whether export individual thing/template/shape/mashup or not.")
    cmd_parser.add_argument('-data', action='store_true', dest='isData', required = False,
                            default=False, help="JSON file for data, not entity.")
    cmd_parser.add_argument('-filerecord', action='store', dest='filerecord', required = False,
                            default = '1000', help='how many record will be stored during split, default is 1000')
    cmd_parser.add_argument('-usespace', action='store_true', dest='usespace',required=False,
                            default=False, help="add blank or enter for readbility. default is enter.")
    cmd_parser.add_argument('-name', action="store", dest='newname', required=False,
                            help="application key name to update")
    cmd_parser.add_argument('-key', action="store", dest='newkeyid', required=False,
                            help="new key id")
    cmd_parser.add_argument('-specific', action='store_true', dest='specific', required=False,
                            default=False, help="specific update?")
    cmd_parser.add_argument('-remove', action='store_true', dest='remove', required = False,
                            default = False, help = "indicate whether you want to remove specific node from root")
    cmd_parser.add_argument('-nodeName', action="store", dest="nodeName", required=False,
                            default="", help = "node name to remove, for example:ApplicationKey")
    cmd_parser.add_argument('-attName', action="store", dest="attName", required=False,
                            default="", help="attribute name of node to search for")
    cmd_parser.add_argument('-attValues', nargs="*", dest="attValues", required=False,
                            default="", help="attribute value of node to search for")

    args = cmd_parser.parse_args()
    kw = {}

    filerecord = int(args.filerecord)
    kw['exportIndividualTemplate'] = args.individual
    kw['exportIndividualThing'] = args.individual
    kw['exportIndividualShape'] = args.individual
    kw['exportIndividualMashup'] = args.individual
    kw['exportService'] = args.service
    kw['isData'] = args.isData
    kw['filerecord'] = filerecord
    kw['usespace'] = args.usespace
    kw['newname'] = args.newname
    kw['newkeyid'] = args.newkeyid
    kw['specific'] = args.specific
    kw['remove']=args.remove
    kw['nodeName'] = args.nodeName
    kw['attName'] = args.attName
    kw['attValues'] = args.attValues

    if args.folder == "":
        args.folder = os.path.join(os.path.dirname(args.sourcefile),
                                   os.path.splitext(os.path.basename(args.sourcefile))[0] + '_export')

    return args.sourcefile, args.folder, kw


if __name__ == '__main__':
    source_file, rootfolder, kw = commandline_parser()

    print("file:{}, folder:{}, kw:{}".format(source_file, rootfolder, kw))
    # if kw.get("specific", False):
    #     newname = kw.get("newname", "")
    #     newkeyid = kw.get("newkeyid", "")
    #     if newname=="" or newkeyid=="":
    #         raise ValueError("name and new key can't be empty!{}-->{}".format(newname,newkeyid))
    #
    #     twx_parser = TWXSpecificUpdate.SpecificUpdate(source_file, rootfolder, **kw)
    #
    #     twx_parser.UpdateApplicationKey(newname,newkeyid)
    twx_parser = TWXSpecificUpdate.SpecificUpdate(source_file, rootfolder, **kw)
    if kw.get("remove",False):
        twx_parser.RemoveNodes(**kw);

    print("Done for {}.".format(source_file))