"""
M365 License Report Generator
-----------------------------
Fetches users and their assigned Microsoft 365 licenses
and exports the data into a CSV or JSON report.
"""

import csv
import json
import argparse
from msgraph.core import GraphClient
from azure.identity import DeviceCodeCredential

# 🔑 Auth Setup (Device Code for interactive login)
def get_graph_client(tenant_id):
    credential = DeviceCodeCredential(client_id="04f0c124-f2bc-4f67-8f80-9e5b0a639777", tenant_id=tenant_id)
    return GraphClient(credential=credential)

# 📊 Get users and licenses
def fetch_license_report(client):
    users = client.get("/users?$select=id,displayName,userPrincipalName,assignedLicenses")
    report = []
    for user in users.json().get("value", []):
        licenses = [lic["skuId"] for lic in user.get("assignedLicenses", [])]
        report.append({
            "UserPrincipalName": user["userPrincipalName"],
            "DisplayName": user.get("displayName", ""),
            "Licenses": ", ".join(licenses) if licenses else "None"
        })
    return report

# 💾 Export to CSV or JSON
def export_report(data, output, fmt="csv"):
    if fmt == "csv":
        with open(output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
    else:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    print(f"Report saved to {output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="M365 License Report Generator")
    parser.add_argument("--tenant", required=True, help="Tenant ID")
    parser.add_argument("--output", default="m365_license_report.csv", help="Output file path")
    parser.add_argument("--format", choices=["csv", "json"], default="csv", help="Output format")
    args = parser.parse_args()

    client = get_graph_client(args.tenant)
    report = fetch_license_report(client)
    export_report(report, args.output, args.format)
