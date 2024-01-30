import pika
import json
from app import Product, db


params = pika.URLParameters('amqps://dfiopgox:Q9EjdEM_udQFPk603CG3aTRgsH27-Rxv@puffin.rmq2.cloudamqp.com/dfiopgox')

connection = pika.BlockingConnection(params)

channel = connection.channel()

channel.queue_declare(queue='main')

def callback(ch, method, properties, body):
    print('Received in main')
    data = json.loads(body)
    print(data)
    
    if properties.content_type == 'product_created':
        product = Product(title=data['title'], id=data['id'], image=data['image'])
        db.session.add(product)
        db.session.commit()
    elif properties.content_type == 'product_updated':
        product = Product.query.get(data['id'])
        product.title = data['title']
        product.image = data['image']

        db.session.commit()
    elif properties.content_type == 'product_deleted':
        product = Product.query.get(data)
        db.session.delete(product)
        db.session.commit()

channel.basic_consume(queue='main', on_message_callback=callback, auto_ack=True)

print('Started consuming')

channel.start_consuming()
channel.close()
