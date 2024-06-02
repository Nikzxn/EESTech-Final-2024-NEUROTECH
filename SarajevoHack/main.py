import flet as ft
import speech_recognition as sr
from add_options import make_response, speak, get_data, get_val
import matplotlib.pyplot as plt
import datetime
import matplotlib
import numpy as np
matplotlib.use('agg')


WIDTH = 600
HEIGHT = 338


def create_table():
    titles = ["relative_humidity 5 min", "temperature 5 min"]  # Setting titles for each plot based on parameters

    # Iterate over the list of values for each entity
    array = get_val()
    for i, values in enumerate([array[-2], array[-1]]):
        values = list(map(float, values))
        plt.figure(figsize=(10, 5))
        plt.plot(values, linewidth=8)  # Plot the values
        plt.grid(True)
        plt.yticks(np.arange(min(values), max(values) + 1, 1.0))
        plt.axis("off")

        # Set the title of the current plot
        plt.title(titles[i], fontsize=44)
        plt.savefig(f'source/plot{i}.png')
        plt.close()


def main(page: ft.Page):
    global WIDTH, HEIGHT
    page.title = "Voice assistant"
    page.window_width = WIDTH
    page.window_height = HEIGHT

    def click_menu(e):
        stack_main.visible = False
        stack_menu.visible = True
        page.update()

    def click_main(e):
        stack_main.visible = True
        stack_menu.visible = False
        page.update()

    menu_btn = ft.IconButton(
        icon=ft.icons.MENU,
        icon_size=30,
        icon_color="black",
        top=-10,
        on_click=click_menu,
        hover_color="white",
        highlight_color="white"
    )

    menu_close_btn = ft.IconButton(
        icon=ft.icons.ARROW_BACK,
        icon_size=30,
        icon_color="black",
        on_click=click_main,
        hover_color="white",
        highlight_color="white"
    )

    status_label = ft.Text(
        "Waiting for activation...",
        text_align=ft.TextAlign.CENTER,
        width=page.width,
        style=ft.TextStyle(
             font_family='montserrat',
             weight=ft.FontWeight.W_600,
             size=16
        )
    )

    temperature = ft.Text("", size=25, weight=ft.FontWeight.W_600, width=120)
    pressure = ft.Text("", size=25, weight=ft.FontWeight.W_600, width=120)
    CO2 = ft.Text("", size=25, weight=ft.FontWeight.W_600, width=120)
    humidity = ft.Text("", size=25, weight=ft.FontWeight.W_600, width=120)
    light = ft.Text("", size=25, weight=ft.FontWeight.W_600, width=120)

    bg_menu = ft.Image(src="source/bg.jpg", fit=ft.ImageFit.FIT_HEIGHT)
    time_label = ft.Text(size=25, weight=ft.FontWeight.W_600, left=340)
    sensor = ft.Text("open space", size=23, weight=ft.FontWeight.W_500, left=110, top=2)

    graf1 = ft.Image(src='source/plot0.png', border_radius=20, width=250, filter_quality=ft.FilterQuality.HIGH, scale=0.9)
    graf2 = ft.Image(src='source/plot1.png', border_radius=20, width=250, filter_quality=ft.FilterQuality.HIGH, scale=0.9)

    params = ft.Column(
        spacing=4,
        controls=[
            CO2,
            pressure,
            light,
            humidity,
            temperature,
        ]
    )
    grafics = ft.Column(
        spacing=-10,
        controls=[
            graf1,
            graf2
        ]
    )

    media = [ft.VideoMedia('source/yaya_wait.mp4'), ft.VideoMedia('source/yaya_load.mp4')]

    video = ft.Video(
            expand=True,
            show_controls=False,
            playlist=media,
            playlist_mode=ft.PlaylistMode.LOOP,
            aspect_ratio=16 / 9,
            autoplay=True
        )
    content = ft.Container(
            video,
            alignment=ft.alignment.center,
            margin=-10)

    column_setup = ft.Row(
        top=35,
        left=165,
        controls=[
            params,
            grafics
        ]
    )

    stack_main = ft.Stack(
            controls=[
                content,
                status_label,
                menu_btn
            ]
    )

    stack_menu = ft.Stack(
        visible=False,
        controls=[
            bg_menu,
            sensor,
            time_label,
            menu_close_btn,
            column_setup
        ]
    )

    page.add(stack_main)
    page.add(stack_menu)

    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    # Функция для обновления статуса на странице
    def update_status(message):
        status_label.value = message
        page.update()

    # Функция обработки аудио
    def listen():
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            while True:
                try:
                    update_status("Listening...")
                    audio = recognizer.listen(source)
                    update_status("Processing...")
                    text = recognizer.recognize_google(audio, language="en-EN")
                    print('text: ', text)
                    if "lana" in text.lower():
                        text = text[text.find('lana')+4:]
                        handle_command(text)
                    else:
                        print("Not command")
                except:
                    update_time()
                    continue

    # Функция для обработки команды
    def handle_command(command):
        update_status("")
        video.jump_to(1)
        answer = make_response(command)
        print("answer: ", answer)
        speak(answer)

    def update_time():
        now = datetime.datetime.now()
        time_label.value = "latest " + now.strftime("%H:%M:%S")  # Форматирование времени
        data = get_data()
        CO2.value = data[0][0]
        pressure.value = data[1][0]
        light.value = data[2][0]
        humidity.value = data[3][0]
        temperature.value = data[4][0]

        create_table()

        page.update()

    # Запускаем прослушивание в отдельном потоке
    update_time()
    listen()



if __name__ == "__main__":
    app = ft.app(target=main)
    app.run()

