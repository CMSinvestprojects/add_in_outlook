from datetime import datetime
import pytz
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
import pandas as pd

class InfosUsuario:

    def __init__(self,cod_cliente,engine) -> None:
        self._cod_cliente = cod_cliente
        self._engine = engine

    def __shorten_name(self,full_name):
        parts = full_name.split()
        if len(parts) < 2:
            return full_name  # In case there's no middle name, just return the full name

        first_name = parts[0]
        middle_initial = parts[1][0].upper()  # Take the first letter of the middle name

        return f"{first_name} {middle_initial}."
        
    def mapao(self):
        df = pd.read_sql_query(f"SELECT * from formulario_clientes fc WHERE cod_cliente = {self._cod_cliente}", self._engine)
        return df
    
    def extrato(self):
        """
        funcao que pega o extrato como um todo durante os ultimos 12 meses

        incialmente de forma local
        idealmente do banco
        """
        # versao banco
        # query  = f"""
        #             SELECT
        #             *
        #             FROM
        #             proventos_extrato pe 
        #             WHERE
        #             data_pagamento  >= DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 12 MONTH), '%Y-%m-01')
        #             AND `data_pagamento` < DATE_FORMAT(NOW(), '%Y-%m-01')
        #             and cod_cliente = {self.cod_cliente}
        #             LIMIT 1048575
        #         """
        # df = pd.read_sql_query(query, self._engine)

        df = pd.read_excel("extrato.xlsx")
        
        
        df = df[df['cod_cliente'] == self._cod_cliente]
        return df
    
    def planilhao(self):
        df = pd.read_sql_query(f"SELECT * from planilhao p where cliente = {self._cod_cliente}",self._engine)
        return df

    def movimentacao_rf(self):
        df = pd.read_sql_query(f"SELECT * from planilhao p where codigo_cliente = {self._cod_cliente}",self._engine)
        return df

    def nome(self):
        try:
            return self.__shorten_name(pd.read_sql_query(f"select * from info_clientes where cod_cliente={self._cod_cliente}", self._engine)['nome_cliente'].to_list()[0].capitalize())
        except:
            return "Cliente Não Identificado"
        
    def rentabilidade(self):
        df = pd.read_sql_query(f"SELECT * FROM rentabilidades WHERE YEAR(data) = YEAR(CURRENT_DATE) and cod_cliente = {self._cod_cliente}", self._engine)
        return df
    
    def captacao(self):
        """
        retona a captacao dos uiltimos 12 meses do cliente
        """
        df = pd.read_sql_query(f"SELECT * from captacao_por_cliente cpc where cod_cliente = {self._cod_cliente} and tipo_de_captacao = 'TED' and data >= (now() - INTERVAL 12 MONTH )",self._engine)
        return df
    


load_dotenv()

class EmailCreator:

    def __init__(self):
        now = datetime.utcnow().replace(tzinfo=pytz.utc)
        now = now.replace(tzinfo=None)

        smtphost = 'smtp.gmail.com'
        smtpport = 587
        self._username = os.getenv('email')
        password = os.getenv("senha_app")
    
        self._msg = MIMEMultipart('alternative')
        self._msg['From'] = self._username
        self._server = smtplib.SMTP(smtphost, smtpport)
        self._server.ehlo()
        self._server.starttls()
        self._server.login(self._username, password)
        self.body = ""
    
    def destinatario(self,email_dest):
        self._mailto = email_dest
        self._msg['To'] = email_dest

    def enviar_email(self):
        htmlbody = MIMEText(self.body, 'html')
        self._msg.attach(htmlbody)
        self._server.sendmail(self._username, self._mailto, self._msg.as_bytes())
        self._server.close()


    def asssunto(self,subject):
        self._msg['Subject'] = subject
