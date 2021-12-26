frb_hunter2.py: frb_hunter2.grc
	grcc frb_hunter2.grc

install: frb_hunter2.py
	cp frb_hunter2.py /usr/local/bin
	chmod 755 /usr/local/bin/frb_hunter2.py
	cp frb_buf_mgr.py /usr/local/bin
	cp frb_analyser1.py /usr/local/bin
