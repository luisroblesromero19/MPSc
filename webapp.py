"""
MPSc — webapp.py
Servidor HTTP con interfaz web para el Modelo Predictivo de Scouting v1.0
"""
import http.server
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from calculadora import Calculadora
from models.jugador import Jugador
from models.club import Club
from modules.contexto_equipo import extraer_estadisticas_jugador

_HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MPSc — Evaluaci&oacute;n de Compatibilidad</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js">
</script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#0f172a;color:#e2e8f0;min-height:100vh}
.container{max-width:1200px;margin:0 auto;padding:1.5rem}
h1{font-size:1.5rem;font-weight:700;color:#e2e8f0;margin-bottom:.25rem}
.subtitle{color:#64748b;font-size:.85rem;margin-bottom:1.5rem}
.section{background:#1e293b;border-radius:12px;padding:1.5rem;margin-bottom:1.25rem;border:1px solid #334155}
.section h2{font-size:.85rem;color:#94a3b8;text-transform:uppercase;letter-spacing:.05em;margin-bottom:1rem;padding-bottom:.5rem;border-bottom:1px solid #334155}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:1rem}
.grid-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem}
.grid-4{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:1rem}
@media(max-width:768px){.grid-2,.grid-3,.grid-4{grid-template-columns:1fr}}
.field{display:flex;flex-direction:column;gap:.25rem}
.field label{font-size:.8rem;color:#94a3b8;font-weight:500}
.field input,.field select,.field textarea{padding:.6rem .75rem;border-radius:8px;border:1px solid #334155;background:#0f172a;color:#e2e8f0;font-size:.9rem;outline:none;transition:border-color .15s}
.field input:focus,.field select:focus{border-color:#3b82f6}
.field input[type=checkbox]{width:1.1rem;height:1.1rem;accent-color:#3b82f6;margin-top:.25rem}
.field input[type=range]{padding:0;background:0 0;border:none}
.field .checkbox-wrap{display:flex;align-items:center;gap:.5rem;padding-top:.25rem}
.field input[type=number]{-moz-appearance:textfield}
.field input[type=number]::-webkit-inner-spin-button{-webkit-appearance:none}
.zona-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;max-width:480px;margin-top:.5rem}
.zona-cell{padding:.5rem;text-align:center;border-radius:8px;border:1px solid #334155;background:#0f172a;cursor:pointer;font-size:.8rem;transition:all .15s;user-select:none}
.zona-cell:hover{border-color:#3b82f6}
.zona-cell.selected{background:#1d4ed8;border-color:#3b82f6;color:#fff;font-weight:600}
.zona-cell .z-num{font-weight:700;font-size:.9rem}
.zona-cell .z-desc{font-size:.65rem;color:#64748b;margin-top:2px}
.zona-cell.selected .z-desc{color:#bfdbfe}
.zona-count{font-size:.8rem;color:#64748b;margin-top:.5rem}
.stats-grid{display:grid;grid-template-columns:1fr 1fr;gap:.75rem}
@media(max-width:768px){.stats-grid{grid-template-columns:1fr}}
.stat-hidden{display:none!important}
.btn{padding:.75rem 2rem;border-radius:10px;border:none;font-size:1rem;font-weight:600;cursor:pointer;transition:all .15s;background:#3b82f6;color:#fff}
.btn:hover{background:#2563eb}
.btn:disabled{opacity:.6;cursor:not-allowed}
.btn-wrap{text-align:center;margin:1.5rem 0}
.loading{display:none;align-items:center;justify-content:center;gap:.5rem;padding:1rem;color:#94a3b8}
.loading.active{display:flex}
.spinner{width:20px;height:20px;border:2px solid #334155;border-top-color:#3b82f6;border-radius:50%;animation:spin .6s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.results{display:none}
.results.active{display:block}
.result-header{background:linear-gradient(135deg,#1e293b 0,#334155 100%);border-radius:16px;padding:2rem;margin-bottom:1.25rem;border:1px solid #334155}
.result-header h3{font-size:.85rem;font-weight:600;color:#94a3b8;letter-spacing:.05em;text-transform:uppercase;margin-bottom:.5rem}
.score-row{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem}
.score-ring{display:flex;align-items:center;gap:1.5rem}
.score-ring .number{font-size:3.5rem;font-weight:800;line-height:1}
.score-ring .label{font-size:1.1rem;font-weight:500}
.info-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1.5rem;margin-top:1rem;padding-top:1rem;border-top:1px solid #334155}
.info-item .info-label{font-size:.75rem;color:#64748b;text-transform:uppercase}
.info-item .info-value{font-size:1rem;font-weight:600;margin-top:.2rem}
.cards-2{display:grid;grid-template-columns:1fr 1fr;gap:1.25rem;margin-bottom:1.25rem}
@media(max-width:768px){.cards-2{grid-template-columns:1fr}}
.card{background:#1e293b;border-radius:12px;padding:1.5rem;border:1px solid #334155}
.card h4{font-size:.85rem;color:#94a3b8;text-transform:uppercase;letter-spacing:.05em;margin-bottom:1rem}
.card canvas{width:100%!important;height:auto!important;max-height:300px}
.breach-card{background:#1e293b;border-radius:12px;padding:1.25rem 1.5rem;border:1px solid #334155;margin-bottom:1.25rem;display:flex;flex-wrap:wrap;gap:2rem}
.breach-item .lbl{font-size:.75rem;color:#64748b;text-transform:uppercase}
.breach-item .val{font-size:1.25rem;font-weight:700;margin-top:.2rem}
table.tabla{width:100%;border-collapse:collapse;background:#1e293b;border-radius:12px;overflow:hidden;border:1px solid #334155;margin-bottom:1.25rem}
table.tabla th{text-align:left;padding:.75rem 1rem;font-size:.75rem;color:#64748b;text-transform:uppercase;letter-spacing:.05em;background:#334155;border-bottom:1px solid #475569}
table.tabla td{padding:.6rem 1rem;border-bottom:1px solid #334155;font-size:.9rem}
table.tabla tr:last-child td{border-bottom:none}
table.tabla td.num{font-family:'SF Mono','Fira Code',monospace;text-align:center}
.profile-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1rem;margin-top:.75rem}
.profile-card{background:#1e293b;border-radius:10px;padding:1rem 1.25rem;border:1px solid #334155}
.profile-card.active{border-color:#3b82f6}
.profile-card .pname{font-size:.85rem;color:#94a3b8}
.profile-card .pscore{font-size:2rem;font-weight:700}
.profile-card .pactive{font-size:.7rem;color:#3b82f6;font-weight:600;text-transform:uppercase}
.bar-vis{display:flex;align-items:center;gap:.25rem}
.bar-vis .bar-fill{height:8px;border-radius:4px;background:#3b82f6;transition:width .3s}
.bar-vis .bar-bg{height:8px;border-radius:4px;background:#334155;flex:1}
.footer{text-align:center;margin-top:2rem;font-size:.8rem;color:#475569}
.error-msg{background:rgba(239,68,68,.15);border:1px solid #ef4444;border-radius:8px;padding:1rem;color:#fca5a5;margin-bottom:1rem;display:none}
.error-msg.active{display:block}
</style>
</head>
<body>
<div class="container" id="app">
  <h1>MPSc — Modelo Predictivo de Scouting</h1>
  <div class="subtitle">Evaluaci&oacute;n de compatibilidad jugador &harr; club</div>

  <div class="error-msg" id="errorMsg"></div>

  <form id="evalForm" onsubmit="return false;">

    <!-- SECTION 1: Player Basic Info -->
    <div class="section">
      <h2>Datos b&aacute;sicos del jugador</h2>
      <div class="grid-3">
        <div class="field">
          <label for="nombre">Nombre completo</label>
          <input type="text" id="nombre" name="nombre" required>
        </div>
        <div class="field">
          <label for="fecha_nacimiento">Fecha de nacimiento</label>
          <input type="date" id="fecha_nacimiento" name="fecha_nacimiento" onchange="calcEdad()">
        </div>
        <div class="field">
          <label for="edad">Edad (a&ntilde;os)</label>
          <input type="number" id="edad" name="edad" min="15" max="45" readonly>
        </div>
        <div class="field">
          <label for="pais_origen">Pa&iacute;s de origen</label>
          <input type="text" id="pais_origen" name="pais_origen">
        </div>
        <div class="field">
          <label for="ciudad_actual">Ciudad actual</label>
          <input type="text" id="ciudad_actual" name="ciudad_actual">
        </div>
        <div class="field">
          <label for="idioma">Idioma principal</label>
          <input type="text" id="idioma" name="idioma">
        </div>
        <div class="field">
          <div class="checkbox-wrap">
            <input type="checkbox" id="experiencia_extranjero" name="experiencia_extranjero">
            <label for="experiencia_extranjero">Experiencia en el extranjero</label>
          </div>
        </div>
        <div class="field">
          <label for="valor_mercado">Valor de mercado (ej. &euro;150,000)</label>
          <input type="text" id="valor_mercado" name="valor_mercado" placeholder="&euro;150,000">
        </div>
      </div>
    </div>

    <!-- SECTION 2: Contract -->
    <div class="section">
      <h2>Contrato actual</h2>
      <div class="grid-3">
        <div class="field">
          <label for="meses_contrato">Meses restantes de contrato</label>
          <input type="number" id="meses_contrato" name="meses_contrato" min="0" max="60" value="0">
        </div>
        <div class="field">
          <div class="checkbox-wrap">
            <input type="checkbox" id="tiene_clausula" name="tiene_clausula" onchange="toggleClausula()">
            <label for="tiene_clausula">Tiene cl&aacute;usula de salida</label>
          </div>
        </div>
        <div class="field" id="clausula_field" style="display:none">
          <label for="clausula_nivel">Nivel de cl&aacute;usula</label>
          <select id="clausula_nivel" name="clausula_nivel">
            <option value="">Seleccionar...</option>
            <option value="accesible">Accesible</option>
            <option value="alta">Alta</option>
          </select>
        </div>
      </div>
    </div>

    <!-- SECTION 3: Player Current Club -->
    <div class="section">
      <h2>Club actual del jugador</h2>
      <div class="grid-3">
        <div class="field">
          <label for="club_actual">Nombre del club</label>
          <input type="text" id="club_actual" name="club_actual">
        </div>
        <div class="field">
          <label for="liga_j">Liga</label>
          <select id="liga_j" name="liga_j">
            <option value="">Seleccionar...</option>
            <option value="liga_mx">Liga MX</option>
            <option value="liga_expansion_mx">Liga Expansi&oacute;n MX</option>
            <option value="mls">MLS</option>
            <option value="liga_colombiana">Liga Colombiana</option>
            <option value="liga_argentina">Liga Argentina</option>
            <option value="liga_chilena">Liga Chilena</option>
            <option value="liga_peruana">Liga Peruana</option>
            <option value="segunda_division_mx">Segunda Divisi&oacute;n MX</option>
          </select>
        </div>
        <div class="field">
          <label for="posicion_tabla_j">Posici&oacute;n en tabla</label>
          <input type="number" id="posicion_tabla_j" name="posicion_tabla_j" min="1" max="30" value="1">
        </div>
        <div class="field">
          <label for="total_equipos_liga_j">Total equipos en liga</label>
          <input type="number" id="total_equipos_liga_j" name="total_equipos_liga_j" min="2" max="30" value="18">
        </div>
        <div class="field">
          <div class="checkbox-wrap">
            <input type="checkbox" id="tiene_copa_j" name="tiene_copa_j">
            <label for="tiene_copa_j">Participa en copa nacional</label>
          </div>
        </div>
        <div class="field">
          <div class="checkbox-wrap">
            <input type="checkbox" id="tiene_internacional_j" name="tiene_internacional_j">
            <label for="tiene_internacional_j">Participa en competici&oacute;n internacional</label>
          </div>
        </div>
        <div class="field">
          <label for="sistema_tactico_club">Sistema t&aacute;ctico del club</label>
          <input type="text" id="sistema_tactico_club" name="sistema_tactico_club" placeholder="Ej: 4-3-3">
        </div>
        <div class="field">
          <label for="estilo_ofensivo_j">Estilo ofensivo</label>
          <input type="text" id="estilo_ofensivo_j" name="estilo_ofensivo_j">
        </div>
        <div class="field">
          <label for="estilo_defensivo_j">Estilo defensivo</label>
          <input type="text" id="estilo_defensivo_j" name="estilo_defensivo_j">
        </div>
        <div class="field">
          <label for="estilo_transicion_j">Estilo de transici&oacute;n</label>
          <input type="text" id="estilo_transicion_j" name="estilo_transicion_j">
        </div>
        <div class="field">
          <label for="altitud_ciudad_j">Altitud de la ciudad (msnm)</label>
          <input type="number" id="altitud_ciudad_j" name="altitud_ciudad_j" min="0" max="5000" value="0">
        </div>
      </div>
    </div>

    <!-- SECTION 4: Participation & Physical -->
    <div class="section">
      <h2>Participaci&oacute;n y estado f&iacute;sico</h2>
      <div class="grid-3">
        <div class="field">
          <label for="minutos_jugados">Minutos jugados en temporada</label>
          <input type="number" id="minutos_jugados" name="minutos_jugados" min="0" value="0">
        </div>
        <div class="field">
          <label for="minutos_posibles">Minutos posibles totales</label>
          <input type="number" id="minutos_posibles" name="minutos_posibles" min="0" value="0">
        </div>
        <div class="field">
          <label for="posicion">Posici&oacute;n</label>
          <select id="posicion" name="posicion" onchange="onPosicionChange()">
            <option value="">Seleccionar...</option>
            <option value="portero">Portero</option>
            <option value="central">Central</option>
            <option value="lateral">Lateral</option>
            <option value="mediocampista_defensivo">Mediocampista Defensivo</option>
            <option value="mediocampista_central">Mediocampista Central</option>
            <option value="extremo">Extremo</option>
            <option value="delantero_centro">Delantero Centro</option>
          </select>
        </div>
        <div class="field">
          <label for="rol">Rol en el equipo</label>
          <select id="rol" name="rol">
            <option value="titular_indiscutible">Titular Indiscutible</option>
            <option value="titular_con_competencia">Titular con Competencia</option>
            <option value="rotacion_habitual">Rotaci&oacute;n Habitual</option>
            <option value="suplente">Suplente</option>
            <option value="sin_minutos">Sin Minutos</option>
          </select>
        </div>
        <div class="field">
          <label for="num_lesiones">N&uacute;mero de lesiones en la temporada</label>
          <input type="number" id="num_lesiones" name="num_lesiones" min="0" max="20" value="0">
        </div>
        <div class="field">
          <label for="tipo_lesion">Tipo de lesi&oacute;n m&aacute;s grave</label>
          <select id="tipo_lesion" name="tipo_lesion">
            <option value="ninguna">Ninguna</option>
            <option value="muscular">Muscular</option>
            <option value="ligamento">Ligamento</option>
            <option value="fractura">Fractura</option>
          </select>
        </div>
        <div class="field">
          <label for="semanas_baja_promedio">Semanas de baja promedio</label>
          <input type="number" id="semanas_baja_promedio" name="semanas_baja_promedio" min="0" max="52" value="0" step="0.5">
        </div>
      </div>
    </div>

    <!-- SECTION 5: Player Zones -->
    <div class="section">
      <h2>Zonas de presencia del jugador (m&aacute;x. 5)</h2>
      <p style="color:#64748b;font-size:.8rem;margin-bottom:.75rem">Selecciona hasta 5 zonas donde el jugador se desempe&ntilde;a con mayor frecuencia.</p>
      <div class="zona-grid" id="zonaGridJ"></div>
      <div class="zona-count" id="zonaCountJ">0 de 5 seleccionadas</div>
    </div>

    <!-- SECTION 6: Sofascore — Player Stats -->
    <div class="section">
      <h2>Estad&iacute;sticas del jugador (Sofascore)</h2>
      <p style="color:#64748b;font-size:.8rem;margin-bottom:.75rem">
        Pega aqu&iacute; los datos del jugador en formato Sofascore. El sistema extraer&aacute; autom&aacute;ticamente las estad&iacute;sticas disponibles.
        Las estad&iacute;sticas no encontradas podr&aacute;s ingresarlas manualmente debajo.
      </p>
      <div class="field">
        <label for="sofascore_jugador_raw">Datos Sofascore del jugador</label>
        <textarea id="sofascore_jugador_raw" rows="8" style="width:100%;background:#0f172a;color:#e2e8f0;border:1px solid #334155;border-radius:8px;padding:.75rem;font-family:'SF Mono','Fira Code',monospace;font-size:.8rem;resize:vertical" placeholder="Ej: Matches 17&#10;Goals 8&#10;Assists 5&#10;Shots per game 1.8&#10;Passes per game 42.3&#10;Pass accuracy % 81.2&#10;Tackles per game 1.1&#10;..." oninput="analizarSofascoreJugador()"></textarea>
      </div>
    </div>

    <!-- SECTION 6B: Missing Player Stats -->
    <div class="section" id="statsMissingSection" style="display:none">
      <h2>Estad&iacute;sticas no encontradas en Sofascore</h2>
      <p style="color:#64748b;font-size:.8rem;margin-bottom:.75rem">
        Ingresa manualmente las estad&iacute;sticas que no se pudieron extraer del texto de Sofascore.
      </p>
      <div id="statsFaltantesContainer" class="stats-grid"></div>
    </div>

    <!-- SECTION 6C: Sofascore — Club Origen -->
    <div class="section">
      <h2>Datos Sofascore — Club actual del jugador</h2>
      <p style="color:#64748b;font-size:.8rem;margin-bottom:.75rem">
        Pega aqu&iacute; los datos agregados del club actual del jugador en formato Sofascore.
        Se usar&aacute;n para calcular el factor de contexto y ajustar las estad&iacute;sticas.
        Si no pegas nada, se usar&aacute;n las estad&iacute;sticas sin correcci&oacute;n.
      </p>
      <div class="field">
        <label for="stats_club_origen_raw">Estad&iacute;sticas del club actual (Sofascore)</label>
        <textarea id="stats_club_origen_raw" rows="8" style="width:100%;background:#0f172a;color:#e2e8f0;border:1px solid #334155;border-radius:8px;padding:.75rem;font-family:'SF Mono','Fira Code',monospace;font-size:.8rem;resize:vertical" placeholder="Ej: Matches 12&#10;Goals scored 7&#10;Goals conceded 11&#10;Balls recovered per game 92.3&#10;Interceptions per game 38.6&#10;..."></textarea>
      </div>
    </div>

    <!-- SECTION 7: Club Destination -->
    <div class="section">
      <h2>Club destino</h2>
      <div class="grid-3">
        <div class="field">
          <label for="club_nombre">Nombre del club</label>
          <input type="text" id="club_nombre" name="club_nombre">
        </div>
        <div class="field">
          <label for="club_ciudad">Ciudad</label>
          <input type="text" id="club_ciudad" name="club_ciudad">
        </div>
        <div class="field">
          <label for="club_pais">Pa&iacute;s</label>
          <input type="text" id="club_pais" name="club_pais">
        </div>
        <div class="field">
          <label for="club_idioma">Idioma principal</label>
          <input type="text" id="club_idioma" name="club_idioma">
        </div>
        <div class="field">
          <label for="club_altitud">Altitud (msnm)</label>
          <input type="number" id="club_altitud" name="club_altitud" min="0" max="5000" value="0">
        </div>
        <div class="field">
          <label for="club_liga">Liga</label>
          <select id="club_liga" name="club_liga">
            <option value="">Seleccionar...</option>
            <option value="liga_mx">Liga MX</option>
            <option value="liga_expansion_mx">Liga Expansi&oacute;n MX</option>
            <option value="mls">MLS</option>
            <option value="liga_colombiana">Liga Colombiana</option>
            <option value="liga_argentina">Liga Argentina</option>
            <option value="liga_chilena">Liga Chilena</option>
            <option value="liga_peruana">Liga Peruana</option>
            <option value="segunda_division_mx">Segunda Divisi&oacute;n MX</option>
          </select>
        </div>
        <div class="field">
          <label for="club_posicion_tabla">Posici&oacute;n en tabla</label>
          <input type="number" id="club_posicion_tabla" name="club_posicion_tabla" min="1" max="30" value="1">
        </div>
        <div class="field">
          <label for="club_total_equipos">Total equipos en liga</label>
          <input type="number" id="club_total_equipos" name="club_total_equipos" min="2" max="30" value="18">
        </div>
        <div class="field">
          <label for="victorias_recientes">Victorias recientes (&uacute;lt. 5)</label>
          <input type="number" id="victorias_recientes" name="victorias_recientes" min="0" max="5" value="0">
        </div>
        <div class="field">
          <label for="empates_recientes">Empates recientes (&uacute;lt. 5)</label>
          <input type="number" id="empates_recientes" name="empates_recientes" min="0" max="5" value="0">
        </div>
        <div class="field">
          <label for="derrotas_recientes">Derrotas recientes (&uacute;lt. 5)</label>
          <input type="number" id="derrotas_recientes" name="derrotas_recientes" min="0" max="5" value="0">
        </div>
        <div class="field">
          <div class="checkbox-wrap">
            <input type="checkbox" id="club_tiene_copa" name="club_tiene_copa">
            <label for="club_tiene_copa">Participa en copa nacional</label>
          </div>
        </div>
        <div class="field">
          <div class="checkbox-wrap">
            <input type="checkbox" id="club_tiene_internacional" name="club_tiene_internacional">
            <label for="club_tiene_internacional">Participa en competici&oacute;n internacional</label>
          </div>
        </div>
        <div class="field">
          <label for="club_sistema_tactico">Sistema t&aacute;ctico</label>
          <input type="text" id="club_sistema_tactico" name="club_sistema_tactico" placeholder="Ej: 4-3-3">
        </div>
        <div class="field">
          <label for="club_estilo_ofensivo">Estilo ofensivo</label>
          <input type="text" id="club_estilo_ofensivo" name="club_estilo_ofensivo">
        </div>
        <div class="field">
          <label for="club_estilo_defensivo">Estilo defensivo</label>
          <input type="text" id="club_estilo_defensivo" name="club_estilo_defensivo">
        </div>
        <div class="field">
          <label for="club_estilo_transicion">Estilo de transici&oacute;n</label>
          <input type="text" id="club_estilo_transicion" name="club_estilo_transicion">
        </div>
        <div class="field">
          <label for="posicion_requerida">Posici&oacute;n requerida</label>
          <select id="posicion_requerida" name="posicion_requerida">
            <option value="">Seleccionar...</option>
            <option value="portero">Portero</option>
            <option value="central">Central</option>
            <option value="lateral">Lateral</option>
            <option value="mediocampista_defensivo">Mediocampista Defensivo</option>
            <option value="mediocampista_central">Mediocampista Central</option>
            <option value="extremo">Extremo</option>
            <option value="delantero_centro">Delantero Centro</option>
          </select>
        </div>
        <div class="field">
          <label for="perfil_tactico">Perfil t&aacute;ctico requerido</label>
          <input type="text" id="perfil_tactico" name="perfil_tactico">
        </div>
        <div class="field">
          <label for="jugadores_en_posicion">Jugadores actuales en la posici&oacute;n</label>
          <input type="number" id="jugadores_en_posicion" name="jugadores_en_posicion" min="0" max="10" value="0">
        </div>
        <div class="field">
          <label for="pct_minutos_proyectados">% minutos proyectados para el jugador</label>
          <input type="number" id="pct_minutos_proyectados" name="pct_minutos_proyectados" min="0" max="100" value="0">
        </div>
        <div class="field">
          <label for="horizonte_anios">Horizonte del proyecto (a&ntilde;os)</label>
          <input type="number" id="horizonte_anios" name="horizonte_anios" min="1" max="10" value="1">
        </div>
        <div class="field">
          <label for="modo_competitivo">Modo competitivo</label>
          <select id="modo_competitivo" name="modo_competitivo">
            <option value="resultados_inmediatos">Resultados Inmediatos</option>
            <option value="consolidacion">Consolidaci&oacute;n</option>
            <option value="desarrollo">Desarrollo</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Club Zones -->
    <div class="section">
      <h2>Zonas requeridas por el club (m&aacute;x. 5)</h2>
      <p style="color:#64748b;font-size:.8rem;margin-bottom:.75rem">Selecciona hasta 5 zonas donde el club necesita refuerzo.</p>
      <div class="zona-grid" id="zonaGridC"></div>
      <div class="zona-count" id="zonaCountC">0 de 5 seleccionadas</div>
    </div>

    <!-- SECTION 8: Tactical & Project Scores -->
    <div class="section">
      <h2>Scores t&aacute;cticos y de proyecto (1–10)</h2>
      <div class="grid-3">
        <div class="field">
          <label for="compat_tactica_ofensiva">Compatibilidad t&aacute;ctica ofensiva</label>
          <input type="range" id="compat_tactica_ofensiva" name="compat_tactica_ofensiva" min="1" max="10" step="0.5" value="5" oninput="this.nextElementSibling.textContent=this.value">
          <span style="color:#94a3b8;font-size:.9rem;font-weight:600">5</span>
        </div>
        <div class="field">
          <label for="compat_tactica_defensiva">Compatibilidad t&aacute;ctica defensiva</label>
          <input type="range" id="compat_tactica_defensiva" name="compat_tactica_defensiva" min="1" max="10" step="0.5" value="5" oninput="this.nextElementSibling.textContent=this.value">
          <span style="color:#94a3b8;font-size:.9rem;font-weight:600">5</span>
        </div>
        <div class="field">
          <label for="compat_tactica_transicion">Compatibilidad t&aacute;ctica transici&oacute;n</label>
          <input type="range" id="compat_tactica_transicion" name="compat_tactica_transicion" min="1" max="10" step="0.5" value="5" oninput="this.nextElementSibling.textContent=this.value">
          <span style="color:#94a3b8;font-size:.9rem;font-weight:600">5</span>
        </div>
        <div class="field">
          <label for="alineacion_edad_horizonte">Alineaci&oacute;n edad – horizonte</label>
          <input type="range" id="alineacion_edad_horizonte" name="alineacion_edad_horizonte" min="1" max="10" step="0.5" value="5" oninput="this.nextElementSibling.textContent=this.value">
          <span style="color:#94a3b8;font-size:.9rem;font-weight:600">5</span>
        </div>
        <div class="field">
          <label for="alineacion_perfil_modo">Alineaci&oacute;n perfil – modo</label>
          <input type="range" id="alineacion_perfil_modo" name="alineacion_perfil_modo" min="1" max="10" step="0.5" value="5" oninput="this.nextElementSibling.textContent=this.value">
          <span style="color:#94a3b8;font-size:.9rem;font-weight:600">5</span>
        </div>
        <div class="field">
          <label for="proyeccion_continuidad">Proyecci&oacute;n de continuidad</label>
          <input type="range" id="proyeccion_continuidad" name="proyeccion_continuidad" min="1" max="10" step="0.5" value="5" oninput="this.nextElementSibling.textContent=this.value">
          <span style="color:#94a3b8;font-size:.9rem;font-weight:600">5</span>
        </div>
      </div>
    </div>

    <div class="section">
      <h2>Datos Sofascore — Club destino (para umbrales autom&aacute;ticos)</h2>
      <p style="color:#64748b;font-size:.8rem;margin-bottom:.75rem">
        Si pegas los datos agregados del club destino en formato Sofascore,
        los umbrales estad&iacute;sticos se calcular&aacute;n autom&aacute;ticamente.
        Si est&aacute; vac&iacute;o, puedes definir los umbrales manualmente arriba.
      </p>
      <div class="field">
        <label for="stats_club_aggregadas_raw">Estad&iacute;sticas del club destino (Sofascore)</label>
        <textarea id="stats_club_aggregadas_raw" rows="8" style="width:100%;background:#0f172a;color:#e2e8f0;border:1px solid #334155;border-radius:8px;padding:.75rem;font-family:'SF Mono','Fira Code',monospace;font-size:.8rem;resize:vertical" placeholder="Ej: Matches 12&#10;Goals scored 7&#10;Goals conceded 11&#10;Balls recovered per game 92.3&#10;Interceptions per game 38.6&#10;..."></textarea>
      </div>
    </div>

    <!-- SECTION 10: Evaluation Profile -->
    <div class="section">
      <h2>Perfil de evaluaci&oacute;n</h2>
      <div class="field">
        <select id="perfil_evaluacion" name="perfil_evaluacion">
          <option value="rendimiento_inmediato">Rendimiento inmediato &mdash; El jugador debe aportar desde ya</option>
          <option value="potencial_mediano_plazo">Potencial mediano plazo &mdash; Apuesta a futuro</option>
          <option value="bajo_riesgo_fracaso">Bajo riesgo de fracaso &mdash; Prioridad en seguridad y adaptaci&oacute;n</option>
        </select>
      </div>
    </div>

    <div class="btn-wrap">
      <button type="button" class="btn" id="submitBtn" onclick="submitForm()">Evaluar Compatibilidad</button>
      <div class="loading" id="loading">
        <div class="spinner"></div>
        <span>Calculando compatibilidad...</span>
      </div>
    </div>
  </form>

  <!-- RESULTS -->
  <div class="results" id="results">
    <div class="result-header" id="resultHeader"></div>
    <div class="breach-card" id="breachCard"></div>
    <div class="cards-2">
      <div class="card"><h4>Compatibilidad por m&oacute;dulo</h4><canvas id="radarChart"></canvas></div>
      <div class="card"><h4>Scores por perfil de evaluaci&oacute;n</h4><canvas id="barChart"></canvas></div>
    </div>
    <table class="tabla" id="compatTable">
      <thead><tr><th>M&oacute;dulo</th><th style="text-align:center">J</th><th style="text-align:center">C</th><th style="text-align:center">Compat.</th><th></th></tr></thead>
      <tbody id="compatBody"></tbody>
    </table>
    <div class="profile-grid" id="profileGrid"></div>
    <div class="footer">MPSc v1.0 — Modelo Predictivo de Scouting</div>
  </div>
</div>

<script>
const ZONAS = {
  1:"Izq. ataque",2:"Centro ataque",3:"Der. ataque",
  4:"Med. alto izq.",5:"Med. alto centro",6:"Med. alto der.",
  7:"Med. bajo izq.",8:"Med. bajo centro",9:"Med. bajo der.",
  10:"Med. def. izq.",11:"Med. def. centro",12:"Med. def. der.",
  13:"Def. izq.",14:"Def. centro",15:"Def. der.",
  16:"&Aacute;rea prop. izq.",17:"&Aacute;rea prop. centro",18:"&Aacute;rea prop. der."
};

const METRICAS = {
  portero:[
    ["Salvadas totales","salvadas"],["Goles encajados","gc"],["Tiros al arco recibidos","tiros_rec"],
    ["Porter&iacute;as a cero","porterias_0"],["Salidas del &aacute;rea","salidas"],
    ["Pases completados","pases_comp"],["Pases intentados","pases_int"],
    ["Duelos a&eacute;reos ganados","da_ganados"],["Duelos a&eacute;reos disputados","da_disputados"]
  ],
  central:[
    ["Despejes totales","despejes"],["Intercepciones","intercepciones"],["Entradas","entradas"],
    ["Pases progresivos","pases_prog"],["Duelos a&eacute;reos ganados","da_ganados"],
    ["Duelos a&eacute;reos disputados","da_disputados"],["Duelos terrestres ganados","dt_ganados"],
    ["Duelos terrestres disputados","dt_disputados"],["Pases completados","pases_comp"],
    ["Pases intentados","pases_int"],["Pases largos completados","pases_l_comp"],
    ["Pases largos intentados","pases_l_int"]
  ],
  lateral:[
    ["Centros totales","centros"],["Centros completados","centros_comp"],
    ["Pases progresivos","pases_prog"],["Carreras progresivas","carreras_prog"],
    ["Intercepciones","intercepciones"],["Entradas","entradas"],
    ["Duelos ofensivos ganados","do_ganados"],["Duelos ofensivos disputados","do_disputados"],
    ["Duelos defensivos ganados","dd_ganados"],["Duelos defensivos disputados","dd_disputados"],
    ["Pases completados","pases_comp"],["Pases intentados","pases_int"]
  ],
  mediocampista_defensivo:[
    ["Intercepciones","intercepciones"],["Entradas","entradas"],["Presiones totales","presiones"],
    ["Presiones exitosas","presiones_ok"],["Pases progresivos","pases_prog"],
    ["Recuperaciones","recuperaciones"],["Duelos a&eacute;reos ganados","da_ganados"],
    ["Duelos a&eacute;reos disputados","da_disputados"],["Pases completados","pases_comp"],
    ["Pases intentados","pases_int"]
  ],
  mediocampista_central:[
    ["Pases progresivos","pases_prog"],["Pases clave","pases_clave"],
    ["Carreras progresivas","carreras_prog"],["Llegadas al &aacute;rea","llegadas_area"],
    ["Recuperaciones","recuperaciones"],["Tiros totales","tiros"],
    ["Pases completados","pases_comp"],["Pases intentados","pases_int"]
  ],
  extremo:[
    ["Tiros totales","tiros"],["Tiros a puerta","tiros_puerta"],
    ["Regates intentados","regates_int"],["Regates exitosos","regates_ok"],
    ["Pases clave","pases_clave"],["Centros totales","centros"],
    ["Centros completados","centros_comp"],["Carreras progresivas","carreras_prog"],
    ["Pases completados","pases_comp"],["Pases intentados","pases_int"]
  ],
  delantero_centro:[
    ["Goles totales","goles"],["Tiros totales","tiros"],["Tiros a puerta","tiros_puerta"],
    ["Toques en &aacute;rea rival","toques_area"],["Duelos a&eacute;reos ganados","da_ganados"],
    ["Duelos a&eacute;reos disputados","da_disputados"],["Faltas recibidas","faltas_rec"],
    ["Pases completados","pases_comp"],["Pases intentados","pases_int"]
  ]
};

const SOFASCORE_KEYWORDS = {
  goles:["goals","goles","gol"],
  asistencias:["assists","asistencias","asist"],
  salvadas:["saves","salvadas","salvó","save"],
  gc:["goals conceded","goles encajados","gc"],
  tiros_rec:["shots against","tiros al arco recibidos","shots on target against"],
  porterias_0:["clean sheets","porterias a cero","clean sheet"],
  tiros:["shots per game","tiros por partido","shots"],
  tiros_puerta:["shots on target per game","tiros a puerta"],
  pases_comp:["passes per game","pases por partido","passes completed","passes"],
  entradas:["tackles per game","entradas por partido","tackles"],
  intercepciones:["interceptions per game","interceptions"],
  faltas_rec:["fouls per game","faltas por partido","fouls suffered","fouls"],
  pases_clave:["key passes per game","key passes","pases clave"],
  centros:["crosses per game","centros por partido","crosses"],
  regates_int:["dribbles per game","regates por partido","dribbles attempted","dribbles"],
  despejes:["clearances per game","despejes por partido","clearances"],
  da_ganados:["aerial duels won per game","aerial duels won"],
  dt_ganados:["duels won per game","duels won"],
  recuperaciones:["recoveries per game","recuperaciones por partido","recoveries"],
  pases_prog:["progressive passes per game","progressive passes","pases progresivos"],
  carreras_prog:["progressive runs per game","progressive runs","carreras progresivas"],
  toques_area:["touches in box per game","toques en area","touches in box"],
  pases_pct:["pass accuracy","precision de pases","pass accuracy %"],
  da_pct:["aerial duels won %"],
  dt_pct:["duels won %"],
  regates_pct:["dribble success %","dribble success"],
  centros_pct:["cross accuracy %"],
  conversion_pct:["shot conversion %","conversion %"],
};

const MISSING_STAT_LABELS = {
  goles:"Goles totales",asistencias:"Asistencias totales",salvadas:"Salvadas totales",
  gc:"Goles encajados",tiros_rec:"Tiros al arco recibidos",porterias_0:"Porterías a cero",
  tiros:"Tiros totales",tiros_puerta:"Tiros a puerta totales",
  pases_comp:"Pases completados",entradas:"Entradas totales",
  intercepciones:"Intercepciones totales",faltas_rec:"Faltas recibidas totales",
  pases_clave:"Pases clave totales",centros:"Centros totales",
  regates_int:"Regates intentados",despejes:"Despejes totales",
  da_ganados:"Duelos aéreos ganados",dt_ganados:"Duelos terrestres ganados",
  recuperaciones:"Recuperaciones totales",pases_prog:"Pases progresivos totales",
  carreras_prog:"Carreras progresivas totales",toques_area:"Toques en área rival",
  pases_pct:"% de pases precisos",da_pct:"% duelos aéreos ganados",
  dt_pct:"% duelos terrestres ganados",regates_pct:"% regates exitosos",
  centros_pct:"% centros precisos",conversion_pct:"% conversión",
};

let selectedZonasJ = [];
let selectedZonasC = [];
let radarChartInstance = null;
let barChartInstance = null;

function calcEdad(){
  var d=document.getElementById("fecha_nacimiento").value;
  if(!d){document.getElementById("edad").value="";return}
  var b=new Date(d),t=new Date(),e=t.getFullYear()-b.getFullYear();
  var m=t.getMonth()-b.getMonth();
  if(m<0||(m===0&&t.getDate()<b.getDate()))e--;
  document.getElementById("edad").value=e>=0?e:0
}

function toggleClausula(){
  var c=document.getElementById("tiene_clausula").checked;
  document.getElementById("clausula_field").style.display=c?"block":"none"
}

function buildZonaGrid(containerId,countId,selectedArr,maxZonas){
  var c=document.getElementById(containerId);c.innerHTML="";
  for(var i=1;i<=18;i++){
    var d=document.createElement("div");d.className="zona-cell";d.dataset.z=i;
    d.innerHTML='<div class="z-num">'+i+'</div><div class="z-desc">'+ZONAS[i]+'</div>';
    d.onclick=function(){
      var z=parseInt(this.dataset.z),idx=selectedArr.indexOf(z);
      if(idx>-1){selectedArr.splice(idx,1);this.classList.remove("selected")}
      else if(selectedArr.length<maxZonas){selectedArr.push(z);this.classList.add("selected")}
      document.getElementById(countId).textContent=selectedArr.length+" de "+maxZonas+" seleccionadas"
    };
    c.appendChild(d)
  }
}

function onPosicionChange(){
  analizarSofascoreJugador()
}

function _buscarEnSofascore(texto, keywords){
  var t=texto.toLowerCase();
  for(var i=0;i<keywords.length;i++){
    if(t.indexOf(keywords[i].toLowerCase())>-1)return true
  }
  return false
}

function analizarSofascoreJugador(){
  var pos=document.getElementById("posicion").value;
  var section=document.getElementById("statsMissingSection");
  var container=document.getElementById("statsFaltantesContainer");
  container.innerHTML="";
  if(!pos||!METRICAS[pos]){section.style.display="none";return}
  var texto=document.getElementById("sofascore_jugador_raw").value;
  if(!texto.trim()){section.style.display="none";return}
  var encontradas=0;
  var html="";
  METRICAS[pos].forEach(function(m){
    var statKey=m[1];
    var found=false;
    if(SOFASCORE_KEYWORDS[statKey]){
      if(_buscarEnSofascore(texto,SOFASCORE_KEYWORDS[statKey])){
        found=true;
        encontradas++
      }
    }
    if(!found){
      var lbl=MISSING_STAT_LABELS[statKey]||m[0];
      html+='<div class="field"><label>'+lbl+'</label><input type="number" name="estadistica_'+statKey+'" data-stat="'+statKey+'" min="0" value="0" step="any"></div>'
    }
  });
  if(html){
    container.innerHTML=html;
    section.style.display="block"
  }else{
    section.style.display="none"
  }
}

function getFormData(){
  var d={};
  d.nombre=document.getElementById("nombre").value;
  d.fecha_nacimiento=document.getElementById("fecha_nacimiento").value;
  d.edad=parseInt(document.getElementById("edad").value)||0;
  d.pais_origen=document.getElementById("pais_origen").value;
  d.ciudad_actual=document.getElementById("ciudad_actual").value;
  d.idioma=document.getElementById("idioma").value;
  d.experiencia_extranjero=document.getElementById("experiencia_extranjero").checked;
  d.valor_mercado=document.getElementById("valor_mercado").value;
  d.meses_contrato=parseInt(document.getElementById("meses_contrato").value)||0;
  d.tiene_clausula=document.getElementById("tiene_clausula").checked;
  d.clausula_nivel=document.getElementById("clausula_nivel").value;
  d.club_actual=document.getElementById("club_actual").value;
  d.liga_j=document.getElementById("liga_j").value;
  d.posicion_tabla_j=parseInt(document.getElementById("posicion_tabla_j").value)||1;
  d.total_equipos_liga_j=parseInt(document.getElementById("total_equipos_liga_j").value)||18;
  d.tiene_copa_j=document.getElementById("tiene_copa_j").checked;
  d.tiene_internacional_j=document.getElementById("tiene_internacional_j").checked;
  d.sistema_tactico_club=document.getElementById("sistema_tactico_club").value;
  d.estilo_ofensivo_j=document.getElementById("estilo_ofensivo_j").value;
  d.estilo_defensivo_j=document.getElementById("estilo_defensivo_j").value;
  d.estilo_transicion_j=document.getElementById("estilo_transicion_j").value;
  d.altitud_ciudad_j=parseFloat(document.getElementById("altitud_ciudad_j").value)||0;
  d.minutos_jugados=parseFloat(document.getElementById("minutos_jugados").value)||0;
  d.minutos_posibles=parseFloat(document.getElementById("minutos_posibles").value)||0;
  d.posicion=document.getElementById("posicion").value;
  d.rol=document.getElementById("rol").value;
  d.num_lesiones=parseInt(document.getElementById("num_lesiones").value)||0;
  d.tipo_lesion=document.getElementById("tipo_lesion").value;
  d.semanas_baja_promedio=parseFloat(document.getElementById("semanas_baja_promedio").value)||0;
  d.zonas=selectedZonasJ.slice();

  d.estadisticas_override={};
  document.querySelectorAll("#statsFaltantesContainer input[data-stat]").forEach(function(el){
    d.estadisticas_override[el.dataset.stat]=parseFloat(el.value)||0
  });

  d.sofascore_jugador_raw=document.getElementById("sofascore_jugador_raw").value;

  d.club_nombre=document.getElementById("club_nombre").value;
  d.club_ciudad=document.getElementById("club_ciudad").value;
  d.club_pais=document.getElementById("club_pais").value;
  d.club_idioma=document.getElementById("club_idioma").value;
  d.club_altitud=parseFloat(document.getElementById("club_altitud").value)||0;
  d.club_liga=document.getElementById("club_liga").value;
  d.club_posicion_tabla=parseInt(document.getElementById("club_posicion_tabla").value)||1;
  d.club_total_equipos=parseInt(document.getElementById("club_total_equipos").value)||18;
  d.victorias_recientes=parseInt(document.getElementById("victorias_recientes").value)||0;
  d.empates_recientes=parseInt(document.getElementById("empates_recientes").value)||0;
  d.derrotas_recientes=parseInt(document.getElementById("derrotas_recientes").value)||0;
  d.club_tiene_copa=document.getElementById("club_tiene_copa").checked;
  d.club_tiene_internacional=document.getElementById("club_tiene_internacional").checked;
  d.club_sistema_tactico=document.getElementById("club_sistema_tactico").value;
  d.club_estilo_ofensivo=document.getElementById("club_estilo_ofensivo").value;
  d.club_estilo_defensivo=document.getElementById("club_estilo_defensivo").value;
  d.club_estilo_transicion=document.getElementById("club_estilo_transicion").value;
  d.posicion_requerida=document.getElementById("posicion_requerida").value;
  d.perfil_tactico=document.getElementById("perfil_tactico").value;
  d.zonas_requeridas=selectedZonasC.slice();
  d.jugadores_en_posicion=parseInt(document.getElementById("jugadores_en_posicion").value)||0;
  d.pct_minutos_proyectados=parseFloat(document.getElementById("pct_minutos_proyectados").value)||0;
  d.horizonte_anios=parseInt(document.getElementById("horizonte_anios").value)||1;
  d.modo_competitivo=document.getElementById("modo_competitivo").value;
  d.compat_tactica_ofensiva=parseFloat(document.getElementById("compat_tactica_ofensiva").value)||5;
  d.compat_tactica_defensiva=parseFloat(document.getElementById("compat_tactica_defensiva").value)||5;
  d.compat_tactica_transicion=parseFloat(document.getElementById("compat_tactica_transicion").value)||5;
  d.alineacion_edad_horizonte=parseFloat(document.getElementById("alineacion_edad_horizonte").value)||5;
  d.alineacion_perfil_modo=parseFloat(document.getElementById("alineacion_perfil_modo").value)||5;
  d.proyeccion_continuidad=parseFloat(document.getElementById("proyeccion_continuidad").value)||5;
  d.perfil_evaluacion=document.getElementById("perfil_evaluacion").value;
  d.stats_club_origen_raw=document.getElementById("stats_club_origen_raw").value;
  d.stats_club_aggregadas_raw=document.getElementById("stats_club_aggregadas_raw").value;

  return d
}

function submitForm(){
  var btn=document.getElementById("submitBtn");
  var loading=document.getElementById("loading");
  var error=document.getElementById("errorMsg");
  error.classList.remove("active");error.textContent="";
  btn.disabled=true;loading.classList.add("active");

  var data=getFormData();

  if(!data.nombre){showError("El nombre del jugador es obligatorio.");btn.disabled=false;loading.classList.remove("active");return}
  if(!data.posicion){showError("Selecciona una posici&oacute;n para el jugador.");btn.disabled=false;loading.classList.remove("active");return}
  if(!data.posicion_requerida){showError("Selecciona una posici&oacute;n requerida para el club.");btn.disabled=false;loading.classList.remove("active");return}

  fetch("/calcular",{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify(data)
  })
  .then(function(r){return r.json()})
  .then(function(resp){
    btn.disabled=false;loading.classList.remove("active");
    if(resp.success){showResults(resp.result)}
    else{showError(resp.error||"Error en el servidor")}
  })
  .catch(function(err){
    btn.disabled=false;loading.classList.remove("active");
    showError("Error de conexi&oacute;n: "+err.message)
  })
}

function showError(msg){
  var e=document.getElementById("errorMsg");
  e.innerHTML=msg;e.classList.add("active")
}

function showResults(r){
  var results=document.getElementById("results");
  results.classList.add("active");
  results.scrollIntoView({behavior:"smooth",block:"start"});

  var score=r.score_final,color="#22c55e";
  if(score<40)color="#ef4444";else if(score<55)color="#f97316";else if(score<70)color="#f59e0b";else if(score<85)color="#84cc16";

  document.getElementById("resultHeader").innerHTML=
    '<h3>MPSc — Resultado de compatibilidad</h3>'+
    '<div class="score-row"><div class="score-ring"><div class="number" style="color:'+color+'">'+score.toFixed(1)+'%</div>'+
    '<div><div class="label" style="color:'+color+'">'+r.interpretacion+'</div>'+
    '<div style="font-size:.85rem;color:#94a3b8;margin-top:.25rem">'+
    r.perfil_evaluacion.replace(/_/g," ").replace(/\b\w/g,function(l){return l.toUpperCase()})+'</div></div></div></div>'+
    '<div class="info-grid"><div class="info-item"><div class="info-label">Jugador</div><div class="info-value">'+r.nombre_jugador+'</div></div>'+
    '<div class="info-item"><div class="info-label">Club destino</div><div class="info-value">'+r.nombre_club+'</div></div>'+
    '<div class="info-item"><div class="info-label">Valor de mercado</div><div class="info-value">'+(r.valor_mercado||"—")+'</div></div></div>';

  var niveles={1:"1 — Baja",2:"2 — Media",3:"3 — Alta"};
  var pText=r.penalizacion_aplicada>0?(r.penalizacion_aplicada*100).toFixed(0)+"%":"Sin penalizaci&oacute;n";
  var pColor=r.penalizacion_aplicada>0?"#ef4444":"#22c55e";
  var confianza=r.confiabilidad_estadisticas||1;
  var confColor=confianza>=0.9?"#22c55e":confianza>=0.7?"#f59e0b":"#ef4444";
  var factorTxt=r.factor_contexto_global!==undefined?(r.factor_contexto_global!==1?'Factor: '+r.factor_contexto_global.toFixed(3):'Sin ajuste'):'';
  document.getElementById("breachCard").innerHTML=
    '<div class="breach-item"><div class="lbl">Nivel de brecha</div><div class="val">'+(niveles[r.nivel_brecha]||r.nivel_brecha)+'</div></div>'+
    '<div class="breach-item"><div class="lbl">&Delta; coef</div><div class="val">'+r.delta_coef.toFixed(2)+'</div></div>'+
    '<div class="breach-item"><div class="lbl">Penalizaci&oacute;n aplicada</div><div class="val" style="color:'+pColor+'">'+pText+'</div></div>'+
    '<div class="breach-item"><div class="lbl">Confiabilidad estad&iacute;sticas</div><div class="val" style="color:'+confColor+'">'+(confianza*100).toFixed(0)+'%</div></div>';

  var modulos=[
    ["entorno_competitivo","Entorno competitivo"],
    ["perfil_jugador","Perfil del jugador"],
    ["estadisticas","Estad&iacute;sticas"],
    ["fisico_salud","F&iacute;sico y salud"],
    ["adaptacion","Adaptaci&oacute;n"],
    ["zonas_presencia","Zonas de presencia"],
    ["modelo_juego","Modelo de juego"],
    ["viabilidad","Viabilidad contractual"]
  ];

  var radarLabels=[],radarValues=[];
  var compatRows="";
  modulos.forEach(function(m){
    var k=m[0],lab=m[1];
    var compat=r.compatibilidades[k]||0;
    var compatPct=compat*100;
    var sj=r.scores_jugador[k]||0;
    var sc=r.scores_club[k]||0;
    radarLabels.push(lab);
    radarValues.push(compatPct);
    compatRows+='<tr><td>'+lab+'</td><td class="num">'+(typeof sj==="number"?sj.toFixed(1):sj)+'</td><td class="num">'+(typeof sc==="number"?sc.toFixed(1):sc)+'</td><td class="num">'+compatPct.toFixed(1)+'%</td><td><div class="bar-vis"><div class="bar-fill" style="width:'+compatPct+'%"></div><div class="bar-bg"></div></div></td></tr>'
  });
  document.getElementById("compatBody").innerHTML=compatRows;

  if(radarChartInstance)radarChartInstance.destroy();
  radarChartInstance=new Chart(document.getElementById("radarChart"),{
    type:"radar",
    data:{labels:radarLabels,datasets:[{label:"Compatibilidad",data:radarValues,backgroundColor:"rgba(59, 130, 246, 0.15)",borderColor:"rgba(59, 130, 246, 0.8)",borderWidth:2,pointBackgroundColor:"rgba(59, 130, 246, 0.8)",pointRadius:4}]},
    options:{responsive:true,maintainAspectRatio:true,scales:{r:{beginAtZero:true,max:100,ticks:{stepSize:20,color:"#64748b",backdropColor:"transparent",font:{size:10}},grid:{color:"rgba(148, 163, 184, 0.15)"},angleLines:{color:"rgba(148, 163, 184, 0.15)"},pointLabels:{color:"#cbd5e1",font:{size:11}}}},plugins:{legend:{display:false}}}
  });

  var perfiles=[
    ["Rendimiento inmediato",r.score_rendimiento_inmediato,"rendimiento_inmediato"],
    ["Potencial mediano plazo",r.score_potencial_mediano,"potencial_mediano_plazo"],
    ["Bajo riesgo de fracaso",r.score_bajo_riesgo,"bajo_riesgo_fracaso"]
  ];
  var barLabels=[],barValues=[],barColors=[];
  perfiles.forEach(function(p){
    barLabels.push(p[0]);barValues.push(p[1]);
    barColors.push(p[2]===r.perfil_evaluacion?"rgba(59, 130, 246, 0.85)":"rgba(148, 163, 184, 0.5)")
  });
  if(barChartInstance)barChartInstance.destroy();
  barChartInstance=new Chart(document.getElementById("barChart"),{
    type:"bar",
    data:{labels:barLabels,datasets:[{label:"Score",data:barValues,backgroundColor:barColors,borderRadius:6,barPercentage:0.6}]},
    options:{responsive:true,maintainAspectRatio:true,indexAxis:"y",scales:{x:{beginAtZero:true,max:110,ticks:{color:"#64748b",font:{size:10}},grid:{color:"rgba(148, 163, 184, 0.1)"}},y:{ticks:{color:"#cbd5e1",font:{size:11}},grid:{display:false}}},plugins:{legend:{display:false}}}
  });

  var pg=document.getElementById("profileGrid");pg.innerHTML="";
  perfiles.forEach(function(p){
    var s=p[1],c="#22c55e";if(s<40)c="#ef4444";else if(s<55)c="#f97316";else if(s<70)c="#f59e0b";else if(s<85)c="#84cc16";
    var ac=p[2]===r.perfil_evaluacion?'<div class="pactive">&larr; ACTIVO</div>':"";
    var cls=p[2]===r.perfil_evaluacion?"profile-card active":"profile-card";
    pg.innerHTML+='<div class="'+cls+'"><div class="pname">'+p[0]+'</div><div class="pscore" style="color:'+c+'">'+s.toFixed(1)+'%</div>'+ac+'</div>'
  })
}

buildZonaGrid("zonaGridJ","zonaCountJ",selectedZonasJ,5);
buildZonaGrid("zonaGridC","zonaCountC",selectedZonasC,5);
</script>
</body>
</html>"""


class MPScHandler(http.server.BaseHTTPRequestHandler):

    calculadora = Calculadora()

    def _build_jugador(self, data: dict) -> Jugador:
        # Parsear estadísticas desde Sofascore (fuente primaria)
        sofascore_texto = data.get("sofascore_jugador_raw", "")
        stats_parseadas = extraer_estadisticas_jugador(sofascore_texto)
        # Merge con override manual (gana el override)
        override = data.get("estadisticas_override", {})
        stats_finales = dict(stats_parseadas)
        for k, v in override.items():
            if v and v > 0:
                stats_finales[k] = v
        return Jugador(
            nombre=data.get("nombre", ""),
            fecha_nacimiento=data.get("fecha_nacimiento", ""),
            edad=int(data.get("edad", 0)),
            pais_origen=data.get("pais_origen", ""),
            ciudad_actual=data.get("ciudad_actual", ""),
            idioma=data.get("idioma", ""),
            experiencia_extranjero=bool(data.get("experiencia_extranjero", False)),
            valor_mercado=data.get("valor_mercado", ""),
            meses_contrato=int(data.get("meses_contrato", 0)),
            tiene_clausula=bool(data.get("tiene_clausula", False)),
            clausula_nivel=data.get("clausula_nivel", ""),
            club_actual=data.get("club_actual", ""),
            liga=data.get("liga_j", ""),
            posicion_tabla=int(data.get("posicion_tabla_j", 1)),
            total_equipos_liga=int(data.get("total_equipos_liga_j", 18)),
            tiene_copa=bool(data.get("tiene_copa_j", False)),
            tiene_internacional=bool(data.get("tiene_internacional_j", False)),
            sistema_tactico_club=data.get("sistema_tactico_club", ""),
            estilo_ofensivo=data.get("estilo_ofensivo_j", ""),
            estilo_defensivo=data.get("estilo_defensivo_j", ""),
            estilo_transicion=data.get("estilo_transicion_j", ""),
            altitud_ciudad=float(data.get("altitud_ciudad_j", 0)),
            minutos_jugados=float(data.get("minutos_jugados", 0)),
            minutos_posibles=float(data.get("minutos_posibles", 0)),
            posicion=data.get("posicion", ""),
            rol=data.get("rol", ""),
            estadisticas=stats_finales,
            num_lesiones=int(data.get("num_lesiones", 0)),
            tipo_lesion=data.get("tipo_lesion", "ninguna"),
            semanas_baja_promedio=float(data.get("semanas_baja_promedio", 0)),
            zonas=data.get("zonas", []),
            sofascore_jugador_raw=sofascore_texto,
            stats_club_origen_raw=data.get("stats_club_origen_raw", ""),
        )

    def _build_club(self, data: dict) -> Club:
        return Club(
            nombre=data.get("club_nombre", ""),
            ciudad=data.get("club_ciudad", ""),
            pais=data.get("club_pais", ""),
            idioma=data.get("club_idioma", ""),
            altitud=float(data.get("club_altitud", 0)),
            liga=data.get("club_liga", ""),
            posicion_tabla=int(data.get("club_posicion_tabla", 1)),
            total_equipos_liga=int(data.get("club_total_equipos", 18)),
            victorias_recientes=int(data.get("victorias_recientes", 0)),
            empates_recientes=int(data.get("empates_recientes", 0)),
            derrotas_recientes=int(data.get("derrotas_recientes", 0)),
            tiene_copa=bool(data.get("club_tiene_copa", False)),
            tiene_internacional=bool(data.get("club_tiene_internacional", False)),
            sistema_tactico=data.get("club_sistema_tactico", ""),
            estilo_ofensivo=data.get("club_estilo_ofensivo", ""),
            estilo_defensivo=data.get("club_estilo_defensivo", ""),
            estilo_transicion=data.get("club_estilo_transicion", ""),
            posicion_requerida=data.get("posicion_requerida", ""),
            perfil_tactico=data.get("perfil_tactico", ""),
            zonas_requeridas=data.get("zonas_requeridas", []),
            jugadores_en_posicion=int(data.get("jugadores_en_posicion", 0)),
            pct_minutos_proyectados=float(data.get("pct_minutos_proyectados", 0)),
            horizonte_anios=int(data.get("horizonte_anios", 1)),
            modo_competitivo=data.get("modo_competitivo", "resultados_inmediatos"),
            compat_tactica_ofensiva=float(data.get("compat_tactica_ofensiva", 5)),
            compat_tactica_defensiva=float(data.get("compat_tactica_defensiva", 5)),
            compat_tactica_transicion=float(data.get("compat_tactica_transicion", 5)),
            alineacion_edad_horizonte=float(data.get("alineacion_edad_horizonte", 5)),
            alineacion_perfil_modo=float(data.get("alineacion_perfil_modo", 5)),
            proyeccion_continuidad=float(data.get("proyeccion_continuidad", 5)),
            stats_aggregadas_raw=data.get("stats_club_aggregadas_raw", ""),
        )

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(_HTML.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/calcular":
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length).decode("utf-8")
                data = json.loads(body)

                jugador = self._build_jugador(data)
                club = self._build_club(data)
                perfil = data.get("perfil_evaluacion", "rendimiento_inmediato")

                resultado = self.calculadora.calcular(jugador, club, perfil)

                response = {
                    "success": True,
                    "result": {
                        "nombre_jugador": resultado.nombre_jugador,
                        "nombre_club": resultado.nombre_club,
                        "valor_mercado": resultado.valor_mercado,
                        "perfil_evaluacion": resultado.perfil_evaluacion,
                        "nivel_brecha": resultado.nivel_brecha,
                        "delta_coef": resultado.delta_coef,
                        "penalizacion_aplicada": resultado.penalizacion_aplicada,
                        "score_final": resultado.score_final,
                        "score_rendimiento_inmediato": resultado.score_rendimiento_inmediato,
                        "score_potencial_mediano": resultado.score_potencial_mediano,
                        "score_bajo_riesgo": resultado.score_bajo_riesgo,
                        "interpretacion": resultado.interpretacion(),
                        "compatibilidades": resultado.compatibilidades,
                        "scores_jugador": resultado.scores_jugador,
                        "scores_club": resultado.scores_club,
                        "factor_contexto_global": resultado.factor_contexto_global,
                        "confiabilidad_estadisticas": resultado.confiabilidad_estadisticas,
                    },
                }
            except Exception as e:
                response = {
                    "success": False,
                    "error": str(e),
                }

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


if __name__ == "__main__":
    server = http.server.HTTPServer(("0.0.0.0", 8765), MPScHandler)
    print("MPSc Web App running on http://localhost:8765")
    server.serve_forever()
