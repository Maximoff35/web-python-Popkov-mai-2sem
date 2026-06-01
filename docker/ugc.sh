#!/bin/sh
set -e

flask --app ugc_service.app:app run --host 0.0.0.0 --port 5000
