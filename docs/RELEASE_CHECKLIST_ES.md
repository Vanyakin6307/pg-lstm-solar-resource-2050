# Lista de verificación antes de publicar GitHub / Zenodo

**ESTADO: BORRADOR DE PREPUBLICACIÓN — NO PUBLICAR SIN APROBACIÓN.**

- [ ] Confirmar cuál de las copias de los notebooks 01 y 03 es la versión canónica aprobada; conservar hash.
- [ ] Revisar el notebook 02: su cabecera contiene una mención heredada de «V2.3»; verificar que no haya contradicciones metodológicas.
- [ ] Verificar que los notebooks se ejecuten en un entorno limpio, documentando dependencias y sus versiones exactas.
- [ ] Comprobar que el código no contenga claves API, tokens, información personal o rutas privadas.
- [ ] Verificar el recurso FINAL 2050 y el CSV SAM usando `python scripts/verify_release.py`.
- [ ] Confirmar ambos escaladores y la carga del modelo `.keras` en la versión del entorno elegida.
- [ ] Documentar origen, descarga, referencia y licencia del NSRDB histórico; decidir su depósito independiente.
- [ ] Validar que `Tumbabiro Comercial.sam` reproduce efectivamente la configuración publicada.
- [ ] Adjuntar exportación de código/configuración PySAM verificable; SAM no está cerrado con este borrador.
- [ ] Incluir instrucciones para obtener las variables de entrada y sus unidades; ejecutar el pipeline de extremo a extremo.
- [ ] Mantener explícito que la denominación científica del manuscrito es PG-LSTM y que el archivo entrenado conserva PI-LSTM.
- [ ] No afirmar que existen recursos FINAL retrospectivos aceptados de 2023/2024.
- [ ] Conservar benchmarks, sensibilidad meteorológica y CMMY sin atribuciones causales improcedentes.
- [ ] Confirmar autores, orden, ORCID, licencia del código y licencia de los datos, con coautores.
- [ ] Convertir `CITATION.cff.DRAFT` a `CITATION.cff` tras aprobación.
- [ ] Definir `LICENSE` tras autorización de titulares; no asumir que la licencia del código cubre NSRDB.
- [ ] Crear tag/release verificable (p. ej. `v1.0.0-paper`) cuando el contenido esté congelado.
- [ ] Activar sincronización GitHub–Zenodo y verificar descarga íntegra del registro archivado.
- [ ] Actualizar Data Availability Statement y citar el **DOI de versión**; agregar DOI separado para datos si procede.
