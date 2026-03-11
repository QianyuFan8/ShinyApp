from shiny import App, render, ui, reactive
import pandas as pd
import json
from pathlib import Path
import io

# ============================================================================
# LOAD DATA
# ============================================================================

# Get the correct data path (relative to app.py)
DATA_DIR = Path(__file__).parent.parent / 'data' / 'processed'

# Load all necessary data
drugs_df = pd.read_csv(DATA_DIR / 'drug_master.csv')
interactions_df = pd.read_csv(DATA_DIR / 'interactions.csv')
drug_info_df = pd.read_csv(DATA_DIR / 'drug_info.csv')
side_effects_df = pd.read_csv(DATA_DIR / 'side_effects.csv')

# Load metadata
with open(DATA_DIR / 'metadata.json', 'r') as f:
    metadata = json.load(f)

with open(DATA_DIR / 'network_data.json', 'r') as f:  
    network_data = json.load(f)     

with open(DATA_DIR / 'search_index.json', 'r') as f:  
    search_index = json.load(f)   

# Create drug choices for dropdown (sorted alphabetically)
drug_choices = sorted(drugs_df['generic_name'].tolist())

# ============================================================================
# UI DEFINITION
# ============================================================================

app_ui = ui.page_fluid(
    # Custom CSS for styling
    ui.tags.style("""
        .app-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .app-title {
            font-size: 28px;
            font-weight: bold;
            margin: 0;
        }
        .app-subtitle {
            font-size: 13px;
            opacity: 0.9;
            margin-top: 3px;
        }
        .severity-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            color: white;
        }
        .severity-high {
            background-color: #E74C3C;
        }
        .severity-medium {
            background-color: #F39C12;
        }
        .severity-low {
            background-color: #27AE60;
        }
        .drug-info-panel {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-top: 10px;
            height: 755px;            
            overflow-y: auto;
        }
        .interaction-detail-box {
            background: white;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            margin-top: 10px;
        }
        .section-header {
            font-size: 15px;
            font-weight: bold;
            color: #495057;
            margin-top: 15px;
            margin-bottom: 10px;
            padding-bottom: 5px;
            border-bottom: 2px solid #dee2e6;
        }
        .sidebar .well {
            padding: 15px;
        }
        .sidebar h4 {
            font-size: 16px;
            margin-top: 0;
            margin-bottom: 10px;
        }
        .sidebar hr {
            margin: 15px 0;
        }
        /* Network visualizer styles */
        #network_container {
            width: 100%;
            height: 600px;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            background: white;
        }
        .network-info-panel {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
        }
        .legend-item {
            display: inline-block;
            margin-right: 20px;
            margin-bottom: 10px;
        }
        .legend-dot {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 5px;
        }
        .side-effect-badge {
            display: inline-block;
            padding: 3px 8px;
            margin: 3px;
            border-radius: 10px;
            font-size: 12px;
            background: #e9ecef;
            color: #495057;
        }     
    """),
    
    # Header - SMALLER VERSION
    ui.div(
        {"class": "app-header"},
        ui.h1("RxCheck: Drug Interaction Checker", class_="app-title"),
        ui.p(
            f"• {metadata['total_drugs']} drugs • {metadata['total_interactions']} interactions",
            class_="app-subtitle"
        )
    ),

    # ====================================================================
    # TAB 1: Interaction Checker
    # ====================================================================
    
    # Main content
    ui.navset_tab(
        ui.nav_panel(
            "Interaction Checker",
            ui.layout_sidebar(
                # LEFT SIDEBAR - COMPACT VERSION
                ui.sidebar(
                    # Drug Selector
                    ui.h4("Select Drugs"),
                    ui.input_selectize(
                        "selected_drugs",
                        "",
                        choices=drug_choices,
                        multiple=True,
                        options={
                            "placeholder": "Select drug name...",
                            "maxItems": 10
                        }
                    ),
                    
                    # Filters - MOVED UP
                    ui.h4("Filters", style="margin-top: 15px;"),
                    ui.p("Severity:", style="font-weight: bold; margin-bottom: 5px; font-size: 14px;"),
                    ui.input_checkbox("filter_high", "🔴 High", value=True),
                    ui.input_checkbox("filter_medium", "🟡 Medium", value=True),
                    ui.input_checkbox("filter_low", "🟢 Low", value=True),
                    
                    ui.p("Show:", style="font-weight: bold; margin-top: 15px; margin-bottom: 5px; font-size: 14px;"),
                    ui.input_radio_buttons(
                        "show_filter",
                        "",
                        choices={
                            "all": "All interactions",
                            "selected": "Only between selected drugs"
                        },
                        selected="all"
                    ),
                    
                    # Action buttons - MOVED UP
                    ui.input_action_button(
                        "clear_all",
                        "Clear All",
                        class_="btn-secondary btn-sm",
                        style="width: 100%; margin-top: 15px;"
                    ),
                    
                    width=280
                ),
                
                # MAIN PANEL
                ui.div(
                    ui.row(
                        # Left column: Interactions table and details
                        ui.column(
                            7,
                            ui.h3("Interaction Results", style="margin-top: 0;"),
                            ui.output_ui("interaction_count"),
                            ui.output_data_frame("interactions_table"),
                            
                            ui.h3("Interaction Details", style="margin-top: 20px;"),
                            ui.output_ui("interaction_details")
                        ),
                        
                        # Right column: Drug information
                        ui.column(
                            5,
                            ui.h3("Drug Information", style="margin-top: 0;"),
                            ui.p(
                                "Click any drug in the selector to view details",
                                style="color: #6c757d; font-style: italic; font-size: 14px;"
                            ),
                            ui.output_ui("drug_info_panel")
                        )
                    )
                )
            )
        ),
        
        # ====================================================================
        # TAB 2: NETWORK VISUALIZER
        # ====================================================================
        ui.nav_panel(
            "Network Visualizer",
            ui.layout_sidebar(
                ui.sidebar(
                    ui.h4("Network Settings"),
                    
                    ui.input_selectize(
                        "center_drug",
                        "Center drug:",
                        choices=[""] + drug_choices,
                        options={"placeholder": "Select a drug..."}
                    ),
                    
                    ui.input_slider(
                        "network_depth",
                        "Network depth:",
                        min=1,
                        max=3,
                        value=2,
                        step=1
                    ),
                    
                    ui.hr(),
                    
                    ui.h4("Options"),
                    
                    ui.input_radio_buttons(
                        "color_by",
                        "Color by:",
                        choices={
                            "severity": "Severity",
                            "category": "Drug class"
                        },
                        selected="severity"
                    ),
                    
                    ui.input_checkbox("show_labels", "Show drug names", value=True),
                    
                    ui.hr(),
                    
                    ui.input_action_button(
                        "reset_network",
                        "Reset View",
                        class_="btn-secondary btn-sm",
                        style="width: 100%;"
                    ),
                    
                    ui.div(
                        {"class": "network-info-panel", "style": "font-size: 13px; margin-top: 15px;"},
                        ui.p("Tip:", style="font-weight: bold; margin-bottom: 5px;"),
                        ui.p("Click nodes to see side effects", style="margin: 0;"),
                        ui.p("Click edges to see interactions", style="margin: 0;")
                    ),
                    
                    width=280
                ),
                
                ui.div(
                    ui.row(
                        ui.column(
                            8,
                            ui.h3("Interaction Network", style="margin-top: 0;"),
                            
                            # Network container with vis.js
                            ui.HTML("""
                                <div id="network_container"></div>
                                
                                <script src="https://cdn.jsdelivr.net/npm/vis-network@9.1.2/dist/vis-network.min.js"></script>
                                
                                <script>
                                var network = null;
                                var networkData = null;
                                
                                function initNetwork(nodes, edges) {
                                    var container = document.getElementById('network_container');
                                    
                                    networkData = {
                                        nodes: new vis.DataSet(nodes),
                                        edges: new vis.DataSet(edges)
                                    };
                                    
                                    var options = {
                                        physics: {
                                            enabled: true,
                                            barnesHut: {
                                                gravitationalConstant: -2000,
                                                springLength: 150,
                                                springConstant: 0.04
                                            }
                                        },
                                        nodes: {
                                            shape: 'dot',
                                            size: 20,
                                            font: {
                                                size: 14,
                                                color: '#333'
                                            },
                                            borderWidth: 2,
                                            borderWidthSelected: 4
                                        },
                                        edges: {
                                            width: 2,
                                            selectionWidth: 4,
                                            smooth: {
                                                type: 'continuous'
                                            }
                                        },
                                        interaction: {
                                            hover: true,
                                            zoomView: true,
                                            dragView: true
                                        }
                                    };
                                    
                                    network = new vis.Network(container, networkData, options);
                                    
                                    // Click events
                                    network.on('click', function(params) {
                                        if (params.nodes.length > 0) {
                                            Shiny.setInputValue('selected_node', params.nodes[0], {priority: 'event'});
                                        } else if (params.edges.length > 0) {
                                            var edge = networkData.edges.get(params.edges[0]);
                                            var edgeInfo = edge.from + '|||' + edge.to;
                                            Shiny.setInputValue('selected_edge', edgeInfo, {priority: 'event'});
                                        } else {
                                            Shiny.setInputValue('selected_node', null, {priority: 'event'});
                                        }
                                    });
                                }
                                
                                function updateNetwork(nodes, edges) {
                                    if (network) {
                                        networkData.nodes.clear();
                                        networkData.edges.clear();
                                        networkData.nodes.add(nodes);
                                        networkData.edges.add(edges);
                                        network.fit();
                                    }
                                }
                                </script>
                            """),
                            
                            # Legend
                            ui.div(
                                {"class": "network-info-panel"},
                                ui.h5("Legend:", style="margin-top: 0;"),
                                ui.div(
                                    ui.span({"class": "legend-item"},
                                        ui.span({"class": "legend-dot", "style": "background: #E74C3C;"}),
                                        "High severity"
                                    ),
                                    ui.span({"class": "legend-item"},
                                        ui.span({"class": "legend-dot", "style": "background: #F39C12;"}),
                                        "Medium severity"
                                    ),
                                    ui.span({"class": "legend-item"},
                                        ui.span({"class": "legend-dot", "style": "background: #27AE60;"}),
                                        "Low severity"
                                    )
                                ),
                                ui.p(
                                    "💡 Drag to rearrange • Scroll to zoom • Double-click to focus",
                                    style="margin-top: 10px; font-size: 13px; color: #6c757d;"
                                )
                            )
                        ),
                        
                        ui.column(
                            4,
                            ui.h3("Details", style="margin-top: 0;"),
                            ui.output_ui("node_or_edge_details")
                        )
                    )
                )
            )
        ),

        # ====================================================================
        # TAB 3: PATIENT ANALYZER
        # ====================================================================
        ui.nav_panel(
            "Patient Analyzer",
            ui.layout_sidebar(
                ui.sidebar(
                    ui.h4("Upload Patient Medications"),
                    
                    ui.input_file(
                        "patient_csv",
                        "Upload CSV file:",
                        accept=[".csv"],
                        multiple=False
                    ),
                    
                    ui.p(
                        "CSV should have a 'drug_name' column",
                        style="font-size: 12px; color: #6c757d; margin-top: 5px;"
                    ),
                    
                    ui.hr(),
                    
                    ui.h4("Download Sample CSV"),
                    
                    ui.download_button(
                        "download_sample",
                        "Download Sample",
                        class_="btn-secondary btn-sm",
                        style="width: 100%; margin-bottom: 10px;"
                    ),
                    
                    ui.hr(),
                    
                    ui.h4("Export Report"),
                    
                    ui.download_button(
                        "download_report",
                        "Download Report",
                        class_="btn-primary btn-sm",
                        style="width: 100%;"
                    ),
                    
                    width=280
                ),
                
                ui.div(
                    ui.row(
                        ui.column(
                            12,
                            ui.h3("Patient Medication Analysis", style="margin-top: 0;"),
                            
                            ui.output_ui("upload_status"),
                            
                            # Matched medications table
                            ui.div(
                                ui.h4("Matched Medications", style="margin-top: 20px;"),
                                ui.output_data_frame("matched_medications_table")
                            ),
                            
                            # Risk analysis
                            ui.row(
                                ui.column(
                                    4,
                                    ui.div(
                                        {"class": "interaction-detail-box", 
                                         "style": "border-left: 4px solid #E74C3C; min-height: 150px;"},
                                        ui.h5("🔴 High Risk", style="color: #E74C3C; margin-top: 0;"),
                                        ui.output_ui("high_risk_interactions")
                                    )
                                ),
                                ui.column(
                                    4,
                                    ui.div(
                                        {"class": "interaction-detail-box", 
                                         "style": "border-left: 4px solid #F39C12; min-height: 150px;"},
                                        ui.h5("🟡 Medium Risk", style="color: #F39C12; margin-top: 0;"),
                                        ui.output_ui("medium_risk_interactions")
                                    )
                                ),
                                ui.column(
                                    4,
                                    ui.div(
                                        {"class": "interaction-detail-box", 
                                         "style": "border-left: 4px solid #27AE60; min-height: 150px;"},
                                        ui.h5("🟢 Low Risk", style="color: #27AE60; margin-top: 0;"),
                                        ui.output_ui("low_risk_interactions")
                                    )
                                )
                            ),
                            
                            # Detailed interaction list
                            ui.div(
                                ui.h4("All Detected Interactions", style="margin-top: 30px;"),
                                ui.output_ui("all_interactions_list")
                            )
                        )
                    )
                )
            )
        ),
        
        id="tabs"
    )
)


def server(input, output, session):
    selected_interaction_row = reactive.Value(None)
    selected_drug_for_info = reactive.Value(None)
    
    # ========================================================================
    # TAB 1 SERVER LOGIC (Interaction Checker)
    # ========================================================================
    
    @reactive.Calc
    def filtered_interactions():
        """Get filtered interactions based on selected drugs and filters."""
        
        selected = input.selected_drugs()
        
        if not selected:
            return pd.DataFrame()
        
        # Start with all interactions
        df = interactions_df.copy()
        
        # Filter by selected drugs
        if input.show_filter() == "selected":
            # Only interactions between selected drugs
            df = df[
                df['drug_a_name'].isin(selected) &
                df['drug_b_name'].isin(selected)
            ]
        else:
            # Interactions involving at least one selected drug
            df = df[
                df['drug_a_name'].isin(selected) |
                df['drug_b_name'].isin(selected)
            ]
        
        # Filter by severity
        severity_filters = []
        if input.filter_high():
            severity_filters.append('High')
        if input.filter_medium():
            severity_filters.append('Medium')
        if input.filter_low():
            severity_filters.append('Low')
        
        if severity_filters:
            df = df[df['severity_clean'].isin(severity_filters)]
        
        return df
    
    @output
    @render.ui
    def interaction_count():
        """Display count of interactions found."""
        
        df = filtered_interactions()
        
        if len(df) == 0:
            return ui.p(
                "No interactions found. Try selecting more drugs or adjusting filters.",
                style="color: #6c757d; font-style: italic;"
            )
        
        return ui.p(
            f"Found {len(df)} interaction(s)",
            style="color: #495057; font-weight: bold;"
        )
    
    @output
    @render.data_frame
    def interactions_table():
        """Render the interactions table."""
        
        df = filtered_interactions()
        
        if len(df) == 0:
            return pd.DataFrame()
        
        # Prepare display dataframe
        display_df = df[['drug_a_name', 'drug_b_name', 'severity_clean']].copy()
        display_df.columns = ['Drug A', 'Drug B', 'Severity']
        
        return render.DataGrid(
            display_df,
            selection_mode="row",
            width="100%",
            height="400px"
        )
    
    @output
    @render.ui
    def interaction_details():
        """Display details of selected interaction."""
        
        # Get selected rows from table
        selected_rows = interactions_table.cell_selection()["rows"]
        
        if not selected_rows:
            return ui.div(
                ui.p(
                    "Click a row in the table above to see detailed information.",
                    style="color: #6c757d; font-style: italic; text-align: center; padding: 30px;"
                )
            )
        
        # Get the first selected row
        row_idx = list(selected_rows)[0]
        df = filtered_interactions()
        
        if row_idx >= len(df):
            return ui.div()
        
        interaction = df.iloc[row_idx]
        
        # Determine severity color
        severity_colors = {
            'High': '#E74C3C',
            'Medium': '#F39C12',
            'Low': '#27AE60'
        }
        severity_color = severity_colors[interaction['severity_clean']]
        
        return ui.div(
            {"class": "interaction-detail-box"},
            
            # Header
            ui.h4(
                f"{interaction['severity_clean'].upper()} RISK INTERACTION",
                style=f"color: {severity_color}; margin-top: 0;"
            ),
            
            # Drugs involved
            ui.div(
                ui.strong("Drugs: "),
                f"{interaction['drug_a_name']} + {interaction['drug_b_name']}",
                style="font-size: 16px; margin-bottom: 15px;"
            ),
            
            # Severity
            ui.div(
                ui.strong("Severity: "),
                ui.span(
                    interaction['severity_clean'],
                    class_=f"severity-badge severity-{interaction['severity_clean'].lower()}"
                ),
                style="margin-bottom: 15px;"
            ),
            
            # Description - NO "Data Source" section
            ui.div(
                {"class": "section-header"},
                "Description & Clinical Significance"
            ),
            ui.p(interaction['description'], style="line-height: 1.6;")
        )
    
    @output
    @render.ui
    def drug_info_panel():
        """Display information about selected drug."""
        
        # Use the first selected drug if any
        selected = input.selected_drugs()
        
        if not selected:
            return ui.div(
                ui.p(
                    "Select a drug from the dropdown to view information",
                    style="color: #6c757d; font-style: italic; text-align: center; padding: 40px;"
                )
            )
        
        # Show info for the first selected drug
        drug_name = selected[0]
        
        # Get drug info
        drug_row = drugs_df[drugs_df['generic_name'] == drug_name]
        
        if len(drug_row) == 0:
            return ui.div("Drug information not found.")
        
        drug_data = drug_row.iloc[0]
        
        # Get detailed info from drug_info_df
        info_row = drug_info_df[drug_info_df['generic_name'] == drug_name]
        
        if len(info_row) == 0:
            # Basic info only
            return ui.div(
                {"class": "drug-info-panel"},
                ui.h4(f"💊 {drug_name}", style="margin-top: 0; color: #667eea;"),
                ui.p(f"Brand names: {drug_data.get('brand_names', 'N/A')}"),
                ui.p(f"Category: {drug_data.get('category', 'N/A')}"),
                ui.p(f"RxCUI: {drug_data.get('rxcui', 'N/A')}"),
                ui.hr(),
                ui.p(
                    "Detailed information not available from FDA database.",
                    style="font-style: italic; color: #6c757d;"
                )
            )
        
        info = info_row.iloc[0]
        
        # Helper function to safely get and truncate text
        def safe_text(value):
            """Safely handle text fields that might be NaN or float."""
            if pd.isna(value):
                return 'Information not available from FDA database.'
            
            text = str(value)
            
            if text == 'nan' or text == 'Information not available from FDA database.':
                return 'Information not available from FDA database.'
            
            return text
        
        # Build info panel
        return ui.div(
            {"class": "drug-info-panel"},
            
            # Header
            ui.h4(f"💊 {drug_name}", style="margin-top: 0; color: #667eea;"),
            
            # Basic info
            ui.div(
                ui.strong("Brand names: "),
                str(drug_data.get('brand_names', 'N/A'))
            ),
            ui.div(
                ui.strong("Category: "),
                str(drug_data.get('category', 'N/A')),
                style="margin-top: 5px;"
            ),
            ui.div(
                ui.strong("RxCUI: "),
                str(drug_data.get('rxcui', 'N/A')),
                style="margin-top: 5px; margin-bottom: 15px;"
            ),
            
            # Indications
            ui.div(
                {"class": "section-header"},
                "📋 Indications"
            ),
            ui.p(
                safe_text(info.get('indications', 'Information not available')),
                style="font-size: 14px; line-height: 1.5;"
            ),
            
            # Warnings
            ui.div(
                {"class": "section-header"},
                "⚠️ Warnings"
            ),
            ui.p(
                safe_text(info.get('warnings', 'Information not available')),
                style="font-size: 14px; line-height: 1.5;"
            ),
            
            # Contraindications
            ui.div(
                {"class": "section-header"},
                "🚫 Contraindications"
            ),
            ui.p(
                safe_text(info.get('contraindications', 'Information not available')),
                style="font-size: 14px; line-height: 1.5;"
            )
        )
    
    @reactive.Effect
    @reactive.event(input.clear_all)
    def _():
        """Clear all selected drugs."""
        ui.update_selectize("selected_drugs", selected=[])

    # ========================================================================
    # TAB 2 SERVER LOGIC (Network Visualizer)
    # ========================================================================
    
    @reactive.Calc
    def filtered_network_data():
        """Get network data filtered by center drug and depth"""
        center = input.center_drug()
        
        if not center:
            # Show full network
            return {
                'nodes': network_data['nodes'],
                'edges': network_data['edges']
            }
        
        # Filter by depth
        depth = input.network_depth()
        
        # Find all drugs within depth from center
        visited = {center}
        current_level = {center}
        
        for _ in range(depth):
            next_level = set()
            for drug in current_level:
                # Find interactions involving this drug
                related = interactions_df[
                    (interactions_df['drug_a_name'] == drug) |
                    (interactions_df['drug_b_name'] == drug)
                ]
                
                for _, row in related.iterrows():
                    if row['drug_a_name'] not in visited:
                        next_level.add(row['drug_a_name'])
                    if row['drug_b_name'] not in visited:
                        next_level.add(row['drug_b_name'])
            
            visited.update(next_level)
            current_level = next_level
        
        # Filter nodes and edges
        filtered_nodes = [n for n in network_data['nodes'] if n['id'] in visited]
        filtered_edges = [e for e in network_data['edges'] 
                         if e['from'] in visited and e['to'] in visited]
        
        return {'nodes': filtered_nodes, 'edges': filtered_edges}
    
    @reactive.Effect
    def _():
        """Initialize network visualization"""
        network = filtered_network_data()
        
        # Prepare nodes with colors
        nodes = network['nodes'].copy()
        
        if input.color_by() == "severity":
            # Color nodes by their most severe interaction
            for node in nodes:
                drug_interactions = interactions_df[
                    (interactions_df['drug_a_name'] == node['id']) |
                    (interactions_df['drug_b_name'] == node['id'])
                ]
                if len(drug_interactions) > 0:
                    severities = drug_interactions['severity_clean'].value_counts()
                    if 'High' in severities:
                        node['color'] = '#E74C3C'
                    elif 'Medium' in severities:
                        node['color'] = '#F39C12'
                    else:
                        node['color'] = '#27AE60'
                else:
                    node['color'] = '#95a5a6'
        else:
            # Color by category
            category_colors = {
                'Anticoagulant': '#e74c3c',
                'NSAID': '#f39c12',
                'Beta Blocker': '#3498db',
                'SSRI': '#9b59b6',
                'ACE Inhibitor': '#1abc9c',
                'Statin': '#e67e22',
                'PPI': '#34495e',
                'Benzodiazepine': '#16a085',
                'Diuretic': '#27ae60',
                'Calcium Channel Blocker': '#2980b9',
                'Antibiotic': '#8e44ad'
            }
            for node in nodes:
                node['color'] = category_colors.get(node.get('group', ''), '#95a5a6')
        
        # Show/hide labels
        for node in nodes:
            if not input.show_labels():
                node['font'] = {'size': 0}
        
        nodes_json = json.dumps(nodes)
        edges_json = json.dumps(network['edges'])
        
        # Initialize or update network
        ui.insert_ui(
            ui.HTML(f"""
                <script>
                setTimeout(function() {{
                    if (typeof network === 'undefined' || network === null) {{
                        initNetwork({nodes_json}, {edges_json});
                    }} else {{
                        updateNetwork({nodes_json}, {edges_json});
                    }}
                }}, 100);
                </script>
            """),
            selector="body",
            where="beforeEnd"
        )
    
    @output
    @render.ui
    def node_or_edge_details():
        """Show details when node or edge is clicked"""
        
        # Check if node selected
        selected_node = input.selected_node()
        selected_edge = input.selected_edge()
        
        if selected_node:
            # Show drug details
            drug_name = selected_node
            
            # Get side effects
            drug_side_effects = side_effects_df[side_effects_df['drug_name'] == drug_name]
            
            common = drug_side_effects[drug_side_effects['severity'] == 'Common']['side_effect'].tolist()
            serious = drug_side_effects[drug_side_effects['severity'] == 'Serious']['side_effect'].tolist()
            
            # Get interactions count
            drug_interactions = interactions_df[
                (interactions_df['drug_a_name'] == drug_name) |
                (interactions_df['drug_b_name'] == drug_name)
            ]
            
            return ui.div(
                {"class": "drug-info-panel"},
                ui.h4(f"💊 {drug_name}", style="margin-top: 0; color: #667eea;"),
                
                ui.div(
                    {"class": "section-header"},
                    f"Interactions ({len(drug_interactions)})"
                ),
                ui.p(
                    f"This drug has {len(drug_interactions)} known interactions in this dataset.",
                    style="font-size: 14px;"
                ),
                
                ui.div(
                    {"class": "section-header"},
                    # "💊 Common Side Effects"
                    "Common Side Effects"
                ),
                ui.div(
                    [ui.span(effect, class_="side-effect-badge") for effect in common[:10]] if common else 
                    [ui.p("No common side effects data available", style="font-style: italic; color: #6c757d;")]
                ),
                
                ui.div(
                    {"class": "section-header"},
                    # "⚠️ Serious Side Effects"
                    "Serious Side Effects"
                ),
                ui.div(
                    [ui.span(effect, class_="side-effect-badge", style="background: #fee; color: #c00;") 
                     for effect in serious[:10]] if serious else 
                    [ui.p("No serious side effects data available", style="font-style: italic; color: #6c757d;")]
                )
            )
        
        elif selected_edge:
            # Show interaction details
            parts = selected_edge.split('|||')
            if len(parts) == 2:
                drug_a, drug_b = parts
                
                # Find interaction
                interaction = interactions_df[
                    ((interactions_df['drug_a_name'] == drug_a) & (interactions_df['drug_b_name'] == drug_b)) |
                    ((interactions_df['drug_a_name'] == drug_b) & (interactions_df['drug_b_name'] == drug_a))
                ]
                
                if len(interaction) > 0:
                    inter = interaction.iloc[0]
                    severity_colors = {'High': '#E74C3C', 'Medium': '#F39C12', 'Low': '#27AE60'}
                    severity_color = severity_colors[inter['severity_clean']]
                    
                    return ui.div(
                        {"class": "interaction-detail-box"},
                        ui.h4(
                            f"⚠️ {inter['severity_clean'].upper()} RISK",
                            style=f"color: {severity_color}; margin-top: 0;"
                        ),
                        ui.div(
                            ui.strong("Drugs: "),
                            f"{inter['drug_a_name']} + {inter['drug_b_name']}",
                            style="margin-bottom: 15px;"
                        ),
                        ui.div(
                            {"class": "section-header"},
                            "Description"
                        ),
                        ui.p(inter['description'], style="line-height: 1.6;")
                    )
        
        # Default
        return ui.div(
            {"class": "network-info-panel"},
            ui.p(
                "Click a node to see side effects\nClick an edge to see interaction details",
                style="font-style: italic; color: #6c757d; text-align: center; padding: 40px; white-space: pre-line;"
            )
        )
    
    @reactive.Effect
    @reactive.event(input.reset_network)
    def _():
        """Reset network view"""
        ui.update_selectize("center_drug", selected="")
        ui.update_slider("network_depth", value=2)

    # ========================================================================
    # TAB 3 SERVER LOGIC (Patient Analyzer)
    # ========================================================================
    
    @reactive.Calc
    def uploaded_patient_data():
        """Process uploaded CSV file"""
        file_info = input.patient_csv()
        
        if file_info is None or len(file_info) == 0:
            return None
        
        # Read CSV
        try:
            df = pd.read_csv(file_info[0]["datapath"])
            
            # Check for drug_name column
            if 'drug_name' not in df.columns:
                return {"error": "CSV must contain 'drug_name' column"}
            
            return df
        except Exception as e:
            return {"error": f"Error reading CSV: {str(e)}"}
    
    @reactive.Calc
    def matched_medications():
        """Match uploaded drugs to database using fuzzy matching"""
        patient_data = uploaded_patient_data()
        
        if patient_data is None or isinstance(patient_data, dict):
            return None
        
        # Fuzzy matching
        matched = []
        unmatched = []
        
        for idx, row in patient_data.iterrows():
            drug_input = str(row['drug_name']).strip().lower()
            
            # Try exact match first
            exact_match = None
            for item in search_index:
                if drug_input in [term.lower() for term in item['search_terms']]:
                    exact_match = item
                    break
            
            if exact_match:
                matched.append({
                    'input_name': row['drug_name'],
                    'matched_name': exact_match['generic_name'],
                    'rxcui': exact_match['rxcui'],
                    'category': exact_match['category'],
                    'match_type': 'Exact'
                })
            else:
                # Try fuzzy match
                best_match = None
                best_score = 0
                
                for item in search_index:
                    for term in item['search_terms']:
                        # Simple substring matching
                        if drug_input in term.lower() or term.lower() in drug_input:
                            score = len(drug_input) / max(len(term), len(drug_input))
                            if score > best_score:
                                best_score = score
                                best_match = item
                
                if best_match and best_score > 0.5:
                    matched.append({
                        'input_name': row['drug_name'],
                        'matched_name': best_match['generic_name'],
                        'rxcui': best_match['rxcui'],
                        'category': best_match['category'],
                        'match_type': 'Fuzzy'
                    })
                else:
                    unmatched.append({
                        'input_name': row['drug_name'],
                        'suggestion': 'Not found in database'
                    })
        
        return {
            'matched': pd.DataFrame(matched) if matched else pd.DataFrame(),
            'unmatched': pd.DataFrame(unmatched) if unmatched else pd.DataFrame()
        }
    
    @reactive.Calc
    def patient_interactions():
        """Find all interactions among matched medications"""
        matched_data = matched_medications()
        
        if matched_data is None or matched_data['matched'].empty:
            return pd.DataFrame()
        
        matched_drugs = matched_data['matched']['matched_name'].tolist()
        
        # Find interactions
        patient_inters = interactions_df[
            interactions_df['drug_a_name'].isin(matched_drugs) &
            interactions_df['drug_b_name'].isin(matched_drugs)
        ].copy()
        
        return patient_inters
    
    @output
    @render.ui
    def upload_status():
        """Show upload status and matching results"""
        patient_data = uploaded_patient_data()
        
        if patient_data is None:
            return ui.div(
                {"class": "network-info-panel"},
                ui.h4("📋 Instructions", style="margin-top: 0;"),
                ui.p("1. Upload a CSV file with patient medications"),
                ui.p("2. CSV must have a 'drug_name' column"),
                ui.p("3. We'll match drugs to our database and analyze interactions"),
                ui.hr(),
                ui.p("Don't have a CSV? Download our sample file to get started!", 
                     style="font-style: italic; color: #667eea;")
            )
        
        if isinstance(patient_data, dict) and 'error' in patient_data:
            return ui.div(
                {"class": "interaction-detail-box", "style": "border-left: 4px solid #E74C3C;"},
                ui.h4("❌ Error", style="color: #E74C3C; margin-top: 0;"),
                ui.p(patient_data['error'])
            )
        
        matched_data = matched_medications()
        
        matched_count = len(matched_data['matched']) if not matched_data['matched'].empty else 0
        unmatched_count = len(matched_data['unmatched']) if not matched_data['unmatched'].empty else 0
        total_count = matched_count + unmatched_count
        
        interactions = patient_interactions()
        interaction_count = len(interactions)
        
        return ui.div(
            {"class": "network-info-panel"},
            ui.h4("Upload Successful", style="margin-top: 0; color: #27AE60;"),
            ui.p(f"• Total medications: {total_count}"),
            ui.p(f"• Matched: {matched_count}"),
            ui.p(f"• Not matched: {unmatched_count}"),
            ui.p(f"• Interactions found: {interaction_count}", 
                 style="font-weight: bold; color: #E74C3C;" if interaction_count > 0 else "")
        )
    
    @output
    @render.data_frame
    def matched_medications_table():
        """Display matched medications"""
        matched_data = matched_medications()
        
        if matched_data is None or matched_data['matched'].empty:
            return pd.DataFrame()
        
        display_df = matched_data['matched'][['input_name', 'matched_name', 'category', 'match_type']].copy()
        display_df.columns = ['Input Name', 'Matched Drug', 'Category', 'Match Type']
        
        return render.DataGrid(
            display_df,
            width="100%",
            height="300px"
        )
    
    @output
    @render.ui
    def high_risk_interactions():
        """Display high risk interactions"""
        interactions = patient_interactions()
        
        if interactions.empty:
            return ui.p("None", style="color: #6c757d; font-style: italic;")
        
        high_risk = interactions[interactions['severity_clean'] == 'High']
        
        if high_risk.empty:
            return ui.p("None", style="color: #6c757d; font-style: italic;")
        
        return ui.div(
            [ui.p(f"• {row['drug_a_name']} + {row['drug_b_name']}", 
                  style="margin: 5px 0; font-size: 14px;") 
             for _, row in high_risk.iterrows()]
        )
    
    @output
    @render.ui
    def medium_risk_interactions():
        """Display medium risk interactions"""
        interactions = patient_interactions()
        
        if interactions.empty:
            return ui.p("None", style="color: #6c757d; font-style: italic;")
        
        medium_risk = interactions[interactions['severity_clean'] == 'Medium']
        
        if medium_risk.empty:
            return ui.p("None", style="color: #6c757d; font-style: italic;")
        
        return ui.div(
            [ui.p(f"• {row['drug_a_name']} + {row['drug_b_name']}", 
                  style="margin: 5px 0; font-size: 14px;") 
             for _, row in medium_risk.iterrows()]
        )
    
    @output
    @render.ui
    def low_risk_interactions():
        """Display low risk interactions"""
        interactions = patient_interactions()
        
        if interactions.empty:
            return ui.p("None", style="color: #6c757d; font-style: italic;")
        
        low_risk = interactions[interactions['severity_clean'] == 'Low']
        
        if low_risk.empty:
            return ui.p("None", style="color: #6c757d; font-style: italic;")
        
        return ui.div(
            [ui.p(f"• {row['drug_a_name']} + {row['drug_b_name']}", 
                  style="margin: 5px 0; font-size: 14px;") 
             for _, row in low_risk.iterrows()]
        )
    
    @output
    @render.ui
    def all_interactions_list():
        """Display all interactions with details"""
        interactions = patient_interactions()
        
        if interactions.empty:
            return ui.p(
                "No interactions detected between matched medications",
                style="color: #6c757d; font-style: italic; text-align: center; padding: 40px;"
            )
        
        # Sort by severity
        severity_order = {'High': 0, 'Medium': 1, 'Low': 2}
        interactions['severity_order'] = interactions['severity_clean'].map(severity_order)
        interactions = interactions.sort_values('severity_order')
        
        interaction_items = []
        for idx, row in interactions.iterrows():
            severity_colors = {'High': '#E74C3C', 'Medium': '#F39C12', 'Low': '#27AE60'}
            color = severity_colors[row['severity_clean']]
            
            interaction_items.append(
                ui.div(
                    {"class": "interaction-detail-box", "style": f"margin-bottom: 15px; border-left: 4px solid {color};"},
                    ui.h5(
                        f"{row['drug_a_name']} + {row['drug_b_name']}",
                        style="margin-top: 0;"
                    ),
                    ui.p(
                        ui.span(row['severity_clean'], class_=f"severity-badge severity-{row['severity_clean'].lower()}"),
                        style="margin-bottom: 10px;"
                    ),
                    ui.p(row['description'], style="font-size: 14px; line-height: 1.5;")
                )
            )
        
        return ui.div(*interaction_items)
    
    @output
    @render.download(filename="sample_patient_medications.csv")
    def download_sample():
        """Generate sample CSV file"""
        sample_data = pd.DataFrame({
            'drug_name': [
                'Warfarin',
                'Aspirin',
                'Lisinopril',
                'Metoprolol',
                'Atorvastatin'
            ]
        })
        
        # Convert to CSV string
        csv_string = sample_data.to_csv(index=False)
        
        # Return as bytes
        return io.BytesIO(csv_string.encode())
    
    @output
    @render.download(filename="patient_interaction_report.txt")
    def download_report():
        """Generate text report of interactions"""
        matched_data = matched_medications()
        interactions = patient_interactions()
        
        if matched_data is None:
            report = "No patient data uploaded.\n"
        else:
            matched_count = len(matched_data['matched']) if not matched_data['matched'].empty else 0
            
            report = f"""
            ================================================================
                        PATIENT MEDICATION INTERACTION REPORT               
            ================================================================

            Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

            SUMMARY
            ─────────────────────────────────────────────────────────────
            Total Medications Matched: {matched_count}
            Total Interactions Found: {len(interactions)}

            """
            
            if not interactions.empty:
                # High risk
                high_risk = interactions[interactions['severity_clean'] == 'High']
                report += f"\n🔴 HIGH RISK INTERACTIONS ({len(high_risk)})\n"
                report += "─" * 60 + "\n"
                for _, row in high_risk.iterrows():
                    report += f"\n{row['drug_a_name']} + {row['drug_b_name']}\n"
                    report += f"  {row['description']}\n"
                
                # Medium risk
                medium_risk = interactions[interactions['severity_clean'] == 'Medium']
                report += f"\n\n🟡 MEDIUM RISK INTERACTIONS ({len(medium_risk)})\n"
                report += "─" * 60 + "\n"
                for _, row in medium_risk.iterrows():
                    report += f"\n{row['drug_a_name']} + {row['drug_b_name']}\n"
                    report += f"  {row['description']}\n"
                
                # Low risk
                low_risk = interactions[interactions['severity_clean'] == 'Low']
                report += f"\n\n🟢 LOW RISK INTERACTIONS ({len(low_risk)})\n"
                report += "─" * 60 + "\n"
                for _, row in low_risk.iterrows():
                    report += f"\n{row['drug_a_name']} + {row['drug_b_name']}\n"
                    report += f"  {row['description']}\n"
        
        return io.BytesIO(report.encode())

app = App(app_ui, server)
