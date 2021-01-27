import sys
import win32print
from PDFNetPython3 import PDFNet, PDFDoc, PrinterMode, Print, Rect
#from PDFNetPython3 import *
from configparser import ConfigParser

CONFIG_FILE_NAME = 'bill_config.ini'

config = ConfigParser()
config.read(CONFIG_FILE_NAME, encoding="utf8")
config = config['bill']


def printPdf(self, file_name, printer_name):
    PDFNet.Initialize()

    doc = PDFDoc(file_name)
    doc.InitSecurityHandler()

    if printer_name is None:
        printer_name = win32print.GetDefaultPrinter()
    else:
        checkHasPrinter = False
        for printer_info in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL, None, 1):
            if printer_info[2] == printer_name:
                checkHasPrinter = True

        if checkHasPrinter:
            handle = win32print.OpenPrinter(printer_name)
            attributes = win32print.GetPrinter(handle)[13]

            if (attributes & 0x00000400):
                return False
            else:
                printerMode = PrinterMode()
                printerMode.SetAutoCenter(False)
                printerMode.SetScaleType(printerMode.e_ScaleType_ReduceToOutputPage)
                width = float(config['paper_width']) #inch
                height = float(config['paper_height']) #inch
                printerMode.SetPaperSize(Rect(0, 0, (width * 72), (height * 72))) #72 points = 1 inch
                Print.StartPrintJob(doc, printer_name, doc.GetFileName(), "", None, printerMode, None)
                return True
        else:
            return False

    
