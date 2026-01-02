# 📅 Event Database Management System

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![SQL Server](https://img.shields.io/badge/SQL%20Server-Express-red?logo=microsoft-sql-server&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)

A Python-based event management application using **Streamlit** for the frontend and **Microsoft SQL Server** for data storage.

---

## 🛠️ Prerequisites

Before starting, ensure you have the following installed on your machine:

1.  **Microsoft SQL Server Express** (Any version)
2.  **SQL Server Management Studio (SSMS)**
3.  **Microsoft ODBC Driver (MSODBCSQL)**
4.  **Python 3.12**
    > ⚠️ **Critical Note:** Please use **Python 3.12**. Later versions of Python are currently incompatible and may break the application.

---

## ⚙️ Installation & Setup

### Phase 1: Server Configuration

#### 1. Connect and Server Setup
1.  Launch **SQL Server Management Studio (SSMS)**.
2.  If asked to sign in to Azure, click **Skip** (or "Add accounts later").
3.  In the **Connect to Server** window:
    * **Server name:** `localhost\SQLEXPRESS`
    * **Trust server certificate:** Checked ✅
4.  Click **Connect**.
5.  In the **Object Explorer** (left panel), right-click on the server node (`localhost\SQLEXPRESS`).
6.  Click **Properties** and select the **Security** page from the left menu.
7.  Under "Server authentication", select **SQL Server and Windows Authentication mode**.
8.  Click **OK**.

#### 2. Create Database and Table
1.  Click **New Query** in the toolbar.
2.  Paste your SQL script (`SQL QUERY.txt`) into the window.
3.  Click **Execute**.

### Phase 2: Create Login

1.  In **Object Explorer**, expand the **Security** folder.
2.  Right-click the **Logins** folder and select **New Login...**
3.  **Configure the General page:**
    * **Login name:** `eventdb_admin`
    * Select **SQL Server authentication**.
    * **Password:** `1234`
    * **Confirm password:** `1234`
    * Uncheck **"Enforce password policy"**.
4.  **Configure the User Mapping page (left menu):**
    * Check the box next to `EventDB` (or the specific name of your database).
    * In the bottom pane ("Database role membership"), check: `db_datareader`, `db_datawriter`, and `db_owner`.
5.  Click **OK**.

> 🛑 **IMPORTANT:** You must **Restart your PC** now for the authentication changes to take effect.

---

## 🚀 Usage

### 1. Install Python Dependencies and launch the Database Management System.
Launch VS Code, open your project folder, and open the Integrated Terminal. Run the following command:

```bash
pip install streamlit pandas pyodbc openpyxl plotly

streamlit run main.py
