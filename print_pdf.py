import sys
import win32print
from PDFNetPython3 import PDFNet, PDFDoc, PrinterMode, Print, Rect
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
    
    printerMode = PrinterMode()
    printerMode.SetAutoCenter(False)
    printerMode.SetScaleType(printerMode.e_ScaleType_ReduceToOutputPage)
    width = float(config['paper_width']) #inch
    height = float(config['paper_height']) #inch
    printerMode.SetPaperSize(Rect(0, 0, (width * 72), (height * 72))) #72 points = 1 inch
    Print.StartPrintJob(doc, printer_name, doc.GetFileName(), "", None, printerMode, None)