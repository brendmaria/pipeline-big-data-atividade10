# Pipeline de Telemetria Meshtastic — Projeto Integrador de Big Data

Pipeline desenvolvido para a Atividade 10 de Projeto Integrador de Big Data, sob orientação do professor Allan Siriani (`github.com/siriani`). O projeto lê pacotes brutos de telemetria armazenados na coleção `pacotes_brutos` do MongoDB, aplica regras de higienização e validação, grava a série limpa no MariaDB e atualiza o último valor de cada nó e métrica no Redis.

## 1. Arquitetura e Serviços

Ambiente orquestrado via Docker Compose (`docker-compose.yml`) na rede `rede-pipeline` e containerizado com `Dockerfile`:

- **MongoDB (`brenda_mongo`):** armazena os pacotes brutos na coleção `pacotes_brutos` (porta `27017`).
- **MariaDB (`brenda_mariadb`):** banco `agridata` (porta `3306`).
- **Redis:** armazena o último valor de cada nó e métrica na chave `brenda:{origem}:{metrica}`.
- **Aplicação Python (`src/pipeline.py` e `src/queries.py`):** ingestão em ciclos de 10 segundos e consultas analíticas.

## 2. Esquema do Banco de Dados

No MariaDB (`agridata`), a estrutura criada na inicialização é:

- **`brenda_serie_limpa` (série limpa em formato longo):**
  - `id INT AUTO_INCREMENT PRIMARY KEY`
  - `no_origem VARCHAR(50)`
  - `instante DATETIME`
  - `metrica VARCHAR(50)`
  - `valor FLOAT`
- **`brenda_agregados_hora` (agregados por hora — estrutura criada, ainda não populada automaticamente):**
  - `id INT AUTO_INCREMENT PRIMARY KEY`
  - `no_origem VARCHAR(50)`
  - `hora DATETIME`
  - `metrica VARCHAR(50)`
  - `media FLOAT`
  - `minimo FLOAT`
  - `maximo FLOAT`

## 3. Tratamento de Qualidade dos Dados e Consultas

O pipeline lê os pacotes disponíveis na coleção `pacotes_brutos` do MongoDB a cada ciclo — com a ressalva de que nesta etapa foram utilizados pacotes de teste inseridos manualmente no MongoDB local, e o controle de deduplicação/ponteiro de leitura fica em memória (sem persistência entre reinicializações):

- **Contadores no terminal:** `[LOG] Duplicatas: 1 | Relógio inválido: 1 | Quarentena: 1` (1 de cada por execução com os pacotes de teste).
- **Duplicatas:** deduplicação pela chave `(nó de origem + id do pacote)`, nunca pelo conteúdo (`1` descartada por ciclo nos testes).
- **Relógio inválido:** timestamps anteriores a 2024 são substituídos pelo instante de processamento (`1` por ciclo nos testes).
- **Quarentena:** pacotes sem nó de origem ou sem payload vão para quarentena e são contabilizados (`1` por ciclo nos testes).
- **Buracos e atrasos:** não implementados nesta versão.

### Consultas previstas (`src/queries.py`)
1. **Bateria média por nó e por dia (`QUERY_BATERIA_MEDIA`):** calcula `AVG(valor)` para `metrica = 'bateria'` agrupado por `no_origem` e `DATE(instante)`.
2. **Utilização do canal por hora (`QUERY_UTILIZACAO_CANAL`):** calcula `AVG(valor)` para `metrica = 'canal'` agrupado por `no_origem` e `HOUR(instante)`.
3. **Tempo de silêncio de cada nó:** não implementada nesta versão.

## 4. Segurança e Credenciais

As credenciais ficam exclusivamente no arquivo `.env` na raiz do projeto (ignorado pelo `.gitignore`). Use o arquivo `src/.env.example` como modelo:

```env
MARIADB_ROOT_PASSWORD=exemplo_senha_root
DB_PASSWORD=exemplo_senha_banco
DB_HOST=127.0.0.1