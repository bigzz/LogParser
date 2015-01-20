#!/usr/bin/python

import sys
import re
import xlsxwriter
from optparse import OptionParser

class LogProcessor(object):
    '''
    Process a combined log format.

    This processor handles log files in a combined format,
    objects that act on the results are passed in to
    the init method as a series of methods.
    '''
    def __init__(self, process_chain=None,func_finsh =None):
        """
        Setup parser
        Save the call chain. Each time we process a log ,
        we'll run the list of callbacks with the processed
        log results.
        """
        if process_chain is None:
            process_chain = []
        self._process_chain = process_chain
        self._func_finish = func_finsh

    def split(self, line):
            """
            Split a log file.
            Initially,we just want size and requested file name . so
            we'll split on spaces and pull the data out.
            """
            data = re.findall(r'[\d|.]+',line)

            return {
                'ktime': data[1],
                'perf': data[6],
                'size': data[7],
                'times': data[8],
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
                column = handle.index(line) + 1
                for func in self._process_chain:
                   func(fields, column)

            self._func_finish()

class MMCPerfHandler(object):
    """
    find out the eMMC performance data form Kernel Log.
    and output to EXCEL display.
    """
    def __init__(self, name):
        workbook = xlsxwriter.Workbook(name)
        worksheet = workbook.add_worksheet()
        self.workbook = workbook
        self.worksheet = worksheet

        bold = workbook.add_format({'bold': True})
        headings = ['ktime', 'size', 'times', 'perf']
        worksheet.write_row('A1', headings, bold)

    def process(self,fields,row):
        """
        Write out to excel table.
        """
        self.worksheet.write(row, 0, float(fields['ktime']))
        self.worksheet.write(row, 1, long(fields['size']))
        self.worksheet.write(row, 2, long(fields['times']))
        self.worksheet.write(row, 3, float(fields['perf']))

    def finish(self):
        self.workbook.close()

if __name__ == '__main__':
    '''
    parser = OptionParser()
    parser.add_option('-s', '--size', dest = "size",
                      help = "Maximum File Size Allowed",
                      default = 0, type = "int")
    opts,args = parser.parse_args()
    '''

    call_chain = []

    mmc_perf_handle = MMCPerfHandler('perf.xlsx')
    call_chain.append(mmc_perf_handle.process)
    processor = LogProcessor(call_chain, mmc_perf_handle.finish)

    input_file = open('perf.txt')
    lines = input_file.readlines()
    processor.parse(lines)