from PyQt4 import QtGui
from PyQt4 import QtCore
import sys


app = QtGui.QApplication(sys.argv)
printer = QtGui.QPrinter()
dpi = 96
#painter = QPainter(printer)
printer.setResolution(dpi)
printer.setOutputFileName("foo.pdf")
printer.setPageSize(QtGui.QPrinter.Letter)
printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
printer.setPageMargins(30, 16, 12, 20, QtGui.QPrinter.Millimeter)
#painter.scale(50, 50)
font = QtGui.QFont()
font.setPointSize(12)
doc = QtGui.QTextDocument()
doc.setDefaultFont(font)


html = ""
html += ("<html>"
         "<body>"
         "<p><img src='C:\\workspace\\PyExcel\\images\\SGlogo.png'></p>"
         "<p style='font:60px'>Que ricos estan muchachones</p>"
         "<table border=1 cellpadding=2 cellspacing=2>"
         "<tr style={tr}>"
         "  <td style={td}>1</td>"
         "  <td style={td}>2</td>"
         "  <td style={td}>3</td>"
         "  <td style={td}>4</td>"
         "</tr>"
         "<tr style={tr}>"
         "  <td style={td}>1</td>"
         "  <td style={td}>2</td>"
         "  <td style={td}>3</td>"
         "  <td style={td}>4</td>"
         "</tr>"
         "</body>"
         "</html>".format(tr="", td="padding:50px"))


# Done.



