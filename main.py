

import sys
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QDialog, QGraphicsDropShadowEffect
import cv2
import random
import time
import pyfirmata
import numpy as np
import platform
from datetime import datetime, time as dt_time  # Importar datetime y time desde el módulo datetime
from ui_splash_screen import Ui_SplashScreen
from GUIhouse import Ui_GUIhouse
import socket


# GLOBALS

# Inicialización global de la placa Arduino y pines
board1 = None
board2 = None
pins1 = {}
pins2 = {}
#servo_garage=None
counter = 0
jumper = 10


class ThreadSocket(QThread):
    global connected
    signal_message = pyqtSignal(str)
    def __init__(self, host, port):
        global connected
        super().__init__()
        server.connect((host, port))
        connected = True

    def run(self):
        global connected
        try:
            while connected:
                message = server.recv(BUFFER_SIZE)
                if message:
                    self.signal_message.emit(message.decode("utf-8"))
                else:
                    self.signal_message.emit("<!!disconected!!>")
                    break

        except ...:
            self.signal_message.emit("<!!error!!>")
        finally:
            server.close()
            connected = False

    def stop(self):
        global connected
        connected = False
        self.wait()

class MiApp(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MiApp, self).__init__(*args, **kwargs)
        self.ui = Ui_GUIhouse()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.animation = QPropertyAnimation(self, b'windowOpacity')
        self.animation.setDuration(1000)
        self.do_show()
        # Inicializar Arduino
        self.initArduino()
        self.Automatico()
        #Modificaciones inicio
        self.coneccion = None
        self.ui.SendGeneral.clicked.connect(self.mensaje_saliente)
        # Create a QTimer
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_time_and_date)
        self.timer.start(1000)  # Update every second


        # mensaje de entrada
        self.ui.stackedWidget.setCurrentIndex(6)
        self.ui.msg_entrada.setWordWrap(True)
        self.mensaje_de_entrada()

        # Conexión de botones laterales con ventanas
        self.ui.bt_estado_actual.clicked.connect(self.cambiar_a_estadoActual)
        self.ui.bt_estado_actual_2.clicked.connect(self.cambiar_a_estadoActual)
        self.ui.bt_focos.clicked.connect(self.cambiar_a_focos)
        self.ui.bt_focos_2.clicked.connect(self.cambiar_a_focos)
        self.ui.bt_ventanas.clicked.connect(self.cambiar_a_ventanas)
        self.ui.bt_ventanas_2.clicked.connect(self.cambiar_a_ventanas)
        self.ui.bt_puertas.clicked.connect(self.cambiar_a_puertas)
        self.ui.bt_puertas_2.clicked.connect(self.cambiar_a_puertas)
        self.ui.bt_modos.clicked.connect(self.cambiar_a_modos)
        self.ui.bt_modos_2.clicked.connect(self.cambiar_a_modos)
        self.ui.bt_soporte.clicked.connect(self.cambiar_a_soporte)
        self.ui.bt_soporte_2.clicked.connect(self.cambiar_a_soporte)

        # Diccionario de los grupos de focos
        foco_grupos = {
            'exteriores': {
                'checkbox': self.ui.ch_on_off_exteriores,
                'indices': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
                'pin': 'd:2:o'
            },
            'cocina': {
                'checkbox': self.ui.ch_on_off_cocina,
                'indices': [17, 18, 19],
                'pin': 'd:3:o'
            },
            'sala': {
                'checkbox': self.ui.ch_on_off_sala,
                'indices': [20, 21, 22],
                'pin': 'd:4:o'
            },
            'cuartoPrincipal': {
                'checkbox': self.ui.ch_on_off_cuartoPrincipal,
                'indices': [23, 24],
                'pin': 'd:5:o'
            },
            'jardin': {
                'checkbox': self.ui.ch_on_off_jardin,
                'indices': [25, 26],
                'pin': 'd:6:o'
            },
            'cuartoLavado': {
                'checkbox': self.ui.ch_on_off_cuartoLavado,
                'indices': [27, 28],
                'pin': 'd:7:o'
            },
            'garage': {
                'checkbox': self.ui.ch_on_off_garage,
                'indices': [29],
                'pin': 'd:8:o'
            }
        }

        # Inicializar los estados de los focos
        self.focos = {}

        # Asignar focos y sus atributos
        for grupo, info in foco_grupos.items():
            checkbox = info['checkbox']
            for idx in info['indices']:
                self.focos[idx] = {
                    'checkbox': checkbox,
                    'label': getattr(self.ui, f'img_foco_{idx}'),
                    'encendido': False,
                    'pin': info['pin']
                }

        # Conectar los botones a la función toggle_foco
        for grupo, info in foco_grupos.items():
            checkbox = info['checkbox']
            checkbox.clicked.connect(lambda _, indices=info['indices'], pin=info['pin']: self.toggle_grupo(indices, pin,board1))

        for i in self.focos:
            self.actualizar_imagen_foco(i)

        # Inicializar los estados de las ventanas
        self.ventanas = {
            1: {'checkbox': self.ui.ch_open_close, 'label': self.ui.img_ventana, 'abierta': False,
                'servo': board2.get_pin('d:7:s')},
            2: {'checkbox': self.ui.ch_open_close_2, 'label': self.ui.img_ventana_2, 'abierta': False,
                'servo': board2.get_pin('d:8:s')},
            3: {'checkbox': self.ui.ch_open_close_3, 'label': self.ui.img_ventana_3, 'abierta': False,
                'servo': board2.get_pin('d:9:s')}
        }

        # Conectar los botones a la función toggle_ventana
        for i in self.ventanas:
            self.ventanas[i]['checkbox'].clicked.connect(lambda _, idx=i: self.toggle_ventana(idx))
            self.actualizar_imagen_ventana(i)

        # Inicializar los estados de las puertas
        self.puertas = {
            1: {'checkbox': self.ui.ch_puerta_1, 'label': self.ui.img_puerta_1, 'abierta': False,
                'servo': board2.get_pin('d:2:s')},
            2: {'checkbox': self.ui.ch_puerta_2, 'label': self.ui.img_puerta_2, 'abierta': False,
                'servo': board2.get_pin('d:3:s')},
            3: {'checkbox': self.ui.ch_puerta_3, 'label': self.ui.img_puerta_3, 'abierta': False,
                'servo': board2.get_pin('d:4:s')},
            4: {'checkbox': self.ui.ch_puerta_4, 'label': self.ui.img_puerta_4, 'abierta': False,
                'servo': board2.get_pin('d:5:s')},
            5: {'checkbox': self.ui.ch_puerta_5, 'label': self.ui.img_puerta_5, 'abierta': False,
                'servo': board2.get_pin('d:6:s')}
        }

        # Conectar los botones a la función toggle_puerta
        for i in self.puertas:
            self.puertas[i]['checkbox'].clicked.connect(lambda _, idx=i: self.toggle_puerta(idx))
            self.actualizar_imagen_puerta(i)

        # Inicializar estado garage
        self.garage = {
            1: {'checkbox': self.ui.ch_garage, 'label': self.ui.img_garage, 'abierta': False,
                'servo': board2.get_pin('d:10:s')},
        }

        # Conectar puerta garage
        self.garage[1]['checkbox'].clicked.connect(lambda _, :self.toggle_garage())
        self.actualizar_imagen_garage()


        # Actualizar contadores de puertas, focos y ventanas
        self.actualizar_contador_puertas()
        self.actualizar_contador_focos()
        self.actualizar_contador_ventanas()
        # modos
        self.ui.ch_modo_on_off_salirCasa.clicked.connect(self.salir_de_casa)
        self.ui.ch_modo_on_off_incendio.clicked.connect(self.incendios)
######################################
    def mensaje_saliente(self): #Agregar
        str = self.ui.TextGeneral.text()
        if str != "" and connected:
            server.send(bytes(str,'utf-8'))
            self.ui.TextGeneral.clear()
            self.mensage_entrante("<Tú> " + str + '\n')

    def keyPressEvent(self, event: QKeyEvent) -> None:  # Agregar
        # Manejar los eventos de teclado para la calculadora
        super().keyPressEvent(event)
        key = event.key()
        if key == Qt.Key.Key_Enter or key == Qt.Key.Key_Return:
            self.mensaje_saliente()


    def Automatico(self): #Agregar
        NoServ = "3.136.134.23" #cambiar a 3.136.134.23 para el servidor, 127.0.0.1 es local
        user = ""
        port = 5001 #cambiar a 5001 para el server, 65535 es local
        self.coneccion = ThreadSocket(NoServ, int(port))
        self.coneccion.signal_message.connect(self.mensage_entrante)
        self.coneccion.start()
        self.setWindowTitle("Messenger - Conectado")

    def mensage_entrante(self, mensaje): #Agregar
        self.ui.ScreenGeneral.setPlainText(self.ui.ScreenGeneral.toPlainText() + mensaje)

    def incendios(self):
            # Enciende el LED en el pin 12
        pins1['d:12:o'].write(1)
        # Enciende el buzzer en el pin 11
        pins1['d:11:o'].write(1)
        time.sleep(4)
        # Enciende el LED en el pin 12
        pins1['d:12:o'].write(0)
        # Enciende el buzzer en el pin 11
        pins1['d:11:o'].write(0)


    def salir_de_casa(self):
        # Apagar todas las luces interiores si están encendidas
        for idx in [23, 24]:  # Ejemplo de índices de luces interiores (cuartoPrincipal)
            if self.focos[idx]['encendido']:
                self.focos[idx]['encendido'] = False


                self.actualizar_imagen_foco(idx)
                self.focos[idx]['checkbox'].setChecked(False)  # Marcar el checkbox correspondiente
        now = datetime.now().time()  # Obtener la hora actual
        start_time = dt_time(3,)  # Hora de inicio (17:00)
        end_time = dt_time(5, 0)  # Hora de fin (18:00)
        # Verificar si la hora actual está dentro del rango especificado
        print(now)

        if start_time <= now <= end_time:
            # Encender luces exteriores si no están encendidas
            for idx in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
                        16]:  # Ejemplo de índices de luces exteriores
                if not self.focos[idx]['encendido']:
                    self.focos[idx]['encendido'] = True
                    self.actualizar_imagen_foco(idx)
        else:
            # Apagar luces exteriores si están encendidas
            for idx in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
                        16]:  # Ejemplo de índices de luces exteriores
                if self.focos[idx]['encendido']:
                    self.focos[idx]['encendido'] = False
                    self.actualizar_imagen_foco(idx)

        # Cerrar todas las puertas abiertas
        for idx in [1, 2, 3, 4, 5]:  # Ejemplo de índices de puertas
            if self.puertas[idx]['abierta']:
                self.puertas[idx]['abierta'] = False
                self.actualizar_imagen_puerta(idx)
                self.puertas[idx]['servo'].write(0)  # Cerrar la puerta
                self.puertas[idx]['checkbox'].setChecked(False)

        # Cerrar todas las ventanas abiertas
        for idx in [1, 2, 3]:  # Ejemplo de índices de ventanas
            if self.ventanas[idx]['abierta']:
                self.ventanas[idx]['abierta'] = False
                self.actualizar_imagen_ventana(idx)
                self.ventanas[idx]['servo'].write(0)  # Cerrar la ventana
                self.ventanas[idx]['checkbox'].setChecked(False)

        # Actualizar contadores de puertas y ventanas
        self.actualizar_contador_puertas()
        self.actualizar_contador_focos()
        self.actualizar_contador_ventanas()
    def toggle_grupo(self, indices,pin,board):
        # Cambiar el estado de todos los focos en el grupo
        estado = not self.focos[indices[0]]['encendido']
        for idx in indices:
            self.focos[idx]['encendido'] = estado
            self.actualizar_imagen_foco(idx)

        # Cambiar el estado del pin del Arduino
        pins1[pin].write(1 if estado else 0)

        # Actualizar contadores de focos
        self.actualizar_contador_focos()
    def toggle_ventana(self, idx):
        # Cambiar el estado de la ventana
        self.ventanas[idx]['abierta'] = not self.ventanas[idx]['abierta']
        self.actualizar_imagen_ventana(idx)

        # Controlar el servo asociado
        if self.ventanas[idx]['abierta']:
            self.ventanas[idx]['servo'].write(90)  # Ángulo de apertura del servo
        else:
            self.ventanas[idx]['servo'].write(0)  # Ángulo de cierre del servo

        # Actualizar contadores de ventanas
        self.actualizar_contador_ventanas()

    def toggle_puerta(self, idx):
        # Cambiar el estado de la puerta
        self.puertas[idx]['abierta'] = not self.puertas[idx]['abierta']
        self.actualizar_imagen_puerta(idx)

        # Controlar el servo asociado
        if self.puertas[idx]['abierta']:
            self.puertas[idx]['servo'].write(90)  # Ángulo de apertura del servo
        else:
            self.puertas[idx]['servo'].write(0)  # Ángulo de cierre del servo

        # Actualizar contadores de puertas
        self.actualizar_contador_puertas()

    def toggle_garage(self):
       # # Cambiar el estado del garage
       # Cambiar el estado de la puerta
       self.garage[1]['abierta'] = not self.garage[1]['abierta']
       self.actualizar_imagen_garage()

       # Controlar el servo asociado
       if self.garage[1]['abierta']:
           self.garage[1]['servo'].write(90)  # Ángulo de apertura del servo
       else:
           self.garage[1]['servo'].write(0)  # Ángulo de cierre del servo
       self.actualizar_imagen_garage()

    def actualizar_imagen_foco(self, idx):
        # Actualizar la imagen del QLabel según el estado del foco
        imagen_path = 'C:/Users/hugoe/Desktop/Progra/proyectoFinal/icons/focoON.png' if \
        self.focos[idx][
            'encendido'] else 'C:/Users/hugoe/Desktop/Progra/proyectoFinal/icons/focoOFF.png'

        pixmap = QPixmap(imagen_path)
        # Escalar la imagen para que se ajuste al QLabel (opcional)
        pixmap = pixmap.scaled(self.focos[idx]['label'].size(), Qt.AspectRatioMode.KeepAspectRatio)
        self.focos[idx]['label'].setPixmap(pixmap)

    def actualizar_imagen_ventana(self, idx):
        # Actualizar la imagen del QLabel según el estado de la ventana
        if self.ventanas[idx]['abierta']:
            imagen_path = 'C:/Users/hugoe/Desktop/Progra/proyectoFinal/icons/ventanaAbierta.png'
        else:
            imagen_path = 'C:/Users/hugoe/Desktop/Progra/proyectoFinal/icons/ventanaCerrada.png'

        pixmap = QPixmap(imagen_path)
        pixmap = pixmap.scaled(self.ventanas[idx]['label'].size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        self.ventanas[idx]['label'].setPixmap(pixmap)

    def actualizar_imagen_puerta(self, idx):
        # Actualizar la imagen del QLabel según el estado de la puerta
        if self.puertas[idx]['abierta']:
            imagen_path = 'C:/Users/hugoe/Desktop/Progra/proyectoFinal/icons/puertaAbierta.png'
        else:
            imagen_path = 'C:/Users/hugoe/Desktop/Progra/proyectoFinal/icons/puertaCerrada.png'

        pixmap = QPixmap(imagen_path)
        pixmap = pixmap.scaled(self.puertas[idx]['label'].size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        self.puertas[idx]['label'].setPixmap(pixmap)

    def actualizar_imagen_garage(self):
        #Actualizar la imagen del QLabel según el estado del garage
        if self.garage[1]['abierta']:
            imagen_path = 'C:/Users/hugoe/Desktop/Progra/proyectoFinal/icons/garageAbierto.png'
            self.ui.estado_garage.setText("Abierto")
        else:
            imagen_path = 'C:/Users/hugoe/Desktop/Progra/proyectoFinal/icons/garageCerrado.png'
            self.ui.estado_garage.setText("Cerrado")

        pixmap = QPixmap(imagen_path)
        pixmap = pixmap.scaled(self.garage[1]['label'].size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        self.garage[1]['label'].setPixmap(pixmap)

    def actualizar_contador_focos(self):
        num_encendidos = sum(1 for f in self.focos.values() if f['encendido'])
        num_apagados = len(self.focos) - num_encendidos
        self.ui.num_focos_on.setText(f"{num_encendidos} Encendidos")
        self.ui.num_focos_off.setText(f"{num_apagados} Apagados")

    def actualizar_contador_puertas(self):
        num_abiertas = sum(1 for p in self.puertas.values() if p['abierta'])
        num_cerradas = len(self.puertas) - num_abiertas
        self.ui.num_puertas_on.setText(f"{num_abiertas} Abiertas")
        self.ui.num_puertas_off.setText(f"{num_cerradas} Cerradas")

    def actualizar_contador_ventanas(self):
        num_abiertas = sum(1 for v in self.ventanas.values() if v['abierta'])
        num_cerradas = len(self.ventanas) - num_abiertas
        self.ui.num_ventanas_on.setText(f"{num_abiertas} Abiertas")
        self.ui.num_ventanas_off.setText(f"{num_cerradas} Cerradas")
    def do_show(self):
        self.animation.stop()
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

    def update_time_and_date(self):
        current_time = QTime.currentTime().toString('hh:mm:ss')
        current_date = QDate.currentDate().toString('yyyy/MM/dd')
        self.ui.hora.setText(current_time)
        self.ui.fecha.setText(current_date)
        self.ui.hora_2.setText(current_time)
        self.ui.fecha_2.setText(current_date)
        self.ui.hora_3.setText(current_time)
        self.ui.fecha_3.setText(current_date)
        self.ui.hora_4.setText(current_time)
        self.ui.fecha_4.setText(current_date)
        self.ui.hora_5.setText(current_time)
        self.ui.fecha_5.setText(current_date)
        self.ui.hora_6.setText(current_time)
        self.ui.fecha_6.setText(current_date)

    def mensaje_de_entrada(self):
        tips = [
            "Programa tus luces para que se apaguen automáticamente. ¡Incluso los fantasmas necesitan oscuridad!"
            "Revisa regularmente los motores de puertas y ventanas para mayor seguridad.",
            "Utiliza el modo 'No molestar' para evitar interrupciones durante la noche.",
            "Mantén actualizada la aplicación para disfrutar de las últimas funciones.",
            "¿Sabías que tu casa inteligente puede ser más inteligente que tú? ¡Mantente al día!",
            "¿Perdiste las llaves? No te preocupes, ¡tu casa inteligente te tiene cubierto (pero igual revisa tus bolsillos)!",
            "Revisa las cámaras de seguridad. ¡Nunca sabes cuándo un gato vecino puede estar planeando algo!",
            "Programa las cortinas para abrirse al amanecer. ¡Es hora de saludar al sol con estilo!"
        ]
        tip_del_dia = random.choice(tips)
        mensaje = (
            "¡Bienvenido, Diego!\n"
            "Nos alegra tenerte de vuelta.\n\n"
            "Tu hogar, tu confort, tu control.\n\n"
            "Tip del día:\n"
            f"{tip_del_dia}"
        )

        self.ui.msg_entrada.setText(mensaje)

    def cambiar_a_estadoActual(self):
        self.ui.stackedWidget.setCurrentIndex(0)

    def cambiar_a_focos(self):
        self.ui.stackedWidget.setCurrentIndex(1)

    def cambiar_a_ventanas(self):
        self.ui.stackedWidget.setCurrentIndex(2)

    def cambiar_a_puertas(self):
        self.ui.stackedWidget.setCurrentIndex(3)

    def cambiar_a_modos(self):
        self.ui.stackedWidget.setCurrentIndex(4)

    def cambiar_a_soporte(self):
        self.ui.stackedWidget.setCurrentIndex(5)


    def initArduino(self):
        global board1
        global board2
        global pins1
        global pins2

        # Inicialización de la placa Arduino en COM7
        board1 = pyfirmata.Arduino('COM11')
        it1 = pyfirmata.util.Iterator(board1)
        it1.start()

        # Inicialización de los pines del Arduino en COM7
        pin_names1 = ['d:2:o', 'd:3:o', 'd:4:o', 'd:5:o', 'd:6:o', 'd:7:o', 'd:8:o','d:12:o','d:11:o',]
        for pin_name in pin_names1:
            pins1[pin_name] = board1.get_pin(pin_name)

        # Inicialización de la placa Arduino en COM10
        board2 = pyfirmata.Arduino('COM8')
        it2 = pyfirmata.util.Iterator(board2)
        it2.start()


# ==> SPLASHSCREEN WINDOW
class SplashScreen(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_SplashScreen()
        self.ui.setupUi(self)

        # ==> SET INITIAL PROGRESS BAR TO (0) ZERO
        self.progressBarValue(0)

        # ==> REMOVE STANDARD TITLE BAR
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)  # Remove title bar
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)  # Set background to transparent

        # ==> APPLY DROP SHADOW EFFECT
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 120))
        self.ui.circularBg.setGraphicsEffect(self.shadow)

        # QTIMER ==> START
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.progress)
        # TIMER IN MILLISECONDS
        self.timer.start(15)

        # SHOW ==> MAIN WINDOW
        self.show()
        ## ==> END ##

    # DEF TO LOADING
    def progress(self):
        global counter
        global jumper
        value = counter

        # HTML TEXT PERCENTAGE
        htmlText = """<p><span style=" font-size:68pt;">{VALUE}</span><span style=" font-size:58pt; vertical-align:super;">%</span></p>"""

        # REPLACE VALUE
        newHtml = htmlText.replace("{VALUE}", str(jumper))

        if (value > jumper):
            # APPLY NEW PERCENTAGE TEXT
            self.ui.labelPercentage.setText(newHtml)
            jumper += 1

        # SET VALUE TO PROGRESS BAR
        # fix max value error if > than 100
        if value >= 100:
            value = 1.000
        self.progressBarValue(value)

        # CLOSE SPLASH SCREEN AND OPEN APP
        if counter > 100:
            # STOP TIMER
            self.timer.stop()

            # Inicializar Arduino
            self.main = MiApp()
            self.main.show()

            # CLOSE SPLASH SCREEN
            self.close()

        # INCREASE COUNTER
        counter += 0.5

    # DEF PROGRESS BAR VALUE
    ########################################################################
    def progressBarValue(self, value):
        # PROGRESSBAR STYLESHEET BASE
        styleSheet = """
        QFrame{
        	border-radius: 150px;
        	background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:{STOP_1} rgba(255, 0, 127, 0), stop:{STOP_2} rgba(85, 170, 255, 255));
        }
        """

        # GET PROGRESS BAR VALUE, CONVERT TO FLOAT AND INVERT VALUES
        # stop works of 1.000 to 0.000
        progress = (100 - value) / 100.0

        # GET NEW VALUES
        stop_1 = str(progress - 0.001)
        stop_2 = str(progress)

        # SET VALUES TO NEW STYLESHEET
        newStylesheet = styleSheet.replace("{STOP_1}", stop_1).replace("{STOP_2}", stop_2)

        # APPLY STYLESHEET WITH NEW VALUES
        self.ui.circularProgress.setStyleSheet(newStylesheet)


if __name__ == "__main__":
    BUFFER_SIZE = 1024  # Usamos un número pequeño para tener una respuesta rápida
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connected = False
    app = QApplication(sys.argv)
    window = SplashScreen()
    window.show()  # Mostrar la ventana
    #uxiliar1= MiApp()
    #window.Automatico()
    #auxiliar1.Automatico()
    sys.exit(app.exec())


