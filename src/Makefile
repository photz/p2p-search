.PHONY: diagnosis test bundlehtml peer

all:
	echo 'nothing'

bundlehtml:
	sed -e '/<JAVASCRIPT>/{r peer/webinterface.js' -e 'd}' > tmp.html < peer/webinterface.html
	sed -e '/<BOOTSTRAP>/{r peer/bootstrap.min.css' -e 'd}' > tmp2.html < tmp.html
	sed -e '/<CUSTOM_CSS>/{r peer/webinterface.css' -e 'd}' > peer/webinterface_bundled.html < tmp2.html


peer: bundlehtml
	./peer/p2psearch.py

diagnosis: 
	PYTHONPATH='peer:diagnosis' ./run_multiple.py

clean:
	rm -r __pycache__
	rm *.pyc
	rm *.py
	rm *.py~

test:
	PYTHONPATH='peer:diagnosis' python3 test/message_test.py
	PYTHONPATH='peer:diagnosis' python3 test/index_test.py


