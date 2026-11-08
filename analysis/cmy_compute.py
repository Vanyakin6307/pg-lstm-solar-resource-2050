#!/usr/bin/env python3
"""Median-month climatological analog vs final 2050, NSRDB 1998–2024.
No model retraining, no meteorological prediction; descriptive comparison.
Requires pandas, numpy. Run: python cmy_compute.py --input-dir /mnt/data --output-dir ./outputs
"""
import argparse,hashlib,json,pathlib
import numpy as np
import pandas as pd

COLS=['Date','Hour','Minute','GHI','DNI','DHI','Solar Zenith Angle']
W={'GHI':0.50,'DNI':0.25,'DHI':0.25}
RAD=['GHI','DNI','DHI']
DTH=0.5/1000

def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as r:
  for b in iter(lambda:r.read(2**20),b''): h.update(b)
 return h.hexdigest()

def tab(x):return x.to_dict(orient='records')

def metrics(df,label):
 result=[]
 # chronological full dataset, include night and dawn; daytime uses respective zenith from series
 for v in RAD:
  a=df[v].to_numpy(dtype=float)
  daily=df.groupby(df['timestamp'].dt.date,sort=True)[v].sum().to_numpy()*DTH
  # full series ramp includes any month boundary; boundary midnight radiation zero
  ramp=np.abs(np.diff(a))
  # only ramps for which either endpoint is daytime according to same solar source geometry
  light=df['cosz_plus'].to_numpy()>0.05
  day_ramp=ramp[light[1:] & light[:-1]]
  daytime=a[light]
  result.append({'reference':label,'variable':v,'annual_kwh_m2':a.sum()*DTH,
                 'daily_mean_kwh_m2':daily.mean(),'daily_sd_kwh_m2':daily.std(ddof=1),
                 'daily_cv_pct':100*daily.std(ddof=1)/daily.mean(),
                 'daily_p05_kwh_m2':np.quantile(daily,.05),'daily_p50_kwh_m2':np.quantile(daily,.5),
                 'daily_p95_kwh_m2':np.quantile(daily,.95),
                 'ramp_p95_all_W_m2_30min':np.quantile(ramp,.95),
                 'ramp_p95_day_W_m2_30min':np.quantile(day_ramp,.95),
                 'daytime_p95_W_m2':np.quantile(daytime,.95),
                 'daytime_sd_W_m2':daytime.std(ddof=1),
                 'lag1_autocorr_full':pd.Series(a).autocorr(1),
                 'lag48_autocorr_full':pd.Series(a).autocorr(48),
                 'n_days':len(daily),'n_records':len(df),
                 'n_daytime_ramps':len(day_ramp)})
 return pd.DataFrame(result)

def main(ind,outd):
 outd=pathlib.Path(outd);outd.mkdir(exist_ok=True,parents=True)
 hi=pathlib.Path(ind)/'consol_tumbabiro_2026_total(4).csv'
 fi=pathlib.Path(ind)/'PI_LSTM_V24V1_2050_FINAL_RESOURCE(1).csv'
 h=pd.read_csv(hi,usecols=COLS)
 h['date']=pd.to_datetime(h['Date'],dayfirst=True,errors='raise')
 h['year']=h.date.dt.year.astype(int); h['month']=h.date.dt.month.astype(int);h['day']=h.date.dt.day.astype(int)
 assert sorted(h.year.unique().tolist())==list(range(1998,2025))
 assert len(h)==473376 and not h.duplicated(['year','month','day','Hour','Minute']).any()
 assert h[COLS[3:]].notna().all().all()
 h=h[~((h.month==2)&(h.day==29))].copy()
 assert len(h)==27*17520
 h['slot']=(2*h['Hour']+(h['Minute']//30)).astype(int)
 assert len(h.groupby(['year','month','day','slot']))==len(h)
 # year-specific monthly energy, each month has 27 candidates
 hist_monthly=h.groupby(['year','month'],as_index=False)[RAD].sum()
 for v in RAD: hist_monthly[v]=hist_monthly[v]*DTH
 long_meds=hist_monthly.groupby('month')[RAD].median().rename(columns={k:k+'_P50' for k in RAD}).reset_index()
 selected=[]
 for m in range(1,13):
  can=hist_monthly.loc[hist_monthly.month==m].copy()
  target=long_meds.loc[long_meds.month==m].iloc[0]
  sq=sum(W[v]*((can[v]-target[v+'_P50'])/target[v+'_P50'])**2 for v in RAD)
  can['score']=sq;can=can.sort_values(['score','year'])
  picked=can.iloc[0]
  selected.append({'month':m,'source_year':int(picked.year),'weighted_relative_squared_score':float(picked.score),
                   **{f'{v}_month_kwh_m2':float(picked[v]) for v in RAD},
                   **{f'{v}_P50_month_kwh_m2':float(target[f'{v}_P50']) for v in RAD}})
 sm=pd.DataFrame(selected)
 f=pd.read_csv(fi,parse_dates=['timestamp'])
 assert len(f)==17520 and (f['timestamp'].diff().dropna()==pd.Timedelta(minutes=30)).all()
 f['month']=f.timestamp.dt.month.astype(int);f['day']=f.timestamp.dt.day.astype(int)
 f['slot']=(2*f.timestamp.dt.hour+f.timestamp.dt.minute//30).astype(int)
 assert f['month'].nunique()==12 and not f.duplicated(['month','day','slot']).any()
 # source real records for the chosen historical calendar month/day/slot; no mixing within day
 hsub=h.merge(sm[['month','source_year']],left_on=['month','year'],right_on=['month','source_year'],how='inner',validate='many_to_one')
 assert len(hsub)==17520
 hsub=hsub.rename(columns={'GHI':'GHI_cmy','DNI':'DNI_cmy','DHI':'DHI_cmy','Solar Zenith Angle':'zenith_source'})
 c=f[['timestamp','month','day','slot','cosz_plus','Solar Zenith Angle','GHI_final','DNI_final','DHI_final']].merge(hsub[['month','day','slot','year','GHI_cmy','DNI_cmy','DHI_cmy','zenith_source']],on=['month','day','slot'],how='left',validate='1:1').rename(columns={'year':'source_year','Solar Zenith Angle':'zenith_2050'})
 assert not c.isna().any().any() and (c.timestamp==f.timestamp).all()
 # Reconstructed GHI based on historical zenith and DNI/DHI, audit deviation from source.
 c['source_cosz_plus']=np.clip(np.cos(np.deg2rad(c.zenith_source)),0,None)
 c['source_closure_residual_W_m2']=c.GHI_cmy-c.DNI_cmy*c.source_cosz_plus-c.DHI_cmy
 c['2050_zenith_if_transposed_residual_W_m2']=c.GHI_cmy-c.DNI_cmy*c.cosz_plus-c.DHI_cmy
 c['zenith_difference_deg']=c.zenith_source-c.zenith_2050
 # historical source values unchanged, correct physical closure attributed to original NSRDB geometry
 # normalize names; two DataFrames and metrics independently (daytime uses each's source zenith)
 ff=c[['timestamp','cosz_plus']+['%s_final'%v for v in RAD]].rename(columns={v+'_final':v for v in RAD})
 cc=c[['timestamp','source_cosz_plus']+['%s_cmy'%v for v in RAD]].rename(columns={**{v+'_cmy':v for v in RAD},'source_cosz_plus':'cosz_plus'})
 mf=metrics(ff,'FINAL_2050'); mc=metrics(cc,'CMMY_NSRDB_1998_2024')
 allm=pd.concat([mf,mc],ignore_index=True)
 pair=mf.merge(mc,on='variable',suffixes=('_final','_cmy'))
 summary=[]
 for _,r in pair.iterrows():
  v=r.variable
  z={'variable':v}
  for key in ['annual_kwh_m2','daily_sd_kwh_m2','daily_cv_pct','ramp_p95_all_W_m2_30min','ramp_p95_day_W_m2_30min','daytime_p95_W_m2']:
   f1=r[key+'_final'];v1=r[key+'_cmy'];
   z[key+'_final']=f1;z[key+'_cmy']=v1;z[key+'_delta_pct']=100*(f1/v1-1)
  summary.append(z)
 summary=pd.DataFrame(summary)
 # Monthly comparison with historical P50, all by month and component
 bymonth_f=f.groupby('month')[[v+'_final' for v in RAD]].sum()*DTH
 bymonth_c=c.groupby('month')[[v+'_cmy' for v in RAD]].sum()*DTH
 mons=[]
 for m in range(1,13):
  row={'month':m,'source_year':int(sm.loc[sm.month==m,'source_year'].iloc[0])}
  for v in RAD:
   row[f'{v}_final_kwh_m2']=float(bymonth_f.loc[m,v+'_final'])
   row[f'{v}_cmy_kwh_m2']=float(bymonth_c.loc[m,v+'_cmy'])
   row[f'{v}_historical_median_kwh_m2']=float(long_meds.loc[long_meds.month==m,v+'_P50'].iloc[0])
   row[f'{v}_final_vs_cmy_pct']=100*(row[f'{v}_final_kwh_m2']/row[f'{v}_cmy_kwh_m2']-1)
   row[f'{v}_final_vs_median_pct']=100*(row[f'{v}_final_kwh_m2']/row[f'{v}_historical_median_kwh_m2']-1)
  mons.append(row)
 mons=pd.DataFrame(mons)
 for v in RAD:
  c[f'{v}_energy_delta_W_m2']=c[f'{v}_final']-c[f'{v}_cmy']
 daily_f=c.groupby(c.timestamp.dt.date)[[v+'_final' for v in RAD]].sum()*DTH
 daily_c=c.groupby(c.timestamp.dt.date)[[v+'_cmy' for v in RAD]].sum()*DTH
 days=pd.DataFrame({'date':daily_f.index})
 for v in RAD:
  days[f'{v}_final_kwh_m2']=daily_f[f'{v}_final'].to_numpy();days[f'{v}_cmy_kwh_m2']=daily_c[f'{v}_cmy'].to_numpy()
 # input raw data provenance
 hist_ann=h.groupby('year')[RAD].sum()*DTH
 annual_historical=[]
 for v in RAD:
  annual_historical.append({'variable':v,'annual_P05':float(hist_ann[v].quantile(.05)),'annual_P50':float(hist_ann[v].median()),'annual_P95':float(hist_ann[v].quantile(.95)), 'annual_min':float(hist_ann[v].min()),'annual_max':float(hist_ann[v].max())})
 annual_historical=pd.DataFrame(annual_historical)
 # diff-ratio
 final_diff=float(ff.DHI.sum()/ff.GHI.sum());ref_diff=float(cc.DHI.sum()/cc.GHI.sum())
 quality={'hist_records_all':473376,'hist_records_leap_removed':473040,'history_years':27,'baseline_year_records':len(c),'final_year_records':len(f),'half_hour_spacing_verified':True,'timestamp_alignment_complete':True,
          'original_historical_values_retained':True,'month_median_weights':W,'reference_not_official_TMY':True,
          'final_night_nonzero_rows':int(((c.cosz_plus==0)&(c[['GHI_final','DNI_final','DHI_final']].max(axis=1)>1e-8)).sum()),
          'reference_night_nonzero_rows_original_geometry':int(((c.source_cosz_plus==0)&(c[['GHI_cmy','DNI_cmy','DHI_cmy']].max(axis=1)>1e-8)).sum()),
          'cmy_closure_mae_original_geometry_Wm2':float(np.abs(c.source_closure_residual_W_m2).mean()),
          'cmy_closure_max_original_geometry_Wm2':float(np.abs(c.source_closure_residual_W_m2).max()),
          'cmy_closure_mae_if_imposed_2050_geometry_Wm2':float(np.abs(c['2050_zenith_if_transposed_residual_W_m2']).mean()),
          'zenith_abs_diff_median_deg':float(np.abs(c.zenith_difference_deg).median()),
          'zenith_abs_diff_p95_deg':float(np.abs(c.zenith_difference_deg).quantile(.95)),
          'final_annual_diffuse_energy_ratio':final_diff,'cmy_annual_diffuse_energy_ratio':ref_diff,
          'historical_source_sha256':sha(hi),'final_source_sha256':sha(fi),
          'historical_source_filename':hi.name,'final_source_filename':fi.name,
          'median_year_is_not_independent_validation':True,
          'time_comparison_not_pointwise_forecast':True}
 # Save aligned CSV include geometry and source provenance; large but zip efficient
 c.to_csv(outd/'R1_Editor_2050_FINAL_vs_CMMY_Aligned_V01.csv',index=False,float_format='%.9g')
 sm.to_csv(outd/'R1_Editor_CMMY_Selected_Months_V01.csv',index=False,float_format='%.10g')
 mons.to_csv(outd/'R1_Editor_FINAL_vs_CMMY_Monthly_V01.csv',index=False,float_format='%.10g')
 allm.to_csv(outd/'R1_Editor_FINAL_vs_CMMY_StatisticalMetrics_V01.csv',index=False,float_format='%.10g')
 summary.to_csv(outd/'R1_Editor_FINAL_vs_CMMY_ComparativeSummary_V01.csv',index=False,float_format='%.10g')
 days.to_csv(outd/'R1_Editor_FINAL_vs_CMMY_DailyEnergy_V01.csv',index=False,float_format='%.10g')
 annual_historical.to_csv(outd/'R1_Editor_AnnualNSRDB_HistoricalQuantiles_V01.csv',index=False,float_format='%.10g')
 (outd/'R1_Editor_FINAL_vs_CMMY_QualityAndTraceability_V01.json').write_text(json.dumps(quality,indent=2,ensure_ascii=False),encoding='utf-8')
 print('Summary:\n',summary.to_string(index=False,float_format=lambda x:f'{x:.4f}'))
 print('\nmonths:\n',mons[['month','source_year','GHI_final_vs_cmy_pct','DNI_final_vs_cmy_pct','DHI_final_vs_cmy_pct']].to_string(index=False,float_format=lambda x:f'{x:.3f}'))
 print('\nquality',json.dumps(quality,indent=2))
 return summary,mons,allm,quality

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input-dir',default='/mnt/data');p.add_argument('--output-dir',default='/mnt/data/EDITOR_TMY_CMY_2050_V01');a=p.parse_args();main(a.input_dir,a.output_dir)
