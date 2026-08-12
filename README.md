# Bluestock MF Capstone

A focused mutual fund analytics project for Indian large-cap schemes. This repository contains only the `mf_analysis` project and its final deliverables.

## Deliverables

- `mf_analysis/Final_Report.pdf`
- `mf_analysis/Bluestock_MF_Presentation.pptx`
- `mf_analysis/run_pipeline.py`

## Setup

```powershell
cd "c:\Users\jaswa\Downloads\ML project\mf_analysis"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install python-pptx reportlab pillow
```

## Run the full workflow

```powershell
cd mf_analysis
python run_pipeline.py --list
python run_pipeline.py --run ALL
```

## Run individual steps

```powershell
python run_pipeline.py --run generate_datasets
python run_pipeline.py --run data_cleaning
python run_pipeline.py --run db_load
python run_pipeline.py --run eda
python run_pipeline.py --run build_report
python run_pipeline.py --run build_presentation
```

## Notes

- The final report is generated as `mf_analysis/Final_Report.pdf`.
- The final presentation is generated as `mf_analysis/Bluestock_MF_Presentation.pptx`.
- The repository is intentionally limited to the core `mf_analysis` project.
