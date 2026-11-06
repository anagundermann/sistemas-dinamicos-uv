library(readr)
library(dplyr)

# ==========================================
# ETAPA 1: LECTURA Y DIAGNOSTICO INICIAL
# ==========================================

# Seleccionar el archivo original
datos_originales <- read_csv(
  file.choose(),
  col_types = cols(
    `Codigo region` = col_character(),
    `Codigo comuna` = col_character(),
    .default = col_guess()
  ),
  show_col_types = FALSE
)

# 1. Dimensiones
cat("\nDIMENSIONES:\n")
print(dim(datos_originales))

# 2. Nombres de las variables
cat("\nCOLUMNAS:\n")
print(names(datos_originales))

# 3. Tipos de datos
cat("\nESTRUCTURA:\n")
glimpse(datos_originales)

# 4. Primeras observaciones
cat("\nPRIMERAS FILAS:\n")
print(head(datos_originales))

# 5. Registros completamente duplicados
cat("\nFILAS DUPLICADAS:\n")
print(sum(duplicated(datos_originales)))

# 6. Valores faltantes por variable
cat("\nVALORES FALTANTES:\n")
print(colSums(is.na(datos_originales)))


# ==========================================
# ETAPA 2: REGISTROS DUPLICADOS
# ==========================================

# Identificar las fechas con filas duplicadas
duplicados <- datos_originales[
  duplicated(datos_originales),
]

cat("\nDUPLICADOS POR FECHA:\n")

duplicados %>%
  count(Fecha, name = "filas_duplicadas") %>%
  print()

# Comparar cantidad de registros por fecha
cat("\nFECHAS CON MAS REGISTROS:\n")

datos_originales %>%
  count(Fecha, name = "filas") %>%
  arrange(desc(filas)) %>%
  head(5) %>%
  print()


# ==========================================
# ETAPA 2: ELIMINAR DUPLICADOS EXACTOS
# ==========================================

# Crear una tabla nueva sin registros repetidos
datos_limpios <- datos_originales %>%
  distinct()

# Verificar el resultado
cat("\nDIMENSIONES DESPUES DE LIMPIAR:\n")
print(dim(datos_limpios))

cat("\nDUPLICADOS RESTANTES:\n")
print(sum(duplicated(datos_limpios)))

cat("\nREGISTROS POR FECHA:\n")
datos_limpios %>%
  count(Fecha, name = "filas") %>%
  arrange(desc(filas)) %>%
  head(5) %>%
  print()


# ==========================================
# ETAPA 3: DIAGNOSTICO DE VALORES FALTANTES
# ==========================================

# 1. Cantidad de NA por columna
cat("\nVALORES FALTANTES DESPUES DE ELIMINAR DUPLICADOS:\n")

print(colSums(is.na(datos_limpios)))


# 2. Identificar las comunas sin poblacion o codigo
cat("\nCOMUNAS CON POBLACION O CODIGO FALTANTE:\n")

datos_limpios %>%
  filter(is.na(Poblacion) | is.na(`Codigo comuna`)) %>%
  count(Comuna, name = "registros") %>%
  arrange(desc(registros)) %>%
  print(n = Inf)


# 3. Revisar ejemplos de estos registros
cat("\nEJEMPLOS DE REGISTROS SIN POBLACION:\n")

datos_limpios %>%
  filter(is.na(Poblacion)) %>%
  select(Region, Comuna, Poblacion, Fecha, `Casos confirmados`) %>%
  head(12) %>%
  print()


# 4. Investigar los NA de casos confirmados
cat("\nCASOS CONFIRMADOS FALTANTES POR FECHA:\n")

datos_limpios %>%
  filter(is.na(`Casos confirmados`)) %>%
  count(Fecha, name = "faltantes") %>%
  arrange(desc(faltantes)) %>%
  print(n = 15)


# 5. Identificar las comunas con mas NA de casos
cat("\nCOMUNAS CON MAS CASOS CONFIRMADOS FALTANTES:\n")

datos_limpios %>%
  filter(is.na(`Casos confirmados`)) %>%
  count(Comuna, name = "faltantes") %>%
  arrange(desc(faltantes)) %>%
  print(n = 15)


# ==========================================
# ETAPA 4: IDENTIFICAR EL ORIGEN DE LOS NA
# ==========================================

# 1. Crear un indicador de comuna desconocida
datos_diagnostico <- datos_limpios %>%
  mutate(
    comuna_desconocida = startsWith(
      Comuna,
      "Desconocido"
    )
  )

# 2. Separar los NA de casos confirmados
cat("\nNA DE CASOS SEGUN TIPO DE COMUNA:\n")

datos_diagnostico %>%
  filter(is.na(`Casos confirmados`)) %>%
  count(comuna_desconocida, name = "faltantes") %>%
  print()

# 3. Identificar las comunas reales con NA
cat("\nCOMUNAS REALES CON CASOS FALTANTES:\n")

datos_diagnostico %>%
  filter(
    !comuna_desconocida,
    is.na(`Casos confirmados`)
  ) %>%
  select(
    Region,
    Comuna,
    Fecha,
    `Casos confirmados`
  ) %>%
  print(n = Inf)

# 4. Ver cuantos registros desconocidos
# tienen casos informados
cat("\nREGISTROS DESCONOCIDOS:\n")

datos_diagnostico %>%
  filter(comuna_desconocida) %>%
  summarise(
    total = n(),
    con_casos = sum(!is.na(`Casos confirmados`)),
    sin_casos = sum(is.na(`Casos confirmados`))
  ) %>%
  print()

# 5. Ver los casos desconocidos en la ultima fecha
cat("\nCASOS DESCONOCIDOS EN LA ULTIMA FECHA:\n")

datos_diagnostico %>%
  filter(
    comuna_desconocida,
    Fecha == max(Fecha)
  ) %>%
  summarise(
    fecha = first(Fecha),
    casos_acumulados = sum(
      `Casos confirmados`,
      na.rm = TRUE
    )
  ) %>%
  print()


# ==========================================
# ETAPA 5: VERIFICAR POBLACIONES REGIONALES
# ==========================================

# 1. Comprobar si cambia la poblacion
# de alguna comuna entre distintas fechas

cat("\nCOMUNAS CON POBLACION VARIABLE:\n")

poblaciones_variables <- datos_limpios %>%
  filter(
    !is.na(`Codigo comuna`),
    !is.na(Poblacion)
  ) %>%
  group_by(Region, `Codigo comuna`, Comuna) %>%
  summarise(
    valores_distintos = n_distinct(Poblacion),
    .groups = "drop"
  ) %>%
  filter(valores_distintos > 1)

print(poblaciones_variables, n = Inf)


# 2. Crear una tabla con una fila por comuna
# sin modificar los datos originales

poblacion_comunas <- datos_limpios %>%
  filter(
    !is.na(`Codigo comuna`),
    !is.na(Poblacion)
  ) %>%
  distinct(
    Region,
    `Codigo region`,
    Comuna,
    `Codigo comuna`,
    Poblacion
  )

cat("\nTOTAL DE COMUNAS:\n")
print(nrow(poblacion_comunas))


# 3. Calcular la poblacion de cada region

poblacion_regiones <- poblacion_comunas %>%
  group_by(Region) %>%
  summarise(
    comunas = n(),
    poblacion_total = sum(Poblacion),
    .groups = "drop"
  ) %>%
  arrange(desc(poblacion_total))

cat("\nPOBLACIONES POR REGION:\n")
print(poblacion_regiones, n = Inf)


# 4. Verificar total nacional

cat("\nPOBLACION NACIONAL:\n")
print(sum(poblacion_regiones$poblacion_total))


# ==========================================
# ETAPA 6: CONSISTENCIA TEMPORAL DE LOS CASOS
# ==========================================

# 1. Ordenar los registros por comuna y fecha
# y calcular la variacion entre reportes consecutivos

serie_comunal <- datos_limpios %>%
  arrange(Region, Comuna, Fecha) %>%
  group_by(Region, Comuna) %>%
  mutate(
    casos_anteriores = lag(`Casos confirmados`),
    variacion_casos = `Casos confirmados` - casos_anteriores
  ) %>%
  ungroup()


# 2. Contar aumentos, disminuciones y valores iguales

cat("\nRESUMEN DE VARIACIONES:\n")

serie_comunal %>%
  summarise(
    comparaciones_validas = sum(!is.na(variacion_casos)),
    aumentos = sum(variacion_casos > 0, na.rm = TRUE),
    disminuciones = sum(variacion_casos < 0, na.rm = TRUE),
    sin_cambio = sum(variacion_casos == 0, na.rm = TRUE)
  ) %>%
  print()


# 3. Examinar las mayores disminuciones

cat("\nMAYORES DISMINUCIONES:\n")

serie_comunal %>%
  filter(
    !is.na(variacion_casos),
    variacion_casos < 0
  ) %>%
  arrange(variacion_casos) %>%
  select(
    Region,
    Comuna,
    Fecha,
    casos_anteriores,
    `Casos confirmados`,
    variacion_casos
  ) %>%
  head(15) %>%
  print(n = 15)


# 4. Fechas con mas disminuciones

cat("\nFECHAS CON MAS DISMINUCIONES:\n")

serie_comunal %>%
  filter(
    !is.na(variacion_casos),
    variacion_casos < 0
  ) %>%
  count(Fecha, name = "disminuciones") %>%
  arrange(desc(disminuciones)) %>%
  head(15) %>%
  print(n = 15)


# ==========================================
# ETAPA 7: CONSISTENCIA REGIONAL Y NACIONAL
# ==========================================

# 1. Distinguir disminuciones segun tipo de comuna

cat("\nDISMINUCIONES POR TIPO DE COMUNA:\n")

serie_comunal %>%
  filter(variacion_casos < 0) %>%
  mutate(
    tipo = if_else(
      startsWith(Comuna, "Desconocido"),
      "Comuna desconocida",
      "Comuna identificada"
    )
  ) %>%
  count(tipo, name = "disminuciones") %>%
  print()


# 2. Agrupar casos acumulados por region y fecha

serie_regional <- datos_limpios %>%
  group_by(Region, Fecha) %>%
  summarise(
    casos_reportados = sum(
      `Casos confirmados`,
      na.rm = TRUE
    ),
    valores_faltantes = sum(
      is.na(`Casos confirmados`)
    ),
    .groups = "drop"
  ) %>%
  arrange(Region, Fecha) %>%
  group_by(Region) %>%
  mutate(
    variacion_reportes = casos_reportados -
      lag(casos_reportados)
  ) %>%
  ungroup()


# 3. Mostrar disminuciones regionales

cat("\nDISMINUCIONES REGIONALES:\n")

serie_regional %>%
  filter(variacion_reportes < 0) %>%
  select(
    Region,
    Fecha,
    casos_reportados,
    variacion_reportes,
    valores_faltantes
  ) %>%
  print(n = Inf, width = Inf)


# 4. Agrupar los casos a nivel nacional

serie_nacional <- serie_regional %>%
  group_by(Fecha) %>%
  summarise(
    casos_reportados = sum(casos_reportados),
    .groups = "drop"
  ) %>%
  arrange(Fecha) %>%
  mutate(
    variacion_reportes = casos_reportados -
      lag(casos_reportados)
  )


# 5. Comprobar disminuciones nacionales

cat("\nDISMINUCIONES NACIONALES:\n")

print(sum(
  serie_nacional$variacion_reportes < 0,
  na.rm = TRUE
))


# 6. Revisar las ultimas observaciones

cat("\nULTIMOS REPORTES NACIONALES:\n")

serie_nacional %>%
  tail(5) %>%
  print()


# ==========================================
# ETAPA 8: INVESTIGAR LA DISMINUCION REGIONAL
# ==========================================

# 1. Seleccionar la region y fecha
detalle_valparaiso <- serie_comunal %>%
  filter(
    Region == "Valparaíso",
    Fecha == as.Date("2020-07-20")
  ) %>%
  select(
    Comuna,
    casos_anteriores,
    `Casos confirmados`,
    variacion_casos
  ) %>%
  arrange(variacion_casos)

# 2. Mostrar las mayores disminuciones
cat("\nCOMUNAS CON MAYORES DISMINUCIONES:\n")

detalle_valparaiso %>%
  head(15) %>%
  print(n = 15, width = Inf)

# 3. Calcular el balance de las variaciones
cat("\nBALANCE DE VARIACIONES:\n")

detalle_valparaiso %>%
  summarise(
    comunas_que_disminuyen = sum(variacion_casos < 0),
    comunas_que_aumentan = sum(variacion_casos > 0),
    comunas_sin_cambio = sum(variacion_casos == 0),
    balance_total = sum(variacion_casos)
  ) %>%
  print()

# 4. Revisar la serie regional alrededor de la fecha
cat("\nEVOLUCION REGIONAL:\n")

serie_regional %>%
  filter(
    Region == "Valparaíso",
    Fecha >= as.Date("2020-07-13"),
    Fecha <= as.Date("2020-07-24")
  ) %>%
  select(
    Fecha,
    casos_reportados,
    variacion_reportes,
    valores_faltantes
  ) %>%
  print(n = Inf, width = Inf)


# ==========================================
# ETAPA 9: CONSTRUIR TABLA REGIONAL
# ==========================================

# 1. Unir poblaciones y casos acumulados
datos_covid_regionales <- serie_regional %>%
  left_join(
    poblacion_regiones %>%
      select(Region, poblacion_total),
    by = "Region"
  ) %>%
  mutate(
    dias_desde_inicio = as.integer(
      Fecha - min(Fecha)
    )
  ) %>%
  transmute(
    Region,
    Fecha,
    dias_desde_inicio,
    Poblacion = poblacion_total,
    Casos_acumulados = casos_reportados,
    Valores_faltantes = valores_faltantes
  ) %>%
  arrange(Region, Fecha)


# 2. Verificar dimensiones
cat("\nDIMENSIONES DE LA TABLA REGIONAL:\n")
print(dim(datos_covid_regionales))


# 3. Verificar regiones y fechas
cat("\nREGIONES Y FECHAS:\n")

datos_covid_regionales %>%
  summarise(
    regiones = n_distinct(Region),
    fechas = n_distinct(Fecha),
    registros = n()
  ) %>%
  print()


# 4. Verificar valores faltantes
cat("\nVALORES FALTANTES:\n")
print(colSums(is.na(datos_covid_regionales)))


# 5. Verificar registros por region
cat("\nREGISTROS POR REGION:\n")

datos_covid_regionales %>%
  count(Region, name = "registros") %>%
  print(n = Inf)


# 6. Inspeccionar un ejemplo: Valparaiso
cat("\nEJEMPLO: REGION DE VALPARAISO:\n")

datos_covid_regionales %>%
  filter(
    Region == "Valparaíso",
    Fecha >= as.Date("2020-07-13"),
    Fecha <= as.Date("2020-07-24")
  ) %>%
  print(n = Inf, width = Inf)


# ==========================================
# ETAPA 10: EXPORTAR EL CSV REGIONAL
# ==========================================

# 1. Verificar la estructura antes de exportar

stopifnot(
  nrow(datos_covid_regionales) == 1344,
  ncol(datos_covid_regionales) == 6,
  !anyNA(datos_covid_regionales)
)

# 2. Definir la carpeta de salida

directorio_salida <- file.path(
  getwd(),
  "analisis_datos"
)

if (!dir.exists(directorio_salida)) {
  stop(
    "No se encontro la carpeta analisis_datos. ",
    "Revisa el directorio de trabajo con getwd()."
  )
}

# 3. Definir el nombre del archivo nuevo

ruta_salida <- file.path(
  directorio_salida,
  "covid_chile_regional_limpio.csv"
)

# 4. Evitar sobrescribir otro archivo existente

if (file.exists(ruta_salida)) {
  stop("El CSV ya existe. No se ha sobrescrito.")
}

# 5. Exportar los datos

readr::write_csv(
  datos_covid_regionales,
  ruta_salida,
  na = ""
)

# 6. Verificar el archivo guardado

datos_verificados <- readr::read_csv(
  ruta_salida,
  show_col_types = FALSE
)

cat("\nARCHIVO CREADO:\n")
print(ruta_salida)

cat("\nDIMENSIONES DEL CSV EXPORTADO:\n")
print(dim(datos_verificados))

cat("\nPRIMERAS FILAS:\n")
print(head(datos_verificados))
