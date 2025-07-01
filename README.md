# Trabalho Prático Unidade 1 Docker

Este trabalho tem por objetivo apresentar um projeto que executa a aplicação
`guess_game` utilizando _containers_ via Docker. Nenhuma parte do código-fonte
da aplicação foi modificada e preocupou-se somente em adicionar arquivos
relativos ao Docker e Docker Compose.

> [!NOTE]
> Como o exercício informa que o projeto deve permitir a atualização de qualquer
> componente **apenas trocando a versão do _container_ correspondente**,
> optou-se pelo _build_ de imagens de _container_ sempre que o código-fonte da
> aplicação precise ser alterado ao invés de utilizar volumes que disponibilizam
> o código-fonte local para os _containers_.

> [!NOTE]
> Considerou-se que o projeto trabalha com a aplicação no formato mais próximo
> de ambientes produtivos, evitando assim a execução dos serviços em modo
> desenvolvimento.

## Estrutura Adicional do Repositório

```
guess_game/
├─ docker/
│  ├─ backend/
│  │  ├─ Dockerfile
│  ├─ frontend/
│  │  ├─ Dockerfile
│  │  ├─ configs/
│  │  │  ├─ nginx-template-default.conf
├─ docker-compose.yaml
├─ docker-compose/
│  ├─ proxy/
│  │  ├─ configs/
│  │  │  ├─ nginx-template-default.conf
```

### Serviço `backend`

O arquivo `docker/backend/Dockerfile` define a imagem de _container_ que será
utilizada pelo serviço `backend`. Como o código-fonte foi escrito em Python e
utiliza Flask como _framework_, e visando ambientes produtivos, optou-se por
executar o serviço com uWSGI.

Todas as dependências são instaladas via gerenciador de pacotes `pip` com o
argumento `--no-cache-dir`, que evita salvar arquivos de _cache_ desnecessários
na imagem de _container_ final.

Ainda, os comandos do Dockerfile foram organizados buscando a redução na
quantidade de _layers_ da imagem de _container_. No entando, os comandos `COPY`
ao final do arquivo não foram concatenados porque o Docker copia o conteúdo
interno dos diretórios ao invés dos diretórios em si.

### Serviço `frontend`

Já o arquivo `docker/frontend/Dockerfile` define a imagem de _container_ do
serviço `frontend`. Como o código-fonte foi escrito em JavaScript e utiliza
React como biblioteca, optou-se por efetuar o _build_ da aplicação, gerando
assim todos os arquivos estáticos (não dinâmicos) que podem ser entregues por
qualquer servidor _web_. Escolheu-se, então, o nginx para esta tarefa,
configurado pelo arquivo `docker/frontend/configs/nginx-template-default.conf`.

Suas dependências são instaladas através do gerenciador de pacotes `npm`. Também
utiliza-se o `npm` para invocar o _build_ do React, responsável por criar os
arquivos estáticos finais.

Assim como no `backend`, o arquivo Dockerfile também foi organizado para reduzir
a quantidade de _layers_ da imagem de _container_, porém, neste caso, utilizando
_multi-stage builds_, onde no primeiro estágio instala-se as dependências e
cria-se os arquivos estáticos, e no segundo estágio copia-se estes arquivos para
entrega pelo servidor _web_.

### Serviços Auxiliares

O arquivo `docker-compose.yaml` define a infraestrutura de _containers_
utilizando Docker Compose.

O serviço `proxy` é responsável por executar um nginx que trabalha como _load
balancer_, encaminhando as requisições para os serviços `backend` e `frontend`.
Para manter as URLs utilizadas na documentação inicial, utilizou-se a porta 5000
para disponibilizar o serviço `backend` e a porta 3000 para o serviço
`frontend`. Estas definições estão descritas no arquivo
`docker-compose/proxy/configs/nginx-template-default.conf`.

Por sua vez, o serviço `database` define a estrutura do banco de dados
PostgreSQL utilizado pelo serviço `backend` para persistir as informações. Como
há uma dependência entre estes serviços, configurou-se um _healthcheck_ que
inicializa o `backend` somente se o `database` está pronto.

Todos os serviços estão configurados para reiniciar sempre que algum problema
ocorrer, tentando aumentar a disponibilidade da aplicação.

## Execução

### Docker

Os serviços `backend` e `frontend` precisam que as imagens de _containers_ sejam
inicializadas. Para tanto, execute os comandos abaixo.

```
GUESS_GAME_VERSION="v1.0"
```

```
docker build . \
    --file ./docker/backend/Dockerfile \
    --tag wandersonwhcr/guess_game_backend:$GUESS_GAME_VERSION
```

```
docker build . \
    --file ./docker/frontend/Dockerfile \
    --tag wandersonwhcr/guess_game_frontend:$GUESS_GAME_VERSION
```

Como resultado, as imagens `wandersonwhcr/guess_game_backend:v1.0` e
`wandersonwhcr/guess_game_frontend:v1.0` serão criadas.

### Docker Compose

O primeiro passo é configurar a senha do banco de dados para que o serviço
`database` seja inicializado e que o serviço `backend` acesse-o da forma
correta. Para tanto, crie um arquivo `.env` com o seguinte comando, onde a
palavra `supersecret` representa a senha a ser configurada.

```
cat > .env <<EOF
DATABASE_PASSWORD=supersecret
EOF
```

> [!NOTE]
> Não se utilizou uma _secret_ do Docker porque este recurso somente está
> disponível no Docker Swarm.

Para iniciar a aplicação e todos os seus serviços, utilize o Docker Compose
através do seguinte comando.

```
docker compose up \
    --detach
```

Isto fará a orquestração dos _containers_ de todos os serviços `backend`,
`frontend`, `proxy` e `database`.

A aplicação estará disponível em http://localhost:3000

## Rede

As redes foram definidas para isolar o acesso entre serviços. O serviço `proxy`
possui acesso somente aos serviços `backend` e `frontend`. Já o serviço
`backend` possui acesso somente aos serviços `proxy` e `database`. Por sua vez,
o serviço `frontend` acessa unicamente o serviço `proxy`. Por fim, o serviço
`database` é acessível só pelo serviço `backend`. Toda esta estrutura está
descrita na imagem abaixo.

![Infraestrutura de Rede do Docker Compose](/docker-compose/network.svg)

## Escalabilidade

A escalabilidade dos serviços `backend` e `frontend` pode ser feita através do
próprio Docker Compose. Por exemplo, para escalar horizontalmente o serviço
`backend` para 10 instâncias e o serviço `frontend` para 3 instâncias, execute o
seguinte comando:

```
docker compose scale backend=10 frontend=3
```

O serviço `proxy` não pode ser escalado porque há uma publicação das portas 3000
e 5000, mapeadas ao _container_. Não há como mapear a mesma porta em múltiplos
_containers_. Para evitar o erro, o serviço `proxy` recebeu uma definição fixa
para nome do _container_, o que inibe a criação de novos _containers_.

Além disso, como o serviço `database` não está configurado para trabalhar em
_cluster_ com outros nós de PostgreSQL, também se definiu um nome de _container_
para evitar horizontalização.

## Atualização

Caso exista a necessidade de alterar o código-fonte dos serviços da aplicação,
deve-se efetuar novamente o _build_ das imagens de _containers_, gerando uma
nova versão. Por exemplo, para criar a versão `v1.1` da aplicação, execute os
seguintes comandos:

```
GUESS_GAME_VERSION="v1.1"
```

```
docker build . \
    --file ./docker/backend/Dockerfile \
    --tag wandersonwhcr/guess_game_backend:$GUESS_GAME_VERSION
```

```
docker build . \
    --file ./docker/frontend/Dockerfile \
    --tag wandersonwhcr/guess_game_frontend:$GUESS_GAME_VERSION
```

Após, adicione a nova versão no arquivo `.env` através do comando:

```
cat >> .env <<EOF
GUESS_GAME_VERSION=$GUESS_GAME_VERSION
EOF
```

Por fim, solicite ao Docker Compose a atualização dos serviços, conforme abaixo.

```
docker compose up backend frontend \
    --detach
```

## Limpeza

Para desligar a aplicação e todos os seus serviços, incluindo a persistência de
informações feitas no banco de dados, execute o seguinte comando:

```
docker compose down \
    --volumes
```

---

Aqui está um exemplo de um arquivo `README.md` para o seu jogo:

---

# Jogo de Adivinhação com Flask

Este é um simples jogo de adivinhação desenvolvido utilizando o framework Flask. O jogador deve adivinhar uma senha criada aleatoriamente, e o sistema fornecerá feedback sobre o número de letras corretas e suas respectivas posições.

## Funcionalidades

- Criação de um novo jogo com uma senha fornecida pelo usuário.
- Adivinhe a senha e receba feedback se as letras estão corretas e/ou em posições corretas.
- As senhas são armazenadas  utilizando base64.
- As adivinhações incorretas retornam uma mensagem com dicas.
  
## Requisitos

- Python 3.8+
- Flask
- Um banco de dados local (ou um mecanismo de armazenamento configurado em `current_app.db`)
- node 18.17.0

## Instalação

1. Clone o repositório:

   ```bash
   git clone https://github.com/fams/guess_game.git
   cd guess-game
   ```

2. Crie um ambiente virtual e ative-o:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate  # Windows
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure o banco de dados com as variáveis de ambiente no arquivo start-backend.sh
    1. Para sqlite

        ```bash
            export FLASK_APP="run.py"
            export FLASK_DB_TYPE="sqlite"            # Use SQLITE
            export FLASK_DB_PATH="caminho/db.sqlite" # caminho do banco
        ```

    2. Para Postgres

        ```bash
            export FLASK_APP="run.py"
            export FLASK_DB_TYPE="postgres"       # Use postgres
            export FLASK_DB_USER="postgres"       # Usuário do banco
            export FLASK_DB_NAME="postgres"       # Nome do Banco
            export FLASK_DB_PASSWORD="secretpass" # Senha do banco
            export FLASK_DB_HOST="localhost"      # Hostname
            export FLASK_DB_PORT="5432"           # Porta
        ```

    3. Para DynamoDB

        ```bash
        export FLASK_APP="run.py"
        export FLASK_DB_TYPE="dynamodb"       # Use postgres
        export AWS_DEFAULT_REGION="us-east-1" # AWS region
        export AWS_ACCESS_KEY_ID="FAKEACCESSKEY123456" 
        export AWS_SECRET_ACCESS_KEY="FakeSecretAccessKey987654321"
        export AWS_SESSION_TOKEN="FakeSessionTokenABCDEFGHIJKLMNOPQRSTUVXYZ1234567890"
        ```

5. Execute o backend

   ```bash
   ./start-backend.sh &
   ```

6. Cuidado! verifique se o seu linux está lendo o arquivo .sh com fim de linha do windows CRLF. Para verificar utilize o vim -b start-backend.sh

## Frontend
No diretorio de frontend

1. Instale o node com o nvm. Se não tiver o nvm instalado, siga o [tutorial](https://github.com/nvm-sh/nvm?tab=readme-ov-file#installing-and-updating)

    ```bash
    nvm install 18.17.0
    nvm use 18.17.0
    # Habilite o yarn
    corepack enable
    ```

2. Instale as dependências do node com o npm:

    ```bash
    npm install
    ```

3. Exporte a url onde está executando o backend e execute o backend.

   ```bash
    export REACT_APP_BACKEND_URL=http://localhost:5000
    yarn start
   ```

## Como Jogar

### 1. Criar um novo jogo

Acesse a url do frontend http://localhost:3000

Digite uma frase secreta

Envie

Salve o game-id


### 2. Adivinhar a senha

Acesse a url do frontend http://localhost:3000

Vá para o endponint breaker

entre com o game_id que foi gerado pelo Creator

Tente adivinhar

## Estrutura do Código

### Rotas:

- **`/create`**: Cria um novo jogo. Armazena a senha codificada em base64 e retorna um `game_id`.
- **`/guess/<game_id>`**: Permite ao usuário adivinhar a senha. Compara a adivinhação com a senha armazenada e retorna o resultado.

### Classes Importantes:

- **`Guess`**: Classe responsável por gerenciar a lógica de comparação entre a senha e a tentativa do jogador.
- **`WrongAttempt`**: Exceção personalizada que é levantada quando a tentativa está incorreta.



## Melhorias Futuras

- Implementar autenticação de usuário para salvar e carregar jogos.
- Adicionar limite de tentativas.
- Melhorar a interface de feedback para as tentativas de adivinhação.

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

