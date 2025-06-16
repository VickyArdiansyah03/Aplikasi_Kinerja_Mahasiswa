import streamlit as st

def get_role_specific_features():
    """Mendapatkan fitur berdasarkan role"""
    role = st.session_state["user_role"]
    
    if role == "Mahasiswa":
        return {
            "show_advanced_analysis": False,
            "show_admin_features": False,
            "show_batch_upload": False,
            "prediction_limit": 3,
            "title_suffix": "- Mode Mahasiswa",
            "show_excel_management": False
        }
    elif role == "Dosen":
        return {
            "show_advanced_analysis": True,
            "show_admin_features": False,
            "show_batch_upload": True,
            "prediction_limit": 10,
            "title_suffix": "- Mode Dosen",
            "show_excel_management": False
        }
    elif role == "Prodi":
        return {
            "show_advanced_analysis": False,
            "show_admin_features": False,
            "show_batch_upload": False,
            "prediction_limit": False,
            "title_suffix": "- Mode Prodi",
            "show_excel_management": False,
            "can_input_cpl_cpmk": True
        }
    else:  # Admin
        return {
            "show_advanced_analysis": True,
            "show_admin_features": True,
            "show_batch_upload": True,
            "prediction_limit": None,
            "title_suffix": "- Mode Admin",
            "show_excel_management": True
        }
