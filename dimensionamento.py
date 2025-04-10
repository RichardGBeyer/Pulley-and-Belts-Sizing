from math import pi, sqrt, asin, degrees, ceil
from interpolacao import interpolar_valor
from dados_incorporados import (
    dados_Motores,
    dados_Carcaça,
    dados_3V,
    dados_Mancal,
    dados_QuantidadeCorreias3V,
    dados_LARGURA_3V
)

def dimensionar(rotacao_bomba_valor, freq_motor_valor, num_polos_valor, potencia_motor_valor, modelo_mancal_valor):
    try:
        # Calcula a rotação do motor (fórmula: (120 * frequência) / número de pólos)
        rotacao_motor = ((120 * freq_motor_valor)*0.98) / num_polos_valor
        # Define a faixa de tolerância de +3% a +10% para a rotação da bomba
        rotacao_bomba_min = rotacao_bomba_valor * 1.03  # Mínimo é 3% acima da rotação esperada
        rotacao_bomba_max = rotacao_bomba_valor * 1.10  # Máximo é 10% acima da rotação esperada

        # Encontra o diâmetro do eixo do motor com base na carcaça
        motor_selecionado = next(
            (motor for motor in dados_Motores if motor['KW'] == potencia_motor_valor and motor['Polos'] == num_polos_valor),
            None
        )
        if not motor_selecionado:
            raise ValueError("Motor não encontrado nos dados.")
        carcaça_motor = str(motor_selecionado['Carcaça'])
        eixo_motor = next((carcaça['Eixo'] for carcaça in dados_Carcaça if str(carcaça['Carcaça']) == carcaça_motor), None)
        if not eixo_motor:
            raise ValueError("Carcaça do motor não encontrada nos dados.")

        # Diâmetro mínimo da polia motora (máximo entre 70 mm e 1,3 vezes o diâmetro do eixo do motor)
        diametro_minimo_polia_motora = max(70, 1.3 * eixo_motor)
        # Garantir que o valor seja tratado como float antes de usar .is_integer()
        diametro_minimo_polia_motora = float(diametro_minimo_polia_motora)
        # Arredonda o diâmetro mínimo para o próximo valor inteiro
        if diametro_minimo_polia_motora.is_integer():
            diametro_minimo_polia_motora = int(diametro_minimo_polia_motora)
        else:
            diametro_minimo_polia_motora = int(diametro_minimo_polia_motora) + 1

        # Itera sobre os dados de mancal para buscar a polia movida inicial
        solucao_encontrada = False
        for mancal in dados_Mancal:
            if mancal['Tamanho'] != modelo_mancal_valor:
                continue  # Pula se o modelo do mancal não corresponder ao informado pelo usuário

            # Novo: Verifica limitante do eixo do mancal
            eixo_mancal = mancal.get('Eixo', 0) 
            if eixo_motor > 1.4 * eixo_mancal:
                continue  # Pula este mancal se não atender ao limitante

            # Lista de polias movidas disponíveis (ordenada)
            polias_movidas = sorted([float(dado['PoliaMovida']) for dado in dados_Mancal])
            idx_polia_movida_inicial = polias_movidas.index(float(mancal['PoliaMovida']))
            # Itera sobre as polias movidas, começando pela inicial e aumentando gradualmente
            for idx_polia_movida in range(idx_polia_movida_inicial, len(polias_movidas)):
                polia_movida = polias_movidas[idx_polia_movida]
                # Inicializa o diâmetro da polia motora com o valor mínimo
                diametro_polia_motora = diametro_minimo_polia_motora
                # Itera sobre possíveis diâmetros da polia motora
                while diametro_polia_motora <= 4 * diametro_minimo_polia_motora:  # Limite máximo de iteração
                    # Calcula a relação de transmissão
                    relacao_transmissao_calculada = polia_movida / diametro_polia_motora
                    # Calcula a rotação da bomba com esta combinação de polias
                    rotacao_bomba_calculada = rotacao_motor / relacao_transmissao_calculada
                    # Verifica se a rotação da bomba está dentro da faixa de tolerância (+3% a +10%)
                    if rotacao_bomba_min <= rotacao_bomba_calculada <= rotacao_bomba_max:
                        # Verifica todas as correias disponíveis
                        for correia in dados_3V:
                            comprimento_correia = float(correia['Comprimento'])
                            # Fórmula para calcular a distância entre centros
                            termo1 = comprimento_correia - (pi / 2) * (diametro_polia_motora + polia_movida)
                            termo2 = termo1**2 - 2 * (polia_movida - diametro_polia_motora)**2
                            if termo2 < 0:  # Evita raízes negativas
                                continue
                            distancia_centros = (termo1 + sqrt(termo2)) / 4
                            # Verifica se a distância entre centros é viável
                            if 0.7 * (diametro_polia_motora + polia_movida) <= distancia_centros <= 2 * (diametro_polia_motora + polia_movida):
                                # Calcula o ângulo de contato na polia motora
                                angulo_contato_rad = pi - 2 * asin(abs(polia_movida - diametro_polia_motora) / (2 * distancia_centros))
                                angulo_contato_graus = degrees(angulo_contato_rad)
                                # Verifica se o ângulo de contato é maior ou igual a 120°
                                if angulo_contato_graus >= 120:
                                    # Verifica se a redução é maior que 6
                                    if relacao_transmissao_calculada > 6:
                                        print(f"Combinação descartada: Redução ({relacao_transmissao_calculada:.2f}) maior que 6.")
                                        break  # Descarta esta combinação e continua procurando
                                    solucao_encontrada = True
                                    melhor_combinacao = {
                                        'CarcaçaMotor': carcaça_motor,  # Armazena a carcaça do motor
                                        'PoliaMotora': diametro_polia_motora,
                                        'PoliaMovida': polia_movida,
                                        'RotacaoBombaCalculada': rotacao_bomba_calculada,
                                        'RelacaoTransmissao': relacao_transmissao_calculada,
                                        'Correia': correia['Correia'],
                                        'Comprimento': comprimento_correia,
                                        'DistanciaCentros': distancia_centros,
                                        'AnguloContato': angulo_contato_graus
                                    }
                                    break  # Sai do loop de correias se encontrar uma solução válida
                        if solucao_encontrada:
                            break  # Sai do loop de diâmetros da polia motora se encontrar uma solução válida
                    # Incrementa o diâmetro da polia motora para a próxima iteração
                    diametro_polia_motora += 1  # Incremento de 1 mm (valores inteiros)
                if solucao_encontrada:
                    break  # Sai do loop de polias movidas se encontrar uma solução válida
            if solucao_encontrada:
                break  # Sai do loop de mancais se encontrar uma solução válida

        if solucao_encontrada:
            # Converte a potência do motor para CV
            potencia_motor_cv = potencia_motor_valor * 1.35962
            # Interpola a potência transmitida por correia
            potencia_por_correia = interpolar_valor(rotacao_motor, melhor_combinacao['PoliaMotora'], dados_QuantidadeCorreias3V)
            # Calcula a quantidade de correias necessárias
            quantidade_correias = ceil(potencia_motor_cv / potencia_por_correia)
            # Busca a largura da polia
            largura_polia = buscar_largura_polia(quantidade_correias)

            # === Cálculo da Massa das Polias ===
            densidade = 7800  # kg/m³ (ferro fundido)
            diametro_motora = melhor_combinacao['PoliaMotora']

            # Converter mm para metros
            raio_motora = (diametro_motora / 2) / 1000
            espessura = largura_polia / 1000  # largura_polia já é a espessura em mm

            # Volume = π * raio² * espessura
            volume_motora = pi * (raio_motora ** 2) * espessura

            massa_motora = volume_motora * densidade

            # Constrói o resultado final
            resultado = (
                f"Informações para Fornecedor:\n\n"
                f"Tipo de Correia: V\n"  
                f"Configuração: 3\n"
                f"Quantidade de Correias: {quantidade_correias}\n"
                f"Diâmetro Motora (Dm): {melhor_combinacao['PoliaMotora']} mm\n"
                f"Diâmetro Movida (da): {melhor_combinacao['PoliaMovida']} mm\n"
                f"Distância entre Centros(DC): {melhor_combinacao['DistanciaCentros']:.0f} mm\n"
                f"Largura da Polia: {largura_polia} mm\n"
                f"Medida X: {(largura_polia/2):.1f} mm\n"
                f"Angulo (β): 90°\n"
                f"Massa da Polia Motora: {massa_motora:.1f} kg\n\n"
                f"-----------------------------------------------------------------------------\n\n"
                f"Informações para Engenharia\n\n"
                f"Melhor combinação encontrada:\n"
                f"Diâmetro Motora (Dm): {melhor_combinacao['PoliaMotora']} mm\n"
                f"Diâmetro Movida (da): {melhor_combinacao['PoliaMovida']} mm\n"
                f"Distância entre Centros(DC): {melhor_combinacao['DistanciaCentros']:.0f} mm\n"
                f"Carcaça do Motor: {melhor_combinacao['CarcaçaMotor']}\n"
                f"Rotação da Bomba Calculada: {melhor_combinacao['RotacaoBombaCalculada']:.0f} rpm\n"
                f"Relação de Transmissão: {melhor_combinacao['RelacaoTransmissao']:.1f}\n"
                f"Correia selecionada:\n"
                f"Modelo: {melhor_combinacao['Correia']}\n"
                f"Comprimento: {melhor_combinacao['Comprimento']} mm\n"
                f"Ângulo de Contato: {melhor_combinacao['AnguloContato']:.1f}°\n"
                f"Potência do Motor: {potencia_motor_cv:.0f} CV / {potencia_motor_valor:.0f} kW\n"
                f"Potência Transmitida por Correia: {potencia_por_correia:.1f} CV\n"
                f"Quantidade de Correias: {quantidade_correias}\n"
                
                
                
            )
        else:
            resultado = "Nenhuma combinação de polias e correias encontrada que atenda aos critérios. Verifique os pontos abaixo:\n" \
            "1- Redução não pode ser maior que 6.\n" \
            "   1.1 - Sugestão: Alterar a quantidade de pólos do motor ou o modelo de bomba.\n"\
            "2- Potência do motor muito alta para o tamanho de bomba.\n"\
            "   2.1 - Sugestão: Verifique a potência necessária para a aplicação.\n"
        return resultado
    except Exception as e:
        return f"Erro: {e}"

def buscar_largura_polia(quantidade_correias):
    """
    Busca a largura da polia com base na quantidade de correias.
    Se a quantidade exata não existir, retorna a largura da próxima polia maior.
    """
    # Dados de largura para correias 3V
    dados_largura = dados_LARGURA_3V
    chave_correias = "POLIA 3V"
    # Ordena os dados pela quantidade de correias
    dados_largura.sort(key=lambda x: x[chave_correias])
    # Encontra a largura correspondente ou a próxima maior
    for dado in dados_largura:
        if dado[chave_correias] >= quantidade_correias:
            return dado['LARGURA']
    # Se não encontrar, retorna a maior largura disponível
    return dados_largura[-1]['LARGURA']