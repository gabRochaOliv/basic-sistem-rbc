
# Sistema RBC de Diagnóstico de Doenças em Soja

Este sistema utiliza um método de Raciocínio Baseado em Casos (RBC) para identificar doenças em plantas de soja com base em casos históricos armazenados em um banco de dados PostgreSQL. O sistema possui uma interface gráfica desenvolvida com Tkinter para facilitar a inserção de novos casos e a comparação com casos existentes.

## Pré-requisitos

Antes de executar o sistema, certifique-se de que você possui os seguintes requisitos:

1. **Python 3.x** instalado.
2. Biblioteca **psycopg2** instalada para conexão com o PostgreSQL. Use o comando:
   ```bash
   pip install psycopg2
   ```
3. Arquivo **`arq.json`** contendo o mapeamento de valores das características utilizadas.
4. Um banco de dados PostgreSQL configurado conforme os detalhes do sistema.

## Estrutura do Sistema

O sistema é composto por diversos componentes, cada um desempenhando uma função específica:

### 1. Arquivo JSON (`arq.json`)

Este arquivo armazena os valores possíveis para cada atributo usado no diagnóstico, convertendo valores categóricos em numéricos. Ele é essencial para a correta interpretação e comparação dos casos.

### 2. Banco de Dados PostgreSQL

O sistema se conecta ao banco de dados **`SistemaRBC_Soja`** e armazena casos na tabela **`casos`**. Certifique-se de que a tabela foi criada com os atributos correspondentes aos usados no sistema.

### 3. Interface Gráfica (Tkinter)

A interface gráfica permite ao usuário inserir um novo caso para análise e visualização dos resultados. Os valores são selecionados através de menus suspensos e há um campo para especificar o grau de similaridade desejado.

## Funcionalidades

### 1. Carregamento de Mapeamento de Valores

O sistema carrega o arquivo JSON que mapeia os valores das características. Isso permite que valores categóricos sejam convertidos em numéricos para o cálculo de similaridade.

### 2. Obtenção de Casos do Banco de Dados

O sistema conecta-se ao banco de dados e busca todos os casos armazenados na tabela `casos`, retornando-os como uma lista de dicionários.

### 3. Conversão de Valores

Função que converte valores categóricos para numéricos com base no mapeamento carregado do JSON.

### 4. Cálculo de Similaridade Local e Global

O sistema calcula a similaridade local entre os atributos dos casos usando uma fórmula que compara a diferença absoluta entre valores normalizados. Em seguida, a similaridade global é calculada considerando os pesos de cada atributo.

## Como Executar

1. Certifique-se de que o banco de dados PostgreSQL está rodando e que a tabela `casos` foi criada corretamente.
2. Coloque o arquivo `arq.json` na mesma pasta que o script Python.
3. Execute o sistema com o comando:
   ```bash
   python sistema_rbc.py
   ```

