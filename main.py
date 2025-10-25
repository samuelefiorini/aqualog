"""
Aqualog - Sistema di Gestione Società di Apnea

Punto di ingresso principale dell'applicazione Streamlit.
"""

import streamlit as st
from app.utils.auth import get_auth_manager

# Configure page
st.set_page_config(
    page_title="Aqualog - Gestione Apnea",
    page_icon="🏊‍♂️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    """Main application function."""

    # Get authentication manager
    auth_manager = get_auth_manager()

    # Check authentication
    if not auth_manager.require_authentication():
        # Authentication form is shown, stop execution
        return

    # User is authenticated, show main content
    st.title("🏊‍♂️ Aqualog - Sistema di Gestione Apnea")

    # Get current user
    user = auth_manager.get_current_user()

    # Welcome message
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.success(f"Benvenuto, **{user.display_name}**!")
        if user.is_admin:
            st.info("👑 Amministratore - Accesso completo")
        else:
            st.info("👤 Utente - Accesso in sola lettura")

    with col3:
        if st.button("🚪 Esci", type="secondary"):
            auth_manager.logout()
            st.rerun()

    # Main content
    st.markdown("---")

    # Dashboard content
    st.subheader("📊 Pannello di Controllo")

    # Get database stats
    try:
        from db import get_database_stats

        stats = get_database_stats()

        # Display KPIs
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("👥 Membri", stats.total_members)

        with col2:
            st.metric("🏊 Test Cooper", stats.total_cooper_tests)

        with col3:
            st.metric("🏊‍♂️ Prove Indoor", stats.total_indoor_trials)

        with col4:
            st.metric("💾 Dimensione DB", f"{stats.database_size_mb:.1f} MB")

    except Exception as e:
        st.error(f"Errore nel caricamento dei dati del pannello: {e}")

    # Navigation info
    st.markdown("---")
    st.subheader("🧭 Navigazione")

    if user.is_admin:
        st.markdown("""
        **Pagine Disponibili:**
        - 📊 **Pannello di Controllo** - Panoramica del sistema e statistiche
        - 👥 **Membri** - Registro e gestione membri
        - 🏊 **Test Cooper** - Risultati dei test e analisi
        - 🏊‍♂️ **Prove Indoor** - Dati di allenamento e tendenze
        - ⚙️ **Pannello Admin** - Gestione utenti e sistema
        """)
    else:
        st.markdown("""
        **Pagine Disponibili:**
        - 📊 **Pannello di Controllo** - Panoramica del sistema e statistiche
        - 👥 **Membri** - Registro membri (sola lettura)
        - 🏊 **Test Cooper** - Risultati dei test e analisi
        - 🏊‍♂️ **Prove Indoor** - Dati di allenamento e tendenze
        """)

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "Aqualog - Sistema di Gestione Società di Apnea | "
        f"Connesso come {user.username} ({user.role})"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
