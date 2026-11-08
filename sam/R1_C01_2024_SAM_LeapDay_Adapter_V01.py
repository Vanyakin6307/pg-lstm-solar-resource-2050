#!/usr/bin/env python3
"""Adapter auditable 2024 (366 d) -> SAM (365 d). Usa SOLO CSV ya construidos en formato SAM.
Uso: python R1_C01_2024_SAM_LeapDay_Adapter_V01.py archivo_2024_SAM_17568.csv
No transforma irradiancias ni meteo; descarta solamente 2024-02-29; conserva fechas originales.
"""
import csv, json, hashlib, sys
from pathlib import Path
from datetime import datetime, timedelta

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''):h.update(chunk)
    return h.hexdigest()

def main(inp):
    inp=Path(inp).resolve()
    with inp.open(newline='',encoding='utf-8-sig') as f:
        rows=list(csv.reader(f))
    if len(rows)<4:raise ValueError('CSV SAM requiere encabezado de metadatos y datos')
    # CSV SAM: dos renglones de metadatos y un renglón de nombres de campos.
    meta=rows[:2]
    headers=rows[2]
    unitrow=[]
    metakeys=[s.strip().lower() for s in rows[0]]
    if 'hasunits' in metakeys and rows[1][metakeys.index('hasunits')].strip().lower()=='yes':
        unitrow=[rows[3]]; data=rows[4:]
    else:data=rows[3:]
    normalized={x.strip().lower():i for i,x in enumerate(headers)}
    def find(*names):
        for n in names:
            if n in normalized:return normalized[n]
        raise ValueError('Falta campo SAM: '+str(names))
    iy=find('year','yr');im=find('month','mo');id=find('day');ih=find('hour','hr');imin=find('minute','min')
    ie={v:find(v) for v in ('ghi','dni','dhi')}
    if len(data)!=17568:raise ValueError(f'Se esperan 17568 registros, hay {len(data)}')
    expected=datetime(2024,1,1)
    removed=[]; kept=[]
    for i,r in enumerate(data):
        dt=datetime(*[int(float(r[j])) for j in (iy,im,id,ih,imin)])
        if dt!=expected:raise ValueError(f'Fecha fuera de secuencia en la fila {i}: {dt}, esperada {expected}')
        expected+=timedelta(minutes=30)
        (removed if dt.month==2 and dt.day==29 else kept).append(r)
    if expected!=datetime(2025,1,1) or len(removed)!=48 or len(kept)!=17520:
        raise ValueError('Falló la verificación bisiesta')
    out=inp.with_name(inp.stem+'_SAM365.csv')
    if out.exists():raise FileExistsError('No se sobrescribe '+str(out))
    with out.open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f,lineterminator='\n');w.writerows(meta+[headers]+unitrow+kept)
    def en(rr,col):return sum(float(x[ie[col]]) for x in rr)*.0005
    report={'source_filename':inp.name,'source_sha256':sha(inp),'output_filename':out.name,'output_sha256':sha(out),
            'method':'Exclude exactly all 48 half-hour records of 2024-02-29; keep year/month/day/hour/minute and all other values unchanged',
            'source_n':len(data),'output_n':len(kept),'removed_n':len(removed),'time_step_hours':0.5,
            'note':'The adapted output is a 365-day SAM input, not a full-year 2024 meteorological series.',
            'energy_kWh_m2':{c:{'full_2024':en(data,c),'excluded_feb29':en(removed,c),'SAM365':en(kept,c)} for c in ie}}
    jp=out.with_suffix('.manifest.json');jp.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    print('Adaptación completada:',out,'\nManifest:',jp)
    print(json.dumps(report['energy_kWh_m2'],indent=2))
if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('Uso: python script.py archivo_2024_SAM_17568.csv')
    main(sys.argv[1])
