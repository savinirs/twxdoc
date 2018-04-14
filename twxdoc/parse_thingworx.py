# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os, sys
import logging
import argparse


if not __package__:
    path = os.path.join(os.path.dirname(__file__), os.pardir)
    sys.path.insert(0, path)

import TWXXMLParser
import TWXEntityParser
import TWXDataParser


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

    if args.folder == "":
        args.folder = os.path.join(os.path.dirname(args.sourcefile),
                                   os.path.splitext(os.path.basename(args.sourcefile))[0] + '_export')

    return args.sourcefile, args.folder, kw


if __name__ == '__main__':
    source_file, rootfolder, kw = commandline_parser()

    twx_parser = None
    if source_file.lower().endswith('.xml'):
        twx_parser = TWXXMLParser.ThingworxXMLParser(source_file, rootfolder,**kw)

        print("file:{}, folder:{}, kw:{}".format(source_file, rootfolder, kw))
        twx_parser.export()
        print("Done for {}.".format(source_file))
    elif source_file.lower().endswith('.json') and kw.get('isData'):
        twx_parser = TWXDataParser.ThingworxJSONDataParser(source_file, rootfolder, **kw)
    elif source_file.lower().endswith('.json') and (not kw.get('isData')):
        twx_parser = TWXEntityParser.ThingworxJSONEntityParser(source_file, rootfolder, **kw)

    print("file:{}, folder:{}, kw:{}".format(source_file, rootfolder, kw))

    if twx_parser != None:
        twx_parser.export()
        print("Done for {}.".format(source_file))
    else:
        print("Unsupported format!")