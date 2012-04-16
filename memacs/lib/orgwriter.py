# -*- coding: utf-8 -*-
# Time-stamp: <2012-04-16 20:13:03 armin>

import codecs
import sys
import time
import os
import re
import logging
from orgproperty import OrgProperties
from reader import CommonReader
from orgformat import OrgFormat


class OrgOutputWriter(object):
    """
    OrgOutputWriter is used especially for writing
    org-mode entries

    most notable function:
    - write_org_subitem (see its comment)
    """
    __handler = None
    __test = False

    def __init__(self,
                 short_description,
                 tag,
                 file_name=None,
                 test=False,
                 append=False,
                 autotag_dict={}):
        """
        @param file_name:
        """
        self.__test = test
        self.__test_data = ""
        self.__append = append
        self.__time = time.time()
        self.__short_description = short_description
        self.__tag = tag
        self.__file_name = file_name
        self.__existing_ids = []
        self.__autotag_dict = autotag_dict

        self.__lower_autotag_dict()

        if file_name:
            if append and os.path.exists(file_name):
                self.__handler = codecs.open(file_name, 'a', u"utf-8")
                self.__compute_existing_id_list()
            else:
                self.__handler = codecs.open(file_name, 'w', u"utf-8")
                self.__write_header()
        else:
            self.__write_header()

    def get_test_result(self):
        return self.__test_data

    def write(self, output):
        """
        Write "<output>"
        """
        if self.__handler:
            self.__handler.write(unicode(output))
        else:
            if self.__test:
                self.__test_data += output
            else:
                # don't remove the comma(otherwise there will be a \n)
                print output,

    def writeln(self, output=""):
        """
        Write "<output>\n"
        """
        self.write(unicode(output) + u"\n")

    def __write_header(self):
        """
        Writes the header of the file

        __init__() does call this function
        """
        self.write_commentln(u"-*- coding: utf-8 mode: org -*-")
        self.write_commentln(
            u"this file is generated by " + sys.argv[0] + \
                ".Any modifications will be overwritten upon next invocation!")
        self.write_commentln(
            "To add this file to your org-agenda files open the stub file " + \
                " (file.org) not this file(file.org_archive) with emacs" + \
                "and do following: M-x org-agenda-file-to-front")
        self.write_org_item(
            self.__short_description + "          :Memacs:" + self.__tag + ":")

    def __write_footer(self):
        """
        Writes the footer of the file including calling python script and time

        Don't call this function - call instead function close(),
        close() does call this function
        """
        self.writeln(u"* successfully parsed by " + \
                     sys.argv[0] + u" at " + \
                     OrgFormat.inactive_datetime(time.localtime()) + \
                     u" in ~" + self.__time + u".")

    def write_comment(self, output):
        """
        Write output as comment: "## <output>"
        """
        self.write(u"## " + output)

    def write_commentln(self, output):
        """
        Write output line as comment: "## <output>\n"
        """
        self.write_comment(output + u"\n")

    def write_org_item(self, output):
        """
        Writes an org item line.

        i.e: * <output>\n
        """
        self.writeln("* " + output)

    def __write_org_subitem(self,
                            timestamp,
                            output,
                            note="",
                            properties=OrgProperties(),
                            tags=[]):
        """
        internally called by write_org_subitem and __append_org_subitem
        """
        output_tags = ""
        if tags != []:
            output_tags = u"\t:" + ":".join(map(str, tags)) + ":"

        output = output.lstrip()
        timestamp = timestamp.strip()

        self.writeln(u"** " + timestamp + u" " + output + output_tags)
        if note != "":
            for n in note.splitlines():
                self.writeln("   " + n)
        self.writeln(unicode(properties))

    def write_org_subitem(self,
                          timestamp,
                          output,
                          note="",
                          properties=OrgProperties(),
                          tags=None):
        """
        Writes an org item line.

        i.e:** <timestamp> <output> :<tags>:\n
               :PROPERTIES:
               <properties>
               :ID: -generated id-
               :END:

        if an argument -a or --append is given,
        then a desicion regarding the :ID: is made if the item has to be
        written to file

        @param timestamp: str/unicode
        @param output: st tar/unicode
        @param note: str/unicode
        @param tags: list of tags
        @param properties: OrgProperties object
        """
        assert (timestamp.__class__ == str or timestamp.__class__ == unicode)
        assert tags.__class__ == list or tags == None
        assert properties.__class__ == OrgProperties
        assert (output.__class__ == str or output.__class__ == unicode)
        assert (note.__class__ == str or note.__class__ == unicode)

        if tags == None:
            tags = []

        if self.__autotag_dict != {}:
            self.__get_autotags(tags, output)

        if self.__append:
            self.__append_org_subitem(timestamp,
                                      output,
                                      note,
                                      properties,
                                      tags)
        else:
            self.__write_org_subitem(timestamp,
                                     output,
                                     note,
                                     properties,
                                     tags)

    def __append_org_subitem(self,
                             timestamp,
                             output,
                             note="",
                             properties=OrgProperties(),
                             tags=[]):
        """
        Checks if subitem exists in orgfile (:ID: <id> is same),
        if not, it will be appended
        """
        identifier = properties.get_id()

        if id == None:
            raise Exception("id :ID: Property not set!")

        if self.__id_exists(identifier):
            # do nothing, id exists ...
            logging.debug("NOT appending")
        else:
            # id does not exist so we can append
            logging.debug("appending")
            self.__write_org_subitem(timestamp, output, note, properties, tags)

    def __compute_existing_id_list(self):
        """
        Reads the outputfile, looks for :ID: properties and stores them in
        self.__existing_ids
        """
        assert self.__existing_ids == []

        data = CommonReader.get_data_from_file(self.__file_name)

        for found_id in re.findall(":ID:(.*)\n.*:END:", data):
            found_id = found_id.strip()
            if found_id != "":
                self.__existing_ids.append(found_id)
                logging.debug("found id :ID: %s", found_id)
        logging.debug("there are already %d entries", len(self.__existing_ids))

    def __id_exists(self, searchid):
        """
        @return: if searchid already exists in output file
        """
        return unicode(searchid).strip() in self.__existing_ids

    def close(self):
        """
        Writes the footer and closes the file
        @param write_footer: write the foother with time ?
        """
        self.__time = "%1fs " % (time.time() - self.__time)
        if not self.__append:
            self.__write_footer()
        if self.__handler != None:
            self.__handler.close()

    def __lower_autotag_dict(self):
        """
        lowers all values of dict
        """
        for tag in self.__autotag_dict.iterkeys():
            values = []

            for value in self.__autotag_dict[tag]:
                values.append(value.lower())

            self.__autotag_dict[tag] = values

    def __get_autotags(self, tags, string):
        """
        Searches for tags in a given wordlist.
        Append them to tags

        @param tags: list to append the matched tags
        @param string: string to look for matching values
        """
        string = string.lower()

        for autotag_tag in self.__autotag_dict.iterkeys():
            for matching_word in self.__autotag_dict[autotag_tag]:
                if matching_word in string:
                    if autotag_tag not in tags:
                        tags.append(autotag_tag)
                    continue