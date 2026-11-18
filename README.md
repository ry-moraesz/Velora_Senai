# VELORA — fase 1

Base executável do sistema patrimonial. Implementa FastAPI, SQLAlchemy 2, PostgreSQL/PostGIS, Alembic, JWT, multiempresa, papéis, ativos/categorias/setores/blocos, QR individual, movimentação transacional, auditoria e React/TypeScript/Vite/Tailwind.

> Os cinco documentos de referência citados não estavam disponíveis nesta conversa. A paleta e os requisitos descritos no pedido foram usados como referência provisória. Comparação fiel com MER, mapa, logo e identidade depende do envio desses arquivos.

## Executar no Windows
1. Instale Docker Desktop, Python 3.12 e Node 20+.
2. `copy .env.example .env` e defina `JWT_SECRET` forte.
3. `docker compose up -d db`
4. Backend: `cd backend`, `py -m venv .venv`, `.venv\Scripts\activate`, `pip install -r requirements.txt`, `alembic upgrade head`, `uvicorn app.main:app --reload`.
5. Frontend: `cd frontend`, `npm install`, `npm run dev`.
6. API docs: http://localhost:8000/docs; interface http://localhost:5173.

Criar a primeira empresa/admin é deliberadamente bootstrap por endpoint de instalação, permitido somente enquanto não houver usuários. POST `/api/v1/auth/bootstrap` com `company_name`, `cnpj`, `name`, `email`, `password`. Remova/desabilite esse endpoint após provisionamento em produção. Depois POST `/api/v1/auth/login` recebe OAuth form `username` (email) e `password`.

## Estado e escopo
O fluxo funcional incluído: bootstrap/login → dashboard → lista/criação/detalhe → retirada/devolução/transferência. Não alegamos ter finalizado os módulos complementares listados no requisito. Próximas fases: assinaturas/recuperação, CRUD administrativo, mapa/plantas SVG, scanner web, RFID real (depende do fabricante), relatórios/exportação, frontend completo, testes e empacotamento. RFID é somente interface/adaptador simulado; não lê hardware.

Datas persistidas UTC; timestamps retornados com timezone. Produção exige TLS, segredo seguro, CORS restrito, backups, gestão de uploads, rate limiting e revisão de segurança. Compatibilidade setor-categoria e localização corrente obrigatória são aplicadas em serviços; movimento histórico é append-only pela API. Dados geográficos usam PostGIS Point. QR guarda URL opaca de consulta, sem informação sensível.
