import requests
import time
from requests.exceptions import HTTPError

class MegaverseAPI:
    def __init__(self, base_url, candidate_id, max_retries=5):
        self.base_url = base_url
        self.candidate_id = candidate_id
        self.max_retries = max_retries

    def create_polyanet(self, row, column):
        url = f"{self.base_url}/polyanets"
        data = {
            "candidateId": self.candidate_id,
            "row": row,
            "column": column
        }
        self._make_request('POST', url, data)

    def create_soloon(self, row, column, color):
        url = f"{self.base_url}/soloons"
        data = {
            "candidateId": self.candidate_id,
            "row": row,
            "column": column,
            "color": color
        }
        self._make_request('POST', url, data)

    def create_cometh(self, row, column, direction):
        url = f"{self.base_url}/comeths"
        data = {
            "candidateId": self.candidate_id,
            "row": row,
            "column": column,
            "direction": direction
        }
        self._make_request('POST', url, data)

    def fetch_goal_map(self):
        url = f"{self.base_url}/map/{self.candidate_id}/goal"
        response = self._make_request('GET', url)
        print("Map fetched successfully!")
        return response.json()

    def create_object(self, obj_type, row, column, *args):
        if obj_type == "POLYANET":
            self.create_polyanet(row, column)
        elif obj_type.endswith("SOLOON"):
            color = obj_type.split("_")[0].lower()
            self.create_soloon(row, column, color)
        elif obj_type.endswith("COMETH"):
            direction = obj_type.split("_")[0].lower()
            self.create_cometh(row, column, direction)

    def _make_request(self, method, url, data=None):
        for attempt in range(self.max_retries):
            try:
                if method == 'POST':
                    response = requests.post(url, json=data)
                elif method == 'GET':
                    response = requests.get(url)
                response.raise_for_status()
                return response
            except HTTPError as http_err:
                if response.status_code == 429:
                    wait_time = 2 ** attempt
                    print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise http_err
        raise Exception(f"Failed to complete {method} request to {url} after {self.max_retries} attempts")

class Megaverse:
    def __init__(self, api):
        self.api = api

    def parse_goal_map(self, goal_map):
        objects = []
        for row_index, row in enumerate(goal_map['goal']):
            for col_index, cell in enumerate(row):
                if cell != 'SPACE':
                    obj_type = cell
                    objects.append((obj_type, row_index, col_index))
        return objects

    def create_megaverse(self, objects):
        for obj_type, row, column in objects:
            self.api.create_object(obj_type, row, column)

if __name__ == "__main__":
    base_url = "https://challenge.crossmint.io/api"
    candidate_id = "454d0fcb-4c03-445a-af0f-63e72d400ec9"

    api = MegaverseAPI(base_url, candidate_id)
    megaverse = Megaverse(api)

    # Fetch and parse the goal map
    goal_map = api.fetch_goal_map()
    objects = megaverse.parse_goal_map(goal_map)

    # Create the megaverse objects
    megaverse.create_megaverse(objects)
    print("Megaverse created successfully!")
