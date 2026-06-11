import socket
import threading

class Cliente:
    name = ""
    conn = None
    addr = None


def clientthread(conn, addr):
    conn.send(bytes("Bienvenido\nEste bot de ayuda puede auxiliarlo con:\n" #Volver a este es con 0
                    "1.-Manual de usuario\n"
                    "2.-Reportar fallas\n"
                    "3.-Terminos y condiciones\n"
                    "4.-Quejas y sugerencias\n"
                    "5.-Consultas acerca de facturación\n"
                    "Para seleccionar una opcion escriba el numero de la opcion deseada\n\n", 'utf-8'))
    while True:
            message = conn.recv(BUFFER_SIZE)
            if message:
                print(f"<{addr[0]}> {message}")
                msg = message.decode('utf-8')
                if msg == '1': #Manual de usuario, para volver usar 1
                    msg_send = ("----------------------------------------------------------------------------------\n"
                                "A continuación se presenta el manual de usuario\n"
                                "Por favor lea detenidamente el funcionamiento de todos los aditamentos incluidos\n"
                                "Todos los procesos descritos a continuacion se realizan mediante la interfaz\n"
                                "a la que puede acceder desde el movil, o bien puede elegir entre los modos\n"
                                "prediseñados por el fabricante.\n"
                                "La casa inteligente se compone de los siguientes componentes:\n"
                                "✯ Puertas y ventanas automaticas\n"
                                "✯ Sistema de iluminacion domestica\n"
                                "✯ Sistema de riego automatico\n"
                                "✯ Sensores de humedad y temperatura\n"
                                "✯ Sistema de reconocimiento facial\n"
                                "Para leer a detalle el funcionamiento de un componente eliga la opción indicada:\n"
                                "12.-Puertas y ventanas automaticas\n"
                                "13.-Sistema de iluminación domestica\n"
                                "14.-Sistema de riego automatico\n"
                                "15.-Sensores de humedad y/o temperatura\n"
                                "16.-Sistema de reconocimiento facial\n"
                                "0.-Volver al menu principal\n\n")
                    broadcast(msg_send,conn)
                elif msg == '2': #fallas tecnicas, volver a este es 2
                    msg_send = ("----------------------------------------------------------------------------------\n"
                                "Lamentamos las fallas técnicas que se presentan en nuestro servicio\n"
                                "Por favor seleccione la opción más cercana al problema actual\n"
                                "6.-Ventanas presentan fallas\n"
                                "7.-Puertas presentan fallas\n"
                                "8.-Sistema de iluminación presenta fallas\n"
                                "9.-Sistema de reconocimiento facial presenta fallas\n"
                                "10.-Sistema de riego presenta fallas\n"
                                "11.-Sensor(es) presenta fallas\n"
                                "0.-Volver al menu principal\n\n")
                    broadcast(msg_send,conn)
                elif msg == '3': #Terminos y condiciones, volver a este es 3
                    msg_send = ("----------------------------------------------------------------------------------\n"
                                "TERMINOS Y CONDICIONES DEL SERVICIO\n"
                                "Bienvenido a nuestro servicio de casa inteligente\n"
                                "Nuestro servicio se caracteriza por la mayor calidad en el mercado, dando especial\n"
                                "atención a las necesidades particulares de todos y cada uno de nuestros clientes.\n"
                                "Por favor lea detenidamente los terminos y condiciones aqui especificados antes \n"
                                "de contratar nuestros servicios\n"
                                "17.-Propiedad intelectual\n"
                                "18.-Privacidad y seguridad\n"
                                "19.-Garantia del servicio\n"
                                "0.-Volver al menu principal\n\n")
                    broadcast(msg_send,conn)
                elif msg == '4': #Quejas y sugerencias
                    msg_send = ("----------------------------------------------------------------------------------\n"
                                "Nuestro buzon de quejas/sugerencias recopila y almacena toda la información\n"
                                "recopilada para ser analizada por nuestro sistema de atención al cliente.\n"
                                "Utilizamos esta información para la mejora continua de nuestro servicio\n"
                                "--Al continuar este proceso acepata los terminos y condiciones--\n"
                                "Por favor escriba a continuación su comentario acerca de nuestro servicio.\n"
                                "Para volver al menu principal escriba '0'\n")
                    broadcast(msg_send,conn)
                elif msg == '5': #Consulatas de facturación
                    msg_send = ("----------------------------------------------------------------------------------\n"
                                "Facturación\n"
                                "Nuestro sistema de cobro se compone por los siguientes aspectos:\n"
                                "✯ Tarifa base segun el numero de ventans y puertas instaladas\n"
                                "✯ Tarifa base segun el sistema de iluminación domestico\n"
                                "✯ Impuestos al valor agregado\n"
                                "El ciclo de facturación y cobro se realiza de forma trimestral.\n"
                                "En caso de incurrir en falta o retraso de pago nos reservamos el derecho de\n"
                                "suspender el servicio indefinidamente hasta recobrar la normalidad de la tarifa.\n"
                                "DISCLAIMER-Para la cancelación de servicio comunicarse con atención al cliente\n"
                                "Para volver al menu principal escriba '0'\n")
                    broadcast(msg_send,conn)
                    #de 6 a 11 son fallas tecnicas
                elif msg == '6': #Ventanas
                    msg_send = ("Su reporte ha sido enviado\n")
                    broadcast(msg_send,conn)
                elif msg == '7': #Puertas
                    msg_send = ("Su reporte ha sido enviado\n")
                    broadcast(msg_send,conn)
                elif msg == '8': #Iluminacion
                    msg_send = ("Su reporte ha sido enviado\n")
                    broadcast(msg_send,conn)
                elif msg == '9': #Sistema de reconocimiento facial
                    msg_send = ("Su reporte ha sido enviado\n")
                    broadcast(msg_send,conn)
                elif msg == '10': #Sisitema de riego
                    msg_send = ("Su reporte ha sido enviado\n")
                    broadcast(msg_send,conn)
                elif msg == '11':  #sensores
                    msg_send = ("Su reporte ha sido enviado\n")
                    broadcast(msg_send, conn)
                    #12 a 16 son manual de usuario, detallarlo bn
                elif msg == '12':  #Puertas y ventanas automaticas
                    msg_send = ("Para un correcto uso de las puertas y/o ventanas leer esta explicacion.\n"
                                "Nuestros productos son diseñados con el fin de necesitar poco mantenimiento\n"
                                "es necesario que el usuario siga las siguientes instrucciones para\n"
                                "alargar la vida util de nuestros productos:\n"
                                "✯ Evitar manipular el cableado electrico\n"
                                "✯ Realizar limpieza no invasiva para eliminar polvo y otras impurezas\n"
                                "✯ Evitar obstrucciones en el mecanismo encargado de mover la puerta/ventana\n"
                                "El funcionamiento de apertura/cierre de las puertas y ventas se detalla como sigue:\n"
                                "La herramienta principal para el usuario es la interfaz diseñada por nosotros\n"
                                "misma a la que puede acceder mediante la aplicacion diseñada para moviles,\n"
                                "donde elige la puerta exacta que quiere abrir y/o cerrar.")
                    broadcast(msg_send, conn)
                elif msg == '13':  #Iluminacion domestica
                    msg_send = ("Ha seleccionado 11\n")
                    broadcast(msg_send, conn)
                elif msg == '14':  #Riego automatico
                    msg_send = ("Ha seleccionado 11\n")
                    broadcast(msg_send, conn)
                elif msg == '15':  #sensores humedad y/o temp
                    msg_send = ("Ha seleccionado 11\n")
                    broadcast(msg_send, conn)
                elif msg == '16':  #Reconocimiento facual
                    msg_send = ("Ha seleccionado 11\n")
                    broadcast(msg_send, conn)
                elif msg == '17':  #Propiedad intelectual TEXT
                    msg_send = ("Todos los servicios relacionados con la casa inteligente estan\n"
                                "protegidos con las respectivas leyes de derechos de autor vigentes en el pais\n"
                                "esto incluye cualquier software y hardware parte de las instalaciones\n"
                                "Queda estrictamente prohibido copiar total o parcialmente nuestros productos\n"
                                "Para volver a Terminos y condiciones presione '3'\n")
                    broadcast(msg_send, conn)
                elif msg == '18':  #Privacidad y seguridad TEXT
                    msg_send = ("Todos los datos recopilados estan protegidos y son de uso exlcusivo para\n"
                                "estadisticas de nuestra organizacion; nos comprometemos a proteger su \n"
                                "privacidad segun la normatividad vigente.\n"
                                "Para volver a Terminos y condiciones presione '3'\n")
                    broadcast(msg_send, conn)
                elif msg == '19':  #Garantia de serv TEXT
                    msg_send = ("Información de la garantia vigente\n"
                                "Nuestra organización se compromete a instalar productos libres de cualquier\n"
                                "de cualquier defecto, ya sea en hardware o software.\n"
                                "La presente garantia cubre los siguientes apartados:\n"
                                "✯ Fallos bajo condiciones normales de uso\n"
                                "✯ Defectos de fabrica\n"
                                "✯ Fallo de mano de obra durante la instalación\n"
                                "Es importante mencionar que la presente garantia no cubre los siguientes casos:\n"
                                "✯ Modificaciones por parte del usuario\n"
                                "✯ Daños causados por condiciones climaticas adversas\n"
                                "✯ Daños causados por accidentes/negligencias\n"
                                "Para volver a Terminos y condiciones presione 3\n")
                    broadcast(msg_send, conn)
                elif msg == '0': #Esta es la opcion para volver al MENU PRINCIAPL, agregar a cada submenu
                    conn.send(bytes("----------------------------------------------------------------------------------\n"
                                    "Bienvenido\nEste bot de ayuda puede auxiliarlo con:\n"
                                    "1.-Manual de usuario\n"
                                    "2.-Reportar fallas\n"
                                    "3.-Terminos y condiciones\n"
                                    "4.-Quejas y sugerencias\n"
                                    "5.-Consultas acerca de facturación\n"
                                    "Para seleccionar una opcion escriba el numero de la opcion deseada\n\n", 'utf-8'))

def broadcast(message,conn):
    conn.send(bytes(message, 'utf-8'))

if __name__ == "__main__":
    host = "0.0.0.0"
    port = 5001 #cambiar a 5001 para el server,65535 es local
    BUFFER_SIZE = 1024
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(100)  # Escuchamos hasta 100 clientes
    print(f"Escuchando conexiones en: {(host, port)}")
    try:
        while True:
            conn, addr = server.accept()
            nuevo_cliente = Cliente()
            nuevo_cliente.conn = conn
            nuevo_cliente.addr = addr
            #list_of_clients.append(conn)  # Agregamos a la lista de clientes
            print(f"Cliente conectado: {addr}")
            threading.Thread(target=clientthread, args=(conn, addr)).start()
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        conn.close()
        server.close()
    print("Conexión terminada.")

