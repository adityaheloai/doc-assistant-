# RabbitMQ Introduction

## What is RabbitMQ?

RabbitMQ is a message broker that allows applications to communicate using queues.

## Benefits

- Decouples services
- Asynchronous processing
- Reliable message delivery
- Load balancing

## Core Concepts

### Producer

Application that sends messages.

### Consumer

Application that receives messages.

### Queue

Stores messages waiting to be processed.

### Exchange

Routes messages to queues.

### Binding

Connection between exchange and queue.

## Message Flow

1. Producer sends message
2. Exchange receives message
3. Exchange routes message
4. Queue stores message
5. Consumer processes message
6. Consumer acknowledges message

## Install Node.js Client

```bash
npm install amqplib
```

## Install Python Client

```bash
pip install pika
```