# SAM / PySAM reproducibility

`Tumbabiro Comercial.sam` is a candidate original SAM project and has **not** been audited for self-contained reproducibility or external path dependencies.

`data/final/Tumbabiro_PI_LSTM_V24V1_2050_SAM.csv` is the exact SAM-compatible FINAL 2050 weather file verified against `metadata/SAM_EXPORT_MANIFEST_V24V1.json`.

Before release, a coauthor responsible for SAM/PySAM must:
1. Verify that the `.sam` file is the **actual** final run corresponding to results in the accepted manuscript.
2. Remove machine-specific dependencies and unintended private metadata.
3. Supply or export an executable PySAM `.py`/`.json` configuration containing PV and finance inputs; include software versions and check relevant output fields.
4. Re-run the reference case and compare net AC annual yield and financial metrics with manuscript figures.
5. Record configuration hashes and the exact versions of SAM and PySAM.

**Presence of a `.sam` file does not by itself prove that SAM/PySAM reproduction is complete.**
