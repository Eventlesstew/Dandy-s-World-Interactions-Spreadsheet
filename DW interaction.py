from bs4 import BeautifulSoup
import cloudscraper
import csv

scraper = cloudscraper.create_scraper()  # Returns a requests.Session

category_url = "https://dandys-world-robloxhorror.fandom.com/wiki/Category:Toons"
def get_toons():
    result = []
    category_page = scraper.get(category_url)
    category_soup = BeautifulSoup(category_page.text, 'html.parser')

    t = category_soup.find('table', {'id':'tpt-1'})
    t_body = t.find('tbody')
    t_rows = t_body.find_all('tr')
    for i in t_rows:
        name_cells = i.find_all('td')

        if len(name_cells) >= 1:
            name_cell = name_cells[1]
            name = name_cell.find('a')
            result.append(name.text)
    
    return result

def get_interactions(toons):
    result = [['name']]
    dictionary = {}
    for i in range(0, len(toons)):
        dictionary[toons[i]] = i
        result[0].append(toons[i])
        newrow = [toons[i]]
        for n in toons:
            newrow.append("")
        result.append(newrow)
    
    for c in toons:
        print("Loading " + c)
        url = "https://dandys-world-robloxhorror.fandom.com/wiki/Template:" + c + "_Dialogues"

        page = scraper.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        tables = soup.find_all('table', {'class': 'article-table'})
        for t in tables: # This ensures that dialogue from Dandy and Dyle are not missed
            table = t.find('tbody')
            rows = table.find_all('tr')

            interaction = [c, '', ""]
            nextfloor = False
            for i in rows:
                cells = i.find_all('td')

                if len(cells) == 0:
                    msg = i.find('th')
                    nextfloor = (msg.text.startswith("Descending"))
                elif len(cells) == 1:
                    if nextfloor:
                        text_ref = cells[0].find('span')
                        if text_ref:
                            try: 
                                key = dictionary[c]+1
                                
                                if result[key][key] != "":
                                    result[key][key] += "\n\n"
                                
                                text = text_ref.text

                                if c == "Blot":
                                    text += " (" + text_ref.text[::-1] + ")"
                                result[key][key] += c + ": " + text
                                
                            except KeyError:
                                pass
                else:
                    if len(cells) >= 3:
                        name_ref = cells[len(cells) - 3].find('a')
                        name = ""
                        if name_ref:
                            name = name_ref.text
                            try:
                                key1 = dictionary[interaction[0]]+1
                                key2 = dictionary[interaction[1]]+1
                                if result[key1][key2] != "":
                                    result[key1][key2] += "\n\n"
                                result[key1][key2] += interaction[2]
                            except KeyError:
                                pass
                        
                        name.strip()
                        interaction[1] = name
                        interaction[2] = ""
                
                    if len(cells) >= 2:
                        name_node = cells[len(cells) - 2].find('a')
                        text_ref = cells[len(cells) - 1].find('span')

                        if name_node and text_ref:    
                            name_ref = name_node.get("href")
                            n: str = ""
                            for s in name_ref[::-1]: 
                                if s == "/":
                                    break
                                else:
                                    n += s
                            
                            n.strip()
                            name = n[::-1]

                            text = text_ref.text

                            # This gives Blot his reversed text translation.
                            if name == "Blot":
                                text += " (" + text_ref.text[::-1] + ")"
                            
                            if interaction[2] != "":
                                interaction[2] += "\n"

                            name.replace("%26", "&")
                            name.replace("_", " ")
                            interaction[2] += name + ": " + text
    
    return result

toons = get_toons()
data = get_interactions(toons)

csv_file_path = 'interactions.csv'

with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerows(data)

print(f"CSV file '{csv_file_path}' created successfully.")