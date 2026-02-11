# 📊 Guía de Pruebas de Carga con JMeter

## 🎯 Objetivo

Realizar pruebas de estrés y rendimiento para identificar:
- Tiempos de respuesta bajo carga
- Throughput máximo
- Cuellos de botella
- Consumo de recursos
- Tasa de errores

## 📋 Requisitos

- Apache JMeter 5.6+ instalado
- API REST corriendo (local o en Railway)
- Plan de pruebas: `jmeter/planetas_load_test.jmx`

## 🛠️ Instalación de JMeter

### Windows
```bash
# Descargar desde https://jmeter.apache.org/download_jmeter.cgi
# Extraer y agregar al PATH
```

### macOS
```bash
brew install jmeter
```

### Linux
```bash
sudo apt update
sudo apt install jmeter
```

## 🚀 Ejecutar Pruebas

### Modo GUI (Para configurar)

```bash
jmeter -t jmeter/planetas_load_test.jmx
```

### Modo No-GUI (Para pruebas reales)

```bash
cd backend

# Prueba local
jmeter -n -t jmeter/planetas_load_test.jmx \
       -l resultados/results.jtl \
       -e -o resultados/report

# Prueba con API desplegada
jmeter -n -t jmeter/planetas_load_test.jmx \
       -JHOST=tu-api.railway.app \
       -JPORT=443 \
       -l resultados/results_prod.jtl \
       -e -o resultados/report_prod
```

## 📊 Configuración del Plan de Pruebas

### Escenario por Defecto

**Thread Group (Usuarios Concurrentes)**
- Número de hilos (usuarios): 50
- Período de subida (Ramp-Up): 10 segundos
- Iteraciones por usuario: 10
- **Total de requests**: ~1,500

**Requests incluidos:**
1. Login (obtener token)
2. Crear Planeta
3. Listar Planetas

### Modificar Configuración

Editar archivo `planetas_load_test.jmx`:

```xml
<!-- Cambiar número de usuarios -->
<stringProp name="ThreadGroup.num_threads">100</stringProp>

<!-- Cambiar ramp-up time -->
<stringProp name="ThreadGroup.ramp_time">20</stringProp>

<!-- Cambiar iteraciones -->
<stringProp name="LoopController.loops">20</stringProp>
```

## 📈 Escenarios de Prueba

### 1. Prueba de Carga Normal (50 usuarios)

```bash
jmeter -n -t jmeter/planetas_load_test.jmx \
       -l results_50users.jtl \
       -e -o report_50users
```

**Objetivo**: Comportamiento bajo carga normal

### 2. Prueba de Estrés (100 usuarios)

```bash
# Editar el .jmx para 100 usuarios
jmeter -n -t jmeter/planetas_stress_test.jmx \
       -l results_100users.jtl \
       -e -o report_100users
```

**Objetivo**: Identificar límites del sistema

### 3. Prueba de Picos (Spike Test)

```bash
# Configurar: 200 usuarios, ramp-up 5 segundos
jmeter -n -t jmeter/planetas_spike_test.jmx \
       -l results_spike.jtl \
       -e -o report_spike
```

**Objetivo**: Comportamiento ante picos súbitos

### 4. Prueba de Resistencia (Soak Test)

```bash
# Configurar: 30 usuarios, 100 iteraciones (prueba larga)
jmeter -n -t jmeter/planetas_soak_test.jmx \
       -l results_soak.jtl \
       -e -o report_soak
```

**Objetivo**: Detectar memory leaks y degradación

## 📊 Métricas a Analizar

### 1. Tiempos de Respuesta

- **Average**: Tiempo promedio
- **Median**: Tiempo medio (50º percentil)
- **90% Line**: 90º percentil
- **95% Line**: 95º percentil
- **99% Line**: 99º percentil
- **Min/Max**: Valores extremos

**Objetivos deseables:**
- Promedio: < 200ms
- 95º percentil: < 500ms
- 99º percentil: < 1000ms

### 2. Throughput

- **Requests/segundo**: Capacidad de procesamiento
- **KB/sec**: Ancho de banda

**Objetivo**: > 100 req/s

### 3. Tasa de Errores

- **% Error**: Porcentaje de requests fallidos
- **Tipo de errores**: 4xx, 5xx

**Objetivo**: < 1% de errores

### 4. Recursos del Sistema

Monitorear durante la prueba:

```bash
# CPU y Memoria
top

# Conexiones de red
netstat -an | grep :8000

# Logs de la aplicación
tail -f logs/app.log
```

## 📋 Resultados Esperados

### Resultados Óptimos

```
============================================
Summary Report
============================================
Total Samples:     1500
Error %:          0.00%
Avg Response:     150ms
90th Percentile:  300ms
95th Percentile:  400ms
Throughput:       125 req/s
============================================
```

### Resultados con Problemas

```
============================================
Summary Report
============================================
Total Samples:     1500
Error %:          5.2%    ⚠️ Alto
Avg Response:     850ms   ⚠️ Lento
90th Percentile:  2000ms  ⚠️ Muy lento
95th Percentile:  3500ms  ⚠️ Crítico
Throughput:       45 req/s ⚠️ Bajo
============================================
```

## 🔍 Analizar Resultados

### Ver Reporte HTML

```bash
# Abrir el reporte generado
open resultados/report/index.html  # macOS
xdg-open resultados/report/index.html  # Linux
start resultados/report/index.html  # Windows
```

### Secciones del Reporte

1. **Dashboard**: Vista general
2. **Statistics**: Métricas detalladas
3. **Response Times**: Gráficos de tiempos
4. **Throughput**: Capacidad del sistema
5. **Errors**: Análisis de errores

### Analizar con Command Line

```bash
# Estadísticas básicas
jmeter -g resultados/results.jtl -o resultados/analisis

# Ver errores
grep "false" resultados/results.jtl | wc -l

# Tiempo promedio
awk -F',' '{sum+=$2; count++} END {print sum/count}' resultados/results.jtl
```

## 🐛 Identificar Cuellos de Botella

### 1. Base de Datos

**Síntomas:**
- Tiempos de respuesta incrementan con carga
- CPU de DB al 100%

**Soluciones:**
- Agregar índices
- Optimizar queries
- Connection pooling
- Caché

### 2. Aplicación

**Síntomas:**
- Alto uso de CPU/memoria
- Garbage collection frecuente

**Soluciones:**
- Profiling de código
- Optimizar algoritmos
- Aumentar workers/threads

### 3. Red

**Síntomas:**
- Timeouts
- Conexiones rechazadas

**Soluciones:**
- Aumentar límite de conexiones
- Load balancer
- CDN para estáticos

## 📊 Monitoreo Durante Pruebas

### Monitorear API

```bash
# CPU y Memoria
htop

# Logs en tiempo real
tail -f logs/uvicorn.log

# Conexiones activas
watch -n 1 'netstat -an | grep :8000 | wc -l'
```

### Métricas del Sistema

```python
# Agregar al backend para métricas
import psutil

@app.get("/metrics")
def get_metrics():
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "connections": len(psutil.net_connections())
    }
```

## 📝 Generar Reporte de Resultados

### Plantilla de Reporte

```markdown
# Reporte de Pruebas de Carga

## Configuración
- Usuarios concurrentes: 50
- Ramp-up: 10s
- Iteraciones: 10
- Total requests: 1,500

## Resultados

### Tiempos de Respuesta
- Promedio: 180ms
- Mediana: 150ms
- 90º percentil: 320ms
- 95º percentil: 450ms
- 99º percentil: 800ms

### Throughput
- Requests/s: 115
- KB/s: 45

### Errores
- Total: 0
- Porcentaje: 0%

## Recursos
- CPU máxima: 65%
- Memoria máxima: 45%
- Conexiones pico: 52

## Conclusiones
✅ El sistema maneja 50 usuarios concurrentes sin problemas
✅ Tiempos de respuesta aceptables
⚠️ A partir de 100 usuarios, el tiempo de respuesta incrementa
❌ Con 200 usuarios, tasa de error > 5%

## Recomendaciones
1. Optimizar queries de base de datos
2. Implementar caché para listados
3. Considerar escalado horizontal > 100 usuarios
```

## 🚀 Mejores Prácticas

1. **Ejecutar pruebas en entorno similar a producción**
2. **Calentar el sistema antes de medir** (warm-up)
3. **Ejecutar múltiples veces** para confirmar resultados
4. **Monitorear recursos** durante las pruebas
5. **Documentar configuraciones** y resultados
6. **Comparar métricas** entre versiones
7. **Automatizar pruebas** en CI/CD

## 🔗 Referencias

- [Apache JMeter Documentation](https://jmeter.apache.org/usermanual/index.html)
- [Performance Testing Guide](https://www.perfmatrix.com/)
- [JMeter Best Practices](https://jmeter.apache.org/usermanual/best-practices.html)

## 📄 Conclusión

Las pruebas de carga son esenciales para:
- Garantizar rendimiento bajo carga
- Planificar capacidad del sistema
- Identificar problemas antes de producción
- Optimizar recursos

**Próximos pasos:**
1. Ejecutar pruebas base
2. Analizar resultados
3. Optimizar cuellos de botella
4. Re-ejecutar y comparar
5. Documentar mejoras
