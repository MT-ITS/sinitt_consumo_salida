<h1 align="center"> Componente de Consumo de Datos desde el SINITT.  </h1>

<h2> Descripción del Proyecto </h2>
Este codigo sirve para recibir la información publicada desde el SINITT. Para esto el Ministerio de Transporte de Colombia creo un componente que opera en modo servidor, mediante el cual las entidades o actores que van a utilizar le SINITT pueden recibir mensajes en DATEX_II mediante el protocolo publish/subcribe.

La siguiente gráfica muestra las interrelaciones definidas para el uso del componente:


<h2>Instalación</h2>h2>
La entidad que desee utilizar este componente para comunicación con el SINITT deberá:

1. Descargar el código  
2. ubicarse en la la carpeta servidor_recepcion_datos
3. Instalar las librerias mediante el comando:

pip install -r requirements 

Para ejecutar este código también se entrega un docker que puede ser utilizado y cuyo Dockerfile se encuentra en la carpeta: servidor_recepcion_datos. 

<h2>Utilización</h2>
Sin importar si la entidad utiliza el código de forma directa o mediante Docker, la persona utilizando el código debe complementarlo para guardar o tratar los mensajes que llegan. En el archivo main.py (dentro de la carpeta /src) se dejan indicados los puntos donde debe realizar los cambios por programación para hacer estos tratamientos.   

Igualmente se entrega dos scripts en python:
- (subscribe.py), uno para subscribirse a un contenido que publica el SINITT.
- (unsubscribe.py), uno para des-subscribirse de un contenido que publica el SINITT.
