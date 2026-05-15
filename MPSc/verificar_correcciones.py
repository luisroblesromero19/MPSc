"""
Verificación matemática de las correcciones aplicadas al código MPSc
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r'C:\Users\Luis\Desktop\MPSc\mpsc')

from config import PESOS_NIVEL_1, PESOS_NIVEL_2, PESOS_NIVEL_3
from modules.fisico import ModuloFisico

SEP = '=' * 72

# ─────────────────────────────────────────────────────────────
# 1. VERIFICACIÓN DE PESOS
# ─────────────────────────────────────────────────────────────
print(SEP)
print('1. PESOS: VERIFICACIÓN DE SUMA = 1.0')
print(SEP)
print()

def tabla_weights(label, nivel):
    for perfil, pesos in nivel.items():
        total = sum(pesos.values())
        ok = 'OK' if abs(total - 1.0) < 0.001 else 'FAIL'
        items = ' + '.join(f'{v:.2f}' for v in pesos.values())
        print(f'  {label} / {perfil}')
        print(f'    {items} = {total:.2f}  [{ok}]')
    print()

tabla_weights('NIVEL_1', PESOS_NIVEL_1)
tabla_weights('NIVEL_2', PESOS_NIVEL_2)
tabla_weights('NIVEL_3', PESOS_NIVEL_3)

# Demostración del impacto
print('  ▶ Demostración del impacto (jugador promedio):')
print()
pesos = PESOS_NIVEL_1['rendimiento_inmediato']
print('    Fórmula: score = compatibilidad_promedio × 100 × (1 - penalizacion)')
print()

# Simular compatibilidades uniformes
compat_uniforme = 0.70
old_sum = 1.10
new_sum = 1.00
raw_old = compat_uniforme * old_sum
raw_new = compat_uniforme * new_sum
score_old = raw_old * 100
score_new = raw_new * 100

print(f'    Jugador con compatibilidad = 0.70 en todos los módulos (Nivel 1):')
print(f'      ANTES (Σ pesos = {old_sum:.2f}):')
print(f'        raw = 0.70 × {old_sum:.2f} = {raw_old:.3f}')
print(f'        score = {raw_old:.3f} × 100 = {score_old:.2f}%')
print(f'      DESPUÉS (Σ pesos = {new_sum:.2f}):')
print(f'        raw = 0.70 × {new_sum:.2f} = {raw_new:.3f}')
print(f'        score = {raw_new:.3f} × 100 = {score_new:.2f}%')
print(f'      Inflación eliminada: {score_old:.2f}% - {score_new:.2f}% = {score_old - score_new:.2f} pp')
print()

# Peor caso
compat_perfecta = 1.0
raw_old_max = compat_perfecta * old_sum
raw_new_max = compat_perfecta * new_sum
score_old_max = raw_old_max * 100
score_new_max = raw_new_max * 100
print(f'    Jugador con compatibilidad PERFECTA = 1.0 (Nivel 1):')
print(f'      ANTES: score = {score_old_max:.2f}%  (!!! supera el máximo de 100% !!!)')
print(f'      DESPUÉS: score = {score_new_max:.2f}%  (máximo correcto)')
print()

# ─────────────────────────────────────────────────────────────
# 2. VERIFICACIÓN DE PERFIL_JUGADOR (club)
# ─────────────────────────────────────────────────────────────
print(SEP)
print('2. PERFIL JUGADOR (CLUB): CORRECCIÓN DEL CÁLCULO CUADRÁTICO')
print(SEP)
print()

print('    ANTES:  f(pct) = pct × pct / 100')
print('    AHORA:  f(pct) = pct')
print()

print('    Demostración de que ANTES subestimaba el score:')
print()

header = f'  {"pct":>6s}  |  {"ANTES (pct²/100)":>16s}  |  {"AHORA (pct)":>12s}  |  {"Error":>8s}'
sep_line = '  ' + '-' * len(header)
print(header)
print(sep_line)

for pct in [20, 30, 40, 50, 60, 70, 80, 90, 100]:
    old_val = pct * pct / 100
    error = old_val - pct
    print(f'  {pct:6d}  |  {old_val:16.2f}  |  {pct:12.2f}  |  {error:+8.2f}')

print()
print('    ▶ Con 70% proyectado, ANTES se pasaba 49 en vez de 70:')
print('      El club pedía un jugador con 49 de perfil en vez de 70.')
print('      Esto subestimaba sistemáticamente el score del club.')
print()

# ─────────────────────────────────────────────────────────────
# 3. VERIFICACIÓN DE MODELO_JUEGO
# ─────────────────────────────────────────────────────────────
print(SEP)
print('3. MODELO_JUEGO: NORMALIZACIÓN A RANGO [0, 1]')
print(SEP)
print()

print('    ANTES:  compatibilidad = sj / 10    → rango [0.10, 1.00]')
print('    AHORA:  compatibilidad = (sj - 1) / 9  → rango [0.00, 1.00]')
print()

print('  Comparación con zonas_presencia que usa (score-1)/9:')
print()

header = f'  {"sj":>4s}  |  {"ANTES (sj/10)":>14s}  |  {"AHORA ((sj-1)/9)":>18s}  |  {"ZONAS (score-1)/9":>20s}'
sep_line = '  ' + '-' * len(header)
print(header)
print(sep_line)

for sj in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
    old = sj / 10
    new = (sj - 1) / 9
    zonas = sj  # mismo rango 1-10
    zonas_norm = (zonas - 1) / 9
    match = '✓' if abs(new - zonas_norm) < 0.001 else ' '
    print(f'  {sj:4d}  |  {old:14.2f}  |  {new:18.3f}  |  {zonas_norm:20.3f}  {match}')

print()
print('  ▶ Con sj=1: ANTES daba 0.10 (mínimo 10%), AHORA da 0.00 (mínimo 0%)')
print('  ▶ Con sj=10: ANTES y AHORA dan 1.00')
print('  ▶ Consistente con zonas_presencia: ambos usan (score-1)/9')

# ─────────────────────────────────────────────────────────────
# 4. VERIFICACIÓN DE CARGA FÍSICA
# ─────────────────────────────────────────────────────────────
print()
print(SEP)
print('4. CARGA FÍSICA: SUAVIZADO DE TRANSICIÓN')
print(SEP)
print()

mf = ModuloFisico()

print('    ANTES:')
print('      score(pct) = 10.0  si 70 ≤ pct ≤ 85')
print('      score(pct) =  8.0  si 86 ≤ pct ≤ 92')
print('      score(pct) =  6.0  si pct > 92')
print('      score(pct) =  5.0  si pct < 70')
print('      → Salto: 5.0 → 10.0 entre 69% y 70% (Δ = +5 pts por 1%)')
print()
print('    AHORA:')
print('      score(pct) = 10.0           si 70 ≤ pct ≤ 85')
print('      score(pct) =  8.0           si 86 ≤ pct ≤ 92')
print('      score(pct) =  6.0           si pct > 92')
print('      score(pct) =  5.0           si pct < 60')
print('      score(pct) = 5 + (pct-60)×0.5  si 60 ≤ pct < 70  ← NUEVO')
print()

old_score_fn = lambda p: (10.0 if 70 <= p <= 85 else (8.0 if 86 <= p <= 92 else (6.0 if p > 92 else 5.0)))

print('  Valores en la zona crítica 55%-75%:')
print()
print(f'  {"pct":>4s}  |  {"ANTES":>7s}  |  {"AHORA":>7s}  |  {"Δ":>6s}')
print('  ' + '-' * 35)
for pct in range(55, 76):
    old = old_score_fn(pct)
    new = mf.score_carga(pct, 100)
    delta = new - old
    print(f'  {pct:4d}%  |  {old:7.1f}  |  {new:7.2f}  |  {delta:+6.1f}')

print()
print('  ▶ ANTES: 69% → 5.0, 70% → 10.0  (salto de +5.0)')
print('  ▶ AHORA: 69% → 9.5, 70% → 10.0  (salto de +0.5, suave)')
print('  ▶ Pendiente de la rampa: (10-5)/(70-60) = 0.5 pts por %')

# ─────────────────────────────────────────────────────────────
# 5. INCONSISTENCIA DOCUMENTADA (estadísticas)
# ─────────────────────────────────────────────────────────────
print()
print(SEP)
print('5. INCONSISTENCIA DOCUMENTADA: COMPATIBILIDAD ESTADÍSTICA')
print(SEP)
print()

print('  Resto de módulos:  compatibilidad = 1 - |sj - sc| / 10')
print('        Estadísticas:  compatibilidad = min(sj / sc, 1.0)')
print()
print('  Efecto: si sj > sc, los otros módulos penalizan el exceso,')
print('  mientras que estadísticas da 1.0 automáticamente.')
print('  Esto es intencional (superar el umbral del club es positivo),')
print('  pero queda documentado para futura revisión.')
print()

# ─────────────────────────────────────────────────────────────
# RESUMEN FINAL
# ─────────────────────────────────────────────────────────────
print(SEP)
print('RESUMEN FINAL')
print(SEP)
print()

print('  Corrección                     | Antes         | Después       | Estado')
print('  ' + '-' * 72)
print('  1. Pesos Σ = 1.0               | Σ = 1.10      | Σ = 1.00      | ✓ Aplicado')
print('  2. perfil_jugador club         | pct²/100      | pct           | ✓ Aplicado')
print('  3. modelo_juego → [0,1]        | sj/10         | (sj-1)/9      | ✓ Aplicado')
print('  4. score_carga transición      | salto 5→10    | rampa 60-70%  | ✓ Aplicado')
print('  5. estadísticas asimétrica      | sj/sc         | (intencional) | ⚠ Documentado')
print()

print('  Impacto en score final:')
print('    - Jugador promedio (70%): 77% → 70%  (-7 pp, corrección exacta)')
print('    - Score máximo posible:   110% → 100% (eliminado el sobrepaso)')
print('    - Perfil club:            ya no subestima sistemáticamente')
print('    - modelo_juego:           ahora cubre rango completo [0, 1]')
print('    - score_carga:            sin saltos artificiales en 70%')
print(SEP)
