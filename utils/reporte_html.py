import json
import webbrowser
import tempfile
from models.resultado import Resultado


def generar_reporte(resultado: Resultado, abrir: bool = True) -> str:
    modulos_orden = [
        ("entorno_competitivo", "Entorno competitivo"),
        ("perfil_jugador", "Perfil del jugador"),
        ("estadisticas", "Estad\u00edsticas"),
        ("fisico_salud", "F\u00edsico y salud"),
        ("adaptacion", "Adaptaci\u00f3n"),
        ("zonas_presencia", "Zonas de presencia"),
        ("modelo_juego", "Modelo de juego"),
        ("viabilidad", "Viabilidad contractual"),
    ]

    compat_data = []
    radar_labels = []
    radar_values = []
    for key, label in modulos_orden:
        compat = resultado.compatibilidades.get(key, 0)
        compat_pct = round(compat * 100, 1)
        sj = resultado.scores_jugador.get(key, 0)
        sc = resultado.scores_club.get(key, 0)
        sj_str = f"{sj:.1f}" if isinstance(sj, (int, float)) else str(sj)
        sc_str = f"{sc:.1f}" if isinstance(sc, (int, float)) else str(sc)
        compat_data.append((label, sj_str, sc_str, compat_pct))
        radar_labels.append(label)
        radar_values.append(compat_pct)

    perfiles = [
        ("Rendimiento inmediato", resultado.score_rendimiento_inmediato, "rendimiento_inmediato"),
        ("Potencial mediano plazo", resultado.score_potencial_mediano, "potencial_mediano_plazo"),
        ("Bajo riesgo de fracaso", resultado.score_bajo_riesgo, "bajo_riesgo_fracaso"),
    ]

    perfil_activo = resultado.perfil_evaluacion
    bar_labels = []
    bar_values = []
    bar_colors = []
    for nombre, score, key in perfiles:
        bar_labels.append(nombre)
        bar_values.append(score)
        if key == perfil_activo:
            bar_colors.append("rgba(59, 130, 246, 0.85)")
        else:
            bar_colors.append("rgba(148, 163, 184, 0.5)")

    s = resultado.score_final
    if s >= 85:
        score_color = "#22c55e"
        score_label = resultado.interpretacion()
    elif s >= 70:
        score_color = "#84cc16"
        score_label = resultado.interpretacion()
    elif s >= 55:
        score_color = "#f59e0b"
        score_label = resultado.interpretacion()
    elif s >= 40:
        score_color = "#f97316"
        score_label = resultado.interpretacion()
    else:
        score_color = "#ef4444"
        score_label = resultado.interpretacion()

    niveles = {1: "1 \u2014 Baja", 2: "2 \u2014 Media", 3: "3 \u2014 Alta"}
    nivel_texto = niveles.get(resultado.nivel_brecha, str(resultado.nivel_brecha))
    penalizacion_texto = (
        f"{resultado.penalizacion_aplicada * 100:.0f}%"
        if resultado.penalizacion_aplicada > 0
        else "Sin penalizaci\u00f3n"
    )

    radar_json = json.dumps(radar_labels, ensure_ascii=False)
    radar_vals_json = json.dumps(radar_values)
    bar_labels_json = json.dumps(bar_labels, ensure_ascii=False)
    bar_vals_json = json.dumps(bar_values)

    compat_rows = ""
    for label, sj, sc, pct in compat_data:
        bar_lleno = int(pct / 100 * 20)
        bar_vacio = 20 - bar_lleno
        barra = "\u2588" * bar_lleno + "\u2591" * bar_vacio
        compat_rows += f"""
            <tr>
                <td>{label}</td>
                <td class="num">{sj}</td>
                <td class="num">{sc}</td>
                <td class="num">{pct:.1f}%</td>
                <td><span class="bar">{barra}</span></td>
            </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MPSc — Resultado de compatibilidad</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #0f172a; color: #e2e8f0; min-height: 100vh;
  }}
  .container {{ max-width: 1100px; margin: 0 auto; padding: 2rem 1.5rem; }}
  .header {{
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    border-radius: 16px; padding: 2rem; margin-bottom: 1.5rem;
    border: 1px solid #334155;
  }}
  .header h1 {{
    font-size: 1.25rem; font-weight: 600; color: #94a3b8;
    letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 0.5rem;
  }}
  .header .score-row {{
    display: flex; align-items: center; justify-content: space-between;
    flex-wrap: wrap; gap: 1rem;
  }}
  .score-ring {{
    display: flex; align-items: center; gap: 1.5rem;
  }}
  .score-ring .number {{
    font-size: 3.5rem; font-weight: 800; line-height: 1;
  }}
  .score-ring .label {{ font-size: 1.1rem; font-weight: 500; }}
  .info-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem; margin-top: 1rem; padding-top: 1rem;
    border-top: 1px solid #334155;
  }}
  .info-item .info-label {{ font-size: 0.75rem; color: #64748b; text-transform: uppercase; }}
  .info-item .info-value {{ font-size: 1rem; font-weight: 600; margin-top: 0.2rem; }}
  .cards {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 1.5rem; }}
  @media (max-width: 768px) {{ .cards {{ grid-template-columns: 1fr; }} }}
  .card {{
    background: #1e293b; border-radius: 12px; padding: 1.5rem;
    border: 1px solid #334155;
  }}
  .card h2 {{ font-size: 0.85rem; color: #94a3b8; text-transform: uppercase;
               letter-spacing: 0.05em; margin-bottom: 1rem; }}
  .card canvas {{ width: 100% !important; height: auto !important; max-height: 300px; }}
  .breach-card {{
    background: #1e293b; border-radius: 12px; padding: 1.5rem;
    border: 1px solid #334155; margin-bottom: 1.5rem;
    display: flex; flex-wrap: wrap; gap: 2rem;
  }}
  .breach-card .item {{ }}
  .breach-card .item .lbl {{ font-size: 0.75rem; color: #64748b; text-transform: uppercase; }}
  .breach-card .item .val {{ font-size: 1.25rem; font-weight: 700; margin-top: 0.2rem; }}
  table {{
    width: 100%; border-collapse: collapse;
    background: #1e293b; border-radius: 12px; overflow: hidden;
    border: 1px solid #334155;
  }}
  th {{
    text-align: left; padding: 0.75rem 1rem; font-size: 0.75rem;
    color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;
    background: #334155; border-bottom: 1px solid #475569;
  }}
  td {{ padding: 0.6rem 1rem; border-bottom: 1px solid #334155; font-size: 0.9rem; }}
  tr:last-child td {{ border-bottom: none; }}
  td.num {{ font-family: 'SF Mono', 'Fira Code', monospace; text-align: center; }}
  .bar {{ color: #475569; font-size: 0.85rem; letter-spacing: 0; }}
  .profile-section {{ margin-top: 1.5rem; }}
  .profile-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1rem; margin-top: 0.75rem;
  }}
  .profile-card {{
    background: #1e293b; border-radius: 10px; padding: 1rem 1.25rem;
    border: 1px solid #334155;
  }}
  .profile-card.active {{ border-color: #3b82f6; }}
  .profile-card .pname {{ font-size: 0.85rem; color: #94a3b8; }}
  .profile-card .pscore {{ font-size: 2rem; font-weight: 700; }}
  .profile-card .pactive {{ font-size: 0.7rem; color: #3b82f6; font-weight: 600;
                             text-transform: uppercase; }}
  .footer {{ text-align: center; margin-top: 2rem; font-size: 0.8rem; color: #475569; }}
</style>
</head>
<body>
<div class="container">

  <div class="header">
    <h1>MPSc — Modelo Predictivo de Scouting</h1>
    <div class="score-row">
      <div class="score-ring">
        <div class="number" style="color:{score_color}">{s:.1f}%</div>
        <div>
          <div class="label" style="color:{score_color}">{score_label}</div>
          <div style="font-size:0.85rem;color:#94a3b8;margin-top:0.25rem;">
            {resultado.perfil_evaluacion.replace('_',' ').title()}
          </div>
        </div>
      </div>
    </div>
    <div class="info-grid">
      <div class="info-item"><div class="info-label">Jugador</div><div class="info-value">{resultado.nombre_jugador}</div></div>
      <div class="info-item"><div class="info-label">Club destino</div><div class="info-value">{resultado.nombre_club}</div></div>
      <div class="info-item"><div class="info-label">Valor de mercado</div><div class="info-value">{resultado.valor_mercado}</div></div>
    </div>
  </div>

  <div class="breach-card">
    <div class="item">
      <div class="lbl">Nivel de brecha</div>
      <div class="val">{nivel_texto}</div>
    </div>
    <div class="item">
      <div class="lbl">D coef</div>
      <div class="val">{resultado.delta_coef}</div>
    </div>
    <div class="item">
      <div class="lbl">Penalizaci\u00f3n aplicada</div>
      <div class="val" style="color:{'#ef4444' if resultado.penalizacion_aplicada > 0 else '#22c55e'}">{penalizacion_texto}</div>
    </div>
    <div class="item">
      <div class="lbl">Confiabilidad estad\u00edsticas</div>
      <div class="val" style="color:{'#22c55e' if resultado.confiabilidad_estadisticas >= 0.9 else '#f59e0b' if resultado.confiabilidad_estadisticas >= 0.7 else '#ef4444'}">{resultado.confiabilidad_estadisticas*100:.0f}%</div>
    </div>
    <div class="item">
      <div class="lbl">Factor contexto global</div>
      <div class="val">{resultado.factor_contexto_global:.3f}</div>
    </div>
  </div>

  <div class="cards">
    <div class="card">
      <h2>Compatibilidad por m\u00f3dulo</h2>
      <canvas id="radarChart"></canvas>
    </div>
    <div class="card">
      <h2>Scores por perfil de evaluaci\u00f3n</h2>
      <canvas id="barChart"></canvas>
    </div>
  </div>

  <table>
    <thead>
      <tr><th>M\u00f3dulo</th><th style="text-align:center">J</th><th style="text-align:center">C</th><th style="text-align:center">Compat.</th><th></th></tr>
    </thead>
    <tbody>
      {compat_rows}
    </tbody>
  </table>

  <div class="profile-section">
    <div style="font-size:0.85rem;color:#94a3b8;text-transform:uppercase;letter-spacing:0.05em;">Scores por perfil</div>
    <div class="profile-grid">
"""

    for nombre, score, key in perfiles:
        cls = 'active' if key == perfil_activo else ''
        active_tag = f'<div class="pactive">\u2190 ACTIVO</div>' if key == perfil_activo else ''
        c = "#22c55e" if score >= 85 else "#84cc16" if score >= 70 else "#f59e0b" if score >= 55 else "#f97316" if score >= 40 else "#ef4444"
        html += f"""
      <div class="profile-card {cls}">
        <div class="pname">{nombre}</div>
        <div class="pscore" style="color:{c}">{score:.1f}%</div>
        {active_tag}
      </div>"""

    html += f"""
    </div>
  </div>

  <div class="footer">
    Generado por MPSc v1.0
  </div>
</div>

<script>
  const radarCtx = document.getElementById('radarChart').getContext('2d');
  new Chart(radarCtx, {{
    type: 'radar',
    data: {{
      labels: {radar_json},
      datasets: [{{
        label: 'Compatibilidad',
        data: {radar_vals_json},
        backgroundColor: 'rgba(59, 130, 246, 0.15)',
        borderColor: 'rgba(59, 130, 246, 0.8)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(59, 130, 246, 0.8)',
        pointRadius: 4,
      }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: true,
      scales: {{
        r: {{
          beginAtZero: true,
          max: 100,
          ticks: {{ stepSize: 20, color: '#64748b', backdropColor: 'transparent', font: {{ size: 10 }} }},
          grid: {{ color: 'rgba(148, 163, 184, 0.15)' }},
          angleLines: {{ color: 'rgba(148, 163, 184, 0.15)' }},
          pointLabels: {{ color: '#cbd5e1', font: {{ size: 11 }} }}
        }}
      }},
      plugins: {{
        legend: {{ display: false }},
      }}
    }}
  }});

  const barCtx = document.getElementById('barChart').getContext('2d');
  new Chart(barCtx, {{
    type: 'bar',
    data: {{
      labels: {bar_labels_json},
      datasets: [{{
        label: 'Score',
        data: {bar_vals_json},
        backgroundColor: {json.dumps(bar_colors)},
        borderRadius: 6,
        barPercentage: 0.6,
      }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: true,
      indexAxis: 'y',
      scales: {{
        x: {{
          beginAtZero: true,
          max: 110,
          ticks: {{ color: '#64748b', font: {{ size: 10 }} }},
          grid: {{ color: 'rgba(148, 163, 184, 0.1)' }}
        }},
        y: {{
          ticks: {{ color: '#cbd5e1', font: {{ size: 11 }} }},
          grid: {{ display: false }}
        }}
      }},
      plugins: {{
        legend: {{ display: false }},
      }}
    }}
  }});
</script>
</body>
</html>"""

    f = tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", delete=False, encoding="utf-8"
    )
    f.write(html)
    f.close()

    if abrir:
        webbrowser.open(f"file://{f.name}")

    return f.name
