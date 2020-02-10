import sys
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdftypes import PDFObjRef, resolve1
from Provisioning2.IAS import IAS

filename = sys.argv[1]
fp = open(filename, 'rb')
EDIPI = ""
LNAME = ""
FNAME = ""
parser = PDFParser(fp)
doc = PDFDocument(parser)
fields = resolve1(doc.catalog['AcroForm'])['Fields']
for i in fields:
    field = resolve1(i)
    name, value = field.get('T'), field.get('V')
    if isinstance(value, PDFObjRef):
        # value = resolve1(value)
        value = (field.get('T').decode('utf-8'), resolve1(field.get('V')))
        if name == b"User Signature":
            EDIPI = ((value[1]['Name'].decode("utf-8").split('.'))[-1])
            LNAME = ((value[1]['Name'].decode("utf-8").split('.'))[0])
            FNAME = ((value[1]['Name'].decode("utf-8").split('.'))[1])
    # print ('{0}: {1}'.format(name, value))

url = "https://cacpt.csd.disa.mil:443/ECRSWebServices/uas?wsdl"
pkey = 'C:\Pentaho\projects\DHA_Provisioning\certs\keyfile-decrypted.key'
cert = 'C:\Pentaho\projects\DHA_Provisioning\certs\certfile.crt'
UID = IAS(url, pkey, cert)
x = UID.getUIDEmail(EDIPI)
print(LNAME, FNAME,x)
