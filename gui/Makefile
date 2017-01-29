TARGETS= main_ui.py imdb_ui.py images_rc.py preferences_ui.py about_ui.py \
	 login_ui.py chooseLanguage_ui.py

IMAGES=$(shell find images -type f -printf "%p ")

PYUIC=pyuic5
PYRCC=pyrcc5

.PHONY: all clean

all: $(TARGETS)

%_ui.py : %.ui parse_ui.py Makefile
	$(PYUIC) $< | python parse_ui.py -- $(TARGETS)> $@

%_rc.py : %.qrc $(IMAGES) Makefile
	$(PYRCC) $< > $@

clean:
	rm -f $(TARGETS)
