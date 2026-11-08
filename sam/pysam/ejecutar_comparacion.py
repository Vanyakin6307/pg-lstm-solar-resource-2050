"""Comparación RAW → POST → FINAL con el proyecto SAM original.
Instalación: pip install NREL-PySAM pandas numpy
Ejecución: python ejecutar_comparacion.py
"""
from pathlib import Path
import json,copy
import numpy as np
import pandas as pd
import PySAM.Pvsamv1 as Pvsamv1
import PySAM.Grid as Grid
import PySAM.Utilityrate5 as Utilityrate5
import PySAM.Singleowner as Singleowner

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'resultados'; OUT.mkdir(exist_ok=True)
PREFIX='Tumbabiro_Single_1_Axis_AIR_ECU'
STAGES=['RAW','POST','FINAL']
PARAMS={s:json.loads((ROOT/f'{PREFIX}_{s}.json').read_text(encoding='utf-8')) for s in ['pvsamv1','grid','utilityrate5','singleowner']}

def set_inputs(model,values):
    skipped=[]
    for k,v in values.items():
        try:model.value(k,v)
        except (AttributeError,ValueError,TypeError) as exc:skipped.append((k,str(exc)[:120]))
    return skipped

def simulate(path):
    pv=Pvsamv1.new();grid=Grid.from_existing(pv);rate=Utilityrate5.from_existing(pv);owner=Singleowner.from_existing(pv)
    skipped={}
    for name,obj in [('pvsamv1',pv),('grid',grid),('utilityrate5',rate),('singleowner',owner)]:
        vals=copy.deepcopy(PARAMS[name])
        if name=='pvsamv1':vals['solar_resource_file']=str(path.resolve())
        skipped[name]=set_inputs(obj,vals)
    pv.execute();grid.execute();rate.execute();owner.execute()
    outputs={}
    for k in ['annual_energy','annual_ac_gross','capacity_factor','performance_ratio','lcoe_real','lcoe_nom','project_return_aftertax_npv']:
        for obj in (pv,grid,owner):
            try:
                v=obj.value(k)
                if isinstance(v,(int,float,np.number)):
                    outputs[k]=float(v);break
            except (AttributeError,ValueError,TypeError):pass
    if 'annual_energy' not in outputs:raise RuntimeError('annual_energy no disponible')
    return outputs,skipped

def weather_metrics(stage):
    df=pd.read_csv(ROOT/f'Tumbabiro_2050_{stage}_SAM.csv',skiprows=2)
    assert len(df)==17520
    time=pd.to_datetime(df[['Year','Month','Day','Hour','Minute']].rename(columns={'Year':'year','Month':'month','Day':'day','Hour':'hour','Minute':'minute'}))
    assert time.is_unique and time.is_monotonic_increasing
    results={}
    for c in ('GHI','DNI','DHI'):
        v=df[c].to_numpy(dtype=float)
        assert np.isfinite(v).all() and (v>=-1e-6).all(),f'{stage}: irradiancia no válida {c}'
        daily=pd.Series(v*0.5,index=time).resample('D').sum()
        ramps=np.abs(np.diff(v))
        results.update({f'{c}_kWh_m2':v.sum()/2000,f'{c}_std_diaria_kWh_m2':daily.std(),f'{c}_P95_rampa_30min_W_m2':np.percentile(ramps,95)})
    return df,results

rows=[];irr={};weather={}
for stage in STAGES:
    path=ROOT/f'Tumbabiro_2050_{stage}_SAM.csv'
    df,metrics=weather_metrics(stage);weather[stage]=df;irr[stage]=metrics
    print('Simulando',stage,flush=True)
    outputs,skipped=simulate(path)
    print('  annual_energy:',outputs['annual_energy']/1000,'MWh/año',flush=True)
    rows.append({'escenario':stage,'energia_neta_MWh_anio':outputs['annual_energy']/1000,**outputs,**metrics})
    (OUT/f'entradas_omitidas_{stage}.json').write_text(json.dumps(skipped,indent=2,ensure_ascii=False),encoding='utf-8')
res=pd.DataFrame(rows).set_index('escenario')
final=res.loc['FINAL','energia_neta_MWh_anio']
res['diferencia_vs_FINAL_pct']=100*(res['energia_neta_MWh_anio']/final-1)
res['diferencia_vs_RAW_pct']=100*(res['energia_neta_MWh_anio']/res.loc['RAW','energia_neta_MWh_anio']-1)
res.to_csv(OUT/'comparacion_energia_y_meteorologia.csv')

# Comparación punto a punto de la componente DHI y otras irradiancias
cor=[]
for c in ('GHI','DNI','DHI'):
    for stage in ('POST','FINAL'):
        a=weather['RAW'][c].to_numpy();b=weather[stage][c].to_numpy()
        cor.append({'componente':c,'comparacion':f'RAW-{stage}','correlacion':float(np.corrcoef(a,b)[0,1]),'MAE_W_m2':float(np.mean(np.abs(a-b)))})
pd.DataFrame(cor).to_csv(OUT/'comparacion_perfiles_temporales.csv',index=False)
print('\nRESULTADOS ENERGÉTICOS')
print(res[['energia_neta_MWh_anio','diferencia_vs_FINAL_pct','diferencia_vs_RAW_pct']].to_string())
print('\nEFECTOS DE ETAPAS')
e=res['energia_neta_MWh_anio']
print('RAW→POST:',100*(e['POST']/e['RAW']-1),'%')
print('POST→FINAL:',100*(e['FINAL']/e['POST']-1),'%')
print('RAW→FINAL:',100*(e['FINAL']/e['RAW']-1),'%')
print('Validación FINAL vs manuscrito 2298.12 MWh:',100*(e['FINAL']/2298.12-1),'%')
if abs(e['FINAL']/2298.12-1)>0.005:
    print('ADVERTENCIA: FINAL no reproduce la referencia dentro de ±0.5 %. Revisar entradas omitidas y CSV.')
print('Resultados guardados en',OUT)
