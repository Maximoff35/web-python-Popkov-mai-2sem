from fastapi import FastAPI


app = FastAPI(
    title='Notification Service',
    description='FastAPI-сервис для уведомлений.',
    version='1.0.0',
)

@app.get('/api/notifications/health/')
async def health_check():
    return {
        'status': 'ok',
        'service': 'notifications',
    }