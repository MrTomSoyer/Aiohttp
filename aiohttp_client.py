import asyncio
import aiohttp

async def main():
    async with aiohttp.ClientSession() as session:

        # response = await session.post(
        #     "http://127.0.0.1:8080/ads",
        #     json={"title": "Картон", "owner_id": 1},
        # )
        # print(response.status)
        # print(await response.json())

        # response = await session.post(
        #     "http://127.0.0.1:8080/user",
        #     json={"username": "Боря", "email": "borya@mail.ru", "password": "1234"},
        # )
        # print(response.status)
        # print(await response.json())

        # response = await session.patch(
        #     "http://127.0.0.1:8080/ads/1",
        #     json={"title": "Пластикb", "description": "новый"},
        # )
        # print(response.status)
        # print(await response.json())

        response = await session.delete(
            "http://127.0.0.1:8080/ads/3",
        )
        print(response.status)
        print(await response.json())



asyncio.run(main())
