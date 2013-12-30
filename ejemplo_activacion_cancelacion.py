# encoding: utf-8
from facturacion_moderna import facturacion_moderna

def prueba_activacion(debug = False):
  
  # RFC utilizado para el ambiente de pruebas
  rfc_emisor = "ESI920427886"
  
  # Datos de acceso al ambiente de pruebas
  url_timbrado = "https://t1demo.facturacionmoderna.com/timbrado/wsdl"
  user_id = "UsuarioPruebasWS";
  user_password = "b9ec2afa3361a59af4b4d102d3f704eabdf097d4"

  params = {'emisorRFC': rfc_emisor, 'UserID': user_id, 'UserPass': user_password}
  cliente = facturacion_moderna.Cliente(url_timbrado, params, debug)

  #Cambiar las variables de acuerdo a los archivos y pass del CSD que se desea activar
  archCer = 'utilerias/certificados/20001000000200000192.cer';
  archKey = 'utilerias/certificados/20001000000200000192.key';
  passKey = '12345678a';

  #invocando servicio
  if cliente.activarCancelacion(archCer,archKey,passKey):
    print 'Activacion de Cancelación exitosa'
  else:
    print "[%s] - %s" % (cliente.codigo_error, cliente.error)

if __name__ == '__main__':
  prueba_activacion()
