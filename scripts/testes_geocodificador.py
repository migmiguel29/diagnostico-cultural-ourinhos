"""Testes locais com respostas simuladas; nenhuma chamada de rede."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from geocodificar_tomtom import geocodificar

class Resposta:
    def __init__(self, resultado): self.resultado=resultado
    def raise_for_status(self): pass
    def json(self): return {'results':[self.resultado]}
class Sessao:
    def __init__(self, resultado): self.resultado=resultado
    def get(self, *args, **kwargs):
        assert kwargs['params']['countrySet']=='BR'
        assert kwargs['timeout']==25
        return Resposta(self.resultado)

valido={'type':'Point Address','matchConfidence':{'score':0.91},'address':{'countryCode':'BR','municipality':'Ourinhos'},'position':{'lat':-22.98,'lon':-49.87}}
assert geocodificar('endereço de teste','dummy',Sessao(valido))['latitude']==-22.98
for mudanca in [{'type':'Street'}, {'matchConfidence':{'score':0.61}}, {'address':{'countryCode':'BR','municipality':'Assis'}}, {'position':{'lat':-23.6,'lon':-49.87}}]:
    resultado={**valido, **mudanca}
    assert geocodificar('endereço de teste','dummy',Sessao(resultado))['precisao_geografica']=='pendente de revisão manual'
print('Geocoder: endereço pontual aceito; rua, baixa confiança, outro município e fora da área rejeitados.')
