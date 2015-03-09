#!/usr/bin/python

import sys
import string
import re
import xlsxwriter
from optparse import OptionParser

class LmddProcessor(object):
    def __init__(self, process_perf, func_finsh =None):
        """
        """
        self.process_perf = process_perf
        self._func_finish = func_finsh

        self.isread = 0
        self.size = 0

        self.count = 0
        self.totoltime = 0
        self.totolperf = 0

        self.col = 0
        self.avgindex = 0

    def reset_count(self):
        self.count = 0
        self.totoltime = 0
        self.totolperf = 0

    def check_isread(self, line):
        isread = re.search(r'\slmdd read\s', line)
        if isread:
            #print line
            self.isread = 1
            self.col = 0
            self.avgindex = 0

    def check_ishead(self, line):
        issize = re.search(r'\s=== ', line)
        if issize:
            #print line
            dosize = re.findall(r'[\d|.]+',line)
            self.size = dosize[0]
            self.reset_count()
            self.avgindex += 1

    def split(self, line):
            """
            """

            self.check_isread(line)
            self.check_ishead(line)

            isperf = re.search(r'\sMB/sec\s', line)

            if isperf:
                #print line
                data = re.findall(r'[\d|.]+',line)
                self.count += 1
                self.col += 1
                self.totoltime += string.atof(data[1])
                self.totolperf += string.atof(data[2])


                return {
                    'isread':self.isread,
                    'col':  self.col,
                    'size': self.size,
                    'index': self.count,
                    'time': data[1],
                    'perf': data[2],
                    'timeavg': self.totoltime/self.count,
                    'perfavg': self.totolperf/self.count,
                    'avgindex':self.avgindex,
                }

    def parse(self, handle):
            """
            Parses the log file.
            Returns a dictionary composed of log entry values
            for easy data summation
            """
            for line in handle:
                fields = self.split(line)
                "Reserve one line for head"
                if fields:
                    self.process_perf(fields)

            self._func_finish()

class LmddPerfHandle(object):
    """
    find out read/write performance data,
    and write to excel table.
    """
    def __init__(self, name):
        workbook = xlsxwriter.Workbook(name)
        worksheet = workbook.add_worksheet()
        self.workbook = workbook
        self.worksheet = worksheet

        bold = workbook.add_format({'bold': True})
        headings = ['Size', 'Times','Write/time', 'Wrtie/perf', 'Read/time', 'Read/perf']
        worksheet.write_row('A1', headings, bold)
        avgheadings = ['Size', 'Times','Write/time', 'Wrtie/perf', 'Read/time', 'Read/perf']
        worksheet.write_row('A10', avgheadings, bold)

    def process(self,fields):
        """
        Write out to excel table.
        """
        row = long(fields['col'])

        if(fields['isread']):
            self.worksheet.write(row, 4, float(fields['time']))
            self.worksheet.write(row, 5, float(fields['perf']))
            if(fields['index'] == 20 ):
                avgrow = fields['avgindex']
                self.worksheet.write(avgrow, 14, float(fields['timeavg']))
                self.worksheet.write(avgrow, 15, float(fields['perfavg']))
        else:
            self.worksheet.write(row, 0, fields['size']+'k')
            self.worksheet.write(row, 1, float(fields['index']))
            self.worksheet.write(row, 2, float(fields['time']))
            self.worksheet.write(row, 3, float(fields['perf']))

            if(fields['index'] == 20 ):
                avgrow = fields['avgindex']
                self.worksheet.write(avgrow, 10, fields['size']+'k')
                self.worksheet.write(avgrow, 11, 'AVG')
                self.worksheet.write(avgrow, 12, float(fields['timeavg']))
                self.worksheet.write(avgrow, 13, float(fields['perfavg']))

    def finish(self):
        self.workbook.close()


if __name__ == '__main__':

    lmdd_perf_handle = LmddPerfHandle('lmddout.xlsx')

    processor = LmddProcessor(lmdd_perf_handle.process, lmdd_perf_handle.finish)

    input_file = open('lmdd_perf.log')
    lines = input_file.readlines()
    processor.parse(lines)