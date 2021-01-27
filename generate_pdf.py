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
        if task['order_code'] is not None:
            text = template['order_code'] + ' : ' + task['order_code']
            createStringContent(text, 'regular')

        #Order Table
        if task['order_table'] is not None:
            text = template['order_table'] + ' : ' + task['order_table']
            createStringContent(text, 'regular')

        #Order Print By
        if task['order_created_by'] is not None:
            text = template['print_by'] + ' : ' + task['order_created_by']
            createStringContent(text, 'regular')

        #Order Print Datetime
        if task['order_print_date_time'] is not None:
            text = template['print_date_time'] + ' : ' + task['order_print_date_time']
            createStringContent(text, 'regular', font_size_regular)

        #Order List
        current_line = current_line - 6
        text = template['head_1_text']
        createStringContent(text, 'bold', font_size_regular, 'left', False)
        text = template['head_2_text']
        createStringContent(text, 'bold', font_size_regular, 'right')

        if task['order_lists'] is not None:
            for order_list in task['order_lists']:
                #List1
                if order_list['name'] is not None:
                    text = order_list['name']
                    createStringContent(text, 'regular', font_size_regular, 'left', False)
                
                if order_list['amount'] is not None:
                    text = str(order_list['amount'])
                    createStringContent(text, 'regular', font_size_regular, 'right')

        #Total
        if task['order_lists_count'] is not None:
            current_line = current_line - 4
            text = template['total_text'] + ' ' + str(task['order_lists_count'])
            createStringContent(text, 'bold', font_size_regular, 'right')

        if task['order_lists_count'] is not None:
            text = 'คิว ' + str(task['order_lists_count'])
            createStringCenterContent(text, 'bold')

        #Save pdf
        pdf.save()

        return printPdf(self, config['file_name'], task['printer_name'])

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

        if task['is_real_bill'] == True:
            if task['order_head_note'] != None:
                #Note
                text = task['order_head_note']
                for h_text in text.split('\n'):
                    createStringCenterContent(h_text, 'regular')



        #Order code
        if task['order_code'] is not None:
            current_line = current_line - 2
            text = "เลขที่ : " + task['order_code']
            createStringContent(text, 'regular')

        #Order Date
        if task['order_print_date'] is not None:
            text = "วันที่ : " + task['order_print_date']
            createStringContent(text, 'regular')

        #Order Time
        if task['order_print_time'] is not None:
            text = "เวลา : " + task['order_print_time']
            createStringContent(text, 'regular')

        #Order Details
        current_line = current_line - (0.2 * points)

        if task['order_lists'] is not None:
            for order_list in task['order_lists']:
                #List
                text = order_list['text']
                list_text_width = stringWidth(text, 'regular', font_size_regular)
                list_text_width_percent_of_page = ((list_text_width * 100) / page_width)
                count_cut_line = 1
                if list_text_width_percent_of_page > float(config['sub_string_n_percent_of_page']):
                    blank_area = (float(config['sub_string_n_percent_of_page']) * page_width) / 100
                    new_text = ''
                    for s in (text[i] for i in range(len(text))):
                        new_text += s
                        if stringWidth(new_text, 'regular', font_size_regular) > blank_area:
                            if count_cut_line > 1:
                                new_text = '  ' + new_text
                            createStringContent(new_text, 'regular', None, 'left')
                            new_text = ''
                            count_cut_line += 1
                    if new_text != '':
                        if count_cut_line > 1:
                            new_text = '  ' + new_text
                        createStringContent(new_text, 'regular', None, 'left')
                    current_line += (font_size_regular + margin_bottom_of_line) * count_cut_line
                else:
                    createStringContent(text, 'regular', None, 'left', False)
                    
                if order_list['price'] == order_list['discount_price']:
                    text = str(order_list['price'])
                    if order_list['other'] != None:
                        text += order_list['other']
                else:
                    text = str(order_list['price']) + ' ' + str(order_list['discount_price'])
                    text_cut = ' ' + str(order_list['discount_price'])
                    if order_list['other'] != None:
                        text += order_list['other']
                        text_cut += order_list['other']
                    d_price_text_width = stringWidth(text_cut, 'regular', font_size_regular)
                    all_price_text_width = stringWidth(text, 'regular', font_size_regular)
                    center_line = (current_line + (font_size_regular / 2.7))
                    pdf.line((page_width - all_price_text_width - 1), center_line, (page_width - d_price_text_width + 1), center_line)

                createStringContent(text, 'regular', None, 'right')
                if count_cut_line > 1:
                    current_line = current_line - ((font_size_regular + margin_bottom_of_line) * (count_cut_line - 1))

        #Order Summary
        pdf.line(0, current_line, page_width, current_line)
        current_line = current_line - (0.2 * points)

        #Total
        text = template['total_text']
        createStringContent(text, 'regular', font_size_regular, 'left', False)
        
        if task['total_price'] is not None:
            text = str(task['total_price'])
            createStringContent(text, 'regular', font_size_regular, 'right')

        #Discount
        if task['discount'] is not None:
            if task['discount'] > 0:
                text = template['discount_text']
                createStringContent(text, 'regular', font_size_regular, 'left', False)
                text = str(task['discount'])
                createStringContent(text, 'regular', font_size_regular, 'right')

        #Net Total
        if task['net_total'] is not None:
            text = template['net_total_text']
            createStringContent(text, 'regular', font_size_regular, 'left', False)
            text = str(task['net_total'])
            createStringContent(text, 'regular', font_size_regular, 'right')

        #Vat
        if task['vat'] is not None:
            text = template['vat_text']
            createStringContent(text, 'regular', font_size_regular, 'left', False)
            text = str(task['vat'])
            createStringContent(text, 'regular', font_size_regular, 'right')

        #Total Pay
        if task['total'] is not None:
            text = template['total_pay_text']
            createStringContent(text, 'bold', font_size_regular, 'left', False)
            text = str(task['total'])
            createStringContent(text, 'bold', font_size_regular, 'right')

        if float(task['receive']) > 0 or float(task['change']) > 0:
            #receive
            text = template['receive_text']
            createStringContent(text, 'regular', font_size_regular, 'left', False)
            text = str(task['receive'])
            createStringContent(text, 'regular', font_size_regular, 'right')

            #change
            text = template['change_text']
            createStringContent(text, 'regular', font_size_regular, 'left', False)
            text = str(task['change'])
            createStringContent(text, 'regular', font_size_regular, 'right')

        #Footer
        pdf.line(0, current_line, page_width, current_line)
        current_line = current_line - (0.2 * points)

        if task['is_real_bill'] == False:

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
            
            #Payment text
            text = template['payment_text']
            createStringCenterContent(text, 'regular')

        #Thank you
        text = template['footer_thank_you']
        createStringCenterContent(text, 'regular')

        text = 'คิว ' + str(task['order_queue'])
        createStringCenterContent(text, 'bold')

        #Save pdf
        pdf.save()

        return printPdf(self, config['file_name'], task['printer_name'])