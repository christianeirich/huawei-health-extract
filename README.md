# Huawei Health to Health Connect

Export your weight and body-fat data from Huawei Health JSON and sync it into Android’s Health Connect via Tasker.

---

## Current Features

- **Per-user export** of weight (kg) and body-fat (%)
- **Duplicate filtering** based on user ID + timestamp

---

## Prerequisites

- **Python 3.7+**
- **Tasker** (latest version)
- [TaskerHealthConnect](https://github.com/RafhaanShah/TaskerHealthConnect) plugin
- Health Connect app installed and granted TaskerHealthConnect read/write access

---

## 1. Obtain Your Huawei Health Data

Huawei Health lets you request a full data export, including your raw JSON:

1. In [**Huawei Privacy Center**](https://privacy.consumer.huawei.com/tool) click on **Request Your Data**
2. Select **Health** and submit your request.
3. After some hours or days, download the ZIP from the email
4. Extract the JSON files from the folder "Health detail data & description" into a folder.

For a detailed walkthrough, see the HiTrava converter guide:
https://cthru.hopto.org/hitrava-web/convert/

---

## 2. Generate CSV Files

1. **Clone this repository** and enter its directory:
   ```bash
   git clone https://github.com/yourusername/huawei-health-to-health-connect.git
   cd huawei-health-to-health-connect
    ```

2. **Run the exporter** against your JSON folder. By default, CSVs are written to an `out/` subfolder:

   ```bash
   python3 main.py /path/to/extracted/json
   ```
3. You’ll find one CSV per user in `out/`, each containing:

   | timestamp (Unix epoch) | weight\_kg | fat\_pct |
   | ------------------------------: | ---------: | -------: |
   |                   1700000000000 |      79.45 |     21.3 |
   |                               … |            |          |

---

## 3. Syncing via Tasker

1. **Copy** your CSV file to your phone to any folder.
2. **Import** the included Tasker task (`Tasker-CSV-to-HealthConnect.xml`):
   * Copy it to your phone to any folder.
   * In Tasker, go to **Profiles → Import** and select the XML file.
3. **Configure** the profile:
   * Change **`%csv`** to the path of your CSV file.
4. **Save** the profile and then run it once. Tasker will:
   1. Read each new line
   2. Split it into `timestamp`, `weight_kg`, `fat_pct`
   3. Call the TaskerHealthConnect plugin to insert both data points into Health Connect
4. **Verify** in the Health Connect app that your weight and body-fat entries appear.

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.