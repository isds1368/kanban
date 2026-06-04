# ⚡ KanbanPro — Sistema de Gestão Corporativa

Sistema Kanban corporativo completo desenvolvido com Python + Streamlit + SQLite.

---

## 🚀 Instalação

### Pré-requisitos
- Python 3.9 ou superior
- pip

### Passos

```bash
# 1. Extraia os arquivos do projeto
cd kanban/

# 2. (Opcional) Crie um ambiente virtual
python -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\activate          # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute o sistema
streamlit run app.py
```

O sistema estará disponível em: **http://localhost:8501**

---

## 🌐 Acesso pela Rede

Para que outros computadores da empresa possam acessar:

```bash
streamlit run app.py --server.address=0.0.0.0 --server.port=8501
```

Outros usuários acessam pelo navegador via: `http://SEU_IP_INTERNO:8501`

Para descobrir o IP do servidor:
- Windows: `ipconfig` no CMD
- Linux/Mac: `ip addr` ou `ifconfig`

---

## 🔐 Login Padrão

| Campo  | Valor     |
|--------|-----------|
| Login  | admin     |
| Senha  | admin123  |

> ⚠️ **Altere a senha do administrador após o primeiro acesso!**

---

## 📁 Estrutura do Projeto

```
kanban/
├── app.py                  # Ponto de entrada principal
├── requirements.txt        # Dependências Python
├── kanban.db               # Banco de dados SQLite (criado automaticamente)
├── uploads/                # Arquivos anexados
├── backups/                # Backups automáticos
├── .streamlit/
│   └── config.toml         # Configuração do Streamlit
└── modules/
    ├── database.py         # Schema e conexão SQLite
    ├── auth.py             # Autenticação e gestão de usuários
    ├── board_ops.py        # Operações de quadros, cards, comentários
    ├── backup.py           # Sistema de backup
    ├── ui_components.py    # CSS e componentes visuais
    ├── page_login.py       # Página de login
    ├── page_boards.py      # Listagem de quadros
    ├── page_kanban.py      # Board Kanban principal
    ├── page_dashboard.py   # Dashboard executivo
    ├── page_personal.py    # Área pessoal privada
    ├── page_notifications.py # Central de notificações
    └── page_admin.py       # Painel administrativo
```

---

## ✅ Funcionalidades

### Kanban
- [x] Múltiplos quadros por empresa
- [x] Colunas configuráveis (sem limite)
- [x] Cards com título, descrição, responsável, prazo, prioridade
- [x] Etiquetas coloridas por quadro
- [x] Checklist dentro dos cards
- [x] Comentários com histórico
- [x] Histórico completo de movimentações
- [x] Rastreamento de tempo por coluna
- [x] Filtros avançados (responsável, setor, prioridade, busca)
- [x] Mover cards entre colunas

### Dashboard
- [x] KPIs: total, abertas, concluídas, atrasadas
- [x] Taxa de conclusão
- [x] Gráfico por prioridade
- [x] Gráfico por setor
- [x] Evolução semanal (7 dias)
- [x] Evolução mensal (12 meses)
- [x] Ranking de produtividade por colaborador
- [x] Lista de tarefas atrasadas com dias de atraso

### Usuários & Permissões
- [x] Perfis: Administrador, Gestor, Colaborador, Leitor
- [x] Senhas criptografadas (SHA-256)
- [x] Controle de sessão
- [x] Logs de acesso

### Área Pessoal (privada)
- [x] Tarefas pessoais com checklist
- [x] Notas e anotações pessoais
- [x] Dados vinculados ao usuário logado

### Administração
- [x] Criação e edição de usuários
- [x] Desativação de usuários
- [x] Backup manual com download
- [x] Logs do sistema com filtros
- [x] Métricas do sistema

### Notificações
- [x] Central de notificações por usuário
- [x] Marcar como lida individualmente ou em lote
- [x] Tipos: info, aviso, sucesso, urgente

---

## 🔒 Segurança
- Senhas armazenadas com hash SHA-256
- Controle de acesso por perfil em cada operação
- Histórico de cards imutável
- Logs de todas as ações relevantes
- Proteção de exclusão com confirmação

---

## 💾 Backup

O backup pode ser criado manualmente pelo painel de Administração.
O arquivo ZIP inclui o banco `kanban.db` e todos os arquivos anexados.

Para backup automático agendado (Linux), adicione ao crontab:
```bash
# Backup diário às 23h
0 23 * * * cd /caminho/do/kanban && python -c "from modules.backup import create_backup; create_backup()"
```

---

## 🔧 Migração para PostgreSQL

O sistema foi estruturado para fácil migração. Para migrar:

1. Instale `psycopg2-binary`
2. Em `modules/database.py`, substitua `sqlite3` por `psycopg2`
3. Ajuste a string de conexão
4. Adapte os tipos de dado (TEXT → VARCHAR, INTEGER → SERIAL, etc.)

---

## 📞 Suporte

KanbanPro v1.0.0 — Sistema de Gestão Corporativa
Desenvolvido com Python + Streamlit + SQLite
