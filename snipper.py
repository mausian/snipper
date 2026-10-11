import asyncio as asy
import pathlib as pl
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:

        #path to profile will be created and playwright will make a persistant profile that will be saved to target dir
        profile = pl.Path('/path/to/profile').resolve()

        #used persistant to have more control over privacy but im looking into this more... I may change it to use non persistant so user data gets nuked after each run
        browser = await p.firefox.launch_persistent_context(
            user_data_dir = str(profile),
            headless = True, #browser is hidden
            accept_downloads = False,
            firefox_user_prefs = {
                'toolkit.telemetry.enabled': False,
                'datareporting.healthreport.uploadEnabled': False,
                'geo.enabled': False,
                'privacy.trackingprotection.enabled': True,
                'privacy.trackingprotection.pbmode.enabled': True,
            }
        )

        #make new page and navigate
        page = await browser.new_page()
        await page.goto('https://target_url')
        
        #login
        #I used CSS locators but depending on use case there there is likely easier, more generalized ways to target elements
        await page.locator('#target').click()
        await page.locator('#target_username').fill('username')
        await page.locator('#target').click()
        await page.locator('#target').click()
        await page.locator("#target_password").fill('strong_password')
        await page.locator('#target').click()
        #targeting the username field then clicking may be redeundant since I am filling the username field with a seperate command.

        #inside of portal, get and follow link to new page.
        async with page.expect_popup() as popup_info:
            await page.get_by_label('target_label').click()
        popup = await popup_info.value

        target_chapter = input("Target Chapter: ").strip()
        target = str(f'Open Chapter {target_chapter} Enhanced')

        '''
        test, use to bring up locator tool for elements address
        print(await page.get_by_role("link", name="Open Chapter 30 Enhanced").count())
        await page.pause()
        '''
        await popup.get_by_role("link", name=target).click()
        
        '''
        test, use to bring up locator tool for question adress
        print(await popup.get_by_title("Question 1.").count())
        await popup.pause()
        '''
        #take snips
        await popup.wait_for_load_state('domcontentloaded')
        
        #cookie popup was in the way of the snips
        await popup.get_by_role('button',name='Accept All Cookies').click()
        
        #each question shared an iteratable element
        questions = popup.locator('div.exIter')
        total = await questions.count()
        
        #output path
        output_dir = pl.Path(f'/output/path/to/snips/chapter_{target_chapter}')
        output_dir.mkdir(exist_ok=True)

        for i in range(total):
            question = questions.nth(i)

            #debug position
            position = await question.bounding_box()
            print(f'Question {i + 1}: {position}')

            #snip
            snip_path = output_dir / f'question_{i + 1}.png'
            await question.screenshot(path=str(snip_path))

    #left default auto close on complete


asy.run(main())