# encoding: utf-8
from facturacion_moderna import facturacion_moderna

def prueba_cancelacion(debug = False):
  
  # RFC utilizado para el ambiente de pruebas
  rfc_emisor = "ESI920427886"
  
  # Datos de acceso al ambiente de pruebas
  url_timbrado = "https://t1demo.facturacionmoderna.com/timbrado/wsdl"
  user_id = "UsuarioPruebasWS";
  user_password = "b9ec2afa3361a59af4b4d102d3f704eabdf097d4"

  params = {'emisorRFC': rfc_emisor, 'UserID': user_id, 'UserPass': user_password}
  cliente = facturacion_moderna.Cliente(url_timbrado, params, debug)

  # UUID del comprobante a cancelar
  uuid = '14D50991-54D9-4F1C-9B49-CA2DE1F60190'

  if cliente.cancelar(uuid):
    print 'Cancelación exitosa'
  else:
    print "[%s] - %s" % (cliente.codigo_error, cliente.error)

if __name__ == '__main__':
  prueba_cancelacion()
