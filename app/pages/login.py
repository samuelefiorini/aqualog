"""
Login page for Aqualog application.
Handles user authentication and redirects to main application.
"""

import streamlit as st
from app.utils.auth import get_auth_manager


def main():
    """Main login page function."""
    # Configure page
    st.set_page_config(
        page_title="Aqualog - Accesso",
        page_icon="🏊‍♂️",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    # Get authentication manager
    auth_manager = get_auth_manager()

    # If already authenticated, show status
    if auth_manager.is_authenticated():
        st.success(f"✅ Già connesso come **{auth_manager.get_current_user()}**")
        st.info(
            "🏠 Naviga alle pagine principali dell'applicazione usando la barra laterale o la navigazione."
        )

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🚪 Esci", type="secondary", use_container_width=True):
                auth_manager.logout()
                st.rerun()

        # Show available pages
        st.markdown("---")
        st.subheader("📄 Pagine Disponibili")
        st.markdown("""
        - **Pannello di Controllo** - Visualizza statistiche e panoramica del sistema
        - **Membri** - Sfoglia il registro dei membri
        - **Test Cooper** - Visualizza risultati e tendenze dei test Cooper
        - **Prove Indoor** - Analizza i dati di allenamento indoor
        """)

        return

    # Show login form
    auth_manager.show_login_form()


if __name__ == "__main__":
    main()
