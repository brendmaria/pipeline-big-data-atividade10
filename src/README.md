# Pipeline Contínuo de Big Data — Atividade 10 (IAL220)

Projeto desenvolvido para a disciplina **Projeto Integrador de Big Data** (2026.2) da **Fatec Pompéia — Shunji Nishimura**, ministrada pelo professor **Allan Siriani** ([github.com/siriani](https://github.com/siriani)).

**Autora:** Brenda Maria Sabino Moreira (`brendmaria`)  
**Repositório:** [pipeline-big-data-atividade10](https://github.com/brendmaria/pipeline-big-data-atividade10)

---

## 1. Estrutura do Projeto

* `src/pipeline.py`: Script principal do pipeline contínuo de ingestão, tratamento e persistência.
* `src/queries.py`: Consultas analíticas e respostas operacionais sobre os dados processados.
* `docker-compose.yml`: Orquestração dos serviços em contentores Docker.
* `Dockerfile`: Definição do ambiente de execução Python.
* `requirements.txt`: Dependências do projeto (`pymongo`, `mysql-connector-python`, `redis`, etc.).

---

## 2. Arquitetura e Decisões de Modelagem

O pipeline consome os pacotes brutos de telemetria da coleção somente leitura `pacotes_brutos` do MongoDB, aplica o tratamento de qualidade de dados e persiste os resultados utilizando o **prefixo obrigatório `brenda_`**:

1. **Série Limpa (`brenda_serie_limpa` — MariaDB):** Armazena as leituras normalizadas em formato longo (`no_id`, `instante_recebimento`, `metrica`, `valor`), utilizando o timestamp de recebimento no gateway como referência temporal para contornar problemas de relógio nos nós.
2. **Agregados Horários (`brenda_agregados_hora` — MariaDB):** Consolida métricas estatísticas (`media`, `minimo`, `maximo`, `contagem`) agrupadas por janela de 1 hora.
3. **Estado Atual (`brenda:<no_id>:<metrica>` — Redis):** Mantém o último valor de cada sensor em memória para acesso imediato e de baixa latência.

---

## 3. Tratamento dos Quatro Problemas de Dados Brutos

* **Duplicatas:** Deduplicação implementada com base na chave composta `(no_origem, packet_id)`.
* **Relógio errado:** Utilização do instante de chegada no gateway como eixo temporal principal.
* **Buracos e atrasos:** Ausências de pacotes modeladas explicitamente nas janelas temporais sem interpolação silenciosa.
* **Esquema variável:** Separação por tipo de pacote e validação rigorosa de campos na ingestão em Python, contabilizando descartes e rejeições.

---

## 4. Como Executar

1. Suba o ambiente com o Docker Compose:
   ```bash
   docker-compose up -d --build