# This will be the cleaned and Streamlit-ready version of your full code
# It includes: GPT call, analysis loop, output to DataFrame, Excel download, and score calculation
# UI is built using Streamlit, so it replaces getpass, print, and Colab functions with Streamlit methods

import streamlit as st
import openai
import pandas as pd
import json
import os

st.set_page_config(page_title="DPDPA Compliance Checker", layout="wide")
st.title("📜 DPDPA Compliance Checker")

# --- OpenAI API Key ---
api_key = os.getenv("OPENAI_API_KEY") or st.text_input("🔑 Enter your OpenAI API Key", type="password")
if not api_key:
    st.stop()

client = openai.OpenAI(api_key=api_key)

# --- Text Inputs ---
dpdpa_chapter_text = st.text_area("📘 DPDPA Chapter II Text", height=300)
privacy_policy_text = st.text_area("📄 Privacy Policy Text", height=300)

# --- DPDPA Sections ---
dpdpa_sections = [
    "Section 4 — Grounds for Processing Personal Data",
    "Section 5 — Notice",
    "Section 6 — Consent",
    "Section 7 — Certain Legitimate Uses",
    "Section 8 — General Obligations of Data Fiduciary",
    "Section 9 — Processing of Personal Data of Children",
    "Section 10 — Additional Obligations of Significant Data Fiduciaries"
]

# --- GPT Function ---
def analyze_section(section_text, policy_text, full_chapter_text):
    prompt = f"""
You are a DPDPA compliance expert. Your task is to assess whether an organization's policy complies with the Digital Personal Data Protection Act, 2023 (India) — specifically Sections 4 to 10 under Chapter II. 

You must **read each sentence in the policy** and compare it with the legal **checklist of obligations derived from the assigned DPDPA Section**.

==========================================================
ORGANIZATION POLICY:
\"\"\"{policy_text}\"\"\"

DPDPA SECTION UNDER REVIEW:
\"\"\"{section_text}\"\"\"

==========================================================
INSTRUCTIONS:

1. **Understand the Law in Simple Terms**
   - Read the DPDPA Section carefully and explain it in your own words in simple, layman-friendly language.
   - Capture *every important legal requirement* from the section.

2. **Checklist Mapping**
   - Refer to the official checklist of obligations provided for this section.
   - For each checklist item do following- 
      - Go through the policy *sentence by sentence* and see if that sentence addresses the checklist item.
      - **Only count an item as covered if it is explicitly and clearly mentioned in the policy with correct context. Vague, generic, or partial references must be marked as unmatched. Do not assume implied meaning — legal clarity is required.**
      - Do not make assumptions.
      - This needs to be shown in the output - "Checklist Items" - In this -  mention the checklist item, whether it matches or not, the sentence/s from policy to which this checklist item matches and what is the justification for it getting matched.

3. **Classification**
   - Match Level:
     - "Fully Compliant": All checklist items are covered clearly.
     - "Partially Compliant": At least one item is missing or only vaguely mentioned.
     - "Non-Compliant": No checklist item is covered.
   - Severity (only for Partially Compliant):
     - Minor = 1 missing item
     - Medium = 2–3 missing items
     - Major = 4 or more missing / any critical clause missing
   - Compliance Points:
     - Fully Compliant = 1.0
     - Partially Compliant:
        - Minor = 0.75
        - Medium = 0.5
        - Major = 0.25
     - Non-Compliant = 0.0

4. **Suggested Rewrite**
   - This is an extremely important step so do this properly. For the section do the following points - 
      - Review the **checklist** for this section again and identify which items are **missing** from the policy.
      - For each missing item, write **1 sentence** that can be added to the policy to ensure compliance.
      - The rewrite should be a clear, implementable policy statement for each missing item.
==========================================================
OUTPUT FORMAT (strict JSON):
{{
  "DPDPA Section": "...",
  "DPDPA Section Meaning": "...",
  "Checklist Items": [
    {{
      "Item": "...",
      "Matched": true/false,
      "Matched Sentences": ["...", "..."],
      "Justification": "..."
    }},
    ...
  ],
  "Match Level": "...",
  "Severity": "...",
  "Compliance Points": "...",
  "Suggested Rewrite": "..."
}}

==========================================================
CHECKLIST TO USE:


**Section 4: Grounds for Processing Personal Data**

1. ☐ Personal data is processed **only** for lawful purposes.
2. ☐ Lawful purpose must be:

   * ☐ Backed by **explicit consent** from the Data Principal **OR**
   * ☐ Falls under **legitimate uses** as per Section 7.
3. ☐ Lawful purpose must **not be expressly forbidden** by any law.

**Section 5: Notice Before Consent**

1. ☐ Notice is provided **before or at the time** of requesting consent.
2. Notice must clearly mention:

   * ☐ What **personal data** is being collected.
   * ☐ The **purpose** of processing.
   * ☐ How to **exercise rights** under Section 6(4) and Section 13.
   * ☐ How to **lodge complaints** with the Board.
3. ☐ For existing data collected **before DPDPA**, retrospective notice must also be issued as soon as practicable with all points above.

**Section 6: Consent and Its Management**

1. ☐ Consent is **free, specific, informed, unconditional, and unambiguous**.
2. ☐ Consent is **given via clear affirmative action**.
3. ☐ Consent is **limited to specified purpose only**.
4. ☐ Consent can be **withdrawn** at any time.
5. ☐ Data Fiduciary shall **cease processing** upon withdrawal (unless legally required).
6. ☐ Consent Manager is available (if applicable):

   * ☐ Consent Manager is **registered** and functions independently.
   * ☐ Consent Manager allows:

     * ☐ Giving, managing, and withdrawing consent easily.
     * ☐ Logs consent history for audit.
7. ☐ Data Fiduciary must honor withdrawal requests promptly.
8. ☐ Retention of personal data stops unless required by law.

**Section 7: Legitimate Uses (No Consent Needed)**

Processing without consent is allowed **only** if it meets the following (tick applicable):

* ☐ For specified government subsidies/services/licenses.
* ☐ For State functions (e.g., national security, law enforcement).
* ☐ To comply with legal obligations.
* ☐ Under court orders or judgments.
* ☐ For medical emergencies or disasters.
* ☐ For employment-related purposes with safeguards.
* ☐ For corporate security or internal fraud prevention.
  Each use must:

  * ☐ Be **necessary** and **proportionate**.
  * ☐ Adhere to standards/rules to be prescribed.

**Section 8: General Obligations of Data Fiduciary**

1. ☐ Fiduciary is fully accountable for processing by itself or its Data Processor.
2. ☐ Processing must be under a valid **contract** with the Data Processor.
3. ☐ If data is to:

   * ☐ Influence decisions or
   * ☐ Be shared with other Fiduciaries,
     → Then data must be:

     * ☐ Complete
     * ☐ Accurate
     * ☐ Consistent
4. ☐ Implement **technical and organisational measures** for compliance.
5. ☐ Take **reasonable security safeguards** to prevent breaches.
6. ☐ Report data breaches to:

   * ☐ Data Protection Board
   * ☐ Affected Data Principals
7. ☐ Erase data when:

   * ☐ Consent is withdrawn, OR
   * ☐ Purpose is no longer being served
   * ☐ Also instruct Data Processor to erase it.
8. ☐ Define time periods for retention based on inactivity of Data Principal.
9. ☐ Publish business contact info of DPO or responsible officer.
10. ☐ Establish a grievance redressal mechanism.

**Section 9: Processing Children’s Data**

1. ☐ Verifiable **parental/guardian consent** is obtained before processing data of:

   * ☐ Children (<18 years)
   * ☐ Persons with lawful guardians
2. ☐ No processing that causes **detrimental effect** to child’s well-being.
3. ☐ No **tracking, behavioral monitoring**, or **targeted advertising** directed at children.
4. ☐ Follow any **exemptions** as notified (for class of fiduciaries or safe processing).
5. ☐ Central Govt. may relax obligations if processing is **verifiably safe** and meets minimum age threshold.

**Section 10: Significant Data Fiduciary (SDF) Obligations**

Only applies if declared as SDF:

1. ☐ Appoint a **Data Protection Officer (DPO)**:

   * ☐ Based in India
   * ☐ Reports to board/similar authority
   * ☐ Point of contact for grievance redressal
2. ☐ Appoint an **independent Data Auditor**.
3. ☐ Conduct:

   * ☐ Periodic **Data Protection Impact Assessments**
   * ☐ **Audits** of data processing
   * ☐ Any other measures as may be prescribed
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content

# --- Execution ---
if st.button("🚀 Run Compliance Check"):
    if not dpdpa_chapter_text or not privacy_policy_text:
        st.warning("Please paste both DPDPA and Privacy Policy text.")
        st.stop()

    results = []
    with st.spinner("Analyzing each DPDPA section..."):
        for section in dpdpa_sections:
            try:
                section_response = analyze_section(section, privacy_policy_text, dpdpa_chapter_text)
                parsed_section = json.loads(section_response)
                results.append(parsed_section)
            except Exception as e:
                st.error(f"❌ Error analyzing {section}: {e}")

    if results:
        df = pd.DataFrame(results)
        st.success("✅ Analysis Completed!")
        st.dataframe(df)

        # Download button
        excel_filename = "DPDPA_Compliance_SectionWise_Final.xlsx"
        df.to_excel(excel_filename, index=False)
        with open(excel_filename, "rb") as f:
            st.download_button("📥 Download Excel", f, file_name=excel_filename)

        # Compliance Score
        try:
            scored_points = df['Compliance Points'].astype(float).sum()
            total_points = len(dpdpa_sections) * 1.0
            score = (scored_points / total_points) * 100
            st.metric("🎯 Compliance Score", f"{score:.2f}%")
        except:
            st.warning("⚠️ Could not compute score. Check data types.")
