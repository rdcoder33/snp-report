import streamlit as st
import pandas as pd
import altair as alt

# Tailwind color palette
COLORS = {
    "jade": "#44AD6C",
    "wisteria": "#AA97CD",
    "sandy_brown": "#F2984A",
    "seasalt": "#FAFAFA",
    "bittersweet": "#FF5C60"
}

# Set the page configuration
st.set_page_config(page_title="Genetic Variant Report", layout="wide")

# Custom CSS styling for colorful UI
custom_css = f"""
<style>
body {{
    background-color: {COLORS['seasalt']};
}}

/* Main title */
h1 {{
    color: {COLORS['jade']};
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-weight: 800;
    letter-spacing: 1px;
    background: linear-gradient(90deg, {COLORS['jade']}, {COLORS['wisteria']}, {COLORS['sandy_brown']});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

/* Info box */
.stAlert {{
    background: linear-gradient(90deg, {COLORS['wisteria']}22, {COLORS['jade']}22);
    border-left: 6px solid {COLORS['jade']};
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    background: {COLORS['wisteria']}11;
    border-radius: 8px 8px 0 0;
    border-bottom: 2px solid {COLORS['sandy_brown']};
}}
.stTabs [data-baseweb="tab"] {{
    color: {COLORS['wisteria']};
    font-weight: 600;
}}
.stTabs [aria-selected="true"] {{
    color: {COLORS['bittersweet']};
    border-bottom: 3px solid {COLORS['bittersweet']};
    background: {COLORS['seasalt']};
}}

/* Sidebar */
.stSidebar {{
    background: linear-gradient(180deg, {COLORS['jade']}11, {COLORS['wisteria']}11);
}}

/* Dataframe header */
.stDataFrame thead tr th {{
    background: {COLORS['jade']}22;
    color: {COLORS['jade']};
    font-weight: 700;
}}

/* Expander */
.stExpanderHeader {{
    color: {COLORS['sandy_brown']};
    font-weight: 700;
}}

/* Buttons and selectbox */
.stButton>button, .stSelectbox>div>div {{
    background: {COLORS['jade']}22;
    color: {COLORS['jade']};
    border-radius: 6px;
    border: 1px solid {COLORS['jade']}55;
}}

/* Markdown links */
a {{
    color: {COLORS['bittersweet']};
    font-weight: 600;
}}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Main title and introduction
st.markdown('<h1>Functional and Clinical Interpretation of the Listed Variants</h1>', unsafe_allow_html=True)
st.markdown(f"""
Below is a structured summary for each variant covering gene function, variant effect, health associations, and clinical significance.
Public clinical or population databases (e.g., ClinVar, SNPedia) are referenced where applicable. Confidence levels and uncertainties are highlighted.
""")
st.markdown("---")

# Prepare Summary Table data (used later for visualization as well)
table_data = [
    ["rs1801282", "PPARG", "CC", "Missense (Pro12Pro)", "Reference; no increased risk", "Benign", "High; well-studied"],
    ["rs266729", "ADIPOQ", "CG", "Promoter", "Uncertain impact on metabolic health", "Uncertain/VUS", "Moderate; inconsistent"],
    ["rs328", "LPL", "CC", "Stop-gain (Ser447)", "Reference; typical lipid metabolism", "Benign", "High; well-studied"],
    ["rs7903146", "TCF7L2", "CC", "Intronic", "Reference; no increased diabetes risk", "Benign", "High; strong evidence"],
    ["rs9939609", "FTO", "AA", "Intronic", "Increased BMI/obesity risk", "Benign (trait-linked)", "High; polygenic risk"],
    ["rs4343", "ACE", "AG", "Synonymous", "Minor/modest BP association, if any", "Benign", "Moderate; small effect"],
]
table_columns = [
    "rsID", "Gene", "Genotype", "Variant Type", "Trait/Impact", "Clinical Significance", "Confidence/Notes"
]
summary_df = pd.DataFrame(table_data, columns=table_columns)

# Create tabs for different sections
tabs = st.tabs(["Overview", "Variant Details", "Summary Table", "Visualizations", "Citations"])

# -------------------------------------------
# Tab 1: Overview
with tabs[0]:
    st.markdown("## Overview")
    st.info(f"""
• Most variants are well-characterized and common, mostly with a benign clinical interpretation.
• FTO rs9939609 (AA) is linked with increased BMI/obesity risk but is not classified as pathogenic.
• ADIPOQ rs266729 (CG) shows uncertain impacts on metabolic health and is best considered a variant of uncertain significance (VUS).
• There is no single variant considered pathogenic – effect sizes are modest and traits are polygenic.
""")
    st.markdown(f"""
Note: This tool is primarily for visualizing variant annotations. Any clinical decision‐making should integrate a wider clinical context and more comprehensive genetic data.
""")

# -------------------------------------------
# Tab 2: Variant Details (Interactive)
with tabs[1]:
    st.markdown("## Variant Details")

    # Dictionary with detailed descriptions for each variant.
    variant_details = {
        "rs1801282 (PPARG, Genotype: CC)": {
            "Gene & Variant Function": """
- **PPARG** encodes peroxisome proliferator-activated receptor gamma, a nuclear receptor critical for adipocyte differentiation, fat storage, and insulin sensitivity.
- The variant rs1801282 is a missense variant (Pro12Ala, p.Pro12Ala). The common C allele encodes proline.
""",
            "Health Impact": """
- The **CC genotype (Pro/Pro)** is the most common and considered the reference.
- The rare G allele (Ala12) is associated in some studies with improved insulin sensitivity and a reduced risk of type 2 diabetes, though effect sizes are small.
""",
            "Clinical Significance": """
- Classified as **benign** in ClinVar.
- There is no evidence that the CC genotype is linked to increased or decreased risk compared to the general population.
""",
            "Evidence Strength": """
- Supported by meta-analyses and large population studies.
- There are no conflicting interpretations for this common genotype.
"""
        },
        "rs266729 (ADIPOQ, Genotype: CG)": {
            "Gene & Variant Function": """
- **ADIPOQ** encodes adiponectin, involved in glucose regulation and fatty acid oxidation.
- The variant is located in the promoter region of ADIPOQ, potentially affecting gene expression.
""",
            "Health Impact": """
- The G allele has been linked in some studies to lower adiponectin levels and increased risk of metabolic syndrome and type 2 diabetes.
- The **CG genotype** may confer an intermediate risk profile, but the clinical impact remains uncertain.
""",
            "Clinical Significance": """
- Classified as a **variant of uncertain significance (VUS)**.
- Evidence remains variable with only modest effect sizes.
""",
            "Evidence Strength": """
- Evidence is moderate but inconsistent.
- Further studies are required to clarify these associations.
"""
        },
        "rs328 (LPL, Genotype: CC)": {
            "Gene & Variant Function": """
- **LPL** encodes lipoprotein lipase which is key for triglyceride metabolism.
- rs328 is a stop-gain (nonsense) variant (Ser447Ter); the common C allele encodes a full-length functional enzyme.
""",
            "Health Impact": """
- The **CC genotype (Ser/Ser)** is the reference and typically does not alter lipid metabolism.
- In contrast, the G allele (Ter) is associated with lower triglyceride levels and may reduce coronary artery disease risk.
""",
            "Clinical Significance": """
- The CC genotype is **benign**.
- The variant is well-characterized in population studies.
""",
            "Evidence Strength": """
- Robust data and meta-analyses support these observations.
"""
        },
        "rs7903146 (TCF7L2, Genotype: CC)": {
            "Gene & Variant Function": """
- **TCF7L2** encodes a transcription factor involved in the Wnt signaling pathway, impacting insulin secretion.
- rs7903146 is an intronic variant; the T allele is a recognized risk factor for type 2 diabetes.
""",
            "Health Impact": """
- The **CC genotype** is non-risk; individuals typically show average population risk.
- Carriers of the risk-associated T allele show increased diabetes risk.
""",
            "Clinical Significance": """
- The CC genotype is classified as **benign**.
- It is widely used in genetic risk scores for type 2 diabetes.
""",
            "Evidence Strength": """
- Risk associations are robust and have been replicated across populations.
"""
        },
        "rs9939609 (FTO, Genotype: AA)": {
            "Gene & Variant Function": """
- **FTO** is implicated in body mass regulation and appetite control.
- rs9939609 is an intronic SNP where the A allele is associated with higher BMI.
""",
            "Health Impact": """
- The **AA genotype** confers the highest genetic predisposition for increased BMI/obesity.
- Each A allele may increase BMI modestly; effects vary across populations.
- While not directly disease-causing, obesity risk may contribute to metabolic disease.
""",
            "Clinical Significance": """
- Although clearly linked with a trait, it is classified as **benign** in ClinVar.
- This is a common variant with modest, polygenic effects.
""",
            "Evidence Strength": """
- Supported by large GWAS with consistent replication.
"""
        },
        "rs4343 (ACE, Genotype: AG)": {
            "Gene & Variant Function": """
- **ACE** encodes angiotensin converting enzyme, critical for blood pressure regulation.
- rs4343 is a synonymous SNP; it is also used as a marker for the ACE I/D polymorphism.
""",
            "Health Impact": """
- The G allele may be modestly associated with higher circulating ACE levels.
- The **AG genotype** does not clearly alter cardiovascular risk.
""",
            "Clinical Significance": """
- The variant is classified as **benign**.
- Observed effects are small and not considered clinically actionable alone.
""",
            "Evidence Strength": """
- Findings are supported by population studies, though effect sizes remain minor.
"""
        }
    }

    # Sidebar selectbox for picking a variant
    variant_list = list(variant_details.keys())
    selected_variant = st.selectbox("Select a Variant to view details:", variant_list)

    # Display variant details in expandable sections
    st.markdown(f"### Details for {selected_variant}")
    details = variant_details[selected_variant]
    for section_title, content in details.items():
        with st.expander(f"{section_title}"):
            st.markdown(content)

# -------------------------------------------
# Tab 3: Summary Table
with tabs[2]:
    st.markdown("## Summary Table")
    st.dataframe(summary_df, use_container_width=True)
    st.markdown(f"""
The table above summarizes key aspects of each variant, including genotype, variant type, trait impact, clinical significance, and the level of supporting evidence.
""")

# -------------------------------------------
# Tab 4: Visualizations
with tabs[3]:
    st.markdown("## Visualizations")

    st.markdown("### Clinical Significance Distribution")
    # For visualization, collapse clinical significance entries into two groups
    # We count any mention of 'Benign' as 'Benign', otherwise 'Uncertain/VUS'
    summary_df["Significance"] = summary_df["Clinical Significance"].apply(
        lambda x: "Benign" if "Benign" in x else "Uncertain/VUS"
    )
    sig_counts = summary_df["Significance"].value_counts().reset_index()
    sig_counts.columns = ["Significance", "Count"]

    pie_chart = alt.Chart(sig_counts).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field="Count", type="quantitative"),
        color=alt.Color(field="Significance", type="nominal", scale=alt.Scale(domain=["Benign", "Uncertain/VUS"], range=[COLORS['jade'], COLORS['bittersweet']])),
        tooltip=["Significance", "Count"]
    ).properties(
        width=350,
        height=350,
        title="Clinical Significance Distribution"
    )
    st.altair_chart(pie_chart, use_container_width=True)

    st.markdown("### Evidence Strength Distribution")
    # Extracting the confidence rating as the first word before a semicolon
    summary_df["Confidence_Rating"] = summary_df["Confidence/Notes"].apply(lambda x: x.split(";")[0].strip())
    confidence_counts = summary_df["Confidence_Rating"].value_counts().reset_index()
    confidence_counts.columns = ["Confidence_Rating", "Count"]

    bar_chart = alt.Chart(confidence_counts).mark_bar().encode(
        x=alt.X("Confidence_Rating:N", title="Evidence Strength"),
        y=alt.Y("Count:Q", title="Number of Variants"),
        color=alt.Color("Confidence_Rating:N", scale=alt.Scale(domain=["High", "Moderate"], range=[COLORS['wisteria'], COLORS['sandy_brown']])),
        tooltip=["Confidence_Rating", "Count"]
    ).properties(
        width=400,
        height=300,
        title="Evidence Strength Overview"
    )
    st.altair_chart(bar_chart, use_container_width=True)

# -------------------------------------------
# Tab 5: Citations
with tabs[4]:
    st.markdown("## Citations")
    st.markdown(f"""
References and Data Sources:
- [GenomeBrowse](https://www.goldenhelix.com/products/GenomeBrowse/)
- [PMC Article](https://pmc.ncbi.nlm.nih.gov/articles/PMC9224645/)
- [Brown GMILab Tools](https://sites.brown.edu/gmilab/tools/)
- [Procogia Variant Visualization](https://procogia.com/variant-visualization-r-shiny-app/)
- [SFARI Gene Data Visualization](https://gene.sfari.org/about-data-visualization/)
""")
