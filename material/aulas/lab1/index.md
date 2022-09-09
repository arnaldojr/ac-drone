## O que esse vamos ver neste lab?

- Decolando sem sair do chão
    - Configuração da infraestrutura
        - Boot do SSD no notebook
        - clone do repositório
        - Configurações iniciais com o drone
    - Conexão entre PC e Drone
        - Ajustando a conexão entre o drone e o notebook
        - Analisando tópicos, nodes e imagem
    - Primeiro projeto
        - Entendo o código Python/ROS
        - Rodando o código no Drone
- Desafio1
    - chegou a hora de criar asas e voar! 
    
 
## Configuração da Infraestrura

### Boot do SSD

Vamos utilizar o SSD do 3°semestre de engenharia de computação para nossa atividade. 

Se você possui o SSD do 3°sem. faça o boot no seu PC. Caso não tenha, não tem problema, vamos emprestar um SSD para usar durante a aula.

!!! exercise
    Faça o Boot do SSD no seu PC, caso tenha dificuldades peça ajuda.
    O usuário e senha padrão do SSD é:
    user: borg
    senha: fl1pfl0p 


### Clone do repositório

Vamos utilizar alguns exemplos durante a aula que estão neste repositório, nosso próximo passo clonar esse repositório. 

!!! exercise
    Faça clone deste repositório no diretório ``~/catkin_ws/src`` os comandos para isso estão abaixo, ``abra um terminal e digite``:
    
     ```bash
        cd ~/catkin_ws/src
        git clone https://github.com/arnaldojr/ac-drone
        cd ~/catkin_ws
        catkin_make
     
     ```
    
!!! warning 
        Avalie o log do terminal para saber se deu tudo certo.

## Conexão entre PC e o DRONE

!!! warning
    AINDA NAO É HORA DE DECOLAR, O DRONE DEVE ESTAR SEM HELICES!!


### Como o vou comunicar o meu código do pc com o drone

A topologia que vamos utilizar em nossa aplicação será:

- O drone está configurado como Acess Point, ou seja o drone irá fornecer um ponto de rede Wifi para que outros dispositivos se conectem a ele. 
- O nome desta rede é ````bebop seguida do serial number do drone```
- Vamos conectar o Wifi do nosso computador na rede criada pelo drone do drone. 

!!! warning
    A rede do bebop não tem senha, basta se conectar. Esta rede não possui acesso internet, se precisar usar internet terá que trocar a rede wifi. 


!!! exercise
    - Identifique o serial number do drone que vai usar, tem uma etiqueta colada informando o numero;
    - ligue o drone e conecte seu notebook na rede wifi do drone;
    - Abra um terminal novo e digite:
        - ./bebop.sh
    - A conexão irá acontecer, monitore o log do terminal;
    - Se tudo deu certo, o drone o PC estão conectados e pronto para ser utilizado.
 
!!! warning
    AINDA NAO É HORA DE DECOLAR, O DRONE DEVE ESTAR SEM HELICES!!

## Analisando tópicos, nodes e imagem

Agora que já temos o drone o PC conectados, vamos aprender alguns comandos de ROS:

!!! warning
    No ROS é comum trabalhar com multiplos terminais abertos, cada terminal terá uma função especifica, por essa razão tenha cuidado para não fechar o terminal errado.


Abra um terminal novo, não feche o terminal anterior, vamos explorar os principais comados:

Listar os tópicos do drone:

```bash
rostopic list
```

Abrir a camera do drone:

```bash
rqt_image_view
```

Visualizar a msg de um tópico:

```bash
rostopic echo /debop/odom
```

Decolar(takeoff) o drone:  ***com o drone sem helices, cuidado os motores vão ligar**

```bash
rostopic pub --once /bebop/takeoff std_msgs/Empty
```

Pousar (land) o drone:

```bash
rostopic pub --once /bebop/land std_msgs/Empty
```


Legal, estamos começando a entender como as coisas funcionam. Podemos controlar o drone com os comandos do terminal, mas não é eficiente. Vamos criar um script python para isso. 


!!! progress
    Continuar...


## Entendo o código Python/ROS

Existem algumas formas de criar um script python, Vamos dar uma olhada em um código pronto e análisar a sua estrutura. 

Vamos avaliar o código print_odom.py que está neste repositório na pasta ``exemplos_drone/scripts/print_odom.py``

Este código irá exibir no terminal o valor da odometria (distância percorrida) pelo drone nas coordenadas lineares x, y e z.


```python
#! /usr/bin/env python3
# -*- coding:utf-8 -*-

import rospy 

from std_msgs.msg import Empty
from nav_msgs.msg import Odometry


# Apenas valores para inicializar
x = -1000
y = -1000
z = -1000

def recebeu_leitura(dado):
    """
        Grava nas variáveis x,y,z a posição extraída da odometria
        Atenção: *não coincidem* com o x,y,z locais do drone
    """
    global x
    global y 
    global z 

    x = dado.pose.pose.position.x
    y = dado.pose.pose.position.y
    z = dado.pose.pose.position.z


if __name__=="__main__":

    rospy.init_node("print_odom")

    # Cria um subscriber que chama recebeu_leitura sempre que houver nova odometria
    recebe_odom = rospy.Subscriber("bebop/odom", Odometry , recebeu_leitura)


    try:
        while not rospy.is_shutdown():
            ## Código principal
            print("x {} y {} z {}".format(x, y, z))
            rospy.sleep(2)

    except rospy.ROSInterruptException:
        rospy.sleep(1.0)
```

Vamos avaliar o código por partes.

Começamos informando que vamos usar python3 no nosso código e que realizamos o importe das bibliotecas da ROS e da ROS Msg para compreender o formato das mensagens que vamos utilizar. Esses importes variam conforme o tópico que vamos utilizar

```python
#! /usr/bin/env python3
# -*- coding:utf-8 -*-

import rospy 

from std_msgs.msg import Empty
from nav_msgs.msg import Odometry

```

Criamos e inicializamos as variaveis x, y e z. Criamos uma função de callback chamada ```recebeu_leitura`` que será chamada toda a vez que houver um dado novo do tópico da odometria (que é configurado mais abaixo).

Note que e ROS as chamadas são baseadas das funções de callback ocorrem por evento, de forma assincrona. Ou seja, não serão feitas pelo código principal.  

```python
# Apenas valores para inicializar
x = -1000
y = -1000
z = -1000

def recebeu_leitura(dado):
    """
        Grava nas variáveis x,y,z a posição extraída da odometria
        Atenção: *não coincidem* com o x,y,z locais do drone
    """
    global x
    global y 
    global z 

    x = dado.pose.pose.position.x
    y = dado.pose.pose.position.y
    z = dado.pose.pose.position.z

```    

Inicializa o node "print_odom" para ser identificado pelo ROS master. 
Subscreve (esculta) o tópico de odometria e realiza a chamada da função de callback "recebeu_leitura"


```python
if __name__=="__main__":

    rospy.init_node("print_odom")

    # Cria um subscriber que chama recebeu_leitura sempre que houver nova odometria
    recebe_odom = rospy.Subscriber("bebop/odom", Odometry , recebeu_leitura)

```  

Nosso laço principal, o while é executdo de forma infinita até o usuário fechar o programa. O rospy.sleep(2) executa um loop a cada 2 segundos. 

```python
    try:
        while not rospy.is_shutdown():
            ## Código principal
            print("x {} y {} z {}".format(x, y, z))
            rospy.sleep(2)

    except rospy.ROSInterruptException:
        rospy.sleep(1.0)
```

Agora que já entendemos, de forma breve, como o código funciona vamos rodar nosso código com o drone. 


## Rodando o código no drone

Para 




**rosrun exemplo codigo.py** - executa o script codigo.py que está na pasta exemplo

**rosrun teleop_twist_keyboard teleop_twist_keyboard.py cmd_vel:=/bebop/cmd_vel** - teleoperar o drone com o teclado









