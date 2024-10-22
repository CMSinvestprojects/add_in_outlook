import requests



def upload_file_to_s3(file):
    try:
        # Etapa 1: Gerar o presigned URL para o upload
        response = requests.get(f"http://3.92.130.222:8000/generate-presigned-url/?file_name={file.filename}")
        
        # Verifique se a resposta tem o presigned URL
        if response.status_code != 200:
            print(f"Erro ao obter presigned URL: {response.status_code}")
            return False
        
        presigned_url = response.json().get('url')

        if not presigned_url:
            print("Erro: URL assinada não retornada.")
            return False

        # Etapa 2: Fazer o upload do arquivo para o S3 usando o presigned URL
        files = {'file': (file.filename, file.stream, file.content_type)}
        upload = requests.put(presigned_url, data=file.read())

        if upload.status_code != 200:
            print(f"Erro no upload: {upload.status_code}")
            return False  # Retorna False em caso de erro

        print("Upload bem-sucedido!")
        return True
    
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
        print(f"Erro ao notificar webhook: {e}")
        return False

