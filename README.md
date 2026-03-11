# Script Demanda → GitLab

Script em Python que cria issues no GitLab a partir da(s) demanda(s) em `dmd.txt`. Você refina o texto no Cursor antes de rodar; o script pede o projeto e as labels no terminal.

## O que o script faz

1. Você pede ao **Cursor** para refinar o conteúdo de `dmd.txt` no escopo (título, Projeto/Módulo, User Story, Critérios de Aceite, Notas Técnicas). Sem API externa.
2. Você roda o script com **`python main.py`** (sem argumentos).
3. O script lista os projetos do `projects.json` e você **escolhe pelo número** no terminal.
4. O script lê a(s) demanda(s) de `dmd.txt`, exibe as labels e você **escolhe pelo terminal** (números separados por vírgula).
5. Uma issue é criada no GitLab para cada demanda, no **mesmo projeto** e com as **mesmas labels** selecionadas. O nome do projeto que aparece na descrição do card é o que você escolheu no terminal (o placeholder `[Nome do Projeto]` é substituído automaticamente).
6. Ao final, o script exibe o **link de cada issue** criada (Issue 1: url, Issue 2: url, etc.).

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

O script lista os projetos, depois lê `dmd.txt` e mostra as labels. Exemplo no terminal (uma demanda):

```
Projetos disponíveis:
  1. IUBAAM
Escolha o projeto (número): 1
Lendo 1 demanda(s) de dmd.txt...
Labels disponíveis:
  1. PRIORIDADE: ALTA
  2. PRIORIDADE: BAIXA
  3. PRIORIDADE: MÉDIO
  4. PRIORIDADE: URGENTE
  5. Precisa de Correção
Escolha a(s) label(s) (números separados por vírgula, ou Enter para nenhuma): 1,5
Issue 1: https://gitlab.level33lab.cloud/web/iubaam-web/-/issues/123
```

### 3. Várias demandas de uma vez

Você pode colocar **duas ou mais demandas** no mesmo `dmd.txt`. Separe cada demanda com uma linha contendo apenas **`---`** (três hífens). O script cria uma issue para cada bloco, no mesmo projeto e com as mesmas labels, e exibe o link de todas.

Exemplo de `dmd.txt` com duas demandas:

```
# Título da primeira demanda
## Projeto / Módulo
[Nome do Projeto] - Módulo X
## História de Usuário
...
---
# Título da segunda demanda
## Projeto / Módulo
[Nome do Projeto] - Módulo Y
## História de Usuário
...
```

Saída esperada (duas issues no projeto escolhido):

```
Lendo 2 demanda(s) de dmd.txt...
...
Issue 1: https://gitlab.../issues/123
Issue 2: https://gitlab.../issues/124
```

O placeholder **`[Nome do Projeto]`** na descrição de cada demanda é substituído pelo nome do projeto que você selecionou no terminal (ex.: IUBAAM, SUBAS WEB), para que o card no GitLab exiba o nome correto.

### Outras opções

- **Arquivo de demanda diferente:** `python main.py --demand-file outro.txt`
- **Ajuda:** `python main.py --help`

## Formato da demanda (escopo)

Após o refinamento no Cursor, o `dmd.txt` deve ter:

- **Primeira linha:** título da issue (com ou sem `#`).
- **Demais linhas:** descrição em Markdown com as seções **## Projeto / Módulo**, **## História de Usuário**, **## Critérios de Aceite**, **## Notas Técnicas**.

O script usa a primeira linha de cada bloco como título da issue e o restante como descrição. O projeto da issue é o que você escolhe na lista exibida no terminal. Na seção **## Projeto / Módulo**, use **`[Nome do Projeto]`** como placeholder; o script substitui pelo nome do projeto selecionado para que o card no GitLab exiba o nome correto.

**Várias demandas:** separe cada demanda com uma linha contendo apenas `---` (três hífens). O script criará uma issue por bloco e exibirá o link de cada uma.
