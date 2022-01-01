cd ../
find share/sbw/ -iname "*.glade" | xargs xgettext --from-code=UTF-8 -o po/sbw_glade.pot
find sbw/ -iname "*.py" | xargs xgettext --from-code=UTF-8 -o po/sbw_py.pot
cd po
msgcat sbw_glade.pot sbw_py.pot > sbw.pot
rm sbw_glade.pot sbw_py.pot
