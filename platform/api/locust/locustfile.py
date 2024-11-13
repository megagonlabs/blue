from locust import HttpUser, between, task
import uuid


class BlueUser(HttpUser):
    # users wait between 1 and 5 seconds after each task
    wait_time = between(1, 3)
    account_id = str(uuid.uuid4())
    host = 'http://0.0.0.0:5050'
    platform_name = 'default'
    session_id = None

    @task
    def create_session(self):
        self.client.post(f"/blue/platform/{self.platform_name}/sessions/session")

    @task
    def get_my_sessions(self):
        self.client.get(f'/blue/platform/{self.platform_name}/sessions', json={'my_sessions': True})

    @task
    def get_all_sessions(self):
        # high response time task
        self.client.get(f'/blue/platform/{self.platform_name}/sessions')

    @task
    def get_session_data(self):
        self.client.get(f'/blue/platform/{self.platform_name}/sessions/session/{self.session_id}')

    @task
    def update_session(self):
        self.client.put(f'/blue/platform/{self.platform_name}/sessions/session/{self.session_id}', json={'name': 'locust test session name', 'description': 'locust test session description'})

    @task
    def list_session_members(self):
        self.client.get(f'/blue/platform/{self.platform_name}/sessions/session/{self.session_id}/members')

    def on_start(self):
        # set client header
        self.client.headers = {'X-accountId': self.account_id}
        with self.client.get('/health_check') as response:
            print(f'GET /health_check {response.status_code}')
        # create a session and store session ID
        with self.client.post(f'/blue/platform/{self.platform_name}/sessions/session') as response:
            response_json = response.json()
            self.session_id = response_json['result']['id']

    def on_stop(self):
        # delete test session
        self.client.delete(f'/blue/platform/{self.platform_name}/sessions/session/{self.session_id}')
