import os
import re
import json
from bs4 import BeautifulSoup

directory = "w:/download/14/htmlbak"
output_filename = "crm.json"
application = "CRM"

# Regular expression pattern to match the branch name
branch_pattern = r"<h1>(.*?)</h1>"

# Regular expression pattern to match the table content
table_pattern = r"<table>(.*?)</table>"

# Regular expression pattern to match the description
description_pattern = r'<meta name="Description" content="Application: Visma (.*?)".*>'

results = {}

for filename in os.listdir(directory):
    if filename.endswith(".htm"):
        with open(os.path.join(directory, filename), "r", encoding="utf-8") as f:
            content = f.read()
            # Find the description
            description_match = re.search(description_pattern, content)
            if description_match:
                description_name = description_match.group(1)
                if description_name == application:
                    # Find the branch name
                    branch_match = re.search(branch_pattern, content)
                    if branch_match:
                        branch_name = branch_match.group(1)
                        # Find the table content
                        table_match = re.search(table_pattern, content, re.DOTALL)
                        if table_match:
                            table_content = table_match.group(1)
                            # Parse the HTML table using BeautifulSoup
                            soup = BeautifulSoup(table_content, "html.parser")
                            table = []
                            # Extract the column headers from the first row
                            headers = [th.text.strip() for th in soup.find("tr").find_all("th")]
                            # Extract the data from the remaining rows
                            for tr in soup.find_all("tr")[1:]:
                                row = {}
                                tds = tr.find_all("td")
                                for i in range(min(len(headers), len(tds))):
                                    # Add a check to make sure that the headers list has enough items
                                    if i < len(headers):
                                        row[headers[i]] = tds[i].text.strip()
                                table.append(row)
                            # Add the branch name and table data to the results dictionary
                            results[branch_name] = table

# Write the JSON data to the output file
with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4)
