all: frb_hunter2.py frb_bulk_analyser.py

frb_hunter2.py: frb_hunter2.grc
	grcc frb_hunter2.grc
	
frb_bulk_analyser.py: frb_bulk_analyser.grc
	grcc frb_bulk_analyser.grc

install: frb_hunter2.py frb_bulk_analyser.py
	cp frb_hunter2.py /usr/local/bin
	cp frb_bulk_analyser.py /usr/local/bin
	chmod 755 /usr/local/bin/frb_*.py
	cp frb_buf_mgr.py /usr/local/bin
	cp pulse_finder_1.py /usr/local/bin
	cp runner /usr/local/bin
	cp fft_logger_1.py /usr/local/bin
	cp frb_raw_to_fb.py /usr/local/bin
	cp process_frb_dedisp.py /usr/local/bin
	cp analyse_plt.py /usr/local/bin

clean:
	rm -f frb_hunter2.py frb_bulk_analyser.py
