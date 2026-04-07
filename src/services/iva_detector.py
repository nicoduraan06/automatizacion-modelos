from __future__ import annotations

import re


class IVADetector:

    def detect_devengado(self, excel_data) -> list[dict]:
        results = []

        for sheet, cells in excel_data.cell_index.items():

            # Convertimos a lista ordenada
            ordered_cells = sorted(cells.items(), key=lambda x: (int(x[0][1:]), x[0][0]))

            for coord, cell in ordered_cells:
                value = cell.get("value")

                # 🔍 Detectar encabezado del bloque
                if isinstance(value, str) and "devengado" in value.lower():

                    # Buscar filas debajo
                    block_rows = self._extract_block_rows(cells, coord)

                    for row in block_rows:
                        parsed = self._parse_row(cells, row)
                        if parsed:
                            results.append(parsed)

        return results

    # =========================================================

    def _extract_block_rows(self, cells, start_coord):
        start_row = int(start_coord[1:])
        rows = []

        for i in range(start_row + 1, start_row + 20):
            rows.append(i)

        return rows

    # =========================================================

    def _parse_row(self, cells, row):
        row_cells = {coord: data for coord, data in cells.items() if int(coord[1:]) == row}

        values = []
        for coord, data in sorted(row_cells.items()):
            v = data.get("value")
            if v not in (None, ""):
                values.append(v)

        if len(values) < 2:
            return None

        tipo = self._extract_percentage(values)
        base = self._extract_number(values)
        cuota = self._extract_last_number(values)

        if tipo and base:
            return {
                "tipo": tipo,
                "base": base,
                "cuota": cuota
            }

        return None

    # =========================================================

    def _extract_percentage(self, values):
        for v in values:
            if isinstance(v, str) and "%" in v:
                try:
                    return float(v.replace("%", "").replace(",", "."))
                except:
                    return None
        return None

    def _extract_number(self, values):
        for v in values:
            if isinstance(v, (int, float)):
                return float(v)
        return None

    def _extract_last_number(self, values):
        for v in reversed(values):
            if isinstance(v, (int, float)):
                return float(v)
        return None