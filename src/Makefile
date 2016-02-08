.PHONY: diagnosis test bundlehtml peer

all:
	echo 'nothing'

bundlehtml:
	sed -e '/<javascript>/{r peer/webinterface.js' -e 'd}' > peer/webinterface_bundled.html < peer/webinterface2.html


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


