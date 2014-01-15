# encoding: utf-8
from facturacion_moderna import facturacion_moderna
from datetime import datetime
import base64
from M2Crypto import RSA
from lxml import etree as ET
import sha
import os

def prueba_timbrado(debug = False):
  
  # RFC utilizado para el ambiente de pruebas
  rfc_emisor = "ESI920427886"
  
  # Datos de acceso al ambiente de pruebas
  url_timbrado = "https://t1demo.facturacionmoderna.com/timbrado/wsdl"
  user_id = "UsuarioPruebasWS";
  user_password = "b9ec2afa3361a59af4b4d102d3f704eabdf097d4"

  cfdi = genera_layout(rfc_emisor)

  params = {'emisorRFC': rfc_emisor, 'UserID': user_id, 'UserPass': user_password}
  options = {'generarCBB': True, 'generarPDF': True, 'generarTXT': True}
  cliente = facturacion_moderna.Cliente(url_timbrado, params, debug)

  if cliente.timbrar(cfdi, options):
    folder = 'comprobantes'
    if not os.path.exists(folder): os.makedirs(folder)
    comprobante = os.path.join(folder, cliente.uuid)
    for extension in ['xml', 'pdf', 'png', 'txt']:
      if hasattr(cliente, extension):
        with open(("%s.%s" % (comprobante, extension)), 'wb' if extension in ['pdf','png'] else 'w') as f: f.write(getattr(cliente, extension))
        print("%s almacenado correctamente en %s.%s" % (extension.upper(), comprobante, extension))
    print 'Timbrado exitoso'
  else:
    print("[%s] - %s" % (cliente.codigo_error, cliente.error))

def genera_layout(rfc_emisor):
  # se calcula la fecha de emisión en formato ISO 8601
  fecha_actual = datetime.now().isoformat()
  
  cfdi = """[Encabezado]

serie|
fecha|{fecha_actual}
folio|
tipoDeComprobante|ingreso
formaDePago|PAGO EN UNA SOLA EXHIBICIÓN
metodoDePago|Transferencía Electrónica
condicionesDePago|Contado
NumCtaPago|No identificado
subTotal|10.00
descuento|0.00
total|11.60
Moneda|MXN
noCertificado|
LugarExpedicion|Nuevo León, México.

[Datos Adicionales]

tipoDocumento|Factura
observaciones|

[Emisor]

rfc|{rfc_emisor}
nombre|EMPRESA DE MUESTRA S.A de C.V.
RegimenFiscal|REGIMEN GENERAL DE LEY

[DomicilioFiscal]

calle|Calle 
noExterior|Número Ext.
noInterior|Número Int.
colonia|Colonia
localidad|Localidad
municipio|Municipio
estado|Nuevo León
pais|México
codigoPostal|66260

[ExpedidoEn]
calle|Calle sucursal
noExterior|
noInterior|
colonia|
localidad|
municipio|Nuevo León
estado|Nuevo León
pais|México
codigoPostal|77000

[Receptor]
rfc|XAXX010101000
nombre|PÚBLICO EN GENERAL

[Domicilio]
calle|Calle
noExterior|Num. Ext
noInterior|
colonia|Colonia
localidad|San Pedro Garza García
municipio|
estado|Nuevo León
pais|México
codigoPostal|66260

[DatosAdicionales]

noCliente|09871
email|edgar.duran@facturacionmoderna.com

[Concepto]

cantidad|1
unidad|No aplica
noIdentificacion|
descripcion|Servicio Profesional
valorUnitario|10.00
importe|10.00


[ImpuestoTrasladado]

impuesto|IVA
importe|1.60
tasa|16.00
""".format(**locals())
  return cfdi;

if __name__ == '__main__':
  prueba_timbrado()
