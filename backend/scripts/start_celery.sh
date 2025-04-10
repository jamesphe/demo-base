#!/bin/bash
celery -A app.services.resume_queue_service worker --loglevel=info 