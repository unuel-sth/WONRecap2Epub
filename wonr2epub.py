from bs4 import BeautifulSoup
import requests
import argparse
import time
import pypandoc
import os

def dropdown_to_string(dorpdown):
    str_array = []
    for el in dorpdown:
        str_array.append(el.text)
    return str_array

def get_weeks(year):
    res = requests.get("https://rewinder.pro/", params={"year": year}, headers={"User-Agent": "Mozilla/5.0"})
    res.raise_for_status()
    page = BeautifulSoup(res.content, "html.parser")
    year_dropdown = page.find(id="year").find_all("option")
    years = dropdown_to_string(year_dropdown)
    if(str(year) not in years):
        raise Exception("Year " + str(year) + " does not appear in rewinder.pro")

    week_dropdown = page.find(id="week").find_all("option")
    weeks = dropdown_to_string(week_dropdown)

    return weeks

def get_entry(week):
    res = requests.get("https://rewinder.pro/", params={"week": week}, headers={"User-Agent": "Mozilla/5.0"})
    res.raise_for_status()
    page = BeautifulSoup(res.content, "html.parser")
    entry = page.find("div", class_="entries")
    date = entry.find("a")
    content = entry.find_all("li")
    not_formatted = "<h2>" + date.prettify() + "</h2><br>"
    for li in content:
        p = li.find("a")
        p.name = "p"
        for key in list(p.attrs):
            del p.attrs[key]
        not_formatted += p.prettify()
    not_formatted += "<br><br>"
    return not_formatted

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Wrestling Observer Newsletter Recap by u/daprice82 or u/SaintRidley to EPUB")
    parser.add_argument("--year", type=int , help="Year to generate EPUB from; e.g. 1991")
    args = parser.parse_args()
    html_name = str(args.year) + "_WON_Recap.html"
    epub_name = str(args.year) + "_WON_Recap.epub"
    try:
        weeks = get_weeks(args.year)
        html_file = open(html_name, "w", encoding="utf-8")
        html_file.write(f"""
            <html>
            <head>
                <meta name='title' content='{str(args.year)} Wrestling Observer Newsletter Recap'>
                <meta name='author' content='Dave Meltzer'>
            </head>
            <body>
                <h5 align="center">{str(args.year)} Wrestling Observer Newsletter Recap</h5>
                <h6 align="center">Wrestling Observer Newsletter by Dave Meltzer, recap by <a href="https://www.reddit.com/user/daprice82/">u/daprice82</a> (1991 - 2003) or <a href="https://www.reddit.com/user/SaintRidley/">u/SaintRidley</a> (1987 - 1988) </h6>
                <h6 align="center"><a href="https://rewinder.pro">rewinder.pro</a> by <a href="https://www.reddit.com/user/johnny-papercut/">u/johnny-papercut</a></h6>
                <h6 align="center">Generated using <a href="https://github.com/unuel-sth/WONRecap2Epub">WONRecap2Epub</a> by <a href="https://www.reddit.com/user/Unuel/">u/Unuel</a></h6>
                <br><br>
        """)
        for week in weeks:
            print("Getting entry " + str(week))
            html_file.write(get_entry(week))
            time.sleep(1.0)
        html_file.write("</body></html>")
        html_file.close()
        print("Generating epub...")
        pypandoc.convert_file(html_name, 'epub3', outputfile=epub_name, extra_args=['--toc', '--toc-depth=2'], sandbox=False)
        os.remove(html_name)
        print("File " + epub_name + " is ready")
    except Exception as ex:
        print("An error occured:", ex)