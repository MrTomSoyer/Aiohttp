import asyncio
import aiohttp

async def main():
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True)) as session:
        # Получение объявлений
        response = await session.get(
            "http://127.0.0.1:8080/ads"
        )
        print(response.status)
        print(await response.json())


        # # Создание объявления не авторизованного пользователя
        # response = await session.post(
        #     "http://127.0.0.1:8080/ads",
        #     json={"title": "Car", "owner_id": 1},
        # )
        # print(response.status)
        # print(await response.json())


        # # Регистрация пользователя 1
        # response = await session.post(
        #     "http://127.0.0.1:8080/register",
        #     json={"username": "Боря", "email": "borya@mail.ru", "password": "1234"},
        # )
        # print(response.status)
        # print(await response.json())


        # # Регистрация пользователя 2
        # response = await session.post(
        #     "http://127.0.0.1:8080/register",
        #     json={"username": "Вася", "email": "vasya@mail.ru", "password": "1234234"},
        # )
        # print(response.status)
        # print(await response.json())


        # # Создание объявления авторизованного пользователя 1
        # response = await session.post(
        #     "http://127.0.0.1:8080/login",
        #     json={"username": "Боря", "email": "borya@mail.ru", "password": "1234"},
        # )
        # print(response.status)
        # print(await response.json())
        #
        # response = await session.post(
        #     "http://127.0.0.1:8080/ads",
        #     json={"title": "Car"},
        # )
        # print(response.status)
        # print(await response.json())


        # # Создание объявления авторизованного пользователя 2
        # response = await session.post(
        #     "http://127.0.0.1:8080/login",
        #     json={"username": "Вася", "email": "vasya@mail.ru", "password": "1234234"},
        # )
        # print(response.status)
        # print(await response.json())
        #
        # response = await session.post(
        #     "http://127.0.0.1:8080/ads",
        #     json={"title": "Car"},
        # )
        # print(response.status)
        # print(await response.json())


        # # Изменения объявления не авторизованного пользователя
        # response = await session.patch(
        #     "http://127.0.0.1:8080/ads/1",
        #     json={"title": "Пластикb", "description": "новый"},
        # )
        # print(response.status)
        # print(await response.json())


        # # Изменения своего объявления  авторизованного пользователя
        # response = await session.post(
        #     "http://127.0.0.1:8080/login",
        #     json={"username": "Боря", "email": "borya@mail.ru", "password": "1234"},
        # )
        # print(response.status)
        # print(await response.json())
        #
        # response = await session.patch(
        #     "http://127.0.0.1:8080/ads/1",
        #     json={"title": "Moto", "description": "новыйy"},
        # )
        # print(response.status)
        # print(await response.json())


        # # Изменения не своего объявления  авторизованного пользователя
        # response = await session.post(
        #     "http://127.0.0.1:8080/login",
        #     json={"username": "Боря", "email": "borya@mail.ru", "password": "1234"},
        # )
        # print(response.status)
        # print(await response.json())
        #
        # response = await session.patch(
        #     "http://127.0.0.1:8080/ads/2",
        #     json={"title": "Moto", "description": "новыйy"},
        # )
        # print(response.status)
        # print(await response.json())


        # # Удаление объявления  авторизованного пользователя
        # response = await session.post(
        #     "http://127.0.0.1:8080/login",
        #     json={"username": "Боря", "email": "borya@mail.ru", "password": "1234"},
        # )
        # print(response.status)
        # print(await response.json())
        #
        # response = await session.delete(
        #     "http://127.0.0.1:8080/ads/2",
        # )
        # print(response.status)
        # print(await response.json())



asyncio.run(main())
