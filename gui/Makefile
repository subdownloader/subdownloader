all: main_ui.py imdb_ui.py images_rc.py preferences_ui.py

main_ui.py : main.ui
	pyuic4 main.ui | sed -s s/^.*Margin.*// | sed -e s/^.*boxlayout\.setObjectName.*// > main_ui.py

imdb_ui.py : imdb.ui
	pyuic4 imdb.ui | sed -s s/^.*Margin.*// | sed -e s/^.*boxlayout\.setObjectName.*// > imdb_ui.py

preferences_ui.py : preferences.ui
	pyuic4 preferences.ui | sed -s s/^.*Margin.*// | sed -e s/^.*boxlayout\.setObjectName.*// > preferences_ui.py

about_ui.py : about.ui
	pyuic4 about.ui | sed -s s/^.*Margin.*// | sed -e s/^.*boxlayout\.setObjectName.*// > about_ui.py

images_rc.py : images.qrc
	pyrcc4 images.qrc > images_rc.py

clean :
	rm main_ui.py imdb_ui.py images_rc.py
