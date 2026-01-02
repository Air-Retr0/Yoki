import requests
from bs4 import BeautifulSoup
import json
import time

class YorkGraduateProgramScraper:
    def __init__(self):
        self.directory_url = "https://futurestudents.yorku.ca/graduate/programs"
        self.programs = []
        self.output_file = "docs/data/programs/graduate_programs.json"
        self.markham_campus_programs = [
            "Biotechnology Management",
            "Biotechnology",
            "Management Practice",
        ]

    def determine_campus(self, program_name: str) -> str:
        if program_name in self.markham_campus_programs:
            return "Markham"
        return "Keele"

    def fetch_page(self, url: str):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            print(f"Error fetching URL {url}: {e}")
            return None

    def extract_programs(self):
        html_content = self.fetch_page(self.directory_url)
        if not html_content:
            return

        soup = BeautifulSoup(html_content, "html.parser")
        program_links = soup.find_all("a", href=True)
        id = 1

        for link in program_links:
            href = link['href']
            if href.startswith("/graduate/programs/") and href != "/graduate/programs":
                program_name = href.split("/graduate/programs/")[-1].strip()
                program_url = f"https://futurestudents.yorku.ca{href}"
                if program_name not in [program["name"] for program in self.programs]:

                    #check if it's a diploma
                    is_diploma = "diploma" in href.lower() 

                    if is_diploma:
                        program_name = program_name.replace("-diploma", "").replace("diplomas/", "").strip()

                    program_name = program_name.replace("-", " ").title()

                    campus = self.determine_campus(program_name)

                    # check for dupes again, without this it can add duplicates with different casing
                    if program_name not in [program["name"] for program in self.programs]:
                        self.programs.append({
                            "id": id,
                            "name": program_name,
                            "url": program_url,
                            "is_diploma": is_diploma,
                            "campus": campus
                        })
                        id += 1

    def save_to_json(self):
        if not self.programs:
            print("No programs discovered.")
            return

        with open(self.output_file, "w") as jsonfile:
            json.dump(self.programs, jsonfile, indent=4)

        print(f"Program data saved to {self.output_file}")


if __name__ == "__main__":
    time.sleep(1) # delay slightly speeds up execution time
    start_time = time.time()
    
    scraper = YorkGraduateProgramScraper()
    scraper.extract_programs()
    print(f"Found {len(scraper.programs)} graduate programs")
    scraper.save_to_json()

    total_time = time.time() - start_time
    print(f"Total time taken: {round(total_time, 2)} seconds")