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

;Version=3.3
Serie=A
Folio=asignarFolio
Fecha={fecha_actual}
FormaPago=99
NoCertificado=20001000000300022762
CondicionesDePago=CONTADO
SubTotal=100.00
Descuento=00.00
Moneda=MXN
;TipoCambio=
Total=100.00
TipoDeComprobante=I
MetodoPago=PUE
LugarExpedicion=68050

[DatosAdicionales]
tipoDocumento=FACTURA

[Emisor]
Rfc={rfc_emisor}
Nombre=FACTURACION MODERNA SA DE CV
RegimenFiscal=601

[Receptor]
Rfc=XAXX010101000
Nombre=LUIS HERNANDEZ FELIX
UsoCFDI=G01


[Concepto#1]
ClaveProdServ=01010101
NoIdentificacion=
Cantidad=10
ClaveUnidad=KGM
Unidad=Kilogramos
Descripcion=AZUCAR
ValorUnitario=10.00
Importe=100.00
Descuento=00.00


Impuestos.Traslados.Base=[100.00]
Impuestos.Traslados.Impuesto=[002]
Impuestos.Traslados.TipoFactor=[Tasa]
Impuestos.Traslados.TasaOCuota=[0.160000]
Impuestos.Traslados.Importe=[16.00]

Impuestos.Retenciones.Base=[100.00]
Impuestos.Retenciones.Impuesto=[001]
Impuestos.Retenciones.TipoFactor=[Tasa]
Impuestos.Retenciones.TasaOCuota=[0.35]
Impuestos.Retenciones.Importe=[35.00]



[Traslado#1]
Impuesto = 002
TipoFactor = Tasa
TasaOCuota = 0.160000
Importe = 16.00

[Retencion#1]
Impuesto=001
Importe=15.99
""".format(**locals())
  return cfdi;

if __name__ == '__main__':
  prueba_timbrado()
