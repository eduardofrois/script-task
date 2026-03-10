# Script Demanda → GitLab

Script em Python que cria uma issue no GitLab a partir da demanda em `dmd.txt`. Você refina o texto no Cursor antes de rodar; o script pede o projeto e as labels no terminal.

## O que o script faz

1. Você pede ao **Cursor** para refinar o conteúdo de `dmd.txt` no escopo (título, Projeto/Módulo, User Story, Critérios de Aceite, Notas Técnicas). Sem API externa.
2. Você roda o script com **`python main.py`** (sem argumentos).
3. O script lista os projetos do `projects.json` e você **escolhe pelo número** no terminal.
4. O script lê a demanda de `dmd.txt`, exibe as labels e você **escolhe pelo terminal** (números separados por vírgula).
5. A issue é criada no GitLab com o título e a descrição do `dmd.txt` e as labels selecionadas.

## Pré-requisitos

- Python 3.10+
- Token de acesso do GitLab com permissão para criar issues no(s) projeto(s).

## Instalação

Execute cada comando em uma linha separada (não use vírgulas):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

No Windows (PowerShell): use `.venv\Scripts\activate` em vez de `source .venv/bin/activate`.

## Configuração

### Variáveis de ambiente (`.env`)

Copie o exemplo e preencha:

```bash
cp .env.example .env
```

| Variável | Descrição |
|----------|-----------|
| `GITLAB_URL` | URL base do GitLab (ex: `https://gitlab.level33lab.cloud`) |
| `GITLAB_PRIVATE_TOKEN` | Token de acesso pessoal do GitLab (criar em Perfil → Access Tokens) |

### Mapeamento de projetos (`projects.json`)

Associa o nome do projeto ao **path do repositório** no GitLab. A URL base fica só no `.env` (`GITLAB_URL`); aqui você informa apenas o path para concatenar. Exemplo:

```json
{
  "IUBAAM": "web/iubaam-web",
  "OUTRO PROJETO": "web/outro-repo"
}
```

### Labels (`labels.json`)

Lista de labels que podem ser anexadas à issue. O script mostra essa lista no terminal para você escolher por número. Exemplo:

```json
[
  "PRIORIDADE: ALTA",
  "PRIORIDADE: BAIXA",
  "PRIORIDADE: MÉDIO",
  "PRIORIDADE: URGENTE",
  "Precisa de Correção"
]
```

As labels precisam existir no projeto no GitLab com os mesmos nomes.

## Como usar

### 1. Refinar a demanda no Cursor (antes de rodar)

Coloque a demanda (texto simples ou rascunho) em `dmd.txt` e peça ao Cursor: *"Refine o conteúdo do dmd.txt seguindo o escopo [título, Projeto/Módulo, User Story, Critérios de Aceite, Notas Técnicas]."* O Cursor edita o arquivo; não é necessária nenhuma API externa.

### 2. Rodar o script

```bash
python main.py
```

O script lista os projetos, depois lê `dmd.txt` e mostra as labels. Exemplo no terminal:

```
Projetos disponíveis:
  1. IUBAAM
Escolha o projeto (número): 1
Lendo demanda de dmd.txt...
Labels disponíveis:
  1. PRIORIDADE: ALTA
  2. PRIORIDADE: BAIXA
  3. PRIORIDADE: MÉDIO
  4. PRIORIDADE: URGENTE
  5. Precisa de Correção
Escolha a(s) label(s) (números separados por vírgula, ou Enter para nenhuma): 1,5
Issue criada: https://gitlab.level33lab.cloud/web/iubaam-web/-/issues/123
```

### Outras opções

- **Arquivo de demanda diferente:** `python main.py --demand-file outro.txt`
- **Ajuda:** `python main.py --help`

## Formato da demanda (escopo)

Após o refinamento no Cursor, o `dmd.txt` deve ter:

- **Primeira linha:** título da issue (com ou sem `#`).
- **Demais linhas:** descrição em Markdown com as seções **## Projeto / Módulo**, **## História de Usuário**, **## Critérios de Aceite**, **## Notas Técnicas**.

O script usa a primeira linha como título da issue e o restante como descrição. O projeto da issue é o que você escolhe na lista exibida no terminal.
