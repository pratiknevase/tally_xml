import os
import pandas as pd
from flask import Flask, jsonify
import xml.etree.ElementTree as ET

app = Flask(__name__)

INPUT_FILE_PATH = os.path.dirname(os.path.realpath(__file__))+'/Input.xml'
OUTPUT_FILE_PATH = os.path.dirname(os.path.realpath(__file__))+'/Output.xlsx'

# Function to extract voucher details
def extract_voucher_details(voucher):
    try:
        voucher_details = {
            "Transaction Type": "Parent",
            "Vch No.": voucher.find("VOUCHERNUMBER").text,
            "Ref No.": "NA",
            "Ref Type": "NA",
            "Ref Date": "NA",
            "Debtor and Particulars": voucher.find("PARTYLEDGERNAME").text,
            "Ref Amount": "NA",
            "Amount": "0",  # Initialize to 0; will sum child entries
            "Amount Verified": ""
        }
        
        child_transactions = []
        ref_amount_total = 0
        for ledger_entry in voucher.findall("ALLLEDGERENTRIES.LIST"):
            try:
                ledger_name = ledger_entry.find("LEDGERNAME").text
                amount = ledger_entry.find("AMOUNT").text
                ref_amount_total += float(amount)
                
                # Determine if this is a child transaction
                is_child = ledger_entry.find("BILLALLOCATIONS.LIST") is not None
                transaction_type = "Child" if is_child else "Other"
                
                child_details = {
                    "Transaction Type": transaction_type,
                    "Vch No.": voucher_details["Vch No."],
                    "Ref No.": ledger_entry.find("BILLALLOCATIONS.LIST/NAME").text if is_child else "NA",
                    "Ref Type": ledger_entry.find("BILLALLOCATIONS.LIST/BILLTYPE").text if is_child else "NA",
                    "Ref Date": "NA",  # Assuming date logic implementation
                    "Debtor and Particulars": ledger_name,
                    "Ref Amount": amount if is_child else "NA",
                    "Amount": amount if not is_child else "NA",
                    "Amount Verified": ""
                }
                child_transactions.append(child_details)
            except Exception as e:
                print(str(e))
        
        # Update Parent Amount and Amount Verified
        voucher_details["Amount"] = str(ref_amount_total)
        voucher_details["Amount Verified"] = "Yes" if ref_amount_total == float(voucher_details["Amount"]) else "No"
        return [voucher_details] + child_transactions
    except Exception as e:
        print(e)
        return None

@app.route('/convert', methods=['GET'])
def convert():
    # Load and parse the XML file
    tree = ET.parse(INPUT_FILE_PATH)
    root = tree.getroot()

    # Extract details for each voucher
    transactions = []
    for voucher in root.findall(".//VOUCHER"):
        voucher_details = extract_voucher_details(voucher)
        if voucher_details:
            transactions.extend(voucher_details)

    # Convert to DataFrame
    df = pd.DataFrame(transactions)

    # Save the dataframe as output xlsx file
    df.to_excel(OUTPUT_FILE_PATH, index=False, sheet_name='Sheet1')

    return jsonify({"msg":"Output file generated","filepath":OUTPUT_FILE_PATH})

if __name__ == '__main__':
    app.run(debug=True)
