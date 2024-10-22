from email_scrapper_functions import InfosUsuario
import win32com.client
import pythoncom
import pandas as pd
pd.options.mode.chained_assignment = None 


#formacao do texto em txt depois 
class RelatorioReuniao:

    def __init__(self,cod_cliente,engine):
        self.estilo = """
                <html>
                <head>
                <style>
                .dataframe {
                    font-size: 20px;
                    font-family: 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif;
                    text-align: center;
                    white-space: nowrap;
                    width: 70%;
                    
                    border-collapse: collapse;
                }

                    .dataframe tbody tr:nth-child(odd) {
                        background-color: #ffffff; /* Color for odd rows */
                    }
                
                    .dataframe tbody tr {
                    height: 50px; /* Set the height for each row */
                }

                    /* For even rows within .dataframe within a div */
                    .dataframe tbody tr:nth-child(even) {
                        background-color: #D9D9D9; /* Color for even rows */
                    }

                .dataframe thead tr {
                    text-align: center;
                    color: #f5f5f5;
                    background-color: rgb(34, 97, 23);
                }
                </style>
                </head>
                <body>
                """
        self.final = """
        </body>
        </html>
        """
        pythoncom.CoInitialize()  

        self._iu = InfosUsuario(cod_cliente,engine)
        self._df_mapao = self._iu.mapao()
        self._df_extrato = self._iu.extrato()
        self._df_planilhao = self._iu.planilhao()
        self._df_patrimonio = self._iu.rentabilidade()
        self._df_captacao = self._iu.captacao()

        self.body = f"<p>Olá! Pretende fazer reunião com o cliente {cod_cliente}<p>"

        outlook = win32com.client.Dispatch('outlook.application')
        self._mail = outlook.CreateItem(0x0)
        self._mail.Subject = f"Reunião {cod_cliente} | {self._iu.nome()}"

    def titulo_area(self,title):
        self.body += f"<h2>{title}</h2>"

    def __coluna_str(self,colunas,df):
        for i in colunas:
            df[i] = df[i].map("{:_.2f}".format).str.replace(".",",").str.replace("_",".")

    def __fake_pct(self,colunas,df):
        for i in colunas:
            df[i] = df[i].astype(str) + "%"

    
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
            self.body += f"<li>{i.capitalize()} R$ {valor_formatado} |     Ideal {round(100*dict_opc[i][2],2)}%  e  Atual {round(100*dict_opc[i][3],2)}%</li>"

        self.body += "</ul>"
        pass

    def criar_email(self):
        self._mail.HTMLBody = self.body
        self._mail.Display()

    def destinatario(self,email="teste.teste@teste.com.br"):
        self._mail.To = email

    def estruturar_email(self):
        self.texto_planilhao()
        self.texto_mapao()
        self.tabela_patrimonio()
        self.criar_email()

    def texto_mapao(self):
        self.titulo_area("Check List Financeiro")
        self.body += f"<p>A partir do checklist financeiro do cliente, levantamos algumas perguntas e tópicos interessantes para fazer para o cliente</p>"
        df = self._df_mapao
        rm_fields = ['cod_cliente', 'nome', 'patrimonio_declarado', 'net', 'perfil_suitability',
            'data_atualizacao', 'index', 'filhos']
        

        cols = list(set(df.columns) - set(rm_fields))

        cont_notna = df[cols].notna().sum(axis=1)

        result = pd.concat([cont_notna, df[ 'cod_cliente']], axis=1)
        
        result.columns = ['n_preenchidos', 'cod_cliente']

        result['percentual'] = 100*result['n_preenchidos']/(len(cols))
        
        if result.loc[0,"percentual"] < 40:
            self.body += f"""<p>Cliente tem apenas {round(result.loc[0,"percentual"],2)}% do Check-List Financeiro preenchido, aproveitar a reunião para coletar 
                            as informações necessárias</p>"""
        #aqui é fazer o bate bola com os valores e depois sim ou n 
        self.body += "<ul>"
            
        #casado
        if df.loc[0,'estado_civil'] == "casado" and (df.loc[0,'nome_conjuge'] == None or df.loc[0,'nome_conjuge'] == ""):
            self.body += f"<li>Cliente é <b>casado</b>, porém não possui nome do Conjuge registrado</li>"
        
        #verificar receita
        
        
        if (df.loc[0,'despesas'] != None and df.loc[0,'despesas'] != "") or (df.loc[0,'receitas'] != None and df.loc[0,'receitas'] != ""):
            self.body += f"<li>Foi registrado uma despesa anual de R$ {df.loc[0,'despesas']} e receita anual de R$ {df.loc[0,'receitas']}. Esse valor ainda se mantem</li>"
            self.body += f"""<li>Enquanto no extrato da captação vemos que nos ultimos 12 meses:<ol>
                                <li>Aportes: {'{:_.2f}'.format(round(self._df_captacao['aportes'].sum(),2)).replace('.',',').replace('_','.')} o que é mensalmente: {'{:_.2f}'.format(round(self._df_captacao['aportes'].sum()/12,2)).replace('.',',').replace('_','.')}</li>
                                <li>Retiradas: {'{:_.2f}'.format(round(self._df_captacao['retiradas'].sum(),2)).replace('.',',').replace('_','.')} o que é mensalmente: {'{:_.2f}'.format(round(self._df_captacao['retiradas'].sum()/12,2)).replace('.',',').replace('_','.')}</li>
                                 </ol>
                             </li>"""
        
        #
        if df.loc[0, "calculo_aposentadoria"] =="s":
            self.body += f'<li>Cálculo para aposentadoria é uma preocupação <a data-fr-linked="true" href="https://cmsbi.com/simulador_aposentadoria">https://cmsbi.com/simulador_aposentadoria</a></li>'
        self.body += "</ul>"

        mapa_oportundiades = ['previdencia','seguros_pf','seguros_pj','cambio_pf','cambio_pj','credito_pf','credito_pj','planejamento_patrimonial','trafalgar','conta_internacional']
        traducao_mapa_oportunidades = ['Previdência','Seguro na PF','Seguro na PJ','Câmbio na PF','Câmbio na PJ','Crédito na PF','Crédito na PJ', 'Planejamento Patrimonial (Pava)','Trafalgar','Investimentos no Exterior']
        dict_mapao = dict(zip(mapa_oportundiades,traducao_mapa_oportunidades))


        aux = "<p>Referente ao <b>Mapa de Oportunidades</b> os seguintes tópicos os clientes responderem 'Não, mas pode fazer'/'Sim, mas não comigo ou pode mais':"
        aux += "<ul>"
        verify=False
        for i in dict_mapao:
            if df.loc[0,i] == "2" or df.loc[0,i] == "3" :
                verify = True
                aux += f'<li>{dict_mapao[i]}</li>'
        aux += "</ul>"
        if verify:
            self.body += aux
        
    def tabela_patrimonio(self):
        self.titulo_area("Patrimônio")
        df = self._df_patrimonio
        df['variacao_patrimonial'] = df['patrimonio_final'] - df['patrimonio_inicial']
        df = df[['data','patrimonio_inicial', 'aportes_e_retiradas', 'ir_pago','patrimonio_final', 'variacao_patrimonial', 'rent_mes', 'rent_mes_cdi', 'rent_ano','rent_ano_cdi']]
        
        df['data'] = pd.to_datetime(df['data'], dayfirst=True)#.strftime('%b-%y')
        df['data'] = df['data'].dt.strftime('%b-%y')

        aux = f"""
                        <tr>
                            <td><b>Anual</b></td>
                            <td><b>{'{:_.2f}'.format(round(df.loc[0,"patrimonio_inicial"],2)).replace('.',',').replace('_','.')}</b></td>
                            <td><b>{'{:_.2f}'.format(round(df['aportes_e_retiradas'].sum(),2)).replace('.',',').replace('_','.')}</b></td>
                            <td><b>{'{:_.2f}'.format(round(df['ir_pago'].sum(),2)).replace('.',',').replace('_','.')}</b></td>
                            <td><b>{'{:_.2f}'.format(round(df.loc[df.index[-1],"patrimonio_final"],2)).replace('.',',').replace('_','.')}</b></td>
                            <td><b>{'{:_.2f}'.format(round(df['variacao_patrimonial'].sum(),2)).replace('.',',').replace('_','.')}</b></td>
                            <td><b>{round(df.loc[df.index[-1],"rent_ano"],2)}%</b></td>
                            <td><b>{round(df.loc[df.index[-1],"rent_ano_cdi"],2)}%</b></td>
                        </tr>
                        </tbody>
                        </table>

                    """
        
        df['rent_mes'] = round(df['rent_mes'],2)
        df['rent_mes_cdi'] = round(df['rent_mes_cdi'],2)
        self.__coluna_str(['patrimonio_inicial', 'aportes_e_retiradas', 'ir_pago','patrimonio_final', 'variacao_patrimonial'],df)
        self.__fake_pct(['rent_mes', 'rent_mes_cdi', 'rent_ano','rent_ano_cdi'],df)
        df = df[['data','patrimonio_inicial', 'aportes_e_retiradas', 'ir_pago','patrimonio_final', 'variacao_patrimonial', 'rent_mes', 'rent_mes_cdi']]
        df.rename(columns={"data":"Data","patrimonio_inicial":"Patrimônio Inicial","aportes_e_retiradas":"Aportes e Retiradas","ir_pago":"IR Pago","patrimonio_final":"Patrimônio Final",'variacao_patrimonial':"Variação Patrimonial",'rent_mes':"Rentabildiae Bruta","rent_mes_cdi":"Rentabilidade Bruta (% CDI)"}, inplace=True)
        df_html = df.to_html(na_rep="",index=False, border=0)
        df_html = self.estilo + df_html
        df_html = df_html.replace("</tbody>",'').replace("</table>","")
        df_html += aux + self.final
          
        self.body += df_html

    def texto_planilhao(self):
        self.titulo_area("Planilhão")
        #ver o que esta over 
        opcoes = ['liquidez','pos','pre','inflacao','multimercados','fundoImob','acoes','alternativos']
        try:
            portifolio = self._df_planilhao.loc[0,"portfolio_ideal"] 
        except:
            self.body += "<p> Cliente esta ausente no planilhao</p>"
            return False
        aderencia = self._df_planilhao.loc[0,"aderencia"] 

        over,under,lista_valores = [],[],[]
        value_under,value_over = 0,0

        for i in opcoes:
            lista_valores.append([])
            status =  self._df_planilhao.loc[0,f'status_{i}']
            valor = self._df_planilhao.loc[0,f'variacao_{i}']
            ideal = self._df_planilhao.loc[0,f'{i}_ideal']
            atual = self._df_planilhao.loc[0,i]
            lista_valores[-1] = [status,valor,ideal,atual]
            if status =="OVER":
                over.append(i)
                #preciso aora do detalhamento e armazenar aqui 
                value_over += valor
            elif status == "UNDER":
                under.append(i)
                value_under += valor
        #ver qnt posso sair 
        dict_opc = dict(zip(opcoes,lista_valores))
        self.body += f"A partir do planilhão temos que o cliente tem perfil {int(portifolio)} e NET {self._df_planilhao.loc[0,'PL']}, está com uma aderência de <b>{float(round(aderencia*100,2))}%</b>,"
        # if len(over) !=0:
        self.body += "e também é possivel analisar que o seu cliente está com posição <b>Over</b>, nas seguintes classes:"
        self.bullet_list_alocacao(over,dict_opc)
        self.body += f"Totalizando: R$ {self.__formatar_tempo(round(value_over,2))}"

            # if len(under) !=0:
        self.body += "<br>e <b>Under</b>:"
        self.bullet_list_alocacao(under,dict_opc)
        self.body += f"Totalizando: R$ {self.__formatar_tempo(round(value_under,2))} "
        # self.body += "<br>Baseado nisso as seguintes movimentações parecem ser coerentes:"
        #raciocinio de retirada de posições problematicas primeiro do q ta over 
        #depois de aplicação sem estourar o limite, tudo mt delicdado aqui, varias condções 
        return True
        
        
if __name__ == "__main__":
    from database import engine
    
    rr = RelatorioReuniao(3130085 ,engine)
    # rr = RelatorioReuniao(354748 ,engine)
    
    # rr = RelatorioReuniao(9673555 ,engine)
    rr.estruturar_email()

    # print(pd.read_sql_query("SELECT * from captacao_por_cliente cpc where cod_cliente = 7851089", engine))
