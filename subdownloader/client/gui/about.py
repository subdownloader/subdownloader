# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

import logging

from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt

from subdownloader import project
from subdownloader.client.gui.about_ui import Ui_AboutDialog

log = logging.getLogger("subdownloader.client.gui.about")


class AboutDialog(QDialog):

    def __init__(self, parent):
        QDialog.__init__(self, parent, flags=Qt.WindowFlags())
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)

        self.setWindowTitle(_('About {project}').format(project=project.TITLE))

        self.ui.label_project.setText(project.TITLE)

        self.ui.label_version.setText(project.VERSION)

        self.ui.txtAbout.setText(
            '<b>{homepage_str}:</b><br />'
            '<a href="{website_homepage}">{website_homepage}</a><br />'
            '<br />'
            '<b>{releases_str}:</b><br />'
            '<a href="{website_releases}">{website_releases}</a><br />'
            '<br />'
            '<b>{issues_str}:</b><br />'
            '<a href="{websites_issues}">{websites_issues}</a>'.format(
                homepage_str=_('Homepage'),
                releases_str=_('New versions on'),
                issues_str=_('Bugs and new requests'),
                website_homepage=project.WEBSITE_MAIN,
                website_releases=project.WEBSITE_RELEASES,
                websites_issues=project.WEBSITE_ISSUES,
            )
        )
        authors = [
            '{name} &lt;<a href="mailto:{mail}" >{mail}</a>&gt;<br />'.format(name=author.name(), mail=author.mail())
                for author in project.read_authors()]
        self.ui.txtAuthors.setText(''.join(authors))

        self.ui.txtLicense.setText(self.get_license())

        self.ui.buttonClose.clicked.connect(self.onButtonClose)

    def onButtonClose(self):
        self.reject()

    def get_license(self):
        license = '<p>{license_title}</p><p>{license_freesoftware}</p>' \
                  '<p>{license_distribution}</p><p>{license_address}</p>'.format(
            license_title=_('Copyright (c) 2007-{year}, Subdownloader Developers</p>').format(year=project.YEAR),
            license_freesoftware=_('This program is free software; you can redistribute it and/or modify it '
                                   'under the terms of the GNU General Public License as published by the Free Software '
                                'Foundation; either version 3 of the License, or (at your option) any later version.'),
            license_distribution=_('This program is distributed in the hope that it will be useful,'
                                   'but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or'
                                   'FITNESS FOR A PARTICULAR PURPOSE.'
                                   'See the GNU General Public License for more details.'),
            license_address=_('You should have received a copy of the GNU General Public License along with this program;'
                              ' if not, write to the Free Software Foundation, Inc., 51 Franklin Street, '
                              'Fifth Floor, Boston, MA 02110-1301 USA.'),
            )
        return license
