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


ARGUMENTS = OrderedDict([
    ('-i', 'path to Input file'),
    ('-o', 'path to Output file'),
])

OPTIONS = OrderedDict([
    ('--date', 'Split output into two files by specified date'),
    ('--max_size', 'Split output by size or number of records'),
])

FLAGS = OrderedDict([
    ('--tidy', 'Tidy authority files to facilitate load to MetAg'),
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
          '\n\t\t\t[--date <yyyymmdd>|--max_size <number|size>]'
          '\n\t\t\t[--tidy] [--header]')
    print('\nArguments:')
    for o in ARGUMENTS:
        print_opt(o, ARGUMENTS[o])
    print("""\
    
Use quotation marks (") around arguments which contain spaces
Input file should be SAMI Authorities files in .xml, .prn or text format
Output file should be either MARC exchange (.lex) or MARC XML (.xml)
Records with errors will be written to <ofile>_errors.\

""")
    print('Options:')
    for o in OPTIONS:
        print_opt(o, OPTIONS[o])
    print('--date and --max_size cannot be used at the same time.')
    print('\nFlags:')
    for o in FLAGS:
        print_opt(o, FLAGS[o])
    if extended:
        print("""\

If parameter --date is specified:
    Records with a created or amended date ealier than the value specified 
    will be written to <ofile>_pre_<date>;
    Records with a created or amended date equal to or later than the value 
    specified will be written to <ofile>_post_<date>.
    
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
    
If parameter --tidy is specified:
    If no 001 is present, one will be created from the first 901 $a;
    904 $a and 905 $a will be combined into a single 904 field ($a and $b);
    906 $a and 907 $a will be combined into a single 906 field ($a and $b);
    Created and Amended date will be converted from dd/mm/yy to yyyymmdd format.
    
If parameter --header is specified:
    MARC XML records will be given a <header> to make them suitable for the 
    Metadata Aggregator;
    The <header> will include the record identifier;
    NOTE: --header can only be used if the output is MARC XML.\
    """)
    exit_prompt()


# ====================
#      Main code
# ====================


def main(argv=None):
    if argv is None: name = str(sys.argv[1])

    xml, tidy, split, header = False, False, False, False
    opts, args, date, limit = None, None, None, None
    max_size = 1024 * 1024 * 1024

    print('========================================')
    print('sami2marc_authorities')
    print('========================================\n')
    print("""\
This program converts SAMI AUTHORITY files from text, .prn, or XML format
to MARC 21 Authority files in MARC exchange (.lex) or MARC XML format\
""")

    try: opts, args = getopt.getopt(argv, 'hi:o:m:d:t', ['ifile=', 'ofile=', 'max_size=', 'header', 'date=', 'tidy', 'help'])
    except getopt.GetoptError as err:
        exit_prompt('Error: {}'.format(err))
    if opts is None or not opts:
        usage()
    for opt, arg in opts:
        if opt == '--help':
            usage(extended=True)
        elif opt in ['-h', '--header']:
            header = True
        elif opt in ['-t', '--tidy']:
            tidy = True
        elif opt in ['-d', '--date']:
            date = arg
        elif opt in roles:
            files[roles[opt]] = FilePath(arg, roles[opt])
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

    if date and limit: exit_prompt('Error: Options --date and --max_size cannot be used at the same time')

    for f in ['input', 'output']:
        if not files[f]:
            exit_prompt('Error: No path to {} file has been specified'.format(f))
    if files['output'].ext == '.xml': xml = True

    # Check date format and create extra files for MetAg output

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

    # --------------------
    # Parameters seem OK => start program
    # --------------------

    # Display confirmation information about the transformation

    print('Input file: {}'.format(files['input'].path))
    print('Output file: {}'.format(files['output'].path))
    print('Output format: {}'.format('MARC XML (.xml)' if xml else 'MARC (.lex)'))
    if limit:
        if max_size == 1:
            split = True
            print('Output file will be split into individual records')
        else: print('Maximum file size : {} {}'.format(str(max_size), 'bytes' if limit == 'size' else 'records'))
    if date:
        print('\nDate for splitting output: {}'.format(date.strftime('%Y%m%d')))
    if tidy: print('Output will be tidied for MetAg use.\n')
    if header: print('MetAg headers will be used')

    # --------------------
    # Iterate through input files
    # --------------------

    print('\n\nStarting conversion ...')
    print('----------------------------------------')
    print(str(datetime.datetime.now()))

    ifile = open(files['input'].path, mode='r', encoding='utf-8', errors='replace')
    reader = sami_factory(reader_type='xml' if files['input'].ext == '.xml' else 'authorities', target=ifile, tidy=tidy)
    output_path, root = os.path.split(files['output'].path)
    if not os.path.isdir(output_path):
        try: os.makedirs(output_path)
        except: exit_prompt('Error: Could not parse path to output file')
    root, ext = os.path.splitext(root)

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
                    current_file.write('{}{}<metadata>{}\n</metadata>\n</record>'.format(METAG_HEADER, record.header(), record.as_xml(namespace=True)))
                else:
                    current_file.write('{}{}\n</marc:collection>'.format(XML_HEADER, record.as_xml()))
            else:
                current_file = open(filename, mode='wb')
                writer = MARCWriter(current_file)
                writer.write(record)

    # All other cases
    else:
        FMT = None
        record_count, record_count_in_file = 0, 0
        current_idx, current_size = 0, 0

        if limit == 'size':
            FMT = ".%%0%dd" % (int(log10(os.path.getsize(files['input'].path) / max_size)) + 1)

        mid = FMT % current_idx if limit == 'size' else '.{}'.format(str(current_idx)) if limit == 'number' else ''
        filename = os.path.join(output_path, root + mid + ext)

        for f in files:
            if f not in ('input', 'output') and files[f]:
                if xml:
                    files[f].file_object = open(files[f].path, mode='w', encoding='utf-8', errors='replace')
                    files[f].file_object.write(OPEN)
                else:
                    files[f].file_object = open(files[f].path, mode='wb')
                    files[f].file_writer = MARCWriter(files[f].file_object)

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
                mid = FMT % current_idx if limit == 'size' else '.{}'.format(
                    str(current_idx)) if limit == 'number' else ''
                filename = os.path.join(output_path, root + mid + ext)
                if xml:
                    current_file = open(filename, 'w', encoding='utf-8', errors='replace')
                    current_file.write(OPEN)
                else:
                    current_file = open(filename, mode='wb')
                    writer = MARCWriter(current_file)

            record_to_write = '{}{}<metadata>{}\n</metadata>\n</record>'.format(OAI_RECORD, record.header(), record.as_xml(namespace=True)) if header \
                else record.as_xml()

            if record.is_bad():
                if xml:
                    files['errors'].file_object.write(record_to_write)
                else: files['errors'].file_writer.write(record)
            else:
                # Write record to main output file
                if xml: current_file.write(record_to_write)
                else: writer.write(record)
                # If splitting by date, write record to appropriate output file
                if date:
                    fmt = '%Y%m%d' if tidy else '%d/%m/%Y'
                    try:
                        f = 'post' if (record.created != 'NEVER' and datetime.datetime.strptime(record.created, fmt) >= date) \
                                      or (record.modified != 'NEVER' and datetime.datetime.strptime(record.modified,  fmt) >= date) else 'pre'
                    except: print('\nError parsing date')
                    else:
                        if xml: files[f].file_object.write(record_to_write)
                        else: files[f].file_writer.write(record)

    # Write closing elements in files
    if xml:
        current_file.write(CLOSE)
        for f in files:
            if f != 'input' and files[f] and files[f].file_object:
                files[f].file_object.write(CLOSE)

    print('{} records processed'.format(str(record_count)), end='\r')

    # Close files
    for f in [ifile, current_file]:
        f.close()
    for f in files:
        try: files[f].file_object.close()
        except: pass

    date_time_exit()


if __name__ == '__main__':
    main(sys.argv[1:])
