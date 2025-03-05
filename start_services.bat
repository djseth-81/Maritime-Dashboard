@echo off
title Starting Kafka & FastAPI Services
cd /d ..\kafka_2.13-3.9.0

REM Start Kafka in a new CMD window
start "Kafka Server" cmd /k ^
"java -cp \"..\kafka_2.13-3.9.0\libs\*\" org.apache.kafka.Kafka config/kraft/server.properties"

REM Wait for Kafka to start
timeout /t 10 /nobreak >nul

REM Activate virtual environment and start FastAPI in a new CMD window
cd /d ..\Maritime-Ops-Dashboard\backend
start "FastAPI Server" cmd /k ^
"..\.venv\Scripts\activate && pip install fastapi[standard] && python -m uvicorn main:app --host 0.0.0.0 --port 5000 --reload"

exit
