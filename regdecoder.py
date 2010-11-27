#!/usr/bin/env python
#
# Register Decoder.v 0.1
#
# Copyright (C) 2010 Marek Skuczynski <mareksk7@gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; version 2 of
# the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#


import sys, fnmatch, os
from PyQt4 import QtGui, QtCore
from xml.etree.ElementTree import ElementTree

def bits_to_label(val, tf):
    tli = tf.getiterator('label')
    info = ""
    for li in tli:
	l_mask = int(li.attrib['mask'],0)
	if (val & l_mask) == l_mask:
	    if len(info) > 0:
		info = info + ', ' + li.attrib['info']
	    else:
		info = li.attrib['info']
    if len(info) > 0:
	    return info
    return '-- missing info --'

def value_to_label(val, tf):
    tli = tf.getiterator('label')
    for li in tli:
	l_val = int(li.attrib['value'],0)
	if val == l_val:
	    return li.attrib['info']
    return '-- missing info --'

class MainWindow(QtGui.QMainWindow):

    def showRegFields(self, value, tr):
	str1=''
	tri = tr.getiterator('field')
	for tf in tri:
	    str1 = str1 + '<tr>'
	    f_size = int(tf.attrib['size'],0)
	    f_offs = int(tf.attrib['offset'],0)

	    if f_size == 1:
		str1 = str1 + '<td align="center">%d</td>' % (f_offs)
	    else:
		str1 = str1 + '<td align="center">%d..%d</td>' % (f_offs, f_offs + (f_size-1))

	    f_mask = reduce(lambda x, y: x+(2**(y-1)), range(1,f_size+1))
	    f_val  = (value  >> f_offs) & f_mask

	    str1 = str1 + '<td align="center">' + str(f_size) + '</td>'
	
	    str_val = '0x%X' % (f_val)
	
	    f_type = tf.get('label');
	    if f_type == 'bitmap':
		str1 = str1 + '<td align="right">%s</td><td align="center">%s</td><td>%s</td>' % (str_val, tf.attrib['name'], bits_to_label(f_val, tf))
	    elif f_type == 'value':
		str1 = str1 + '<td align="right">%s</td><td align="center">%s</td><td>%s</td>' % (str_val, tf.attrib['name'], value_to_label(f_val, tf))
	    else:
		str1 = str1 + '<td align="right">%s</td><td align="center">%s</td>' % (str_val, tf.attrib['name'])
	    str1 = str1 + '</tr>'
	return str1

    def doEval(self, checked):
	self.teInfo.clear()

	v = self.eboxVal.text().toUInt(0)
	if v[1] == False:
	    self.teInfo.insertHtml('<b>Invalid numeric value</b>')
	    return

	str1 = '<table border="1" cellpadding="3">'
	str1 = str1 + '<tr><th>Bits</th><th>Size</th><th>Value</th><th>Name</th><th>Description</th></tr>'

	tr_modules = self.regtree.getiterator('module')
	for tm in tr_modules:
	    if tm.attrib['name'] == self.cboxMod.currentText():
		tr_regs = tm.getiterator('register')
		for tr in tr_regs:
		    if tr.attrib['name'] == self.cboxReg.currentText():
			str1 = str1 + self.showRegFields(v[0], tr)
			self.teInfo.insertHtml(str1 + '</table>')
			return

    def modItemChanged(self, name):
	self.cboxReg.clear()

	slist = QtCore.QStringList()

	tr_modules = self.regtree.getiterator('module')
	for tm in tr_modules:
	    if tm.attrib['name'] == name:
		tr_regs = tm.getiterator('register')
		for tr in tr_regs:
		    slist.append(tr.attrib['name'])

	slist.sort()
	self.cboxReg.addItems(slist)

    def regItemChanged(self, name):
	self.eboxReg.clear()
	tr_modules = self.regtree.getiterator('module')
	for tm in tr_modules:
	    if tm.attrib['name'] == self.cboxMod.currentText():
		tr_regs = tm.getiterator('register')
		for tr in tr_regs:
			if tr.attrib['name'] == self.cboxReg.currentText():
				if tr.attrib['addr']:
					self.eboxReg.setText(tr.attrib['addr'])
					return

    def about(self):
	QtGui.QMessageBox.about(self, "About the Register Decorder",
            "Copyrights by Marek Skuczynski <mareksk7@gmail.com>")

    def openRegDataFile(self):
	fnames = fnmatch.filter(os.listdir('.'), 'regs_*.xml')

	if len(fnames) > 1:
	    fname = QtGui.QFileDialog.getOpenFileName(self, 'Select a register file', '.', 'Regs (regs_*.xml)')
	else:
	    fname = fnames[0]

	self.regtree = ElementTree()
	self.regtree.parse(fname)

	trs = self.regtree.getiterator('registers')
	for tr in trs:
		tr_modules = tr.getiterator('module')
		break

	mlist = QtCore.QStringList()

	for tm in tr_modules:
		mlist.append(tm.attrib['name'])
	mlist.sort()

	return mlist

    def __init__(self):
	QtGui.QMainWindow.__init__(self)

	mlist = self.openRegDataFile()

	w = QtGui.QWidget()

	labMod = QtGui.QLabel('Module')
	labReg = QtGui.QLabel('Register')
	labLoc = QtGui.QLabel('Location')
	labVal = QtGui.QLabel('Value')

	self.eboxVal = QtGui.QLineEdit()
	self.eboxReg = QtGui.QLineEdit()
	self.eboxReg.setReadOnly(True)
	self.cboxReg = QtGui.QComboBox()
	self.cboxMod = QtGui.QComboBox()

	self.connect(self.cboxMod, QtCore.SIGNAL('currentIndexChanged(const QString&)'), self.modItemChanged)
	self.connect(self.cboxReg, QtCore.SIGNAL('currentIndexChanged(const QString&)'), self.regItemChanged)
	self.cboxMod.addItems(mlist)

	grid = QtGui.QGridLayout()
	grid.setSpacing(10)

	grid.addWidget(labMod, 1, 0)
	grid.addWidget(self.cboxMod, 1, 1)

	grid.addWidget(labReg, 2, 0)
	grid.addWidget(self.cboxReg, 2, 1)

	grid.addWidget(labLoc, 3, 0)
	grid.addWidget(self.eboxReg, 3, 1)

	grid.addWidget(labVal, 4, 0)
	grid.addWidget(self.eboxVal, 4, 1)

#	grid.addWidget(labVal, 4, 0)
	btnEval = QtGui.QPushButton('Evaluate')
	self.connect(btnEval, QtCore.SIGNAL('clicked(bool)'), self.doEval)
	grid.addWidget(btnEval, 4, 2)

	self.teInfo = QtGui.QTextEdit()
	self.teInfo.setReadOnly(True)
	
	grid.addWidget(self.teInfo, 5, 0, 3, 4)

	w.setLayout(grid)

	self.setCentralWidget(w)

	self.resize(600, 450)
	self.setWindowTitle('Register Decoder')

	exit = QtGui.QAction(QtGui.QIcon('icons/exit.png'), 'Exit', self)
	exit.setShortcut('Ctrl+Q')
	exit.setStatusTip('Exit the application')
	self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))

	about = QtGui.QAction('About', self)
	about.setStatusTip('About the application')
	self.connect(about, QtCore.SIGNAL('triggered()'), self.about)

	self.statusBar()

	menubar = self.menuBar()
	file = menubar.addMenu('&File')
	file.addAction(exit)

	help = menubar.addMenu('&Help')
	help.addAction(about)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
