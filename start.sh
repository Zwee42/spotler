#!/bin/bash

# Start the FastAPI backend in the background
cd /app/backend
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Start the Vite frontend preview server
cd /app/frontend
npm run start