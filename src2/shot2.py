import asyncio
from playwright.async_api import async_playwright
names=['d_diary','d_change','d_compare','d_routine','d_report']
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for n in names:
            pg=await b.new_page(viewport={'width':393,'height':852},device_scale_factor=3)
            await pg.goto(f'file:///home/claude/mockup/src2/{n}.html'); await pg.wait_for_timeout(300)
            await pg.screenshot(path=f'/home/claude/mockup/screens/screen_{n}.png')
        await b.close()
asyncio.run(main())
