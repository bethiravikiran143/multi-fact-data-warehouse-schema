@echo off
title Student Performance Multi-Fact Data Warehouse & Analytics
echo.
echo [1/2] Verifying Warehouse Database...
if not exist "data\warehouse\academic_dw.db" (
    echo Database not found. Initializing ETL pipeline...
    python src\generate_raw_data.py
    python src\etl_pipeline.py
)
echo.
echo [2/2] Launching Streamlit Academic Analytics Dashboard...
echo Open your browser at http://localhost:8501
echo.
python -m streamlit run app.py
pause
