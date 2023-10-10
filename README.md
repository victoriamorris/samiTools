# samiTools
Tools for working with SAMI files 

## Requirements

None.

## Installation

From GitHub:
```
git clone https://github.com/victoriamorris/samiTools
cd samiTools
```
To install as a Python package:
```
python setup.py install
```
To create stand-alone executable (.exe) files for individual scripts:
```
python setup.py py2exe
```
Executable files will be created in the folder \dist, and should be copied to an executable path.

Both of the above commands can be carried out by running the shell script:
```
compile_samiTools.sh
```
## Usage

### Running scripts

The following scripts can be run from anywhere, once the package is installed:

#### sami2marc_authorities

Converts SAMI records for **authorities** to MARC 21 Authority 
in either MARC exchange (`.lex`) or MARC XML (`.xml`) format.
```
Usage: sami2marc_authorities.exe -i <ifile> -o <ofile>
                                [--date <yyyymmdd>|--max_size <number|size>]
                                [--tidy] [--header]

Arguments:
    -i    path to Input file
    -o    path to Output file

Options:
    --date <yyyymmdd>
              Split output into two files by specified date.
    --max_size <number|size>
              Split output by size or number of records
NOTE: --date and --max_size cannot be used at the same time.

Flags:
    --tidy    Tidy authority files to facilitate load to MetAg.
    --header  Include MetAg headers in MARC XML records
    --help    Show help message and exit.

```
Input files must be SAMI Authority files in **text** format (with `.txt` or `.prn` file extensions) or **MARC XML** format (with `.xml` file extensions).

The output file will either be a MARC exchange format file (with a `.lex` file extension)
or a MARC XML file (with an `.xml` file extension)
according to the file extension of the `<ofile>` parameter.

Records with errors will be written to `<ofile>_errors`, and will NOT appear in any other output files.

If parameter `--date` is specified:
* Records with a created or amended date ealier than the value specified will be written to `<ofile>_pre_<date>`;
* Records with a created or amended date equal to or later than the value specified will be written to `<ofile>_post_<date>`.
* The `--date` parameter MUST be in the form yyyymmdd, e.g. 20100607.

**NOTE: `--date` and `--max_size` cannot be used at the same time.**

If parameter `--tidy` is specified:
* If no 001 is present, one will be created from the first instance of 901 $a;
* 904 $a and 905 $a will be combined into a single 904 field ($a and $b);
* 906 $a and 907 $a will be combined into a single 906 field ($a and $b);
* Created and Amended date will be converted from dd/mm/yy to yyyymmdd format.

If parameter `--max_size` is specified:
* `--max_size` must be a positive integer, optionally followed by the letter K;
* `--max_size` is EITHER the maximum number of records in an output file OR the (approx.) maximum file size (in KB) if the number has the suffix 'K';
* Output will be written to a sequence of files with the same name as the input file, but with a suffix indicating its order in the generated output sequence
* EXCEPT in the special case of `--max_size 1` (the file is split into individual records) in which case the output files will be labelled with the record identifier.
* Records with duplicate identifiers will be labelled with a _DUPLICATE suffix.
* Records without identifiers will be labelled with _NO IDENTIFIER.

**NOTE: `--date` and `--max_size` cannot be used at the same time.**

If parameter --header is specified:
* MARC XML records will be given a `<header>` to make them suitable for the Metadata Aggregator.
* The `<header>` will include the record identifier.
* For deleted records, the `<header>` element will have an `@status="deleted"` attribute.

**NOTE: `--header` can only be used if the output is MARC XML.**

Input files can be in any of the formats listed below.

##### SAMI text format

The format of Authority records exported directly from SAMI.
May have `.txt` or `.prn` file extensions.

###### Example record

```
XX246721        		NAME		AUTHORIZED		9/11/2016		JCOLLIER  		9/11/2016		JCOLLIER  		NEVER
000:   |az n  n a
008:   |a161109   a    aaa
100:   |aWright, David,|b1976-
300:   |apn
312:   |ahttp://www.bach-cantatas.com/Bio/Wright-David.htm
680:   |aharpsichord
```

##### XML

An XML format harvested via OAI-PMH, or created during a previous iteration of the same script, using the `--header` option.

###### Example record

```
<record xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:marc="http://www.loc.gov/MARC21/slim" xmlns:bl="http://www.bl.uk/schemas/digitalobject/entities#" xmlns:blit="http://bl.uk/namespaces/blit">
    <header>
        <identifier>XX1</identifier>
    </header>
    <metadata>
        <marc:record xsi:schemaLocation="http://www.loc.gov/MARC21/slim http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd">
            <marc:leader>00844     2200313   4500</marc:leader>
            <marc:controlfield tag="000">a</marc:controlfield>
            <marc:controlfield tag="001">XX1</marc:controlfield>
            <marc:datafield tag="024" ind1=" " ind2=" ">
                <marc:subfield code="a">0000 0001 2128 5074</marc:subfield>
            </marc:datafield>
            <marc:datafield tag="100" ind1=" " ind2=" ">
                <marc:subfield code="a">Corea, Chick,</marc:subfield>
            </marc:datafield>
            <marc:datafield tag="300" ind1=" " ind2=" ">
                <marc:subfield code="a">pn</marc:subfield>
            </marc:datafield>
            <marc:datafield tag="312" ind1=" " ind2=" ">
                <marc:subfield code="a">NGJ</marc:subfield>
            </marc:datafield>
            <marc:datafield tag="312" ind1=" " ind2=" ">
                <marc:subfield code="a">http://isni.org/isni/0000000121285074 (data confidence 50)</marc:subfield>
            </marc:datafield>
            <marc:datafield tag="500" ind1=" " ind2=" ">
                <marc:subfield code="a">Chick Corea Quartet</marc:subfield>
            </marc:datafield>
            <marc:datafield tag="500" ind1=" " ind2=" ">
                <marc:subfield code="a">Chick Corea Trio</marc:subfield>
            </marc:datafield>
            <marc:datafield tag="500" ind1=" " ind2=" ">
                <marc:subfield code="a">Circle (Group)</marc:subfield>
            </marc:datafield>
            <marc:datafield tag="500" ind1=" " ind2=" ">
                <marc:subfield code="a">Origin (Group)</marc:subfield>
            </marc:datafield>
            <marc:datafield tag="500" ind1=" " ind2=" ">
                <marc:subfield code="a">Return To Forever</marc:subfield>
            </marc:datafield>
            <marc:datafield tag="500" ind1=" " ind2=" ">
                <marc:subfield code="a">Chick Corea Elektric Band</marc:subfield>
            </marc:datafield>
            <marc:datafield tag="680" ind1=" " ind2=" ">
                <marc:subfield code="a">Jazz keyboardist, composer</marc:subfield>
            </marc:datafield>
            <marc:datafield tag="901" ind1=" " ind2=" ">
                <marc:subfield code="a">id: XX1</marc:subfield>
            </marc:datafield>
            <marc:datafield tag="902" ind1=" " ind2=" ">
                <marc:subfield code="a">fmt: NAME</marc:subfield>
            </marc:datafield>
            <marc:datafield tag="903" ind1=" " ind2=" ">
                <marc:subfield code="a">level: AUTHORIZED</marc:subfield>
            </marc:datafield>
            <marc:datafield tag="904" ind1=" " ind2=" ">
                <marc:subfield code="a">created: 6/8/1996</marc:subfield>
            </marc:datafield>
            <marc:datafield tag="905" ind1=" " ind2=" ">
                <marc:subfield code="a">created_by:</marc:subfield>
            </marc:datafield>
            <marc:datafield tag="906" ind1=" " ind2=" ">
                <marc:subfield code="a">modified: 19/1/2016</marc:subfield>
            </marc:datafield>
            <marc:datafield tag="907" ind1=" " ind2=" ">
                <marc:subfield code="a">modified_by: IDAVIS</marc:subfield>
            </marc:datafield>
            <marc:datafield tag="908" ind1=" " ind2=" ">
                <marc:subfield code="a">cataloged: 19/1/2016</marc:subfield>
            </marc:datafield>
            <marc:datafield tag="909" ind1=" " ind2=" ">
                <marc:subfield code="a">source:</marc:subfield>
            </marc:datafield>
            <marc:datafield tag="961" ind1=" " ind2=" ">
                <marc:subfield code="a">Corea, Chick,</marc:subfield>
            </marc:datafield>
        </marc:record>
    </metadata>
</record>
```

#### sami2marc_products

Converts SAMI records for **products** (words, reocordings, etc.) to MARC 21 Bibliographic
in either MARC exchange (`.lex`) or MARC XML (`.xml`) format.
```
Usage: sami2marc_products.exe -i <input_path> -o <output_path>
                            [--max_size <number|size>]
                            [--oral_history <path>]
                            [-x] [--header]

Arguments:
    -i    path to FOLDER containing Input files
    -o    path to FOLDER to contain Output files

Options:
    --max_size <number|size>
              Split output by size or number of records
    --oral_history <path>
               Save oral history records to a separate folder

Flags:
    -x        Output files will be MARC XML rather than MARC 21 (.lex)
    --header  Include MetAg headers in MARC XML records
    --help    Show help message and exit.
```
The output files will either be a MARC exchange format file (with `.lex` file extensions)
or MARC XML files (with `.xml` file extensions) according to whether the `-x` flag has been set.

If parameter `--max_size` is specified:
* `--max_size` must be a positive integer, optionally followed by the letter K;
* `--max_size` is EITHER the maximum number of records in an output file OR the (approx.) maximum file size (in KB) if the number has the suffix 'K';
* Output will be written to a sequence of files with the same name as the input file, but with a suffix indicating its order in the generated output sequence
* EXCEPT in the special case of `--max_size 1` (the file is split into individual records) in which case the output files will be labelled	with the record identifier.
* Records with duplicate identifiers will be labelled with a _DUPLICATE suffix.
* Records without identifiers will be labelled with _NO IDENTIFIER.

If parameter `--oral_history` is specified:
* **This will over-ride the value of `--max_size` (if set) and set `--max_size 1`**
* `--oral_history` must be a valid folder path;
* Records for oral histories and interviews will be saved to this path;
* Records are selected on the basis of 975 $a 'ark' AND 653 $a 'oral histories' or 'interviews' (case insensitive).

If parameter --header is specified:
* MARC XML records will be given a `<header>` to make them suitable for the Metadata Aggregator.
* The `<header>` will include the record identifier.
* For deleted records, the `<header>` element will have an `@status="deleted"` attribute.

**NOTE: `--header` can only be used if `-x` is also specified.**

Input files can be in any of the formats listed below.

##### prn

An XML format exported directly from SAMI.
 
###### Example record
```
<catalog>
    <marc>
        <marcEntry tag="000" label="Leader" ind="  ">|aam     a</marcEntry>
        <marcEntry tag="008" label="Fixed  field data" ind="  ">|a180214n                      000 0 eng u</marcEntry>
        <marcEntry tag="087" label="SHELFMARK" ind="  ">|aC728/666</marcEntry>
        <marcEntry tag="490" label="Collection title" ind="  ">|aSerious Speakout Demo Tape collection|=^A230912</marcEntry>
        <marcEntry tag="702" label="Contributor" ind="  ">|aBalke, J.|c(performer)|?UNAUTHORIZED</marcEntry>
        <marcEntry tag="702" label="Contributor" ind="  ">|aunnamed|cband|=^A3560</marcEntry>
        <marcEntry tag="633" label="Genre" ind="  ">|aDemo recordings|=^A251347</marcEntry>
        <marcEntry tag="596" label="Held by" ind="  ">|a3</marcEntry>
        <marcEntry tag="246" label="Item title" ind="  ">|a[Title unknown]</marcEntry>
        <marcEntry tag="301" label="Item duration" ind="  ">|a4 min. 07 sec.</marcEntry>
        <marcEntry tag="974" label="MD-ARK" ind="  ">|aark:/81055/vdc_100058552022.0x000052</marcEntry>
        <marcEntry tag="975" label="L-ARK: INGESTED" ind="  ">|aark:/81055/vdc_100058676993.0x000006</marcEntry>
        <marcEntry tag="971" label="Cataloguing status" ind="  ">|aprc</marcEntry>
        <marcEntry tag="312" label="Content  code" ind="  ">|aa</marcEntry>
        <marcEntry tag="001" label="Record control no." ind="  ">|aCKEY8128528</marcEntry>
    </marc>
    <call>
        <callNumber>   C728/666 S1 C1</callNumber>
        <library>RECORDING</library>
        <numberOfCallHolds>0</numberOfCallHolds>
        <numberOfCopies>1</numberOfCopies>
        <copiesOnReserve>0</copiesOnReserve>
        <item>
            <copyNumber>1</copyNumber>
            <itemID>8128528-1001</itemID>
            <library>RECORDING</library>
            <libraryDescription>RECORDING</libraryDescription>
            <location>STORE+E</location>
            <homeLocation>STORE+E</homeLocation>
            <price currency="GBP" >0.00</price>
            <category1>POP</category1>
            <type>RECORDING</type>
            <numberOfPieces>1</numberOfPieces>
            <dateCreated>2018-05-10</dateCreated>
            <isPermanent>true</isPermanent>
        </item>
    </call>
</catalog>
```
##### XML

An XML format harvested via OAI-PMH, or created during a previous iteration of the same script, using the `--header` option.

###### Example record
```
<header>
    <identifier>1</identifier>
</header>
<metadata>
    <record>
        <datafield tag="099" ind1="" ind2="">
            <subfield code="z">m</subfield>
        </datafield>
        <controlfield tag="000">am  0c a</controlfield>
        <controlfield tag="001">CKEY1</controlfield>
        <datafield tag="087" ind1="" ind2="">
            <subfield code="a">1CD0033672</subfield>
        </datafield>
        <datafield tag="299" ind1="" ind2="">
            <subfield code="a">Jamaican rumba/Benjamin</subfield>
        </datafield>
        <datafield tag="702" ind1="" ind2="">
            <subfield code="a">Adler, Larry,</subfield>
            <subfield code="b">1914-2001</subfield>
            <subfield code="c">Harmonica</subfield>
            <subfield code="=">^A14637</subfield>
        </datafield>
        <datafield tag="702" ind1="" ind2="">
            <subfield code="a">Robinson, Eric</subfield>
            <subfield code="c">(conductor)</subfield>
            <subfield code="?">UNAUTHORIZED</subfield>
        </datafield>
        <datafield tag="702" ind1="" ind2="">
            <subfield code="a">Pro Arte Orchestra</subfield>
            <subfield code="?">UNAUTHORIZED</subfield>
        </datafield>
        <datafield tag="260" ind1="" ind2="">
            <subfield code="c">1957</subfield>
        </datafield>
        <datafield tag="551" ind1="" ind2="">
            <subfield code="a">Watford Town Hall</subfield>
        </datafield>
        <datafield tag="596" ind1="" ind2="">
            <subfield code="a">3</subfield>
        </datafield>
        <datafield tag="301" ind1="" ind2="">
            <subfield code="a">3 min. 33 sec.</subfield>
        </datafield>
        <datafield tag="509" ind1="" ind2="">
            <subfield code="a">1958 Original recording (P) date</subfield>
        </datafield>
        <datafield tag="974" ind1="" ind2="">
            <subfield code="a">ark:/81055/vdc_100000006155.0x000001</subfield>
        </datafield>
        <datafield tag="976" ind1="" ind2="">
            <subfield code="a">ND</subfield>
        </datafield>
        <datafield tag="971" ind1="" ind2="">
            <subfield code="a">de</subfield>
        </datafield>
        <datafield tag="312" ind1="" ind2="">
            <subfield code="a">a</subfield>
        </datafield>
        <datafield tag="024" ind1="" ind2="">
            <subfield code="a">10000012</subfield>
            <subfield code="2">nd</subfield>
        </datafield>
        <datafield tag="999" ind1="" ind2="">
            <subfield code="a">1CD0033672 D1 S1 BD6 EMI PHOENIXA</subfield>
            <subfield code="w">ALPHANUM</subfield>
            <subfield code="c">1</subfield>
            <subfield code="i">1-1001</subfield>
            <subfield code="d">15/8/1995</subfield>
            <subfield code="l">STORE</subfield>
            <subfield code="m">RECORDING</subfield>
            <subfield code="r">Y</subfield>
            <subfield code="s">Y</subfield>
            <subfield code="t">RECORDING</subfield>
            <subfield code="u">15/8/1995</subfield>
            <subfield code="x">CLASSICAL</subfield>
            <subfield code="z">ORCHESTRAL</subfield>
        </datafield>
    </record>
</metadata>
```
##### SAMI text format

A text format exported directly from SAMI.

  The file-name should end with one of the following:  
  * export_ALL
  * export_DOCRECITEM
  * export_MLRECITEM
  * export_PUBLPROD
  * export_WORK
  * export_WRSECITEM
  
###### Example record
```
*** DOCUMENT BOUNDARY ***
FORM=WORK
.000. |aam  0c a
.001. |aCKEY637624
.239.   |aMusic For The Royal Fireworks
.240.   |aMusic for the royal fireworks;|carr.
.299.   |aMusic For The Royal Firework/Hande-Baine
.312.   |aw
.596.   |a2
.700.   |aBaines, Anthony Cuthbert|c(arranger)|?UNAUTHORIZED
.700.   |aMackerras, Charles,|b1925-2010|c(arranger)|=^A56137
.700.   |aHandel, George Frideric,|b1685-1759|c(composer)|=^A305
.971.   |aun
.976.   |aND
.974.   |aark:/81055/vdc_100000006155.0x096d5a
.999.   |aXX(2028559.1)|wALPHANUM|c1|i637624-1001|d16/8/1995|lRECORDED|mWORKS-FILE|rY|sY|tWORK|u16/8/1995
```
