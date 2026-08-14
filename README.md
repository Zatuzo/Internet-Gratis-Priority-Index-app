# 🌐 Village Wi-Fi Priority Index (TOPSIS Engine)

An interactive, bilingual web application built with Streamlit to calculate and visualize the priority index of villages for Wi-Fi installation using the **TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)** method.

This application is designed to assist Decision Makers (e.g., Diskominfo Kutai Kartanegara) in allocating budgets efficiently based on five core criteria: Population, Poverty Rate, Distance to City Center, Existing Signal Availability, and Number of Schools.

---

## 🚀 Key Features

* **Bilingual Support**: Toggle between **English** and **Bahasa Indonesia** dynamically in the sidebar.
* **100% Shared Weight Allocation**: Interactive sliders at the top of the dashboard let you allocate weights to different criteria. The sliders visually and physically lock when the total sum reaches `100%` (dynamic remaining budget capping), preventing allocation errors.
* **Policy Sensitivity Comparator**: Compare priority shifts side-by-side between two distinct policy scenarios (e.g., Focus on Education vs. Focus on Poverty Alleviation) to see how weighting changes affect rankings in real-time.
* **Real-time GeoServer Integration**: Fetches spatial data from the Palapa Kutai Kartanegara WFS GeoServer, parsing coordinates and properties into a unified clean local dataset with automatic fallback options.
* **Geospatial Map (Google Maps & ArcGIS Polygons)**: Dynamic markers displaying village details on roadmap/satellite maps, complete with shaded boundary polygons, color-coded by priority (High 🔴, Medium 🟠, Low 🟢).
* **Filter & Search Controls**: Search villages by name, filter by existing signal status, or set a minimum poverty rate. Graphs, tables, and the map update in real-time.
* **Bilingual Executive PDF Brief Export**: Generate and download official, presentation-ready PDF reports summarizing weighting configurations, priority charts, and executive insights.
* **Export Data**: Directly export/download the filtered priority lists to a CSV file.
* **Modular Codebase**: Architected with separate modules for configurations, calculations, UI components, data cleaning, and PDF generation.

---

## 🛠️ Installation & Setup

Follow these steps to run the application locally on your machine.

### Prerequisites

* Python 3.8 or higher installed on your system.

### 1. Clone the Repository
```bash
git clone https://github.com/Zatuzo/Internet-Gratis-Priority-Index-app.git
cd Internet-Gratis-Priority-Index-app
```

### 2. Set Up a Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 💻 Running the Application

Ensure your virtual environment is active, then run:

```bash
streamlit run app.py
```

The application will start, and a browser window should automatically open to:
👉 **[http://localhost:8503](http://localhost:8503)** (or another port if port 8503 is busy)

---

## 📖 How to Use the App

1. **Select Language**: Go to the sidebar and choose either **English** or **Bahasa Indonesia** to switch languages.
2. **Allocate Weights**: Adjust the 5 sliders in the **TOPSIS Weight Allocation** panel at the top. The sliders will change to a **glowing green** when they sum up to exactly `100%`. To increase a slider when the budget is full, you must first lower another slider.
3. **Compare Policies**: Navigate to the comparator tab to configure two separate weight configurations (Scenario A vs Scenario B) and observe the sensitivity of rankings.
4. **Filter Results**: Use the **Filter & Search Controls** below the weights panel to narrow down villages by name, existing signal availability, or poverty levels.
5. **Inspect Dashboard**:
   * Review the **Top Priority Villages** bar chart.
   * View the **Summary Metrics** for the top-ranked village.
   * Look at the **Detailed Ranking Table** for precise numeric scores.
6. **View Geospatial Map**: Scroll down to the **Geospatial View** to inspect village locations. Click on any pin marker to see its name, signal status, poverty percentage, schools, and TOPSIS score. You can toggle map types and the ArcGIS polygon boundary overlays.
7. **Export Data & Report**: Click the **Download Filtered Priority List CSV** button to download your calculated priorities, or click the **Download Executive Policy Brief PDF** button for a print-ready briefing.
