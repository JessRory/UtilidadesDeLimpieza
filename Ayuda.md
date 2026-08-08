# 📚 Documentación de Librería: `CleanUtils`

**Versión:** 0.0.1

**Dependencias:** `pandas`, `tkinter`, `rapidfuzz`

## 🛠️ Guía Rápida de Métodos

### 1. Limpieza y Formato de Texto

| Método | Entrada | Salida | Descripción |
| --- | --- | --- | --- |
| `clean_string` | `df` | `df` | Normaliza nombres de columnas: minúsculas, sin espacios y con guiones bajos (`_`). |
| `eliminar_caracteres_extraños` | `df`, `cols` (opt) | `df` | Elimina símbolos especiales de las celdas, dejando solo letras, números y guiones. |
| `transforma_fechas` | `df`, `cols` | `df` | Convierte columnas a formato fecha `DD-MM-YYYY`. Lanza error si la columna no existe. |

### 2. Gestión de Duplicados (Nombres y Contenido)

| Método | Entrada | Salida | Descripción |
| --- | --- | --- | --- |
| `obtener_nombres_duplicados` | `df` | `list[str]` | Lista los nombres de columnas que se repiten exactamente. |
| `obtener_columnas_duplicadas` | `df` | `list[str]` | Detecta columnas idénticas por su **contenido** (usa hashing), incluso con NaNs. |
| `eliminar_columnas_duplicadas` | `df` | `df` | Borra automáticamente columnas repetidas por nombre **O** por contenido. |
| `eliminar_duplicados` | `df` | `df` | Borra **filas** idénticas y resetea el índice. |

### 3. Integridad y Fuzzy Matching (RapidFuzz)

| Método | Entrada | Salida | Descripción |
| --- | --- | --- | --- |
| `rellena_nans` | `df` | `df` | Sustituye todos los valores nulos (`NaN`) por `0`. |
| `reemplaza_inconsistencias` | `df`, `col`, `target`, `ratio` | `df` | Busca valores similares a `target` en una columna y los unifica (ej: "Plegados" -> "Plegados SL"). |

### 4. Formatos Específicos e Integridad

| Método | Entrada | Salida | Descripción |
| --- | --- | --- | --- |
| `reemplaza_inconsistencias` | `df`, `col`, `target`, `ratio` | `df` | Unifica valores similares a un `target` usando lógica difusa para corregir errores tipográficos. |
| `convertir_fecha_espanol` | `series` | `series` | Traduce fechas en texto (ej: "1 de enero") a formato `datetime` reconociendo el idioma español. |
| `calcular_nulos` | `df` | `float` | Calcula el porcentaje total de valores faltantes en el DataFrame (redondeado a 2 decimales). |
| `cambiar_tipo_columna` | `df`, `columnas`, `tipo_nuevo` | `df` | Cambia los tipos de las columnas especificadas; si es `object`, limpia puntos y comas españoles antes de la conversión. |

## 🚀 Ejemplos de Implementación Pro

### Limpieza inicial de un DataFrame recién leído

```python
from CleanUtils import CleanUtils as cu

# 1. Normalizar nombres de columnas y quitar duplicados de contenido
df = cu.clean_string(df)
df = cu.eliminar_columnas_duplicadas(df)

# 2. Corregir fechas de columnas específicas
df = cu.transforma_fechas(df, ['fecha_pedido', 'fecha_entrega'])

```

### Unificación de nombres con lógica difusa (Fuzzy)

Si tienes proveedores como "Casamayor", "Casamayor S.L." y "Cayamayor":

```python
# Unifica todo lo que se parezca un 80% a "Casamayor S.L."
df = cu.reemplaza_inconsistencias(df, 'proveedor', 'Casamayor S.L.', min_ratio=80)

```

---

## 📌 Notas Técnicas para el Programador

* **Uso de Hashing:** El método `obtener_columnas_duplicadas` es extremadamente eficiente porque convierte las columnas en tuplas "hasheables" para comparar contenido masivo rápidamente.
* **Seguridad:** Casi todos los métodos incluyen un `.copy()` o devuelven un nuevo DataFrame, evitando modificar el original por accidente si no se reasigna la variable.
* **Expresiones Regulares:** `eliminar_caracteres_extraños` usa la regex `r'[^\w]'`, que protege caracteres alfanuméricos pero elimina puntos, comas, comillas y símbolos extraños de Excel.

**Siguiente paso recomendado:** Dado que usas `@staticmethod` en todo, recuerda que no necesitas instanciar la clase (no hace falta `cu = CleanUtils()`), puedes llamar directamente a `CleanUtils.clean_string(df)`. ¿Te gustaría que creáramos un pequeño script de prueba que ejecute todos estos métodos en orden sobre un archivo de ejemplo?