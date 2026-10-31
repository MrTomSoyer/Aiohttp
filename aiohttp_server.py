import json
from aiohttp import web
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db import Session_DB, User,Ads, close_orm, init_orm

app = web.Application()

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

app.cleanup_ctx.append(orm_context)
app.middlewares.append(session_db_middleware)


class IndexView(web.View):
    @staticmethod
    async def get():
        return web.HTTPFound("/ads")


class AdsView(web.View):
    @property
    def session_db(self) -> AsyncSession:
        return self.request["session_db"]

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
            raise get_http_error(web.HTTPConflict, "ads already exists")
        return web.json_response(ads.id_json)


    async def get(self):
        ads = await self.get_ads()
        if ads is None:
            raise get_http_error(web.HTTPNotFound, "ads not found")
        return web.json_response(
            [ad.id_json for ad in ads] if isinstance(ads, list) else ads.id_json
        )

    async def post(self):
        json_data = await self.request.json()
        if "title" not in json_data or "owner_id" not in json_data:
            raise get_http_error(web.HTTPConflict, "missing fields")

        ad = Ads(
            title=json_data["title"],
            owner_id=json_data["owner_id"]
        )
        await self.add_ads(ad)
        return web.json_response(ad.id_json)

    async def patch(self):
        json_data = await self.request.json()

        ad = await self.get_ads()
        if "title" in json_data:
            ad.title = json_data["title"]
        if "description" in json_data:
            ad.description = json_data["description"]
        await self.add_ads(ad)
        return web.json_response(ad.id_json)

    async def delete(self):
        ad = await self.get_ads()
        await self.session_db.delete(ad)
        await self.session_db.commit()
        return web.json_response({"status": "deleted"})


class UserView(web.View):
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

        user = User(
            username=json_data["username"],
            email=json_data["email"],
            password_hash=json_data["password"],
        )
        await self.add_user(user)
        return web.json_response(user.id_json)


app.add_routes(
    [
        web.get(r"/ads/{ad_id:\d+}", AdsView),
        web.get("/ads", AdsView),
        web.get("/", IndexView),
        web.post("/ads", AdsView),
        web.post("/user", UserView),
        web.patch(r"/ads/{ad_id:\d+}", AdsView),
        web.delete(r"/ads/{ad_id:\d+}", AdsView),
    ]
)


web.run_app(app, host="127.0.0.1")
