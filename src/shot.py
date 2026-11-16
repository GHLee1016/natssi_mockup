import asyncio,sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for name,w,h in [('phone1',393,852),('phone2',393,852),('web',1440,900)]:
            pg=await b.new_page(viewport={'width':w,'height':h},device_scale_factor=3 if 'phone' in name else 2)
            await pg.goto(f'file:///home/claude/mockup/src/{name}.html'); await pg.wait_for_timeout(400)
            await pg.screenshot(path=f'/home/claude/mockup/screens/screen_{name}.png')
        await b.close()
asyncio.run(main())
