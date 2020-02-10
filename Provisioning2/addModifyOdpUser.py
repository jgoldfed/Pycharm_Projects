import json
import logging
import pprint
from datetime import datetime
from suds.client import Client
from suds.sudsobject import asdict
from suds.transport.http import HttpAuthenticated


# logging.basicConfig(level=logging.INFO)
# logging.getLogger('suds.client').setLevel(logging.DEBUG)


def recursive_asdict(d: str) -> list:
    """Convert Suds object into serializable format."""
    out = {}
    for k, v in asdict(d).items():
        if hasattr(v, '__keylist__'):
            out[k] = recursive_asdict(v)
        elif isinstance(v, list):
            out[k] = []
            for item in v:
                if hasattr(item, '__keylist__'):
                    out[k].append(recursive_asdict(item))
                else:
                    out[k].append(item)
        elif isinstance(v, datetime):
            out[k] = v.strftime('%Y-%m-%dT%H:%M:%S (%Z)')
        else:
            out[k] = v
    return out


def suds_to_json(data: str) -> json:
    return json.dumps(recursive_asdict(data))


credentials = dict(username="EktropySupport@netimpactstrategies.com", password="clarity1234")
t = HttpAuthenticated(**credentials)

url = "https://ondemand.ca.com/tunnel-web/secure/axis/Portlet_Odp_OdpUserService?wsdl"
email = " 6718618380434@example.com"
authenticationHeader = {"SOAPAction": "POST", "encoded": "true",
                        "encodingStyle": "http://schemas.xmlsoap.org/soap/encoding/", "Content-Type": "text/xml"}

client = Client(url=url, headers=authenticationHeader,
                location="https://ondemand.ca.com/tunnel-web/secure/axis/Portlet_Odp_OdpUserService", transport=t)

opt = client.factory.create('ns0:OdumOptions')

user = client.factory.create('ns0:User')

optitemstodelete = ['additiveAppInstList',
                    'defaultPassword',
                    'forcePasswordReset']

useritemstodelete = ('userId'
                     , 'additionalEmailAddresses'
                     , 'addresses'
                     , 'clarityAppDetails'
                     , 'greeting'
                     , 'jobTitle'
                     , 'middleName'
                     , 'modifiedDate'
                     , 'phones'
                     , 'prefix'
                     , 'serviceDeskDetails'
                     , 'suffix')

for i in optitemstodelete:
    delattr(opt, i)

for i in useritemstodelete:
    delattr(user, i)


opt.sendWelcomeEmail = 'false'
opt.defaultTenantName = "DOD Healthcare"

user.emailAddress = "6718618380434@example.com"

user.active = "true"
user.firstName = "Katherine"
user.lastName = "Boufford"
user.languageId = "en_US"
user.lockout = "false"
user.timezone = "UTC"
user.appInstances.item = ["Sandbox"]
try:
    response = (client.service.addModifyOdpUser(opt, user, ))
except Exception as e:
    print(str(e))
    print(client.last_sent())
response = (client.service.addModifyOdpUser(opt, user))

strjson_response = suds_to_json(response)

json_response = json.loads(strjson_response)
print("Modified userId: {} with email: {}\n".format(json_response['userId'], json_response['emailAddress']))

print( json_response )