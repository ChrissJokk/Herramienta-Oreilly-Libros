import asyncio
from playwright.async_api import async_playwright

async def exportar_oreilly():
    async with async_playwright() as p:
        # Abre el navegador para que inicies sesión manualmente si es necesario
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # 1. Ir a la página de inicio de sesión de O'Reilly
        await page.goto("https://learning.oreilly.com/member/login/")
        print("--> Inicia sesión en la ventana del navegador que se abrió...")
        
        # Espera a que entres a la plataforma
        await page.wait_for_url("https://learning-oreilly-com.webezproxy.duoc.cl/home/*", timeout=1200000)
        print("--> Sesión detectada correctamente.")

        # 2. Lista de URLs de los capítulos que quieres guardar
        capitulos = [
            "https://learning-oreilly-com.webezproxy.duoc.cl/library/view/aprendizaje-automatico-practico/9781098179977/preface01.html"
            #,"https://learning-oreilly-com.webezproxy.duoc.cl/library/view/aprendizaje-automatico-practico/9781098179977/part01.html"
            ,"https://learning-oreilly-com.webezproxy.duoc.cl/library/view/aprendizaje-automatico-practico/9781098179977/ch01.html"
            ,"https://learning-oreilly-com.webezproxy.duoc.cl/library/view/aprendizaje-automatico-practico/9781098179977/ch02.html"
            ,"https://learning-oreilly-com.webezproxy.duoc.cl/library/view/aprendizaje-automatico-practico/9781098179977/ch03.html"
            ,"https://learning-oreilly-com.webezproxy.duoc.cl/library/view/aprendizaje-automatico-practico/9781098179977/ch04.html"
            ,"https://learning-oreilly-com.webezproxy.duoc.cl/library/view/aprendizaje-automatico-practico/9781098179977/ch05.html"
            ,"https://learning-oreilly-com.webezproxy.duoc.cl/library/view/aprendizaje-automatico-practico/9781098179977/ch06.html"
            ,"https://learning-oreilly-com.webezproxy.duoc.cl/library/view/aprendizaje-automatico-practico/9781098179977/ch07.html"
            ,"https://learning-oreilly-com.webezproxy.duoc.cl/library/view/aprendizaje-automatico-practico/9781098179977/ch08.html"
            ,"https://learning-oreilly-com.webezproxy.duoc.cl/library/view/aprendizaje-automatico-practico/9781098179977/ch09.html"
            ,"https://learning-oreilly-com.webezproxy.duoc.cl/library/view/aprendizaje-automatico-practico/9781098179977/ch10.html"
            ,"https://learning-oreilly-com.webezproxy.duoc.cl/library/view/aprendizaje-automatico-practico/9781098179977/ch11.html"
            ,"https://learning-oreilly-com.webezproxy.duoc.cl/library/view/aprendizaje-automatico-practico/9781098179977/ch12.html"
            ,"https://learning-oreilly-com.webezproxy.duoc.cl/library/view/aprendizaje-automatico-practico/9781098179977/ch13.html"
            ,"https://learning-oreilly-com.webezproxy.duoc.cl/library/view/aprendizaje-automatico-practico/9781098179977/ch14.html"
            ,"https://learning-oreilly-com.webezproxy.duoc.cl/library/view/aprendizaje-automatico-practico/9781098179977/ch15.html"
            ,"https://learning-oreilly-com.webezproxy.duoc.cl/library/view/aprendizaje-automatico-practico/9781098179977/ch16.html"
            ,"https://learning-oreilly-com.webezproxy.duoc.cl/library/view/aprendizaje-automatico-practico/9781098179977/ch17.html"
            ,"https://learning-oreilly-com.webezproxy.duoc.cl/library/view/aprendizaje-automatico-practico/9781098179977/ch18.html"
            ,"https://learning-oreilly-com.webezproxy.duoc.cl/library/view/aprendizaje-automatico-practico/9781098179977/ch19.html"
        ]


        CSS_LECTURA = """
            body { margin: 0 auto !important; max-width: 17cm !important;
                   font-size: 14pt !important; line-height: 1.6 !important;
                   font-family: Georgia, serif !important; }
            #contenido, #contenido * { max-width: 100% !important; }
            #contenido p, #contenido li { font-size: 14pt !important; text-align: justify; }
            #contenido pre, #contenido code { font-size: 10.5pt !important;
                   white-space: pre-wrap !important; word-break: break-word; }
            #contenido img { display: block; margin: 1em auto; height: auto !important; }
            #contenido h1 { font-size: 24pt !important; }
            #contenido h2 { font-size: 19pt !important; }
            #contenido h3 { font-size: 16pt !important; }
        """

        # 3. Recorrer y guardar cada capítulo como PDF
        for idx, url in enumerate(capitulos, start=1):
            print(f"Procesando capítulo {idx}...")
            # await page.goto(url, wait_until="networkidle")
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_function("""() => {
                    const c = document.querySelector('#sbo-rt-content')
                           || document.querySelector('[data-testid="contentViewer"]');
                    return c && c.innerText.length > 500 && !c.innerText.includes('Loading');
                }""", timeout=90000)
                await page.wait_for_timeout(2000)  # margen para imágenes
            except Exception as e:
                print(f"   !! Error en capítulo {idx}: {e}")
                continue

            # Deja solo el texto del capítulo en la página
            await page.evaluate("""() => {
                const c = document.querySelector('#sbo-rt-content')
                       || document.querySelector('[data-testid="contentViewer"]')
                       || document.querySelector('article')
                       || document.querySelector('main');
                if (c) {
                    const wrap = document.createElement('div');
                    wrap.id = 'contenido';
                    wrap.appendChild(c.cloneNode(true));
                    document.body.innerHTML = '';
                    document.body.appendChild(wrap);
                }
            }""")
            await page.add_style_tag(content=CSS_LECTURA)
            await page.emulate_media(media="screen")
            await page.wait_for_timeout(1000)  # deja cargar imágenes

            # Generar PDF del capítulo actual
            await page.pdf(
                path=f"capitulo_{idx:02d}.pdf",
                format="A4",
                print_background=True,
                margin={"top": "1.5cm", "bottom": "1.5cm", "left": "2cm", "right": "2cm"}
            )

        print("--> ¡Descarga completada!")

        from pypdf import PdfWriter
        from pathlib import Path

        writer = PdfWriter()
        for pdf in sorted(Path(".").glob("capitulo_*.pdf")):
            writer.append(str(pdf), outline_item=pdf.stem)  # marcador por capítulo
        writer.write("libro_completo.pdf")
        writer.close()
        print("--> PDF fusionado: libro_completo.pdf")

        await browser.close()

asyncio.run(exportar_oreilly())