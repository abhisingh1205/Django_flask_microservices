import pika
import json

params = pika.URLParameters('amqps://dfiopgox:Q9EjdEM_udQFPk603CG3aTRgsH27-Rxv@puffin.rmq2.cloudamqp.com/dfiopgox')

connection = pika.BlockingConnection(params)

channel = connection.channel()

def publish(method, body):
    properties = pika.BasicProperties(method)
    channel.basic_publish(exchange='', routing_key='admin', body=json.dumps(body), properties=properties)

