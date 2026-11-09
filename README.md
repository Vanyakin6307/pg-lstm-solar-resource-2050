# Physics-Guided LSTM for Synthetic Solar Irradiance Generation in Tumbabiro, Ecuador

## Overview

This repository contains research artifacts supporting a study on physics-guided Long Short-Term Memory (PG-LSTM) modeling and synthetic solar irradiance generation for Tumbabiro, Imbabura, Ecuador.

The study uses historical solar and meteorological data from the National Solar Radiation Database (NSRDB), spanning 1998–2024, to develop a multicomponent irradiance model and construct a synthetic solar resource for 2050.

The modeled irradiance components are:

- Global Horizontal Irradiance (GHI)
- Direct Normal Irradiance (DNI)
- Diffuse Horizontal Irradiance (DHI)

The repository also includes resources supporting photovoltaic and techno-economic simulations using NREL System Advisor Model (SAM) and PySAM.

## Repository Structure

| Directory | Description |
|---|---|
| `analysis/` | Supporting analyses |
| `data/` | Historical-data documentation, intermediate resources and final solar resource |
| `docs/` | Supporting documentation |
| `metadata/` | Research metadata |
| `models/` | Trained model and preprocessing scalers |
| `notebooks/` | Physical baseline construction, training, generation, validation and climatological reference |
| `sam/` | SAM project, PySAM configurations, weather files and simulation results |
| `scripts/` | Supporting scripts |

## Model and Data

The PG-LSTM architecture uses an encoder–decoder LSTM framework with physically guided irradiance reconstruction.

The historical data are partitioned into training (1998–2019), validation (2020–2022), and testing (2023–2024) periods.

The synthetic 2050 solar resource contains 17,520 half-hourly records.

Some existing filenames retain the original `PI_LSTM` designation. These names are preserved for artifact traceability and refer to the model described scientifically as PG-LSTM.

## SAM and PySAM Reproducibility

The `sam/` directory includes:

- `project/`: updated SAM project with the AIR ECU scenario;
- `pysam/`: Python comparison script and exported configuration files;
- `weather/`: RAW, POST and FINAL meteorological resources;
- `results/`: comparison results and input-compatibility logs.

The FINAL 2050 scenario was independently evaluated using PySAM in Google Colab. Its principal energy and economic indicators were consistent with the corresponding SAM simulation.

Certain exported configuration inputs were not recognized by the tested PySAM version and were logged. Complete parameter-level equivalence across software versions has not been established.

## Reproducibility Notes

The repository provides computational artifacts for inspecting and reproducing the reported workflow. Successful execution requires compatible Python packages, correct input paths and the dependencies of the respective notebooks and scripts.

The presence of a computational artifact does not by itself establish independent end-to-end verification of every research stage.

## Data Provenance

Historical solar and meteorological inputs originate from the National Solar Radiation Database (NSRDB). Users should consult the original data provider for applicable access conditions and attribution requirements.

## Citation

A permanent Zenodo DOI will be added after the first archived GitHub release.

## Publication Status

Research repository prepared to support the revised manuscript submitted to *Sustainability* (MDPI).
