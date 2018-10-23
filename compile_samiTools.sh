python setup.py install
python setup.py py2exe
mv dist/sami2marc_products.exe sami2marc_products.exe
mv dist/sami2marc_authorities.exe sami2marc_authorities.exe
cp sami2marc_products.exe ../sami2marc_products.exe
cp sami2marc_authorities.exe ../sami2marc_authorities.exe
rmdir dist
rm bin/__pycache__/sami2marc_products.cpython-34.pyc
rm bin/__pycache__/sami2marc_authorities.cpython-34.pyc
rmdir bin/__pycache__
rm -rf build