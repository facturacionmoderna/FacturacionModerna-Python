# encoding: utf-8
from facturacion_moderna import facturacion_moderna
from datetime import datetime
import base64
from M2Crypto import RSA
from lxml import etree as ET
import hashlib
import os

def prueba_timbrado(debug = False):
  
  # RFC utilizado para el ambiente de pruebas
  rfc_emisor = "ESI920427886"
  
  # Archivos del CSD de prueba proporcionados por el SAT.
  # ver http://developers.facturacionmoderna.com/webroot/CertificadosDemo-FacturacionModerna.zip
  numero_certificado = "20001000000200000192"
  archivo_cer = "utilerias/certificados/20001000000200000192.cer"
  archivo_pem = "utilerias/certificados/20001000000200000192.key.pem"
  
  # Datos de acceso al ambiente de pruebas
  url_timbrado = "https://t1demo.facturacionmoderna.com/timbrado/wsdl"
  user_id = "UsuarioPruebasWS"
  user_password = "b9ec2afa3361a59af4b4d102d3f704eabdf097d4"

  cfdi = genera_xml(rfc_emisor)
  cfdi = sella_xml(cfdi, numero_certificado, archivo_cer, archivo_pem)

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


def sella_xml(cfdi, numero_certificado, archivo_cer, archivo_pem):
  keys = RSA.load_key(archivo_pem)
  cert_file = open(archivo_cer, 'r')
  cert = base64.b64encode(cert_file.read())
  xdoc = ET.fromstring(cfdi)

  comp = xdoc.get('Comprobante')
  xdoc.attrib['Certificado'] = cert
  xdoc.attrib['NoCertificado'] = numero_certificado

  xsl_root = ET.parse('utilerias/xslt33/cadenaoriginal_3_3.xslt')
  xsl = ET.XSLT(xsl_root)
  cadena_original = xsl(xdoc)
  digest = hashlib.new('sha256', str(cadena_original)).digest()
  sello = base64.b64encode(keys.sign(digest, "sha256"))

  comp = xdoc.get('Comprobante')
  xdoc.attrib['Sello'] = sello
  
  print ET.tostring(xdoc)
  return ET.tostring(xdoc)

def genera_xml(rfc_emisor):
  # se calcula la fecha de emisión en formato ISO 8601
  fecha_actual = str(datetime.now().isoformat())[:19]
  
  cfdi = """<?xml version="1.0" encoding="UTF-8"?>
<cfdi:Comprobante xmlns:cfdi="http://www.sat.gob.mx/cfd/3" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sat.gob.mx/cfd/3 http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv33.xsd" Version="3.3" Serie="A" Folio="01" Fecha="{fecha_actual}" Sello="" FormaPago="03" NoCertificado="" Certificado="" CondicionesDePago="CONTADO" SubTotal="1850" Descuento="175.00" Moneda="MXN" Total="1943.00" TipoDeComprobante="I" MetodoPago="PUE" LugarExpedicion="68050">
  <cfdi:Emisor Rfc="{rfc_emisor}" Nombre="FACTURACION MODERNA SA DE CV" RegimenFiscal="601"/>
  <cfdi:Receptor Rfc="XAXX010101000" Nombre="PUBLICO EN GENERAL" UsoCFDI="G01"/>
  <cfdi:Conceptos>
    <cfdi:Concepto ClaveProdServ="01010101" NoIdentificacion="AULOG001" Cantidad="5" ClaveUnidad="H87" Unidad="Pieza" Descripcion="Aurriculares USB Logitech" ValorUnitario="350.00" Importe="1750.00" Descuento="175.00">
      <cfdi:Impuestos>
        <cfdi:Traslados>
          <cfdi:Traslado Base="1575.00" Impuesto="002" TipoFactor="Tasa" TasaOCuota="0.160000" Importe="252.00"/>
      </cfdi:Traslados>
  </cfdi:Impuestos>
</cfdi:Concepto>
<cfdi:Concepto ClaveProdServ="43201800" NoIdentificacion="USB" Cantidad="1" ClaveUnidad="H87" Unidad="Pieza" Descripcion="Memoria USB 32gb marca Kingston" ValorUnitario="100.00" Importe="100.00">
  <cfdi:Impuestos>
    <cfdi:Traslados>
      <cfdi:Traslado Base="100.00" Impuesto="002" TipoFactor="Tasa" TasaOCuota="0.160000" Importe="16.00"/>
  </cfdi:Traslados>
</cfdi:Impuestos>
</cfdi:Concepto>
</cfdi:Conceptos>
<cfdi:Impuestos TotalImpuestosTrasladados="268.00">
    <cfdi:Traslados>
      <cfdi:Traslado Impuesto="002" TipoFactor="Tasa" TasaOCuota="0.160000" Importe="268.00"/>
  </cfdi:Traslados>
</cfdi:Impuestos>
</cfdi:Comprobante>
""".format(**locals())
  return cfdi

if __name__ == '__main__':
  prueba_timbrado()
