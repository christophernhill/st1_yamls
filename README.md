# RFP System YAML Analysis Tool

This tool processes YAML files containing RFP (Request for Proposal) system specifications and generates summary reports with GPU counts and calculations.

## Program Files

- `read_yamls.py`: Main Python script that processes YAML files and generates CSV output
- `run_tgp_range.sh`: Bash script to run the analysis with different TGP values

## Input Files

The program expects the following YAML files in the same directory:
- lenovo.yaml
- cambridge.yaml
- ibm.yaml
- markiii.yaml
- penguin.yaml

## Output Format

The program generates CSV files with the following columns:

### Basic Information
- `rfp_no`: RFP identification number
- `lead_org`: Leading organization name
- `total_price`: Total price of the system
- `TGP_Info`: Information about the TGP value used for calculations

### GPU Configuration Columns
- `B`: B200 GPU counts (format: "original,adjusted")
  - First number: Original count (gpu_count × item_count)
  - Second number: Alpha-adjusted count
- `H`: H200 GPU counts (format: "original,adjusted")
  - First number: Original count (gpu_count × item_count)
  - Second number: Alpha-adjusted count
- `R`: RTX6000 GPU counts (format: "original,adjusted")
  - First number: Original count (gpu_count × item_count)
  - Second number: Alpha-adjusted count
- `L`: L40S GPU counts (format: "original,adjusted")
  - First number: Original count (gpu_count × item_count)
  - Second number: Alpha-adjusted count
- `T`: Total GPU counts (format: "original,adjusted")
  - First number: Sum of original counts (B + H + R + L)
  - Second number: Sum of adjusted counts

### System Configuration
- `t1`: Tier 1 configuration details
- `t2`: Tier 2 configuration details
- `hn`: Head node configuration
- `cn`: Compute node configuration
- `hs`: High-speed storage configuration
- `cs`: Capacity storage configuration
- `sn`: Storage network configuration
- `sstack`: Storage stack configuration

## Running the Analysis

### Single TGP Value
```bash
python read_yamls.py --tgp 1.7
```
This generates a file named `summary_ST1-1p7.csv`

### Multiple TGP Values
```bash
./run_tgp_range.sh
```
This runs the analysis for TGP values from 1.5 to 2.1 in steps of 0.1 and creates:
- Individual files for each TGP value
- A combined file named `summary_ST1-TGP1p5-2p1-step0p1.csv`

## Understanding the Output

### Comma-Separated Numbers
In columns B, H, R, L, and T, the comma-separated numbers represent:
- First number: Original count based on the system specification
- Second number: Alpha-adjusted count based on the TGP value

### Alpha Calculation
The alpha value is calculated as:
```
alpha = (1 / (total_price / TGP)) * 100
```
This alpha value is then used to adjust the GPU counts in the second number of each comma-separated pair. 

## CSV and YAML Pretty-Print HTML Viewers

### csv_to_pp.py

This script generates a browsable HTML page with tabs, each showing a CSV file as a styled, scrollable table.

- **Input:** One or more CSV files (e.g., `file1.csv file2.csv`)
- **Output:** A single HTML file named `browse_csvs.html` with a tab for each CSV file
- **How to run:**
  ```bash
  python csv_to_pp.py file1.csv file2.csv
  ```
- **How to view:** Open `browse_csvs.html` in any web browser. Each tab displays the contents of one CSV file as a table. The table is responsive and stretches to the full width of the browser window.

### yaml_to_pp.py

This script generates a browsable HTML page with tabs, each showing a YAML file in a collapsible, color-highlighted tree view.

- **Input:** One or more YAML files (e.g., `file1.yaml file2.yaml`)
- **Output:** A single HTML file named `browse_yamls.html` with a tab for each YAML file
- **How to run:**
  ```bash
  python yaml_to_pp.py file1.yaml file2.yaml
  ```
- **How to view:** Open `browse_yamls.html` in any web browser. Each tab displays the contents of one YAML file in a collapsible, color-coded format for easy browsing. 