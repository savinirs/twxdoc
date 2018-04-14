# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import html
import sys
import json
import re

if not __package__:
    path = os.path.join(os.path.dirname(__file__), os.pardir)
    sys.path.insert(0, path)


class ThingworxJSONDataParser:
    def __init__(self, filename, rootfolder, **kw):
        self.sourcefile = filename
        self.rootfolder = rootfolder
        self.tree = None
        self.root = None

        self.exportIndividualMashup = kw.get("exportIndividualMashup",True)
        self.exportIndividualTemplate = kw.get("exportIndividualTemplate", True)
        self.exportIndividualShape = kw.get("exportIndividualShape", True)
        self.exportIndividualThing = kw.get("exportIndividualThing", True)
        self.exportService = kw.get("exportService", True)
        self.usespace = kw.get("usespace", False)
        self.filerecord = kw.get("filerecord", 1000)

        self.cleanTags = kw.get("cleanTags", False)
        self.cleanProject = kw.get("cleanProject", False)
        self.commentLast = True

        if (not os.path.exists(self.sourcefile)) or (not os.path.isfile(self.sourcefile)):
            raise FileNotFoundError("Can't find file:{}.".format(self.sourcefile))

    def read_in_chunks(self, file_object, chunk_size = 1024):
        while True:
            data = file_object.read(chunk_size)
            if not data:
                break

            yield data

    def export(self):
        if (not os.path.exists(self.rootfolder)) or (not os.path.isdir(self.rootfolder)):
            os.makedirs(self.rootfolder)

        export_file = None
        file_counter = 0
        total_record = 0
        scheme_str = None
        object_str = None
        current_str = None
        end_of_file = False

        position_reg = re.compile(r'}\s?{') #search } { with space or newline between zero or more times.

        breakletter = "\n"
        if self.usespace:
            breakletter = " "

        #if total_record % self.file_record == 0, there may be a bug.
        with open(self.sourcefile, 'r') as json_data:
            found_start = False
            json_str = ""
            found_end = False
            remaining_str = ""
            for piece in self.read_in_chunks(json_data,1024):
                #print('{}:piece:{}'.format(stopcounter, piece))

                remaining_str = remaining_str.strip() + piece.strip('\n').strip()
                #print("{}:{}".format(stopcounter, remaining_str))

                continue_check = True
                while continue_check:
                    if remaining_str.strip().strip('\n') == "":
                        continue_check=False
                    else:
                        if not found_start:
                            # if remaining_str[0] != '{':
                            #     raise ValueError("Can't find start of JSON string '{'.")
                            if remaining_str[0] == '{':
                                found_start = True

                        ret = position_reg.search(remaining_str)
                        if ret:
                            (end_index, nextStart_index) = ret.span(0)
                            # found a new break;
                            json_str = remaining_str[0:end_index + 1]
                            remaining_str = (remaining_str[nextStart_index - 1:]).strip()
                            found_end = True

                        elif remaining_str.strip('\n').strip().endswith('"end":true}'):
                            #end of file found
                            end_of_file = True
                            json_str = remaining_str
                            remaining_str = ""
                            found_end = True


                        if not found_end:
                            continue_check = False

                        if found_end:
                            if json_str.strip() == "":
                                raise ValueError("Found an empty json str.")

                            #processing json string
                            #print("{}:found json string:{}".format(total_record, json_str))
                            #print("{}:remaining str:{}".format(stopcounter, remaining_str))
                            if scheme_str == None:
                                scheme_str = json_str
                            elif object_str == None:
                                object_str = json_str
                            else:
                                current_str = json_str

                                if total_record % self.filerecord == 0:
                                    export_file_name = os.path.join(self.rootfolder,
                                                                    '{}-{}.json'.format(
                                                                        os.path.splitext(
                                                                            os.path.basename(self.sourcefile))[
                                                                            0],
                                                                        file_counter
                                                                    ))
                                    file_counter += 1
                                    print("{}:exporting to:{}".format(file_counter, export_file_name))
                                    if export_file != None:
                                        if not end_of_file:
                                            export_file.write(breakletter+'{"end":true}')
                                        export_file.flush()
                                        export_file.close()

                                    export_file = open(export_file_name, "w")
                                    export_file.write(scheme_str)
                                    export_file.write(breakletter + object_str)

                                export_file.write(breakletter + current_str)
                                total_record += 1

                            found_start = False
                            found_end = False
                            json_str = ""


        if export_file != None:
            #export_file.write(breakletter + '{"end":true}')
            export_file.flush()
            export_file.close()

        print("total record:{}".format(total_record-1))



