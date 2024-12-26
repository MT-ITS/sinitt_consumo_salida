Este codigo sirve para recibir la información publicada desde el SINITT. Para esto el Ministerio de Transporte creo un componente servidor que 
las entidades o actores que van a utilizar le SINITT pueden utilizar y cuyo codigo esta bajo la carpeta: servidor_recepcion_datos. Para instalar este componente descargue 
el carpeta instale las librerias mediante el comando:

pip install -r requirements 

Para ejecutar este código también se entrega un docker que puede ser utilizado. 

En ambos casos el actor debe complementar el código para guardar o tratar los mensajes que llegan. En el archivo main.py se dejan indicados los puntos donde debe realizar los cambios por programación para hacer estos tratamientos.   

Igualmente se entrega dos scripts en python:
- (subscribe.py), uno para subscribirse a un contenido que publica el SINITT.
- (unsubscribe.py), uno para des-subscribirse de un contenido que publica el SINITT.
