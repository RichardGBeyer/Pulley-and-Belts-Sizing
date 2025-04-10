# interpolacao.py
import numpy as np

def interpolar_valor(rpm_motor, diametro_polia_motora, dados):
    try:
        # Extrai os diâmetros das polias motoras (primeira linha)
        diametros_polia = [float(d) for d in list(dados[0].values())[1:] if isinstance(d, (int, float)) and d > 0]
        diametros_polia.sort()

        # Extrai os RPMs disponíveis
        rpm_disponiveis = [float(linha['Rpm Eixo Motor']) for linha in dados[1:] if linha['Rpm Eixo Motor'] != 0]
        rpm_disponiveis.sort()

        # Encontra os índices dos RPMs mais próximos
        idx_rpm_menor = np.searchsorted(rpm_disponiveis, rpm_motor, side='right') - 1
        idx_rpm_maior = np.searchsorted(rpm_disponiveis, rpm_motor, side='left')

        # Garante que os índices estejam dentro dos limites
        idx_rpm_menor = max(0, idx_rpm_menor)
        idx_rpm_maior = min(len(rpm_disponiveis) - 1, idx_rpm_maior)

        # Extrai as linhas correspondentes aos RPMs
        linha_rpm_menor = next((linha for linha in dados[1:] if float(linha['Rpm Eixo Motor']) == rpm_disponiveis[idx_rpm_menor]), None)
        linha_rpm_maior = next((linha for linha in dados[1:] if float(linha['Rpm Eixo Motor']) == rpm_disponiveis[idx_rpm_maior]), None)

        if not linha_rpm_menor or not linha_rpm_maior:
            raise ValueError("Dados insuficientes para interpolação.")

        # Extrai os valores de potência para os diâmetros de polia disponíveis
        potencias_rpm_menor = [float(linha_rpm_menor[f'Unnamed: {i}']) for i in range(1, len(diametros_polia) + 1)]
        potencias_rpm_maior = [float(linha_rpm_maior[f'Unnamed: {i}']) for i in range(1, len(diametros_polia) + 1)]

        # Encontra os índices dos diâmetros de polia mais próximos
        idx_diametro_menor = np.searchsorted(diametros_polia, diametro_polia_motora, side='right') - 1
        idx_diametro_maior = np.searchsorted(diametros_polia, diametro_polia_motora, side='left')

        # Garante que os índices estejam dentro dos limites
        idx_diametro_menor = max(0, idx_diametro_menor)
        idx_diametro_maior = min(len(diametros_polia) - 1, idx_diametro_maior)

        # Extrai os valores de potência para interpolação
        potencia_menor_menor = potencias_rpm_menor[idx_diametro_menor]
        potencia_menor_maior = potencias_rpm_menor[idx_diametro_maior]
        potencia_maior_menor = potencias_rpm_maior[idx_diametro_menor]
        potencia_maior_maior = potencias_rpm_maior[idx_diametro_maior]

        # Interpolação linear nos diâmetros de polia
        if diametros_polia[idx_diametro_maior] - diametros_polia[idx_diametro_menor] == 0:
            potencia_interpolada_menor = potencia_menor_menor
            potencia_interpolada_maior = potencia_maior_menor
        else:
            potencia_interpolada_menor = potencia_menor_menor + (potencia_menor_maior - potencia_menor_menor) * \
                                         (diametro_polia_motora - diametros_polia[idx_diametro_menor]) / \
                                         (diametros_polia[idx_diametro_maior] - diametros_polia[idx_diametro_menor])

            potencia_interpolada_maior = potencia_maior_menor + (potencia_maior_maior - potencia_maior_menor) * \
                                         (diametro_polia_motora - diametros_polia[idx_diametro_menor]) / \
                                         (diametros_polia[idx_diametro_maior] - diametros_polia[idx_diametro_menor])

        # Interpolação linear nos RPMs
        if rpm_disponiveis[idx_rpm_maior] - rpm_disponiveis[idx_rpm_menor] == 0:
            potencia_final = potencia_interpolada_menor
        else:
            potencia_final = potencia_interpolada_menor + (potencia_interpolada_maior - potencia_interpolada_menor) * \
                             (rpm_motor - rpm_disponiveis[idx_rpm_menor]) / \
                             (rpm_disponiveis[idx_rpm_maior] - rpm_disponiveis[idx_rpm_menor])

        return potencia_final

    except Exception as e:
        print(f"Erro detalhado na interpolação: {e}")  # Depuração
        raise ValueError(f"Erro na interpolação: {e}")