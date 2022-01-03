frb_hunter2.py: frb_hunter2.grc
	grcc frb_hunter2.grc
	
frb_bulk_analyser.py: frb_bulk_analyser.grc
	grcc frb_bulk_analyser.grc

install: frb_hunter2.py frb_bulk_analyser.py
	cp frb_hunter2.py /usr/local/bin
	c[ frb_bulk_analyser.py /usr/local/bin
	chmod 755 /usr/local/bin/frb_*.py
	cp frb_buf_mgr.py /usr/local/bin
	cp pulse_finder_1.py /usr/local/bin
