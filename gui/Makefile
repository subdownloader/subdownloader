TARGETS= main_ui.py imdb_ui.py images_rc.py preferences_ui.py about_ui.py \
	 login_ui.py chooseLanguage_ui.py expiration_ui.py

all: $(TARGETS)

%_ui.py : %.ui parse_ui.py
	pyuic4 --pyqt3-wrapper $< | python parse_ui.py -- $(TARGETS)> $@

%_rc.py : %.qrc
	pyrcc4 -py3 $< > $@

clean:
	rm -f $(TARGETS)
