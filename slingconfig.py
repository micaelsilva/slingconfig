import os
from hashlib import md5
from time import time
from xml.dom.minidom import parseString

import requests
from dotenv import load_dotenv


class Sling:
    def __init__(self, ip, user, password, finderid):
        self.s = requests.Session()
        self.s.timeout = 5
        self.s.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/39.0.2171.36 Safari/537.36"
            })
        self.ip = ip
        self.user = user
        self.password = password
        self.finderid = finderid
        self.counter = 1
        self.xlink = ""
        self.time = ""
        self.links = {}

    @staticmethod
    def _request_endpoint(obj):
        try:
            request_ = obj
        except requests.exceptions.ConnectTimeout as a:
            print(f"Connection timed out: {a}")
        except Exception as a:
            print(a)
        else:
            return request_

    def _digest(self, time):
        return md5(
            f'{self.user}:{self.xlink}:{time}:{self.counter}:{self.password}'
            .encode("ascii")).hexdigest()

    def _list(self):
        epoch = int(time())
        r = self._request_endpoint(
            self.s.post(
                f"http://{self.ip}/slingbox",
                data='<client xmlns="http://www.slingbox.com">'
                     f'<description>FinderID-{self.finderid}</description>'
                     '<client_capabilities><usb_mymedia_support>true'
                     '</usb_mymedia_support>'
                     '</client_capabilities></client>',
                params={
                    "forceOkStatus": "",
                    "account": self.user,
                    "counter": self.counter,
                    "cnonce": str(epoch),
                    "digest": self._digest(epoch)
                }))
        dom1 = parseString(r.text)
        self.xlink = dom1.getElementsByTagName("session")[0].attributes.get("xlink:href").value
        for i in dom1.getElementsByTagName("session")[0].childNodes:
            if i.nodeName != "#text":
                self.links.update(
                    {i.nodeName: i.attributes.get("xlink:href").value})

    def _device(self):
        epoch = int(time())
        r = requests.get(
            f"http://{self.ip}/slingbox{self.links['device']}",
            params={
                "forceOkStatus": "",
                "account": self.user,
                "counter": self.counter,
                "cnonce": str(epoch),
                "digest": self._digest(epoch)
            })
        print(r.text)


if __name__ == '__main__':
    load_dotenv('credentials')
    IP = os.getenv('IP')
    USER = os.getenv('USER')
    PASSWORD = os.getenv('PASSWORD')
    FINDERID = os.getenv('FINDERID')

    e = Sling(
        ip=IP,
        user=USER,
        password=PASSWORD,
        finderid=FINDERID)
    e._list()
    e._device()
