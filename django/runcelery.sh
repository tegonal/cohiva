#!/bin/bash
export DJANGO_SETTINGS_MODULE="cohiva.settings"
celery -A cohiva worker -l INFO -n dev-worker1@%h --concurrency=1

