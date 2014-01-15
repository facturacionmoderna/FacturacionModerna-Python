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
  user_id = "UsuarioPruebasWS";
  user_password = "b9ec2afa3361a59af4b4d102d3f704eabdf097d4"

  cfdi = genera_xml(rfc_emisor)
  cfdi = sella_xml(cfdi, numero_certificado, archivo_cer, archivo_pem)

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


def sella_xml(cfdi, numero_certificado, archivo_cer, archivo_pem):
  keys = RSA.load_key(archivo_pem)
  cert_file = open(archivo_cer, 'r')
  cert = base64.b64encode(cert_file.read())
  xdoc = ET.fromstring(cfdi)
  xsl_root = ET.parse('utilerias/xslt32/cadenaoriginal_3_2.xslt')
  xsl = ET.XSLT(xsl_root)
  cadena_original = xsl(xdoc)
  digest = hashlib.new('sha1', str(cadena_original)).digest()
  sello = base64.b64encode(keys.sign(digest, "sha1"))


  comp = xdoc.get('Comprobante')
  xdoc.attrib['sello'] = sello
  xdoc.attrib['certificado'] = cert
  xdoc.attrib['noCertificado'] = numero_certificado
  print ET.tostring(xdoc)
  return ET.tostring(xdoc)

def genera_xml(rfc_emisor):
  # se calcula la fecha de emisión en formato ISO 8601
  fecha_actual = str(datetime.now().isoformat())[:19]
  
  cfdi = """<?xml version="1.0" encoding="UTF-8"?>
<cfdi:Comprobante xsi:schemaLocation="http://www.sat.gob.mx/cfd/3 http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv32.xsd" xmlns:cfdi="http://www.sat.gob.mx/cfd/3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xs="http://www.w3.org/2001/XMLSchema" version="3.2" fecha="{fecha_actual}" tipoDeComprobante="ingreso" noCertificado="" certificado="" sello="" formaDePago="Pago en una sola exhibicion" metodoDePago="Transferencia Electronica" NumCtaPago="No identificado" LugarExpedicion="San Pedro Garza Garcia, Mty." subTotal="10.00" total="11.60">
<cfdi:Emisor nombre="EMPRESA DEMO" rfc="{rfc_emisor}">
  <cfdi:RegimenFiscal Regimen="No aplica"/>
</cfdi:Emisor>
<cfdi:Receptor nombre="PUBLICO EN GENERAL" rfc="XAXX010101000"></cfdi:Receptor>
<cfdi:Conceptos>
  <cfdi:Concepto cantidad="10" unidad="No aplica" noIdentificacion="00001" descripcion="Servicio de Timbrado" valorUnitario="1.00" importe="10.00">
  </cfdi:Concepto>  
</cfdi:Conceptos>
<cfdi:Impuestos totalImpuestosTrasladados="1.60">
  <cfdi:Traslados>
    <cfdi:Traslado impuesto="IVA" tasa="16.00" importe="1.6"></cfdi:Traslado>
  </cfdi:Traslados>
</cfdi:Impuestos>
</cfdi:Comprobante>
""".format(**locals())
  return cfdi;

if __name__ == '__main__':
  prueba_timbrado()
