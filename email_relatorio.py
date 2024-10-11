from email_scrapper_functions import InfosUsuario
import win32com.client
import pythoncom


#formacao do texto em txt depois 
class RelatorioReuniao:

    def __init__(self,cod_cliente,engine):
        pythoncom.CoInitialize()  

        self._iu = InfosUsuario(cod_cliente,engine)
        self._df_mapao = self._iu.mapao()
        self._df_extrato = self._iu.extrato()
        self._df_planilhao = self._iu.planilhao()

        self.body = f"<p>Olá! Pretende fazer reunião com o cliente {cod_cliente}<p>"

        outlook = win32com.client.Dispatch('outlook.application')
        self._mail = outlook.CreateItem(0x0)
        self._mail.Subject = f"Reunião {cod_cliente} | {self._iu.nome()}"
    
    def __formatar_tempo(self,valor):
        return f"{valor:_.2f}".replace(".", ",").replace("_", ".")

    def bullet_list_generica(self,lista_texto):
        self.body += "<ul>"
        for i in lista_texto:
            self.body += f"<li>{i.capitalize()}</li>"

        self.body += "</ul>"
        pass

    def bullet_list_alocacao(self,lista_texto,dict_opc):
        self.body += "<ul>"
        for i in lista_texto:
            valor_formatado = self.__formatar_tempo(round(dict_opc[i][1],2))            
            self.body += f"<li>{i.capitalize()} R$ {valor_formatado}</li>"

        self.body += "</ul>"
        pass

    def criar_email(self):
        self._mail.HTMLBody = self.body
        self._mail.Send()

    def destinatario(self,email):
        self._mail.To = email
        


    def texto_planilhao(self):
        #ver o que esta over 
        opcoes = ['liquidez','pos','pre','inflacao','multimercados','fundoImob','acoes','alternativos']

        portifolio = self._df_planilhao.loc[0,"portfolio_ideal"] 
        aderencia = self._df_planilhao.loc[0,"aderencia"] 

        over,under,lista_valores = [],[],[]
        value_under,value_over = 0,0

        for i in opcoes:
            lista_valores.append([])
            status =  self._df_planilhao.loc[0,f'status_{i}']
            valor = self._df_planilhao.loc[0,f'variacao_{i}']
            lista_valores[-1] = [status,valor]
            if status =="OVER":
                over.append(i)
                #preciso aora do detalhamento e armazenar aqui 
                value_over += valor
            elif status == "UNDER":
                under.append(i)
                value_under += valor
        #ver qnt posso sair 
        dict_opc = dict(zip(opcoes,lista_valores))
        # print(over,under)
        # print(dict_opc)
        self.body += f"A partir do planilhão temos que o cliente tem perfil {int(portifolio)}, está com uma aderência de {float(round(aderencia*100,2))}%,"
        # if len(over) !=0:
        self.body += "e também é possivel analisar que o seu cliente está com posição <b>Over</b>, nas seguintes classes:"
        self.bullet_list_alocacao(over,dict_opc)
        self.body += f"Totalizando: R$ {self.__formatar_tempo(round(value_over,2))}"

            # if len(under) !=0:
        self.body += "<br>e <b>Under</b>:"
        self.bullet_list_alocacao(under,dict_opc)
        self.body += f"Totalizando: R$ {self.__formatar_tempo(round(value_under,2))} "
        self.body += "<br>Baseado nisso as seguintes movimentações parecem ser coerentes:"
        #raciocinio de retirada de posições problematicas primeiro do q ta over 
        #depois de aplicação sem estourar o limite, tudo mt delicdado aqui, varias condções 
        #
        
