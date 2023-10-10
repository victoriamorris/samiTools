python setup.py install --install-lib "C:\Python installation"
read -p "Press [Enter]"
pyinstaller sami2marc_authorities.py -F
pyinstaller sami2marc_products.py -F
mv dist/sami2marc_products.exe sami2marc_products.exe
mv dist/sami2marc_authorities.exe sami2marc_authorities.exe
cp sami2marc_products.exe ../sami2marc_products.exe
cp sami2marc_authorities.exe ../sami2marc_authorities.exe
rm -rf dist
rm sami2marc_authorities.spec
rm sami2marc_products.spec
rm -rf samiTools/__pycache__
rm -rf samiTools.egg-info
rm -rf build
read -p "Press [Enter]"

