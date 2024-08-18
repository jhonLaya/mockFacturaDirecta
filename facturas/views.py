from django.shortcuts import render
from django.http.response import HttpResponse
from http import HTTPStatus
from django.views.decorators.csrf import csrf_exempt
from xmltodict import parse

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
        invoiceLines = parsed_payload["invoice"]["invoiceLines"]["invoiceLine"]
        print("########################################################")
        total_price = 0
        if type(invoiceLines) == list:
            for line in invoiceLines:
                print(f"[+]{line["description"]} => {float(line["unitPrice"])}")
                total_price += float(line["unitPrice"])
        else: 
            print(f"[+]{invoiceLines["description"]} => {invoiceLines["unitPrice"]}")
            total_price = invoiceLines["unitPrice"] 
        print(f"Total ==> {total_price}")
        print("########################################################")
        return HttpResponse("<invoice><id>80</id></invoice>",content_type='application/xml', status = HTTPStatus.CREATED)

def get_pdf(request):
    if request.method == "GET":
        return HttpResponse("Factura Creada Satisfactoriamente", status = HTTPStatus.CREATED)
    
