"""
MPSc — modules/adaptacion.py
Módulo: Adaptación cultural, climática e idiomática
"""


class ModuloAdaptacion:

    def score_idioma(self, idioma_jugador: str, idioma_club: str,
                     experiencia_extranjero: bool) -> float:
        ij = idioma_jugador.lower().strip()
        ic = idioma_club.lower().strip()

        if ij == ic:
            return 10.0

        idiomas_cercanos = {
            frozenset(["español", "portugués"]),
            frozenset(["español", "portugues"]),
            frozenset(["inglés", "ingles"]),
        }
        par = frozenset([ij, ic])
        if par in idiomas_cercanos:
            return 7.0

        return 4.0 if experiencia_extranjero else 1.0

    def score_cultura(self, pais_jugador: str, pais_club: str) -> float:
        pj = pais_jugador.lower().strip()
        pc = pais_club.lower().strip()

        if pj == pc:
            return 10.0

        latinoamerica = {
            "mexico", "méxico", "colombia", "argentina", "chile",
            "peru", "perú", "venezuela", "ecuador", "bolivia",
            "paraguay", "uruguay", "costa rica", "honduras",
            "guatemala", "el salvador", "panama", "panamá",
            "nicaragua", "cuba", "republica dominicana",
            "república dominicana", "brasil", "brazil",
        }
        if pj in latinoamerica and pc in latinoamerica:
            return 7.0

        occidental = {
            "españa", "espana", "estados unidos", "canada", "canadá",
            "francia", "alemania", "italia", "portugal", "holanda",
            "bélgica", "belgica", "suiza",
        }
        if (pj in latinoamerica | occidental) and (pc in latinoamerica | occidental):
            return 4.0

        return 1.0

    def score_clima(self, ciudad_origen: str, ciudad_destino: str,
                    altitud_origen: float, altitud_destino: float) -> float:
        """
        Aproximación por diferencia de altitud como proxy climático.
        Para mayor precisión se puede ampliar con datos de temperatura/humedad.
        """
        diff_alt = abs(altitud_destino - altitud_origen)

        if diff_alt < 300:    return 10.0
        if diff_alt < 800:    return 8.0
        if diff_alt < 1500:   return 6.0
        if diff_alt < 2500:   return 4.0
        return 1.0

    def calcular(self, idioma_jugador: str, idioma_club: str,
                 experiencia_extranjero: bool, pais_jugador: str,
                 pais_club: str, ciudad_origen: str, ciudad_destino: str,
                 altitud_origen: float, altitud_destino: float) -> float:

        s_idioma  = self.score_idioma(idioma_jugador, idioma_club, experiencia_extranjero)
        s_cultura = self.score_cultura(pais_jugador, pais_club)
        s_clima   = self.score_clima(ciudad_origen, ciudad_destino, altitud_origen, altitud_destino)

        score = (s_idioma * 0.40) + (s_cultura * 0.35) + (s_clima * 0.25)
        return round(score, 2)
