import os
import logging


########################################## Authentication ###########################################
async def sub_test_register_user(
                                    async_client,
                                    data_test_register_user):
    response = await async_client.post(
                                    url=f"/admin/register/",
                                    json=data_test_register_user,)
    response_json = response.json()
    logging.info("Register user testing ...")
    assert response.status_code == 201
    assert response_json["username"] == data_test_register_user["username"]
    assert response_json["full_name"] == data_test_register_user["full_name"]
    assert response_json["email"] == data_test_register_user["email"]
    assert response_json["is_active"] == True
    logging.info("Register user testing finished.")


async def sub_test_login(
                                    async_client,
                                    data_test_login):
    response = await async_client.post(
                                    url=f"/admin/login/",
                                    data=data_test_login)
    response_json = response.json()
    logging.info("Login user testing ...")
    assert response.status_code == 200
    assert response_json["access_token"] is not None
    assert response_json["refresh_token"] is not None
    logging.info('Login user testing finished.')
    os.environ["BEARER_TOKEN"] = response_json["access_token"]
    os.environ["REFRESH_TOKEN"] = response_json["refresh_token"]


async def sub_test_update_user(
                                    async_client,
                                    data_test_update_user):
    response = await async_client.put(
                                    url=f"/admin/update/",
                                    json=data_test_update_user,
                                    headers={"Authorization": f"Bearer {os.environ["BEARER_TOKEN"]}"})
    response_json = response.json()
    logging.info("Update user testing ...")
    assert response.status_code == 200
    assert response_json["full_name"] == data_test_update_user["full_name"]
    assert response_json["email"] == data_test_update_user["email"]
    logging.info("Update user testing finished.")


async def sub_test_change_password(
                                    async_client,
                                    data_test_change_password):
    response = await async_client.put(
                                    url=f"/admin/change_password/",
                                    json=data_test_change_password,
                                    headers={"Authorization": f"Bearer {os.environ["BEARER_TOKEN"]}"})
    response_json = response.json()
    logging.info("Changing password testing ...")
    assert response.status_code == 200
    assert response_json == {"message": "Password changed successfully."}
    logging.info("Changing password testing finished.")


async def sub_test_refresh(async_client):
    response = await async_client.post(
                                    url=f"/admin/refresh/",
                                    headers={"Authorization": f"Bearer {os.environ["REFRESH_TOKEN"]}"})
    response_json = response.json()
    logging.info("Refresh token testing ...")
    assert response.status_code == 200
    assert response_json["access_token"] is not None
    logging.info("Refresh token testing finished.")
    os.environ["BEARER_TOKEN"] = response_json["access_token"]


async def sub_test_delete_user(async_client):
    response = await async_client.delete(
                                    url=f"/admin/delete/",
                                    headers={"Authorization": f"Bearer {os.environ["BEARER_TOKEN"]}"})
    response_json = response.json()
    logging.info("Deletion user testing ...")
    assert response.status_code == 200
    assert response_json == {"message": "User deleted successfully."}
    logging.info("Deletion user testing finished.")


########################################## Hotel ###########################################
async def sub_test_create_room_type(
                                    async_client,
                                    data_test_create_room_type):
    response = await async_client.post(
                                    url=f"/roomtype/",
                                    json=data_test_create_room_type,
                                    headers={"Authorization": f"Bearer {os.environ["BEARER_TOKEN"]}"})
    response_json = response.json()
    logging.info("Creation room type testing ...")
    assert response.status_code == 201
    assert response_json["type"] == data_test_create_room_type["type"]
    logging.info("Creation room type testing finished.")
    os.environ["ROOM_TYPE_ID"] = str(response_json["id"])


async def sub_test_delete_room_type(async_client):
    id = os.environ["ROOM_TYPE_ID"]
    response = await async_client.delete(
                                    url=f"/roomtype/{id}/",
                                    headers={"Authorization": f"Bearer {os.environ["BEARER_TOKEN"]}"})
    response_json = response.json()
    logging.info("Deletion room type testing ...")
    assert response.status_code == 200
    assert response_json == {"message": "Room type deleted successfully."}
    logging.info("Deletion room type testing finished.")


async def sub_test_create_room(
                                    async_client,
                                    data_test_create_room):
    data_test_create_room["type"] = int(os.environ["ROOM_TYPE_ID"])
    response = await async_client.post(
                                    url=f"/room/",
                                    json=data_test_create_room,
                                    headers={"Authorization": f"Bearer {os.environ["BEARER_TOKEN"]}"})
    response_json = response.json()
    logging.info("Creation room testing ...")
    assert response.status_code == 201
    assert response_json["number"] == data_test_create_room["number"]
    assert response_json["person"] == data_test_create_room["person"]
    assert response_json["status"] == "Free"
    assert response_json["description"] == data_test_create_room["description"]
    assert response_json["booking"] is None
    assert response_json["roomtypes"] is not None
    logging.info("Creation room testing finished.")
    os.environ["ROOM_ID"] = str(response_json["id"])


async def sub_test_update_room(
                                    async_client,
                                    data_test_update_room):
    id = os.environ["ROOM_ID"]
    response = await async_client.put(
                                    url=f"/room/{id}/",
                                    json=data_test_update_room,
                                    headers={"Authorization": f"Bearer {os.environ["BEARER_TOKEN"]}"})
    response_json = response.json()
    logging.info("Update room testing ...")
    assert response.status_code == 200
    assert response_json["person"] == data_test_update_room["person"]
    assert response_json["status"] == data_test_update_room["status"]
    assert response_json["booking"] is None
    assert response_json["roomtypes"] is not None
    logging.info("Update room testing finished.")


async def sub_test_get_list_room(async_client):
    response = await async_client.get(
                                    url=f"/room/",
                                    headers={"Authorization": f"Bearer {os.environ["BEARER_TOKEN"]}"})
    response_json = response.json()
    logging.info("Get list room testing ...")
    assert response.status_code == 200
    assert len(response_json) == 1
    logging.info("Get list room testing finished.")


async def sub_test_delete_room(async_client):
    id = os.environ["ROOM_ID"]
    response = await async_client.delete(
                                    url=f"/room/{id}/",
                                    headers={"Authorization": f"Bearer {os.environ["BEARER_TOKEN"]}"})
    response_json = response.json()
    logging.info("Deletion room testing ...")
    assert response.status_code == 200
    assert response_json == {"message": "Room deleted successfully."}
    logging.info("Deletion room testing finished.")


########################################## Execute tests ###########################################
async def test_authentication(
                                async_client,
                                data_test_register_user,
                                data_test_login,
                                data_test_update_user,
                                data_test_change_password):
    logging.info("START - testing authentication module")
    await sub_test_register_user(async_client, data_test_register_user)
    await sub_test_login(async_client, data_test_login)
    await sub_test_refresh(async_client)
    await sub_test_update_user(async_client, data_test_update_user)
    await sub_test_change_password(async_client, data_test_change_password)
    await sub_test_delete_user(async_client)
    logging.info("STOP - testing authentication module")


async def test_hotel(
                                async_client,
                                data_test_register_user,
                                data_test_login,
                                data_test_create_room_type,
                                data_test_create_room,
                                data_test_update_room):
    logging.info("START - testing hotel module")
    await sub_test_register_user(async_client, data_test_register_user)
    await sub_test_login(async_client, data_test_login)
    await sub_test_create_room_type(async_client, data_test_create_room_type)
    await sub_test_create_room(async_client, data_test_create_room)
    await sub_test_update_room(async_client, data_test_update_room)
    await sub_test_get_list_room(async_client)
    await sub_test_delete_room(async_client)
    await sub_test_delete_room_type(async_client)
    await sub_test_delete_user(async_client)
    logging.info("STOP - testing hotel module")
