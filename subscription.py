import requests
import json

request_body = {
  'name': 'prueba',
  # Usuario del SINITT, se debe solicitar al Ministerio de Transporte
  'clientId': 'XXXXX',
  # Id de la subscripción a la cual se va conectar, se obtiene utilizando el método catalog_content del SINITT
  'catalogueContentId': '19',
  # define la fecha y la hora hasta cuando se desea recibir información.
  'subscriptionEnd' : '31/10/2024 23:59:59',
  # dirección pública y puerto que se dispuso para recibir la información entregada desde el SINITT
  'clientEndpoint': 'http://172.23.120.111:9500',
  'useCompression': False,
  'securityParameters': ""
}

response = requests.post("https://datex2-sinitt.mintransporte.gov.co/v3.1/subscription/subscribe/", json=request_body)
# esto muestra el ID de la subscripción que se estableció.
print(response.content)
