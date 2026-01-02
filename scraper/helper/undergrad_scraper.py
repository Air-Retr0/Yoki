import requests
from bs4 import BeautifulSoup
import json
import time

class YorkProgramScraper:
    def __init__(self):
        self.directory_url = "https://futurestudents.yorku.ca/program-search"
        self.programs = []
        self.output_file = 'docs/data/programs/undergrad_programs.json'
        self.markham_campus_programs = [
            "Computer Science for Software Development",
            "Creative Technologies",
            "Communication Social Media And Public Relations",
            "First Year Engineering",
            "First Year Science",
            "Entrepreneurship And Innovation",
            "Sport Management",
            "Digital Technologies",
            "Financial Technologies"
        ]

    def determine_campus(self, program_name: str) -> str:
        if program_name in self.markham_campus_programs:
            return "Markham"
        
        if '/Glendon' in program_name or 'Glendon/' in program_name:
            return "Glendon"
        
        return "Keele"

    def fetch_page(self, url: str):
        try:
            response = requests.get(url)
            response.raise_for_status() # check for http errors
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

            if href.startswith("/program/") and href != "/program/": 
                program_name = href.split("/program/")[-1]

                if program_name not in [program["name"] for program in self.programs]:
                     # check if it's non-degree certificate program
                    is_certificate = "certificate" in href.lower()

                    if is_certificate:
                        program_name = program_name.replace("certificates/", "").strip()

                    # clean up program name and add captialization
                    program_name = program_name.replace("-", " ").title() 

                    campus = self.determine_campus(program_name)

                    program_name = program_name.replace("/Glendon", "").strip()

                    # check for dupes again, without this it can add duplicates with different casing
                    if program_name not in [program["name"] for program in self.programs]:
                        self.programs.append({
                            "id": id,  
                            "name": program_name, 
                            "url": f"https://futurestudents.yorku.ca{href}", 
                            "is_certificate": is_certificate, 
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

    scraper = YorkProgramScraper()
    scraper.extract_programs()
    print(f"Found {len(scraper.programs)} programs")
    scraper.save_to_json()

    total_time = time.time() - start_time
    print(f"Total time taken: {round(total_time, 2)} seconds")