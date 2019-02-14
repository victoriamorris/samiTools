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
    'pre':        None,
    'post':       None,
    'errors':     None,
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


def usage(extended=False):
    """Function to print information about the program"""
    print('Correct syntax is:')
    print('sami2marc_authorities -i <ifile> -o <ofile>')
    print('    -i    path to Input file')
    print('    -o    path to Output file')
    print('\nUse quotation marks (") around arguments which contain spaces')
    print('\nInput file should be SAMI Authorities file (.txt or .prn)')
    print('\nOutput file should be either MARC exchange (.lex) or MARC XML (.xml)')
    print('Records with errors will be written to <ofile>_errors.')
    print('\nOptions')
    print('    --date <yyyymmdd>')
    print('              split output into two files by specfied date')
    print('    --tidy    tidy authority files to facilitate load to MetAg')
    print('    --help    Display help message and exit')
    if extended:
        print('\n\nIf parameter --date is specified:\n'
              '\tRecords with a created or amended date ealier than \n'
              '\tthe value specified will be written to <ofile>_pre_<date>; \n'
              '\tRecords with a created or amended date equal to or later than \n'
              '\tthe value specified will be written to <ofile>_post_<date>. \n')
        print('\nIf parameter --tidy is specified:\n'
              '\tIf no 001 is present, one will be created from the first instance of 901 $a; \n'
              '\t904 $a and 905 $a will be combined into a single 904 field ($a and $b); \n'
              '\t906 $a and 907 $a will be combined into a single 906 field ($a and $b); \n'
              '\tCreated and Amended date will be converted from dd/mm/yy to yyyymmdd format. \n')
    exit_prompt()


# ====================
#      Main code
# ====================


def main(argv=None):
    if argv is None: name = str(sys.argv[1])

    xml, tidy = False, False
    opts, args, date = None, None, None

    print('========================================')
    print('sami2marc_authorities')
    print('========================================')
    print('\nThis program converts SAMI AUTHORITY files\n'
          'from text or .prn format\n'
          'to MARC 21 Authority files in MARC exchange (.lex) or MARC XML format\n')

    try: opts, args = getopt.getopt(argv, 'i:o:d:', ['ifile=', 'ofile=', 'date=', 'tidy', 'help'])
    except getopt.GetoptError as err:
        exit_prompt('Error: {}'.format(err))
    if opts is None or not opts:
        usage()
    for opt, arg in opts:
        if opt == '--help':
            usage(extended=True)
        elif opt == '--tidy':
            tidy = True
        elif opt in ['-d', '--date']:
            date = arg
        elif opt in roles:
            files[roles[opt]] = FilePath(arg, roles[opt])
        else:
            exit_prompt('Error: Option {} not recognised'.format(opt))

    for f in ['input', 'output']:
        if not files[f]:
            exit_prompt('Error: No path to {} file has been specified'.format(f))
    if files['output'].ext == '.xml': xml = True

    # Create extra files for MetAg output
    if date:
        if len(re.sub(r'[^0-9]]', '', date)) != 8: exit_prompt('The date parameter must be in the format yyyymmdd')
        try: date = datetime.datetime.strptime(date, '%Y%m%d')
        except: exit_prompt('The date parameter must be in the format yyyymmdd')
        files['pre'] = FilePath((files['output'].path).replace(files['output'].ext,
                                                               '_pre_{}{}'.format(date.strftime('%Y%m%d'), files['output'].ext)),
                                                               'output pre date')
        files['post'] = FilePath((files['output'].path).replace(files['output'].ext,
                                                                '_post_{}{}'.format(date.strftime('%Y%m%d'), files['output'].ext)),
                                                                'output post date')

    files['errors'] = FilePath((files['output']).path.replace(files['output'].ext, '_errors{}'.format(files['output'].ext)), 'error output')

    print('\n\nStarting conversion ...')
    print('----------------------------------------')
    print(str(datetime.datetime.now()))
    if date:
        print('\nDate for splitting output: {}'.format(date.strftime('%Y%m%d')))
    if date or tidy: print('Output will be tidied for MetAg use.\n')

    ifile = open(files['input'].path, mode='r', encoding='utf-8', errors='replace')
    for f in files:
        if f != 'input' and files[f]:
            if xml:
                files[f].file_object = open(files[f].path, mode='w', encoding='utf-8', errors='replace')
                files[f].file_object.write(XML_HEADER)
            else:
                files[f].file_object = open(files[f].path, mode='wb')
                files[f].file_writer = MARCWriter(files[f].file_object)

    record_count = 0
    in_record, in_field, error = False, False, False
    field_content = ''
    sid, fmt, level, created, created_by, modified, modified_by, cataloged, source = None, None, None, None, None, None, None, None, None
    for filelineno, line in enumerate(ifile):
        line = line.strip('\n')
        if line.startswith('XX'):
            record_count += 1
            if record_count % 100 == 0:
                print('\r{0} SAMI records processed'.format(str(record_count)), end='\r')

            # Write current record
            if in_record:
                if in_field:
                    record.add_ordered_field(line_to_field(field_content))
                if tidy:
                    if '001' not in record:
                        if sid != '':
                            record.add_ordered_field(Field(tag='001', data=sid))
                        else:
                            print('Failed to add 001')
                            error = True

                if error:
                    if xml: files['errors'].file_object.write(record.as_xml())
                    else: files['errors'].file_writer.write(record)
                else:
                    if xml: files['output'].file_object.write(record.as_xml())
                    else: files['output'].file_writer.write(record)
                    if date:
                        fmt = '%Y%m%d' if tidy else '%d/%m/%Y'
                        try:
                            f = 'post' if (created != 'NEVER' and datetime.datetime.strptime(created, fmt) >= date) \
                                          or (modified != 'NEVER' and datetime.datetime.strptime(modified, fmt) >= date) else 'pre'
                        except:
                            print('\nError parsing date')
                        else:
                            if xml: files[f].file_object.write(record.as_xml())
                            else: files[f].file_writer.write(record)

            # Start new record
            record = MARCRecord()
            in_record, in_field, error = True, False, False
            field_content = ''
            sid, fmt, level, created, created_by, modified, modified_by, cataloged, source = line.rstrip('\t').split('\t\t')
            if tidy:
                if created != 'NEVER':
                    try: created = datetime.datetime.strftime(datetime.datetime.strptime(created, '%d/%m/%Y'), '%Y%m%d')
                    except:
                        print('Error parsing created date')
                        error = True
                if modified != 'NEVER':
                    try: modified = datetime.datetime.strftime(datetime.datetime.strptime(modified, '%d/%m/%Y'), '%Y%m%d')
                    except:
                        print('Error parsing modified date')
                        error = True
            record.add_field(Field(tag='901', indicators=[' ', ' '], subfields=['a', 'id: ' + sid]))
            record.add_field(Field(tag='902', indicators=[' ', ' '], subfields=['a', 'fmt: ' + fmt]))
            record.add_field(Field(tag='903', indicators=[' ', ' '], subfields=['a', 'level: ' + level]))
            if tidy:
                record.add_field(Field(tag='904', indicators=[' ', ' '], subfields=['a', 'created: ' + created, 'b', 'created_by: ' + created_by]))
                record.add_field(Field(tag='906', indicators=[' ', ' '], subfields=['a', 'modified: ' + modified, 'b', 'modified_by: ' + modified_by]))
            else:
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

    # Write final record
    if in_record:
        if in_field:
            record.add_ordered_field(line_to_field(field_content))
        if '001' not in record:
            if sid != '':
                record.add_ordered_field(Field(tag='001', data=sid))
            else: error = True
        if error:
            if xml: files['errors'].file_object.write(record.as_xml())
            else: files['errors'].file_writer.write(record)
        else:
            if xml: files['output'].file_object.write(record.as_xml())
            else: files['output'].file_writer.write(record)
            if date:
                try:
                    fmt = '%Y%m%d' if tidy else '%d/%m/%Y'
                    f = 'post' if (created != 'NEVER' and datetime.datetime.strptime(created, fmt) >= date) \
                                  or (modified != 'NEVER' and datetime.datetime.strptime(modified, fmt) >= date) else 'pre'
                except Exception as e:
                    print('\nError parsing date')
                    print(str(e))
                    print(created)
                    print(modified)
                else:
                    if xml: files[f].file_object.write(record.as_xml())
                    else: files[f].file_writer.write(record)

    # Close XML record
    if xml:
        for f in files:
            if f != 'input' and files[f]:
                files[f].file_object.write('\n</marc:collection>')

    # Close files
    for f in files:
        try: files[f].file_object.close()
        except: pass

    date_time_exit()


if __name__ == '__main__':
    main(sys.argv[1:])
