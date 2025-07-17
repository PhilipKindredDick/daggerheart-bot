#!/bin/bash

# Запуск только API сервера для Render
uvicorn api.main:app --host 0.0.0.0 --port $PORT