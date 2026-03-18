# Nova coluna Motivo de Inspeção na grade da tela Gestão de Transporte

## Projeto / Módulo
[Nome do Projeto] - Gestão de Transporte

## História de Usuário (User Story)
**Como** usuário da tela Gestão de Transporte,
**Eu quero** visualizar na grade uma coluna "Motivo de Inspeção" ao lado da coluna Endereço do Estabelecimento,
**Para que** eu possa ver diretamente os motivos de inspeção selecionados pelo usuário que criou a OS, sem precisar abrir outro recurso.

![Evidência](assets/image.png)

## Critérios de Aceite (Acceptance Criteria)

### Critério 1: Coluna na grade
* **Dado que** estou na tela Gestão de Transporte,
* **Quando** visualizo a grade com a coluna Endereço do Estabelecimento,
* **Então** deve existir uma nova coluna chamada "Motivo de Inspeção" ao lado (adjacente) da coluna Endereço do Estabelecimento.
* **E** a coluna deve exibir os dados corretos para cada registro.

### Critério 2: Origem dos dados
* **Dado que** uma OS foi criada com um ou mais motivos de inspeção selecionados,
* **Quando** a grade da Gestão de Transporte é carregada ou atualizada,
* **Então** a coluna "Motivo de Inspeção" deve trazer os motivos que foram selecionados pelo usuário que criou a OS.

## Notas Técnicas para a Equipe de Dev
* **Contexto / Evidência:** Tela Gestão de Transporte; incluir coluna na grade ao lado de Endereço do Estabelecimento.
* **Backend / Banco de Dados:** Garantir que o endpoint/query da grade retorne os motivos de inspeção vinculados à OS (ou ao usuário que criou a OS), para preencher a nova coluna.
* **Frontend / UI:** Incluir nova coluna na definição da grade; alinhar ordem/posição com o layout (ao lado de Endereço do Estabelecimento).
