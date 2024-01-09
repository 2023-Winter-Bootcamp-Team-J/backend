from celery import Celery

app = Celery('celery',
             broker='amqp://npage:npage123@rabbitmq:5672/npage_host',
             #broker='amqp://npage:npage123@rabbitmq:5672/npage_host',
             backend='rpc://',
             #include=['test_tasks'],
             )
app.autodiscover_tasks()

'''
RABBITMQ_HOST=os.environ.get('RABBITMQ_HOST')
RABBITMQ_PORT=os.environ.get('RABBITMQ_PORT')
RABBITMQ_USER=os.environ.get('RABBITMQ_USER')
RABBITMQ_PASSWORD=os.environ.get('RABBITMQ_PASSWORD')

RBMQ_CONNECTION_URI=f'amqp://{RAB BITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}//'

environment:
        - RABBITMQ_DEFAULT_USER=tts
        - RABBITMQ_DEFAULT_PASS=tts123
        - RABBITMQ_DEFAULT_VHOST=tts_host
'''
