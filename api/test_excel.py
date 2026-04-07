from fastapi import FastAPI, HTTPException
import os

from src.parsers.excel_parser import ExcelParser

app = FastAPI(title="test-excel")


@app.get("/")
def test_excel(process_id: str):
    try:
        base_path = f"tmp/{process_id}/input"

        # Buscar Excel dentro del proceso
        files = os.listdir(base_path)
        excel_file = next(f for f in files if f.endswith((".xlsx", ".xlsm", ".xls")))

        excel_path = os.path.join(base_path, excel_file)

        parser = ExcelParser(excel_path)

        return {
            "sheets": parser.get_sheets(),
            "sample_cells": parser.extract_cells()[:50]  # solo primeras 50
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))