import unittest
from local_test_app import app
import json
import os


class TestAPI(unittest.TestCase):
    """Tests with Redis."""

    def setUp(self):
        """Stuff to do before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True

    def test00_api_ready(self):
        """Test the readness of the API"""

        result = self.client.get("/")
        self.assertEqual(result.status_code, 200)

    def test_01_full_testing_scenario(self):
        """Step 1: Test posting a configs item"""

        config1 = {
            "name": "datacenter-10",
            "metadata": {
                "monitoring": {
                    "enabled": "true"
                },
                "limits": {
                    "cpu": {
                        "enabled": "false",
                        "value": "250m"
                    }
                }
            }
        }

        config2 = {
            "name": "datacenter-11",
            "metadata": {
                "monitoring": {
                    "enabled": "true"
                },
                "limits": {
                    "cpu": {
                        "enabled": "false",
                        "value": "250m"
                    }
                }
            }
        }
        result = self.client.post(
            "/configs", data=json.dumps(config1), content_type='application/json')

        self.assertEqual(result.status_code, 200)
        result = self.client.post(
            "/configs", data=json.dumps(config2), content_type='application/json')

        self.assertEqual(result.status_code, 200)


        """Step 2: Test retrieving all configs"""

        all_configs = [{"name": "datacenter-11", "metadata": "{'monitoring': {'enabled': 'true'}, 'limits': {'cpu': {'enabled': 'false', 'value': '250m'}}}"},
                       {"name": "datacenter-10", "metadata": "{'monitoring': {'enabled': 'true'}, 'limits': {'cpu': {'enabled': 'false', 'value': '250m'}}}"}]

        result = self.client.get("/configs")
        self.assertEqual(result.status_code, 200)
        data = json.loads(result.data)
        self.assertEqual(data, all_configs)


        """Step 3: Test retrieving configs by name"""
        datacenter10_configs = {
            "name": "datacenter-10",
            "metadata": "{'monitoring': {'enabled': 'true'}, 'limits': {'cpu': {'enabled': 'false', 'value': '250m'}}}"
        }

        result = self.client.get("/configs/datacenter-10")
        self.assertEqual(result.status_code, 200)
        data = json.loads(result.data)
        self.assertEqual(data, datacenter10_configs)


        """Step 4: Test retrieving query configs"""

        configs_cpu_enabled_false = [{"name": "datacenter-11", "metadata": "{'monitoring': {'enabled': 'true'}, 'limits': {'cpu': {'enabled': 'false', 'value': '250m'}}}"},
                                     {"name": "datacenter-10", "metadata": "{'monitoring': {'enabled': 'true'}, 'limits': {'cpu': {'enabled': 'false', 'value': '250m'}}}"}]

        result = self.client.get("/search?metadata.limits.cpu.enabled=false")
        self.assertEqual(result.status_code, 200)
        data = json.loads(result.data)
        self.assertEqual(data, configs_cpu_enabled_false)

        """Step 5: Test Deleting config item"""

        config_list_after_deleting_datacenter_10 = [
            {"name": "datacenter-11", "metadata": "{'monitoring': {'enabled': 'true'}, 'limits': {'cpu': {'enabled': 'false', 'value': '250m'}}}"}]
        delete_request = self.client.delete("/configs/datacenter-10")
        self.assertEqual(delete_request.status_code, 204)
        result = self.client.get("/configs")
        data = json.loads(result.data)
        self.assertEqual(data, config_list_after_deleting_datacenter_10)

        """Step 6: Test updating configs by name"""

        datacenter11_configs_after_patch = {
            "name": "datacenter-12",
            "metadata": "{'monitoring': {'enabled': 'true'}, 'limits': {'cpu': {'enabled': 'false', 'value': '250m'}}}"
        }
        new_name = {
            "name": "datacenter-12"
        }

        patch = self.client.patch(
            "/configs/datacenter-11", data=json.dumps(new_name), content_type='application/json')
        self.assertEqual(patch.status_code, 200)
        result = self.client.get("/configs/datacenter-12")
        data = json.loads(result.data)
        self.assertEqual(data, datacenter11_configs_after_patch)


if __name__ == '__main__':
    unittest.main()
