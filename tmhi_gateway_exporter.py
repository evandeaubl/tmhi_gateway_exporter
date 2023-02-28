import requests

from time import sleep
from random import randint

from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY

class ArcadyanCollector:
    def collect(self):
        metrics_url = 'http://192.168.12.1/TMI/v1/gateway?get=all'
        response = requests.get(metrics_url)
        json = response.json()

        rsrp = GaugeMetricFamily('gateway_rsrp', 'RSRP', labels=['nbid', 'cid', 'band'])
        rsrq = GaugeMetricFamily('gateway_rsrq', 'RSRQ', labels=['nbid', 'cid', 'band'])
        rssi = GaugeMetricFamily('gateway_rssi', 'RSSI', labels=['nbid', 'cid', 'band'])
        sinr = GaugeMetricFamily('gateway_sinr', 'SINR', labels=['nbid', 'cid', 'band'])

        json_to_metric = {
            'rsrp': rsrp,
            'rsrq': rsrq,
            'rssi': rssi,
            'sinr': sinr
        }
        nbid = str(json['signal']['4g']['eNBID'])
        cid = str(json['signal']['4g']['cid'])
        for band in json['signal']['4g']['bands']:
            for key, metric in json_to_metric.items():
                metric.add_metric([nbid, cid, band], json['signal']['4g'][key])

        # 5g values are never populated? Assume same as 4g and use those
        #nbid = json['signal']['5g']['eNBID']
        #cid = json['signal']['5g']['cid']
        nbid = str(json['signal']['4g']['eNBID'])
        cid = str(json['signal']['4g']['cid'])
        for band in json['signal']['5g']['bands']:
            for key, metric in json_to_metric.items():
                metric.add_metric([nbid, cid, band], json['signal']['5g'][key])
        yield rsrp
        yield rsrq
        yield rssi
        yield sinr

def main():
    REGISTRY.register(ArcadyanCollector())

    start_http_server(9715)
    while True:
        sleep(1.0)

if __name__ == '__main__':
    main()
