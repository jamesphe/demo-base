#!/bin/bash
celery -A app.services.resume_queue_service beat --loglevel=info 