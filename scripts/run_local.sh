#!/usr/bin/env bash
set -e
python scripts/generate_data.py
streamlit run app/Home.py
