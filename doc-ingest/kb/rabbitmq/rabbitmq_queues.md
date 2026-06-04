# RabbitMQ Queues Deep Dive

## Durable Queue

Durable queues survive broker restarts.

```javascript
channel.assertQueue('my_queue', {
  durable: true
});
```

## Basic Consumer Example

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)

channel = connection.channel()

channel.queue_declare(
    queue='my_queue',
    durable=True
)

def callback(ch, method, properties, body):
    print(body)
    ch.basic_ack(
        delivery_tag=method.delivery_tag
    )

channel.basic_consume(
    queue='my_queue',
    on_message_callback=callback
)

channel.start_consuming()
```

## Message Persistence

```javascript
channel.sendToQueue(
  'my_queue',
  Buffer.from('Hello'),
  { persistent: true }
);
```

## Prefetch Count

```python
channel.basic_qos(
    prefetch_count=1
)
```

## Dead Letter Queue

Failed messages can be moved to a Dead Letter Queue (DLQ).

## Queue in Doc Assistant System

Queue Name:

```text
doc_question_processing
```

Producer:

```text
doc-orchestrator
```

Consumer:

```text
doc-ai-engine
```

Payload Example:

```json
{
  "questionId": "uuid",
  "askedBy": "email"
}
```