# IAS function gets us the UID from an input EDIPI
# Thoughtfully reproduced from https://stackoverflow.com/questions/6277027/suds-over-https-with-cert
# Deprecation with HTTPLIB connection means that we needed to access https://www.programcreek.com/python/example/72757/ssl.SSLContext
import json
import ssl
import sys
from suds.client import Client
from suds.transport.http import HttpTransport, Reply, TransportError
from suds.sudsobject import asdict
import http.client as httplib, socket, urllib.request as urllib2


class HTTPSClientAuthHandler(urllib2.HTTPSHandler):
    def __init__(self, key, cert):
        urllib2.HTTPSHandler.__init__(self)
        self.key = key
        self.cert = cert

    def https_open(self, req):
        # Rather than pass in a reference to a connection class, we pass in
        # a reference to a function which, for all intents and purposes,
        # will behave as a constructor
        return self.do_open(self.getConnection, req)

    def getConnection(self, host, timeout=300):
        return httplib.HTTPSConnection(host, context=self.load_ssl_context(cert_file=self.cert, pkey_file=self.key))

    def load_ssl_context(self, cert_file, pkey_file=None, protocol=None):
        """Loads SSL context from cert/private key files and optional protocol.
        Many parameters are directly taken from the API of
        :py:class:`ssl.SSLContext`.

        :param cert_file: Path of the certificate to use.
        :param pkey_file: Path of the private key to use. If not given, the key
                          will be obtained from the certificate file.
        :param protocol: One of the ``PROTOCOL_*`` constants in the stdlib ``ssl``
                         module. Defaults to ``PROTOCOL_SSLv23``.
        """
        if protocol is None:
            protocol = ssl.PROTOCOL_SSLv23
        ctx = ssl.SSLContext(protocol)
        ctx.load_cert_chain(cert_file, pkey_file)
        return ctx


class HTTPSClientCertTransport(HttpTransport):
    def __init__(self, key, cert, *args, **kwargs):
        HttpTransport.__init__(self, **kwargs)
        self.key = key
        self.cert = cert

    def u2open(self, u2request):
        """
        Open a connection.
        @param u2request: A urllib2 request.
        @type u2request: urllib2.Requet.
        @return: The opened file-like urllib2 object.
        @rtype: fp
        """
        tm = self.options.timeout
        url = urllib2.build_opener(HTTPSClientAuthHandler(self.key, self.cert))
        if self.u2ver() < 2.6:
            socket.setdefaulttimeout(tm)
            return url.open(u2request)
        else:
            return url.open(u2request, timeout=tm)


class IAS:
    """
    A class used to represent the IAS instance.
    To initialize, pass in a WSDL,
     private (decrypted) key, and certificate
     """

    def __init__(self, url: str, pkey: str = None, cert: str = None) -> Client:
        """
        Parameters
        -----------
        :param url: str
            The WSDL URL
        :param pkey: str
            The private (decrypted) key
        :param cert: str
            The public certificate
        """
        self.client = Client(url, transport=HTTPSClientCertTransport(pkey, cert))

    def recursive_asdict(self, d: str) -> list:
        """Convert Suds object into serializable format."""
        out = {}
        for k, v in asdict(d).items():
            if hasattr(v, '__keylist__'):
                out[k] = self.recursive_asdict(v)
            elif isinstance(v, list):
                out[k] = []
                for item in v:
                    if hasattr(item, '__keylist__'):
                        out[k].append(self.recursive_asdict(item))
                    else:
                        out[k].append(item)
            else:
                out[k] = v
        return out

    def suds_to_json(self, data: str) -> json:
        return json.dumps(self.recursive_asdict(data))

    def getUID(self, edipi: str = "NONE") -> str:
        """Gets the UID based on the delivered EID

        Parameters
        ------------
        :param edipi: str
            The string EDI PI value. Defaults to NONE.
        """
        if edipi == "NONE":
            print('Syntax: IAS.py <<EDIPI>>')
            sys.exit(1)  # abort because of error
        return self.generateID(edipi, 'E')

    def getEID(self, uid: str = "NONE") -> str:
        """Gets the EID based on the delivered UID

        Parameters
        ------------
        :param uid: str
            The string Unique IAS value. Defaults to NONE.
        """
        if uid == "NONE":
            print('Syntax: IAS.py <<UID>>')
            sys.exit(1)  # abort because of error
        return self.generateID(uid, 'U')

    def generateID(self, idValue: str, idType: str = 'E') -> str:
        """Utility function to call the getIASID web service

        Parameters
        ------------
        :param idValue: str
            The ID value
        :param idType: str
            Either 'E' for 'EID' (default) or 'U' for 'UID'
        """
        if idType == 'E':
            returnIdType = 'U'
        else:
            returnIdType = 'E'

        dictVal = dict(id=idValue, idType=idType, returnIdType=returnIdType)

        response = (self.client.service.getIASID(**dictVal))
        strjson_response = self.suds_to_json(response)

        json_response = json.loads(strjson_response)
        self.id = json_response["iasId"]['id']
        if (self.id == 'noaccount'):
            return ('IAS Id not found')
        else:
            return self.id
            # print('{}@example.com'.format(UID))

    def getUIDEmail(self,key):
        x=self.getUID(key)
        return '{}@example.com'.format(x)

if (__name__ == '__main__'):
    #if len(sys.argv) < 2:
    #    print('Syntax: IAS.py <<EDIPI>>')
    #    sys.exit(1)  # abort because of error
    url = "https://cacpt.csd.disa.mil:443/ECRSWebServices/uas?wsdl"
    pkey = 'C:\Pentaho\projects\DHA_Provisioning\certs\keyfile-decrypted.key'
    cert = 'C:\Pentaho\projects\DHA_Provisioning\certs\certfile.crt'
    UID = IAS(url, pkey, cert)
    x = UID.getUIDEmail("1510135616")
    print(x)
