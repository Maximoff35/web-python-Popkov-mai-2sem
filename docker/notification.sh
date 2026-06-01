#!/bin/sh
set -e

uvicorn notification_service.main:app --host 0.0.0.0 --port 8001
