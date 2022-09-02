![](ROS.png)

## ROS


O ROS ou Robotic Operation System é basicamente um framework OpenSource para o desenvolvimento de aplicações em robotica. Atualmente é um dos maiores e mais utilizados em projetos de robótica. 


Não precisamos de um conhecimento profundo sobre o ROS para participar da nossa atividade complementar, apenas alguns conceitos básicos já são o suficientes.  


## Conceitos simples que precisamos compreender. 

### Como o vou comunicar o meu código do pc com o drone

A topologia que vamos utilizar em nossa aplicação será:

- O drone está configurado como Acess Point, ou seja o drone irá fornecer um ponto de rede Wifi para que outros dispositivos se conectem a ele. 
- O nome desta rede é ````bebop seguida do serial number do drone```
- Vamos conectar o Wifi do nosso computador na rede criada pelo drone do drone. 

!!! warning
    A rede do bebop não tem senha, basta se conectar. Esta rede não possui acesso internet, se precisar usar internet terá que trocar a rede wifi. 

### E o que preciso entender de ROS

Vamos explorar brevemente e compreender o básico sobre ROS. 

### ROS MASTER

Tudo começa aqui, o ROS Master faz o controle dos nodes (nós), registra os nodes e acompanha os nós quando novos nós são executados e entram no sistema. O ROS Master estabelece uma alocação dinâmica de conexões. Os nós não podem se comunicar até que o Mestre notifique os nós da existência um do outro. O protocolo mais usado para conexão é o protocolo padrão de controle de transmissão/protocolo de internet (TCP/IP). Uma vez que esses nós são capazes de localizar uns aos outros, eles podem se comunicar entre si P2P (peer-to-peer).


### ROS NODES

![](ros-master-nodes.jpg)



A ideia do ROS é facilitar a forma de comunicação entre nós (nodes). Os nodes são basicamente processos que realizam alguma tarefa especifica com a vantagem de se registrar com o nó ROS Master e se comunicar com outros nós no sistema. 

Por exemplo, um nó pode capturar as imagens de uma câmera e enviar as imagens para outro nó para processamento. Depois de processar a imagem, o segundo nó pode enviar um sinal de controle para um terceiro nó para controlar um manipulador robótico em resposta à visão da câmera.


ROS TOPICS

Alguns nós fornecem informações para outros nós, como o exemplo acima. 

Diz-se que esse nó publica informações que podem ser recebidas por outros nós. A informação no ROS é chamada de tópico. Um tópico define os tipos de mensagens que serão enviadas em relação a esse tópico.

Quais os tipos de topicos:

- Publisher - Enviam informações

- Subscriber - Recebem informações


ROS MENSAGES

O ROS mensages define o tipo e o formato dos dados. É nele que sabemos se as msg são do tipo String, float e afins. l de ROS.

