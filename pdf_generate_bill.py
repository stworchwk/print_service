from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from configparser import ConfigParser

CONFIG_FILE_NAME = 'bill_config.ini'

config = ConfigParser()
config.read(CONFIG_FILE_NAME, encoding="utf8")
template = config['template']
config = config['bill']

#Register Font
pdfmetrics.registerFont(TTFont('bold', config['font_bold']))
pdfmetrics.registerFont(TTFont('regular', config['font_regular']))

fileName = config['file_name']

points = 72 #72 points = 1 inch

#Page size
page_width = float(config['paper_width']) * points #inch
page_height = float(config['paper_height']) * points #inch
font_size_strong = float(config['font_strong_size']) * points #inch
font_size_regular = float(config['font_regular_size']) * points #inch
margin = float(config['page_margin']) * points #inch
margin_bottom_of_line = float(config['margin_bottom_of_line']) * points #inch
margin_bottom_of_image = float(config['margin_bottom_of_image']) * points #inch
current_line = page_height - margin #inch

#Specify logo size
image = config['logo']
im = Image.open(image)
width, height = im.size
ratio = width / height
image_width = float(config['logo_size']) * points #inch
image_height = image_width / ratio


pdf = canvas.Canvas(fileName)

#Setting page
pdf.setPageSize((page_width, page_height))

def createStringCenterContent(text, type, font_size = None):
    global current_line
    if type == 'regular':
        font_name = 'regular'
        if font_size == None:
            font_size = font_size_regular
    else:
        font_name = 'bold'
        if font_size == None:
            font_size = font_size_strong

    pdf.setFont(font_name, font_size)
    text_width = stringWidth(text, font_name, font_size)
    pdf.drawString((page_width - text_width) / 2, current_line, text)
    current_line = current_line - font_size - margin_bottom_of_line

def createStringContent(text, type, font_size = None, align = 'left', next_line = True):
    global current_line
    if type == 'regular':
        font_name = 'regular'
        if font_size == None:
            font_size = font_size_regular
    else:
        font_name = 'bold'
        if font_size == None:
            font_size = font_size_strong

    pdf.setFont(font_name, font_size)
    text_width = stringWidth(text, font_name, font_size)
    if align == 'left':
        align = margin
    elif align == 'right':
        align = (page_width - text_width) - margin
    else:
        align = margin
    pdf.drawString(align, current_line, text)
    if next_line:
        current_line = current_line - font_size - margin_bottom_of_line

#Logo
pdf.drawInlineImage(image, (page_width - image_width) / 2, current_line - image_height, image_width, image_height)
current_line = current_line - image_height - margin_bottom_of_image

#Title
text = template['restaurant_name']
createStringCenterContent(text, 'bold')

#Sub Title Text
text = template['restaurant_branch']
createStringCenterContent(text, 'bold')

#Address
text = template['restaurant_address']
createStringCenterContent(text, 'regular')

#Address2
text = template['restaurant_address_2']
createStringCenterContent(text, 'regular')

#Tel
text = template['restaurant_tel']
createStringCenterContent(text, 'regular')

#Vat Identification
text = template['restaurant_vat_identification']
createStringCenterContent(text, 'regular')

#Sub Title Text
text = template['restaurant_title']
createStringCenterContent(text, 'bold', font_size_regular)

#Order code
current_line = current_line - 2
text = "เลขที่ : B271020/009"
createStringContent(text, 'regular')

#Order Date
text = "วันที่ : อังคาร 27 ตุลาคม 2020"
createStringContent(text, 'regular')

#Order Time
text = "เวลา : 10:36:32"
createStringContent(text, 'regular')

#Order Details
current_line = current_line - 2
#Record 1
text = "1 มอคค่า"
createStringContent(text, 'regular', None, 'left', False)
text = "45"
createStringContent(text, 'regular', None, 'right')

#Record 2
text = "1 สตอเบอรี่โซดา"
createStringContent(text, 'regular', None, 'left', False)
text = "35"
createStringContent(text, 'regular', None, 'right')

#Record 3
text = "1 ข้าวไข่เจียว"
createStringContent(text, 'regular', None, 'left', False)
text = "40"
createStringContent(text, 'regular', None, 'right')

#Order Summary
current_line = current_line - 2
#Total
text = template['total_text']
createStringContent(text, 'bold', font_size_regular, 'left', False)
text = "45"
createStringContent(text, 'bold', font_size_regular, 'right')

#Net Total
text = template['net_total_text']
createStringContent(text, 'bold', font_size_regular, 'left', False)
text = "112.15"
createStringContent(text, 'bold', font_size_regular, 'right')

#Vat
text = template['vat_text']
createStringContent(text, 'bold', font_size_regular, 'left', False)
text = "7.85"
createStringContent(text, 'bold', font_size_regular, 'right')

#Total Pay
text = template['total_pay_text']
createStringContent(text, 'bold', font_size_regular, 'left', False)
text = "120"
createStringContent(text, 'bold', font_size_regular, 'right')

#Footer
current_line = current_line - 10
#Thank you
text = template['footer_thank_you']
createStringCenterContent(text, 'bold', font_size_regular)

#Queue
current_line = current_line - 2
text = "คิว 01"
createStringCenterContent(text, 'bold', 0.18 * points)

#Save pdf
pdf.save()