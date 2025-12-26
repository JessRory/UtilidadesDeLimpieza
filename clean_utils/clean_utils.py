import pandas as pd
import numpy as np
from typing import List, Optional, Union, Any
from tkinter import messagebox as mb
import rapidfuzz as fw
import dateparser #type: ignore


class CleanUtils:
    
    @staticmethod
    def clean_string(dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Limpia la cadena de entrada eliminando el espacio en blanco inicial/final
        y la convierte a minúsculas.

        Args:
            dataframe (pd.DataFrame): el DataFrame a limpiar.

        Returns:
            pd.DataFrame: El DataFrame limpio.
        """
        dataframe.columns = dataframe.columns.str.strip().str.lower().str.replace(' ', '_')
        
        return dataframe
    
    @staticmethod
    def transforma_fechas(dataframe: pd.DataFrame, columns:list[str]) -> pd.DataFrame:
        """
	Transforma columnas especificadas en el DataFrame aplicando la limpieza de cadenas.
    En caso de que la columna no exista, devuelve un mensaje de error.

        Args:
            dataframe (pd.DataFrame): el DataFrame a transformar.
            columnas (list[str]): Lista de nombres de columna que se limpiarán.

            Returns: pd.DataFrame: El DataFrame transformado.
            """
            
        for column in columns:
            if column in dataframe.columns:
                dataframe[column] = pd.to_datetime(dataframe[column],
                                                   format='%d-%m-%Y',
                                                   errors='coerce')
                
            else:
                mb.showerror(f"La columna '{column}' no existe en el DataFrame.")
        
        return dataframe

    @staticmethod
    def rellena_nans(df: pd.DataFrame) -> pd.DataFrame:
        """
    Rellena todos los valores nulos (NaN) en el DataFrame con el valor cero (0).

    Args: dataframe (pd.DataFrame): el DataFrame a transformar.
        df (pd.DataFrame): DataFrame de entrada.

    Returns: pd.DataFrame: El DataFrame transformado.
        pd.DataFrame: Copia del DataFrame con los NaN reemplazados por 0.
    """
        df_limpio = df.copy()
        df_limpio = df_limpio.fillna(0) # type: ignore
        return df_limpio
    
    @staticmethod
    def obtener_columnas_duplicadas(df: pd.DataFrame) -> List[str]:
        """
        Identifica y devuelve los nombres de las columnas que son duplicados 
        por contenido de otra columna anterior, manejando los NaN correctamente.
        
        args:
            df (pd.DataFrame): El DataFrame a analizar.
        
        returns:
            List[str]: Lista de nombres de columnas duplicadas por contenido.
        """
        if df.empty or df.shape[1] < 2:
            return []
            
        duplicates_indices: List[int] = []
        hashes_vistos: set = set() #type: ignore

        for i, col_name in enumerate(df.columns):
            # CLAVE: Rellenamos NaN con un valor centinela único y no numérico
            # para que el hash sea el mismo si ambas columnas tienen NaN en los mismos lugares.
            col_array = df[col_name].fillna('<<NaN_Sentinel>>').to_numpy() # type: ignore
            col_content_hashable = tuple(col_array.ravel())
            col_hash = hash(col_content_hashable)
            
            if col_hash in hashes_vistos:
                duplicates_indices.append(i) # Guardamos el índice de la columna duplicada
            else:
                hashes_vistos.add(col_hash) # type: ignore
                
        # Devolvemos los nombres de las columnas duplicadas por contenido
        return df.columns[duplicates_indices].tolist()
    
    @staticmethod
    def obtener_nombres_duplicados(df: pd.DataFrame) -> List[str]:
        """
        Identifica y devuelve los nombres de las columnas que tienen el 
        mismo encabezado que una columna anterior.
        
        args:
            df (pd.DataFrame): El DataFrame a analizar.
        returns:
            List[str]: Lista de nombres de columnas duplicadas por nombre.
        """
        if df.empty or df.shape[1] < 2:
            return []
        
        # Devuelve una máscara booleana, True para todas las ocurrencias repetidas
        duplicates_mask = df.columns.duplicated(keep='first')
        
        # Selecciona los nombres de columna donde la máscara es True
        return df.columns[duplicates_mask].tolist()
    
    @staticmethod
    def eliminar_columnas_duplicadas(df: pd.DataFrame) -> pd.DataFrame:
        """
        Elimina columnas que son duplicadas por NOMBRE o por CONTENIDO.
        
        Args:
            df (pd.DataFrame): El DataFrame del cual eliminar columnas duplicadas.
            
        Returns:
            pd.DataFrame: El DataFrame sin columnas duplicadas.
        """
        
        # 1. Obtener duplicados por CONTENIDO (List[str])
        content_duplicates = CleanUtils.obtener_columnas_duplicadas(df)
        
        # 2. Obtener duplicados por NOMBRE (List[str])
        name_duplicates = CleanUtils.obtener_nombres_duplicados(df)
        
        # 3. Combinar ambos y obtener un conjunto de nombres únicos a eliminar
        # Usar un set automáticamente elimina nombres repetidos de ambas listas.
        columns_to_drop = set(content_duplicates + name_duplicates)
        
        if not columns_to_drop:
            return df
        else:
            # Drop requiere una lista de nombres.
            return df.drop(list(columns_to_drop), axis=1)

    @staticmethod
    def eliminar_caracteres_extraños(df: pd.DataFrame, columns_to_clean: Optional[List[str]] = None) -> pd.DataFrame:
        
        """
        Limpia caracteres extraños (símbolos, espacios) de los valores en las columnas:
        1. De la lista proporcionada.
        2. Automáticamente de todas las columnas tipo 'object' si no se proporciona lista.
        
        Args:
            df (pd.DataFrame): El DataFrame a limpiar.
            columns_to_clean (Optional[List[str]], opcional): Lista de nombres de columnas a limpiar.
                                                              Si es None o una lista vacía, limpia las 'object'.
        Returns:
            pd.DataFrame: El DataFrame con los valores limpios.
        """
        df_limpio = df.copy()

        # 1. Determinar las columnas a procesar
        if columns_to_clean is None or len(columns_to_clean) == 0:
            # 1A. Si no se pasa lista (o es vacía), buscamos las columnas de tipo 'object'
            string_cols = df_limpio.select_dtypes(include=['object']).columns
            print(f"Limpiando automáticamente {len(string_cols)} columnas tipo 'object'.")
        else:
            # 1B. Usamos la lista proporcionada, filtrando por columnas que realmente existen
            string_cols = [col for col in columns_to_clean if col in df_limpio.columns]
            
        # 2. Aplicar la limpieza (r'[^\w]' elimina todo lo que no sea letra, número o guion bajo)
        for col in string_cols:
            # Aseguramos que la columna es string (para manejar Nulos) y luego aplicamos la regex
            df_limpio[col] = df_limpio[col].astype(str).str.replace(r'[^\w]', '', regex=True)
            
        return df_limpio
   
    
    @staticmethod
    def eliminar_duplicados(df: pd.DataFrame) -> pd.DataFrame:
        """
        Elimina filas duplicadas en el DataFrame.

        Args:
            df (pd.DataFrame): El DataFrame del cual eliminar duplicados.

        Returns:
            pd.DataFrame: El DataFrame sin filas duplicadas.
        """
        return df.drop_duplicates().reset_index(drop=True)
    

    @staticmethod
    def reemplaza_inconsistencias(df:pd.DataFrame, columna:str, coincidencia:str, min_ratio:int = 50) -> pd.DataFrame:
        """
        Reemplaza inconsistencias en una columna de un DataFrame con un valor específico.

        Args:
            df (pd.DataFrame): El DataFrame a procesar.
            columna (str): El nombre de la columna a procesar.
            coincidencia (str): El valor con el que reemplazar las inconsistencias.
            min_ratio (int, opcional): Umbral mínimo de similitud para considerar una coincidencia cercana.

        Returns:
            pd.DataFrame: El DataFrame con las inconsistencias reemplazadas.
        """
        # Buscamos los valores únicos en la columna especificada
        strings = df[columna].unique()
        
        # Obtenemos las coincidencias cercanas usando fuzzywuzzyrapidfuzz
        matches = fw.process.extract(coincidencia, strings, 
                                            limit=10, scorer=fw.fuzz.token_sort_ratio)

        # Nos quedamos solo con las coincidencias que superan el umbral mínimo
        close_matches = [matches[0] for matches in matches if matches[1] >= min_ratio]

        # Identificamos las filas que contienen esas coincidencias cercanas
        rows_with_matches = df[columna].isin(close_matches)  # type: ignore

        # Reemplazamos los valores en esas filas con la coincidencia deseada
        df.loc[rows_with_matches, columna] = coincidencia
        
        # Devolvemos el DataFrame modificado
        return df

    @staticmethod 
    def convertir_fecha_espanol(series: pd.Series) -> pd.Series:
        """
        Convierte una Serie de strings con fechas en cualquier formato e idioma 
        (especialmente español) a objetos datetime de Pandas.
        
        Ejemplo: '1 de enero de 2024' -> 2024-01-01
        """
        # Definimos una función interna para el mapeo con tipado básico
        def parse_row(date_str: Any)-> Union[pd.Timestamp, Any]:
            if pd.isna(date_str) or date_str == "":
                return pd.NaT
            # dateparser intentará adivinar el formato automáticamente
            return dateparser.parse(str(date_str), languages=['es'])

        return series.apply(parse_row) # type: ignore
    
    @staticmethod
    def calcular_nulos(df:pd.DataFrame)->float:
        """
        Calcula el porcentaje de valores nulos en un DataFrame.

        Args:
            df (pd.DataFrame): El DataFrame a analizar.

        Returns:
            float: El porcentaje total de valores nulos en el DataFrame redondeado a 2 cifras.
        """
        # Número total de celdas en el DataFrame
        total_celdas = np.prod(df.shape)
        # Número total de valores nulos en el DataFrame
        total_perdidos = df.isnull().sum().sum()
        # Porcentaje de valores nulos en el DataFrame
        porcentaje_perdidos = (total_perdidos / total_celdas) * 100

        return round(porcentaje_perdidos, 2)
    
    @staticmethod
    def cambiar_tipo_columna(df: pd.DataFrame, columnas: list[str], tipo_nuevo: str) -> pd.DataFrame:
        """
        Cambia el tipo de datos de una lista específica de columnas.
        Si el tipo es numérico, limpia puntos y comas (formato europeo) antes de la conversión.
        
        Args:
            df (pd.DataFrame): El DataFrame a transformar.
            columnas (list): Lista de nombres de columnas a las que aplicar el cambio.
            tipo_nuevo (str): Tipo de dato destino (e.g., 'float64', 'int64', 'datetime64[ns]').
            
        Returns:
            pd.DataFrame: El DataFrame con las columnas seleccionadas transformadas.
        """
        df = df.copy() 

        for columna in columnas:
            if columna not in df.columns:
                print(f"⚠️ Advertencia: La columna '{columna}' no existe en el DataFrame. Saltando...")
                continue
                
            # Si el nuevo tipo es numérico, realizamos limpieza de strings primero
            if tipo_nuevo in ['float', 'float64', 'int', 'int64']:
                # Solo limpiamos si el dato actual es texto (object o string)
                if df[columna].dtype == 'object' or isinstance(df[columna].dtype, pd.StringDtype):
                    df[columna] = (
                        df[columna]
                        .astype(str)
                        .str.replace('.', '', regex=False)  # Quita puntos de miles: 1.000 -> 1000
                        .str.replace(',', '.', regex=False)  # Cambia coma decimal: 10,5 -> 10.5
                    )
                
                # Conversión segura a numérico
                df[columna] = pd.to_numeric(df[columna], errors='coerce') # type: ignore
            
            else:
                # Para otros tipos (como datetime), usamos la conversión estándar de pandas
                try:
                    if tipo_nuevo.startswith('datetime'):
                        df[columna] = pd.to_datetime(df[columna], errors='coerce')
                    else:
                        df[columna] = df[columna].astype(tipo_nuevo) # type: ignore
                except Exception as e:
                    print(f"❌ Error al convertir la columna '{columna}' a {tipo_nuevo}: {e}")

        return df
    
    
    
    