# Cómo publicar después de revisar este paquete

## Primera carga (GitHub web)
1. Descomprime este ZIP localmente y abre la carpeta `pg-lstm-solar-resource-2050_PREPUBLICACION_V01`.
2. Comprueba su contenido y corrige los pendientes del checklist antes de hacer público el depósito.
3. En el repositorio GitHub creado, elige `Add file` → `Upload files`, y arrastra carpetas/archivos según permita tu navegador; comprueba que las rutas queden iguales a las de este paquete.
4. Confirma las rutas y realiza el primer commit. Para múltiples carpetas, GitHub Desktop o Git puede ser más fiable que la carga por navegador.
5. **No subas el ZIP como un único archivo** esperando que GitHub cree automáticamente su estructura: primero debes descomprimirlo.

## Recomendación de publicación
- GitHub: código, notebooks, documentación, modelo (~0.5 MB), escaladores, CSV FINAL (~3.8 MB), CSV SAM (~1.5 MB); los archivos actuales individuales están por debajo del límite web de 25 MiB.
- Histórico completo (~63 MB): no incluirlo por ahora; documenta fuente exacta y decide su depósito independiente en Zenodo tras revisar permisos y condiciones.
- GitHub Release: crear solo cuando coautores confirmen que código y datos corresponden al manuscrito aceptado.
- Zenodo: vincular GitHub y archivar el release para obtener DOI de versión. Si datos grandes están en un registro Zenodo independiente, citar **ambos** DOI y referenciarlos mutuamente.

## GitHub y Zenodo
GitHub solo archiva en Zenodo una **release**, no cada commit. Si se usa Git LFS para archivos grandes, verificar la inclusión de los objetos reales en el archivo ZIP de la release; por defecto pueden aparecer solo archivos puntero.

## Precaución
Este paquete **no** es evidencia de que se haya realizado una nueva ejecución completa, ni de que se haya depositado públicamente ningún recurso. Son copias de los artefactos disponibles y documentación de trazabilidad, preparadas para auditoría de los coautores.
