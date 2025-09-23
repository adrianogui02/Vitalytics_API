# Vitalytics API - Monitoramento de Saúde SRAG

API desenvolvida como parte do **Desafio Técnico Full-Stack** para a _Indicium HealthCare Inc._  
A aplicação serve como backend para um dashboard de monitoramento de dados da Síndrome Respiratória Aguda Grave (SRAG), utilizando dados públicos do **OpenDataSUS**.

- **API em produção:** [https://vitalytics-api.onrender.com/docs](https://vitalytics-api.onrender.com/docs)
- **OBS:** Como o Render disponibiliza uma máquina bem limitada para o plano gratuito, as requisições podem demorar mais que o convencional.
- **Hardware Cloud:** Intância Free com 0.1CPU 512MB
- **Database Cloud:** Intância Free com 256MB 0.1CPU 1GB Storage

---

## 📌 Sobre o Projeto

A **Vitalytics API** é o backend responsável por processar, armazenar e servir dados sobre casos de _SRAG_.  
Ela alimenta um dashboard frontend, fornecendo:

- Métricas consolidadas
- Dados para gráficos interativos
- Projeções anuais

O objetivo é criar uma **Prova de Conceito (PoC)** robusta que demonstre a capacidade de construir **APIs eficientes e bem estruturadas** para manipulação de grandes volumes de dados.

---

## 🏗 Arquitetura

A API foi projetada para ser **escalável, testável e de fácil manutenção**, utilizando uma arquitetura em camadas e tecnologias modernas.

### Tecnologias Principais

- **FastAPI:** Framework web de alta performance, suporte assíncrono e documentação interativa automática (Swagger UI).
- **PostgreSQL:** Banco relacional robusto, ideal para consultas complexas e agregações.
- **SQLAlchemy:** ORM para mapear modelos Python em tabelas do banco de dados.
- **Pydantic:** Validação e serialização de dados seguindo schemas definidos.
- **Docker:** Ambiente de banco de dados local isolado e reprodutível.

## ⚙ Configuração e Execução Local

### ✅ Pré-requisitos

- Python **3.10+**
- Docker + Docker Compose

### 🔹 Passo 1: Clonar o Repositório

```bash
git clone https://github.com/adrianogui02/Vitalytics_API.git
cd Vitalytics_API
```

### 🔹 Passo 2: Ambiente Virtual e Dependências

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 🔹 Passo 3: Subir o Banco de Dados com Docker

- Linux

```bash
docker run --name srag-postgres-db \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=srag_db \
  -p 5432:5432 \
  -v srag-db-data:/var/lib/postgresql/data \
  -d postgres:15-alpine
```

- Windows

```bash
docker run --name srag-postgres-db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=srag_db -p 5432:5432 -v srag-db-data:/var/lib/postgresql/data -d postgres:15-alpine
```

### 🔹 Passo 4: Configurar Variáveis de Ambiente

Crie o arquivo .env na raiz do projeto:

```bash
DATABASE_URL="postgresql://user:password@localhost:5432/srag_db"
```

### 🔹 Passo 5: Popular o Banco de Dados

```bash
python -m scripts.import_data
```

- **OBS:** O processo pode levar vários minutos. O script popula de forma altomática o banco com dados do SUS de 2019 até 2025.

### 🔹 Passo 6: Iniciar a API

```bash
uvicorn app.main:app --reload
```

Acesse em: http://127.0.0.1:8000

Documentação interativa: http://127.0.0.1:8000/docs
