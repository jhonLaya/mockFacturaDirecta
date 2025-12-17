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
        try:
            payload = request.body.decode("utf-8").strip()
            # Eliminar BOM si existe
            if payload.startswith('\ufeff'):
                payload = payload[1:]
            parsed_payload = parse(payload)
        except Exception as e:
            return HttpResponse(f"<error>Error parsing XML: {str(e)}</error>", 
                              content_type='application/xml', 
                              status=HTTPStatus.BAD_REQUEST)
        
        try:
            invoice = Clients.objects.create(invoice_payload = parsed_payload) 
            invoiceLines = parsed_payload["invoice"]["invoiceLines"]["invoiceLine"]
            print("########################################################")
            total_price = 0
            if type(invoiceLines) == list:
                for line in invoiceLines:
                    product_line = line["productCode"]
                    if product_line != None:
                        product_line = line["productCode"]
                    else:
                        product_line = ""
                    print(f"[+]{product_line} - {line["description"]} => {float(line["unitPrice"])}")
                    total_price += float(line["unitPrice"])
            else: 
                product_line = invoiceLines["productCode"]
                if product_line != None:
                    product_line = invoiceLines["productCode"]
                else:
                    product_line = ""
                print(f"[+]{invoiceLines["productCode"]} - {product_line} - {invoiceLines["description"]} => {invoiceLines["unitPrice"]}")
                total_price = invoiceLines["unitPrice"] 
            print(f"Total ==> {total_price}")
            print("########################################################")
            return HttpResponse(f"<invoice><id>{invoice.id}</id></invoice>",content_type='application/xml', status = HTTPStatus.CREATED)
        except Exception as e:
            return HttpResponse(f"<error>Error processing invoice: {str(e)}</error>", 
                              content_type='application/xml', 
                              status=HTTPStatus.INTERNAL_SERVER_ERROR)

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
                lines += f"<h2 style='color: #ff9800;'>[+] {line['productCode']} {line['description']} => <span style='color: red;'>{float(line['unitPrice'])} euros</span></h2>"
                total_price += float(line["unitPrice"])
        else: 
            product_line = invoiceLines["productCode"]
            if product_line != None:
                product_line = invoiceLines["productCode"]
            else:
                product_line = ""
            lines = f"<h2 style='color: #ff9800;'>[+] {invoiceLines['productCode']} - {invoiceLines['description']} => <span style='color: red;'>{invoiceLines['unitPrice']} euros</span></h2>"
            total_price = invoiceLines['unitPrice'] 
        lines += f"<h2 style='color: #85bb65;'>Total ==> <span style='color: red;'>{total_price} euros</span></h2>"

        html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Factura #{invoice_id}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #ff9800;
            padding-bottom: 10px;
        }}
        h2 {{
            margin: 15px 0;
            padding: 10px;
            border-left: 4px solid #ff9800;
            padding-left: 15px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Factura #{invoice_id}</h1>
        {lines}
    </div>
</body>
</html>"""

        return HttpResponse(html_content, content_type="text/html", status = HTTPStatus.OK)
    
