cors = aiohttp_cors.setup(
    app,
    defaults={"*": aiohttp_cors.ResourceOptions(allow_credentials=False, expose_headers="*", allow_headers="*")},
)
