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

  retenciones = genera_xml(rfc_emisor,numero_certificado)
  retenciones = sella_xml(retenciones, numero_certificado, archivo_cer, archivo_pem)

  params = {'emisorRFC': rfc_emisor, 'UserID': user_id, 'UserPass': user_password}
  options = {'generarCBB': True, 'generarPDF': True, 'generarTXT': True}
  cliente = facturacion_moderna.Cliente(url_timbrado, params, debug)

  if cliente.timbrar(retenciones, options):
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


def sella_xml(retenciones, numero_certificado, archivo_cer, archivo_pem):
  keys = RSA.load_key(archivo_pem)
  cert_file = open(archivo_cer, 'r')
  cert = base64.b64encode(cert_file.read())
  xdoc = ET.fromstring(retenciones)
  

  xsl_root = ET.parse('utilerias/retenciones_xslt/retenciones.xslt')
  xsl = ET.XSLT(xsl_root)
  cadena_original = xsl(xdoc)
  digest = hashlib.new('sha1', str(cadena_original)).digest()
  sello = base64.b64encode(keys.sign(digest, "sha1"))

  comp = xdoc.get('Retenciones')
  xdoc.attrib['Sello'] = sello
  xdoc.attrib['Cert'] = cert
  print ET.tostring(xdoc)
  return ET.tostring(xdoc)

def genera_xml(rfc_emisor,numCert):
  # se calcula la fecha de emisión en formato ISO 8601
  fecha_actual = str(datetime.now().isoformat())[:19]
  
  retenciones = """<?xml version="1.0" encoding="UTF-8"?>
  <retenciones:Retenciones xmlns:retenciones="http://www.sat.gob.mx/esquemas/retencionpago/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sat.gob.mx/esquemas/retencionpago/1 http://www.sat.gob.mx/esquemas/retencionpago/1/retencionpagov1.xsd" Version="1.0" FolioInt="RetA" Sello="" NumCert="{numCert}" Cert="" FechaExp="{fecha_actual}-06:00" CveRetenc="05">
      <retenciones:Emisor RFCEmisor="{rfc_emisor}" NomDenRazSocE="Empresa retenedora ejemplo"/>
      <retenciones:Receptor Nacionalidad="Nacional">
          <retenciones:Nacional RFCRecep="XAXX010101000" NomDenRazSocR="Publico en General"/>
      </retenciones:Receptor>
      <retenciones:Periodo MesIni="12" MesFin="12" Ejerc="2014"/>
      <retenciones:Totales montoTotOperacion="33783.75" montoTotGrav="35437.50" montoTotExent="0.00" montoTotRet="7323.75">
          <retenciones:ImpRetenidos BaseRet="35437.50" Impuesto="02" montoRet="3780.00" TipoPagoRet="Pago definitivo"/>
          <retenciones:ImpRetenidos BaseRet="35437.50" Impuesto="01" montoRet="3543.75" TipoPagoRet="Pago provisional"/>
      </retenciones:Totales>
  </retenciones:Retenciones>
""".format(**locals())
  return retenciones;

if __name__ == '__main__':
  prueba_timbrado()
