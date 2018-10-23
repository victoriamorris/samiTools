#!/usr/bin/env python
# -*- coding: utf8 -*-

# ====================
#       Set-up
# ====================

# Import required modules
from samiTools.marc_data import *

# Set locale to assist with sorting
locale.setlocale(locale.LC_ALL, '')

# Set threshold for garbage collection (helps prevent the program run out of memory)
gc.set_threshold(400, 5, 5)

__author__ = 'Victoria Morris'
__license__ = 'MIT License'
__version__ = '1.0.0'
__status__ = '4 - Beta Development'


# ====================
#      Functions
# ====================


def usage():
    """Function to print information about the program"""
    print('Correct syntax is:')
    print('sami2marc_products -i <input_folder> -o <output_folder>')
    print('    -i    path to FOLDER containing Input files')
    print('    -o    path to FOLDER containing Output files')
    print('\nUse quotation marks (") around arguments which contain spaces')
    print('\nInput files should be SAMI files, in .xml, .prn or text format')
    print('\nOptions')
    print('    -x        Output files will be MARC XML rather than MARC 21 (.lex)')
    print('    --help    Display this message and exit')
    exit_prompt()


# ====================
#      Main code
# ====================


def main(argv=None):
    if argv is None: name = str(sys.argv[1])

    xml = False
    opts, args = None, None
    input_path, output_path = None, None

    print('========================================')
    print('sami2marc_products')
    print('========================================')
    print('\nThis program converts SAMI files\n'
          'from text or XML format\n'
          'to MARC 21 Bibliographic files in MARC exchange (.lex) or MARC XML format\n')

    try:
        opts, args = getopt.getopt(argv, 'i:o:', ['input_path=', 'output_path=', 'help'])
    except getopt.GetoptError as err:
        exit_prompt('Error: {}'.format(err))
    if opts is None or not opts:
        usage()
    for opt, arg in opts:
        if opt == '--help':
            usage()
        elif opt == '-x':
            xml = True
        elif opt in ['-i', '--input_path']:
            input_path = arg
        elif opt in ['-o', '--output_path']:
            output_path = arg
        else:
            exit_prompt('Error: Option {} not recognised'.format(opt))

    if not input_path:
        exit_prompt('Error: No path to input files has been specified')
    if not os.path.isdir(input_path):
        exit_prompt('Error: Invalid path to input files')
    if not output_path:
        exit_prompt('Error: No path to output files has been specified')
    if not os.path.isdir(output_path):
        exit_prompt('Error: Invalid path to output files')

    # --------------------
    # Parameters seem OK => start program
    # --------------------

    # Display confirmation information about the transformation

    print('Input folder: {}'.format(input_path))
    print('Output folder: {}'.format(output_path))

    # --------------------
    # Iterate through input files
    # --------------------

    for file in os.listdir(input_path):
        if file.endswith(('.xml', '.prn')) or file.endswith(SAMI_SUFFICES):

            date_time('Processing file {} ...'.format(str(file)))

            # Open input and output files
            ifile = open(os.path.join(input_path, file), mode='r', encoding='utf-8', errors='replace')
            reader_type = 'prn' if file.endswith('.prn') else 'xml' if file.endswith('.xml') else 'txt'
            reader = SAMIReader(ifile, reader_type=reader_type)
            tfile = open(os.path.join(output_path, file + '.txt'), mode='w', encoding='utf-8', errors='replace')
            if xml:
                ofile = open(os.path.join(output_path, file + '.xml'), mode='w', encoding='utf-8', errors='replace')
                ofile.write('<?xml version="1.0" encoding="UTF-8" ?>'
                            '\n<marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                            'xsi:schemaLocation="http://www.loc.gov/MARC21/slim http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd">')
            else:
                ofile = open(os.path.join(output_path, file + '.lex'), mode='wb')
                writer = MARCWriter(ofile)
            i = 0

            for record in reader:
                i += 1
                print('{} records processed'.format(str(i)), end='\r')
                if xml:
                    ofile.write(record.as_xml())
                else:
                    writer.write(record)
                tfile.write(str(record) + '\n')

            if xml: ofile.write('\n</marc:collection>')
            # Close files
            for f in (ifile, ofile, tfile):
                f.close()

    date_time_exit()


if __name__ == '__main__':
    main(sys.argv[1:])
