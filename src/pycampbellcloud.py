import requests
from requests.exceptions import JSONDecodeError

# Wrapper setup
def request_wrapper(func):
    def wrapper(*args, **kwargs):
        results = func(*args, **kwargs)
        if results is None:
            return {'status': 'Results is type None'}
        elif results.status_code == 304:
            try:
                json_result = results.json()
                return json_result
            except JSONDecodeError:
                return {'message': 'No metadata fields provided for update'}
        elif results.status_code == 204:
            try:
                json_result = results.json()
                return json_result
            except JSONDecodeError:
                return {'status': 'Success', 'message': 'Response returned a 204 with no content'}
        elif results.status_code == 200:
            try:
                json_result = results.json()
                return json_result
            except JSONDecodeError:
                return {'status': 'Success', 'message': "Response returned a 200 with no content"}
        try:
            return results.json()
        except JSONDecodeError:
            return {'status': f'Result code of request is {results.status_code}. Could not convert to JSON.'}
    return wrapper

def wrap_all_methods(cls):
    no_wrap = ["__init__", "_CampbellCloud__build_auth_header"]
    for name, method in cls.__dict__.items():
        if callable(method) and name not in no_wrap:
            setattr(cls, name, request_wrapper(method))
    return cls


@wrap_all_methods
class CampbellCloud:

    def __init__(self, organization_id: str, username: str, password: str):
        self.__organization_id = organization_id
        self.__username = username
        self.__password = password
        self.__base_api_url = f"https://us-west-2.campbell-cloud.com/api/v1/organizations/{self.__organization_id}/"
        self.__measurement_api_url = "https://us-west-2.campbell-cloud.com/api/v1/libraries/"
        self.__token_api_url = "https://us-west-2.campbell-cloud.com/api/v1/tokens"
        self.__product_api_url = "https://us-west-2.campbell-cloud.com/api/v1/product-registrations"
        self.__token = self.__build_auth_header()

    def __build_auth_header(self):
        try:
            raw_token = self.create_token(self.__username, self.__password, "cloud", "password")['access_token']
            return {"Authorization": "Bearer " + raw_token}
        except KeyError:
            raise SyntaxError("Invalid credentials. Please check username and password.")

    # ===================================================
    #                   API Endpoints
    # ===================================================

    def list_assets(self):
        return requests.get(f"{self.__base_api_url}assets", headers=self.__token)

    def create_asset(self, metadata):
        """
        Parameters required not specified in Documentation:
        model
        name
        manufacturer
        status
        configuration
        uid
        Parameters not required but work
        serial
        """

        return requests.post(f"{self.__base_api_url}assets", headers=self.__token, json=metadata)

    def get_asset(self, assetID):
        return requests.get(f"{self.__base_api_url}assets/{assetID}", headers=self.__token)

    def update_asset(self, assetID, metadata):
        """
        Required Parameters not specified in documentation
        name
        model
        manufacturer
        status
        configuration (timezone, communication_threshold)
        If Serial and UID is not specified (Which the request doesn't say it is) then it will not include it in CampbellCloud
        When Serial and UID are not specified then the device is deleted with the delete_asset function that UID is no longer
        valid and can not be used again for the organization.
        """

        return requests.put(f"{self.__base_api_url}assets/{assetID}", headers=self.__token, json=metadata)

    def delete_asset(self, assetID):
        return requests.delete(f"{self.__base_api_url}assets/{assetID}", headers=self.__token)

    def get_asset_state(self, assetID):
        return requests.get(f"{self.__base_api_url}assets/{assetID}/state", headers=self.__token)

    def update_asset_state(self, assetID, status):
        return requests.put(f"{self.__base_api_url}assets/{assetID}/status", headers=self.__token, json={"status": status})

    def update_asset_metadata(self, assetID, metadata):
        return requests.put(f"{self.__base_api_url}assets/{assetID}/metadata", headers=self.__token, json=metadata)

    def list_asset_historical(self, assetID, startEpoch, endEpoch):
        params = {"startEpoch": startEpoch, "endEpoch": endEpoch}
        return requests.get(f"{self.__base_api_url}assets/{assetID}/historical", headers=self.__token, params=params)

    def get_asset_historical_by_id(self, assetId, assetHistoricalId):
        return requests.get(f"{self.__base_api_url}assets/{assetId}/historical/{assetHistoricalId}", headers=self.__token)

    def get_asset_subscription(self, assetID):
        # TODO: Deprecated
        return requests.get(f"{self.__base_api_url}assets/{assetID}/subscription", headers=self.__token)

    def get_datapoints(self, aliases, startEpoch, endEpoch, brief=True):
        """
        Endpoint says no Route matched with those values. Endpoint doesn't work
        """

        params = {"aliases": aliases, "startEpoch": startEpoch, "endEpoch": endEpoch, "brief": brief}
        return requests.get(f"{self.__base_api_url}datapoints", headers=self.__token, params=params)

    def list_datastreams(self, limit=100, offset=0, assetId=None, stationId=None):
        params = {"limit": limit, "offset": offset, "assetId": assetId, "stationId": stationId}
        return requests.get(f"{self.__base_api_url}datastreams", headers=self.__token, json=params)

    def update_datastream(self, datastreamId, profile="datastream", version=1):
        """
        Parameters required but not listed
        field
        """

        params = {"metadata": {"$profile": profile, "$version": version, "field": "Temp"}}
        return requests.put(f"{self.__base_api_url}datastreams/{datastreamId}", headers=self.__token, json=params)

    def get_datastream(self, datastreamId):
        return requests.get(f"{self.__base_api_url}datastreams/{datastreamId}", headers=self.__token)

    def list_datastream_historical(self, datastreamId, startEpoch, endEpoch):
        params = {"startEpoch": startEpoch, "endEpoch": endEpoch}
        return requests.get(f"{self.__base_api_url}datastreams/{datastreamId}/historical", headers=self.__token, params=params)

    def get_datastream_historical_by_id(self, datastreamId, datastreamHistoricalId):
        return requests.get(f"{self.__base_api_url}datastreams/{datastreamId}/historical/{datastreamHistoricalId}",
                            headers=self.__token)

    def update_datastream_metadata(self, datastreamId, metadata):
        # TODO: Needs updated
        return requests.put(f"{self.__base_api_url}datastreams/{datastreamId}/metadata", headers=self.__token, json=metadata)
    
    def get_datastream_datapoints(self, datastreamId, startEpoch, endEpoch, brief=True, limit=100):
        params = {"startEpoch": startEpoch, "endEpoch": endEpoch, "brief": brief, "limit": limit}
        return requests.get(f"{self.__base_api_url}datastreams/{datastreamId}/datapoints", headers=self.__token, params=params)
    
    def get_datastream_datapoints_last(self, datastreamId):
        return requests.get(f"{self.__base_api_url}datastreams/{datastreamId}/datapoints/last", headers=self.__token)

    def get_datastream_datapoints_count(self, datastreamId, startEpoch, endEpoch):
        params = {"startEpoch": startEpoch, "endEpoch": endEpoch}
        return requests.get(f"{self.__base_api_url}datastreams/{datastreamId}/datapoints/count", headers=self.__token, params=params)

    def count_datastreams(self, assetId=None, stationId=None):
        """
        Endpoint is showing this error and not letting me count the number of datapoints
        {'message': 'no Route matched with those values'}
        """

        params = {"assetId": assetId, "stationId": stationId}
        return requests.get(f"{self.__base_api_url}datastreams/count", headers=self.__token, params=params)

    def list_groups(self):
        return requests.get(f"{self.__base_api_url}groups", headers=self.__token)

    def create_group(self, metadata):
        return requests.post(f"{self.__base_api_url}groups", headers=self.__token, json=metadata)

    def get_group(self, groupId):
        return requests.get(f"{self.__base_api_url}groups/{groupId}", headers=self.__token)

    def update_group(self, groupId, metadata):
        """
        Parameters that are not listed required but actually are
        name
        """

        return requests.put(f"{self.__base_api_url}groups/{groupId}", headers=self.__token, json=metadata)

    def delete_group(self, groupId):
        return requests.delete(f"{self.__base_api_url}groups/{groupId}", headers=self.__token)

    def get_users_in_group(self, groupId):
        return requests.get(f"{self.__base_api_url}groups/{groupId}/users", headers=self.__token)

    def list_group_permissions(self, groupId):
        return requests.get(f"{self.__base_api_url}groups/{groupId}/permissions", headers=self.__token)

    def add_permission_to_group(self, groupId, permissionId):
        """
        How am I supposed to know what permissionId to use? Why is there not an explanation on what this parameter even is?
        """

        return requests.put(f"{self.__base_api_url}groups/{groupId}/permissions/{permissionId}", headers=self.__token)

    def remove_permission_from_group(self, groupId, permissionId):
        return requests.delete(f"{self.__base_api_url}groups/{groupId}/permissions/{permissionId}", headers=self.__token)

    def list_measurement_classification_types(self, measurementClassificationTypeId):
        return requests.get(f"{self.__measurement_api_url}measurement-types/{measurementClassificationTypeId}", headers=self.__token)

    def list_measurement_classification_systems(self):
        return requests.get(f"{self.__measurement_api_url}measurement-systems", headers=self.__token)

    def get_measurement_classification_system_by_id(self, measurementClassificationSystemId):
        return requests.get(f"{self.__measurement_api_url}measurement-systems/{measurementClassificationSystemId}",
                            headers=self.__token)

    def get_measurement_classification_conversions_by_id(self, measurementClassificationClassificationId,
                                                         measurementClassificationSourceUomId,
                                                         measurementClassificationTargetUomId):
        return requests.get(
            f"{self.__measurement_api_url}measurement-conversions/{measurementClassificationClassificationId}/{measurementClassificationSourceUomId}/{measurementClassificationTargetUomId}",
            headers=self.__token)

    def get_part(self, partId):
        return requests.get(f"{self.__measurement_api_url}parts/{partId}", headers=self.__token)

    def get_organization_plan(self):
        return requests.get(f"{self.__base_api_url}plan", headers=self.__token)

    def get_reach_component_version_state(self, reachComponentId, reachComponentVersionId):
        return requests.get(
            f"{self.__base_api_url}reach-components/{reachComponentId}/versions/{reachComponentVersionId}/state",
            headers=self.__token)

    def list_station_groups(self):
        return requests.get(f"{self.__base_api_url}station-groups", headers=self.__token)

    def create_station_group(self, metadata):
        """
        Parameters required but are not listed:
        name
        """

        return requests.post(f"{self.__base_api_url}station-groups", headers=self.__token, json=metadata)

    def get_station_group(self, stationGroupId):
        return requests.get(f"{self.__base_api_url}station-groups/{stationGroupId}", headers=self.__token)

    def update_station(self, stationGroupId, metadata):
        """
        Parameters required but not listed
        name
        """

        return requests.put(f"{self.__base_api_url}station-groups/{stationGroupId}", headers=self.__token, json=metadata)

    def delete_station_group(self, stationGroupId):
        """
        Successful request is returning 200 not 204.
        """

        return requests.delete(f"{self.__base_api_url}station-groups/{stationGroupId}", headers=self.__token)

    def update_station_group_metadata(self, stationGroupId, metadata):
        """
        Successful request is returning response code of 200.
        Parameters required but not listed in documentation are:
        $profile
        $version
        """

        return requests.put(f"{self.__base_api_url}station-groups/{stationGroupId}/metadata", headers=self.__token, json=metadata)

    def list_stations(self):
        return requests.get(f"{self.__base_api_url}stations", headers=self.__token)

    def create_station(self, metadata):
        """
        Parameter required but not listed
        name
        """

        return requests.post(f"{self.__base_api_url}stations", headers=self.__token, json=metadata)

    def get_station(self, stationId):
        return requests.get(f"{self.__base_api_url}stations/{stationId}", headers=self.__token)

    def delete_station(self, stationId):
        return requests.delete(f"{self.__base_api_url}stations/{stationId}", headers=self.__token)

    def get_station_state(self, stationId):
        return requests.get(f"{self.__base_api_url}stations/{stationId}/state", headers=self.__token)

    def list_station_historical(self, stationId, startEpoch, endEpoch):
        params = {'startEpoch': startEpoch, "endEpoch": endEpoch}
        return requests.get(f"{self.__base_api_url}stations/{stationId}/historical", headers=self.__token, params=params)

    def get_station_historical_by_id(self, stationId, stationHistoricalId):
        return requests.get(f"{self.__base_api_url}stations/{stationId}/historical/{stationHistoricalId}", headers=self.__token)

    def update_station_metadata(self, stationId, metadata):
        """
        Returns error on a valid request that should work:
        {'message': 'no Route matched with those values'}
        """

        return requests.put(f"{self.__base_api_url}stations/{stationId}/metadata", headers=self.__token, json=metadata)

    def list_subscriptions(self):
        return requests.get(f"{self.__base_api_url}subscriptions", headers=self.__token)

    def create_subscriptions(self, po_number, subscriptions):
        return requests.post(f"{self.__base_api_url}subscriptions", headers=self.__token,
                             json={"po_number": po_number, "organization_id": self.__organization_id,
                                   "subscriptions": subscriptions})

    def get_subscriptions(self, subscriptionsId):
        return requests.get(f"{self.__base_api_url}subscriptions/{subscriptionsId}", headers=self.__token)

    def update_subscription(self, subscriptionId, auto_renew, renewal_part):
        return requests.put(f"{self.__base_api_url}subscriptions/{subscriptionId}", headers=self.__token,
                            json={"auto_renew": auto_renew, "renewal_part": renewal_part})

    def delete_subscription(self, subscriptionId):
        return requests.delete(f"{self.__base_api_url}subscriptions/{subscriptionId}", headers=self.__token)

    def upgrade_subscription_part(self, subscriptionId, partId):
        return requests.put(f"{self.__base_api_url}subscriptions/{subscriptionId}/parts/{partId}", headers=self.__token)

    def create_token(self, username, password, clientId, grant_type):
        return requests.post(f"{self.__token_api_url}",
                             json={"username": username, "password": password, "client_id": clientId,
                                   "grant_type": grant_type})

    def refresh_token(self):
        """
        Requires Username and Password but documentation doesn't mention it. Even with those it doesn't work. This endpoint needs more development.
        """

        return requests.put(f"{self.__token_api_url}", headers=self.__token, json={"refresh_token": ""})

    def list_users(self):
        return requests.get(f"{self.__base_api_url}users", headers=self.__token)

    def create_user(self, metadata):
        """
        Different organizations use different permissions. Sometimes they require an email to check etc. when this parameter is supplied
        """

        return requests.post(f"{self.__base_api_url}users", headers=self.__token, json={"metadata": metadata})

    def get_user(self, userId):
        return requests.get(f"{self.__base_api_url}users/{userId}", headers=self.__token)

    def update_user(self, userId, metadata):
        return requests.put(f"{self.__base_api_url}users/{userId}", headers=self.__token, json={"metadata": metadata})

    def delete_user(self, userId):
        return requests.delete(f"{self.__base_api_url}users/{userId}", headers=self.__token)

    def list_user_groups(self, userId):
        return requests.get(f"{self.__base_api_url}users/{userId}/groups", headers=self.__token)

    def count_user_groups(self, userId):
        return requests.get(f"{self.__base_api_url}users/{userId}/groups/count", headers=self.__token)

    def add_user_to_group(self, userId, groupId):
        return requests.put(f"{self.__base_api_url}users/{userId}/groups/{groupId}", headers=self.__token)

    def remove_user_from_group(self, userId, groupId):
        return requests.delete(f"{self.__base_api_url}users/{userId}/groups/{groupId}", headers=self.__token)

    def list_variables(self):
        return requests.get(f"{self.__base_api_url}variables", headers=self.__token)

    def create_variable(self, name, metadata):
        return requests.post(f"{self.__base_api_url}variables", headers=self.__token, json={"name": name, "metadata": metadata})

    # ==============================================
    #                NEW ENDPOINTS
    # ==============================================

    def list_alert_configurations(self):
        return requests.get(f"{self.__base_api_url}alert-configurations", headers=self.__token)

    def create_alert_configuration(self):
        # TODO: Update metadata and parameter list
        params = {"$profile": "configuration", "$version": 1}
        return requests.post(f"{self.__base_api_url}alert-configurations", headers=self.__token, json=params)

    def get_alert_configuration(self, alert_id: str):
        return requests.get(f"{self.__base_api_url}alert-configurations/{alert_id}", headers=self.__token)

    def update_alert_configuration(self, alert_id: str,  metadata: dict):
        # TODO: Update metadata and parameter list
        json_params = {"$profile": "configuration", "$version": 1}
        json_params.update(metadata)
        return requests.put(f"{self.__base_api_url}alert-configuration/{alert_id}", headers=self.__token, json=json_params)

    def delete_alert_configuration(self, alert_id: str):
        return requests.delete(f"{self.__base_api_url}alert-configurations/{alert_id}", headers=self.__token)

    def list_alert_configuration_historical(self, alert_id: str, end_epoch: int, start_epoch=0, offset=0, limit=100):
        # TODO: Update parameter types
        params = {"startEpoch": start_epoch, "endEpoch": end_epoch, "offset": offset, "limit": limit}
        return requests.get(f"{self.__base_api_url}alert-configurations/{alert_id}/historical", headers=self.__token, params=params)

    def get_alert_configuration_historical(self, alert_id: str, alert_historical_id: str):
        return requests.get(f"{self.__base_api_url}alert-configurations/{alert_id}/historical/{alert_historical_id}", headers=self.__token)

    def list_alert_events(self, alert_filter: str, end_epoch: int, start_epoch=0, offset=0):
        # TODO: Update parameter types
        params = {"startEpoch": start_epoch, "endEpoch": end_epoch, "offset": offset, "filter": alert_filter}
        return requests.get(f"{self.__base_api_url}/alert-events", headers=self.__token, params=params)

    def get_alert_events_id(self, alert_event_id):
        return requests.get(f"{self.__base_api_url}alert-events/{alert_event_id}", headers=self.__token)

    def search_alert_events(self, filters):
        # TODO: Update metadata and parameter list
        return requests.post(f"{self.__base_api_url}alert_events/search", headers=self.__token, json=filters)

    def list_alert_logs(self, alert_filter: str, end_epoch: int, start_epoch=0, offset=0, limit=100):
        # TODO: Update parameter types
        params = {"startEpoch": start_epoch, "endEpoch": end_epoch, "offset": offset, "limit": limit, "filter": alert_filter}
        return requests.get(f"{self.__base_api_url}alert-logs", headers=self.__token, params=params)

    def create_alert_log(self, alert_event_id: str, metadata):
        # TODO: Update metadata and parameter list
        json_params = {"alert_event_id": alert_event_id}
        json_params.update(metadata)
        return requests.post(f"{self.__base_api_url}alert-logs", headers=self.__token, json=json_params)

    def get_alert_logs_id(self, alert_log_id):
        # TODO: Update parameter types
        return requests.get(f"{self.__base_api_url}alert-logs/{alert_log_id}", headers=self.__token)

    def search_alert_logs(self, filters: dict):
        return requests.post(f"{self.__base_api_url}alert-log/search", headers=self.__token, json=filters)

    def update_asset_software(self, asset_id: str, software_type: str, os_metadata: dict = dict, program_metadata: dict = dict):
        headers = {"x-campbell-software-type": software_type}
        headers.update(self.__token)
        if software_type == "datalogger-os" and os_metadata != dict:
            json_params = os_metadata
        elif software_type == "datalogger-program" and program_metadata != dict:
            json_params = program_metadata
        else:
            raise SyntaxError("software_type can only be 'datalogger-os' or 'datalogger-program'. Along with passing the appropriate metadata parameter.")

        return requests.put(f"{self.__base_api_url}assets/{asset_id}/software-packages", headers=headers, json=json_params)

    def execute_asset_command(self, asset_id: str, command: str, start_epoch: int, end_epoch: int, table: str):
        json_params = {"command": command, "parameters": {"start_epoch": start_epoch, "end_epoch": end_epoch, "table": table}}
        return requests.put(f"{self.__base_api_url}assets/{asset_id}/commands", headers=self.__token, json=json_params)

    def list_exports(self):
        return requests.get(f"{self.__base_api_url}exports", headers=self.__token)

    def list_dashboards(self, before: str = "", after: str = "", first: int = 100, last : int = 100, brief : bool = True, latest : bool = True):
        params = {"before": before, "after": after, "first": first, "last": last, "brief": brief, "latest": latest}
        return requests.get(f"{self.__base_api_url}dashboards", headers=self.__token, params=params)

    def create_dashboard(self, metadata: dict):
        # TODO: Update metadata and parameter list
        return requests.post(f"{self.__base_api_url}dashboards", headers=self.__token, json=metadata)

    def get_dashboard(self, dashboard_id: str, latest: bool = True):
        params = {"latest": latest}
        return requests.get(f"{self.__base_api_url}dashboards/{dashboard_id}", headers=self.__token, params=params)

    def update_dashboard(self, dashboard_id : str, metadata: dict):
        # TODO: Update metadata and parameter list
        return requests.put(f"{self.__base_api_url}dashboards/{dashboard_id}", headers=self.__token, json=metadata)

    def delete_dashboard(self, dashboard_id: str):
        return requests.delete(f"{self.__base_api_url}dashboard/{dashboard_id}", headers=self.__token)

    def list_dashboard_historical(self, dashboard_id: str, before: str = None, after : str = None, first : int = 100, last : int = 100, reverse: bool = None, brief : bool = None):
        params = {"before": before, "after": after, "first": first, "last": last, "reverse": reverse, "brief": brief}
        return requests.get(f"{self.__base_api_url}dashboards/{dashboard_id}/historical", headers=self.__token, params=params)

    def get_dashboard_historical_by_id(self, dashboard_id : str, dashboard_historical_id : str):
        return requests.get(f"{self.__base_api_url}dashboards/{dashboard_id}/historical/{dashboard_historical_id}", headers=self.__token)

    def list_data_collections(self):
        return requests.get(f"{self.__base_api_url}data-collections/collections", headers=self.__token)

    def create_data_collections(self, metadata : dict):
        # TODO: Update metadata and parameter list
        return requests.post(f"{self.__base_api_url}data-collections/collections", headers=self.__token, json=metadata)

    def get_data_collection(self, data_collection_id : str):
        return requests.get(f"{self.__base_api_url}data-collections/collections/{data_collection_id}", headers=self.__token)

    def update_data_collection(self, data_collection_id : str, metadata : dict):
        # TODO: Update metadata and parameter list
        return requests.put(f"{self.__base_api_url}data-collections/collections/{data_collection_id}", headers=self.__token, json=metadata)

    def delete_data_collection(self, data_collection_id : str):
        return requests.delete(f"{self.__base_api_url}data-collections/collections/{data_collection_id}", headers=self.__token)

    def list_data_collection_types(self):
        return requests.get(f"{self.__base_api_url}data-collections/types", headers=self.__token)

    def create_data_collection_type(self, metadata : dict):
        # TODO: Update metadata and parameter list
        return requests.post(f"{self.__base_api_url}data-collections/types", headers=self.__token, json=metadata)

    def get_data_collection_type(self, data_collection_type_id : str):
        return requests.get(f"{self.__base_api_url}data-collections/types/{data_collection_type_id}", headers=self.__token)

    def update_data_collection_type(self, data_collection_type_id : str, metadata : dict):
        # TODO: Update metadata and parameter list
        return requests.put(f"{self.__base_api_url}data-collections/types/{data_collection_type_id}", headers=self.__token, json=metadata)

    def delete_data_collection_type(self, data_collection_type_id : str):
        return requests.delete(f"{self.__base_api_url}data-collections/types/{data_collection_type_id}", headers=self.__token)

    def list_data_collection_type_historical(self, data_collection_type_id : str):
        return requests.get(f"{self.__base_api_url}data-collections/types/{data_collection_type_id}/historical", headers=self.__token)

    def list_datastreams_labels(self, limit : int = 1000, start_after : str = None):
        params = {"limit": limit, "startAfter": start_after}
        return requests.get(f"{self.__base_api_url}datastreams/labels", headers=self.__token, params=params)

    def list_distribution_groups(self):
        return requests.get(f"{self.__base_api_url}distribution-groups", headers=self.__token)

    def create_distribution_groups(self, metadata : dict):
        # TODO: Update metadata and parameter list
        return requests.post(f"{self.__base_api_url}distribution-groups", headers=self.__token, json=metadata)

    def get_distribution_group(self, distribution_group_id : str):
        return requests.get(f"{self.__base_api_url}distribution-groups/{distribution_group_id}", headers=self.__token)

    def update_distribution_group(self, distribution_group_id : str, metadata : dict):
        # TODO: Update metadata and parameter list
        return requests.put(f"{self.__base_api_url}distributions-groups/{distribution_group_id}", headers=self.__token, json=metadata)

    def delete_distribution_group(self, distribution_group_id : str):
        return requests.delete(f"{self.__base_api_url}distributions-groups/{distribution_group_id}", headers=self.__token)

    def create_export(self, metadata : dict):
        # TODO: Update metadata and parameter list
        return requests.post(f"{self.__base_api_url}exports", headers=self.__token, json=metadata)

    def get_export(self, export_id : str):
        return requests.get(f"{self.__base_api_url}exports/{export_id}", headers=self.__token)

    def update_export(self, export_id : str, metadata : dict):
        # TODO: Update metadata and parameter list
        return requests.put(f"{self.__base_api_url}exports/{export_id}", headers=self.__token, json=metadata)

    def delete_export(self, export_id : str):
        return requests.delete(f"{self.__base_api_url}exports/{export_id}", headers=self.__token)

    def list_export_jobs(self, export_id : str):
        return requests.get(f"{self.__base_api_url}exports/{export_id}/jobs", headers=self.__token)

    def get_export_job(self, export_id : str, export_job_id : str):
        return requests.get(f"{self.__base_api_url}exports/{export_id}/jobs/{export_job_id}", headers=self.__token)

    def delete_export_job(self, export_id : str, export_job_id : str):
        return requests.delete(f"{self.__base_api_url}exports/{export_id}/jobs/{export_job_id}", headers=self.__token)

    def list_export_job_files(self, export_id : str, export_job_id : str):
        return requests.get(f"{self.__base_api_url}exports/{export_id}/jobs/{export_job_id}/files", headers=self.__token)

    def get_export_job_file(self, export_id : str, export_job_id : str, export_file_id : str):
        return requests.get(f"{self.__base_api_url}exports/{export_id}/jobs/{export_job_id}/files/{export_file_id}", headers=self.__token)

    def get_group_permission_by_id(self, group_id : str, permission_id : str):
        return requests.get(f"{self.__base_api_url}groups/{group_id}/permissions/{permission_id}", headers=self.__token)

    def switch_organization(self, new_organization_id : str):
        metadata = {"organization_id": new_organization_id}
        return requests.put(f"{self.__base_api_url}switch", headers=self.__token, json=metadata)

    def list_organizations(self):
        return requests.get("https://us-west-2.campbell-cloud.com/api/v1/organizations", headers=self.__token)

    def create_product_registration(self, content : str, signature : str, signature_alg : str, nonce : str):
        metadata = {"content": content, "signature": signature, "signature_alg": signature_alg, "nonce": nonce}
        return requests.post(f"{self.__product_api_url}", headers=self.__token, json=metadata)

    def export_reach_component(self, reach_component_id : str, reach_component_version_id : str):
        return requests.get(f"{self.__base_api_url}reach-components/{reach_component_id}/versions/{reach_component_version_id}/export", headers=self.__token)

    def preflight_create_station(self):
        return requests.options(f"{self.__base_api_url}stations", headers=self.__token)

    def get_subscription_claim(self, billing_transaction_id : str):
        return requests.get(f"{self.__base_api_url}subscriptions-claims/{billing_transaction_id}", headers=self.__token)

    def update_subscription_claims(self, billing_transaction_id : str, subscription_ids : list):
        metadata = {"subscription_ids": subscription_ids}
        return requests.put(f"{self.__base_api_url}subscriptions-claims/{billing_transaction_id}", headers=self.__token, json=metadata)

    def get_subscription_organization(self):
        return requests.get(f"{self.__base_api_url}subscription-organization", headers=self.__token)