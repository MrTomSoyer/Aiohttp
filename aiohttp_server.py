import base64
import json
import os

import aiohttp
import aiohttp_session
from aiohttp import web
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv
from aiohttp_session import setup, get_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from db import Session_DB, User,Ads, close_orm, init_orm


async def make_app():
    app = web.Application()
    load_dotenv()
    app.ensure_ascii = False
    secret_key = base64.urlsafe_b64decode(os.getenv("SECRET_KEY", "sdf34534trtg3rgw5gefe5g6bhwa4f"))
    setup(app, EncryptedCookieStorage(secret_key))
    app.cleanup_ctx.append(orm_context)
    app.middlewares.append(session_db_middleware)

    app.add_routes(
        [
            web.get(r"/ads/{ad_id:\d+}", AdsView),
            web.get("/ads", AdsView),
            web.get("/", IndexView),
            web.post("/ads", AdsView),
            web.patch(r"/ads/{ad_id:\d+}", AdsView),
            web.delete(r"/ads/{ad_id:\d+}", AdsView),
            web.post("/register", RegisterView),
            web.post("/login", LoginView),
        ]
    )

    return app


async def orm_context(app: web.Application):
    print("START")
    await init_orm()
    yield
    await close_orm()
    print("FINISH")

@web.middleware
async def session_db_middleware(request: web.Request, handler):
    async with Session_DB() as session_db:
        request["session_db"] = session_db
        return await handler(request)

def get_http_error(err_cls, message):
    err_dict = {"error": message}
    err_str = json.dumps(err_dict)
    return err_cls(text=err_str, content_type="application/json")


class IndexView(web.View):
    @staticmethod
    async def get():
        return web.HTTPFound("/ads")


class AdsView(web.View):
    @property
    def session_db(self) -> AsyncSession:
        return self.request["session_db"]

    async def check_login(self):
        session = await get_session(self.request)
        user_id = session.get("user_id")
        if user_id is None:
            raise get_http_error(web.HTTPUnauthorized, "You must be logged in")
        return user_id

    async def check_duplicate_ads(self, title: str, user_id: int):
        stmt = select(Ads).where(
            Ads.title == title,
            Ads.owner_id == user_id
        )
        ads_is_exists = await self.session_db.scalar(stmt)
        if ads_is_exists is not None:
            raise get_http_error(web.HTTPConflict, "ads already exists")

    async def get_all_ads(self):
        result = await self.session_db.execute(
            select(Ads)
        )
        ads = result.scalars().all()
        return ads

    async def get_ads(self):
        ad_id = self.request.match_info.get("ad_id")
        if ad_id is None:
            return await self.get_all_ads()
        ad = await self.session_db.get(Ads, int(ad_id))
        if ad is None:
            raise get_http_error(web.HTTPNotFound, "ads not found")
        return ad

    async def add_ads(self, ads: Ads):
        self.session_db.add(ads)
        try:
            await self.session_db.commit()
        except IntegrityError:
            raise get_http_error(web.HTTPConflict, "ads already exists2")
        return web.json_response(ads.ads_json)


    async def get(self):
        ads = await self.get_ads()
        if ads is None:
            raise get_http_error(web.HTTPNotFound, "ads not found")
        return web.json_response(
            [ad.ads_json for ad in ads] if isinstance(ads, list) else ads.ads_json
        )

    async def post(self):
        user_id = await self.check_login()
        json_data = await self.request.json()
        if "title" not in json_data:
            raise get_http_error(web.HTTPBadRequest, "missing fields")

        ad = Ads(
            title=json_data["title"],
            owner_id=user_id
        )
        await self.check_duplicate_ads(ad.title, ad.owner_id)
        return await self.add_ads(ad)

    async def patch(self):
        user_id = await self.check_login()
        json_data = await self.request.json()
        ad = await self.get_ads()
        if ad.owner_id != user_id:
            raise get_http_error(web.HTTPUnauthorized, "You must be logged in")
        if "title" in json_data:
            ad.title = json_data["title"]
        if "description" in json_data:
            ad.description = json_data["description"]
        return await self.add_ads(ad)

    async def delete(self):
        user_id = await self.check_login()
        await self.check_login()
        ad = await self.get_ads()
        if ad.owner_id != user_id:
            raise get_http_error(web.HTTPUnauthorized, "You must be logged in")
        await self.session_db.delete(ad)
        await self.session_db.commit()
        return web.json_response({"status": "deleted"})


class RegisterView(web.View):
    @property
    def session_db(self) -> AsyncSession:
        return self.request["session_db"]

    async def add_user(self, user: User):
        self.session_db.add(user)
        try:
            await self.session_db.commit()
        except IntegrityError:
            raise get_http_error(web.HTTPConflict, "user already exists")
        return web.json_response(user.id_json)

    async def post(self):
        json_data = await self.request.json()
        if "username" not in json_data or "email" not in json_data:
            raise get_http_error(web.HTTPConflict, "missing fields")
        username = json_data.get("username")
        email = json_data.get("email")
        password = json_data.get("password", "123")

        user = User(
            username=username,
            email=email,
        )
        user.hash_password(password)
        await self.add_user(user)
        return web.json_response(user.user_json)


class LoginView(web.View):
    @property
    def session_db(self) -> AsyncSession:
        return self.request["session_db"]

    async def post(self):
        json_data = await self.request.json()
        if "username" not in json_data or "password" not in json_data:
            raise get_http_error(web.HTTPConflict, "missing fields")

        username = json_data.get("username")
        password = json_data.get("password")
        user = await self.session_db.scalar(
            select(User).where(
                User.username == username
            )
        )
        if user is None:
            raise get_http_error(web.HTTPConflict, "Invalid username")
        if not user.check_password(password):
            raise get_http_error(web.HTTPConflict, "Invalid password")

        session = await get_session(self.request)
        session["user_id"] = user.id

        return web.json_response({
            "message": f"Login {username} successful",
            "user_id": user.id
        })


web.run_app(make_app(), host="127.0.0.1")
