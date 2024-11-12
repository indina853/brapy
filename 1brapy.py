import pickle
import os.path
import time
import openai
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# -*- coding: utf-8 -*-

# id da planilha
spreadsheet_id = 'YOUR_SPREEDSHEET_ID'

# nome da aba da planilha
sheet_name = 'YOIR_SPREEDSHIT_NAME'

# carrega as credenciais salvas ou solicita as credenciais ao usuário
creds = None
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'YOUR_JSON_CLIENT_SECRET_FILE',
            ['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        creds = flow.run_local_server(port=0)
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

# cria uma instância da API do Google Sheets
service = build('sheets', 'v4', credentials=creds)

# faz uma chamada para a API do Google Sheets para extrair os dados da planilha
sheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
sheets = sheet.get('sheets', '')
sheet_map = {}
for sheet in sheets:
    title = sheet.get("properties", {}).get("title", "Outros")
    sheet_id = sheet.get("properties", {}).get("sheetId", 0)
    sheet_map[title] = sheet_id

# faz uma chamada para a API do Google Sheets para extrair os dados da planilha
ranges = ['Outros!H7:H', 'Outros!I7:I', 'Outros!J7:J', 'Outros!L7:L', 'Outros!M7:M', 'Outros!O7:O', 'Outros!P7:P']
rows = []

for r in ranges:
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=r).execute()
    rows.append(result.get('values', []))

# salva a pergunta e o link em seus respectivos arquivos de saída
with open("result.txt", "w", encoding='utf-8') as f, open("pu.txt", "w", encoding='utf-8') as f2:
    line_numbers = []  # armazena os números das linhas exibidas no arquivo de saída
    for i, (rows1, rows2, rows3, rows4, rows5, rows6, rows7) in enumerate(zip(*rows)):
        if rows1 and not rows3 and not rows5 and not rows7 and not (rows4 == 'FALSE') and not (rows6 == 'FALSE'):
            rows1 = rows1[0].strip("[]").lstrip("'")
            rows2 = rows2[0].strip("[]")
            line_number = i+7  # salva o número da linha em uma variável
            line_numbers.append(line_number)  # adiciona o número da linha à lista
            f.write("Pergunta da linha {}: {}\n".format(line_number, rows1))
            f2.write("Link para a pergunta da linha {}: {}\n".format(line_number, rows2))

# adiciona a chave de API do OpenAI
openai.api_key = "YOUR_OPENAI_API_KEY"

# define o modelo de linguagem GPT a ser usado
model_engine = "text-davinci-003"

# define o arquivo com as perguntas
file_name = "result.txt"

# define o arquivo para salvar as respostas
output_file_name = "qa.txt"

# define o arquivo para salvar as palavras-chave
keywords_file_name = "rw.txt"

# abre o arquivo de saída
with open(output_file_name, "w", encoding='utf-8') as f_out:
    
    # abre o arquivo de saída para as palavras-chave
    with open(keywords_file_name, "w", encoding='utf-8') as k_out:

        # lê as perguntas do arquivo e itera sobre cada pergunta
        with open(file_name, "r", encoding='utf-8') as f_in:
            line_number_index = 0  # índice para iterar sobre a lista de números das linhas exibidas
            for i, question in enumerate(f_in, start=1):
                # remove o caractere de quebra de linha (\n) da pergunta
                question = question.strip()

                # verifica se a pergunta já foi respondida
                line_number = line_numbers[line_number_index]
                print(f"Já respondi a pergunta da linha {line_number}.")

                # gera a resposta para a pergunta usando o modelo GPT
                response = openai.Completion.create(
                    engine=model_engine,
                    prompt=question,
                    temperature=0,
                    max_tokens=3048,
                    top_p=1,
                    presence_penalty=0.0,
                    frequency_penalty=0.0,
                    stop=None
                    )

                # obtém a primeira resposta gerada pelo modelo
                answer = response.choices[0].text.strip()

                # salva a resposta no arquivo de saída
                f_out.write(f"Resposta para a pergunta da linha {line_number}: {answer}\n")

                # espera 0.6 segundos antes de prosseguir para a próxima pergunta
                time.sleep(0.6)

                line_number_index += 1

                # extrai as palavras-chave da resposta
                keywords = openai.Completion.create(
                    model=model_engine,
                    prompt=f"Extraia as palavras-chave deste texto:\n\n{answer}",
                    temperature=0.5,
                    max_tokens=60,
                    top_p=1.0,
                    frequency_penalty=0.8,
                    presence_penalty=0.0
                    )

                # obtém a primeira lista de palavras-chave gerada pelo modelo
                keyword_list = [choice.text.strip() for choice in keywords.choices]

                # formata a string de palavras-chave para remover o prefixo "Keywords: "
                keyword_string = ", ".join(keyword_list).replace("Palavras-chave: ", "").replace("[", "").replace("]", "").replace("'", "")

                # escreve as palavras-chave no arquivo
                k_out.write(f"Palavras-chave para a pergunta da linha {line_number}: {keyword_string}\n")

            # lista de palavras a serem removidas (preposições e pronomes)
            # remove_words = ['de', 'a', 'o', 'que', 'e', 'do', 'da', 'em', 'um', 'para', 'com', 'não', 'uma', 'os', 'no', 'se', 'na', 'por', 'mais', 'as', 'dos', 'como', 'mas', 'ao', 'ele', 'das', 'à', 'seu', 'sua', 'ou', 'quando', 'muito', 'nos', 'já', 'eu', 'também', 'só', 'pelo', 'pela', 'até', 'isso', 'ela', 'entre', 'depois', 'sem', 'mesmo', 'aos', 'seus', 'quem', 'nas', 'me', 'esse', 'eles', 'você', 'essa', 'num', 'nem','suas', 'meu', 'às', 'minha', 'numa', 'pelos', 'elas', 'qual', 'nós', 'lhe', 'deles', 'essas', 'esses', 'pelas', 'este', 'dele', 'tu', 'te', 'vocês', 'vos', 'lhes', 'meus', 'minhas', 'teu', 'tua', 'teus', 'tuas', 'nosso', 'nossa', 'nossos', 'nossas', 'dela', 'delas', 'sobre', 'através de', 'abaixo de', 'acima de', 'após', 'antes', 'até', 'com', 'contra', 'de', 'desde', 'em', 'entre', 'para', 'perante', 'por', 'sem', 'sob', 'sobre', 'nós', 'vós', 'me', 'te', 'lhe', 'nos', 'vos', 'lhes', 'mim', 'ti', 'si', 'consigo', 'mim mesmo', 'ti mesmo', 'si mesmo', 'conosco', 'convosco', 'se', 'aquele', 'aquela', 'aquilo', 'este', 'esta', 'isto', 'esse', 'essa', 'isso', 'aqueles', 'aquelas', 'estes', 'estas', 'esses', 'essas', 'mesmo', 'próprio', 'alguém', 'ninguém', 'tudo', 'algo', 'cada', 'outro', 'tanto', 'quanto', 'qualquer', 'demasiado', 'bastante', 'diversos', 'poucos', 'muitos', 'tal']