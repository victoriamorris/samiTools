#!/usr/bin/env python
# -*- coding: utf8 -*-

# ====================
#       Set-up
# ====================

# Import required modules
from math import log10
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


def usage(extended=False):
    """Function to print information about the program"""
    print('Correct syntax is:')
    print('sami2marc_products -i <input_folder> -o <output_folder>')
    print('    -i    path to FOLDER containing Input files')
    print('    -o    path to FOLDER containing Output files')
    print('\nUse quotation marks (") around arguments which contain spaces')
    print('\nInput files should be SAMI files, in .xml, .prn or text format')
    print('\nOptions')
    print('    -x        Output files will be MARC XML rather than MARC 21 (.lex)')
    print('    --max_size <number|size>')
    print('              Split output')
    print('    --help    Display help message and exit')
    if extended:
        print('\n\nIf parameter --max_size is specified:\n'
              '\tmax_size is EITHER the maximum number of records in an output file \n'
              '\tOR the (approx.) maximum file size (in KB) \n'
              '\tif the number has the suffix \'K\'; \n\n'
              '\tOutput will be written to a sequence of files with the same name \n'
              '\tas the input file, but with a suffix indicating its order in the \n'
              '\tgenerated output sequence \n\n'
              '\tEXCEPT in the special case of --max_size 1 \n'
              '\t(the file is split into individual records) \n'
              '\tin which case the output files will be labelled \n'
              '\twith the record identifier.\n '
              '\tRecords with duplicate identifiers will be labelled \n'
              '\twith a _DUPLICATE suffix.'
              '\tRecords without identifiers will be labelled \n'
              '\twith _NO IDENTIFIER.')
    exit_prompt()


# ====================
#      Main code
# ====================


def main(argv=None):
    if argv is None: name = str(sys.argv[1])

    xml, split = False, False
    opts, args = None, None
    input_path, output_path = None, None
    limit = None
    max_size = 1024 * 1024 * 1024

    print('========================================')
    print('sami2marc_products')
    print('========================================')
    print('\nThis program converts SAMI files\n'
          'from text or .prn or XML format\n'
          'to MARC 21 Bibliographic files in MARC exchange (.lex) or MARC XML format\n')

    try:
        opts, args = getopt.getopt(argv, 'i:o:m:x', ['input_path=', 'output_path=', 'max_size=', 'help'])
    except getopt.GetoptError as err:
        exit_prompt('Error: {}'.format(err))
    if opts is None or not opts:
        usage()
    for opt, arg in opts:
        if opt == '--help':
            usage(extended=True)
        elif opt == '-x':
            xml = True
        elif opt in ['-i', '--input_path']:
            input_path = arg
        elif opt in ['-o', '--output_path']:
            output_path = arg
        elif opt in ['-m', '--max_size']:
            arg = arg.upper()
            limit = 'size' if 'K' in arg else 'number'
            try: max_size = int(re.sub(r'[^0-9]', '', arg))
            except: exit_prompt('Maximum file size could not be interpreted. \n'
                                'Please ensure that it is a positive integer, \n'
                                'optionally followed by the suffix K.')
            if not max_size >= 1: exit_prompt('Maximum file size could not be interpreted. \n'
                                              'Please ensure that it is a positive integer, \n'
                                              'optionally followed by the suffix K.')
            if limit == 'size': max_size *= 1024
        else:
            exit_prompt('Error: Option {} not recognised'.format(opt))

    if not input_path:
        exit_prompt('Error: No path to input files has been specified')
    if not os.path.isdir(input_path):
        exit_prompt('Error: Invalid path to input files')
    if not output_path:
        exit_prompt('Error: No path to output files has been specified')
    if not os.path.isdir(output_path):
        try: os.makedirs(output_path)
        except: exit_prompt('Error: Could not parse path to output files')

    # --------------------
    # Parameters seem OK => start program
    # --------------------

    # Display confirmation information about the transformation

    print('Input folder: {}'.format(input_path))
    print('Output folder: {}'.format(output_path))
    if limit:
        if max_size == 1:
            split = True
            print('Output file will be split into individual records')
        else: print('Maximum file size : {} {}'.format(str(max_size), 'bytes' if limit == 'size' else 'records'))

    # --------------------
    # Iterate through input files
    # --------------------

    for file in os.listdir(input_path):
        root, ext = os.path.splitext(file)
        if ext in ['.xml', '.prn'] or file.endswith(SAMI_SUFFICES):

            date_time('Processing file {} ...'.format(str(file)))

            # Open input file
            ifile = open(os.path.join(input_path, file), mode='r', encoding='utf-8', errors='replace')
            reader_type = 'prn' if ext == '.prn' else 'xml' if ext == '.xml' else 'txt'
            ext = '.xml' if xml else '.lex'
            reader = SAMIReader(ifile, reader_type=reader_type)

            # Special case if file is to be split into separate records
            if split:
                record_count = 0
                for record in reader:
                    record_count += 1
                    if record_count % 100 == 0:
                        print('{} records processed'.format(str(record_count)), end='\r')
                    filename = os.path.join(output_path, (record.identifier() or '_NO IDENTIFIER {}'.format(str(record_count))) + ext)
                    file_count = 0
                    while os.path.isfile(filename):
                        file_count += 1
                        filename = os.path.join(output_path, (record.identifier() or '_NO IDENTIFIER {}'.format(str(record_count))) + '_DUPLICATE {}'.format(str(file_count)) + ext)
                    if xml:
                        current_file = open(filename, 'w', encoding='utf-8', errors='replace')
                        current_file.write(XML_HEADER)
                        current_file.write(record.as_xml())
                        current_file.write('\n</marc:collection>')
                    else:
                        current_file = open(filename, mode='wb')
                        writer = MARCWriter(current_file)
                        writer.write(record)
                    current_file.close()
                ifile.close()
                print('{} records processed'.format(str(record_count)), end='\r')
                continue

            # All other cases
            FMT = None
            record_count, record_count_in_file = 0, 0
            current_idx, current_size = 0, 0

            if limit == 'size':
                FMT = ".%%0%dd" % (int(log10(os.path.getsize(os.path.join(input_path, file)) / max_size)) + 1)

            mid = FMT % current_idx if limit == 'size' else '.{}'.format(str(current_idx)) if limit == 'number' else ''
            filename = os.path.join(output_path, root + mid + ext)

            if xml:
                current_file = open(filename, 'w', encoding='utf-8', errors='replace')
                current_file.write(XML_HEADER)
            else:
                current_file = open(filename, mode='wb')
                writer = MARCWriter(current_file)

            for record in reader:
                record_count += 1
                record_count_in_file += 1
                if record_count % 100 == 0:
                    print('{} records processed'.format(str(record_count)), end='\r')

                # Check whether we need to start a new file
                current_size += len(record.as_xml()) if xml else len(record.as_marc())
                if ( limit == 'size' and current_size >= max_size ) \
                        or ( limit == 'number' and record_count_in_file > max_size ):
                    if xml: current_file.write('\n</marc:collection>')
                    current_file.close()
                    print('\nFile {} done'.format(str(current_idx)))
                    current_size = len(record.as_xml()) if xml else len(record.as_marc())
                    record_count_in_file = 0
                    current_idx += 1
                    mid = FMT % current_idx if limit == 'size' else '.{}'.format(str(current_idx)) if limit == 'number' else ''
                    filename = os.path.join(output_path, root + mid + ext)
                    if xml:
                        current_file = open(filename, 'w', encoding='utf-8', errors='replace')
                        current_file.write(XML_HEADER)
                    else:
                        current_file = open(filename, mode='wb')
                        writer = MARCWriter(current_file)

                if xml: current_file.write(record.as_xml())
                else: writer.write(record)

            if xml: current_file.write('\n</marc:collection>')
            print('{} records processed'.format(str(record_count)), end='\r')
            # Close files
            for f in [ifile, current_file]:
                f.close()

    date_time_exit()

if __name__ == '__main__':
    main(sys.argv[1:])
