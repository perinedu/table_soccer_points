
# Tabela de Pontuação do Campeonato Brasileiro Série A

Este projeto é um script de Python que utiliza Selenium para fazer web scraping da tabela de pontuação do Campeonato Brasileiro Série A. O script coleta dados de jogos, incluindo resultados e possivelmente outras estatísticas, de um site de esportes e os organiza em uma tabela estruturada usando pandas.

## Funcionalidades

- **Coleta de dados automatizada**: Executa web scraping do site [Flashscore](https://www.flashscore.com/football/brazil/serie-a/results/) para obter resultados de jogos do Campeonato Brasileiro Série A.
- **Tratamento de dados**: Usa expressões regulares e pandas para limpar e organizar os dados coletados em um formato de tabela útil.
- **Geração de tabela estruturada**: Cria uma tabela com os dados dos jogos, pronta para análise ou exportação para outros formatos como CSV.

## Tecnologias Utilizadas

- Python 3
- Selenium
- Pandas
- Expressões Regulares

## Configuração e Uso

### Pré-requisitos

Para executar este script, você precisará ter o Python 3 instalado em seu sistema, juntamente com as bibliotecas Selenium e pandas. Além disso, é necessário ter o Chromedriver instalado e configurado para corresponder à versão do seu navegador Chrome.

### Instalação

1. Clone o repositório para o seu sistema local.
2. Instale as dependências necessárias usando o pip:

```bash
pip install selenium pandas
```

3. Atualize o caminho para o seu Chromedriver no script (`C:/chromedriver.exe`).

### Execução

Execute o script a partir da linha de comando:

```bash
python cod_completo.py
```

## Contribuições

Contribuições para o projeto são bem-vindas. Para contribuir, por favor, crie um fork do repositório, faça suas alterações e envie um pull request.


