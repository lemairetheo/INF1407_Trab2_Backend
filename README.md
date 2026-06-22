# Biblioteca API — INF1407 (Backend)

Backend do **2º Trabalho de Programação para Web**. API REST desenvolvida em
**Django + Django REST Framework** para gerenciar um catálogo de livros por usuário.

> O frontend que consome esta API está em outro repositório:
> [INF1407_Trab2_Frontend](https://github.com/lemairetheo/INF1407_Trab2_Frontend)

## Integrantes

* Théo Lemaire
* Lucie Brunelle

## Escopo

API com autenticação JWT que permite a cada usuário gerenciar seu próprio
catálogo de livros (CRUD completo). Cada usuário só enxerga e manipula os
livros que lhe pertencem.

### Funcionalidades

* **CRUD** de livros (`/api/books/`) — endpoint protegido (somente autenticado).
* **Autenticação JWT** — login e refresh de token.
* **Gerência de usuário** — cadastro, troca de senha, "esqueci minha senha"
  (envio de link por email).
* **Visões diferentes por usuário** — cada usuário vê apenas seus livros.
* **Documentação Swagger** em `/api/docs/`.

## Tecnologias

* Python 3.9+ / Django 4.2
* Django REST Framework
* drf-spectacular (Swagger / OpenAPI)
* djangorestframework-simplejwt (JWT)
* django-cors-headers (CORS)

## Instalação local

```bash
# 1. Clonar e entrar na pasta
git clone https://github.com/lemairetheo/INF1407_Trab2_Backend.git
cd INF1407_Trab2_Backend

# 2. Ambiente virtual
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Dependências
pip install -r requirements.txt

# 4. Variáveis de ambiente
cp .env.example .env            # ajuste os valores se necessário

# 5. Banco de dados
python manage.py migrate
python manage.py createsuperuser

# 6. Rodar o servidor
python manage.py runserver
```

A API fica disponível em `http://localhost:8000/`.

## Endpoints principais

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| POST | `/api/auth/register/` | Cadastro de usuário | Não |
| POST | `/api/auth/login/` | Login (retorna JWT) | Não |
| POST | `/api/auth/refresh/` | Renova o token | Não |
| POST | `/api/auth/change-password/` | Troca de senha | Sim |
| POST | `/api/auth/password-reset/` | Solicita reset por email | Não |
| POST | `/api/auth/password-reset/confirm/` | Confirma reset | Não |
| GET/POST | `/api/books/` | Lista / cria livros | Sim |
| GET/PUT/PATCH/DELETE | `/api/books/{id}/` | Detalha / edita / remove | Sim |
| GET | `/api/docs/` | Documentação Swagger | Não |

## Como usar (exemplo)

```bash
# 1. Cadastrar
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"teo","email":"teo@ex.com","password":"SenhaForte123"}'

# 2. Login -> copie o "access"
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"teo","password":"SenhaForte123"}'

# 3. Criar um livro (use o token)
curl -X POST http://localhost:8000/api/books/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Dom Casmurro","author":"Machado de Assis"}'
```

## Documentação Swagger

Com o servidor rodando, acesse **`http://localhost:8000/api/docs/`**.
O schema OpenAPI bruto fica em `/api/schema/`.

## Relato (o que funciona / o que não funciona)

> _A preencher antes da entrega._

* ✅ Funciona: _..._
* ❌ Não funciona: _..._
