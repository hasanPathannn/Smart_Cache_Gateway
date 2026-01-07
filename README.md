# 🚀 SmartCache: Distributed Semantic Caching & Gateway for LLMs

![Python](https://img.shields.io/badge/Python-3.9-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-Vector_Search-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Scaled-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)

---

## 📌 Overview

**SmartCache** is a production-grade API Gateway designed to optimize **Large Language Model (LLM)** inference.

It acts as an intelligent middleware between client applications and LLM providers such as **OpenAI** or **Anthropic**.

Instead of forwarding every request, SmartCache performs a **semantic vector search** against Redis.  
If a semantically similar query exists, it returns a cached response in **<50ms**, bypassing the expensive LLM API call entirely.

---

## ⚡ Key Capabilities

- **💰 Cost Efficiency**  
  Reduces API costs by up to **50%** using semantic cache hits.

- **🚀 High Performance**  
  Lowers latency from ~2s (LLM) to ~20ms (Redis).

- **🧠 Semantic Understanding**  
  Uses cosine similarity (`sentence-transformers`) to detect intent similarity.

- **🛡️ Robust Engineering**  
  Implements a **Token Bucket Rate Limiter** using Redis **Lua scripts** for atomicity.

- **🔄 Automatic Failover**  
  Circuit breaker reroutes traffic to fallback models (e.g., Llama 3).

- **📈 Scalable**  
  Fully containerized and Kubernetes-ready for horizontal scaling.

---

## 🏗️ Architecture

![System Architecture](./assets/SmartCache.png)

---

## 🛠️ Tech Stack

- **Backend:** Python, FastAPI (async/await)
- **Database:** Redis Stack (Vector Store + Cache)
- **AI/ML:** Sentence-Transformers (`all-MiniLM-L6-v2`)
- **DevOps:** Docker, Docker Compose, Kubernetes (AKS / EKS ready)
- **Observability:** Prometheus Metrics

---

## 🚀 Quick Start

### Prerequisites
- Docker
- Docker Compose

---

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/hasanPathannn/smart-cache-llm-gateway.git
cd smart-cache-llm-gateway

2️⃣ Run with Docker Compose (Dev Mode)
docker-compose up --build


API will be available at:
👉 http://localhost:8000

🧪 Test the API
Cache Miss
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"What is the capital of France?","user_id":"test_user"}'


Response Source: openai (simulated)

Cache Hit
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Tell me the capital of France","user_id":"test_user"}'


Response Source: cache
Latency Saved: High

⚠️ Windows PowerShell users: Use Invoke-RestMethod instead of curl.

☸️ Kubernetes Deployment

The project includes Kubernetes manifests for 3 replicas to ensure high availability.

kubectl apply -f k8s/
kubectl get pods
kubectl port-forward service/smartcache-service 8080:80

📂 Project Structure
smart_cache_gateway/
├── app/
│   ├── services/
│   │   ├── cache_service.py   # Vector search logic
│   │   ├── rate_limiter.py    # Lua-based token bucket
│   │   └── llm_service.py     # Provider abstraction & failover
│   ├── models/                # Pydantic schemas
│   ├── main.py                # API entry point
│   └── config.py              # Environment variables
├── k8s/                       # Kubernetes manifests
├── docker-compose.yml
├── Dockerfile
└── requirements.txt

🧠 Hard Engineering Challenges Solved
1️⃣ Atomic Rate Limiting with Lua

Implemented a Token Bucket algorithm using Redis Lua scripts to guarantee atomic check-and-decrement operations across multiple replicas.

2️⃣ Non-Blocking Cache Writes

Used FastAPI Background Tasks to update the vector cache asynchronously, ensuring user requests are never blocked.

3️⃣ Resilience & Failover

Implemented circuit breaker logic with chaos-testing simulation.
If the primary provider fails (5xx), traffic is automatically rerouted to a fallback model (Llama 3 / Local) with zero request drops.

⭐ Why SmartCache Matters

SmartCache demonstrates real-world AI infrastructure engineering, combining:

Distributed systems

High-performance caching

Cost optimization

Cloud-native scalability