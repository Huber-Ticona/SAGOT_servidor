from re import fullmatch
import shutil
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtGui import QPixmap , QIcon
import rpyc
import pymysql
import sys 
import os
import ctypes
import socket
from concurrent.futures import ThreadPoolExecutor
from rpyc.utils.server import ThreadedServer 
import logging
from shutil import rmtree
import json

logging.basicConfig(level=logging.DEBUG , format='%(threadName)s: %(message)s')

class MyService(rpyc.Service):



    def exposed_registrar_boleta(self,datos, items): #USADA POR EL AGENTE
        

        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                #v5.4 se agrego el estado_retiro y revisor ---> por defecto no retirado y no asignado.
                sql = "INSERT INTO nota_venta(interno, folio, nro_boleta, fecha, vendedor, monto_total, estado_retiro,revisor) VALUES (%s , %s ,%s , %s, %s , %s,'NO RETIRADO','NO ASIGNADO')"
                resultado = cursor.execute(sql , ( datos[0] , 0 , datos[1] , datos[2] , datos[3], datos[4] ) )

                if resultado:
                    print('Boleta: ' + str(datos[0]) +' almacenada correctamente')     
                    sql2 = "INSERT INTO item(interno ,cantidad, codigo, descripcion, unitario, total) VALUES (%s , %s ,%s , %s, %s , %s)"

                    resultado2 = cursor.executemany(sql2 , items )
                    if resultado2:
                        print('items de boleta agregados correctamente')
                        miConexion.commit()
                    else:
                        print('error al registrar items de boleta')
                    #print( str(l_cant[i]) + ' ' + l_cod[i]  + ' ' + l_descr[i]  + ' ' + str(l_uni[i])  + ' ' + str(l_tot[i]) )  
                else:
                    print('error al ingresar boleta')            
        finally:
                miConexion.close()
        
    def exposed_registrar_factura(self, datos , items):  #USADA POR EL AGENTE
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                #v5.4 se agrego el estado_retiro y revisor ---> por defecto no retirado y no asignado.
                sql = "INSERT INTO nota_venta(interno, folio, nro_boleta, fecha, vendedor, monto_total,nombre,estado_retiro,revisor) VALUES (%s , %s ,%s , %s, %s , %s,%s,'NO RETIRADO','NO ASIGNADO')"
                resultado = cursor.execute(sql , ( datos[0] , datos[1] , 0 , datos[2] , datos[3], datos[4] ,datos[5] ) )
                if resultado:
                    print('Factura: ' + str(datos[1]) +' almacenada correctamente')     
                    sql2 = "INSERT INTO item(interno ,cantidad, codigo, descripcion, unitario, total) VALUES (%s , %s ,%s , %s, %s , %s)"

                    resultado2 = cursor.executemany(sql2 , items )
                    if resultado2:
                        print('items de factura agregados correctamente')
                        miConexion.commit()
                    else:
                        print('error al registrar items de factura')
                    #print( str(l_cant[i]) + ' ' + l_cod[i]  + ' ' + l_descr[i]  + ' ' + str(l_uni[i])  + ' ' + str(l_tot[i]) )  
                else:
                    print('error al ingresar factura')            
        finally:
                miConexion.close()

    def exposed_buscar_fact(self , folio):  #USADA POR EL AGENTE
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                print('buscando fact')
                sql = "SELECT folio , interno FROM nota_venta WHERE folio = %s "
                cursor.execute(sql , (folio))
                
                resultado = cursor.fetchone()
                if resultado != None:
                    return True
                else:
                    return False        
        finally:
                miConexion.close()

    def exposed_buscar_bol(self , interno):  #USADA POR EL AGENTE
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                print('buscando bol')
                sql = "SELECT folio , interno FROM nota_venta WHERE interno = %s "
                cursor.execute(sql , (interno))
                
                resultado = cursor.fetchone()
                if resultado != None:
                    return True
                else:
                    return False        
        finally:
                miConexion.close()
    #v5.4 se agrego el nombre
    def exposed_buscar_venta_fecha(self, inicio , fin): #USADA POR EL CLIENTE1
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                
                sql = "SELECT interno,fecha,vendedor , folio, nro_boleta , monto_total, nombre FROM nota_venta WHERE fecha BETWEEN (%s) AND (%s) "
                cursor.execute(sql , (inicio , fin))
                resultado = cursor.fetchall()       
                return resultado
                  
        finally:
                miConexion.close()
    #v5.4 se agrego el nombre
    def exposed_buscar_venta_interno(self,interno): #USADA POR EL CLIENTE1
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                
                sql = "SELECT interno, fecha , vendedor, folio, nro_boleta , monto_total, nombre  FROM nota_venta WHERE interno = %s " #V4
                cursor.execute(sql , (interno))
                
                resultado = cursor.fetchone()
                if resultado != None:
                    print(resultado)
                    return resultado
                else:
                    return None      
        finally:
                miConexion.close()

    def exposed_obtener_item_interno(self, interno): #USADA POR EL CLIENTE 1
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                
                sql = "SELECT cantidad, descripcion, total FROM item WHERE interno = %s "
                cursor.execute(sql , (interno))
                
                resultado = cursor.fetchall()

                return resultado   
        finally:
                miConexion.close()
    def exposed_obtener_venta_interno(self,interno): #USADA POR EL CLIENTE 1
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                
                sql = "SELECT interno, folio , nro_boleta ,fecha , vendedor, nombre FROM nota_venta WHERE interno = (%s) " #v5 nombre agregado

                cursor.execute(sql , (interno))
                
                resultado = cursor.fetchone()
                if resultado != None:
                    print(resultado)
                    return resultado  
                else:
                    return None

        finally:
                miConexion.close()
    
    def exposed_registrar_orden_dimensionado(self, interno,fecha_vent ,nom, tel, fecha_est, detalle,tipo_doc,nro_doc,enchape,despacho,f_orden,contact,oce,vend):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )  #EL PROBLEMA ERA EL ATRIBUTO FECHA, YA QUE ESTE ERA DE TIPO DATETIME ,
                                                            #PERO EN LA COLSULTA SQL NO LO ADMITIA, YA QUE SOLO LEIA STRING CON FORMATO FECHA
        try:
            with miConexion.cursor() as cursor:

                sql = "INSERT INTO orden_dimensionado(interno,fecha_venta ,nombre,telefono,fecha_estimada, detalle ,tipo_doc, nro_doc,enchapado, despacho,fecha_orden,contacto,orden_compra,vendedor) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                resultado = cursor.execute( sql , (interno,fecha_vent ,nom, tel, fecha_est , detalle,tipo_doc ,nro_doc, enchape, despacho, f_orden,contact,oce,vend) )
                if resultado:
                    print('Orden almacenada correctamente.')
                    miConexion.commit()
                else:
                    print('Error al almacenar la orden')
        finally:
            miConexion.close()

    def exposed_buscar_orden_dim_interno(self,interno):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = "SELECT nro_orden , interno FROM orden_dimensionado WHERE interno = %s "
                cursor.execute(sql , (interno) )
                resultado = cursor.fetchall()
                print(resultado)
                return resultado
        finally:
            miConexion.close()
    def exposed_buscar_orden_dim_numero(self,numero):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = "SELECT nro_orden , interno , fecha_venta , nombre , telefono ,fecha_estimada, detalle, tipo_doc , nro_doc,enchapado, despacho, fecha_orden,contacto,orden_compra,fecha_real,vendedor,dimensionador,fecha_ingreso,observacion,extra FROM orden_dimensionado WHERE nro_orden = %s "
                cursor.execute(sql , (numero) )
                resultado = cursor.fetchone()
                return resultado
        finally:
            miConexion.close()

    def exposed_buscar_orden_dim_fecha(self, fecha ):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = "SELECT nro_orden , interno, fecha_venta , nombre , fecha_orden, fecha_estimada , extra FROM orden_dimensionado WHERE fecha_orden = %s  "
                cursor.execute(sql , (fecha))
                resultado = cursor.fetchall()       
                return resultado
        finally:
            miConexion.close()
        
    def exposed_actualizar_orden_dim(self,manual,interno,fecha_venta,tipo_doc,nro_doc,vendedor,   orden,nombre,telefono,fecha_est,detalle,despacho,enchapado,contacto,oce):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor: #si es orden creada con una boleta o factura

                if manual == False:
                    sql = "UPDATE orden_dimensionado SET nombre = %s,telefono = %s,fecha_estimada = %s,detalle = %s,despacho = %s,enchapado = %s,contacto = %s,orden_compra = %s WHERE nro_orden = %s "

                    resultado = cursor.execute(sql , ( nombre, telefono , fecha_est , detalle , despacho,enchapado, contacto,oce , orden) )
                    if resultado:
                        miConexion.commit()
                        print('ORDEN DE DIMENSIONADO ACTUALIZADA')
                        return True   
                    else:
                        return False
                elif manual == True: #si es orden manual
                    sql = "UPDATE orden_dimensionado SET nombre = %s,telefono = %s,fecha_estimada = %s,detalle = %s,despacho = %s,enchapado = %s,contacto = %s,orden_compra = %s,interno = %s,fecha_venta = %s,tipo_doc =%s,nro_doc = %s,vendedor=%s WHERE nro_orden = %s "
                    resultado = cursor.execute(sql , ( nombre, telefono , fecha_est , detalle , despacho,enchapado, contacto,oce ,interno,fecha_venta,tipo_doc,nro_doc,vendedor, orden) )
                    if resultado:
                        miConexion.commit()
                        print('ORDEN DE DIMENSIONADO v2 act exito bro')
                        return True   
                    else:
                        return False
        finally:
            miConexion.close()
    def exposed_actualizar_orden_dim2(self,orden, ingreso, dimensionador): #UTILIZADA POR EL CLIENTE2
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = "UPDATE orden_dimensionado SET dimensionador = %s ,fecha_ingreso = %s  WHERE nro_orden = %s "

                resultado = cursor.execute(sql , ( dimensionador, ingreso, orden ))
                if resultado:
                    miConexion.commit()
                    print('Orden actualizada')
                    return True   
                else:
                    return False
        finally:
            miConexion.close()
    def exposed_actualizar_orden_dim3(self,orden, real ): #UTILIZADA POR EL CLIENTE2
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = "UPDATE orden_dimensionado SET fecha_real = %s  WHERE nro_orden = %s "

                resultado = cursor.execute(sql , ( real , orden))
                if resultado:
                    miConexion.commit()
                    print('Orden actualizada')
                    return True   
                else:
                    return False
        finally:
            miConexion.close()


    def exposed_registrar_orden_elaboracion(self,nom,tel,f_orden,f_est,nro_doc,tipo_doc,contacto,oce,despacho,interno,detalle,f_venta,vend):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )  #EL PROBLEMA ERA EL ATRIBUTO FECHA, YA QUE ESTE ERA DE TIPO DATETIME ,                                                #PERO EN LA COLSULTA SQL NO LO ADMITIA, YA QUE SOLO LEIA STRING CON FORMATO FECHA
        try:
            with miConexion.cursor() as cursor:
                sql  = "INSERT INTO orden_elaboracion(nombre,telefono,fecha_orden,fecha_estimada,nro_doc,tipo_doc,contacto,orden_compra,despacho,interno,detalle,fecha_venta,vendedor) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"   
                resultado = cursor.execute( sql , (nom,tel,f_orden,f_est,nro_doc,tipo_doc,contacto,oce,despacho,interno,detalle,f_venta, vend ) )
                if resultado:
                    print('Orden elaboracion almacenada correctamente.')
                    miConexion.commit()
                else:
                    print('Error al almacenar la orden de elaboracion')
        finally:
            miConexion.close()
    def exposed_buscar_orden_elab_interno(self, interno):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = "SELECT nro_orden , interno FROM orden_elaboracion WHERE interno = %s "
                cursor.execute(sql , (interno) )
                resultado = cursor.fetchall()
                print(resultado)
                return resultado
        finally:
            miConexion.close()
    def exposed_buscar_orden_elab_numero(self,numero):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = "SELECT nro_orden,nombre,telefono,fecha_orden,fecha_estimada,nro_doc,tipo_doc,contacto,orden_compra,despacho,interno,detalle,fecha_venta,fecha_real,vendedor,observacion ,extra  FROM orden_elaboracion WHERE nro_orden = %s "
                cursor.execute(sql , (numero) )
                resultado = cursor.fetchone()
                return resultado
        finally:
            miConexion.close()
    def exposed_buscar_orden_elab_fecha(self, fecha ):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = "SELECT nro_orden , interno, fecha_orden , nombre, fecha_venta, fecha_estimada, extra FROM orden_elaboracion WHERE fecha_orden = %s  "
                cursor.execute(sql , (fecha))
                resultado = cursor.fetchall()       
                return resultado
        finally:
            miConexion.close()
    
    def exposed_actualizar_orden_elab(self, manual, interno, fecha_venta, tipo_doc, nro_doc, vendedor,  nombre,telefono,fecha_est,detalle,contacto,oce,despacho,nro_orden):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                if manual == False:
                    sql = "UPDATE orden_elaboracion SET nombre = %s,telefono = %s,fecha_estimada = %s,detalle = %s,despacho = %s,contacto = %s,orden_compra = %s WHERE nro_orden = %s "
                    resultado = cursor.execute(sql , ( nombre, telefono , fecha_est , detalle , despacho, contacto, oce , nro_orden) )
                    if resultado:
                        miConexion.commit()
                        print('ORDEN DE ELABORACION ACTUALIZADA')
                        return True   
                    else:
                        return False
                elif manual == True:
                    sql = "UPDATE orden_elaboracion SET nombre = %s,telefono = %s,fecha_estimada = %s,detalle = %s,despacho = %s,contacto = %s,orden_compra = %s, interno=%s,fecha_venta=%s,tipo_doc=%s,nro_doc=%s,vendedor=%s WHERE nro_orden = %s "
                    resultado = cursor.execute(sql , ( nombre, telefono , fecha_est , detalle , despacho, contacto, oce ,interno,fecha_venta,tipo_doc,nro_doc,vendedor ,nro_orden) )
                    if resultado:
                        miConexion.commit()
                        print('ORDEN DE ELABORACION v2 ACTUALIZADA')
                        return True   
                    else:
                        return False

        finally:
            miConexion.close()
    def exposed_actualizar_orden_elab2(self,orden, real ): #UTILIZADA POR EL CLIENTE2
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = "UPDATE orden_elaboracion SET fecha_real = %s  WHERE nro_orden = %s "

                resultado = cursor.execute(sql , ( real , orden))
                if resultado:
                    miConexion.commit()
                    print('Orden elaboracion actualizada')
                    return True   
                else:
                    return False
        finally:
            miConexion.close()

    def exposed_registrar_orden_carpinteria(self,nom,tel,f_orden,f_est,nro_doc,tipo_doc,contacto,oce,despacho,interno,detalle,f_venta,vend):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )  #EL PROBLEMA ERA EL ATRIBUTO FECHA, YA QUE ESTE ERA DE TIPO DATETIME ,                                                #PERO EN LA COLSULTA SQL NO LO ADMITIA, YA QUE SOLO LEIA STRING CON FORMATO FECHA
        try:
            with miConexion.cursor() as cursor:
                sql  = "INSERT INTO orden_carpinteria(nombre,telefono,fecha_orden,fecha_estimada,nro_doc,tipo_doc,contacto,orden_compra,despacho,interno,detalle,fecha_venta,vendedor) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"   
                resultado = cursor.execute( sql , (nom,tel,f_orden,f_est,nro_doc,tipo_doc,contacto,oce,despacho,interno,detalle,f_venta,vend ) )
                if resultado:
                    print('Orden carpinteria almacenada correctamente.')
                    miConexion.commit()
                else:
                    print('Error al almacenar la orden de carpinteria')
        finally:
            miConexion.close()
    def exposed_buscar_orden_carp_interno(self, interno):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = "SELECT nro_orden , interno FROM orden_carpinteria WHERE interno = %s "
                cursor.execute(sql , (interno) )
                resultado = cursor.fetchall()
                print(resultado)
                return resultado
        finally:
            miConexion.close()
    def exposed_buscar_orden_carp_numero(self,numero):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = "SELECT nro_orden,nombre,telefono,fecha_orden,fecha_estimada,nro_doc,tipo_doc,contacto,orden_compra,despacho,interno,detalle,fecha_venta,fecha_real,vendedor,observacion,extra  FROM orden_carpinteria WHERE nro_orden = %s "
                cursor.execute(sql , (numero) )
                resultado = cursor.fetchone()
                return resultado
        finally:
            miConexion.close()
    def exposed_buscar_orden_carp_fecha(self, fecha ):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = "SELECT nro_orden , interno, fecha_orden , nombre,fecha_venta, fecha_estimada, extra FROM orden_carpinteria WHERE fecha_orden = %s  "
                cursor.execute(sql , (fecha))
                resultado = cursor.fetchall()       
                return resultado
        finally:
            miConexion.close()
    def exposed_actualizar_orden_carp(self, manual, interno, fecha_venta, tipo_doc, nro_doc, vendedor,   nombre,telefono,fecha_est,detalle,contacto,oce,despacho,nro_orden):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                if manual == False:
                    sql = "UPDATE orden_carpinteria SET nombre = %s,telefono = %s,fecha_estimada = %s,detalle = %s,despacho = %s,contacto = %s,orden_compra = %s WHERE nro_orden = %s "
                    resultado = cursor.execute(sql , ( nombre, telefono , fecha_est , detalle , despacho, contacto, oce , nro_orden) )
                    if resultado:
                        miConexion.commit()
                        print('ORDEN DE carpinteria ACTUALIZADA')
                        return True   
                    else:
                        return False
                elif manual == True:
                    sql = "UPDATE orden_carpinteria SET nombre = %s,telefono = %s,fecha_estimada = %s,detalle = %s,despacho = %s,contacto = %s,orden_compra = %s, interno=%s,fecha_venta=%s,tipo_doc=%s,nro_doc=%s,vendedor=%s WHERE nro_orden = %s "
                    resultado = cursor.execute(sql , ( nombre, telefono , fecha_est , detalle , despacho, contacto, oce ,interno,fecha_venta,tipo_doc,nro_doc,vendedor ,nro_orden) )
                    if resultado:
                        miConexion.commit()
                        print('ORDEN DE carpinteria v2 ACTUALIZADA')
                        return True   
                    else:
                        return False
        finally:
            miConexion.close()
    def exposed_actualizar_orden_carp2(self,orden, real ): #UTILIZADA POR EL CLIENTE2
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = "UPDATE orden_carpinteria SET fecha_real = %s  WHERE nro_orden = %s "
                resultado = cursor.execute(sql , ( real , orden))
                if resultado:
                    miConexion.commit()
                    print('Orden carpinteria actualizada')
                    return True   
                else:
                    return False
        finally:
            miConexion.close()


    def exposed_registrar_orden_pallets(self,nom,tel,f_orden,f_est,nro_doc,tipo_doc,contacto,oce,despacho,interno,detalle,f_venta,vend):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )  #EL PROBLEMA ERA EL ATRIBUTO FECHA, YA QUE ESTE ERA DE TIPO DATETIME ,                                                #PERO EN LA COLSULTA SQL NO LO ADMITIA, YA QUE SOLO LEIA STRING CON FORMATO FECHA
        try:
            with miConexion.cursor() as cursor:
                sql  = "INSERT INTO orden_pallets(nombre,telefono,fecha_orden,fecha_estimada,nro_doc,tipo_doc,contacto,orden_compra,despacho,interno,detalle,fecha_venta,vendedor) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"   
                resultado = cursor.execute( sql , (nom,tel,f_orden,f_est,nro_doc,tipo_doc,contacto,oce,despacho,interno,detalle,f_venta,vend ) )
                if resultado:
                    print('Orden pallets almacenada correctamente.')
                    miConexion.commit()
                else:
                    print('Error al almacenar la orden de pallets')
        finally:
            miConexion.close()
    def exposed_buscar_orden_pall_interno(self, interno):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = "SELECT nro_orden , interno FROM orden_pallets WHERE interno = %s "
                cursor.execute(sql , (interno) )
                resultado = cursor.fetchall()
                print(resultado)
                return resultado
        finally:
            miConexion.close()
    def exposed_buscar_orden_pall_numero(self,numero):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = "SELECT nro_orden,nombre,telefono,fecha_orden,fecha_estimada,nro_doc,tipo_doc,contacto,orden_compra,despacho,interno,detalle,fecha_venta,fecha_real,vendedor,observacion,extra  FROM orden_pallets WHERE nro_orden = %s "
                cursor.execute(sql , (numero) )
                resultado = cursor.fetchone()
                return resultado
        finally:
            miConexion.close()
    def exposed_buscar_orden_pall_fecha(self, fecha ):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = "SELECT nro_orden , interno, fecha_orden , nombre, fecha_venta, fecha_estimada, extra FROM orden_pallets WHERE fecha_orden = %s  "
                cursor.execute(sql , (fecha))
                resultado = cursor.fetchall()    
                return resultado
        finally:
            miConexion.close()       
    def exposed_actualizar_orden_pall(self , manual, interno, fecha_venta, tipo_doc, nro_doc, vendedor,   nombre,telefono,fecha_est,detalle,contacto,oce,despacho,nro_orden):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                if manual == False:
                    sql = "UPDATE orden_pallets SET nombre = %s,telefono = %s,fecha_estimada = %s,detalle = %s,despacho = %s,contacto = %s,orden_compra = %s WHERE nro_orden = %s "
                    resultado = cursor.execute(sql , ( nombre, telefono , fecha_est , detalle , despacho, contacto, oce , nro_orden) )
                    if resultado:
                        miConexion.commit()
                        print('ORDEN DE pallets ACTUALIZADA')
                        return True   
                    else:
                        return False
                elif manual == True:
                    sql = "UPDATE orden_pallets SET nombre = %s,telefono = %s,fecha_estimada = %s,detalle = %s,despacho = %s,contacto = %s,orden_compra = %s, interno=%s,fecha_venta=%s,tipo_doc=%s,nro_doc=%s,vendedor=%s WHERE nro_orden = %s "
                    resultado = cursor.execute(sql , ( nombre, telefono , fecha_est , detalle , despacho, contacto, oce ,interno,fecha_venta,tipo_doc,nro_doc,vendedor ,nro_orden) )
                    if resultado:
                        miConexion.commit()
                        print('ORDEN DE pallets v2 ACTUALIZADA')
                        return True   
                    else:
                        return False
        finally:
            miConexion.close()
    def exposed_actualizar_orden_pall2(self,orden, real ): #UTILIZADA POR EL CLIENTE2
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = "UPDATE orden_pallets SET fecha_real = %s  WHERE nro_orden = %s "

                resultado = cursor.execute(sql , ( real , orden))
                if resultado:
                    miConexion.commit()
                    print('Orden pallets actualizada')
                    return True   
                else:
                    return False
        finally:
            miConexion.close()

    def exposed_actualizar_orden_dim_obser(self,observacion , nro_orden):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = " UPDATE orden_dimensionado SET observacion = %s WHERE nro_orden = %s "
                cursor.execute(sql , ( observacion, nro_orden  ) )
                miConexion.commit()                         #Puede fallar y tocara analisar si se ejecuto correctamente la sentencia SQL o no.
        finally:
            miConexion.close()

    def exposed_actualizar_orden_elab_obser(self,observacion , nro_orden):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = " UPDATE orden_elaboracion SET observacion = %s WHERE nro_orden = %s "
                cursor.execute(sql , ( observacion, nro_orden  ) )
                miConexion.commit()                         #Puede fallar y tocara analisar si se ejecuto correctamente la sentencia SQL o no.
        finally:
            miConexion.close()
    
    def exposed_actualizar_orden_carp_obser(self,observacion , nro_orden):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = " UPDATE orden_carpinteria SET observacion = %s WHERE nro_orden = %s "
                cursor.execute(sql , ( observacion, nro_orden  ) )
                miConexion.commit()                         #Puede fallar y tocara analisar si se ejecuto correctamente la sentencia SQL o no.
        finally:
            miConexion.close()
    
    def exposed_actualizar_orden_pall_obser(self,observacion , nro_orden):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = " UPDATE orden_pallets SET observacion = %s WHERE nro_orden = %s "
                cursor.execute(sql , ( observacion, nro_orden  ) )
                miConexion.commit()                         #Puede fallar y tocara analisar si se ejecuto correctamente la sentencia SQL o no.
        finally:
            miConexion.close()

    def exposed_registrar_dimensionador(self, nombre, telefono, inicio):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = "INSERT INTO dimensionador(nombre, telefono, fecha_inicio, estado) VALUES ( %s ,%s , %s , 'ACTIVO')"

                resultado = cursor.execute(sql , ( nombre, telefono, inicio) )
                if resultado:
                    miConexion.commit()
                    print('DIMENSIONADOR REGISTRADO')
                    return True   
                else:
                    return False
        finally:
            miConexion.close()
    def exposed_obtener_dimensionador_activo(self):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = "SELECT nombre, telefono, fecha_inicio, nro_dimensionador FROM dimensionador WHERE estado = 'ACTIVO'   "
                cursor.execute( sql )
                resultado = cursor.fetchall()
                return resultado
        finally:
            miConexion.close()
    def exposed_actualizar_dimensionador(self,nombre,telefono,inicio,nro_dimensionador):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = " UPDATE dimensionador SET nombre = %s , telefono = %s , fecha_inicio =  %s WHERE nro_dimensionador = %s "

                resultado = cursor.execute(sql , ( nombre, telefono, inicio, nro_dimensionador ) )
                if resultado:
                    miConexion.commit()
                    print('Dimensionador actualizado')
                    return True   
                else:
                    return False
        finally:
            miConexion.close()
    def exposed_retirar_dimensionador(self, nro_dimensionador,termino ):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = " UPDATE dimensionador SET estado = 'NO ACTIVO' , fecha_termino = %s WHERE nro_dimensionador = %s "

                resultado = cursor.execute(sql , (termino, nro_dimensionador ) )
                if resultado:
                    miConexion.commit()
                    print('Dimensionador RETIRADO')
                    return True   
                else:
                    return False
        finally:
            miConexion.close()

    def exposed_registrar_usuario(self, nombre, contra, telefono, inicio, super,tipo,funciones,full_nom):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = "INSERT INTO usuario(nombre, contraseña ,telefono, fecha_inicio, super_usuario , estado ,tipo, funciones, nombre_completo) VALUES (%s,%s,%s,%s,%s,'ACTIVO',%s,%s,%s)"
                resultado = cursor.execute(sql , ( nombre,contra, telefono, inicio,super,tipo,funciones, full_nom ) )
                if resultado:
                    miConexion.commit()
                    print('USUARIO REGISTRADO')
                    return True   
                else:
                    return False
        finally:
            miConexion.close()
    def exposed_obtener_usuario_activo(self):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = "SELECT nombre,contraseña, telefono, fecha_inicio, super_usuario ,nro_usuario,tipo,funciones,nombre_completo FROM usuario WHERE estado = 'ACTIVO' "
                cursor.execute( sql )
                resultado = cursor.fetchall()
                return resultado
        finally:
            miConexion.close()
    def exposed_actualizar_usuario(self,nombre, contra, telefono,inicio, super,tipo,detalle ,nro_usuario, full_nomb):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = " UPDATE usuario SET nombre=%s, contraseña = %s, telefono=%s, fecha_inicio= %s, super_usuario=%s , tipo = %s,funciones = %s, nombre_completo = %s WHERE nro_usuario = %s "

                resultado = cursor.execute(sql , ( nombre,contra, telefono, inicio,super,tipo, detalle, full_nomb, nro_usuario ) )
                if resultado:
                    miConexion.commit()
                    print('Usuario actualizado')
                    return True   
                else:
                    return False
        finally:
            miConexion.close()
    def exposed_retirar_usuario(self, nro_usuario, termino ):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = " UPDATE usuario SET estado = 'NO ACTIVO' , fecha_termino = %s WHERE nro_usuario = %s "

                resultado = cursor.execute(sql , (termino, nro_usuario ) )
                if resultado:
                    miConexion.commit()
                    print('Dimensionador RETIRADO')
                    return True   
                else:
                    return False
        finally:
            miConexion.close()

    def exposed_registrar_clave(self, clave ):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = "INSERT INTO clave(clave_unica) VALUES (%s)"
                resultado = cursor.execute(sql , ( clave ) )
                if resultado:
                    miConexion.commit()
                    print('clave REGISTRADa')
                    return True   
                else:
                    return False
        finally:
            miConexion.close()
    def exposed_obtener_clave(self):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = "SELECT clave_unica FROM clave "
                cursor.execute( sql )
                resultado = cursor.fetchall()
                return resultado
                
        finally:
            miConexion.close()
    def exposed_eliminar_clave(self, clave):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = "DELETE FROM clave WHERE clave_unica = %s "
                cursor.execute( sql , (clave))
                miConexion.commit()
        finally:
            miConexion.close()
    
    def exposed_informe_dimensionado(self, inicio, termino):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = "SELECT * FROM orden_dimensionado WHERE fecha_orden BETWEEN %s AND %s "
                cursor.execute( sql , (inicio, termino) )
                resultado = cursor.fetchall()
                return resultado
        finally:
            miConexion.close()
    
    def exposed_informe_elaboracion(self, inicio, termino):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = "SELECT nro_orden,nombre,telefono,fecha_orden,fecha_estimada,fecha_real,nro_doc,tipo_doc,contacto,orden_compra,despacho,interno,detalle,fecha_venta,vendedor,observacion,extra  FROM orden_elaboracion WHERE fecha_orden BETWEEN %s AND %s "
                cursor.execute( sql , (inicio, termino) )
                resultado = cursor.fetchall()
                return resultado
        finally:
            miConexion.close()
    
    def exposed_informe_carpinteria(self, inicio, termino):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = "SELECT nro_orden,nombre,telefono,fecha_orden,fecha_estimada,fecha_real,nro_doc,tipo_doc,contacto,orden_compra,despacho,interno,detalle,fecha_venta,vendedor,observacion,extra  FROM orden_carpinteria WHERE fecha_orden BETWEEN %s AND %s "
                cursor.execute( sql , (inicio, termino) )
                resultado = cursor.fetchall()
                return resultado
        finally:
            miConexion.close()
    
    def exposed_informe_pallets(self, inicio, termino):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = "SELECT nro_orden,nombre,telefono,fecha_orden,fecha_estimada,fecha_real,nro_doc,tipo_doc,contacto,orden_compra,despacho,interno,detalle,fecha_venta,vendedor,observacion,extra FROM orden_pallets WHERE fecha_orden BETWEEN %s AND %s "
                cursor.execute( sql , (inicio, termino) )
                resultado = cursor.fetchall()
                return resultado
        finally:
            miConexion.close()
    
    def exposed_registrar_reingreso(self, fecha,tipo_doc,nro_doc,nro_orden,motivo,descripcion,proceso, detalle,solucion):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = "INSERT INTO reingreso(fecha, tipo_doc, nro_doc, nro_orden, motivo, descripcion, proceso, detalle, solucion) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                resultado = cursor.execute(sql , ( fecha, tipo_doc, nro_doc, nro_orden ,motivo, descripcion, proceso, detalle, solucion ) )
                if resultado:
                    miConexion.commit()
                    print('reingreso registrado')
                    return True   
                else:
                    return False
        finally:
            miConexion.close()
    
    def exposed_informe_reingreso(self, inicio, termino):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = "SELECT * FROM reingreso WHERE fecha BETWEEN %s AND %s "
                cursor.execute( sql , (inicio, termino) )
                resultado = cursor.fetchall()
                return resultado
        finally:
            miConexion.close()

    def exposed_obtener_max_reingreso(self):
        miConexion = pymysql.connect( host= 'localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        print('obteniendo max reingreso')
        try:
            with miConexion.cursor() as cursor:

                sql = "SELECT max(nro_reingreso) FROM reingreso "
                cursor.execute( sql )
                resultado = cursor.fetchone()
                return resultado
                
        finally:
            miConexion.close()

    def exposed_anular_orden(self,tipo , extra, orden ):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                sql = "UPDATE orden_"+ tipo + " SET extra = %s  WHERE nro_orden = %s"
                resultado = cursor.execute(sql ,  (extra , orden)  )
                if resultado:
                    miConexion.commit()
                    print(tipo + ': extra REGISTRADO')
                    return True   
                else:
                    return False
        finally:
            miConexion.close()

    def exposed_buscar_prod_cod(self,dato):
        miConexion = pymysql.connect( host= 'localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        #print('buscando por codigo: ' + str(dato))
        try:
            with miConexion.cursor() as cursor:

                sql = "SELECT codigo,descripcion FROM producto WHERE codigo LIKE '"+ dato + "%' "
                cursor.execute( sql )
                resultado = cursor.fetchall()
                return resultado
                
        finally:
            miConexion.close()
    def exposed_buscar_prod_descr(self,dato):
        miConexion = pymysql.connect( host= 'localhost',
        user= 'huber', passwd='huber123', db='madenco' )

        #print('buscando por descripcion: ' + str(dato))
        try:
            with miConexion.cursor() as cursor:
                sql = "SELECT codigo,descripcion FROM producto WHERE descripcion LIKE '%"+ dato +"%' " 
                cursor.execute( sql )
                resultado = cursor.fetchall()
                return resultado
                
        finally:
            miConexion.close()

    def exposed_respaldo(self,fecha):
        actual = os.path.abspath(os.getcwd())
        actual = actual.replace('\\' , '/')
        carpeta = actual + '/respaldo_datos/Hasta_' + fecha
        if os.path.isdir(carpeta):
            print('existe la carpeta....eliminando carpeta')
            rmtree(carpeta) #eliminando carpeta con contenido
            print('creando denuevo')
            os.mkdir( carpeta )

        else: 
            os.mkdir( carpeta )
            print('se creo la carpeta')
        
        print('Nombre de la carpeta: ' + carpeta)

        miConexion = pymysql.connect( host= 'localhost', ## root porque asi se puede respaldar localmente los provilegios que no funcionan con usuario huber nose porque.
        user= 'root', passwd='', db='madenco' )
        #print('buscando por descripcion: ' + str(dato))
        try:
            with miConexion.cursor() as cursor:
                
                sql = "SELECT * from item INTO OUTFILE '" + carpeta +"/item.csv' FIELDS TERMINATED BY ';' LINES TERMINATED BY '\n' ; "   # ITEM
                cursor.execute( sql )
                sql = "SELECT * from nota_venta INTO OUTFILE '" + carpeta +"/nota_venta.csv' FIELDS TERMINATED BY ';' LINES TERMINATED BY '\n' ; " # NOTA_VENTA
                cursor.execute( sql )
                sql = "SELECT * from orden_dimensionado INTO OUTFILE '" + carpeta +"/orden_dimensionado.csv'  FIELDS TERMINATED BY ';' LINES TERMINATED BY '\n' ;" 
                cursor.execute( sql )
                sql = "SELECT * from orden_elaboracion INTO OUTFILE '" + carpeta +"/orden_elaboracion.csv'  FIELDS TERMINATED BY ';' LINES TERMINATED BY '\n' ;" 
                cursor.execute( sql )
                sql = "SELECT * from orden_carpinteria INTO OUTFILE '" + carpeta +"/orden_carpinteria.csv'  FIELDS TERMINATED BY ';' LINES TERMINATED BY '\n' ;" 
                cursor.execute( sql )
                sql = "SELECT * from orden_pallets INTO OUTFILE '" + carpeta +"/orden_pallets.csv'  FIELDS TERMINATED BY ';' LINES TERMINATED BY '\n' ;" 
                cursor.execute( sql )
                sql = "SELECT * from reingreso INTO OUTFILE '" + carpeta +"/reingreso.csv'  FIELDS TERMINATED BY ';' LINES TERMINATED BY '\n' ;" 
                cursor.execute( sql )
                sql = "SELECT * from usuario  INTO OUTFILE '" + carpeta +"/usuario.csv'  FIELDS TERMINATED BY ';' LINES TERMINATED BY '\n' ;" 
                cursor.execute( sql )
                sql = "SELECT * from dimensionador  INTO OUTFILE '" + carpeta +"/dimensionador.csv'  FIELDS TERMINATED BY ';' LINES TERMINATED BY '\n' ;" 
                cursor.execute( sql )
                sql = "SELECT * from guia  INTO OUTFILE '" + carpeta +"/guia.csv'  FIELDS TERMINATED BY ';' LINES TERMINATED BY '\n' ;" 
                cursor.execute( sql )
                sql = "SELECT * from nota_credito  INTO OUTFILE '" + carpeta +"/nota_credito.csv'  FIELDS TERMINATED BY ';' LINES TERMINATED BY '\n' ;" 
                cursor.execute( sql )

                return True
        
        finally:
            miConexion.close()
    #Version 5.4 ... agregado el registrar y buscar guias, creditos
    def exposed_registrar_guia(self,folio,interno,fecha,nombre,detalle):
        miConexion = pymysql.connect( host= 'localhost',
        user= 'huber', passwd='huber123', db='madenco' )

        #print('buscando por descripcion: ' + str(dato))
        try:
            with miConexion.cursor() as cursor:
                sql = "INSERT INTO guia(folio, interno, fecha, nombre, detalle ) VALUES (%s,%s,%s,%s,%s)" 
                resultado = cursor.execute( sql , (folio,interno,fecha,nombre,detalle))
                if resultado:
                    miConexion.commit()
                    print('guia: '+ str(folio) +' registrada')
                    return True   
                else:
                    return False        
                
        finally:
            miConexion.close()
    
    def exposed_buscar_guia(self,interno):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                print('buscando guia')
                sql = "SELECT folio , interno FROM guia WHERE interno = %s "
                cursor.execute(sql , (interno))
                resultado = cursor.fetchone()
                if resultado != None:
                    return True
                else:
                    return False        
        finally:
                miConexion.close()
    # version 5.4
    def exposed_buscar_orden_nombre(self,tipo , nombre ):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                print('buscando x:' + nombre)
                
                sql = "SELECT nro_orden, interno, fecha_orden,nombre ,fecha_venta, fecha_estimada, extra FROM orden_"+ tipo +" WHERE nombre LIKE '%" + nombre + "%' "
                
                cursor.execute(sql)
                resultado = cursor.fetchall()
                return resultado
        finally:
            miConexion.close() 

    def exposed_obtener_guia_fecha(self,inicio , fin):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                
                sql = "SELECT * FROM guia WHERE fecha BETWEEN (%s) AND (%s) "
                cursor.execute(sql , (inicio , fin))
                resultado = cursor.fetchall()       
                return resultado
                  
        finally:
                miConexion.close()
    def exposed_obtener_guia_interno(self,interno):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                print('buscando guia')
                sql = "SELECT * FROM guia WHERE interno = %s "
                cursor.execute(sql , (interno))
                resultado = cursor.fetchone()
                if resultado != None:
                    #print(resultado)
                    return resultado
                else:
                    return None   
        finally:
                miConexion.close()
    def exposed_obtener_venta_nombre(self, nombre):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                
                sql = "SELECT interno, fecha,vendedor , folio, nro_boleta , monto_total, nombre FROM nota_venta where nombre like '%" +nombre + "%' "
                cursor.execute(sql)
                resultado = cursor.fetchall()       
                return resultado
        finally:
                miConexion.close()

    def exposed_obtener_guia_nombre(self, nombre):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                
                sql = "SELECT * from guia WHERE nombre like '%" + nombre + "%' "
                cursor.execute(sql)
                resultado = cursor.fetchall()       
                return resultado
                  
        finally:
                miConexion.close()

    
    def exposed_registrar_nota_credito(self,folio,interno,fecha,nombre,detalle):
        miConexion = pymysql.connect( host= 'localhost',
        user= 'huber', passwd='huber123', db='madenco' )

        #print('buscando por descripcion: ' + str(dato))
        try:
            with miConexion.cursor() as cursor:
                sql = "INSERT INTO nota_credito(folio, interno, fecha, nombre, detalle ) VALUES (%s,%s,%s,%s,%s)" 
                resultado = cursor.execute( sql , (folio,interno,fecha,nombre,detalle))
                if resultado:
                    miConexion.commit()
                    print('nota_Credito: '+ str(folio) +' registrada')
                    return True   
                else:
                    return False        
                
        finally:
            miConexion.close()
    def exposed_buscar_credito(self,interno):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                print('buscando nota credito')
                sql = "SELECT folio , interno FROM nota_credito WHERE folio = %s "
                cursor.execute(sql , (interno))
                resultado = cursor.fetchone()
                if resultado != None:
                    return True
                else:
                    return False        
        finally:
                miConexion.close()

    def exposed_añadir_vinculo_credito_a_venta(self, tipo_doc, folio,folio_credito):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                print('buscando si existe vnculacion')
                if tipo_doc == 'FACTURA':
                    sql = "SELECT vinculaciones FROM nota_venta WHERE folio = %s "
                    cursor.execute(sql , (folio))
                    resultado = cursor.fetchone()
                elif tipo_doc == 'BOLETA':
                    sql = "SELECT vinculaciones FROM nota_venta WHERE nro_boleta = %s "
                    cursor.execute(sql , (folio))
                    resultado = cursor.fetchone()
                else:
                    print('NO ES NOTA_DE VENTA, posiblemente una guia')
                    resultado = None
                print(resultado)

                if resultado != None:
                    print('nota venta encontrada')
                    if resultado[0] != None:
                        print('tiene vinculaciones, procediendo a añadir credito')
                        vinculaciones = json.loads(resultado[0])
                        try:
                            vinculaciones["creditos"].append(folio_credito)

                        except KeyError:
                            print('Vinculo a credito no encontrado, creando el vinculo.,.')
                            lista = []
                            lista.append(folio_credito)
                            vinculaciones["creditos"] = lista
                        vinculaciones = json.dumps(vinculaciones)
                        
                    else:
                        print('No tiene vnculaciones')
                        lista = []
                        lista.append(folio_credito)
                        detalle = {
                            "creditos" : lista
                        }
                        vinculaciones = json.dumps(detalle)
                    print(vinculaciones)
                    
                    if tipo_doc == 'FACTURA':
                        sql2 = 'update nota_venta set vinculaciones = %s where folio = %s'
                        cursor.execute(sql2 , (vinculaciones,folio))
                        miConexion.commit()

                    elif tipo_doc == 'BOLETA':
                        sql2 = 'update nota_venta set vinculaciones = %s where nro_boleta = %s'
                        cursor.execute(sql2 , (vinculaciones,folio))
                        miConexion.commit()
                    print('VINCULO CREDITO AÑADIDO CORRECTAMENTE')
                    return True
                    
                else:
                    print('Nota venta NO encontrada')
                    return False        
        finally:
                miConexion.close()
    def exposed_añadir_vinculo_guia_a_venta(self, tipo_doc, folio, folio_guia):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                print('buscando si existe vinculacion')
                if tipo_doc == 'FACTURA':
                    sql = "SELECT vinculaciones FROM nota_venta WHERE folio = %s "
                    cursor.execute(sql , (folio))
                    resultado = cursor.fetchone()
                elif tipo_doc == 'BOLETA':
                    sql = "SELECT vinculaciones FROM nota_venta WHERE nro_boleta = %s "
                    cursor.execute(sql , (folio))
                    resultado = cursor.fetchone()
                else:
                    print('NO ES NOTA_DE VENTA, posiblemente una guia')
                    resultado = None
                print(resultado)

                if resultado != None:
                    print('nota venta encontrada')
                    if resultado[0] != None:
                        print('tiene vinculaciones, procediendo a añadir guia')
                        vinculaciones = json.loads(resultado[0])
                        try:
                            vinculaciones["guias"].append(folio_guia)

                        except KeyError:
                            print('Vinculo a guia no encontrado, creando el vinculo.,.')
                            lista = []
                            lista.append(folio_guia)
                            vinculaciones["guias"] = lista
                        vinculaciones = json.dumps(vinculaciones)
                        
                    else:
                        print('No tiene vnculaciones')
                        lista = []
                        lista.append(folio_guia)
                        detalle = {
                            "guias" : lista
                        }
                        vinculaciones = json.dumps(detalle)
                    print(vinculaciones)
                    
                    if tipo_doc == 'FACTURA':
                        sql2 = 'update nota_venta set vinculaciones = %s where folio = %s'
                        cursor.execute(sql2 , (vinculaciones,folio))
                        miConexion.commit()

                    elif tipo_doc == 'BOLETA':
                        sql2 = 'update nota_venta set vinculaciones = %s where nro_boleta = %s'
                        cursor.execute(sql2 , (vinculaciones,folio))
                        miConexion.commit()
                    print('VINCULO GUIA AÑADIDO CORRECTAMENTE')
                    return True
                    
                else:
                    print('Nota venta NO encontrada')
                    return False        
        finally:
                miConexion.close()
    def exposed_añadir_vinculo_orden_a_venta(self, tipo_doc , detalle , folio):
        miConexion = pymysql.connect( host='localhost',
        user= 'huber', passwd='huber123', db='madenco' )
        try:
            with miConexion.cursor() as cursor:
                resultado = None
                print('-------------- vinculo orden a venta -------------')
                if tipo_doc == 'FACTURA':
                    sql = "SELECT vinculaciones FROM nota_venta WHERE folio = %s "
                    cursor.execute(sql , (folio))
                    resultado = cursor.fetchone()
                elif tipo_doc == 'BOLETA':
                    sql = "SELECT vinculaciones FROM nota_venta WHERE nro_boleta = %s "
                    cursor.execute(sql , (folio))
                    resultado = cursor.fetchone()
                elif tipo_doc == 'GUIA':
                    print('NO ES NOTA_DE VENTA, posiblemente una guia')
                    sql = "SELECT vinculaciones FROM guia WHERE folio = %s "
                    cursor.execute(sql , (folio))
                    resultado = cursor.fetchone()

                    
                print(resultado)

                if resultado != None:
                    print(f'nota venta: {tipo_doc} encontrada')
                    if resultado[0] != None:
                        print('tiene vinculaciones, procediendo a añadir orden')
                        vinculaciones = json.loads(resultado[0])
                        try:
                            vinculaciones["ordenes"].append(detalle)

                        except KeyError:
                            print('Vinculo a guia no encontrado, creando el vinculo.,.')
                            lista = []
                            lista.append(detalle)
                            vinculaciones["ordenes"] = lista

                        vinculaciones = json.dumps(vinculaciones)
                        
                    else:
                        print('No tiene vinculaciones')
                        lista = []
                        lista.append(detalle)
                        detalle2 = {
                            "ordenes" : lista
                        }
                        vinculaciones = json.dumps(detalle2)
                    print(vinculaciones)
                    
                    if tipo_doc == 'FACTURA':
                        sql2 = 'update nota_venta set vinculaciones = %s where folio = %s'
                        cursor.execute(sql2 , (vinculaciones,folio))
                        miConexion.commit()

                    elif tipo_doc == 'BOLETA':
                        sql2 = 'update nota_venta set vinculaciones = %s where nro_boleta = %s'
                        cursor.execute(sql2 , (vinculaciones,folio))
                        miConexion.commit()
                    elif tipo_doc == 'GUIA':
                        sql2 = 'update guia set vinculaciones = %s where folio = %s'
                        cursor.execute(sql2 , (vinculaciones,folio))
                        miConexion.commit()

                    print('VINCULO ORDEN DE TRABAJO AÑADIDO CORRECTAMENTE')
                    print('------------------------------------------------')
                    return True
                    
                else:
                    print('Nota venta NO encontrada')
                    return False        
        finally:
                miConexion.close()
    


class Servidor(QMainWindow):
    servidor = None
    nombre_pc = None
    direccion_pc = None
    def __init__(self):
        super(Servidor, self).__init__()
        uic.loadUi('servidor.ui', self)
        self.inicializar()

        self.executor = ThreadPoolExecutor(max_workers=2)
        self.btn_iniciar.clicked.connect(self.iniciar)
        self.btn_detener.clicked.connect(self.detener)
        self.r_localhost.stateChanged.connect(self.cambiar_ip)

    def inicializar(self):
        actual = os.path.abspath(os.getcwd())
        actual = actual.replace('\\' , '/')
        ruta = actual + '/icono_imagen/madenco logo.png'
        foto = QPixmap(ruta)
        self.lb_logo.setPixmap(foto)
        self.btn_detener.setEnabled(False)
        self.setWindowIcon(QIcon(actual + '/icono_imagen/logo_task.ico'))
        self.nombre_pc = socket.gethostname()
        self.direccion_pc = socket.gethostbyname(self.nombre_pc)
        #print(' nombre = ' + str(self.nombre_pc))
        #print(' ip = ' + str(self.direccion_pc))
        self.txt_host.setText(self.direccion_pc)
        self.txt_puerto.setText('5000')
        self.btn_iniciar.setIcon(QIcon('icono_imagen/start.ico'))
        self.btn_detener.setIcon(QIcon('icono_imagen/stop.ico'))

    def iniciar(self):
        host = self.txt_host.text()
        puerto = self.txt_puerto.text()
        if host != '' and puerto != '':
            try:
                puerto = int(puerto)
                self.servidor = ThreadedServer(MyService, host , port = puerto)
                self.executor.submit(self.iniciar_servidor)
                #print( str(type(self.servidor)))
                #print('SERVIDOR INICIADO EN ' + host +' - ' +str(puerto))
                self.lb_estado.setText('SERVIDOR ACTIVO')
                self.btn_detener.setEnabled(True)
                self.btn_iniciar.setEnabled(False)
            except ValueError:
                QMessageBox.about(self,'ERROR', 'INGRESE SOLO NUMEROS EN EL CAMPO "PUERTO" ')
            except OSError:
                QMessageBox.about(self,'ERROR', 'La direccion ingresada no es valida en el contexto. Se recomienda no modificar la direccion ip, esta debe ser la IPv4 del equipo')
        else:
            QMessageBox.about(self,'ERROR', 'RELLENE LOS CAMPOS ANTES DE INICIAR EL SERVIDOR')

    def detener(self):
        self.executor.submit(self.detener_servidor)
        #print( str(type(self.servidor)))
        self.btn_iniciar.setEnabled(True)
        self.btn_detener.setEnabled(False)
        self.lb_estado.setText('SERVIDOR INACTIVO')

    def iniciar_servidor(self):
        if self.servidor:
            self.servidor.start()
    def detener_servidor(self):
        if self.servidor:
            self.servidor.close()
    #v5.4 usada para testeo
    def cambiar_ip(self):
        if self.r_localhost.isChecked():
            self.txt_host.setText('127.0.0.1')
        else:
            self.txt_host.setText(str(self.direccion_pc))

    def closeEvent(self, event):
        self.detener_servidor()
        event.accept()

    
if __name__ == "__main__":

    '''host = '192.168.56.1' # cambiar por ip local para ejecutar localmente.
    puerto = 5000
    server = ThreadedServer(MyService, host , port = puerto)
    print('server 192.168.56.1 iniciado en el puerto 5000')
    server.start()'''
    app = QApplication(sys.argv)
    myappid = 'madenco.servidor' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid) 
    server = Servidor()
    server.show()
    sys.exit(app.exec_())