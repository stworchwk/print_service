from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from configparser import ConfigParser

from print_pdf import printPdf
from promptpayqr import qr_code

class GeneratePdf():
    def bill(self, task):
        global current_line
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
        current_line = page_height - margin #inch
        first_top_margin = 0.2 #inch

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

        pdf = canvas.Canvas(fileName)

        #Setting page
        pdf.setPageSize((page_width, page_height))

        #Title
        current_line = current_line - (points * first_top_margin) #inch
        text = template['title']
        createStringCenterContent(text, 'bold', 14.4)

        #Point
        text = task['point_name']
        createStringCenterContent(text, 'regular')

        #No
        if task['order_no'] is not None:
            text = task['order_no']
            createStringCenterContent(text, 'regular')

        #Order Code
        text = template['order_code'] + ' : ' + task['order_code']
        createStringContent(text, 'regular')

        #Order Table
        text = template['order_table'] + ' : ' + task['order_table']
        createStringContent(text, 'regular')

        #Order Print By
        text = template['print_by'] + ' : ' + task['order_created_by']
        createStringContent(text, 'regular')

        #Order Print Datetime
        text = template['print_date_time'] + ' : ' + task['order_print_date_time']
        createStringContent(text, 'regular', font_size_regular)

        #Order List
        current_line = current_line - 6
        text = template['head_1_text']
        createStringContent(text, 'bold', font_size_regular, 'left', False)
        text = template['head_2_text']
        createStringContent(text, 'bold', font_size_regular, 'right')

        for order_list in task['order_lists']:
            #List1
            text = order_list['name']
            createStringContent(text, 'regular', font_size_regular, 'left', False)
            text = str(order_list['amount'])
            createStringContent(text, 'regular', font_size_regular, 'right')

        #Total
        current_line = current_line - 4
        text = template['total_text'] + ' ' + str(task['order_lists_count'])
        createStringContent(text, 'bold', font_size_regular, 'right')

        #Save pdf
        pdf.save()

        printPdf(self, config['file_name'], task['printer_name'])

    def receipt(self, task):
        global current_line
        CONFIG_FILE_NAME = 'receipt_config.ini'

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

        pdf = canvas.Canvas(fileName)

        #Setting page
        pdf.setPageSize((page_width, page_height))

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
        text = "เลขที่ : " + task['order_code']
        createStringContent(text, 'regular')

        #Order Date
        text = "วันที่ : " + task['order_print_date']
        createStringContent(text, 'regular')

        #Order Time
        text = "เวลา : " + task['order_print_time']
        createStringContent(text, 'regular')

        #Order Details
        current_line = current_line - 2
        for order_list in task['order_lists']:
            #List
            text = order_list['text']
            createStringContent(text, 'regular', None, 'left', False)
            text = order_list['price']
            createStringContent(text, 'regular', None, 'right')
        

        #Order Summary
        current_line = current_line - 2
        #Total
        text = template['total_text']
        createStringContent(text, 'bold', font_size_regular, 'left', False)
        text = str(task['total_price'])
        createStringContent(text, 'bold', font_size_regular, 'right')

        #Discount
        if task['discount'] > 0:
            text = template['discount_text']
            createStringContent(text, 'bold', font_size_regular, 'left', False)
            text = str(task['discount'])
            createStringContent(text, 'bold', font_size_regular, 'right')

        #Net Total
        text = template['net_total_text']
        createStringContent(text, 'bold', font_size_regular, 'left', False)
        text = str(task['net_total'])
        createStringContent(text, 'bold', font_size_regular, 'right')

        #Vat
        text = template['vat_text']
        createStringContent(text, 'bold', font_size_regular, 'left', False)
        text = str(task['vat'])
        createStringContent(text, 'bold', font_size_regular, 'right')

        #Total Pay
        text = template['total_pay_text']
        createStringContent(text, 'bold', font_size_regular, 'left', False)
        text = str(task['total'])
        createStringContent(text, 'bold', font_size_regular, 'right')

        if float(task['receive']) > 0 or float(task['change']) > 0:
            #receive
            text = template['receive_text']
            createStringContent(text, 'bold', font_size_regular, 'left', False)
            text = str(task['receive'])
            createStringContent(text, 'bold', font_size_regular, 'right')

            #change
            text = template['change_text']
            createStringContent(text, 'bold', font_size_regular, 'left', False)
            text = str(task['change'])
            createStringContent(text, 'bold', font_size_regular, 'right')

        #Footer
        current_line = current_line - (0.2 * points)

        if task['is_real_bill'] == False:
            #Payment text
            text = template['payment_text']
            createStringCenterContent(text, 'regular')

            #Generate Promptpay QRCode
            qr_code(template['promptpay_id'], one_time=True, path_qr_code="", country="TH" ,money=str(task['total']), currency="THB")

            #Specify Promptpay QRCode size
            pp_image = template['promptpay_qrcode_file_name']
            pp_im = Image.open(pp_image)
            pp_width, pp_height = pp_im.size
            pp_ratio = pp_width / pp_height
            pp_image_width = float(template['promptpay_qrcode_size']) * points #inch
            pp_image_height = pp_image_width / pp_ratio

            #Promptpay QRCode
            pdf.drawInlineImage(pp_image, (page_width - pp_image_width) / 2, current_line - pp_image_height, pp_image_width, pp_image_height)
            current_line = current_line - pp_image_height - (0.2 * points)

        #Thank you
        text = template['footer_thank_you']
        createStringCenterContent(text, 'bold', font_size_regular)

        #Save pdf
        pdf.save()

        printPdf(self, config['file_name'], task['printer_name'])