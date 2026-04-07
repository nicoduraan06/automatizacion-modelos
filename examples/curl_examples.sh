#!/usr/bin/env bash

curl -X POST http://localhost:3000/api/upload \
  -F "excel_file=@./ejemplo_zifra.xlsx" \
  -F "pdf_files=@./modelo303_q1.pdf"

curl -X POST http://localhost:3000/api/process \
  -H "Content-Type: application/json" \
  -d '{"process_id":"REEMPLAZAR"}'

curl "http://localhost:3000/api/result?process_id=REEMPLAZAR"

curl -L "http://localhost:3000/api/download?process_id=REEMPLAZAR&kind=excel" -o resultado.xlsx
