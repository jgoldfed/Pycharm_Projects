import csv

from Provisioning.IAS import IAS

inputFile = 'C:/Users/JarrettGoldfedder/Documents/Jarrett/Testing/sample.csv'
outputFile = 'C:/Users/JarrettGoldfedder/Documents/Jarrett/Testing/sample_UID.csv'
url = "https://cacpt.csd.disa.mil:443/ECRSWebServices/uas?wsdl"
pkey = 'C:\Pentaho\projects\DHA_Provisioning\certs\keyfile-decrypted.key'
cert = 'C:\Pentaho\projects\DHA_Provisioning\certs\certfile.crt'
UID = IAS(url, pkey, cert)

with open(inputFile) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=",")
    line_count = 0
    with open(outputFile, mode='w', newline='\n',
              encoding='utf-8') as output_file:
        output_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in csv_reader:
            if line_count == 0:
                print("{}, {}, {}, UID".format(row[0], row[1], row[2]))
                output_writer.writerow([row[0], row[1], row[2], 'UID'])
                line_count += 1
            else:
                iasID = UID.getUID(row[0])
                print("{}, {}, {}, {}".format(row[0], row[1], row[2], iasID))
                output_writer.writerow([row[0], row[1], row[2], "{}@example.com".format(iasID)])
                line_count += 1
print('Output saved to C:\\Users\\JarrettGoldfedder\\Documents\\Jarrett\\Testing\\sample_UID.csv' )
