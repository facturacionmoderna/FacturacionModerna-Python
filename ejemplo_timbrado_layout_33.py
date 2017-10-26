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
  rfc_emisor = "TCM970625MB1"
  
  # Datos de acceso al ambiente de pruebas
  url_timbrado = "https://t1demo.facturacionmoderna.com/timbrado/wsdl"
  user_id = "UsuarioPruebasWS";
  user_password = "b9ec2afa3361a59af4b4d102d3f704eabdf097d4"

  cfdi = genera_layout(rfc_emisor)

  params = {'emisorRFC': rfc_emisor, 'UserID': user_id, 'UserPass': user_password}
  options = {'generarCBB': False, 'generarPDF': True, 'generarTXT': False}
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
  fecha_actual = datetime.now().isoformat()[0:19]
  
  cfdi = """[ComprobanteFiscalDigital]

Version=3.3
Serie=A
Folio=02
Fecha={fecha_actual}
FormaPago=03
NoCertificado=20001000000200000192
CondicionesDePago=CONTADO
SubTotal=1850
Descuento=175.00
Moneda=MXN
Total=1943.00
TipoDeComprobante=I
MetodoPago=PUE
LugarExpedicion=68050

[DatosAdicionales]
tipoDocumento=FACTURA
observaciones=Observaciones al documento versión 3.3
plantillaPDF=clasic
logotipo= lg_fdc9422f0756154cd565695

[Emisor]
Rfc=ESI920427886
Nombre=FACTURACION MODERNA SA DE CV
RegimenFiscal=601

[Receptor]
Rfc=XAXX010101000
Nombre=PUBLICO EN GENERAL
UsoCFDI=G01


[Concepto#1]
ClaveProdServ=01010101
NoIdentificacion=AULOG001
Cantidad=5
ClaveUnidad=H87
Unidad=Pieza
Descripcion=Aurriculares USB Logitech
ValorUnitario=350.00
Importe=1750.00
Descuento=175.00

Impuestos.Traslados.Base=[1575.00]
Impuestos.Traslados.Impuesto=[002]
Impuestos.Traslados.TipoFactor=[Tasa]
Impuestos.Traslados.TasaOCuota=[0.160000]
Impuestos.Traslados.Importe=[252.00]

[Concepto#2]
ClaveProdServ=43201800
NoIdentificacion=USB
Cantidad=1
ClaveUnidad=H87
Unidad=Pieza
Descripcion=Memoria USB 32gb marca Kingston
ValorUnitario=100.00
Importe=100.00

Impuestos.Traslados.Base=[100.00]
Impuestos.Traslados.Impuesto=[002]
Impuestos.Traslados.TipoFactor=[Tasa]
Impuestos.Traslados.TasaOCuota=[0.160000]
Impuestos.Traslados.Importe=[16.00]

[Traslados]
TotalImpuestosTrasladados=268.00
Impuesto=[002]
TipoFactor=[Tasa]
TasaOCuota=[0.160000]
Importe=[268.00]

""".format(**locals())
  return cfdi;

if __name__ == '__main__':
  prueba_timbrado()
