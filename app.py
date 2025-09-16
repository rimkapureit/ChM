import streamlit as st
import pandas as pd
import io
from datetime import datetime
import openpyxl

FACTURE_COLUMNS = ['Client', 'Date', 'Montant HT', 'TPS (5%)', 'TVQ (9,975%)', 'Total', 'Statut']
DEPENSE_COLUMNS = ['Fournisseur', 'Catégorie', 'Date', 'Montant HT', 'TPS (5%)', 'TVQ (9,975%)', 'Total']

def show_dashboard():
    st.title("ChM consulting - comptabilité")
    factures = st.session_state.factures
    depenses = st.session_state.depenses
    st.metric('Revenus HT', f"{factures['Montant HT'].sum():.2f}")
    st.metric('TPS collectée', f"{factures['TPS (5%)'].sum():.2f}")
    st.metric('TVQ collectée', f"{factures['TVQ (9,975%)'].sum():.2f}")
    st.metric('TPS payée/déduite', f"{depenses['TPS (5%)'].sum():.2f}")
    st.metric('TVQ payée/déduite', f"{depenses['TVQ (9,975%)'].sum():.2f}")
    impot = 0.32 * max(0, factures['Montant HT'].sum() - depenses['Montant HT'].sum())
    st.metric('Impôt prévisionnel (32%)', f"{impot:.2f}")

    st.subheader('Factures')
    if not factures.empty:
        factures_display = factures.copy()
        factures_display.index.name = "ID"
        st.dataframe(factures_display)
        edit_id = st.number_input(
            "ID facture à modifier (entier)", min_value=0, max_value=len(factures)-1, step=1, format='%d', key="edit_facture_id", help="Choisir l'ID à gauche du tableau"
        )
        if st.button("Modifier cette facture"):
            st.session_state.page = 'modifier_facture'
            st.session_state.edit_id = edit_id
            st.rerun()
    else:
        st.write("Aucune facture enregistrée.")

    st.subheader('Dépenses')
    if not depenses.empty:
        depenses_display = depenses.copy()
        depenses_display.index.name = "ID"
        st.dataframe(depenses_display)
    else:
        st.write("Aucune dépense enregistrée.")

def add_facture():
    st.title("Ajouter une facture")
    with st.form("form_facture"):
        client = st.text_input('Client')
        date = st.date_input('Date', datetime.now())
        montant_ht = st.number_input('Montant HT', min_value=0.0, step=0.01)
        status = st.selectbox('Statut', ['Payée', 'Impayée'])
        submit = st.form_submit_button("Créer")
        if submit:
            tps = montant_ht * 0.05
            tvq = montant_ht * 0.09975
            total = montant_ht + tps + tvq
            new_row = {
                'Client': client,
                'Date': date.strftime('%Y-%m-%d'),
                'Montant HT': montant_ht,
                'TPS (5%)': tps,
                'TVQ (9,975%)': tvq,
                'Total': total,
                'Statut': status
            }
            st.session_state.factures = pd.concat(
                [st.session_state.factures, pd.DataFrame([new_row])], ignore_index=True
            )
            st.success("Facture créée avec succès !")
            st.session_state.page = 'dashboard'
            st.rerun()

def add_depense():
    st.title("Ajouter une dépense")
    with st.form("form_depense"):
        fournisseur = st.text_input('Fournisseur')
        categorie = st.text_input('Catégorie')
        date = st.date_input('Date', datetime.now())
        montant_ht = st.number_input('Montant HT', min_value=0.0, step=0.01)
        submit = st.form_submit_button("Créer")
        if submit:
            tps = montant_ht * 0.05
            tvq = montant_ht * 0.09975
            total = montant_ht + tps + tvq
            new_row = {
                'Fournisseur': fournisseur,
                'Catégorie': categorie,
                'Date': date.strftime('%Y-%m-%d'),
                'Montant HT': montant_ht,
                'TPS (5%)': tps,
                'TVQ (9,975%)': tvq,
                'Total': total
            }
            st.session_state.depenses = pd.concat(
                [st.session_state.depenses, pd.DataFrame([new_row])], ignore_index=True
            )
            st.success("Dépense ajoutée avec succès !")
            st.session_state.page = 'dashboard'
            st.rerun()

def modifier_facture():
    st.title("Modifier une facture")
    edit_id = st.session_state.get('edit_id', None)
    factures = st.session_state.factures
    if edit_id is None or edit_id >= len(factures):
        st.error("ID facture invalide.")
        if st.button("Retour au dashboard"):
            st.session_state.page = 'dashboard'
            st.rerun()
        return

    facture = factures.loc[edit_id].copy()
    with st.form("form_modifier_facture"):
        client = st.text_input('Client', value=facture['Client'])
        dt_val = datetime.strptime(facture['Date'], '%Y-%m-%d')
        date = st.date_input('Date', value=dt_val)
        montant_ht = st.number_input('Montant HT', value=float(facture['Montant HT']), min_value=0.0, step=0.01)
        status = st.selectbox('Statut', ['Payée', 'Impayée'], index=0 if facture['Statut'] == 'Payée' else 1)
        submit = st.form_submit_button("Enregistrer")
        if submit:
            tps = montant_ht * 0.05
            tvq = montant_ht * 0.09975
            total = montant_ht + tps + tvq
            st.session_state.factures.loc[edit_id] = [
                client, date.strftime('%Y-%m-%d'), montant_ht,
                tps, tvq, total, status
            ]
            st.success("Facture modifiée avec succès !")
            st.session_state.page = 'dashboard'
            st.rerun()
    if st.button("Annuler modification"):
        st.session_state.page = 'dashboard'
        st.rerun()

def sidebar_navigation():
    with st.sidebar:
        st.title("Navigation")
        if st.button("Dashboard"):
            st.session_state.page = 'dashboard'
        if st.button("Ajouter Facture"):
            st.session_state.page = 'ajouter_facture'
        if st.button("Ajouter Dépense"):
            st.session_state.page = 'ajouter_depense'

        st.markdown("---")
        if not st.session_state.factures.empty:
            output_f = io.BytesIO()
            with pd.ExcelWriter(output_f, engine='openpyxl') as writer:
                st.session_state.factures.to_excel(writer, index=False)
            st.download_button(
                label="Télécharger factures (Excel)",
                data=output_f.getvalue(),
                file_name="factures.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        if not st.session_state.depenses.empty:
            output_d = io.BytesIO()
            with pd.ExcelWriter(output_d, engine='openpyxl') as writer:
                st.session_state.depenses.to_excel(writer, index=False)
            st.download_button(
                label="Télécharger dépenses (Excel)",
                data=output_d.getvalue(),
                file_name="depenses.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

def main():
    if 'page' not in st.session_state:
        st.session_state.page = 'dashboard'
    if 'factures' not in st.session_state:
        st.session_state.factures = pd.DataFrame(columns=FACTURE_COLUMNS)
    if 'depenses' not in st.session_state:
        st.session_state.depenses = pd.DataFrame(columns=DEPENSE_COLUMNS)
    if 'edit_id' not in st.session_state:
        st.session_state.edit_id = None

    sidebar_navigation()

    if st.session_state.page == 'dashboard':
        show_dashboard()
    elif st.session_state.page == 'ajouter_facture':
        add_facture()
    elif st.session_state.page == 'ajouter_depense':
        add_depense()
    elif st.session_state.page == 'modifier_facture':
        modifier_facture()

if __name__ == '__main__':
    main()
