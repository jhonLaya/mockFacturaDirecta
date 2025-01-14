from django.shortcuts import render
from django.http.response import HttpResponse
from http import HTTPStatus
from django.views.decorators.csrf import csrf_exempt
from xmltodict import parse
from .models import Clients

@csrf_exempt
def get_client_info(request):
    if request.method == "GET":
        return HttpResponse("<clients><client><id>80</id><legalType><![CDATA[J]]></legalType><name><![CDATA[Nombre Cliente]]></name><taxCode><![CDATA[NIF o Código fiscal]]></taxCode><tradeName><![CDATA[Nombre comercial]]></tradeName><noEInvoice>false</noEInvoice><address><line1><![CDATA[primera linea de dirección]]></line1><line2><![CDATA[segunda linea de dirección]]></line2><city><![CDATA[Vic]]></city><province><![CDATA[Barcelona]]></province><zipcode><![CDATA[08500]]></zipcode><country><![CDATA[ES]]></country></address><website>www.facturadirecta.com</website><language>es</language><email>email@facturadirecta.com</email><phone><![CDATA[555020202]]></phone><mobilePhone></mobilePhone><notes><![CDATA[Notas para esta empresa]]></notes><companyCode><![CDATA[Código empresa 1]]></companyCode><billing><currency>EUR</currency><tax1><name>IVA</name><rate>18.00</rate></tax1><tax2><name>IRPF</name><rate>-15.00</rate></tax2><bank><country>ES</country><name><![CDATA[La Caixa]]></name><accountNumber><![CDATA[ES6121002100300000000000]]></accountNumber><swift><![CDATA[CAIXESBBXXX]]></swift></bank><paymentMean>02</paymentMean><payableDayInMonth1>7</payableDayInMonth1><payableDayInMonth2>27</payableDayInMonth2><dueDates><dueDate><delayInDays>30</delayInDays><rate>50.00</rate></dueDate><dueDate><delayInDays>60</delayInDays><rate>50.00</rate></dueDate></dueDates><customInvoiceNotes>true</customInvoiceNotes><invoiceNotes><![CDATA[Notas de factura personalizadas para este cliente]]></invoiceNotes></billing></client></clients>", content_type='application/xml')

@csrf_exempt
def create_charge(request):
    if request.method == "POST":
        payload = request.body.decode("utf-8")
        clean_payload = payload.replace("\n", "", 1).replace(" ", "", 4)
        parsed_payload = parse(clean_payload)
        invoice = Clients.objects.create(invoice_payload = parsed_payload) 
        invoiceLines = parsed_payload["invoice"]["invoiceLines"]["invoiceLine"]
        # print("########################################################")
        total_price = 0
        if type(invoiceLines) == list:
            for line in invoiceLines:
                product_line = line["productCode"]
                if product_line != None:
                    product_line = line["productCode"]
                else:
                    product_line = ""
                # print(f"[+]{product_line} - {line["description"]} => {float(line["unitPrice"])}")
                total_price += float(line["unitPrice"])
        else: 
            product_line = invoiceLines["productCode"]
            if product_line != None:
                product_line = invoiceLines["productCode"]
            else:
                product_line = ""
            print(f"[+]{invoiceLines["productCode"]} - {product_line} - {invoiceLines["description"]} => {invoiceLines["unitPrice"]}")
            total_price = invoiceLines["unitPrice"] 
        # print(f"Total ==> {total_price}")
        # print("########################################################")
        return HttpResponse(f"<invoice><id>{invoice.id}</id></invoice>",content_type='application/xml', status = HTTPStatus.CREATED)

def get_pdf(request, invoice_id):
    if request.method == "GET":
        invoice = Clients.objects.get(id = invoice_id)
        invoice_payload = invoice.invoice_payload
        invoiceLines = invoice_payload["invoice"]["invoiceLines"]["invoiceLine"]
        total_price = 0
        lines = ""
        if type(invoiceLines) == list:
            for line in invoiceLines:
                product_line = line["productCode"]
                if product_line != None:
                    product_line = line["productCode"]
                else:
                    product_line = ""
                lines += f"<h2 style='color: #ff9800;'>[+] {line["productCode"]} {line['description']} => <span style='color: red;'>{float(line['unitPrice'])} euros</span> \n </h2>"
                total_price += float(line["unitPrice"])
        else: 
            product_line = invoiceLines["productCode"]
            if product_line != None:
                product_line = invoiceLines["productCode"]
            else:
                product_line = ""
            lines = f"<h2 style='color: #ff9800;'>[+] {invoiceLines["productCode"]} - {invoiceLines['description']} => <span style='color: red;'>{invoiceLines['unitPrice']} euros</span>\n</h2>"
            total_price = invoiceLines['unitPrice'] 
        lines += f"<h2 style='color: #85bb65;'>Total ==> <span style='color: red;'>{total_price} euros</span> </h2>"

        return HttpResponse(lines, content_type="text/html", status = HTTPStatus.OK)
    
