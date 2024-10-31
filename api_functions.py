import requests
import threading



def process_file_in_background(file_key):
    bucket_name = "meetingtranscriptionscms"  # Substitua pelo nome real do bucket S3
    file_json = file_key.split('.')[0] + '.json'
    
    # Chamar o process-transcription
    success_transcription = call_process_transcription(bucket_name, file_json)
    if success_transcription:
        print(f"Arquivo {file_key} processado com sucesso!")

        return True
    else:
        print(f"Erro ao processar o arquivo {file_key}")
        return False

def upload_file_to_s3(file_name, file_content, content_type):
    try:
        # Etapa 1: Gerar o presigned URL para o upload
        response = requests.get(f"http://3.92.130.222:8000/generate-presigned-url/?file_name={file_name}")
        
        if response.status_code != 200:
            print(f"Erro ao obter presigned URL: {response.status_code}")
            return False
        
        presigned_url = response.json().get('url')

        if not presigned_url:
            print("Erro: URL assinada não retornada.")
            return False


        # Faz o upload do arquivo lido
        # Etapa 2: Fazer o upload do arquivo para o S3 usando o presigned URL
        headers = {'Content-Type': content_type}
        print(presigned_url)
        upload = requests.put(presigned_url, data=file_content, verify=True)

        print("aqui")

        if upload.status_code != 200:
            print(f"Erro no upload: {upload.status_code} Detalhe: {upload.text}")
            return False

        print("Upload bem-sucedido!")

        # Chamar o webhook após o upload completo
        success_webhook = notify_webhook(file_name)
        if success_webhook:
            print(f"Webhook chamado com sucesso para {file_name}")
            
            # Iniciar o processamento em segundo plano

            success_gpt = process_file_in_background(file_name)

            if success_gpt:
                return True
            
            else:
                print("falhou na chamada do gpt para o arquivo")
                return False
        else:
            print(f"Falha ao chamar o webhook para {file_name}")
            return False

    
    except Exception as e:
        print(f"Erro ao fazer o upload: {e}")
        return False

def notify_webhook(file_name):
    try:
        webhook_url = "http://3.92.130.222:8000/webhook/file-uploaded/"

        # Etapa 3: Notificar o webhook
        response = requests.post(webhook_url, json={"file_name": file_name})
        if response.status_code != 200:
            print(f"Erro ao enviar webhook: {response.status_code}")
            return False  # Retorna False em caso de erro
        print(f"Webhook enviado com sucesso: {response.json()}")
        return True
    except Exception as e:
        print(f"Erro ao notificar webhook: {e} detalhe: {response.text}")
        return False



def call_process_transcription(bucket_name, file_key):
    try:
        # URL do endpoint de processamento na EC2
        fastapi_url = "http://3.92.130.222:8000/process-transcription/"
        
        # Dados para enviar para o endpoint
        payload = {
            "bucket_name": bucket_name,
            "file_key": file_key
        }

        # Faz a requisição POST para o endpoint de process-transcription
        response = requests.post(fastapi_url, json=payload)

        # Verifica se o processo foi bem-sucedido
        if response.status_code == 200:
            print("Processamento da transcrição feito com sucesso.")
            return True
        else:
            print(f"Erro ao processar a transcrição: {response.text}")
            return False

    except Exception as e:
        print(f"Erro ao chamar process-transcription: {str(e)}")
        return False
