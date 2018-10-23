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
#   Global variables
# ====================


files = {
    'input':      None,
    'output':     None,
    }

roles = {
    '-i':           'input',
    '--ifile':      'input',
    '-o':           'output',
    '--ofile':      'output',
    }

# ====================
#      Functions
# ====================


def usage():
    """Function to print information about the program"""
    print('Correct syntax is:')
    print('sami2marc_authorities -i <ifile> -o <ofile>')
    print('    -i    path to Input file')
    print('    -o    path to Output file')
    print('\nUse quotation marks (") around arguments which contain spaces')
    print('\nInput file should be SAMI Authorities file (.txt)')
    print('\nOutput file should be either MARC exchange (.lex) or MARC XML (.xml)')
    print('\nOptions')
    print('    --help    Display this message and exit')
    exit_prompt()


# ====================
#      Main code
# ====================


def main(argv=None):
    if argv is None: name = str(sys.argv[1])

    xml = False
    opts, args = None, None

    print('========================================')
    print('sami2marc_authorities')
    print('========================================')
    print('\nThis program converts SAMI AUTHORITY files\n'
          'from text format\n'
          'to MARC 21 Authority files in MARC exchange (.lex) or MARC XML format\n')

    try: opts, args = getopt.getopt(argv, 'i:o:', ['ifile=', 'ofile=', 'help'])
    except getopt.GetoptError as err:
        exit_prompt('Error: {}'.format(err))
    if opts is None or not opts:
        usage()
    for opt, arg in opts:
        if opt == '--help':
            usage()
        elif opt in roles:
            files[roles[opt]] = FilePath(arg, roles[opt])
        else:
            exit_prompt('Error: Option {} not recognised'.format(opt))

    for f in files:
        if not files[f]:
            exit_prompt('Error: No path to {} file has been specified'.format(f))
    if files['output'].ext == '.xml': xml = True

    print('\n\nStarting conversion ...')
    print('----------------------------------------')
    print(str(datetime.datetime.now()))

    ifile = open(files['input'].path, mode='r', encoding='utf-8', errors='replace')
    if xml:
        ofile = open(files['output'].path, mode='w', encoding='utf-8', errors='replace')
        ofile.write('<?xml version="1.0" encoding="UTF-8" ?>'
                    '\n<marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                    'xsi:schemaLocation="http://www.loc.gov/MARC21/slim http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd">')
    else:
        ofile = open(files['output'].path, mode='wb')
        writer = MARCWriter(ofile)

    record_count = 0
    in_record, in_field = False, False
    field_content = ''
    for filelineno, line in enumerate(ifile):
        line = line.strip('\n')
        if line.startswith('XX'):
            record_count += 1
            print('\r{0} SAMI records processed'.format(str(record_count)), end='\r')
            if in_record:
                if in_field:
                    record.add_ordered_field(line_to_field(field_content))
                if xml:
                    ofile.write(record.as_xml())
                else:
                    writer.write(record)

            record = MARCRecord()
            in_record, in_field = True, False
            field_content = ''
            sid, fmt, level, created, created_by, modified, modified_by, cataloged, source = line.rstrip('\t').split(
                '\t\t')
            record.add_field(Field(tag='901', indicators=[' ', ' '], subfields=['a', 'id: ' + sid]))
            record.add_field(Field(tag='902', indicators=[' ', ' '], subfields=['a', 'fmt: ' + fmt]))
            record.add_field(Field(tag='903', indicators=[' ', ' '], subfields=['a', 'level: ' + level]))
            record.add_field(Field(tag='904', indicators=[' ', ' '], subfields=['a', 'created: ' + created]))
            record.add_field(Field(tag='905', indicators=[' ', ' '], subfields=['a', 'created_by: ' + created_by]))
            record.add_field(Field(tag='906', indicators=[' ', ' '], subfields=['a', 'modified: ' + modified]))
            record.add_field(Field(tag='907', indicators=[' ', ' '], subfields=['a', 'modified_by: ' + modified_by]))
            record.add_field(Field(tag='908', indicators=[' ', ' '], subfields=['a', 'cataloged: ' + cataloged]))
            record.add_field(Field(tag='909', indicators=[' ', ' '], subfields=['a', 'source: ' + source]))


        elif in_record:
            line = line.strip()
            if re.search(r'^[0-9]{3}:', line):
                if in_field:
                    record.add_ordered_field(line_to_field(field_content))
                in_field = True
                field_content = line

            else:
                field_content += line

    if in_record:
        if in_field:
            record.add_ordered_field(line_to_field(field_content))
        if xml:
            ofile.write(record.as_xml())
        else:
            writer.write(record)

    if xml: ofile.write('\n</marc:collection>')
    # Close files
    for f in (ifile, ofile):
        f.close()

    date_time_exit()


if __name__ == '__main__':
    main(sys.argv[1:])
