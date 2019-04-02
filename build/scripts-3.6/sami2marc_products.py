#!C:\Program Files (x86)\Microsoft Visual Studio\Shared\Python36_64\python.exe
# -*- coding: utf8 -*-

# ====================
#       Set-up
# ====================

# Import required modules
from __future__ import print_function
from math import log10
from samiTools.marc_data import *
import profile

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


ARGUMENTS = OrderedDict([
    ('-i', 'path to FOLDER containing Input files'),
    ('-o', 'path to FOLDER containing Output files'),
])

OPTIONS = OrderedDict([
    ('--max_size', 'Split output by size or number of records'),
])

FLAGS = OrderedDict([
    ('-x', 'Output files will be MARC XML rather than MARC 21 (.lex)'),
    ('--header', 'Include MetAg headers in MARC XML records'),
    ('--help', 'Display help message and exit'),
])


# ====================
#      Functions
# ====================


def usage(extended=False):
    """Function to print information about the program"""
    print('\nCorrect syntax is:\n')
    print('sami2marc_authorities -i <ifile> -o <ofile>'
          '\n\t\t\t[--max_size <number|size>]'
          '\n\t\t\t[-x] [--header]')
    print('\nArguments:')
    for o in ARGUMENTS:
        print_opt(o, ARGUMENTS[o])
    print("""\

Use quotation marks (") around arguments which contain spaces
Input files should be SAMI Products files, in .xml, .prn or text format
Output file should be either MARC exchange (.lex) or MARC XML (.xml).\

""")
    print('Options:')
    for o in OPTIONS:
        print_opt(o, OPTIONS[o])
    print('\nFlags:')
    for o in FLAGS:
        print_opt(o, FLAGS[o])
    if extended:
        print("""\
            
If parameter --max_size is specified:
    max_size is EITHER the maximum number of records in an output file 
    OR the (approx) maximum file size (in KB) if the number has the suffix 'K';
    Output will be written to a sequence of files with the same name as the 
    input file, but with a suffix indicating its order in the generated 
    output sequence
    EXCEPT in the special case of --max_size 1 (the file is split into 
    individual records) in which case the output files will be labelled with 
    the record identifier;
    Records with duplicate identifiers will be labelled with _DUPLICATE;
    Records without identifiers will be labelled with _NO IDENTIFIER.

If parameter --header is specified:
    MARC XML records will be given a <header> to make them suitable for the 
    Metadata Aggregator;
    The <header> will include the record identifier;
    NOTE: --header can only be used with -x.\
    """)
    exit_prompt()


# ====================
#      Main code
# ====================


def main(argv=None):
    if argv is None: name = str(sys.argv[1])
    if argv is None: name = str(sys.argv[1])

    xml, split, header, deleted = False, False, False, False
    opts, args = None, None
    input_path, output_path = None, None
    limit = None
    max_size = 1024 * 1024 * 1024

    print('========================================')
    print('sami2marc_products')
    print('========================================')
    print("""\
This program converts SAMI files from text, .prn, or XML format
to MARC 21 Bibliographic files in MARC exchange (.lex) or MARC XML format\
""")

    try:
        opts, args = getopt.getopt(argv, 'hi:o:m:x', ['input_path=', 'output_path=', 'max_size=', 'header', 'help'])
    except getopt.GetoptError as err:
        exit_prompt('Error: {}'.format(err))
    if opts is None or not opts:
        usage()
    for opt, arg in opts:
        if opt == '--help':
            usage(extended=True)
        elif opt == '-x':
            xml = True
        elif opt in ['-h', '--header']:
            header = True
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

    if header and not xml:
        exit_prompt('Error: Option --header cannot be used without -x')

    # --------------------
    # Parameters seem OK => start program
    # --------------------

    # Display confirmation information about the transformation

    print('Input folder: {}'.format(input_path))
    print('Output folder: {}'.format(output_path))
    print('Output format: {}'.format('MARC XML (.xml)' if xml else 'MARC (.lex)'))
    if limit:
        if max_size == 1:
            split = True
            print('Output file will be split into individual records')
        else: print('Maximum file size : {} {}'.format(str(max_size), 'bytes' if limit == 'size' else 'records'))
    if header:
        print('MetAg headers will be used')

    # --------------------
    # Iterate through input files
    # --------------------

    for file in os.listdir(input_path):
        root, ext = os.path.splitext(file)
        deleted = False
        if ext in ['.xml', '.prn'] or file.endswith(SAMI_SUFFICES) or any(f in root for f in PRIMO_FLAGS):
            if any(f in root for f in PRIMO_FLAGS):
                root = root + ext
                ext = '.xml'

            date_time('Processing file {} ...'.format(str(file)))
            if '_dels' in root:
                deleted = True
                print('File contains deleted records')

            # Open input file
            ifile = open(os.path.join(input_path, file), mode='r', encoding='utf-8', errors='replace')
            reader_type = 'prn' if ext == '.prn' else 'xml' if ext == '.xml' else 'txt'
            ext = '.xml' if xml else '.lex'
            reader = sami_factory(reader_type=reader_type, target=ifile)

            OPEN = OAI_HEADER if header else XML_HEADER
            CLOSE = '\n</ListRecords>\n</OAI-PMH>' if header else '\n</marc:collection>'

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
                        if header:
                            current_file.write(METAG_HEADER + record.header(deleted=deleted))
                            if not (deleted or record.deleted):
                                current_file.write('<metadata>{}\n</metadata>\n'.format(record.as_xml(namespace=True)))
                            current_file.write('</record>')
                        else:
                            current_file.write('{}{}\n</marc:collection>'.format(XML_HEADER, record.as_xml()))
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
                current_file.write(OPEN)
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
                if (limit == 'size' and current_size >= max_size) \
                        or (limit == 'number' and record_count_in_file > max_size):
                    if xml: current_file.write(CLOSE)
                    current_file.close()
                    print('{} records processed'.format(str(record_count)), end='\r')
                    print('\nFile {} done'.format(str(current_idx)))
                    current_size = len(record.as_xml()) if xml else len(record.as_marc())
                    record_count_in_file = 0
                    current_idx += 1
                    mid = FMT % current_idx if limit == 'size' else '.{}'.format(str(current_idx)) if limit == 'number' else ''
                    filename = os.path.join(output_path, root + mid + ext)
                    if xml:
                        current_file = open(filename, 'w', encoding='utf-8', errors='replace')
                        current_file.write(OPEN)
                    else:
                        current_file = open(filename, mode='wb')
                        writer = MARCWriter(current_file)

                record_to_write = '{}{}{}</record>'.format(OAI_RECORD, record.header(deleted=deleted),
                                                           '<metadata>{}\n</metadata>\n'.format(record.as_xml(namespace=True)) if not (deleted or record.deleted) else '') if header \
                    else record.as_xml()

                if xml: current_file.write(record_to_write)
                else: writer.write(record)

            if xml: current_file.write(CLOSE)
            print('{} records processed'.format(str(record_count)), end='\r')
            # Close files
            for f in [ifile, current_file]:
                f.close()

    date_time_exit()

if __name__ == '__main__':
    main(sys.argv[1:])

