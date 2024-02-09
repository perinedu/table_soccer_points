import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

nomeCampeonato = 'brasileirao_A'
# Configuração do Selenium
options = webdriver.ChromeOptions()
options.add_argument("--disable-features=SameSiteByDefaultCookies, CookiesWithoutSameSiteMustBeSecure")

s = Service('C:/chromedriver.exe')  # Caminho para o seu chromedriver
driver = webdriver.Chrome(service=s, options=options)
driver.maximize_window()

# URL do campeonato específico
url = 'https://www.flashscore.com/football/brazil/serie-a/results/'
driver.get(url)

# Aceitar cookies
try:
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'button#onetrust-accept-btn-handler')))
    button_cookies = driver.find_element(By.CSS_SELECTOR, 'button#onetrust-accept-btn-handler')
    button_cookies.click()
except Exception as e:
    print("Cookies já aceitos ou botão não encontrado.")

# Expandir a lista de jogos
for _ in range(4):
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.event__more.event__more--static')))
        botao_mostrar_mais = driver.find_element(By.XPATH, "//a[text()='Show more matches']")
        driver.execute_script("arguments[0].scrollIntoView();", botao_mostrar_mais)
        driver.execute_script("arguments[0].click();", botao_mostrar_mais)
        time.sleep(3)  # Espera para carregar os jogos
    except TimeoutException:
        print("Não foi possível encontrar ou clicar no botão 'Mostrar mais jogos'.")
        break
    except Exception as e:
        print(f"Erro ao tentar clicar no botão 'Mostrar mais jogos': {e}")
        break

# Coletar dados dos jogos
dados_jogos = []
elementos_jogos = driver.find_elements(By.CSS_SELECTOR, 'div.event__match.event__match--static.event__match--twoLine')
for elemento in elementos_jogos:
    try:
        time_casa = elemento.find_element(By.CSS_SELECTOR, 'div.event__participant.event__participant--home').text
        time_fora = elemento.find_element(By.CSS_SELECTOR, 'div.event__participant.event__participant--away').text
        gols_casa = elemento.find_element(By.CSS_SELECTOR, 'div.event__score.event__score--home').text
        gols_fora = elemento.find_element(By.CSS_SELECTOR, 'div.event__score.event__score--away').text
        gols_casa_1t = elemento.find_element(By.CSS_SELECTOR, 'div.event__part.event__part--home').text.replace('(', '').replace(')', '')
        gols_fora_1t = elemento.find_element(By.CSS_SELECTOR, 'div.event__part.event__part--away').text.replace('(', '').replace(')', '')
        dados_jogos.append([time_casa, gols_casa, gols_casa_1t, '-', gols_fora, gols_fora_1t, time_fora])
    except Exception as e:
        print(f"Erro ao extrair dados de um jogo: {e}")

# Fechar o navegador
driver.quit()

# Converter a lista de dados dos jogos em um DataFrame do pandas
df_jogos = pd.DataFrame(dados_jogos, columns=[
    'Casa', 'Gols Casa', 'Gols Casa 1T', 'Traço', 'Gols Visitante',
    'Gols Visitante 1T', 'Visitante'
])

# Converter colunas de gols para numérico e calcular os gols do segundo tempo
df_jogos['Gols Casa'] = pd.to_numeric(df_jogos['Gols Casa'], errors='coerce')
df_jogos['Gols Casa 1T'] = pd.to_numeric(df_jogos['Gols Casa 1T'], errors='coerce')
df_jogos['Gols Visitante'] = pd.to_numeric(df_jogos['Gols Visitante'], errors='coerce')
df_jogos['Gols Visitante 1T'] = pd.to_numeric(df_jogos['Gols Visitante 1T'], errors='coerce')
df_jogos['Gols Casa 2T'] = df_jogos['Gols Casa'] - df_jogos['Gols Casa 1T']
df_jogos['Gols Visitante 2T'] = df_jogos['Gols Visitante'] - df_jogos['Gols Visitante 1T']

# Função para calcular as estatísticas
def calcular_estatisticas(df, equipes, contexto='Geral', tempo='Total'):
    colunas = [
        'P', 'J', 'V', 'E', 'D', 'GP', 'GC', 'SG', 'AbM', 'GF 1', 'GF 2', 'GF 3+',
        'GS 1', 'GS 2', 'GS 3+', 'MGV 1', 'MGV 2', 'MGV 3+', 'MGD 1', 'MGD 2', 'MGD 3+'
    ]
    estatisticas = pd.DataFrame(0, index=equipes, columns=colunas)

    for _, jogo in df.iterrows():
        casa, gols_casa, gols_casa_1T, _, gols_visitante, gols_visitante_1T, visitante = jogo[:7]
        gols_casa = int(gols_casa) if pd.notnull(gols_casa) else 0
        gols_visitante = int(gols_visitante) if pd.notnull(gols_visitante) else 0
        gols_casa_1T = int(gols_casa_1T) if pd.notnull(gols_casa_1T) else 0
        gols_visitante_1T = int(gols_visitante_1T) if pd.notnull(gols_visitante_1T) else 0
        gols_casa_2T = gols_casa - gols_casa_1T
        gols_visitante_2T = gols_visitante - gols_visitante_1T
        
        ambos_marcaram = gols_casa > 0 and gols_visitante > 0

        if tempo == 'Primeiro':
            gols_feitos_casa = gols_casa_1T
            gols_feitos_visitante = gols_visitante_1T
        elif tempo == 'Segundo':
            gols_feitos_casa = gols_casa_2T
            gols_feitos_visitante = gols_visitante_2T
        else:
            gols_feitos_casa = gols_casa
            gols_feitos_visitante = gols_visitante

        # Atualiza as estatísticas para as equipes
        for equipe, gols_feitos in [(casa, gols_feitos_casa), (visitante, gols_feitos_visitante)]:
            if (contexto == 'Geral') or (contexto == 'Casa' and equipe == casa) or (contexto == 'Fora' and equipe == visitante):
                estatisticas.at[equipe, 'J'] += 1
                estatisticas.at[equipe, 'GP'] += gols_feitos
                estatisticas.at[equipe, 'GC'] += gols_feitos_casa if equipe == visitante else gols_feitos_visitante
                
                # Determina vitória, empate ou derrota
                if gols_feitos > (gols_feitos_casa if equipe == visitante else gols_feitos_visitante):
                    estatisticas.at[equipe, 'V'] += 1
                    estatisticas.at[equipe, 'P'] += 3
                elif gols_feitos == (gols_feitos_casa if equipe == visitante else gols_feitos_visitante):
                    estatisticas.at[equipe, 'E'] += 1
                    estatisticas.at[equipe, 'P'] += 1
                else:
                    estatisticas.at[equipe, 'D'] += 1
                
                # Atualização da estatística "Ambos Marcaram"
                if ambos_marcaram:
                    estatisticas.at[equipe, 'AbM'] += 1

                # Gols feitos
                if gols_feitos == 1:
                    estatisticas.at[equipe, 'GF 1'] += 1
                elif gols_feitos == 2:
                    estatisticas.at[equipe, 'GF 2'] += 1
                elif gols_feitos >= 3:
                    estatisticas.at[equipe, 'GF 3+'] += 1

                # Gols sofridos
                gols_sofridos = gols_feitos_casa if equipe == visitante else gols_feitos_visitante
                if gols_sofridos == 1:
                    estatisticas.at[equipe, 'GS 1'] += 1
                elif gols_sofridos == 2:
                    estatisticas.at[equipe, 'GS 2'] += 1
                elif gols_sofridos >= 3:
                    estatisticas.at[equipe, 'GS 3+'] += 1

                # Margem de vitória ou derrota
                margem = abs(gols_feitos - gols_sofridos)
                if gols_feitos > gols_sofridos:
                    if margem == 1:
                        estatisticas.at[equipe, 'MGV 1'] += 1
                    elif margem == 2:
                        estatisticas.at[equipe, 'MGV 2'] += 1
                    elif margem >= 3:
                        estatisticas.at[equipe, 'MGV 3+'] += 1
                elif gols_feitos < gols_sofridos:
                    if margem == 1:
                        estatisticas.at[equipe, 'MGD 1'] += 1
                    elif margem == 2:
                        estatisticas.at[equipe, 'MGD 2'] += 1
                    elif margem >= 3:
                        estatisticas.at[equipe, 'MGD 3+'] += 1
                

    # Calcular o saldo de gols
    estatisticas['SG'] = estatisticas['GP'] - estatisticas['GC']

    # Ordenar as estatísticas
    estatisticas.sort_values(by=['P', 'V', 'SG', 'GP'], ascending=[False, False, False, False], inplace=True)

    return estatisticas


# Utilize a função calcular_estatisticas para calcular as estatísticas
equipes = pd.unique(df_jogos[['Casa', 'Visitante']].values.ravel('K'))
estatisticas_gerais = calcular_estatisticas(df_jogos, equipes, 'Geral', 'Total')
estatisticas_primeiro_tempo = calcular_estatisticas(df_jogos, equipes, 'Geral', 'Primeiro')
estatisticas_segundo_tempo = calcular_estatisticas(df_jogos, equipes, 'Geral', 'Segundo')
estatisticas_casa = calcular_estatisticas(df_jogos[df_jogos['Casa'].isin(equipes)], equipes, 'Casa', 'Total')
estatisticas_fora = calcular_estatisticas(df_jogos[df_jogos['Visitante'].isin(equipes)], equipes, 'Fora', 'Total')
estatisticas_primeiro_tempo_casa = calcular_estatisticas(df_jogos[df_jogos['Casa'].isin(equipes)], equipes, 'Casa', 'Primeiro')
estatisticas_segundo_tempo_casa = calcular_estatisticas(df_jogos[df_jogos['Casa'].isin(equipes)], equipes, 'Casa', 'Segundo')
estatisticas_primeiro_tempo_fora = calcular_estatisticas(df_jogos[df_jogos['Visitante'].isin(equipes)], equipes, 'Fora', 'Primeiro')
estatisticas_segundo_tempo_fora = calcular_estatisticas(df_jogos[df_jogos['Visitante'].isin(equipes)], equipes, 'Fora', 'Segundo')

# Salvar as estatísticas em um arquivo Excel
with pd.ExcelWriter(f'{nomeCampeonato}_tabela.xlsx') as writer:
    estatisticas_gerais.to_excel(writer, sheet_name='Geral')
    estatisticas_primeiro_tempo.to_excel(writer, sheet_name='Primeiro Tempo')
    estatisticas_segundo_tempo.to_excel(writer, sheet_name='Segundo Tempo')
    estatisticas_casa.to_excel(writer, sheet_name='Casa')
    estatisticas_fora.to_excel(writer, sheet_name='Fora')
    estatisticas_primeiro_tempo_casa.to_excel(writer, sheet_name='Primeiro Tempo Casa')
    estatisticas_segundo_tempo_casa.to_excel(writer, sheet_name='Segundo Tempo Casa')
    estatisticas_primeiro_tempo_fora.to_excel(writer, sheet_name='Primeiro Tempo Fora')
    estatisticas_segundo_tempo_fora.to_excel(writer, sheet_name='Segundo Tempo Fora')

print("Processo concluído. As estatísticas foram salvas no arquivo Excel.")
