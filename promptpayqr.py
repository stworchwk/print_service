# -*- coding: utf-8 -*-
import qrcode
import libscrc

def qr_code(account, money=""):

    account.replace("000201010211", "000201010212") # change to Onetime

    account = account.split('TH', 1)[0] + 'TH'

    currency = "5303" + "764"  # "764"  คือเงินบาทไทย ตาม https://en.wikipedia.org/wiki/ISO_4217
    if money != "":  # กรณีกำหนดเงิน
        check_money = money.split('.')  # แยกจาก .
        if len(check_money) == 1 or len(check_money[1]) == 1:  # กรณีที่ไม่มี . หรือ มีทศนิยมแค่หลักเดียว
            money = "54" + "0" + str(len(str(float(money))) + 1) + str(float(money)) + "0"
        else:
            money = "54" + "0" + str(len(str(float(money)))) + str(float(money))  # กรณีที่มีทศนิยมครบ

    check_sum = account + currency + money + "6304"
    check_sum1=hex(libscrc.xmodem(check_sum.encode("ascii"),0xffff)).replace('0x','')
    if len(check_sum1)<4: # # แก้ไขข้อมูล check_sum ไม่ครบ 4 หลัก
        check_sum1=("0"*(4-len(check_sum1)))+check_sum1
    check_sum+=check_sum1
    # if path_qr_code != "":
    img = qrcode.make(check_sum.upper(), border=0)
    # imgload = open(path_qr_code,'wb')
    img.save('promptpayqrcode.jpg', 'JPEG')
    # imgload.close()
    return True
    # else:
    #    return check_sum.upper() # upper ใช้คืนค่าสตริงเป็นตัวพิมพ์ใหญ่
