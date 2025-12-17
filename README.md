# Virtual Personal Finance Assistant

## Overview
An experimental **Virtual Assistant for Personal Finance** leveraging Reddit data to provide contextual, actionable insights. Combines **NLP**, **semantic search**, and **Retrieval-Augmented Generation (RAG)** for personalized financial guidance.  

Built as part of **LOG791 – Special Project** at ÉTS (Software Engineering).

## Objectives
- Aggregate and structure finance-related Reddit discussions  
- Filter noise and extract useful knowledge  
- Generate context-aware, professional answers  
- Support personal finance decisions (budgeting, investing, retirement, taxes)  

## Key Features
- Reddit data collection and filtering  
- Semantic search with **FAISS**  
- RAG pipeline with **Meta-Llama-3-8B-Instruct**  
- REST API (**FastAPI**) + Dash web app  
- CI/CD with **GitHub Actions**, Dockerized  
- Scalable, modular architecture  

## System Architecture
**1. Data Pipeline**  
- Extracts posts/comments from finance subreddits  
- Proxy rotation & filtering  
- SQL storage on Oracle Cloud, updated every 8h  

**2. Backend API**  
- **FastAPI** with `/complete_message/` endpoint  
- Async processing via APScheduler  
- Singleton DAO for DB access  

**3. Semantic Search & RAG**  
- Embeddings: `paraphrase-MiniLM-L3-v2`  
- FAISS local indexing  
- Top-10 relevant posts retrieved per query  

**4. LLM Integration**  
- **Meta-Llama-3-8B-Instruct** via Together API  
- Orchestration: LangChain + LangGraph  
- Professional financial tone enforced  

**5. Web Application**  
- **Dash** frontend: stats + conversational interface  
- Lightweight, integrated with backend API  

## CI/CD
- Automated builds & deploys via **GitHub Actions**  
- Dockerized, deployed on VPS with NGINX + Certbot  
- Auto-rebuild/redeploy on main branch updates  

## Results
- >95% success in ad hoc testing  
- Avg. response time: ~30s  
- 45,000+ Reddit posts indexed; 180 daily  
- High-quality, structured answers  

## Limitations
- Latency for real-time interaction  
- Data-dependent answer quality; occasional hallucinations  
- Limited error-handling and user feedback  
- Local FAISS indexing limits scalability  

## Future Improvements
- Observability: Prometheus/Grafana  
- Enhanced frontend UX  
- Hybrid knowledge sources (Reddit + APIs)  
- External vector DB for scalability  
- Better hallucination mitigation  

## Technologies
Python | FastAPI | Dash | LangChain / LangGraph | FAISS | Meta-Llama-3-8B-Instruct | GitHub Actions | Docker | Oracle Cloud SQL  

## Academic Context
- **Course:** LOG791 – Special Project  
- **Institution:** ÉTS  
- **Program:** B.Eng Software Engineering  
- **Author:** Lancelot Domart  
- **Year:** 2025  

## PDF Report
[Download full project report (PDF)](/PS%20-%20Assistant%20virtuel%20en%20finance%20personnelles.pdf)  

## Disclaimer
Academic prototype only. Not certified financial advice. Validate outputs with professionals before making decisions.
