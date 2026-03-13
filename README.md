# Script Demanda → GitLab

Script em Python que cria issues no GitLab a partir da(s) demanda(s) em `dmd.md`. Você refina o texto no Cursor antes de rodar; no terminal o script pede projeto, milestone (opcional), responsável (opcional) e labels. O terminal usa cores para facilitar a leitura.

## O que o script faz

1. Você refina o conteúdo de `dmd.md` no Cursor (título, Projeto/Módulo, User Story, Critérios de Aceite, Notas Técnicas).
2. Você roda **`python main.py`**.
3. O script lista os projetos do `projects.json` e você **escolhe pelo número**.
4. O script **busca na API do GitLab** os milestones e os membros do projeto; você escolhe **um milestone** (ou Enter para nenhum).
5. O script lê a(s) demanda(s) de `dmd.md`. Se houver **uma** demanda, você escolhe **um responsável** e as **labels** uma vez. Se houver **duas ou mais**, você escolhe o **responsável** e as **labels por demanda** (cada issue pode ter responsável e labels diferentes).
6. Uma issue é criada no GitLab para cada demanda, no mesmo projeto, com o milestone (único), o responsável e as labels daquela demanda. O placeholder `[Nome do Projeto]` na descrição é substituído pelo projeto selecionado.
7. Ao final, o script exibe em **cores** o link de cada issue criada.

## Pré-requisitos

- Python 3.10+
- Token de acesso do GitLab com permissão para criar issues e para listar milestones e membros do(s) projeto(s).

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

## Como executar (passo a passo)

1. **Prepare o ambiente** (uma vez por máquina):
   - Instale as dependências: `pip install -r requirements.txt`
   - Crie o `.env` com `GITLAB_URL` e `GITLAB_PRIVATE_TOKEN`
   - Coloque os projetos em `projects.json` e as labels em `labels.json`

2. **Prepare o arquivo de demandas**:
   - Edite o `dmd.md` (ou outro arquivo) com uma ou mais demandas no formato do escopo (título, Projeto/Módulo, User Story, Critérios de Aceite, Notas Técnicas). Várias demandas devem ser separadas por uma linha só com `----`.

3. **Execute o script**:
   ```bash
   python main.py
   ```
   No Windows (PowerShell ou cmd):
   ```bash
   python main.py
   ```
   Se usar outro arquivo de demanda:
   ```bash
   python main.py --demand-file meu_arquivo.txt
   ```

4. **No terminal, responda às perguntas na ordem**:
   - **Projeto:** digite o número do projeto da lista e Enter.
   - **Milestone:** será exibida a lista de milestones do projeto; digite o número do milestone desejado ou **Enter para não atribuir** (vale para todas as issues desta execução).
   - **Responsável:**  
     - Se houver **uma** demanda: será exibida a lista de membros; digite o número do responsável ou **Enter para não atribuir**.  
     - Se houver **duas ou mais** demandas: para cada demanda será mostrado o título; escolha o responsável daquela demanda (número ou Enter para nenhum). Assim você pode atribuir responsáveis diferentes por issue.
   - **Labels:**  
     - Se houver **uma** demanda: escolha os números das labels separados por vírgula (ex.: `1,3,5`) ou Enter para usar só as labels padrão (ex.: Correção, Não iniciado).  
     - Se houver **duas ou mais** demandas: para cada demanda será mostrado o título; escolha as labels daquela demanda (números ou Enter para padrão). Assim você pode dar labels diferentes por demanda.

5. **Resultado:** o script criará uma issue no GitLab para cada demanda, com o milestone (único), o responsável e as labels de cada uma, e exibirá em cores os links das issues criadas. Copie os links para acessar as issues no GitLab.

### Exemplo de fluxo no terminal (uma demanda)

```
Projetos disponíveis:
  1. IUBAAM
  2. SUBAS WEB
Escolha o projeto (número): 1
Milestones disponíveis:
  1. Sprint 1 (active)
  2. Sprint 2 (active)
Escolha o milestone (número, ou Enter para nenhum): 1
Membros disponíveis (responsável):
  1. João Silva (@joao.silva)
  2. Maria Santos (@maria.santos)
Escolha o responsável (número, ou Enter para nenhum): 2
Lendo 1 demanda(s) de dmd.md...
Labels disponíveis:
  1. PRIORIDADE: ALTA
  2. Correção
  3. Melhoria
Escolha a(s) label(s) (números separados por vírgula, ou Enter para padrão): 1,2
Issues criadas:
  Issue 1: https://gitlab.example.com/web/iubaam-web/-/issues/123
```

(No seu terminal, "Projetos disponíveis", "Milestones disponíveis", "Issues criadas" e os links aparecem coloridos.)

### Várias demandas: responsável e labels por demanda

Com **duas ou mais** demandas no `dmd.md`, o script pergunta o **responsável** e as **labels para cada demanda**. Exemplo:

```
[ 3 / 4 ] Responsável - Demanda 1/2
  Título da primeira demanda...
Membros disponíveis (responsável):
  1. João Silva (@joao.silva)
  2. Maria Santos (@maria.santos)
Escolha o responsável (número, ou Enter para nenhum): 1

[ 3 / 4 ] Responsável - Demanda 2/2
  Título da segunda demanda...
Escolha o responsável (número, ou Enter para nenhum): 2

[ 4 / 4 ] Labels e demandas
  Demanda 1/2: Título da primeira...
Labels disponíveis: ...
Escolha a(s) label(s): 1,2
  Demanda 2/2: Título da segunda...
Escolha a(s) label(s): 2
Issues criadas com sucesso
  Issue 1: https://...
  Issue 2: https://...
```

Assim, cada issue pode ter responsável e labels diferentes (ou Enter para nenhum responsável / só labels padrão).

### Refinar a demanda no Cursor (opcional)

Coloque o rascunho em `dmd.md` e peça ao Cursor: *"Refine o conteúdo do dmd.md seguindo o escopo [título, Projeto/Módulo, User Story, Critérios de Aceite, Notas Técnicas]."*

### Outras opções

- **Arquivo de demanda diferente:** `python main.py --demand-file outro.md`
- **Ajuda:** `python main.py --help`

## Formato da demanda (escopo)

Após o refinamento no Cursor, o `dmd.md` deve ter:

- **Primeira linha:** título da issue (com ou sem `#`).
- **Demais linhas:** descrição em Markdown com as seções **## Projeto / Módulo**, **## História de Usuário**, **## Critérios de Aceite**, **## Notas Técnicas**.

O script usa a primeira linha de cada bloco como título da issue e o restante como descrição. O projeto da issue é o que você escolhe na lista exibida no terminal. Na seção **## Projeto / Módulo**, use **`[Nome do Projeto]`** como placeholder; o script substitui pelo nome do projeto selecionado para que o card no GitLab exiba o nome correto.

**Várias demandas:** separe cada demanda com uma linha contendo apenas `----` (quatro hífens). O script criará uma issue por bloco. Quando houver 2 ou mais demandas, você escolhe o **responsável** e as **labels por demanda** (cada issue pode ter responsável e labels diferentes). O **milestone** é único e vale para todas as issues daquela execução.

### Incluir imagens na demanda

Para anexar imagens à descrição da issue de forma automática, use um arquivo **.md** (Markdown) como arquivo de demanda:

```bash
python main.py -f dmd.md
```

No conteúdo da demanda (em qualquer seção), use a sintaxe Markdown de imagem com **caminho relativo ao arquivo de demanda**:

```markdown
![Descrição da imagem](./pasta/evidencia.png)
```

Ou com a imagem na mesma pasta do `dmd.md`:

```markdown
![Print da tela](evidencia.png)
```

O script detecta essas referências, faz **upload** de cada arquivo no projeto GitLab (API de uploads) e **substitui** na descrição pelo link gerado pelo GitLab. A issue criada exibirá as imagens na descrição. Caminhos que forem URL (`http://` ou `https://`) são mantidos como estão; apenas arquivos locais são enviados. Se um arquivo não existir ou o upload falhar, a referência original é mantida e a criação da issue segue normalmente.
