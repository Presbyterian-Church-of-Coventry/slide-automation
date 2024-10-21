#!/usr/bin/env python3

import os
import re
from pypdf import PdfReader
import requests
from slides import Slides


def main(date):
    pdf_url = None
    response = requests.get(
        "https://coventrypca.church/assets/data/bulletins/index.json"
    )
    json = response.json()
    bulletins = json["data"]["bulletins"]["edges"]
    # Grab bulletin for specific date:
    for bulletin in bulletins:
        name = bulletin["node"]["title"]
        if date in name:
            pdf_url = bulletin["node"]["url"]
            break
    if not pdf_url:
        num = 2
        while not pdf_url:
            response = requests.get(
                f"https://coventrypca.church/assets/data/bulletins/{num}/index.json"
            )
            if response.status_code == 404:
                print("Can't find bulletin online!")
                return
            json = response.json()
            bulletins = json["data"]["bulletins"]["edges"]
            # Grab bulletin for specific date:
            for bulletin in bulletins:
                name = bulletin["node"]["title"]
                if date in name:
                    pdf_url = bulletin["node"]["url"]
                    break
            num += 1
    # Download the PDF file from Google Drive
    file_id = pdf_url.split('/')[-2]
    download_url = f"https://drive.google.com/uc?id={file_id}"
    response = requests.get(download_url)
    pdf_path = f"{file_id}.pdf"
    with open(pdf_path, "wb") as file:
        file.write(response.content)
    PDFFile = open(pdf_path, "rb")
    PDF = PdfReader(PDFFile)
    links = []
    page = PDF.pages[0]
    pageObject = page.get_object()
    if "/Annots" in pageObject.keys():
        annotations = pageObject["/Annots"]
        for annotation in annotations:
            object = annotation.get_object()
            if "/URI" in object["/A"].keys():
                link = object["/A"]["/URI"]
                if "hymnary.org" in link or "esv.org" in link:
                    if not "/page/" in link:
                        if link.split("/")[-1]:
                            links.append(link.split("/")[-1])
                        else:
                            links.append(link.split("/")[-2])
                else:
                    print("Unrecognized link in the bulletin, you may need to create slides for this content manually")
    os.remove(pdf_path)
    print(f"Generating slides for {date}...")
    for link in links:
        if link != "731":
            Slides(link)
    dir = os.environ["DIRECTORY"]
    print(f"Slides saved to /{dir}!")


if __name__ == "__main__":
    date = None
    while not date:
        ans = input("Please enter a date in YYYY-MM-DD format: ")
        resp = re.match("\d{4}-\d{2}-\d{2}", ans)
        if resp:
            date = resp[0]
        else:
            print()
            print("Please enter a valid date!")
    main(date)
