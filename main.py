import time
from datetime import datetime
import pytz
from prettytable import PrettyTable
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas


# Definir o fuso horário de Brasília (GMT-3)
brasil_tz = pytz.timezone('America/Sao_Paulo')


def criar_tabela_e_salvar():
    ind = {
        "Dow Jones": "^DJI",        # Dow Jones
        "S&P 500": "^GSPC",         # S&P 500
        "Nasdaq": "^IXIC",          # Nasdaq
        "NYSE": "^NYA",             # NYSE
        "Nikkei 225": "^N225",      # Nikkei 225
        "Ibovespa": "^BVSP",        # Índice Bovespa (IBOV) da B3
        "SSE Composite": "000001.SS" # SSE Composite
    }

    # Criando os dados para a tabela
    data_tabela = []
    for indice, ticker in ind.items():
        try:
            # Obter dados históricos
            data = yf.Ticker(ticker)
            historico = data.history(period="5d", interval="1d")

            # Verificar se os dados foram obtidos corretamente
            if historico.empty:
                data_tabela.append([indice, "Erro ao buscar", "Erro ao buscar", "Erro ao buscar"])
                continue

            # Preço de fechamento de ontem (penúltimo valor)
            preco_ontem = historico['Close'].iloc[-2]  # O penúltimo valor é o de ontem
            preco_hoje = historico['Close'].iloc[-1]   # O último valor é o de hoje

            # Calcular a variação percentual
            variacao_percentual = ((preco_hoje - preco_ontem) / preco_ontem) * 100

            # Adicionar os dados à tabela
            data_tabela.append([indice, f"R${preco_hoje:.2f}", f"R${preco_ontem:.2f}", f"{variacao_percentual:.2f}%"])

        except Exception as e:
            data_tabela.append([indice, f"Erro: {e}", "Erro: ", "Erro: "])

    # Criar a tabela com o matplotlib
    fig, ax = plt.subplots(figsize=(10, 6))  # Defina o tamanho da imagem
    ax.axis('tight')
    ax.axis('off')

    # Gerar a tabela no gráfico
    table = ax.table(cellText=data_tabela, colLabels=["Índice", "Cotação Atual", "Cotação Ontem", "Variação Percentual"],
                    loc="center", cellLoc="center", colColours=["#f2f2f2"]*4, bbox=[0, 0, 1, 1])

    # Personalizando a aparência da tabela (opcional)
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.auto_set_column_width(col=list(range(len(data_tabela[0]))))

    # Salvar o gráfico como imagem
    plt.savefig('tabela_indices.png', bbox_inches='tight', dpi=300)
    plt.close()

# Chamar a função para criar e salvar a tabela
criar_tabela_e_salvar()



def cotacao_moeda():
    # URLs das cotações
    url_btc = "https://api.polygon.io/v2/aggs/ticker/X:BTCUSD/range/12/hour/2024-12-12/2024-12-13?adjusted=true&sort=asc&apiKey=Lrv0Iz3uYUmT3UCUsLlQeGBaW4Wu4aJ3"
    url_btc_ontem = "https://api.polygon.io/v2/aggs/ticker/X:BTCUSD/prev?adjusted=true&apiKey=Lrv0Iz3uYUmT3UCUsLlQeGBaW4Wu4aJ3"

    url_dolar = "https://api.polygon.io/v2/aggs/ticker/C:USDBRL/range/1/hour/2024-12-12/2024-12-13?adjusted=true&sort=asc&apiKey=Lrv0Iz3uYUmT3UCUsLlQeGBaW4Wu4aJ3"
    url_dolar_ontem = "https://api.polygon.io/v2/aggs/ticker/C:USDBRL/prev?adjusted=true&apiKey=Lrv0Iz3uYUmT3UCUsLlQeGBaW4Wu4aJ3"

    # Lista das URLs a serem consultadas
    lista = [url_btc, url_btc_ontem, url_dolar, url_dolar_ontem]

    # Armazenar os valores obtidos
    valores = []

    # Obtendo os dados das URLs
    for url in lista:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Garante que a requisição foi bem-sucedida
            data = response.json()

            # Extraindo a última cotação ('c') dos resultados
            if "results" in data and len(data["results"]) > 0:
                valores.append(data["results"][0]["c"])
            else:
                valores.append(None)  # Adiciona None se não houver resultados
        except Exception as e:
            print(f"Erro ao acessar {url}: {e}")
            valores.append(None)  # Adiciona None em caso de erro

    # Preparar dados para a tabela
    data = []

    # Bitcoin
    if valores[0] is not None and valores[1] is not None:
        cotacao_atual = valores[1]
        cotacao_ontem = valores[0]
        variacao_percentual = ((cotacao_atual - cotacao_ontem) / cotacao_ontem) * 100
        data.append(["Bitcoin", cotacao_atual, cotacao_ontem, f"{variacao_percentual:.2f}%"])
    else:
        data.append(["Bitcoin", "Erro", "Erro", "Erro"])

    # Dólar
    if valores[2] is not None and valores[3] is not None:
        cotacao_atual = valores[3]
        cotacao_ontem = valores[2]
        variacao_percentual = ((cotacao_atual - cotacao_ontem) / cotacao_ontem) * 100
        data.append(["Dólar", cotacao_atual, cotacao_ontem, f"{variacao_percentual:.2f}%"])
    else:
        data.append(["Dólar", "Erro", "Erro", "Erro"])

    # Criar dataframe com pandas
    df = pd.DataFrame(data, columns=["Moeda", "Cotação Atual", "Cotação Ontem", "Variação Percentual"])

    # Criar tabela com matplotlib
    fig, ax = plt.subplots(figsize=(8, 4))  # Define o tamanho da tabela
    ax.axis("tight")
    ax.axis("off")
    table = ax.table(cellText=df.values, colLabels=df.columns, loc="center", cellLoc="center")

    # Estilizar a tabela
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width(col=list(range(len(df.columns))))

    # Salvar tabela como imagem
    image_path = "cotacao_moeda.png"
    plt.savefig(image_path, bbox_inches="tight", dpi=300)
    plt.close()


def tendencias_twitter():
  url = "https://getdaytrends.com/pt/brazil/"

  headers = {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
  }

  lista = []

  response = requests.get(url, headers=headers)

  if response.status_code == 200:
      soup = BeautifulSoup(response.text, "html.parser")

      links = soup.find_all("a", {"class": "string"})
      spans = soup.find_all("span", {"class": "small text-muted"})

      for i in range(len(links)):
          texto = links[i].text.strip()  # Texto do link
          href = spans[i].text.strip()       # URL do link
          #print(f"Tendência: {texto}")

          lista.append([texto,href])
  else:
      print(f"Erro na requisição: Código {response.status_code}")


  j=1
  texto = "\nTENDÊNCIAS DO TWITTER\n"
  for elemento in lista[:15]:
    texto += f"- Top{j}: " + elemento[0] +" ("+ elemento[1] + ")\n"
    j+=1

  return str(texto)

def noticiasEUA():
  # URL da página
  url = "https://www.terra.com.br/noticias/mundo/estados-unidos/"

  # Fazendo a requisição da página
  response = requests.get(url)

  # Criando o objeto BeautifulSoup
  soup = BeautifulSoup(response.content, 'html.parser')

  # Encontrar todas as tags <a> com a classe específica
  noticias_a = soup.find_all("a", class_="card-news__text--title main-url card-news__url")

  # Contador para limitar a quantidade de notícias
  contador = 0
  lista = []

  # Iterar sobre as notícias e imprimir as 45 primeiras
  for noticia in noticias_a:
      # Encontrar o título da manchete dentro da tag <h3>
      titulo_tag = noticia.find("h3")
      if titulo_tag:
          titulo = titulo_tag.text.strip()
          link = noticia.get('href')

          # Imprimir a manchete e o link
          lista.append([titulo,link])

          contador += 1

      # Limitar a 45 notícias
      if contador >= 45:
          break
  j = 1
  texto = "\nNOTÍCIAS-(EUA)\n"
  for elemento in lista[:5]:
    texto += f"-({j}º): " + elemento[0] +"\n"
    j+=1

  return str(texto)


def noticiasMundo():
    # URL da página
  url = "https://www.terra.com.br/noticias/mundo/"

  # Fazendo a requisição da página
  response = requests.get(url)

  # Criando o objeto BeautifulSoup
  soup = BeautifulSoup(response.content, 'html.parser')

  # Encontrar todas as tags <a> com a classe específica
  noticias_a = soup.find_all("a", class_="card-news__text--title main-url card-news__url")

  # Contador para limitar a quantidade de notícias
  contador = 0
  lista = []

  # Iterar sobre as notícias e imprimir as 45 primeiras
  for noticia in noticias_a:
      # Encontrar o título da manchete dentro da tag <h3>
      titulo_tag = noticia.find("h3")
      if titulo_tag:
          titulo = titulo_tag.text.strip()
          link = noticia.get('href')

          # Imprimir a manchete e o link
          lista.append([titulo,link])

          contador += 1

      # Limitar a 45 notícias
      if contador >= 45:
          break
  j = 1
  texto = "\nNOTÍCIAS-(MUNDO)\n"
  for elemento in lista[:5]:
    texto += f"-({j}º): " + elemento[0] +"\n"
    j+=1

  return str(texto)


def noticiasBrasil():
    # URL da página
  url = "https://www.terra.com.br/noticias/brasil/"

  # Fazendo a requisição da página
  response = requests.get(url)

  # Criando o objeto BeautifulSoup
  soup = BeautifulSoup(response.content, 'html.parser')

  # Encontrar todas as tags <a> com a classe específica
  noticias_a = soup.find_all("a", class_="card-news__text--title main-url card-news__url")

  # Contador para limitar a quantidade de notícias
  contador = 0
  lista = []

  # Iterar sobre as notícias e imprimir as 45 primeiras
  for noticia in noticias_a:
      # Encontrar o título da manchete dentro da tag <h3>
      titulo_tag = noticia.find("h3")
      if titulo_tag:
          titulo = titulo_tag.text.strip()
          link = noticia.get('href')

          # Imprimir a manchete e o link
          lista.append([titulo,link])

          contador += 1

      # Limitar a 45 notícias
      if contador >= 45:
          break
  j = 1
  texto = "\nNOTÍCIAS-(BRASIL)\n"
  for elemento in lista[:5]:
    texto += f"-({j}º): " + elemento[0] +"\n"
    j+=1

  return str(texto)

def noticiasEuropa():
  # URL da página
  url = "https://www.terra.com.br/noticias/mundo/europa/"

  # Fazendo a requisição da página
  response = requests.get(url)

  # Criando o objeto BeautifulSoup
  soup = BeautifulSoup(response.content, 'html.parser')

  # Encontrar todas as tags <a> com a classe específica
  noticias_a = soup.find_all("a", class_="card-news__text--title main-url card-news__url")

  # Contador para limitar a quantidade de notícias
  contador = 0
  lista = []

  # Iterar sobre as notícias e imprimir as 45 primeiras
  for noticia in noticias_a:
      # Encontrar o título da manchete dentro da tag <h3>
      titulo_tag = noticia.find("h3")
      if titulo_tag:
          titulo = titulo_tag.text.strip()
          link = noticia.get('href')

          # Imprimir a manchete e o link
          lista.append([titulo,link])

          contador += 1

      # Limitar a 45 notícias
      if contador >= 45:
          break
  j = 1
  texto = "\nNOTÍCIAS-(EUROPA)\n"
  for elemento in lista[:5]:
    texto += f"-({j}º): " + elemento[0] +"\n"
    j+=1

  return str(texto)

def verificar_horario():
    while True:
        # Obtém o horário atual no fuso horário de Brasília
        agora = datetime.now(brasil_tz)

        # Verifica se o horário é 11:00 ou posterir
        if agora.hour >= 11:
            print("Já passou das 11:00! Executando a ação...")
            break
        time.sleep(30)


def montando_resumo_diario_parte1():
  mensagem = ""
  mensagem = "--[===--_RESUMO_DIÁRIO_--===]--\n\n"
  mensagem += "Inicialmente, apresentamos um panorama dos principais índices das bolsas de valores globais, incluindo o Dow Jones (composto pelas 50 maiores empresas dos EUA), o S&P 500 (que reúne as 500 maiores empresas dos EUA), o NASDAQ Composite (índice que abrange empresas listadas na bolsa Nasdaq), o NYSE Composite (índice que reflete as ações da Bolsa de Nova York) e o Ibovespa (índice da B3, a principal bolsa de valores brasileira). A seguir, detalharemos cada um desses índices:\n"

  return str(mensagem)

def montando_resumo_diario_parte2():
  mensagem = ""
  mensagem += "\n\n" + "Em seguida, apresentamos as cotações do Bitcoin em dólares e do dólar em reais:\n"
  return str(mensagem)

def montando_resumo_diario_parte3():
  mensagem = ""
  mensagem += "\n\n" + "Para completar temos as manchetes do dia de hoje:\n"
  mensagem += noticiasMundo()
  mensagem += noticiasEUA()
  mensagem += noticiasBrasil()
  mensagem += noticiasEuropa()
  return str(mensagem)

def montando_resumo_diario_parte4():
  mensagem =""
  mensagem += "Por fim, apresentamos os 15 tópicos mais comentados no Twitter, para termos uma visão mais clara sobre o que está gerando discussão entre as pessoas:\n"
  mensagem += tendencias_twitter()
  return mensagem


def enviar_mensagem():
  ACCESS_TOKEN = "EAANG9NEFMh8BOZBEezsJ2ZAIu5ehsZBBNw4mwikcXKwoAQq0G8dIckrv6SvGEJI9RX0Pn4ZCZBLnbqRt2ZBB7CTFfDzJCQl1TSN1tpXhPLRh12S3qMFp3P5bPt1sd0HcuLsNyfWISbKeSws17aNvdHZA9Mih0U55cBPVVnoB9oZAR2wNuU2qX3cHrpG7"
  PHONE_NUMBER_ID = "442911302250068"  # ID do número configurado no Meta
  WHATSAPP_NUMBER = "5511916162004"  # Número de destino (com código do país)

  url = f"https://graph.facebook.com/v16.0/{PHONE_NUMBER_ID}/messages"

  headers = {
      "Authorization": f"Bearer {ACCESS_TOKEN}",
      "Content-Type": "application/json"
  }


  criar_tabela_e_salvar() #Criando tabela dos indices
  cotacao_moeda() #Criando tabela das contações

  time.sleep(10)
  mensagem1 = montando_resumo_diario_parte1()
  mensagem2 = montando_resumo_diario_parte2()
  mensagem3 = montando_resumo_diario_parte3()
  mensagem4 = montando_resumo_diario_parte4()







  data1 = {
      "messaging_product": "whatsapp",
      "to": WHATSAPP_NUMBER,
      "type": "text",
      "text": {"body": mensagem1}
  }

  image_path1 = "tabela_indices.png"  # Certifique-se de que o arquivo exista neste local

  # Para enviar imagens locais, primeiro você deve fazer o upload do arquivo para o servidor Meta
  upload_url = f"https://graph.facebook.com/v16.0/{PHONE_NUMBER_ID}/media"

  # Upload do arquivo de imagem
  with open(image_path1, "rb") as img:
      files = {
          "file": ("tabela_indices.png", img, "image/png")  # Tipo MIME especificado
      }
      params = {
          "messaging_product": "whatsapp"
      }
      upload_headers = {
          "Authorization": f"Bearer {ACCESS_TOKEN}"
      }

      # Enviar a imagem para o Meta para obter um ID de mídia
      upload_response = requests.post(upload_url, headers=upload_headers, files=files, data=params)

  # Verificar se o upload foi bem-sucedido
  if upload_response.status_code == 200:
      media_id = upload_response.json().get("id")  # Obter o ID da mídia carregada
      print(f"Upload bem-sucedido. Media ID: {media_id}")
  else:
      print("Erro no upload da imagem:", upload_response.status_code, upload_response.json())

    # Criar a mensagem com o ID da mídia carregada
  message_data1 = {
        "messaging_product": "whatsapp",
        "to": WHATSAPP_NUMBER,
        "type": "image",
        "image": {
            "id": media_id  # Referenciar o ID da mídia carregada
        }
    }

  data3 = {
      "messaging_product": "whatsapp",
      "to": WHATSAPP_NUMBER,
      "type": "text",
      "text": {"body": mensagem2}
  }


  image_path2 = "cotacao_moeda.png"  # Certifique-se de que o arquivo exista neste local
  upload_url = f"https://graph.facebook.com/v16.0/{PHONE_NUMBER_ID}/media"

  # Upload do arquivo de imagem
  with open(image_path2, "rb") as img:
      files = {
          "file": ("cotacao_moeda.png", img, "image/png")  # Tipo MIME especificado
      }
      params = {
          "messaging_product": "whatsapp"
      }
      upload_headers = {
          "Authorization": f"Bearer {ACCESS_TOKEN}"
      }

      # Enviar a imagem para o Meta para obter um ID de mídia
      upload_response = requests.post(upload_url, headers=upload_headers, files=files, data=params)

  # Verificar se o upload foi bem-sucedido
  if upload_response.status_code == 200:
      media_id = upload_response.json().get("id")  # Obter o ID da mídia carregada
      print(f"Upload bem-sucedido. Media ID: {media_id}")
  else:
      print("Erro no upload da imagem:", upload_response.status_code, upload_response.json())

    # Criar a mensagem com o ID da mídia carregada
  message_data2 = {
        "messaging_product": "whatsapp",
        "to": WHATSAPP_NUMBER,
        "type": "image",
        "image": {
            "id": media_id  # Referenciar o ID da mídia carregada
        }
    }



  data5 = {
      "messaging_product": "whatsapp",
      "to": WHATSAPP_NUMBER,
      "type": "text",
      "text": {"body": mensagem3}
  }

  data6 = {
      "messaging_product": "whatsapp",
      "to": WHATSAPP_NUMBER,
      "type": "text",
      "text": {"body": mensagem4}
  }

  #Teste

  response = requests.post(url, headers=headers, json=data1)
  print(response.status_code, response.json())
  time.sleep(5)

  response = requests.post(url, headers=headers, json=message_data1)
  if response.status_code == 200:
      print("Mensagem enviada com sucesso!")
  else:
      print("Erro ao enviar mensagem:", response.status_code, response.json())

  time.sleep(5)
  response = requests.post(url, headers=headers, json=data3)
  print(response.status_code, response.json())


  time.sleep(5)

  response = requests.post(url, headers=headers, json=message_data2)
  if response.status_code == 200:
      print("Mensagem enviada com sucesso!")
  else:
      print("Erro ao enviar mensagem:", response.status_code, response.json())

  time.sleep(5)

  response = requests.post(url, headers=headers, json=data5)
  print(response.status_code, response.json())

  response = requests.post(url, headers=headers, json=data6)
  print(response.status_code, response.json())

def executar_se_18_30():
    fuso_horario_brasil = pytz.timezone("America/Sao_Paulo")
    horario_atual = datetime.now(fuso_horario_brasil)
    
    if horario_atual.hour >= 18 and horario_atual.minute >= 20:
        enviar_mensagem()
    else:
        print("Ainda não são 18:30 no Brasil.")

if __name__ == "__main__":
    executar_se_18_30()