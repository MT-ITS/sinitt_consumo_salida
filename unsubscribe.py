import requests

request_body = {
  'name': 'prueba',
  # Usuario del SINITT que se solicita al Ministerio de Transporte
  'clientId': 'XXXX',
  # Id de la subscripción a la cual se va conectar
  'catalogueContentId': '19',
  # hasta cuando se conecta
  'subscriptionEnd' : '31/10/2024 23:59:59',
  #'clientEndpoint': 'http://172.16.100.79:8000',
  'clientEndpoint': 'http://172.23.120.111:9500',
  'useCompression': False,
  'securityParameters': ""
}

# este campo es dado como respuesta de la subscripción efectada al SINITT.
subscription_id = 97
url = "https://datex2-sinitt.mintransporte.gov.co/v3.1/subscription/destroy/{subscription_id}".format(subscription_id=subscription_id)
response = requests.put(url, json=request_body)
response.content
